#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BROWSER MOD - Browser Rendering & Issue Monitor
Automated browser testing and issue tracking for production deployments.

Usage:
    python scripts/browser_mod.py --url https://paiid-frontend.onrender.com
    python scripts/browser_mod.py --url http://localhost:3000 --dev
    python scripts/browser_mod.py --check-render  # Quick render check
    python scripts/browser_mod.py --full-audit   # Complete UX audit
"""

import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
import argparse

# Fix Windows console encoding
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

try:
    from playwright.async_api import async_playwright, Browser, Page, Error as PlaywrightError
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
except ImportError:
    print("[ERROR] Missing dependencies. Install with:")
    print("   pip install -r scripts/requirements-monitor.txt")
    print("   playwright install chromium")
    sys.exit(1)

console = Console()

# Default configuration
DEFAULT_URL = "https://paiid-frontend.onrender.com"
TIMEOUT = 30000  # 30 seconds
WORKFLOWS = [
    "Morning Routine",
    "Active Positions",
    "Execute Trade",
    "Research",
    "AI Recommendations",
    "P&L Dashboard",
    "News Review",
    "Strategy Builder",
    "Backtesting",
    "Settings"
]


class BrowserMod:
    """Browser monitoring and validation system"""

    def __init__(self, base_url: str, headless: bool = True, slow_mo: int = 0):
        self.base_url = base_url.rstrip('/')
        self.headless = headless
        self.slow_mo = slow_mo
        self.results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "base_url": base_url,
            "checks": {},
            "issues": [],
            "screenshots": [],
            "performance": {}
        }

    async def run_full_audit(self):
        """Run complete browser audit"""
        console.print("\n[bold cyan]🌐 BROWSER MOD - Full Audit[/bold cyan]\n")

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=self.headless,
                slow_mo=self.slow_mo
            )

            try:
                # Create browser context
                context = await browser.new_context(
                    viewport={"width": 1920, "height": 1080},
                    user_agent="BrowserMod/1.0 (Automated Testing)"
                )

                page = await context.new_page()

                # Run all checks
                await self.check_initial_render(page)
                await self.check_console_errors(page)
                await self.check_network_errors(page)
                await self.check_workflows(page)
                await self.check_performance(page)
                await self.check_accessibility(page)
                await self.check_responsive_design(page)

                # Generate report
                self.generate_report()

            finally:
                await browser.close()

    async def check_initial_render(self, page: Page):
        """Check if page renders successfully"""
        console.print("[yellow]📄 Checking initial render...[/yellow]")

        try:
            # Navigate to page
            response = await page.goto(self.base_url, wait_until="networkidle", timeout=TIMEOUT)

            if response and response.status >= 400:
                self.add_issue(
                    "RENDER_ERROR",
                    f"HTTP {response.status} - Page failed to load",
                    "CRITICAL"
                )
                self.results["checks"]["initial_render"] = "❌ FAIL"
                console.print("[red]❌ Initial render FAILED[/red]")
                return False

            # Wait for React to load
            await page.wait_for_selector("body", timeout=10000)

            # Check for common elements
            has_radial_menu = await page.locator('[data-testid="radial-menu"], svg').count() > 0
            has_content = await page.content()

            if not has_radial_menu and "PaiiD" not in has_content:
                self.add_issue(
                    "RENDER_INCOMPLETE",
                    "Page loaded but main content not visible",
                    "HIGH"
                )
                self.results["checks"]["initial_render"] = "⚠️ PARTIAL"
                console.print("[yellow]⚠️ Initial render PARTIAL[/yellow]")
                return False

            # Take screenshot
            screenshot_path = f"screenshots/initial-render-{datetime.now().strftime('%Y%m%d-%H%M%S')}.png"
            Path("screenshots").mkdir(exist_ok=True)
            await page.screenshot(path=screenshot_path, full_page=True)
            self.results["screenshots"].append(screenshot_path)

            self.results["checks"]["initial_render"] = "✅ PASS"
            console.print("[green]✅ Initial render successful[/green]")
            return True

        except PlaywrightError as e:
            self.add_issue(
                "RENDER_TIMEOUT",
                f"Page failed to load: {str(e)}",
                "CRITICAL"
            )
            self.results["checks"]["initial_render"] = "❌ FAIL"
            console.print(f"[red]❌ Render failed: {e}[/red]")
            return False

    async def check_console_errors(self, page: Page):
        """Monitor console for JavaScript errors"""
        console.print("[yellow]🐛 Checking console errors...[/yellow]")

        console_errors = []
        console_warnings = []

        # Listen to console messages
        page.on("console", lambda msg: (
            console_errors.append(msg.text) if msg.type == "error" else
            console_warnings.append(msg.text) if msg.type == "warning" else None
        ))

        # Navigate and wait for console messages
        await page.goto(self.base_url, wait_until="networkidle")
        await page.wait_for_timeout(3000)  # Wait 3s for async errors

        # Filter out known non-critical warnings
        critical_errors = [
            e for e in console_errors
            if not any(skip in e.lower() for skip in ["favicon", "sourcemap", "hydration"])
        ]

        if critical_errors:
            for error in critical_errors[:5]:  # Show first 5
                self.add_issue(
                    "CONSOLE_ERROR",
                    error,
                    "HIGH" if "TypeError" in error or "ReferenceError" in error else "MEDIUM"
                )

            self.results["checks"]["console_errors"] = f"❌ {len(critical_errors)} errors"
            console.print(f"[red]❌ Found {len(critical_errors)} console errors[/red]")
        else:
            self.results["checks"]["console_errors"] = "✅ PASS"
            console.print(f"[green]✅ No critical console errors ({len(console_warnings)} warnings)[/green]")

    async def check_network_errors(self, page: Page):
        """Check for failed network requests"""
        console.print("[yellow]🌐 Checking network errors...[/yellow]")

        failed_requests = []

        # Listen to failed requests
        page.on("requestfailed", lambda request: failed_requests.append({
            "url": request.url,
            "failure": request.failure
        }))

        await page.goto(self.base_url, wait_until="networkidle")
        await page.wait_for_timeout(2000)

        # Filter out known non-critical failures
        critical_failures = [
            r for r in failed_requests
            if not any(skip in r["url"].lower() for skip in ["analytics", "tracking", "fonts.googleapis"])
        ]

        if critical_failures:
            for failure in critical_failures[:5]:
                self.add_issue(
                    "NETWORK_ERROR",
                    f"Failed to load: {failure['url']}",
                    "HIGH"
                )

            self.results["checks"]["network_errors"] = f"❌ {len(critical_failures)} failures"
            console.print(f"[red]❌ Found {len(critical_failures)} network failures[/red]")
        else:
            self.results["checks"]["network_errors"] = "✅ PASS"
            console.print("[green]✅ No network errors[/green]")

    async def check_workflows(self, page: Page):
        """Test all 10 radial menu workflows"""
        console.print("[yellow]🔄 Checking workflows...[/yellow]")

        await page.goto(self.base_url, wait_until="networkidle")

        working_workflows = []
        broken_workflows = []

        for workflow in WORKFLOWS:
            try:
                # Try to find and click workflow
                # This is a simplified check - in reality would need more specific selectors
                workflow_selector = f"text={workflow}"

                # Check if workflow element exists
                element = page.locator(workflow_selector).first
                is_visible = await element.is_visible(timeout=5000) if await element.count() > 0 else False

                if is_visible:
                    working_workflows.append(workflow)
                else:
                    broken_workflows.append(workflow)
                    self.add_issue(
                        "WORKFLOW_NOT_FOUND",
                        f"Workflow '{workflow}' not found or not clickable",
                        "MEDIUM"
                    )

            except Exception as e:
                broken_workflows.append(workflow)
                self.add_issue(
                    "WORKFLOW_ERROR",
                    f"Error testing '{workflow}': {str(e)}",
                    "MEDIUM"
                )

        self.results["checks"]["workflows"] = f"✅ {len(working_workflows)}/10 working"
        console.print(f"[green]✅ {len(working_workflows)}/10 workflows accessible[/green]")

        if broken_workflows:
            console.print(f"[yellow]⚠️ Issues with: {', '.join(broken_workflows)}[/yellow]")

    async def check_performance(self, page: Page):
        """Check page performance metrics"""
        console.print("[yellow]⚡ Checking performance...[/yellow]")

        # Navigate with timing
        start_time = asyncio.get_event_loop().time()
        await page.goto(self.base_url, wait_until="networkidle")
        load_time = asyncio.get_event_loop().time() - start_time

        # Get performance metrics
        metrics = await page.evaluate("""
            () => {
                const timing = performance.timing;
                const paint = performance.getEntriesByType('paint');
                return {
                    domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
                    loadComplete: timing.loadEventEnd - timing.navigationStart,
                    firstPaint: paint.find(e => e.name === 'first-paint')?.startTime || 0,
                    firstContentfulPaint: paint.find(e => e.name === 'first-contentful-paint')?.startTime || 0
                };
            }
        """)

        self.results["performance"] = {
            "page_load_time": round(load_time, 2),
            "dom_content_loaded": metrics.get("domContentLoaded", 0),
            "load_complete": metrics.get("loadComplete", 0),
            "first_paint": metrics.get("firstPaint", 0),
            "first_contentful_paint": metrics.get("firstContentfulPaint", 0)
        }

        # Check thresholds
        if load_time > 10:
            self.add_issue(
                "PERFORMANCE_SLOW",
                f"Page load time: {load_time:.2f}s (target: <10s)",
                "MEDIUM"
            )
            self.results["checks"]["performance"] = f"⚠️ {load_time:.2f}s"
            console.print(f"[yellow]⚠️ Slow load time: {load_time:.2f}s[/yellow]")
        else:
            self.results["checks"]["performance"] = f"✅ {load_time:.2f}s"
            console.print(f"[green]✅ Good load time: {load_time:.2f}s[/green]")

    async def check_accessibility(self, page: Page):
        """Basic accessibility checks"""
        console.print("[yellow]♿ Checking accessibility...[/yellow]")

        await page.goto(self.base_url, wait_until="networkidle")

        # Check for common accessibility issues
        issues = []

        # Check for images without alt text
        images_without_alt = await page.evaluate("""
            () => Array.from(document.querySelectorAll('img:not([alt])')).length
        """)

        if images_without_alt > 0:
            issues.append(f"{images_without_alt} images without alt text")

        # Check for buttons without labels
        unlabeled_buttons = await page.evaluate("""
            () => Array.from(document.querySelectorAll('button:not([aria-label]):not(:has(*))')).length
        """)

        if unlabeled_buttons > 0:
            issues.append(f"{unlabeled_buttons} buttons without labels")

        if issues:
            for issue in issues:
                self.add_issue("ACCESSIBILITY", issue, "LOW")

            self.results["checks"]["accessibility"] = f"⚠️ {len(issues)} issues"
            console.print(f"[yellow]⚠️ Accessibility issues: {', '.join(issues)}[/yellow]")
        else:
            self.results["checks"]["accessibility"] = "✅ PASS"
            console.print("[green]✅ No critical accessibility issues[/green]")

    async def check_responsive_design(self, page: Page):
        """Test responsive breakpoints"""
        console.print("[yellow]📱 Checking responsive design...[/yellow]")

        viewports = [
            {"name": "Mobile", "width": 375, "height": 667},
            {"name": "Tablet", "width": 768, "height": 1024},
            {"name": "Desktop", "width": 1920, "height": 1080}
        ]

        responsive_issues = []

        for viewport in viewports:
            await page.set_viewport_size({"width": viewport["width"], "height": viewport["height"]})
            await page.goto(self.base_url, wait_until="networkidle")

            # Check for horizontal scroll
            has_scroll = await page.evaluate("""
                () => document.documentElement.scrollWidth > document.documentElement.clientWidth
            """)

            if has_scroll:
                responsive_issues.append(f"{viewport['name']}: Horizontal scroll detected")
                self.add_issue(
                    "RESPONSIVE_ISSUE",
                    f"Horizontal scroll on {viewport['name']} ({viewport['width']}px)",
                    "MEDIUM"
                )

        if responsive_issues:
            self.results["checks"]["responsive"] = f"⚠️ {len(responsive_issues)} issues"
            console.print(f"[yellow]⚠️ Responsive issues: {len(responsive_issues)}[/yellow]")
        else:
            self.results["checks"]["responsive"] = "✅ PASS"
            console.print("[green]✅ Responsive design working[/green]")

    def add_issue(self, issue_type: str, description: str, severity: str):
        """Add issue to results"""
        self.results["issues"].append({
            "type": issue_type,
            "description": description,
            "severity": severity,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

    def generate_report(self):
        """Generate and save final report"""
        console.print("\n[bold cyan]📊 BROWSER MOD - Final Report[/bold cyan]\n")

        # Summary table
        table = Table(title="Test Results", show_header=True)
        table.add_column("Check", style="cyan")
        table.add_column("Result", style="white")

        for check, result in self.results["checks"].items():
            table.add_row(check.replace("_", " ").title(), result)

        console.print(table)

        # Issues summary
        if self.results["issues"]:
            console.print(f"\n[yellow]⚠️ Found {len(self.results['issues'])} issues:[/yellow]\n")

            for i, issue in enumerate(self.results["issues"][:10], 1):  # Show first 10
                severity_color = {
                    "CRITICAL": "red",
                    "HIGH": "yellow",
                    "MEDIUM": "cyan",
                    "LOW": "dim"
                }.get(issue["severity"], "white")

                console.print(f"  {i}. [{severity_color}]{issue['severity']}[/{severity_color}]: {issue['description']}")

            if len(self.results["issues"]) > 10:
                console.print(f"\n  ... and {len(self.results['issues']) - 10} more issues")
        else:
            console.print("\n[green]✅ No issues found![/green]")

        # Performance summary
        if self.results["performance"]:
            console.print(f"\n[cyan]⚡ Performance Metrics:[/cyan]")
            console.print(f"  Page Load: {self.results['performance']['page_load_time']}s")
            console.print(f"  First Paint: {self.results['performance']['first_paint']}ms")
            console.print(f"  FCP: {self.results['performance']['first_contentful_paint']}ms")

        # Save to file
        report_path = Path(f"browser-mod-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json")
        report_path.write_text(json.dumps(self.results, indent=2))
        console.print(f"\n[dim]📄 Full report saved to: {report_path}[/dim]")

        # Return exit code based on critical issues
        critical_count = sum(1 for issue in self.results["issues"] if issue["severity"] == "CRITICAL")
        return 1 if critical_count > 0 else 0


async def quick_render_check(url: str):
    """Quick check if page renders"""
    console.print(f"\n[bold cyan]🚀 Quick Render Check: {url}[/bold cyan]\n")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        try:
            page = await browser.new_page()
            response = await page.goto(url, wait_until="networkidle", timeout=30000)

            if response and response.status < 400:
                console.print(f"[green]✅ Page renders successfully (HTTP {response.status})[/green]")
                return 0
            else:
                console.print(f"[red]❌ Page failed (HTTP {response.status if response else 'timeout'})[/red]")
                return 1

        except Exception as e:
            console.print(f"[red]❌ Render check failed: {e}[/red]")
            return 1
        finally:
            await browser.close()


def main():
    parser = argparse.ArgumentParser(description="BROWSER MOD - Browser testing and monitoring")
    parser.add_argument("--url", default=DEFAULT_URL, help="Base URL to test")
    parser.add_argument("--dev", action="store_true", help="Use localhost:3000")
    parser.add_argument("--check-render", action="store_true", help="Quick render check only")
    parser.add_argument("--full-audit", action="store_true", help="Run full audit")
    parser.add_argument("--headed", action="store_true", help="Show browser window")
    parser.add_argument("--slow", type=int, default=0, help="Slow down operations (ms)")

    args = parser.parse_args()

    # Determine URL
    url = "http://localhost:3000" if args.dev else args.url

    # Quick check
    if args.check_render:
        exit_code = asyncio.run(quick_render_check(url))
        sys.exit(exit_code)

    # Full audit (default)
    mod = BrowserMod(url, headless=not args.headed, slow_mo=args.slow)
    exit_code = asyncio.run(mod.run_full_audit())
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
