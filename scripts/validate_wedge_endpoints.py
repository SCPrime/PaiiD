#!/usr/bin/env python3
"""
API Endpoint Validator for PaiiD Wedges
Pre-flight check to verify all wedge-required endpoints are accessible
"""
import asyncio
import os
from datetime import datetime
from typing import Dict, List

import httpx
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "https://paiid-backend.onrender.com")
API_TOKEN = os.getenv("API_TOKEN", "rnd_bDRqi1TvLvd3rC78yvUSgDraH2Kl")
TIMEOUT = 30.0

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

# Wedge-to-Endpoint Mapping
WEDGE_ENDPOINTS = {
    "1. Morning Routine": [
        ("/api/account", "GET", True, "Portfolio account data"),
        ("/api/market/indices", "GET", True, "Market indices (SPY, QQQ)"),
    ],
    "2. News Review": [
        ("/api/news/providers", "GET", False, "News source providers"),
        ("/api/news/market", "GET", False, "Market news articles"),
        ("/api/news/sentiment/market", "GET", False, "News sentiment analysis"),
    ],
    "3. AI Recommendations": [
        ("/api/ai/recommendations", "GET", True, "AI trade recommendations"),
    ],
    "4. Active Positions": [
        ("/api/positions", "GET", True, "Current positions from Alpaca"),
        ("/api/positions/greeks", "GET", True, "Portfolio Greeks aggregation"),
    ],
    "5. P&L Dashboard": [
        ("/api/portfolio", "GET", True, "Portfolio summary"),
        ("/api/analytics/pnl", "GET", True, "P&L historical data"),
    ],
    "6. Strategy Builder": [
        ("/api/strategies/list", "GET", True, "List saved strategies"),
        ("/api/strategies/templates", "GET", True, "Strategy templates"),
    ],
    "7. Backtesting": [
        ("/api/backtesting/strategies", "GET", True, "Strategies available for backtest"),
        ("/api/market/historical/AAPL", "GET", True, "Historical market data (Tradier)"),
    ],
    "8. Execute Trade": [
        ("/api/market/quote/AAPL", "GET", True, "Real-time quote from Tradier"),
        ("/api/market/search", "GET", True, "Symbol search/lookup"),
        ("/api/order-templates", "GET", True, "Order templates"),
    ],
    "9. Options Trading": [
        ("/api/options/chain/SPY", "GET", True, "Options chain from Tradier"),
        ("/api/options/greeks/SPY", "GET", True, "Options Greeks calculation"),
    ],
    "10. Repo Monitor": [
        ("/api/monitor/github", "GET", False, "GitHub repository stats"),
    ],
    "11. ML Intelligence": [
        ("/api/ml/sentiment/AAPL", "GET", True, "ML sentiment analysis"),
        ("/api/ml/patterns/AAPL", "GET", True, "ML pattern recognition"),
    ],
}

async def check_endpoint(
    client: httpx.AsyncClient,
    endpoint: str,
    method: str,
    require_auth: bool,
    description: str
) -> Dict:
    """Check a single API endpoint"""

    url = f"{BACKEND_URL}{endpoint}"
    headers = HEADERS if require_auth else {}

    try:
        start = datetime.now()

        if method == "GET":
            response = await client.get(url, headers=headers, timeout=TIMEOUT)
        elif method == "POST":
            response = await client.post(url, headers=headers, json={}, timeout=TIMEOUT)
        else:
            response = await client.request(method, url, headers=headers, timeout=TIMEOUT)

        latency_ms = (datetime.now() - start).total_seconds() * 1000

        return {
            "endpoint": endpoint,
            "method": method,
            "status": response.status_code,
            "latency_ms": round(latency_ms, 2),
            "success": response.status_code < 400,
            "description": description,
            "error": None
        }

    except httpx.TimeoutException:
        return {
            "endpoint": endpoint,
            "method": method,
            "status": 0,
            "latency_ms": TIMEOUT * 1000,
            "success": False,
            "description": description,
            "error": "Timeout"
        }
    except Exception as e:
        return {
            "endpoint": endpoint,
            "method": method,
            "status": 0,
            "latency_ms": 0,
            "success": False,
            "description": description,
            "error": str(e)
        }

async def validate_all_endpoints():
    """Validate all wedge endpoints"""

    console.print(Panel.fit(
        "[bold cyan]PaiiD Wedge API Endpoint Validator[/bold cyan]\n"
        f"Backend: {BACKEND_URL}\n"
        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        border_style="cyan"
    ))

    console.print("\n[cyan]Testing all wedge-required endpoints...[/cyan]\n")

    wedge_results = {}

    async with httpx.AsyncClient() as client:
        for wedge_name, endpoints in WEDGE_ENDPOINTS.items():
            console.print(f"[yellow]Testing {wedge_name}...[/yellow]")

            tasks = [
                check_endpoint(client, endpoint, method, require_auth, desc)
                for endpoint, method, require_auth, desc in endpoints
            ]

            results = await asyncio.gather(*tasks)
            wedge_results[wedge_name] = results

    # Generate report
    generate_report(wedge_results)

    # Save to JSON
    save_json_report(wedge_results)

