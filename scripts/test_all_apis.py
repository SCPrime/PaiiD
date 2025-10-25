#!/usr/bin/env python3
"""
🔍 API Health Check & Monitoring Script
Tests all PaiiD APIs and external integrations
"""
import asyncio
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

import httpx
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.layout import Layout

console = Console()

# API Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "https://paiid-backend.onrender.com")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://paiid-frontend.onrender.com")
API_TOKEN = os.getenv("API_TOKEN", "rnd_bDRqi1TvLvd3rC78yvUSgDraH2Kl")

# Test configuration
TIMEOUT = 30.0
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

class APIHealthChecker:
    """Comprehensive API health checker"""

    def __init__(self):
        self.results: Dict[str, dict] = {}
        self.start_time = datetime.now()

    async def check_endpoint(
        self,
        name: str,
        url: str,
        method: str = "GET",
        headers: Optional[Dict] = None,
        require_auth: bool = False
    ) -> dict:
        """Check a single endpoint"""
        test_headers = headers or {}
        if require_auth:
            test_headers.update(HEADERS)

        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                start = datetime.now()

                if method == "GET":
                    response = await client.get(url, headers=test_headers)
                elif method == "POST":
                    response = await client.post(url, headers=test_headers, json={})
                else:
                    response = await client.request(method, url, headers=test_headers)

                latency_ms = (datetime.now() - start).total_seconds() * 1000

                return {
                    "name": name,
                    "url": url,
                    "status": "✅ OK" if response.status_code < 400 else "⚠️ ERROR",
                    "status_code": response.status_code,
                    "latency_ms": round(latency_ms, 2),
                    "response_size": len(response.content),
                    "success": response.status_code < 400
                }
        except httpx.TimeoutException:
            return {
                "name": name,
                "url": url,
                "status": "❌ TIMEOUT",
                "status_code": 0,
                "latency_ms": TIMEOUT * 1000,
                "response_size": 0,
                "success": False,
                "error": "Request timeout"
            }
        except Exception as e:
            return {
                "name": name,
                "url": url,
                "status": "❌ FAILED",
                "status_code": 0,
                "latency_ms": 0,
                "response_size": 0,
                "success": False,
                "error": str(e)
            }

    async def check_all_endpoints(self):
        """Check all API endpoints"""

        endpoints = [
            # Core Health Checks
            ("Backend Health", f"{BACKEND_URL}/api/health", "GET", False),
            ("Frontend", FRONTEND_URL, "GET", False),

            # Authentication & Users
            ("Auth - Login", f"{BACKEND_URL}/api/auth/token", "POST", False),
            ("Users", f"{BACKEND_URL}/api/users/me", "GET", True),

            # Market Data (Tradier Integration)
            ("Market - Indices", f"{BACKEND_URL}/api/market/indices", "GET", True),
            ("Market - Quote", f"{BACKEND_URL}/api/market/quote/AAPL", "GET", True),
            ("Market - Search", f"{BACKEND_URL}/api/market/search?query=AAPL", "GET", True),

            # Options Data
            ("Options - Chain", f"{BACKEND_URL}/api/options/chain/AAPL", "GET", True),
            ("Options - Greeks", f"{BACKEND_URL}/api/options/greeks/AAPL", "GET", True),

            # Portfolio & Positions (Alpaca Integration)
            ("Portfolio - Account", f"{BACKEND_URL}/api/portfolio", "GET", True),
            ("Positions - List", f"{BACKEND_URL}/api/positions", "GET", True),

            # Orders (Alpaca Integration)
            ("Orders - List", f"{BACKEND_URL}/api/orders", "GET", True),
            ("Orders - History", f"{BACKEND_URL}/api/orders/history", "GET", True),

            # AI & ML
            ("AI - Chat", f"{BACKEND_URL}/api/ai/chat", "POST", True),
            ("AI - Recommendations", f"{BACKEND_URL}/api/ai/recommendations", "GET", True),
            ("ML - Sentiment", f"{BACKEND_URL}/api/ml/sentiment/AAPL", "GET", True),

            # Analytics & Backtesting
            ("Analytics - P&L", f"{BACKEND_URL}/api/analytics/pnl", "GET", True),
            ("Backtesting - Run", f"{BACKEND_URL}/api/backtesting/strategies", "GET", True),

            # News & Market Intel
            ("News - Latest", f"{BACKEND_URL}/api/news", "GET", True),
            ("News - Symbol", f"{BACKEND_URL}/api/news/AAPL", "GET", True),

            # Strategies
            ("Strategies - List", f"{BACKEND_URL}/api/strategies", "GET", True),
            ("Strategies - Active", f"{BACKEND_URL}/api/strategies/active", "GET", True),

            # Monitoring & Telemetry
            ("Monitor - GitHub", f"{BACKEND_URL}/api/monitor/github/webhook", "POST", False),
            ("Telemetry - Events", f"{BACKEND_URL}/api/telemetry/events", "GET", True),

            # Scheduler & Automation
            ("Scheduler - Jobs", f"{BACKEND_URL}/api/scheduler/jobs", "GET", True),

            # Settings & Config
            ("Settings - User", f"{BACKEND_URL}/api/settings", "GET", True),
        ]

        console.print("\n[cyan]Testing All API Endpoints...[/cyan]\n")

        tasks = [
            self.check_endpoint(name, url, method, require_auth=auth)
            for name, url, method, auth in endpoints
        ]

        results = await asyncio.gather(*tasks)

        return results

    async def check_external_apis(self):
        """Check external API integrations"""

        console.print("\n[cyan]Testing External API Integrations...[/cyan]\n")

        checks = []

        # Check if backend can reach Tradier
        tradier_check = await self.check_endpoint(
            "Tradier API (via Backend)",
            f"{BACKEND_URL}/api/market/quote/SPY",
            "GET",
            require_auth=True
        )
        checks.append(tradier_check)

        # Check if backend can reach Alpaca
        alpaca_check = await self.check_endpoint(
            "Alpaca API (via Backend)",
            f"{BACKEND_URL}/api/portfolio",
            "GET",
            require_auth=True
        )
        checks.append(alpaca_check)

        # Check Claude AI integration
        claude_check = await self.check_endpoint(
            "Claude AI (via Backend)",
            f"{BACKEND_URL}/api/ai/recommendations",
            "GET",
            require_auth=True
        )
        checks.append(claude_check)

        return checks

    def generate_report(self, endpoint_results: List[dict], external_results: List[dict]):
        """Generate comprehensive health report"""

        # Calculate stats
        total_endpoints = len(endpoint_results)
        successful = sum(1 for r in endpoint_results if r["success"])
        failed = total_endpoints - successful
        avg_latency = sum(r["latency_ms"] for r in endpoint_results) / total_endpoints if total_endpoints > 0 else 0

        external_total = len(external_results)
        external_success = sum(1 for r in external_results if r["success"])

        # Create summary table
        summary = Table(title="📊 API Health Summary", show_header=True, header_style="bold cyan")
        summary.add_column("Metric", style="cyan")
        summary.add_column("Value", style="white")
        summary.add_column("Status", style="bold")

        summary.add_row(
            "Total Endpoints",
            str(total_endpoints),
            "✅" if total_endpoints > 0 else "❌"
        )
        summary.add_row(
            "Successful",
            f"{successful}/{total_endpoints}",
            "✅" if successful == total_endpoints else "⚠️"
        )
        summary.add_row(
            "Failed",
            str(failed),
            "✅" if failed == 0 else "❌"
        )
        summary.add_row(
            "Success Rate",
            f"{(successful/total_endpoints*100):.1f}%",
            "✅" if successful/total_endpoints >= 0.9 else "⚠️"
        )
        summary.add_row(
            "Average Latency",
            f"{avg_latency:.2f}ms",
            "✅" if avg_latency < 1000 else "⚠️"
        )
        summary.add_row(
            "External APIs",
            f"{external_success}/{external_total}",
            "✅" if external_success == external_total else "❌"
        )

        console.print(summary)

        # Detailed endpoint table
        details = Table(title="\n📝 Endpoint Details", show_header=True, header_style="bold cyan")
        details.add_column("Status", style="white", width=10)
        details.add_column("Endpoint", style="cyan", width=30)
        details.add_column("Code", justify="center", width=8)
        details.add_column("Latency", justify="right", width=12)
        details.add_column("Size", justify="right", width=10)

        # Sort by status (failed first)
        sorted_results = sorted(endpoint_results, key=lambda x: (x["success"], x["name"]))

        for result in sorted_results:
            latency_str = f"{result['latency_ms']:.0f}ms"
            size_str = f"{result['response_size']} B"

            details.add_row(
                result["status"],
                result["name"],
                str(result["status_code"]) if result["status_code"] > 0 else "N/A",
                latency_str,
                size_str
            )

        console.print(details)

        # External APIs table
        if external_results:
            external_table = Table(title="\n🌐 External API Status", show_header=True, header_style="bold cyan")
            external_table.add_column("Status", style="white", width=10)
            external_table.add_column("Service", style="cyan", width=30)
            external_table.add_column("Latency", justify="right", width=12)

            for result in external_results:
                external_table.add_row(
                    result["status"],
                    result["name"],
                    f"{result['latency_ms']:.0f}ms"
                )

            console.print(external_table)

        # Overall health assessment
        overall_health = "✅ HEALTHY" if failed == 0 and external_success == external_total else \
                        "⚠️ DEGRADED" if successful/total_endpoints >= 0.7 else \
                        "❌ CRITICAL"

        health_color = "green" if "HEALTHY" in overall_health else \
                      "yellow" if "DEGRADED" in overall_health else "red"

        console.print(f"\n[{health_color}]Overall System Health: {overall_health}[/{health_color}]\n")

        return {
            "total": total_endpoints,
            "successful": successful,
            "failed": failed,
            "success_rate": successful/total_endpoints*100 if total_endpoints > 0 else 0,
            "avg_latency_ms": avg_latency,
            "external_success": external_success,
            "external_total": external_total,
            "health": overall_health
        }

