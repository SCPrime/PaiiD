import json
import os
from datetime import datetime

from playwright.sync_api import sync_playwright


def main() -> int:
    base_url = os.getenv(
        "PRODUCTION_URL", "https://paiid-frontend.onrender.com"
    ).rstrip("/")
    backend_url = os.getenv("BACKEND_URL", "https://paiid-backend.onrender.com").rstrip(
        "/"
    )

    report = {
        "base_url": base_url,
        "backend_url": backend_url,
        "checks": [],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # 1) Page render
        resp = page.goto(base_url, wait_until="domcontentloaded", timeout=30000)
        report["checks"].append(
            {
                "name": "page_render",
                "status": resp.status if resp else None,
                "ok": bool(resp and resp.ok),
            }
        )

        # 2) Proxy CORS preflight (allowed origin)
        preflight = page.request.fetch(
            f"{base_url}/api/proxy/api/telemetry/events",
            method="OPTIONS",
            headers={
                "Origin": base_url,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "authorization,content-type",
            },
        )
        report["checks"].append(
            {
                "name": "proxy_preflight_allowed",
                "status": preflight.status,
                "ok": preflight.status == 204,
            }
        )

        # 3) Backend health
        health = page.request.get(f"{backend_url}/api/health")
        report["checks"].append(
            {
                "name": "backend_health",
                "status": health.status,
                "ok": health.ok,
            }
        )

        # 4) Backend features
        features = page.request.get(f"{backend_url}/api/health/features")
        report["checks"].append(
            {
                "name": "backend_features",
                "status": features.status,
                "ok": features.ok,
            }
        )

        browser.close()

    # Save report
    out = f"live-smoke-report-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Exit code: 0 if all ok, else 1
    all_ok = all(chk.get("ok") for chk in report["checks"])
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
