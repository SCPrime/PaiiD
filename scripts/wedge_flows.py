import json
import os
from datetime import UTC, datetime

from playwright.sync_api import sync_playwright

WEDGES = [
    "morning-routine",
    "active-positions",
    "execute",
    "research",
    "proposals",
    "my-account",
    "news-review",
    "strategy-builder",
    "backtesting",
    "settings",
]

FALLBACK_TEXT: dict[str, list[str]] = {
    "morning-routine": ["MORNING"],
    "active-positions": ["ACTIVE"],
    "execute": ["EXECUTE"],
    "research": ["RESEARCH"],
    "proposals": ["RECOMMENDATIONS", "PaiiD"],
    "my-account": ["P&L"],
    "news-review": ["NEWS"],
    "strategy-builder": ["STRATEGY"],
    "backtesting": ["BACKTESTING"],
    "settings": ["SETTINGS"],
}


def main() -> int:
    base_url = os.getenv(
        "PRODUCTION_URL", "https://paiid-frontend.onrender.com"
    ).rstrip("/")
    output = os.getenv("WEDGE_OUTPUT", "reports/wedge_flows.json")

    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)

    report = {
        "base_url": base_url,
        "timestamp": datetime.now(UTC).isoformat(),
        "results": [],
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        console_errors: list[str] = []
        page.on(
            "console",
            lambda msg: console_errors.append(msg.text)
            if msg.type == "error"
            else None,
        )

        # Load home
        page.goto(base_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(1000)

        for wedge in WEDGES:
            errors_before = len(console_errors)
            result = {
                "wedge": wedge,
                "clicked": False,
                "visible": False,
                "errors": [],
            }

            try:
                locator = page.locator(f'[data-testid="wedge-{wedge}"]').first
                if locator.count() > 0:
                    # Ensure visible before click
                    if locator.is_visible():
                        result["visible"] = True
                    locator.click(timeout=5000)
                    result["clicked"] = True
                    # Allow network to settle
                    page.wait_for_load_state("networkidle", timeout=10000)
                    page.wait_for_timeout(500)
                else:
                    # Fallback: try visible text tokens in SVG
                    tokens = FALLBACK_TEXT.get(wedge, [])
                    clicked = False
                    for token in tokens:
                        text_loc = page.locator(f"text={token}").first
                        if text_loc.count() > 0 and text_loc.is_visible():
                            text_loc.click(timeout=5000)
                            result["visible"] = True
                            result["clicked"] = True
                            page.wait_for_load_state("networkidle", timeout=10000)
                            page.wait_for_timeout(500)
                            clicked = True
                            break
                    if not clicked:
                        result["errors"].append("locator_not_found")
            except Exception as e:  # noqa: BLE001 - capturing for report
                result["errors"].append(str(e))

            # Capture new console errors after interaction
            new_errors = console_errors[errors_before:]
            if new_errors:
                # keep only first few to avoid bloat
                result["errors"].extend(new_errors[:5])

            report["results"].append(result)

        browser.close()

    with open(output, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Pass if all wedges were clickable and produced no errors
    all_ok = all(r["clicked"] and not r["errors"] for r in report["results"])
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
