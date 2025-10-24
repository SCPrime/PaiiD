# Release Notes – 2025-10-24

## Authentication & Session Management
- Replaced legacy API token guard with `CurrentUser` / `require_current_user` wrappers around `get_current_user`.
- Updated test fixtures to mint real JWT access/refresh pairs using `create_token_pair` and validated refresh rotation.
- Added coverage for protected route access without headers and with valid tokens.

## Options API Reliability
- Hardened `/api/options/chains/{symbol}` to annotate responses with `source` and cache metadata.
- Patched `/api/options/expirations/{symbol}` to return clean lists and guard against misconfigured Tradier clients, eliminating the 500 regression.
- Added pytest coverage for success and failure paths plus mocked Tradier chain payloads.

## Market & Portfolio Metadata
- Market quote/quotes/scanner endpoints now emit `source` (and `cached` when appropriate) to unblock downstream provenance tracking.
- Portfolio account/positions responses include `source` + `user_id`, ensuring UI consumers know which session produced cached payloads.
- Front-end data fetchers (`frontend/lib/marketData.ts`) accept the enriched payloads while remaining backward compatible.

## Testing & Tooling
- Extended backend API tests to validate updated response envelopes, caching semantics, and error handling.
- Added dedicated options endpoint test suite covering chains, expirations, and Tradier error propagation.
- Playwright/API suites should be updated to exercise token refresh and options flows (see `/frontend/tests` for examples).

## Deployment Notes
- Set `JWT_SECRET_KEY` and `TRADIER_ACCOUNT_ID` in environments before bootstrapping the app.
- Cached responses may now contain structured metadata; verify Redis invalidation rules to account for the new schema keys.
