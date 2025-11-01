"""
PaiiD Trading Platform
Copyright © 2025 Dr. SC Prime. All Rights Reserved.

PROPRIETARY AND CONFIDENTIAL
Unauthorized copying, modification, or distribution is strictly prohibited.
🚨 THIS CODE IS MONITORED: Violators WILL be found.

GitHub Traffic Data Fetcher
Fetches visitor, clone, and download statistics from GitHub API.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

try:
    import requests
except ImportError:
    print("ERROR: requests library not installed. Install with: pip install requests")
    sys.exit(1)


def fetch_repo_traffic(
    owner: str, repo: str, token: str | None = None
) -> Dict[str, Any]:
    """Fetch traffic data for a repository."""
    base_url = "https://api.github.com/repos"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "PaiiD-Traffic-Fetcher",
    }

    if token:
        headers["Authorization"] = f"token {token}"

    results = {
        "repository": f"{owner}/{repo}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "page_views": None,
        "clones": None,
        "referrers": None,
        "popular_paths": None,
        "error": None,
    }

    # Fetch page views (last 14 days)
    try:
        response = requests.get(
            f"{base_url}/{owner}/{repo}/traffic/views",
            headers=headers,
            timeout=10,
        )
        if response.status_code == 200:
            results["page_views"] = response.json()
        elif response.status_code == 403:
            results["error"] = "Access forbidden - requires authentication token"
        elif response.status_code == 404:
            results["error"] = "Repository not found or access denied"
        else:
            results["error"] = f"HTTP {response.status_code}: {response.text[:200]}"
    except Exception as e:
        results["error"] = f"Failed to fetch page views: {str(e)}"

    # Fetch clones (last 14 days)
    try:
        response = requests.get(
            f"{base_url}/{owner}/{repo}/traffic/clones",
            headers=headers,
            timeout=10,
        )
        if response.status_code == 200:
            results["clones"] = response.json()
        elif response.status_code == 403:
            if not results["error"]:
                results["error"] = "Access forbidden - requires authentication token"
        elif response.status_code == 404:
            if not results["error"]:
                results["error"] = "Repository not found or access denied"
    except Exception as e:
        if not results["error"]:
            results["error"] = f"Failed to fetch clones: {str(e)}"

    # Fetch referrers (last 14 days)
    try:
        response = requests.get(
            f"{base_url}/{owner}/{repo}/traffic/popular/referrers",
            headers=headers,
            timeout=10,
        )
        if response.status_code == 200:
            results["referrers"] = response.json()
    except Exception:
        pass  # Non-critical

    # Fetch popular paths (last 14 days)
    try:
        response = requests.get(
            f"{base_url}/{owner}/{repo}/traffic/popular/paths",
            headers=headers,
            timeout=10,
        )
        if response.status_code == 200:
            results["popular_paths"] = response.json()
    except Exception:
        pass  # Non-critical

    return results


def format_traffic_report(results: Dict[str, Any]) -> str:
    """Format traffic data into readable report."""
    repo = results["repository"]
    report = f"\n{'=' * 70}\n"
    report += f"GitHub Traffic Report: {repo}\n"
    report += f"Generated: {results['timestamp']}\n"
    report += f"{'=' * 70}\n\n"

    if results.get("error"):
        report += f"[ERROR] {results['error']}\n"
        report += "\n[WARN] To fetch this data, you need:\n"
        report += "1. A GitHub Personal Access Token\n"
        report += "2. Token with 'repo' scope\n"
        report += "3. Run: python scripts/fetch_github_traffic.py --token YOUR_TOKEN\n"
        return report

    # Page Views Summary
    if results.get("page_views"):
        pv = results["page_views"]
        report += "[PAGE VIEWS] Last 14 Days:\n"
        report += f"   Total Views: {pv.get('count', 'N/A')}\n"
        report += f"   Unique Visitors: {pv.get('uniques', 'N/A')}\n"
        if pv.get("views"):
            report += "\n   Daily Breakdown:\n"
            for view in pv["views"][-7:]:  # Last 7 days
                date = view.get("timestamp", "")[:10]
                count = view.get("count", 0)
                uniques = view.get("uniques", 0)
                report += f"   {date}: {count} views ({uniques} unique)\n"
        report += "\n"

    # Clones Summary
    if results.get("clones"):
        clones = results["clones"]
        report += "[CLONE ACTIVITY] Last 14 Days:\n"
        report += f"   Total Clones: {clones.get('count', 'N/A')}\n"
        report += f"   Unique Cloners: {clones.get('uniques', 'N/A')}\n"
        if clones.get("clones"):
            report += "\n   Daily Breakdown:\n"
            for clone in clones["clones"][-7:]:  # Last 7 days
                date = clone.get("timestamp", "")[:10]
                count = clone.get("count", 0)
                uniques = clone.get("uniques", 0)
                report += f"   {date}: {count} clones ({uniques} unique)\n"
        report += "\n"

    # Referrers
    if results.get("referrers"):
        report += "[TOP REFERRING SITES]:\n"
        for ref in results["referrers"][:10]:
            site = ref.get("referrer", "Direct")
            count = ref.get("count", 0)
            uniques = ref.get("uniques", 0)
            report += f"   {site}: {count} ({uniques} unique)\n"
        report += "\n"

    # Popular Paths
    if results.get("popular_paths"):
        report += "[MOST VIEWED FILES/PATHS]:\n"
        for path in results["popular_paths"][:10]:
            file_path = path.get("path", "")
            title = path.get("title", "")
            count = path.get("count", 0)
            uniques = path.get("uniques", 0)
            report += f"   {file_path} ({title}): {count} views ({uniques} unique)\n"
        report += "\n"

    return report


def main():
    """Main execution."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Fetch GitHub traffic statistics for PaiiD repositories"
    )
    parser.add_argument(
        "--token",
        help="GitHub Personal Access Token (or set GITHUB_TOKEN env var)",
        default=os.getenv("GITHUB_TOKEN"),
    )
    parser.add_argument(
        "--output",
        help="Output file path (default: github_traffic_report.json)",
        default="github_traffic_report.json",
    )
    parser.add_argument(
        "--repos",
        nargs="+",
        default=["SCPrime/PaiiD", "SCPrime/Pa-D-2mx"],
        help="Repositories to check (format: owner/repo)",
    )

    args = parser.parse_args()

    if not args.token:
        print("[WARN] No GitHub token provided.")
        print("   Traffic data requires authentication.")
        print("   Either:")
        print("   1. Set GITHUB_TOKEN environment variable")
        print("   2. Use --token YOUR_TOKEN")
        print("   3. Create token at: https://github.com/settings/tokens")
        print("      (Requires 'repo' scope)")
        print("\n   Attempting to fetch without token (will likely fail)...\n")

    all_results = []
    full_report = ""

    for repo_full_name in args.repos:
        parts = repo_full_name.split("/")
        if len(parts) != 2:
            print(f"[ERROR] Invalid repository format: {repo_full_name}")
            continue

        owner, repo = parts
        print(f"[FETCH] Traffic data for {owner}/{repo}...")

        results = fetch_repo_traffic(owner, repo, args.token)
        all_results.append(results)

        report = format_traffic_report(results)
        full_report += report
        print(report)

    # Save to JSON file
    output_path = Path(args.output)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "generated": datetime.now(timezone.utc).isoformat(),
                "repositories": all_results,
            },
            f,
            indent=2,
        )

    # Save human-readable report
    report_path = output_path.with_suffix(".txt")
    with report_path.open("w", encoding="utf-8") as f:
        f.write(full_report)

    print("\n[OK] Data saved to:")
    print(f"   JSON: {output_path}")
    print(f"   Report: {report_path}")


if __name__ == "__main__":
    main()
