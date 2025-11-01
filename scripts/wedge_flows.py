import json
import os
from datetime import UTC, datetime

from playwright.sync_api import sync_playwright

try:
    from .mod_config import get_base_url, get_reports_dir  # type: ignore
except Exception:
    # Fallback for direct execution
    try:
        from mod_config import get_base_url, get_reports_dir  # type: ignore
    except Exception:

        def get_base_url() -> str:  # type: ignore
            return os.getenv(
                "PRODUCTION_URL", "https://paiid-frontend.onrender.com"
            ).rstrip("/")

        def get_reports_dir() -> str:  # type: ignore
            return os.getenv("REPORTS_DIR", "reports")


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
    base_url = get_base_url()
    output_dir = get_reports_dir()
    output = os.getenv("WEDGE_OUTPUT", f"{output_dir}/wedge_flows.json")

    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)

    report = {
        "base_url": base_url,
        "timestamp": datetime.now(UTC).isoformat(),
        "results": [],
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        # Ensure onboarding is bypassed so radial menu renders
        context.add_init_script(
            """
            () => {
              try {
                localStorage.setItem('user-setup-complete','true');
                localStorage.setItem('admin-bypass','true');
                localStorage.setItem('bypass-timestamp', new Date().toISOString());
              } catch (_) {}
            }
            """
        )
        page = context.new_page()

        console_errors: list[str] = []
        page.on(
            "console",
            lambda msg: console_errors.append(msg.text)
            if msg.type == "error"
            else None,
        )

        # Load home and wait for radial SVG
        page.goto(base_url, wait_until="networkidle", timeout=30000)
        try:
            page.wait_for_selector("svg", timeout=10000)
        except Exception:
            pass
        page.wait_for_timeout(800)

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
                        # Final fallback: click by segment index in the SVG
                        try:
                            index = WEDGES.index(wedge)
                            segs = page.locator("svg .segment path")
                            if segs.count() >= index + 1:
                                seg = segs.nth(index)
                                try:
                                    seg.hover(timeout=2000)
                                except Exception:
                                    pass
                                seg.click(timeout=5000)
                                result["clicked"] = True
                                result["visible"] = True
                                page.wait_for_load_state("networkidle", timeout=10000)
                                page.wait_for_timeout(500)
                            else:
                                result["errors"].append("segment_index_not_found")
                        except Exception as e:
                            result["errors"].append(f"fallback_click_error: {e}")
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
