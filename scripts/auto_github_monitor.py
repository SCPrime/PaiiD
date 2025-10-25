#!/usr/bin/env python3
"""
🔍 Auto GitHub Monitor
Automatically tracks GitHub events and updates counters.
"""
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from rich.console import Console
import httpx
import json
import os
import sys


console = Console()

# GitHub API setup
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = os.getenv("REPO_OWNER", "SCPrime")
REPO_NAME = os.getenv("REPO_NAME", "PaiiD")
EVENT_NAME = os.getenv("EVENT_NAME", "unknown")
CHECK_TYPE = os.getenv("CHECK_TYPE", "all")

API_BASE = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

def load_monitor_data():
    """Load existing monitor data"""
    data_file = Path("monitor-data.json")
    if data_file.exists():
        return json.loads(data_file.read_text())
    return {
        "last_check": None,
        "counters": {
            "total_commits": 0,
            "total_prs": 0,
            "open_issues": 0,
            "closed_issues": 0,
            "deployments": 0,
            "workflow_runs": 0,
            "errors": 0,
        },
        "events": [],
    }

def save_monitor_data(data):
    """Save monitor data to file"""
    data["last_check"] = datetime.now(timezone.utc).isoformat()
    Path("monitor-data.json").write_text(json.dumps(data, indent=2))

async def check_github_api():
    """Check GitHub API for repository stats"""
    console.print(f"[cyan]🔍 Checking GitHub API for {REPO_OWNER}/{REPO_NAME}...[/cyan]")

    data = load_monitor_data()

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Get repository info
            if CHECK_TYPE in ["all", "health"]:
                console.print("[yellow]📊 Fetching repository stats...[/yellow]")
                repo_resp = await client.get(API_BASE, headers=HEADERS)
                repo_resp.raise_for_status()
                repo_data = repo_resp.json()

                console.print(f"[green]✅ Repo: {repo_data['full_name']}[/green]")
                console.print(f"[blue]⭐ Stars: {repo_data['stargazers_count']}[/blue]")
                console.print(f"[blue]🍴 Forks: {repo_data['forks_count']}[/blue]")

            # Get open issues
            if CHECK_TYPE in ["all", "issues"]:
                console.print("[yellow]🐛 Fetching issues...[/yellow]")
                issues_resp = await client.get(
                    f"{API_BASE}/issues",
                    headers=HEADERS,
                    params={"state": "open", "per_page": 100},
                )
                issues_resp.raise_for_status()
                issues = issues_resp.json()

                # Filter out pull requests (they also show up in issues endpoint)
                actual_issues = [i for i in issues if "pull_request" not in i]
                data["counters"]["open_issues"] = len(actual_issues)

                console.print(f"[green]✅ Open Issues: {len(actual_issues)}[/green]")

            # Get pull requests
            if CHECK_TYPE in ["all", "health"]:
                console.print("[yellow]🔀 Fetching pull requests...[/yellow]")
                prs_resp = await client.get(
                    f"{API_BASE}/pulls",
                    headers=HEADERS,
                    params={"state": "all", "per_page": 10},
                )
                prs_resp.raise_for_status()
                prs = prs_resp.json()
                data["counters"]["total_prs"] = len(prs)

                console.print(f"[green]✅ Recent PRs: {len(prs)}[/green]")

            # Get recent commits
            if CHECK_TYPE in ["all", "health"]:
                console.print("[yellow]📝 Fetching commits...[/yellow]")
                commits_resp = await client.get(
                    f"{API_BASE}/commits",
                    headers=HEADERS,
                    params={"per_page": 10},
                )
                commits_resp.raise_for_status()
                commits = commits_resp.json()

                console.print(f"[green]✅ Recent Commits: {len(commits)}[/green]")

                # Log recent commit info
                if commits:
                    latest = commits[0]
                    console.print(
                        f"[dim]   Latest: {latest['commit']['message'][:60]}...[/dim]"
                    )

            # Get deployments
            if CHECK_TYPE in ["all", "deployments"]:
                console.print("[yellow]🚀 Fetching deployments...[/yellow]")
                deployments_resp = await client.get(
                    f"{API_BASE}/deployments", headers=HEADERS, params={"per_page": 10}
                )
                if deployments_resp.status_code == 200:
                    deployments = deployments_resp.json()
                    data["counters"]["deployments"] = len(deployments)
                    console.print(f"[green]✅ Deployments: {len(deployments)}[/green]")

            # Get workflow runs
            if CHECK_TYPE in ["all", "health"]:
                console.print("[yellow]⚙️  Fetching workflow runs...[/yellow]")
                workflows_resp = await client.get(
                    f"{API_BASE}/actions/runs",
                    headers=HEADERS,
                    params={"per_page": 10},
                )
                workflows_resp.raise_for_status()
                workflows = workflows_resp.json()
                data["counters"]["workflow_runs"] = workflows.get("total_count", 0)

                # Check for failed workflows
                failed = [w for w in workflows.get("workflow_runs", []) if w["conclusion"] == "failure"]
                if failed:
                    data["counters"]["errors"] = len(failed)
                    console.print(f"[red]❌ Failed Workflows: {len(failed)}[/red]")
                else:
                    console.print("[green]✅ All workflows passing[/green]")

            # Log event
            event_record = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event": EVENT_NAME,
                "check_type": CHECK_TYPE,
                "counters_snapshot": data["counters"].copy(),
            }
            data["events"].append(event_record)

            # Keep only last 100 events
            data["events"] = data["events"][-100:]

            save_monitor_data(data)

            console.print("\n[bold green]✅ Monitor check complete![/bold green]")
            console.print(f"[dim]Event: {EVENT_NAME} | Check: {CHECK_TYPE}[/dim]")

            return True

        except httpx.HTTPStatusError as e:
            console.print(f"[red]❌ HTTP Error: {e}[/red]")
            data["counters"]["errors"] += 1
            save_monitor_data(data)
            return False
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")
            data["counters"]["errors"] += 1
            save_monitor_data(data)
            return False

def main():
    """Main entry point"""
    console.print("\n[bold cyan]═══════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]   🔍 AUTO GITHUB MONITOR v1.0[/bold cyan]")
    console.print("[bold cyan]═══════════════════════════════════[/bold cyan]\n")

    if not GITHUB_TOKEN:
        console.print("[red]❌ GITHUB_TOKEN not set![/red]")
        sys.exit(1)

    success = asyncio.run(check_github_api())

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
