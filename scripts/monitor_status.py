#!/usr/bin/env python3
"""
PaiiD Repository Monitor - CLI Tool

Quick terminal interface to check repository status and counters.

Usage:
    python scripts/monitor_status.py              # Full status
    python scripts/monitor_status.py --counters   # Counters only
    python scripts/monitor_status.py --health     # Health check only
    python scripts/monitor_status.py --trend commits --hours 24  # Trend for commits
"""

import argparse
import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

import httpx
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table


# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


console = Console()


class MonitorCLI:
    """CLI interface for PaiiD repository monitor"""

    def __init__(self, base_url: str = None, token: str = None):
        self.base_url = base_url or os.getenv(
            "BACKEND_URL", "https://paiid-backend.onrender.com"
        )
        self.token = token or os.getenv("API_TOKEN")
        self.headers = {}
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

    async def fetch_health(self) -> dict:
        """Fetch monitor health status"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{self.base_url}/api/monitor/health")
            response.raise_for_status()
            return response.json()

    async def fetch_counters(self) -> dict:
        """Fetch all counters"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{self.base_url}/api/monitor/counters", headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def fetch_dashboard(self) -> dict:
        """Fetch complete dashboard data"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{self.base_url}/api/monitor/dashboard", headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def fetch_trend(self, counter_name: str, hours: int = 24) -> dict:
        """Fetch trend data for a counter"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{self.base_url}/api/monitor/trend/{counter_name}",
                params={"hours": hours},
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()

    def display_health(self, health_data: dict) -> None:
        """Display health status"""
        status = health_data.get("status", "unknown")
        services = health_data.get("services", {})

        # Color based on status
        if status == "healthy":
            status_text = "[green]✅ HEALTHY[/green]"
        elif status == "degraded":
            status_text = "[yellow]⚠️  DEGRADED[/yellow]"
        else:
            status_text = "[red]❌ UNHEALTHY[/red]"

        table = Table(title="🔍 Monitor Service Health", show_header=True)
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="magenta")

        table.add_row("Overall Status", status_text)

        for service_name, service_status in services.items():
            if service_status in ["ready", "connected", True]:
                status_icon = "[green]✅ Ready[/green]"
            else:
                status_icon = "[red]❌ Error[/red]"

            # Format service name
            display_name = service_name.replace("_", " ").title()
            table.add_row(display_name, status_icon)

        console.print(table)

    def display_counters(self, counters: dict) -> None:
        """Display counter values"""
        table = Table(title="📊 This Week's Activity", show_header=True)
        table.add_column("Metric", style="cyan", width=20)
        table.add_column("Count", justify="right", style="magenta", width=10)
        table.add_column("Status", style="green", width=10)

        # Group counters by category
        git_metrics = {
            "commits": "Commits",
            "pushes": "Pushes",
        }

        pr_metrics = {
            "pulls_opened": "PRs Opened",
            "pulls_merged": "PRs Merged",
            "pulls_closed": "PRs Closed",
        }

        issue_metrics = {
            "issues_opened": "Issues Opened",
            "issues_closed": "Issues Closed",
        }

        quality_metrics = {
            "build_failures": "Build Failures",
            "test_failures": "Test Failures",
            "conflicts": "Merge Conflicts",
        }

        deployment_metrics = {
            "deployments": "Deployments",
            "hotfixes": "Hotfixes",
        }

        # Display Git activity
        table.add_row("[bold cyan]Git Activity[/bold cyan]", "", "")
        for key, label in git_metrics.items():
            count = counters.get(key, 0)
            status = "🔥" if count > 10 else "✅" if count > 0 else "—"
            table.add_row(f"  {label}", str(count), status)

        # Display PR activity
        table.add_row("[bold cyan]Pull Requests[/bold cyan]", "", "")
        for key, label in pr_metrics.items():
            count = counters.get(key, 0)
            status = "🔥" if count > 5 else "✅" if count > 0 else "—"
            table.add_row(f"  {label}", str(count), status)

        # Display Issue activity
        table.add_row("[bold cyan]Issues[/bold cyan]", "", "")
        for key, label in issue_metrics.items():
            count = counters.get(key, 0)
            opened = counters.get("issues_opened", 0)
            closed = counters.get("issues_closed", 0)
            if key == "issues_closed" and opened > 0:
                status = "🎯" if closed >= opened else "⚠️"
            else:
                status = "✅" if count > 0 else "—"
            table.add_row(f"  {label}", str(count), status)

        # Display Quality metrics
        table.add_row("[bold cyan]Quality[/bold cyan]", "", "")
        for key, label in quality_metrics.items():
            count = counters.get(key, 0)
            status = "❌" if count > 0 else "✅"
            table.add_row(f"  {label}", str(count), status)

        # Display Deployments
        table.add_row("[bold cyan]Deployments[/bold cyan]", "", "")
        for key, label in deployment_metrics.items():
            count = counters.get(key, 0)
            status = "🚀" if count > 5 else "✅" if count > 0 else "—"
            table.add_row(f"  {label}", str(count), status)

        console.print(table)

    def display_trend(self, trend_data: dict) -> None:
        """Display trend data"""
        counter_name = trend_data.get("counter_name", "unknown")
        hours = trend_data.get("hours", 24)
        data_points = trend_data.get("data", [])

        if not data_points:
            console.print(
                f"[yellow]No trend data available for '{counter_name}'[/yellow]"
            )
            return

        # Calculate stats
        values = [point["value"] for point in data_points]
        total = sum(values)
        avg = total / len(values) if values else 0
        max_val = max(values) if values else 0
        min_val = min(values) if values else 0

        # Create simple ASCII chart
        title = f"📈 Trend: {counter_name.replace('_', ' ').title()} (Last {hours}h)"
        table = Table(title=title, show_header=True)
        table.add_column("Statistic", style="cyan")
        table.add_column("Value", justify="right", style="magenta")

        table.add_row("Total Events", str(total))
        table.add_row("Average", f"{avg:.2f}")
        table.add_row("Maximum", str(max_val))
        table.add_row("Minimum", str(min_val))
        table.add_row("Data Points", str(len(data_points)))

        console.print(table)

        # Display recent activity (last 10 points)
        if len(data_points) > 0:
            console.print("\n[bold cyan]Recent Activity:[/bold cyan]")
            recent = data_points[-10:]
            for point in recent:
                timestamp = datetime.fromtimestamp(point["timestamp"])
                time_str = timestamp.strftime("%H:%M:%S")
                value = point["value"]
                bar = "█" * min(value, 20)  # Simple bar chart
                console.print(f"  {time_str}: {bar} ({value})")

    async def run_full_status(self) -> None:
        """Display full status with all information"""
        console.print(
            Panel.fit(
                "[bold cyan]🔍 PaiiD Repository Monitor[/bold cyan]\n"
                f"Connected to: {self.base_url}",
                border_style="cyan",
            )
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # Fetch health
            task1 = progress.add_task("Fetching health status...", total=None)
            try:
                health = await self.fetch_health()
                progress.update(task1, completed=True)
                self.display_health(health)
                console.print()
            except Exception as e:
                progress.update(task1, completed=True)
                console.print(f"[red]❌ Health check failed: {e}[/red]\n")

            # Fetch counters
            task2 = progress.add_task("Fetching counters...", total=None)
            try:
                counters = await self.fetch_counters()
                progress.update(task2, completed=True)
                self.display_counters(counters)
                console.print()
            except Exception as e:
                progress.update(task2, completed=True)
                console.print(f"[red]❌ Counters fetch failed: {e}[/red]\n")
                console.print("[yellow]Tip: Make sure API_TOKEN is set[/yellow]\n")


async def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="PaiiD Repository Monitor CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/monitor_status.py                    # Full status
  python scripts/monitor_status.py --counters         # Counters only
  python scripts/monitor_status.py --health           # Health only
  python scripts/monitor_status.py --trend commits    # Trend for commits
        """,
    )

    parser.add_argument(
        "--counters", action="store_true", help="Show counters only"
    )
    parser.add_argument("--health", action="store_true", help="Show health status only")
    parser.add_argument(
        "--trend", type=str, metavar="COUNTER", help="Show trend for counter"
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=24,
        help="Hours of trend data to show (default: 24)",
    )
    parser.add_argument("--url", type=str, help="Backend URL (default: from env)")
    parser.add_argument("--token", type=str, help="API token (default: from env)")

    args = parser.parse_args()

    cli = MonitorCLI(base_url=args.url, token=args.token)

    try:
        if args.health:
            health = await cli.fetch_health()
            cli.display_health(health)
        elif args.counters:
            counters = await cli.fetch_counters()
            cli.display_counters(counters)
        elif args.trend:
            trend = await cli.fetch_trend(args.trend, args.hours)
            cli.display_trend(trend)
        else:
            # Full status
            await cli.run_full_status()

        # Success message
        console.print(
            "\n[green]✅ Monitor check complete![/green]",
            style="bold",
        )

    except httpx.HTTPError as e:
        console.print(f"\n[red]❌ HTTP Error: {e}[/red]")
        console.print("[yellow]Check your network connection and API token[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]❌ Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

