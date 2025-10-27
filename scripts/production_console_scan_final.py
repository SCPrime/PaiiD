"""
Production Browser Console Scanner - FINAL VERSION
Handles user setup, then scans all 10 workflows for console errors
"""

import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright, Page, ConsoleMessage, Response
from typing import List, Dict, Any
import os

class ProductionConsoleScanFinal:
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
        if msg.type in ["error", "warning"]:
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
            if response.status >= 500:  # Only print server errors
                print(f"[NETWORK {response.status}] {response.request.method} {response.url}")

    async def skip_user_setup(self, page: Page):
        """Skip the user setup screen to get to the radial menu"""
        print("\n[SETUP] Checking for user setup screen...")

        try:
            # Check if setup screen is present
            ai_setup_button = page.locator("text=AI-Guided Setup").first
            manual_setup_button = page.locator("text=Manual Setup").first

            if await ai_setup_button.count() > 0 or await manual_setup_button.count() > 0:
                print("[SETUP] User setup screen detected, clicking 'AI-Guided Setup'...")
                await ai_setup_button.click(timeout=5000)
                await asyncio.sleep(2)

                # Skip AI setup by setting localStorage directly
                print("[SETUP] Bypassing AI setup via localStorage...")
                await page.evaluate("""
                () => {
                    localStorage.setItem('user-setup-complete', 'true');
                    localStorage.setItem('trading-preferences', JSON.stringify({
                        riskTolerance: 'medium',
                        preferredStrategies: ['options'],
                        tradingExperience: 'intermediate'
                    }));
                }
                """)

                # Reload to apply localStorage changes
                print("[SETUP] Reloading page to apply settings...")
                await page.reload(wait_until="domcontentloaded")
                await asyncio.sleep(5)

                print("[SETUP] Setup bypassed successfully!")
                return True
            else:
                print("[SETUP] No setup screen detected, proceeding...")
                return False

        except Exception as e:
            print(f"[SETUP] Could not skip setup: {e}")
            # Try to bypass anyway
            await page.evaluate("""
            () => {
                localStorage.setItem('user-setup-complete', 'true');
                localStorage.setItem('trading-preferences', JSON.stringify({
                    riskTolerance: 'medium',
                    preferredStrategies: ['options'],
                    tradingExperience: 'intermediate'
                }));
            }
            """)
            await page.reload(wait_until="domcontentloaded")
            await asyncio.sleep(5)
            return True

    async def click_workflow_by_coordinates(self, page: Page, workflow_name: str, angle_deg: float) -> bool:
        """Click a workflow wedge by calculating its center coordinates"""
        try:
            # Calculate click coordinates for the wedge
            # Radial menu is centered on the page, wedges at radius ~200px
            script = f"""
            () => {{
                // Find the SVG element
                const svg = document.querySelector('svg');
                if (!svg) return false;

                // Get SVG center coordinates
                const rect = svg.getBoundingClientRect();
                const centerX = rect.left + rect.width / 2;
                const centerY = rect.top + rect.height / 2;

                // Calculate wedge center at angle {angle_deg} degrees, radius 150px
                const angleRad = ({angle_deg} - 90) * Math.PI / 180; // -90 to start from top
                const radius = 150;
                const clickX = centerX + Math.cos(angleRad) * radius;
                const clickY = centerY + Math.sin(angleRad) * radius;

                // Create and dispatch click event at calculated position
                const clickEvent = new MouseEvent('click', {{
                    view: window,
                    bubbles: true,
                    cancelable: true,
                    clientX: clickX,
                    clientY: clickY
                }});

                // Find element at that position and click it
                const element = document.elementFromPoint(clickX, clickY);
                if (element) {{
                    element.dispatchEvent(clickEvent);
                    return true;
                }}
                return false;
            }}
            """
            result = await page.evaluate(script)
            return result
        except Exception as e:
            print(f"[ERROR] Could not click workflow {workflow_name}: {e}")
            return False

    async def test_workflow(self, page: Page, workflow_name: str, angle_deg: float) -> Dict[str, Any]:
        """Test a workflow by clicking its wedge"""
        print(f"\n{'='*80}")
        print(f"Testing Workflow: {workflow_name}")
        print(f"{'='*80}")

        workflow_start = datetime.now()
        errors_before = len(self.errors)
        warnings_before = len(self.warnings)
        network_failures_before = len(self.network_failures)

        try:
            # Click the workflow wedge
            clicked = await self.click_workflow_by_coordinates(page, workflow_name, angle_deg)

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
                f"screenshots/workflow_{workflow_name.replace(' ', '_')}.png"
            )
            os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
            await page.screenshot(path=screenshot_path, full_page=True)

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
        print("PRODUCTION CONSOLE SCAN - FINAL VERSION")
        print(f"Target: https://paiid-frontend.onrender.com")
        print(f"Time: {self.start_time.isoformat()}")
        print(f"{'='*80}\n")

        # Workflow mapping by angle (degrees, clockwise from top)
        workflows = [
            ("Morning Routine", 0),
            ("Active Positions", 36),
            ("Execute Trade", 72),
            ("Research", 108),
            ("AI Recommendations", 144),
            ("P&L Dashboard", 180),
            ("News Review", 216),
            ("Strategy Builder", 252),
            ("Backtesting", 288),
            ("Settings", 324)
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
                await asyncio.sleep(5)

                # Skip user setup if present
                await self.skip_user_setup(page)

                # Wait for radial menu to render
                print("Waiting for radial menu to render...")
                await asyncio.sleep(5)

                # Take screenshot of initial state
                initial_screenshot = os.path.join(os.path.dirname(__file__), "..", "screenshots/radial_menu_ready.png")
                os.makedirs(os.path.dirname(initial_screenshot), exist_ok=True)
                await page.screenshot(path=initial_screenshot, full_page=True)
                print(f"[OK] Screenshot saved: {initial_screenshot}")

                # Capture initial page state
                print(f"[OK] Initial console logs: {len(self.console_logs)}")
                print(f"[OK] Initial errors: {len(self.errors)}")
                print(f"[OK] Initial warnings: {len(self.warnings)}")
                print(f"[OK] Initial network failures: {len(self.network_failures)}")

                # Test each workflow
                for workflow_name, angle in workflows:
                    result = await self.test_workflow(page, workflow_name, angle)
                    self.workflow_results[workflow_name] = result
                    await asyncio.sleep(2)

                # Final wait to catch any delayed errors
                print("\n[WAIT] Waiting for delayed errors...")
                await asyncio.sleep(5)

            except Exception as e:
                print(f"\n[CRITICAL ERROR] during scan: {e}")
                import traceback
                traceback.print_exc()
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
            "critical": [],
            "network": [],
            "sse": [],
            "react": [],
            "known": [],
            "new": []
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
                categories["known"].append({**error, "known_issue": "forceFieldConfidence bug"})

            elif "telemetry" in text and "403" in text:
                categories["known"].append({**error, "known_issue": "Telemetry 403 (auth issue)"})

            # New errors
            else:
                # Filter out known 403 telemetry resource errors
                if not ("403" in text and "telemetry" in text):
                    categories["new"].append(error)

        # Categorize network errors
        for failure in self.network_failures:
            if "telemetry" in failure["url"] and failure["status"] == 403:
                pass  # Skip known telemetry 403s
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
            "all_errors": self.errors[:50],  # Limit to first 50 to keep file manageable
            "all_warnings": self.warnings[:50],
            "all_network_failures": self.network_failures[:50]
        }

        # Save report to file
        report_path = os.path.join(os.path.dirname(__file__), "..", "PRODUCTION_CONSOLE_SCAN_FINAL.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n{'='*80}")
        print("PRODUCTION CONSOLE SCAN - RESULTS")
        print(f"{'='*80}")
        print(f"Duration: {duration:.2f} seconds")
        print(f"Workflows Tested: {len(self.workflow_results)}")
        print(f"\nConsole Output:")
        print(f"  - Total Logs: {len(self.console_logs)}")
        print(f"  - Errors: {len(self.errors)}")
        print(f"  - Warnings: {len(self.warnings)}")
        print(f"  - Network Failures: {len(self.network_failures)}")
        print(f"\nCategorized Errors:")
        print(f"  - Critical: {len(categorized_errors['critical'])}")
        print(f"  - SSE: {len(categorized_errors['sse'])}")
        print(f"  - React: {len(categorized_errors['react'])}")
        print(f"  - Known: {len(categorized_errors['known'])}")
        print(f"  - New: {len(categorized_errors['new'])}")
        print(f"  - Network: {len(categorized_errors['network'])}")
        print(f"\nReport saved to: {report_path}")
        print(f"{'='*80}\n")

        # Check forceFieldConfidence error
        forcefield_found = any("forcefieldconfidence" in err["text"].lower() for err in self.errors)
        if forcefield_found:
            print("[FAIL] forceFieldConfidence error STILL PRESENT")
        else:
            print("[SUCCESS] forceFieldConfidence error NOT FOUND - HOTFIX WORKED!")

        # Print critical errors
        if categorized_errors["critical"]:
            print(f"\n[ALERT] {len(categorized_errors['critical'])} CRITICAL ERRORS:")
            for i, error in enumerate(categorized_errors["critical"][:3], 1):
                print(f"\n{i}. {error['text'][:300]}")
                if error.get('location'):
                    print(f"   Location: {error['location'].get('url', 'Unknown')}")

        # Print new errors
        if categorized_errors["new"]:
            print(f"\n[ALERT] {len(categorized_errors['new'])} NEW ERRORS:")
            for i, error in enumerate(categorized_errors["new"][:3], 1):
                print(f"\n{i}. {error['text'][:300]}")

        # Print workflow summary
        print(f"\n{'='*80}")
        print("WORKFLOW TEST SUMMARY")
        print(f"{'='*80}")
        for workflow, result in self.workflow_results.items():
            status_icon = "[OK]" if result["status"] == "success" else "[FAIL]"
            print(f"{status_icon} {workflow}: {result['status']}")
            if result["status"] == "success":
                print(f"      Errors: {result['new_errors']}, Warnings: {result['new_warnings']}")
        print(f"{'='*80}\n")

async def main():
    scanner = ProductionConsoleScanFinal()
    await scanner.scan()

if __name__ == "__main__":
    asyncio.run(main())
