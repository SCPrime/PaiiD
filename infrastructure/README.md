# Render service configuration exports

This directory stores the subset of Render service configuration that we want to track in Git for drift detection. The JSON files can be refreshed with the Render CLI (`render`) and are intentionally normalized to only include the fields we care about comparing in CI.

## Files

- `paiid-backend.json` – FastAPI backend service information (auto-deploy flag, repository branch/root, build and start commands).
- `paiid-frontend.json` – Next.js frontend (Docker) service information (auto-deploy flag, repository branch/root, Docker build context/command).

## Updating the specs

Run `scripts/export-render-config.sh` after authenticating with the Render CLI. The script exports the live configuration for each service and rewrites the JSON files in this directory.

```bash
# Log in once per environment (stores credentials securely via the CLI)
render login

# Install the CLI if it is not already on your PATH
curl -fsSL https://render.com/static/cli/install.sh | bash
export PATH="$HOME/.render/bin:$PATH"

# Refresh the tracked settings
./scripts/export-render-config.sh
```

## CI drift detection

The GitHub Actions workflow `render-config-drift.yml` calls `scripts/check-render-config.sh` to compare the exported JSON with the current Render settings. Any deviation fails the workflow so that configuration drift is detected immediately.

## Smoke test after deployments

`scripts/render-deploy-smoke-test.sh` validates that the most recent deploy of each tracked service was built from the same commit as `origin/main`. This is designed to run immediately after a deployment pipeline finishes.
