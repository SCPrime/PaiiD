import anthropic
import json
import os
import requests
import sys


GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
ANTHROPIC_API_KEY = os.environ['ANTHROPIC_API_KEY']
REPO = os.environ['REPO']
JOB_TO_FIX = os.environ['JOB_TO_FIX']

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def get_latest_workflow_run():
    """Get the latest failed workflow run"""
    url = f"https://api.github.com/repos/{REPO}/actions/runs"
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    params = {'status': 'failure', 'per_page': 1}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"Failed to fetch workflow runs: {response.status_code}")
        return None

    runs = response.json()['workflow_runs']
    return runs[0] if runs else None

def get_job_logs(run_id, job_name):
    """Get logs for a specific job"""
    # Get jobs for the run
    url = f"https://api.github.com/repos/{REPO}/actions/runs/{run_id}/jobs"
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch jobs: {response.status_code}")
        return None

    jobs = response.json()['jobs']
    target_job = None

    for job in jobs:
        if job_name in job['name'].lower():
            target_job = job
            break

    if not target_job:
        print(f"Job {job_name} not found")
        return None

    # Get logs
    log_url = target_job['url'].replace('/jobs/', '/jobs/') + '/logs'
    log_response = requests.get(log_url, headers=headers)

    if log_response.status_code != 200:
        print(f"Failed to fetch logs: {log_response.status_code}")
        return None

    return log_response.text

def get_relevant_files(job_name):
    """Get list of files to check based on job name"""
    if 'backend' in job_name:
        return ['backend/tests/', 'backend/app/', 'backend/requirements.txt']
    elif 'frontend' in job_name:
        return ['frontend/tests/', 'frontend/__tests__/', 'frontend/package.json']
    return []

def read_file_contents(paths):
    """Read contents of relevant files"""
    contents = {}
    for path in paths:
        if os.path.isdir(path):
            for root, _, files in os.walk(path):
                for file in files:
                    if file.endswith(('.py', '.ts', '.tsx', '.js', '.json')):
                        filepath = os.path.join(root, file)
                        try:
                            with open(filepath, 'r') as f:
                                contents[filepath] = f.read()
                        except:
                            pass
        elif os.path.isfile(path):
            try:
                with open(path, 'r') as f:
                    contents[path] = f.read()
            except:
                pass
    return contents

def ask_claude_for_fixes(logs, file_contents, job_name):
    """Ask Claude to analyze and provide fixes"""

    files_context = "\n\n".join([
        f"FILE: {path}\n```\n{content[:2000]}\n```"
        for path, content in list(file_contents.items())[:5]
    ])

    prompt = f"""You are a senior DevOps engineer fixing CI/CD failures.

JOB: {job_name}

FAILURE LOGS:
```
{logs[-5000:]}
```

RELEVANT CODE:
{files_context}

TASK:
1. Identify the root cause of the test failures
2. Provide EXACT file changes to fix the issues
3. Format as JSON with this structure:
{{
  "analysis": "brief explanation of what's wrong",
  "fixes": [
    {{
      "file": "path/to/file",
      "action": "modify|create",
      "content": "full new file content"
    }}
  ]
}}

Respond ONLY with valid JSON, no markdown formatting."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = message.content[0].text

    # Clean markdown formatting if present
    response_text = response_text.replace('```json', '').replace('```', '').strip()

    return json.loads(response_text)

def apply_fixes(fixes_json):
    """Apply the fixes to files"""
    for fix in fixes_json['fixes']:
        filepath = fix['file']
        content = fix['content']

        # Create directory if needed
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Write file
        with open(filepath, 'w') as f:
            f.write(content)

        print(f"✓ Fixed: {filepath}")

def main():
    print(f"Analyzing CI failures for: {JOB_TO_FIX}")

    # Get latest failed run
    run = get_latest_workflow_run()
    if not run:
        print("No failed runs found")
        sys.exit(1)

    print(f"Found run: {run['id']}")

    # Handle "both" option
    jobs_to_fix = []
    if JOB_TO_FIX == 'both':
        jobs_to_fix = ['test-backend', 'test-frontend']
    else:
        jobs_to_fix = [JOB_TO_FIX]

    for job_name in jobs_to_fix:
        print(f"\n📋 Analyzing {job_name}...")

        # Get logs
        logs = get_job_logs(run['id'], job_name)
        if not logs:
            print(f"Could not get logs for {job_name}")
            continue

        # Get relevant files
        file_paths = get_relevant_files(job_name)
        file_contents = read_file_contents(file_paths)

        print(f"Loaded {len(file_contents)} files")

        # Ask Claude for fixes
        print("🤖 Asking Claude for fixes...")
        fixes = ask_claude_for_fixes(logs, file_contents, job_name)

        print(f"\n📊 Analysis: {fixes['analysis']}")

        # Apply fixes
        print("\n🔧 Applying fixes...")
        apply_fixes(fixes)

    print("\n✅ All fixes applied!")

if __name__ == '__main__':
    main()