async def main():
    """Main execution"""
    console.print(Panel.fit(
        "[bold cyan]PaiiD API Health Check & Monitoring[/bold cyan]\n"
        f"Backend: {BACKEND_URL}\n"
        f"Frontend: {FRONTEND_URL}\n"
        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        border_style="cyan"
    ))

    checker = APIHealthChecker()

    # Run all checks
    endpoint_results = await checker.check_all_endpoints()
    external_results = await checker.check_external_apis()

    # Generate report
    stats = checker.generate_report(endpoint_results, external_results)

    # Save results to JSON
    import json
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "backend_url": BACKEND_URL,
        "frontend_url": FRONTEND_URL,
        "summary": stats,
        "endpoints": endpoint_results,
        "external_apis": external_results
    }

    report_file = "api-health-report.json"
    with open(report_file, "w") as f:
        json.dump(report_data, f, indent=2)

    console.print(f"[green]✅ Report saved to: {report_file}[/green]\n")

    # Exit with appropriate code
    if stats["success_rate"] < 70:
        console.print("[red]❌ Critical: Success rate below 70%[/red]")
        sys.exit(1)
    elif stats["success_rate"] < 90:
        console.print("[yellow]⚠️ Warning: Success rate below 90%[/yellow]")
        sys.exit(0)
    else:
        console.print("[green]✅ All systems operational[/green]")
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
