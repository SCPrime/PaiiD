# Prelaunch Validation Guide

This guide explains the automated configuration validators that execute at FastAPI startup (`backend/app/main.py`). Use it to interpret startup logs and remediate any failures before deploying to staging or production.

## Reading the Startup Output

During application boot you will see a `===== PRELAUNCH VALIDATION =====` block. Each validator reports:

- **PASS** – configuration looks good.
- **WARN** – non-blocking issue that should be addressed before scaling traffic.
- **FAIL** – blocking issue; deployment should be halted until resolved.

Each failure includes a remediation hint that maps back to the sections below.

## Validator Reference

### `environment-profile`
- **Purpose:** Confirms `APP_ENV` resolves to a supported profile so downstream toggles behave correctly.
- **Fails When:** `APP_ENV` is empty or set to an unknown value (typos, whitespace, or legacy names).
- **Impact:** Startup policies (rate limits, auth defaults) may not match expectations; production safeguards can be skipped or double-applied.
- **Remediation:** Set `APP_ENV` to one of: `local`, `development`, `test`, `staging`, `preview`, or `production`.

### `api-token`
- **Purpose:** Ensures the backend is protected by a shared secret rather than the `change-me` placeholder.
- **Fails When:** `API_TOKEN` is blank or still equal to `change-me`.
- **Impact:** Frontend proxy requests receive 401/500 responses once rate limiting kicks in; unauthenticated access becomes possible.
- **Remediation:** Generate a strong token, update `API_TOKEN` on the backend, and mirror it to the frontend (`NEXT_PUBLIC_API_TOKEN`).

### `tradier-api-key`
- **Purpose:** Verifies access to the Tradier data APIs used by the options workflow.
- **Fails When:** `TRADIER_API_KEY` is missing or empty.
- **Impact:** All options expiration and quote requests fail upstream and surface as 500s.
- **Remediation:** Provision a valid Tradier token and add it to the backend environment.

### `sentry-dsn`
- **Purpose:** Enforces observability for staging/preview/production environments.
- **Fails When:** `APP_ENV` is not `local`/`development`/`test` and `SENTRY_DSN` is unset.
- **Impact:** Crashes and 500 errors (including options issues) go unreported, slowing incident response.
- **Remediation:** Create a Sentry project and set `SENTRY_DSN` in Render.

### `allow-origin` *(warning)*
- **Purpose:** Checks CORS configuration for hosted environments.
- **Warns When:** `ALLOW_ORIGIN` is missing while `APP_ENV` targets a remote deployment.
- **Impact:** Browsers may block the frontend’s proxy requests, leading to apparent 500s or empty option chains.
- **Remediation:** Set `ALLOW_ORIGIN` to the deployed frontend base URL.

### `alpaca-paper-credentials` *(warning)*
- **Purpose:** Confirms paper-trading credentials are available for the simulated execution flow.
- **Warns When:** Either `ALPACA_PAPER_API_KEY` or `ALPACA_PAPER_SECRET_KEY` is missing.
- **Impact:** Follow-up trading actions after retrieving expirations fail, breaking end-to-end validation.
- **Remediation:** Add both Alpaca paper trading credentials to the environment. These can be dummy values in local/dev.

## Frontend Validator Reference

The Next.js application now runs the same validation suite during `next build`, server bootstrap, and within every API route. The
validator names mirror the backend counterparts so remediation guidance stays consistent across services.

### `environment-profile`
- **Purpose:** Validates `NEXT_PUBLIC_APP_ENV`/`APP_ENV` so client toggles align with the backend profile.
- **Fails When:** The value is empty or not one of `local`, `development`, `test`, `staging`, `preview`, `production`.
- **Impact:** UI feature flags (e.g., telemetry, Sentry) drift from backend expectations.
- **Remediation:** Set `NEXT_PUBLIC_APP_ENV` in Vercel/Render or export `APP_ENV` before running `next build` locally.

### `sentry-dsn`
- **Purpose:** Enforces error monitoring for any non-local deployment.
- **Fails When:** `NEXT_PUBLIC_SENTRY_DSN` is missing while the environment profile targets staging/preview/production.
- **Impact:** Browser crashes and Next.js API exceptions are invisible in Sentry, prolonging incident response.
- **Remediation:** Add `NEXT_PUBLIC_SENTRY_DSN` to the frontend environment dashboard (and keep it in sync with the backend DSN).

### `api-token`
- **Purpose:** Ensures the frontend proxy has the same shared secret as the backend.
- **Fails When:** Neither `API_TOKEN` (server-side) nor `NEXT_PUBLIC_API_TOKEN` (client) is configured outside local/test profiles.
- **Impact:** Next.js API routes return 401/500 because requests to the backend are unauthorized.
- **Remediation:** Copy the backend `API_TOKEN` into both Render (server) and the public prefixed variable for client fallbacks.

### `backend-base-url`
- **Purpose:** Verifies the frontend knows where to call the backend API.
- **Fails When:** `NEXT_PUBLIC_BACKEND_API_BASE_URL` is empty.
- **Impact:** All fetches default to an invalid URL, resulting in failed requests before reaching the backend.
- **Remediation:** Set `NEXT_PUBLIC_BACKEND_API_BASE_URL` to the deployed backend origin (or override with `BACKEND_API_BASE_URL`).

### `git-commit` *(warning)*
- **Purpose:** Encourages release traceability across frontend builds.
- **Warns When:** Commit metadata is missing from the deployment environment.
- **Impact:** Harder to correlate Sentry errors or console logs with the source revision.
- **Remediation:** Ensure the hosting provider exposes `VERCEL_GIT_COMMIT_SHA`/`NEXT_PUBLIC_VERCEL_GIT_COMMIT_SHA` (or `GIT_COMMIT`).

## Additional Tips

- Render automatically sets `RENDER_GIT_COMMIT`; local development falls back to `git rev-parse HEAD` for logging.
- `RELEASE_VERSION` is optional but recommended so Sentry and startup logs correlate with deployment artifacts.
- Keep a copy of `backend/RENDER_ENV_TEMPLATE.txt` handy when updating dashboard values—it includes every variable each validator expects.
