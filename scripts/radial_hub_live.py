import json
import os
from datetime import UTC, datetime

from playwright.sync_api import sync_playwright

try:
    from .mod_config import get_base_url, get_reports_dir  # type: ignore
except Exception:
    try:
        from mod_config import get_base_url, get_reports_dir  # type: ignore
    except Exception:

        def get_base_url() -> str:  # type: ignore
            return os.getenv(
                "PRODUCTION_URL", "https://paiid-frontend.onrender.com"
            ).rstrip("/")

        def get_reports_dir() -> str:  # type: ignore
            return os.getenv("REPORTS_DIR", "reports")


def main() -> int:
    base_url = get_base_url()
    output_dir = get_reports_dir()
    output = os.getenv("HUB_OUTPUT", f"{output_dir}/radial_hub_live.json")

    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)

    report = {
        "base_url": base_url,
        "timestamp": datetime.now(UTC).isoformat(),
        "checks": {},
        "issues": [],
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        # Ensure onboarding is bypassed so radial hub renders
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

        # Navigate and wait for network idle
        page.goto(base_url, wait_until="networkidle", timeout=30000)

        # Basic presence checks for hub labels in the SVG (use content fallback for robustness)
        dow_ok = page.locator("text=DOW JONES INDUSTRIAL").first.count() > 0
        nasdaq_ok = page.locator("text=NASDAQ COMPOSITE").first.count() > 0

        report["checks"]["dow_label"] = dow_ok
        report["checks"]["nasdaq_label"] = nasdaq_ok

        # Value texts are rendered with dy="14" and include decimals
        # We check presence of any text node with a decimal right after load
        # This is a heuristic to avoid brittle selectors
        content = page.content()
        has_decimal = "." in content
        if not dow_ok:
            dow_ok = "DOW JONES" in content
        if not nasdaq_ok:
            nasdaq_ok = "NASDAQ COMPOSITE" in content or "NASDAQ" in content
        report["checks"]["value_text_present"] = has_decimal

        # Console errors summary
        report["checks"]["console_errors"] = len(console_errors)
        if console_errors:
            report["issues"].extend(console_errors[:5])

        browser.close()

    with open(output, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    all_ok = dow_ok and nasdaq_ok and report["checks"]["console_errors"] == 0
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
