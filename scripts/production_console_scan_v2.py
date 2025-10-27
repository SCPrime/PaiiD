"""
Production Browser Console Scanner V2
Enhanced version with SVG click handling and screenshots
"""

import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright, Page, ConsoleMessage, Response
from typing import List, Dict, Any
import os

class ProductionConsoleScanV2:
    def __init__(self):
        self.console_logs = []
        self.errors = []
        self.warnings = []
        self.network_failures = []
        self.page_errors = []
        self.workflow_results = {}
        self.start_time = datetime.now()

        # Known errors to check for
        self.known_errors = [
            "forceFieldConfidence",
            "EventSource",
            "403",
            "CSRF",
            "500",
            "ReferenceError",
            "TypeError",
            "hydration"
        ]

    async def handle_console(self, msg: ConsoleMessage):
        """Capture all console messages"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": msg.type,
            "text": msg.text,
            "location": msg.location if hasattr(msg, 'location') else None
        }

        self.console_logs.append(log_entry)

        if msg.type == "error":
            self.errors.append(log_entry)
        elif msg.type == "warning":
            self.warnings.append(log_entry)

        # Print to terminal for real-time monitoring
        print(f"[{msg.type.upper()}] {msg.text[:150]}")

    async def handle_page_error(self, error):
        """Capture unhandled page errors"""
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "error": str(error),
            "type": "PageError"
        }
        self.page_errors.append(error_entry)
        print(f"[PAGE ERROR] {error}")

    async def handle_response(self, response: Response):
        """Capture network failures"""
        if response.status >= 400:
            failure = {
                "timestamp": datetime.now().isoformat(),
                "url": response.url,
                "status": response.status,
                "statusText": response.status_text,
                "method": response.request.method
            }
            self.network_failures.append(failure)
            print(f"[NETWORK {response.status}] {response.request.method} {response.url}")

    async def wait_for_stability(self, page: Page, timeout_ms: int = 5000):
        """Wait for network to be idle and page to stabilize"""
        try:
            await page.wait_for_load_state("networkidle", timeout=timeout_ms)
        except Exception as e:
            print(f"[TIMEOUT] Network not idle after {timeout_ms}ms")

    async def click_svg_wedge(self, page: Page, workflow_index: int) -> bool:
        """Click a specific SVG wedge by index (0-9)"""
        try:
            # Try to click using JavaScript (more reliable for SVG)
            script = f"""
            () => {{
                // Find all path elements with click handlers
                const wedges = document.querySelectorAll('svg path[style*="cursor: pointer"]');
                if (wedges && wedges[{workflow_index}]) {{
                    wedges[{workflow_index}].click();
                    return true;
                }}
                return false;
            }}
            """
            result = await page.evaluate(script)
            return result
        except Exception as e:
            print(f"[ERROR] Could not click SVG wedge {workflow_index}: {e}")
            return False

    async def test_workflow_by_index(self, page: Page, index: int, workflow_name: str) -> Dict[str, Any]:
        """Test a workflow by clicking its wedge index"""
        print(f"\n{'='*80}")
        print(f"Testing Workflow {index + 1}/10: {workflow_name}")
        print(f"{'='*80}")

        workflow_start = datetime.now()
        errors_before = len(self.errors)
        warnings_before = len(self.warnings)
        network_failures_before = len(self.network_failures)

        try:
            # Click the SVG wedge
            clicked = await self.click_svg_wedge(page, index)

            if not clicked:
                print(f"[FAIL] Could not click workflow: {workflow_name}")
                return {
                    "workflow": workflow_name,
                    "status": "not_clicked",
                    "errors": 0,
                    "warnings": 0,
                    "network_failures": 0
                }

            print(f"[OK] Clicked workflow: {workflow_name}")

            # Wait for workflow to render and capture errors
            await asyncio.sleep(5)
            await self.wait_for_stability(page, 3000)

            # Check for specific known errors in console
            known_errors_found = []
            for log in self.console_logs[-30:]:  # Check last 30 logs
                for known_error in self.known_errors:
                    if known_error.lower() in log["text"].lower():
                        known_errors_found.append(known_error)

            workflow_duration = (datetime.now() - workflow_start).total_seconds()

            result = {
                "workflow": workflow_name,
                "status": "success",
                "duration_seconds": workflow_duration,
                "new_errors": len(self.errors) - errors_before,
                "new_warnings": len(self.warnings) - warnings_before,
                "new_network_failures": len(self.network_failures) - network_failures_before,
                "known_errors_found": list(set(known_errors_found))
            }

            print(f"[OK] Workflow tested: {workflow_name}")
            print(f"  - Duration: {workflow_duration:.2f}s")
            print(f"  - New errors: {result['new_errors']}")
            print(f"  - New warnings: {result['new_warnings']}")
            print(f"  - New network failures: {result['new_network_failures']}")
            if known_errors_found:
                print(f"  - Known errors detected: {', '.join(set(known_errors_found))}")

            # Take screenshot of workflow
            screenshot_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                f"screenshots/workflow_{index}_{workflow_name.replace(' ', '_')}.png"
            )
            os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"  - Screenshot saved: {screenshot_path}")

            return result

        except Exception as e:
            print(f"[ERROR] Error testing workflow {workflow_name}: {e}")
            return {
                "workflow": workflow_name,
                "status": "error",
                "error": str(e),
                "new_errors": len(self.errors) - errors_before,
                "new_warnings": len(self.warnings) - warnings_before,
                "new_network_failures": len(self.network_failures) - network_failures_before
            }

    async def scan(self):
        """Main scanning function"""
        print(f"\n{'='*80}")
        print("PRODUCTION CONSOLE SCAN V2 - STARTING")
        print(f"Target: https://paiid-frontend.onrender.com")
        print(f"Time: {self.start_time.isoformat()}")
        print(f"{'='*80}\n")

        # Workflow mapping by radial menu index (0-9 clockwise from top)
        workflows = [
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

        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080}
            )
            page = await context.new_page()

            # Set up event listeners
            page.on("console", self.handle_console)
            page.on("pageerror", self.handle_page_error)
            page.on("response", self.handle_response)

            try:
                # Navigate to production frontend
                print("Navigating to production frontend...")
                await page.goto("https://paiid-frontend.onrender.com", wait_until="domcontentloaded", timeout=60000)

                # Wait for radial menu to render
                print("Waiting for radial menu to render...")
                await asyncio.sleep(8)  # Longer wait for D3.js rendering
                await self.wait_for_stability(page, 5000)

                # Take screenshot of initial state
                initial_screenshot = os.path.join(os.path.dirname(__file__), "..", "screenshots/initial_radial_menu.png")
                os.makedirs(os.path.dirname(initial_screenshot), exist_ok=True)
                await page.screenshot(path=initial_screenshot, full_page=True)
                print(f"Initial screenshot saved: {initial_screenshot}")

                # Capture initial page state
                print("[OK] Page loaded successfully")
                print(f"[OK] Initial console logs: {len(self.console_logs)}")
                print(f"[OK] Initial errors: {len(self.errors)}")
                print(f"[OK] Initial warnings: {len(self.warnings)}")
                print(f"[OK] Initial network failures: {len(self.network_failures)}")

                # Test each workflow by index
                for i, workflow in enumerate(workflows):
                    result = await self.test_workflow_by_index(page, i, workflow)
                    self.workflow_results[workflow] = result

                    # Wait before next workflow
                    await asyncio.sleep(2)

                # Final wait to catch any delayed errors
                print("\nWaiting for delayed errors...")
                await asyncio.sleep(5)

            except Exception as e:
                print(f"\n[CRITICAL ERROR] during scan: {e}")
                self.page_errors.append({
                    "timestamp": datetime.now().isoformat(),
                    "error": str(e),
                    "type": "ScanError"
                })

            finally:
                await browser.close()

        # Generate report
        self.generate_report()

    def categorize_errors(self) -> Dict[str, List[Dict]]:
        """Categorize errors by type"""
        categories = {
            "critical": [],  # TypeErrors, ReferenceErrors, crashes
            "network": [],   # 403, 500, timeouts
            "sse": [],       # EventSource errors
            "react": [],     # Hydration, rendering issues
            "known": [],     # Previously tracked errors
            "new": []        # New unknown errors
        }

        for error in self.errors:
            text = error["text"].lower()

            # Critical errors
            if any(x in text for x in ["typeerror", "referenceerror", "syntaxerror", "cannot read", "undefined is not"]):
                categories["critical"].append(error)

            # SSE errors
            elif any(x in text for x in ["eventsource", "sse", "server-sent"]):
                categories["sse"].append(error)

            # React errors
            elif any(x in text for x in ["hydration", "react", "component"]):
                categories["react"].append(error)

            # Known errors
            elif "forcefieldconfidence" in text:
                categories["known"].append({**error, "known_issue": "forceFieldConfidence bug (should be fixed)"})

            # Network errors (telemetry 403s are known)
            elif "telemetry" in text and "403" in text:
                categories["known"].append({**error, "known_issue": "Telemetry 403 (known auth issue)"})

            # New errors
            else:
                categories["new"].append(error)

        # Network errors
        for failure in self.network_failures:
            if "telemetry" in failure["url"] and failure["status"] == 403:
                categories["known"].append({**failure, "known_issue": "Telemetry 403 (known auth issue)"})
            else:
                categories["network"].append(failure)

        return categories

    def generate_report(self):
        """Generate comprehensive JSON report"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        categorized_errors = self.categorize_errors()

        report = {
            "scan_metadata": {
                "start_time": self.start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "target_url": "https://paiid-frontend.onrender.com",
                "workflows_tested": len(self.workflow_results)
            },
            "summary": {
                "total_console_logs": len(self.console_logs),
                "total_errors": len(self.errors),
                "total_warnings": len(self.warnings),
                "total_network_failures": len(self.network_failures),
                "total_page_errors": len(self.page_errors),
                "critical_errors": len(categorized_errors["critical"]),
                "sse_errors": len(categorized_errors["sse"]),
                "react_errors": len(categorized_errors["react"]),
                "known_errors": len(categorized_errors["known"]),
                "new_errors": len(categorized_errors["new"]),
                "network_errors": len(categorized_errors["network"])
            },
            "categorized_errors": categorized_errors,
            "workflow_results": self.workflow_results,
            "all_errors": self.errors,
            "all_warnings": self.warnings,
            "all_network_failures": self.network_failures,
            "all_page_errors": self.page_errors
        }

        # Save report to file
        report_path = os.path.join(os.path.dirname(__file__), "..", "PRODUCTION_CONSOLE_SCAN_REPORT_V2.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n{'='*80}")
        print("PRODUCTION CONSOLE SCAN V2 - COMPLETE")
        print(f"{'='*80}")
        print(f"Duration: {duration:.2f} seconds")
        print(f"Total Console Logs: {len(self.console_logs)}")
        print(f"Total Errors: {len(self.errors)}")
        print(f"Total Warnings: {len(self.warnings)}")
        print(f"Total Network Failures: {len(self.network_failures)}")
        print(f"Total Page Errors: {len(self.page_errors)}")
        print(f"\nCategorized Errors:")
        print(f"  - Critical: {len(categorized_errors['critical'])}")
        print(f"  - SSE: {len(categorized_errors['sse'])}")
        print(f"  - React: {len(categorized_errors['react'])}")
        print(f"  - Known: {len(categorized_errors['known'])}")
        print(f"  - New: {len(categorized_errors['new'])}")
        print(f"  - Network: {len(categorized_errors['network'])}")
        print(f"\nReport saved to: {report_path}")
        print(f"{'='*80}\n")

        # Print critical errors for immediate attention
        if categorized_errors["critical"]:
            print("\n[ALERT] CRITICAL ERRORS DETECTED:")
            for i, error in enumerate(categorized_errors["critical"][:5], 1):
                print(f"\n{i}. {error['text'][:300]}")
                if error.get('location'):
                    print(f"   Location: {error['location']}")

        # Check if forceFieldConfidence error is gone
        forcefield_found = any("forcefieldconfidence" in err["text"].lower() for err in self.errors)
        if forcefield_found:
            print("\n[FAIL] forceFieldConfidence error STILL PRESENT (hotfix failed)")
        else:
            print("\n[SUCCESS] forceFieldConfidence error NOT FOUND (hotfix successful)")

        # Print new unknown errors
        if categorized_errors["new"]:
            print(f"\n[ALERT] {len(categorized_errors['new'])} NEW UNKNOWN ERRORS:")
            for i, error in enumerate(categorized_errors["new"][:3], 1):
                print(f"\n{i}. {error['text'][:300]}")

async def main():
    scanner = ProductionConsoleScanV2()
    await scanner.scan()

if __name__ == "__main__":
    asyncio.run(main())
