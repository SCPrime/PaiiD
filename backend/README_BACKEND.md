# PaiiD Backend

FastAPI backend service for the PaiiD application.

## Features

- Token-based authentication
- Idempotency key support for safe order execution
- Global kill-switch for emergency trading halt
- WebSocket support for real-time market data
- Health and readiness endpoints

## Deployment

This backend is designed to be deployed on Render or Fly.io.

### Render Deployment

1. Connect your repository to Render
2. Create a new Web Service
3. Set Root Directory to `backend/`
4. Configure environment variables:
   - `API_TOKEN`: Secure random token for authentication
   - `LIVE_TRADING`: Set to "false" for safety (default)
   - `ALLOW_ORIGIN`: Your Vercel frontend URL

### Environment Variables

- `API_TOKEN`: Authentication token (required)
- `LIVE_TRADING`: Enable live trading (default: false)
- `IDMP_TTL_SECONDS`: Idempotency key TTL in seconds (default: 600)
- `ALLOW_ORIGIN`: Allowed CORS origin for frontend
- Observability-related variables are documented in
  [`docs/OBSERVABILITY_RUNBOOK.md`](docs/OBSERVABILITY_RUNBOOK.md).

## Observability

- Structured JSON logging is enabled by default and includes Datadog trace IDs
  when tracing is active.
- Sentry, Datadog, and New Relic can be enabled through environment variables;
  see the [Observability Runbook](docs/OBSERVABILITY_RUNBOOK.md) for setup and
  verification procedures.

## Endpoints

- `GET /api/health` - Health check
- `GET /api/ready` - Readiness check
- `GET /api/settings` - Get trading settings
- `POST /api/settings` - Update trading settings (authenticated)
- `GET /api/portfolio/positions` - Get portfolio positions (authenticated)
- `POST /api/trading/execute` - Execute trades (authenticated)
- `POST /api/admin/kill` - Toggle kill switch (authenticated)
- `WS /api/ws` - WebSocket for real-time data