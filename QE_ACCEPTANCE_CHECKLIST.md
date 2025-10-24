# QE Acceptance Checklist — Pre-launch Validation & Options Endpoint

This checklist confirms the PaiiD backend and frontend are production-ready after the pre-launch validation and deterministic fixture enhancements.

## ✅ Environment & Configuration
- [ ] `.env` synchronized with Render secrets and contains `API_TOKEN`, `TRADIER_API_KEY`, and production `SENTRY_DSN`.
- [ ] `ENVIRONMENT` set appropriately (`development`, `staging`, or `production`).
- [ ] `PRELAUNCH_REQUIRED_PORTS` updated when custom ports are exposed.
- [ ] `python -m app.core.prelaunch` passes locally and in CI before deployment.

## ✅ Backend Verification
- [ ] `poetry run pytest` or `pipenv run pytest` passes for all backend tests, including `tests/test_prelaunch_validation.py`.
- [ ] `python -m app.core.prelaunch` executed via `start.sh` completes with all checks marked `PASS`.
- [ ] Sentry initialization logs appear at startup with release identifier (e.g., `paiid-backend@<version>`).
- [ ] `/options/chains/SPY?fixture=true` returns deterministic fixture data and bypasses Tradier.
- [ ] `/options/chains/SPY` (without fixture flag) continues to proxy to Tradier in non-test environments.

## ✅ Frontend Verification
- [ ] `npm run lint` and `npm run test:ci` succeed in the `frontend/` directory.
- [ ] `npm run test:playwright` passes using the deterministic fixture data.
- [ ] Frontend telemetry includes `fixture_mode` events when Playwright runs.

## ✅ Deployment & Observability
- [ ] `deploy.sh` completes without errors when executed with default flags.
- [ ] Render service health checks report healthy within 60 seconds of deployment.
- [ ] Telemetry dashboards confirm receipt of `prelaunch_validation` events from backend startup.

## ✅ Regression Guardrails
- [ ] CI pipeline updated to run `python -m app.core.prelaunch` before migrations.
- [ ] Playwright tests added to CI workflow for deterministic validation of options chain UI.
- [ ] Documentation updates (`PRELAUNCH_VALIDATION_GUIDE.md`, `BUG_REPORT_OPTIONS_500.md`) reviewed and published in the release notes.
