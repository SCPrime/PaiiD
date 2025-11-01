import json
import os
import re
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
    reports_dir = get_reports_dir()
    os.makedirs(reports_dir, exist_ok=True)
    output = os.path.join(reports_dir, "branding_a11y.json")

    report = {
        "base_url": base_url,
        "timestamp": datetime.now(UTC).isoformat(),
        "checks": {},
        "issues": [],
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        page.goto(base_url, wait_until="networkidle", timeout=30000)

        # Branding: aria label present
        has_paiid_aria = page.locator('[aria-label="PaiiD"]').count() > 0
        report["checks"]["aria_PaiiD_present"] = has_paiid_aria
        if not has_paiid_aria:
            report["issues"].append("Missing element with aria-label=PaiiD")

        # Header presence
        header_ok = page.locator("header").count() > 0
        report["checks"]["header_present"] = header_ok
        if not header_ok:
            report["issues"].append("Header element not found")

        # Disallowed UI text checks (heuristic)
        html = page.content()
        if re.search(r"\\biPi\\b", html):
            report["issues"].append("Found forbidden branding: iPi")
        # Look for AI in text nodes (simple heuristic)
        if re.search(r">[^<]*\\bAI\\b", html):
            report["issues"].append("Found forbidden branding: AI")

        # Basic A11y: unlabeled buttons, images without alt
        unlabeled_buttons = page.evaluate(
            """
            () => Array.from(document.querySelectorAll('button')).filter(b => !b.getAttribute('aria-label') && !b.textContent?.trim()).length
            """
        )
        images_without_alt = page.evaluate(
            """
            () => Array.from(document.querySelectorAll('img')).filter(img => !img.hasAttribute('alt')).length
            """
        )
        report["checks"]["unlabeled_buttons"] = unlabeled_buttons
        report["checks"]["images_without_alt"] = images_without_alt
        if unlabeled_buttons:
            report["issues"].append(f"Unlabeled buttons: {unlabeled_buttons}")
        if images_without_alt:
            report["issues"].append(f"Images without alt: {images_without_alt}")

        browser.close()

    with open(output, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Pass if no issues
    return 0 if not report["issues"] else 1


if __name__ == "__main__":
    raise SystemExit(main())



