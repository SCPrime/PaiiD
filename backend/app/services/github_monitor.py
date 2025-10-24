"""
GitHub Monitor Service - Handles webhook events and polling

Monitors:
- Push events (commits)
- Pull request events (opened, merged, conflicts)
- Issue events (opened, closed, labeled)
- Check suite events (CI/CD results)
- Deployment events
"""

import asyncio
import hashlib
import hmac
import logging
from datetime import datetime
from typing import Any

import httpx

from app.core.config import settings
from app.services.alert_manager import AlertSeverity, get_alert_manager
from app.services.counter_manager import get_counter_manager


logger = logging.getLogger(__name__)


class GitHubWebhookHandler:
    """Handles GitHub webhook events"""

    def __init__(self, webhook_secret: str):
        self.secret = webhook_secret.encode() if webhook_secret else b""

    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify GitHub webhook signature

        Args:
            payload: Raw request body
            signature: X-Hub-Signature-256 header value

        Returns:
            True if signature is valid
        """
        if not self.secret:
            logger.warning(
                "No webhook secret configured - skipping signature verification"
            )
            return True

        expected = hmac.new(self.secret, payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(f"sha256={expected}", signature)

    async def handle_push(self, event: dict[str, Any]):
        """Handle push events"""
        commits = event.get("commits", [])
        branch = event.get("ref", "").split("/")[-1]
        pusher = event.get("pusher", {}).get("name", "unknown")

        # Update counters
        counter_mgr = await get_counter_manager()
        await counter_mgr.increment("pushes")
        await counter_mgr.increment("commits", len(commits))

        # Check for sensitive files
        alert_mgr = get_alert_manager()
        for commit in commits:
            added = commit.get("added", [])
            modified = commit.get("modified", [])
            all_files = added + modified

            # Check for secrets
            sensitive_patterns = [
                ".env",
                ".key",
                ".pem",
                "secret",
                "password",
                "credentials",
            ]
            for file_path in all_files:
                if any(pattern in file_path.lower() for pattern in sensitive_patterns):
                    await alert_mgr.send_alert(
                        AlertSeverity.CRITICAL,
                        "Sensitive File Committed",
                        f"File '{file_path}' may contain sensitive data!",
                        context={
                            "file": file_path,
                            "branch": branch,
                            "commit": commit.get("id", "")[:7],
                            "author": pusher,
                        },
                        tags=["security", "git"],
                    )

        logger.info(f"Push event: {len(commits)} commit(s) to {branch} by {pusher}")

    async def handle_pull_request(self, event: dict[str, Any]):
        """Handle PR events"""
        action = event.get("action")
        pr = event.get("pull_request", {})
        pr_number = pr.get("number")
        title = pr.get("title")

        # Update counters
        counter_mgr = await get_counter_manager()
        await counter_mgr.increment(f"pulls_{action}")

        alert_mgr = get_alert_manager()

        # Check for conflicts
        if pr.get("mergeable") is False:
            await counter_mgr.increment("conflicts")
            await alert_mgr.send_alert(
                AlertSeverity.HIGH,
                f"PR #{pr_number} Has Conflicts",
                f"Pull request '{title}' has merge conflicts that need resolution",
                context={
                    "pr_number": pr_number,
                    "title": title,
                    "url": pr.get("html_url"),
                },
                tags=["git", "pr", "conflicts"],
            )

        # Alert on PR opened
        if action == "opened":
            await alert_mgr.send_alert(
                AlertSeverity.LOW,
                f"New PR #{pr_number} Opened",
                f"Pull request: {title}",
                context={
                    "pr_number": pr_number,
                    "author": pr.get("user", {}).get("login"),
                    "url": pr.get("html_url"),
                },
                tags=["git", "pr"],
            )

        # Alert on PR merged
        if action == "closed" and pr.get("merged"):
            await alert_mgr.send_alert(
                AlertSeverity.LOW,
                f"PR #{pr_number} Merged",
                f"Pull request '{title}' was merged successfully",
                context={
                    "pr_number": pr_number,
                    "merged_by": pr.get("merged_by", {}).get("login"),
                    "url": pr.get("html_url"),
                },
                tags=["git", "pr", "merge"],
            )

        logger.info(f"PR event: #{pr_number} - {action}")

    async def handle_check_suite(self, event: dict[str, Any]):
        """Handle CI/CD check results"""
        check = event.get("check_suite", {})
        conclusion = check.get("conclusion")
        branch = check.get("head_branch")

        counter_mgr = await get_counter_manager()
        alert_mgr = get_alert_manager()

        if conclusion == "failure":
            await counter_mgr.increment("build_failures")
            await alert_mgr.send_alert(
                AlertSeverity.HIGH,
                "Build Failed",
                f"CI/CD checks failed on branch '{branch}'",
                context={
                    "branch": branch,
                    "conclusion": conclusion,
                    "url": check.get("html_url"),
                },
                tags=["ci", "build", "failure"],
            )
        elif conclusion == "success":
            await alert_mgr.send_alert(
                AlertSeverity.LOW,
                "Build Succeeded",
                f"CI/CD checks passed on branch '{branch}'",
                context={"branch": branch},
                tags=["ci", "build", "success"],
            )

        logger.info(f"Check suite event: {branch} - {conclusion}")

    async def handle_issues(self, event: dict[str, Any]):
        """Handle issue events"""
        action = event.get("action")
        issue = event.get("issue", {})
        issue_number = issue.get("number")
        title = issue.get("title")

        # Update counters
        counter_mgr = await get_counter_manager()
        await counter_mgr.increment(f"issues_{action}")

        # Update issue health metrics
        await self.update_issue_health()

        # Alert on critical issues
        alert_mgr = get_alert_manager()
        labels = [l.get("name", "") for l in issue.get("labels", [])]

        if "P0" in labels or "critical" in labels:
            await alert_mgr.send_alert(
                AlertSeverity.CRITICAL,
                f"P0 Issue #{issue_number} {action.title()}",
                f"Critical issue: {title}",
                context={
                    "issue_number": issue_number,
                    "labels": ", ".join(labels),
                    "url": issue.get("html_url"),
                },
                tags=["issue", "critical", "P0"],
            )
        elif "P1" in labels or "high" in labels:
            await alert_mgr.send_alert(
                AlertSeverity.HIGH,
                f"P1 Issue #{issue_number} {action.title()}",
                f"High priority issue: {title}",
                context={
                    "issue_number": issue_number,
                    "labels": ", ".join(labels),
                    "url": issue.get("html_url"),
                },
                tags=["issue", "high", "P1"],
            )

        logger.info(f"Issue event: #{issue_number} - {action}")

    async def handle_deployment(self, event: dict[str, Any]):
        """Handle deployment events"""
        deployment = event.get("deployment", {})
        status = event.get("deployment_status", {})
        state = status.get("state")
        environment = deployment.get("environment", "production")

        counter_mgr = await get_counter_manager()
        alert_mgr = get_alert_manager()

        if state == "success":
            await counter_mgr.increment("deployments")
            await alert_mgr.send_alert(
                AlertSeverity.LOW,
                "Deployment Successful",
                f"Deployment to {environment} completed successfully",
                context={"environment": environment, "url": status.get("target_url")},
                tags=["deployment", "success"],
            )
        elif state == "failure":
            await alert_mgr.send_alert(
                AlertSeverity.CRITICAL,
                "Deployment Failed",
                f"Deployment to {environment} failed!",
                context={
                    "environment": environment,
                    "url": status.get("target_url"),
                    "description": status.get("description"),
                },
                tags=["deployment", "failure"],
            )

        logger.info(f"Deployment event: {environment} - {state}")

    async def update_issue_health(self):
        """Update issue health metrics from GitHub API"""
        # This would make API call to GitHub to get current issue counts
        # For now, we'll track increments only
        pass


class GitHubPoller:
    """Polls GitHub API every 5 minutes for repository state"""

    def __init__(self, token: str, repo: str):
        self.token = token
        self.repo = repo  # Format: "owner/repo"
        self.base_url = f"https://api.github.com/repos/{repo}"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
        }
        self.running = False

    async def start(self):
        """Start polling loop"""
        self.running = True
        logger.info("GitHub poller started")

        while self.running:
            try:
                await self.run_checks()
            except Exception as e:
                logger.error(f"Polling error: {e}")

            # Wait 5 minutes before next poll
            await asyncio.sleep(300)

    def stop(self):
        """Stop polling loop"""
        self.running = False
        logger.info("GitHub poller stopped")

    async def run_checks(self):
        """Execute all polling checks"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Run checks in parallel
            results = await asyncio.gather(
                self.check_open_prs(client),
                self.check_ci_status(client),
                self.check_deployments(client),
                return_exceptions=True,
            )

            # Log any errors
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Check {i} failed: {result}")

    async def check_open_prs(self, client: httpx.AsyncClient):
        """Check for stale or problematic PRs"""
        url = f"{self.base_url}/pulls?state=open"
        response = await client.get(url, headers=self.headers)

        if response.status_code != 200:
            logger.error(f"Failed to fetch PRs: {response.status_code}")
            return

        prs = response.json()
        alert_mgr = get_alert_manager()

        for pr in prs:
            created_at = datetime.fromisoformat(pr["created_at"].rstrip("Z"))
            age_days = (datetime.utcnow() - created_at).days

            # Alert on stale PRs (>7 days)
            if age_days > 7:
                await alert_mgr.send_alert(
                    AlertSeverity.MEDIUM,
                    f"Stale PR #{pr['number']}",
                    f"Pull request '{pr['title']}' is {age_days} days old",
                    context={
                        "pr_number": pr["number"],
                        "age_days": age_days,
                        "url": pr["html_url"],
                    },
                    tags=["pr", "stale"],
                )

    async def check_ci_status(self, client: httpx.AsyncClient):
        """Check latest CI/CD run status"""
        url = f"{self.base_url}/actions/runs?per_page=1"
        response = await client.get(url, headers=self.headers)

        if response.status_code != 200:
            logger.error(f"Failed to fetch CI status: {response.status_code}")
            return

        runs = response.json().get("workflow_runs", [])

        if runs and runs[0]["conclusion"] == "failure":
            alert_mgr = get_alert_manager()
            await alert_mgr.send_alert(
                AlertSeverity.HIGH,
                "Latest CI Run Failed",
                f"Workflow '{runs[0]['name']}' failed",
                context={"workflow": runs[0]["name"], "url": runs[0]["html_url"]},
                tags=["ci", "failure"],
            )

    async def check_deployments(self, client: httpx.AsyncClient):
        """Check deployment health"""
        alert_mgr = get_alert_manager()

        # Check Frontend (Vercel)
        try:
            frontend_url = "https://paiid-snowy.vercel.app/api/proxy/api/health"
            response = await client.get(frontend_url, timeout=10.0)
            if response.status_code != 200:
                await alert_mgr.send_alert(
                    AlertSeverity.CRITICAL,
                    "Frontend Deployment Down",
                    f"Frontend health check failed with status {response.status_code}",
                    context={"url": frontend_url},
                    tags=["deployment", "frontend", "critical"],
                )
        except Exception as e:
            await alert_mgr.send_alert(
                AlertSeverity.CRITICAL,
                "Frontend Deployment Unreachable",
                f"Cannot connect to frontend: {e!s}",
                context={"url": frontend_url},
                tags=["deployment", "frontend", "critical"],
            )

        # Check Backend (Render)
        try:
            backend_url = "https://paiid-86a1.onrender.com/api/health"
            response = await client.get(backend_url, timeout=10.0)
            if response.status_code != 200:
                await alert_mgr.send_alert(
                    AlertSeverity.CRITICAL,
                    "Backend Deployment Down",
                    f"Backend health check failed with status {response.status_code}",
                    context={"url": backend_url},
                    tags=["deployment", "backend", "critical"],
                )
        except Exception as e:
            await alert_mgr.send_alert(
                AlertSeverity.CRITICAL,
                "Backend Deployment Unreachable",
                f"Cannot connect to backend: {e!s}",
                context={"url": backend_url},
                tags=["deployment", "backend", "critical"],
            )


# Singleton poller instance
_poller_instance = None


async def start_github_poller():
    """Start the GitHub poller (call from app startup)"""
    global _poller_instance

    github_token = getattr(settings, "GITHUB_TOKEN", None)
    github_repo = getattr(settings, "GITHUB_REPO", "SCPrime/PaiiD")

    if not github_token:
        logger.warning("GITHUB_TOKEN not configured - poller disabled")
        return

    _poller_instance = GitHubPoller(github_token, github_repo)

    # Start poller in background task
    asyncio.create_task(_poller_instance.start())
    logger.info("GitHub poller background task started")


def stop_github_poller():
    """Stop the GitHub poller"""
    global _poller_instance
    if _poller_instance:
        _poller_instance.stop()
