# Zombie Process Elimination Playbook

This document summarises the process lifecycle tooling that keeps the PaiiD
stack free from stray background processes during local development, automated
testing, and production deployments.

## Runtime Directories

| Path | Purpose |
| ---- | ------- |
| `backend/.run/` | PID files for backend processes started by helper scripts |
| `backend/.logs/` | Persistent backend runtime logs (log rotation handled by scripts) |
| `frontend/.run/` | PID files for frontend processes |
| `frontend/.logs/` | Frontend runtime logs |

Each directory is committed with a `.gitkeep` file and ignored for everything
else. Scripts remove stale PID files on startup and during CI execution.

## Scripts

- `scripts/ci-cleanup.sh` – idempotent cleanup for CI jobs. It kills processes
  listening on development ports, prunes zombie processes, and empties runtime
  directories.
- `scripts/health-monitor.ps1` – lightweight Windows health monitor that can be
  scheduled with Task Scheduler. It verifies TCP ports, the FastAPI health
  endpoint, and the Next.js frontend before writing a timestamped report under
  `monitoring/logs/`.
- `scripts/validate-managed-processes.sh` – validation utility that checks PID
  files and fails when stale processes are detected. Integrate into local hooks
  or run manually before deployments.

## CI Integration

The GitHub Actions workflow runs the cleanup script both before and after every
backend/frontend job. This guarantees a consistent environment even when a
previous job terminated unexpectedly.

## Production Deployment

`render.yaml` now launches Uvicorn with explicit lifespan management and
increased graceful shutdown limits. Docker Compose mirrors this configuration
with `init: true` (enabling `tini`) and extended `stop_grace_period` values so
containers flush background tasks before termination.

## API Observability

The `HealthMonitor` service collates request metadata, CPU/memory consumption,
managed PID status, and upstream dependency checks. The `/api/health/processes`
endpoint surfaces this data for operational dashboards.
