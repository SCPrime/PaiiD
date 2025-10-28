import json
import os
import time
from datetime import datetime

from playwright.sync_api import sync_playwright

THRESHOLD_MS = int(os.getenv("FLOW_THRESHOLD_MS", "2000"))


def timed_fetch(page, url: str, method: str = "GET", headers: dict | None = None):
    start = time.perf_counter()
    resp = page.request.fetch(url, method=method, headers=headers or {})
    duration_ms = int((time.perf_counter() - start) * 1000)
    return resp, duration_ms


def main() -> int:
    base_url = os.getenv(
        "PRODUCTION_URL", "https://paiid-frontend.onrender.com"
    ).rstrip("/")
    origin = base_url

    report = {
        "base_url": base_url,
        "threshold_ms": THRESHOLD_MS,
        "flows": [],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Open home
        page.goto(base_url, wait_until="domcontentloaded", timeout=30000)

        # Flow 1: market quote SPY
        url_quote = f"{base_url}/api/proxy/api/market/quote/SPY"
        resp, dur = timed_fetch(page, url_quote, headers={"Origin": origin})
        flow1 = {
            "flow": "quote_SPY",
            "status": resp.status,
            "duration_ms": dur,
            "ok": resp.ok and dur <= THRESHOLD_MS,
        }
        report["flows"].append(flow1)

        # Flow 2: options expirations SPY
        url_exp = f"{base_url}/api/proxy/api/options/expirations/SPY"
        resp, dur = timed_fetch(page, url_exp, headers={"Origin": origin})
        flow2 = {
            "flow": "options_expirations_SPY",
            "status": resp.status,
            "duration_ms": dur,
            "ok": resp.ok and dur <= THRESHOLD_MS,
        }
        report["flows"].append(flow2)

        # Flow 3: market bars SPY (daily, limited)
        url_bars = f"{base_url}/api/proxy/api/market/bars/SPY?timeframe=daily&limit=50"
        resp, dur = timed_fetch(page, url_bars, headers={"Origin": origin})
        flow3 = {
            "flow": "bars_SPY_daily",
            "status": resp.status,
            "duration_ms": dur,
            "ok": resp.ok and dur <= THRESHOLD_MS,
        }
        report["flows"].append(flow3)

        browser.close()

    out = f"live-flows-report-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    all_ok = all(item["ok"] for item in report["flows"])
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