def generate_report(wedge_results: Dict):
    """Generate detailed validation report"""

    all_endpoints = []
    wedge_stats = {}

    for wedge_name, results in wedge_results.items():
        total = len(results)
        successful = sum(1 for r in results if r["success"])
        failed = total - successful

        wedge_stats[wedge_name] = {
            "total": total,
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / total * 100) if total > 0 else 0
        }

        all_endpoints.extend(results)

    # Summary Table
    summary_table = Table(title="\nWedge Validation Summary", show_header=True, header_style="bold cyan")
    summary_table.add_column("Wedge", style="cyan", width=25)
    summary_table.add_column("Success", justify="center", width=10)
    summary_table.add_column("Failed", justify="center", width=10)
    summary_table.add_column("Rate", justify="right", width=10)

    for wedge_name, stats in wedge_stats.items():
        status_icon = "✅" if stats["failed"] == 0 else "⚠️" if stats["success_rate"] >= 50 else "❌"
        summary_table.add_row(
            f"{status_icon} {wedge_name}",
            f"{stats['successful']}/{stats['total']}",
            str(stats["failed"]),
            f"{stats['success_rate']:.0f}%"
        )

    console.print(summary_table)

    # Detailed Endpoint Table
    details_table = Table(title="\nDetailed Endpoint Results", show_header=True, header_style="bold cyan")
    details_table.add_column("Status", width=8)
    details_table.add_column("Endpoint", style="white", width=35)
    details_table.add_column("Method", justify="center", width=8)
    details_table.add_column("Code", justify="center", width=6)
    details_table.add_column("Latency", justify="right", width=10)
    details_table.add_column("Description", style="dim", width=30)

    # Sort by status (failed first)
    sorted_endpoints = sorted(all_endpoints, key=lambda x: (x["success"], x["endpoint"]))

    for result in sorted_endpoints:
        status_icon = "✅" if result["success"] else "❌"
        code_str = str(result["status"]) if result["status"] > 0 else "ERR"
        latency_str = f"{result['latency_ms']:.0f}ms" if result["latency_ms"] > 0 else "N/A"

        details_table.add_row(
            status_icon,
            result["endpoint"],
            result["method"],
            code_str,
            latency_str,
            result["description"]
        )

    console.print(details_table)

    # Failed Endpoints (if any)
    failed_endpoints = [r for r in all_endpoints if not r["success"]]
    if failed_endpoints:
        console.print("\n[red]❌ Failed Endpoints:[/red]")
        for result in failed_endpoints:
            error_msg = result.get("error", "Unknown error")
            console.print(f"  [red]•[/red] {result['endpoint']} - {error_msg}")

    # Overall Stats
    total_endpoints = len(all_endpoints)
    total_success = sum(1 for r in all_endpoints if r["success"])
    total_failed = total_endpoints - total_success
    overall_rate = (total_success / total_endpoints * 100) if total_endpoints > 0 else 0

    console.print(f"\n[bold]Overall Endpoint Health:[/bold]")
    console.print(f"  Total Endpoints: {total_endpoints}")
    console.print(f"  Successful: {total_success}")
    console.print(f"  Failed: {total_failed}")
    console.print(f"  Success Rate: {overall_rate:.1f}%")

    if overall_rate >= 90:
        console.print(f"\n[green]✅ Excellent! All wedges should work properly.[/green]")
    elif overall_rate >= 70:
        console.print(f"\n[yellow]⚠️  Some endpoints failing. Check failed APIs above.[/yellow]")
    else:
        console.print(f"\n[red]❌ Critical! Many endpoints unavailable. Check backend status.[/red]")

def save_json_report(wedge_results: Dict):
    """Save validation results to JSON"""
    import json

    report_data = {
        "timestamp": datetime.now().isoformat(),
        "backend_url": BACKEND_URL,
        "wedge_results": {}
    }

    for wedge_name, results in wedge_results.items():
        report_data["wedge_results"][wedge_name] = {
            "endpoints": results,
            "total": len(results),
            "successful": sum(1 for r in results if r["success"]),
            "failed": sum(1 for r in results if not r["success"])
        }

    report_file = "wedge-endpoint-validation.json"
    with open(report_file, "w") as f:
        json.dump(report_data, f, indent=2)

    console.print(f"\n[green]📄 Report saved to: {report_file}[/green]")

async def main():
    """Main execution"""
    try:
        await validate_all_endpoints()
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Validation interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]❌ Error: {e}[/red]")

if __name__ == "__main__":
    asyncio.run(main())
