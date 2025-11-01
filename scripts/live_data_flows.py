import json
import os
import time
from datetime import UTC, datetime

import requests
from playwright.sync_api import sync_playwright

try:
    from .mod_config import get_base_url  # type: ignore
except Exception:
    try:
        from mod_config import get_base_url  # type: ignore
    except Exception:

        def get_base_url() -> str:  # type: ignore
            return os.getenv(
                "PRODUCTION_URL", "https://paiid-frontend.onrender.com"
            ).rstrip("/")


THRESHOLD_MS = int(os.getenv("FLOW_THRESHOLD_MS", "2000"))


def timed_fetch(
    session: requests.Session,
    url: str,
    method: str = "GET",
    headers: dict | None = None,
):
    start = time.perf_counter()
    try:
        response = session.request(method, url, headers=headers or {}, timeout=5)
        duration_ms = int((time.perf_counter() - start) * 1000)
        return response, duration_ms
    except requests.RequestException as exc:
        duration_ms = int((time.perf_counter() - start) * 1000)

        # Create lightweight object to mimic response interface
        class _FailedResponse:
            status_code = 0
            ok = False
            text = str(exc)

        return _FailedResponse(), duration_ms


def main() -> int:
    base_url = get_base_url()
    origin = base_url

    report = {
        "base_url": base_url,
        "threshold_ms": THRESHOLD_MS,
        "flows": [],
        "timestamp": datetime.now(UTC).isoformat(),
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            # Simple ping to ensure site reachable (headless browser handles rendering guardrail)
            page = browser.new_page()
            try:
                page.goto(base_url, wait_until="domcontentloaded", timeout=30000)
            finally:
                page.close()

            with requests.Session() as session:
                session.headers.update({"Origin": origin})

                # Flow 1: market quote SPY
                url_quote = f"{base_url}/api/proxy/api/market/quote/SPY"
                resp, dur = timed_fetch(session, url_quote)
                flow1 = {
                    "flow": "quote_SPY",
                    "status": getattr(resp, "status_code", 0),
                    "duration_ms": dur,
                    "ok": getattr(resp, "ok", False) and dur <= THRESHOLD_MS,
                }
                report["flows"].append(flow1)

                # Flow 2: options expirations SPY
                url_exp = f"{base_url}/api/proxy/api/options/expirations/SPY"
                resp, dur = timed_fetch(session, url_exp)
                flow2 = {
                    "flow": "options_expirations_SPY",
                    "status": getattr(resp, "status_code", 0),
                    "duration_ms": dur,
                    "ok": getattr(resp, "ok", False) and dur <= THRESHOLD_MS,
                }
                report["flows"].append(flow2)

                # Flow 3: market bars SPY (daily, limited)
                url_bars = (
                    f"{base_url}/api/proxy/api/market/bars/SPY?timeframe=daily&limit=50"
                )
                resp, dur = timed_fetch(session, url_bars)
                flow3 = {
                    "flow": "bars_SPY_daily",
                    "status": getattr(resp, "status_code", 0),
                    "duration_ms": dur,
                    "ok": getattr(resp, "ok", False) and dur <= THRESHOLD_MS,
                }
                report["flows"].append(flow3)
        finally:
            browser.close()

    out = f"live-flows-report-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    all_ok = all(item["ok"] for item in report["flows"])
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
