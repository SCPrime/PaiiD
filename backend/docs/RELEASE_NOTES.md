# Release Notes - Backend Authentication & Options Fixes

## Summary
- Restored JWT authentication across all routers and services using shared dependency helpers.
- Fixed options chain regression by reintroducing the `source` field, hardening the expirations endpoint, and preventing negative `days_to_expiry` values.
- Added API and Playwright integration tests covering token refresh flows, options chains, and error handling for Tradier failures.
- Updated the Next.js proxy to require caller Authorization headers and surface backend errors.

## Details
- FastAPI routers now depend on `get_current_user` via centralized helpers for consistent authorization checks.
- Options responses once again include `source="tradier"`, and expirations handle both list and single-date payloads while clamping `days_to_expiry` to zero.
- New tests validate login, refresh, logout, options success, and 500-error scenarios to prevent regressions across both pytest and Playwright.
- Frontend proxy now rejects unauthenticated requests instead of falling back to legacy API tokens, ensuring JWT enforcement end-to-end.

## Testing
- `pytest backend/tests -q`
