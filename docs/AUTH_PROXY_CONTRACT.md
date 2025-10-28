# Auth–Proxy Contract

## Overview
- Service endpoints (telemetry, monitor, analytics): API token required. Proxy injects `Authorization: Bearer ${API_TOKEN}`.
- User endpoints (users, orders, portfolio, settings): JWT required. Proxy preserves client `Authorization` header.
- Public endpoints: health, selected telemetry reads.

## Proxy Behavior
- Route-aware auth (toggle via `ROUTE_AUTH_AWARE_ENABLED`, default true):
  - apiToken: `telemetry/*`, `monitor/*`, `analytics/*`
  - jwt: `users/*`, `orders/*`, `portfolio/*`, `settings/*`
  - none: others
- Env-driven CORS via `ALLOWED_ORIGINS`.
- Optional OpenAPI allowlist via `USE_OPENAPI_ALLOWLIST`.

## Diagnostics
- Proxy: `GET /api/proxy/_routes`
- Backend: `GET /api/_auth/echo`


