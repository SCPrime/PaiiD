# Backend Script Guide

## Process Lifecycle Utilities

Although the cross-platform process manager lives under the repository `scripts/`
directory, backend developers interact with the following resources:

| Script | Description |
| ------ | ----------- |
| `../scripts/ci-cleanup.sh` | Clears PID files, kills lingering dev servers, and removes zombie processes. Executed automatically in CI but can be run manually. |
| `../scripts/health-monitor.ps1` | Windows health checks for backend/fronted ports. Produces timestamped logs. |

## Runtime Directories

The backend expects the following directories to exist:

- `backend/.run/` – PID files for managed backend workers.
- `backend/.logs/` – Plain-text log output captured by helper scripts.

Both directories are git-ignored except for the `.gitkeep` placeholder. Cleanup
scripts remove residual files on each run.
