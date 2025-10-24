#!/usr/bin/env python3
"""
Custom Claude Code Review Script for GitHub Actions
Uses Anthropic API to review PR changes based on .github/CLAUDE.md standards
"""

import os
import sys
from pathlib import Path

import anthropic
import requests


def load_review_standards():
    """Load the CLAUDE.md file with review standards"""
    claude_md_path = Path(".github/CLAUDE.md")
    if claude_md_path.exists():
        return claude_md_path.read_text(encoding="utf-8")
    return ""


def get_pr_diff(github_token, repo, pr_number):
    """Fetch PR diff from GitHub API"""
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github.v3.diff",
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching PR diff: {response.status_code}")
        return None

    return response.text


def get_changed_files_content(changed_files):
    """Read content of changed files"""
    files_content = {}

    for file_path in changed_files.split(","):
        file_path = file_path.strip()
        if not file_path:
            continue

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                files_content[file_path] = f.read()
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}")

    return files_content


def review_code_with_claude(api_key, review_standards, pr_diff, files_content):
    """Send code to Claude for review - FOCUSED ON STABILITY ONLY"""
    client = anthropic.Anthropic(api_key=api_key)

    # Build the review prompt
    files_list = "\n".join([f"- {path}" for path in files_content.keys()])

    prompt = f"""You are reviewing a pull request for the PaiiD trading platform.
⚡ FOCUS: CRITICAL STABILITY & SECURITY ISSUES ONLY ⚡

REVIEW STANDARDS:
{review_standards}

CHANGED FILES:
{files_list}

PR DIFF:
{pr_diff}

🎯 WHAT TO FLAG (CRITICAL BLOCKERS & STABILITY ISSUES):

**CRITICAL BLOCKERS** - App won't work:
- API endpoint errors (500 errors, missing error handling)
- Authentication/security vulnerabilities (SQL injection, exposed secrets)
- Database connection failures
- Missing dependency imports that break builds
- Syntax errors

**STABILITY ISSUES** - App might crash:
- Unhandled exceptions in external API calls (Tradier, Alpaca, Anthropic)
- Float usage in financial calculations (MUST use Decimal)
- Missing CORS/security headers
- Race conditions in async code
- Options endpoint routing issues (known problem - check for similar patterns)

🚫 WHAT TO IGNORE (NOT CRITICAL):
- Code style/formatting issues
- TODO/FIXME comments
- TypeScript warnings that don't block builds
- Missing tests or documentation
- Performance optimizations
- Minor naming conventions

📊 FORMAT YOUR RESPONSE:

## Summary
[One sentence: What changed and stability impact]

## Critical Blockers 🚨
[ONLY issues that WILL break the app - with file:line numbers]

## Stability Warnings ⚠️
[Issues that MIGHT cause crashes - with file:line numbers]

## Cursor Migration Notes 💡
[List which issues could be caught by Cursor locally instead of GitHub Actions]

## Approval Status
- [ ] ✅ APPROVED (no critical/stability issues)
- [ ] ⚠️ APPROVED WITH WARNINGS (stability concerns noted)
- [ ] 🚨 BLOCKED (critical issues MUST be fixed)

## Cost Estimate
[Estimated tokens used: ~X,XXX tokens ≈ $X.XX]
"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,  # Reduced from 8192 to save costs
            messages=[{"role": "user", "content": prompt}],
        )

        # Calculate cost estimate
        input_tokens = message.usage.input_tokens
        output_tokens = message.usage.output_tokens
        # Sonnet 4.5 pricing: $3/MTok input, $15/MTok output
        cost = (input_tokens * 3 / 1_000_000) + (output_tokens * 15 / 1_000_000)

        review_text = message.content[0].text

        # Append actual cost to review
        cost_report = f"\n\n---\n**Actual API Cost**: {input_tokens:,} input + {output_tokens:,} output tokens ≈ ${cost:.4f}"

        return review_text + cost_report

    except Exception as e:
        print(f"Error calling Claude API: {e}")
        return None


def post_review_comment(github_token, repo, pr_number, review_text):
    """Post the review as a PR comment"""
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }

    body = f"""## 🤖 Claude AI Code Review

{review_text}

---
*Generated with Claude Sonnet 4.5 using [PaiiD Code Review Standards](.github/CLAUDE.md)*
"""

    response = requests.post(url, headers=headers, json={"body": body})

    if response.status_code == 201:
        print("✅ Review comment posted successfully")
        return True
    else:
        print(f"❌ Failed to post comment: {response.status_code}")
        print(response.text)
        return False


def main():
    # Get environment variables
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    github_token = os.getenv("GITHUB_TOKEN")
    pr_number = os.getenv("PR_NUMBER")
    repo_name = os.getenv("REPO_NAME")
    changed_files = os.getenv("CHANGED_FILES", "")

    # Validate required env vars
    if not all([anthropic_api_key, github_token, pr_number, repo_name]):
        print("❌ Missing required environment variables")
        sys.exit(1)

    print(f"🔍 Reviewing PR #{pr_number} in {repo_name}")
    print(f"📝 Changed files: {changed_files}")

    # Load review standards
    print("📖 Loading review standards from .github/CLAUDE.md...")
    review_standards = load_review_standards()

    if not review_standards:
        print("⚠️ Warning: .github/CLAUDE.md not found, using default standards")

    # Get PR diff
    print("📥 Fetching PR diff from GitHub...")
    pr_diff = get_pr_diff(github_token, repo_name, pr_number)

    if not pr_diff:
        print("❌ Failed to fetch PR diff")
        sys.exit(1)

    # Get changed files content
    print("📂 Reading changed files...")
    files_content = get_changed_files_content(changed_files)

    # Review with Claude
    print("🤖 Sending to Claude for review...")
    review_text = review_code_with_claude(
        anthropic_api_key, review_standards, pr_diff, files_content
    )

    if not review_text:
        print("❌ Failed to get review from Claude")
        sys.exit(1)

    # Post review comment
    print("💬 Posting review comment to PR...")
    success = post_review_comment(github_token, repo_name, pr_number, review_text)

    if success:
        print("✅ Code review completed successfully!")
        sys.exit(0)
    else:
        print("❌ Failed to post review comment")
        sys.exit(1)


if __name__ == "__main__":
    main()
