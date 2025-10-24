# Pre-launch Validation Guide

This guide explains the automated validation pipeline introduced in `app/core/prelaunch.py`. The validator runs before migrations and service startup to prevent zombie processes, missing configuration, and other high-risk deployment failures.

## Overview
- **Entry point:** `python -m app.core.prelaunch`
- **Invocation points:**
  - `backend/app/main.py` during ASGI initialization
  - `backend/start.sh` prior to Alembic migrations
  - `backend/Procfile` (Render, Railway, etc.) before `uvicorn`
- **Exit codes:** `0` on success, `1` when any check fails

## Checks Performed
| Check | Description | Remediation |
| --- | --- | --- |
| `python_version` | Ensures Python ≥ 3.10 to match project dependencies | Upgrade runtime or container image |
| `binary:uvicorn` / `binary:alembic` | Verifies executables exist in `$PATH` | Install missing CLI or activate virtualenv |
| `env:API_TOKEN`, `env:TRADIER_API_KEY`, `env:SENTRY_DSN` (prod/staging) | Confirms critical environment variables are populated | Update `.env`, Render secrets, or GitHub Actions secrets |
| `port:####` | Validates configured ports are free (defaults to 8000) | Terminate rogue processes or adjust `PRELAUNCH_REQUIRED_PORTS` |
| `env_file` | Confirms `.env` is present beside the repository root | Copy or generate `.env` before deployment |

## Configuration
- `ENVIRONMENT` controls whether `SENTRY_DSN` is required (`production` and `staging` enforce it).
- `PRELAUNCH_REQUIRED_PORTS` accepts a comma-separated list (e.g., `8000,8001`).
- `BACKEND_FIXTURE_PATH` overrides the default fixture directory for deterministic tests.
- `USE_FIXTURE_DATA=true` enables fixture responses without query parameters (useful in CI).

## Interpreting Output
Example success payload:
```json
{
  "checks": [
    {"name": "python_version", "passed": true, "message": "Python 3.11.9 detected"},
    {"name": "binary:uvicorn", "passed": true, "message": "uvicorn found at /usr/local/bin/uvicorn"},
    {"name": "env:API_TOKEN", "passed": true, "message": "Environment variable API_TOKEN set"},
    {"name": "port:8000", "passed": true, "message": "Port 8000 is available"}
  ]
}
```
A failing check emits `"passed": false` with a remediation message and causes a non-zero exit code.

## Integrating in CI/CD
1. **Local development:** run `python -m app.core.prelaunch` before `uvicorn` to surface misconfiguration quickly.
2. **Git hooks:** add the command to `pre-commit` or `pre-push` hooks for teams.
3. **CI workflows:** insert the validator before database migrations to avoid partial deploys.
4. **Render / Procfile environments:** keep the Procfile entry `python -m app.core.prelaunch && uvicorn ...` to guarantee parity with local execution.

## Related Artifacts
- `BUG_REPORT_OPTIONS_500.md` — updated resolution referencing the validator and fixture mode.
- `QE_ACCEPTANCE_CHECKLIST.md` — QA requirements that include validator success criteria.
- `backend/tests/test_prelaunch_validation.py` — automated coverage for key scenarios.
- `frontend/tests/fixtures/options.ts` — deterministic data powering Playwright tests.

For further assistance, contact the release engineering team or file an issue referencing the failing check name.
