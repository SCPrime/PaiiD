"""
GitHub Monitor Service
Handles GitHub webhook events and tracks repository activity
"""

import hashlib
import hmac
import logging
from datetime import datetime
from typing import Any

from ..core.config import get_settings
from .counter_manager import get_counter_manager


logger = logging.getLogger(__name__)
settings = get_settings()


class GitHubWebhookHandler:
    """Handles GitHub webhook events"""

    def __init__(self):
        self.counter_manager = get_counter_manager()
        self.webhook_secret = settings.GITHUB_WEBHOOK_SECRET

    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify GitHub webhook signature

        Args:
            payload: Raw request body
            signature: X-Hub-Signature-256 header value

        Returns:
            True if signature is valid
        """
        if not self.webhook_secret:
            logger.warning(
                "GitHub webhook secret not configured - skipping verification"
            )
            return True

        try:
            expected = hmac.new(
                self.webhook_secret.encode(), payload, hashlib.sha256
            ).hexdigest()
            return hmac.compare_digest(f"sha256={expected}", signature)
        except Exception as e:
            logger.error(f"Error verifying signature: {e}")
            return False

    async def handle_push(self, event: dict[str, Any]) -> dict[str, Any]:
        """
        Handle push events

        Args:
            event: GitHub push event payload

        Returns:
            Processing result
        """
        try:
            commits = event.get("commits", [])
            branch = event.get("ref", "").split("/")[-1]
            pusher = event.get("pusher", {}).get("name", "unknown")

            # Increment counters
            await self.counter_manager.increment("pushes")
            await self.counter_manager.increment("commits", len(commits))

            # Check for sensitive files
            sensitive_files = []
            for commit in commits:
                added_files = commit.get("added", [])
                for file in added_files:
                    if any(
                        pattern in file.lower()
                        for pattern in [".env", ".key", ".secret", "credentials"]
                    ):
                        sensitive_files.append(file)

            result = {
                "event": "push",
                "branch": branch,
                "pusher": pusher,
                "commit_count": len(commits),
                "timestamp": datetime.utcnow().isoformat(),
            }

            if sensitive_files:
                result["warning"] = (
                    f"Sensitive files detected: {', '.join(sensitive_files)}"
                )
                logger.warning(
                    f"Sensitive files committed on {branch}: {sensitive_files}"
                )

            logger.info(f"Push event: {len(commits)} commits to {branch} by {pusher}")
            return result

        except Exception as e:
            logger.error(f"Error handling push event: {e}")
            return {"event": "push", "error": str(e)}

    async def handle_pull_request(self, event: dict[str, Any]) -> dict[str, Any]:
        """
        Handle pull request events

        Args:
            event: GitHub PR event payload

        Returns:
            Processing result
        """
        try:
            action = event.get("action", "unknown")
            pr = event.get("pull_request", {})
            pr_number = pr.get("number", 0)
            title = pr.get("title", "")
            author = pr.get("user", {}).get("login", "unknown")

            # Increment counters based on action
            counter_key = f"pulls_{action}"
            await self.counter_manager.increment(counter_key)

            result = {
                "event": "pull_request",
                "action": action,
                "pr_number": pr_number,
                "title": title,
                "author": author,
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Check for conflicts
            if pr.get("mergeable") is False:
                await self.counter_manager.increment("conflicts")
                result["warning"] = f"PR #{pr_number} has merge conflicts"
                logger.warning(f"Merge conflicts detected in PR #{pr_number}")

            # Check if merged
            if action == "closed" and pr.get("merged", False):
                await self.counter_manager.increment("pulls_merged")
                result["merged"] = True

            logger.info(f"PR event: #{pr_number} - {action} by {author}")
            return result

        except Exception as e:
            logger.error(f"Error handling PR event: {e}")
            return {"event": "pull_request", "error": str(e)}

    async def handle_issues(self, event: dict[str, Any]) -> dict[str, Any]:
        """
        Handle issue events

        Args:
            event: GitHub issue event payload

        Returns:
            Processing result
        """
        try:
            action = event.get("action", "unknown")
            issue = event.get("issue", {})
            issue_number = issue.get("number", 0)
            title = issue.get("title", "")
            author = issue.get("user", {}).get("login", "unknown")
            labels = [label.get("name", "") for label in issue.get("labels", [])]

            # Increment counters based on action
            counter_key = f"issues_{action}"
            await self.counter_manager.increment(counter_key)

            result = {
                "event": "issues",
                "action": action,
                "issue_number": issue_number,
                "title": title,
                "author": author,
                "labels": labels,
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Check for critical issues
            is_critical = any(
                label.upper() in ["P0", "CRITICAL", "URGENT"] for label in labels
            )
            if is_critical and action == "opened":
                result["alert"] = f"Critical issue opened: #{issue_number} - {title}"
                logger.warning(f"Critical issue #{issue_number} opened: {title}")

            logger.info(f"Issue event: #{issue_number} - {action} by {author}")
            return result

        except Exception as e:
            logger.error(f"Error handling issue event: {e}")
            return {"event": "issues", "error": str(e)}

    async def handle_check_suite(self, event: dict[str, Any]) -> dict[str, Any]:
        """
        Handle CI/CD check suite events

        Args:
            event: GitHub check suite event payload

        Returns:
            Processing result
        """
        try:
            check = event.get("check_suite", {})
            conclusion = check.get("conclusion", "")
            status = check.get("status", "")
            branch = check.get("head_branch", "unknown")

            result = {
                "event": "check_suite",
                "status": status,
                "conclusion": conclusion,
                "branch": branch,
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Track failures
            if conclusion == "failure":
                await self.counter_manager.increment("build_failures")
                result["warning"] = f"Build failed on {branch}"
                logger.warning(f"CI/CD check failed on {branch}")

            # Track test failures
            if conclusion == "failure" and "test" in check.get("name", "").lower():
                await self.counter_manager.increment("test_failures")

            logger.info(f"Check suite event: {status}/{conclusion} on {branch}")
            return result

        except Exception as e:
            logger.error(f"Error handling check suite event: {e}")
            return {"event": "check_suite", "error": str(e)}

    async def handle_deployment(self, event: dict[str, Any]) -> dict[str, Any]:
        """
        Handle deployment events

        Args:
            event: GitHub deployment event payload

        Returns:
            Processing result
        """
        try:
            deployment = event.get("deployment", {})
            environment = deployment.get("environment", "unknown")
            ref = deployment.get("ref", "unknown")

            await self.counter_manager.increment("deployments")

            result = {
                "event": "deployment",
                "environment": environment,
                "ref": ref,
                "timestamp": datetime.utcnow().isoformat(),
            }

            logger.info(f"Deployment event: {ref} to {environment}")
            return result

        except Exception as e:
            logger.error(f"Error handling deployment event: {e}")
            return {"event": "deployment", "error": str(e)}

    async def handle_deployment_status(self, event: dict[str, Any]) -> dict[str, Any]:
        """
        Handle deployment status events

        Args:
            event: GitHub deployment status event payload

        Returns:
            Processing result
        """
        try:
            deployment_status = event.get("deployment_status", {})
            state = deployment_status.get("state", "unknown")
            environment = deployment_status.get("environment", "unknown")

            result = {
                "event": "deployment_status",
                "state": state,
                "environment": environment,
                "timestamp": datetime.utcnow().isoformat(),
            }

            if state == "failure":
                result["warning"] = f"Deployment to {environment} failed"
                logger.warning(f"Deployment to {environment} failed")

            logger.info(f"Deployment status: {state} for {environment}")
            return result

        except Exception as e:
            logger.error(f"Error handling deployment status event: {e}")
            return {"event": "deployment_status", "error": str(e)}

    async def handle_release(self, event: dict[str, Any]) -> dict[str, Any]:
        """
        Handle release events

        Args:
            event: GitHub release event payload

        Returns:
            Processing result
        """
        try:
            action = event.get("action", "unknown")
            release = event.get("release", {})
            tag_name = release.get("tag_name", "")
            name = release.get("name", "")

            result = {
                "event": "release",
                "action": action,
                "tag_name": tag_name,
                "name": name,
                "timestamp": datetime.utcnow().isoformat(),
            }

            logger.info(f"Release event: {action} - {tag_name}")
            return result

        except Exception as e:
            logger.error(f"Error handling release event: {e}")
            return {"event": "release", "error": str(e)}


# Global instance
_github_handler: GitHubWebhookHandler | None = None


def get_github_handler() -> GitHubWebhookHandler:
    """Get or create GitHub webhook handler instance"""
    global _github_handler
    if _github_handler is None:
        _github_handler = GitHubWebhookHandler()
    return _github_handler
