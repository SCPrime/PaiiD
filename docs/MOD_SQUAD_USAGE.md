# MOD SQUAD Usage

## Checkpoints
1. Before changes: Run GITHUB MOD; record commit; open issues/PRs.
2. Pre-commit: Run BROWSER MOD `--check-render` (dev/prod).
3. Post-push: GITHUB MOD + Actions status.
4. Post-deploy: BROWSER MOD `--full-audit`; save report.

## Commands
- GitHub: `python scripts/auto_github_monitor.py`
- Browser quick: `python scripts/browser_mod.py --check-render`
- Browser full: `python scripts/browser_mod.py --full-audit`

## Evidence
- `monitor-data.json`, `browser-mod-report-*.json`, screenshots.

## Diagnostics
- Proxy: `/api/proxy/_routes`
- Backend: `/api/_auth/echo`, `/api/health/*`
