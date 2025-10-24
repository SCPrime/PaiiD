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

### Optional system metrics dependency

The health monitoring service exposes CPU, memory, and disk statistics when
[`psutil`](https://pypi.org/project/psutil/) is available. The backend now
degrades gracefully if the native wheel cannot be installed (for example in CI
environments running `pytest`).

For production images where these metrics are required, install `psutil`
alongside the other backend dependencies after ensuring the necessary system
packages (such as build tools or `python3-dev`) are present:

```bash
pip install psutil>=5.9.0
```

On Debian-based systems without wheels, install compilation prerequisites first:

```bash
apt-get update && apt-get install -y gcc python3-dev
```

With the optional dependency installed, the `/api/health/detailed` endpoint will
report live system statistics. Without it, the endpoint continues to function
using lightweight fallback metrics.

## Endpoints

- `GET /api/health` - Health check
- `GET /api/health/ready` - Legacy readiness check
- `GET /api/health/readiness` - Kubernetes-style readiness probe
- `GET /api/health/liveness` - Liveness probe
- `GET /api/health/sentry-test` - Triggers a 500 error for Sentry verification
- `GET /api/settings` - Get trading settings
- `POST /api/settings` - Update trading settings (authenticated)
- `GET /api/portfolio/positions` - Get portfolio positions (authenticated)
- `POST /api/trading/execute` - Execute trades (authenticated)
- `POST /api/admin/kill` - Toggle kill switch (authenticated)
- `WS /api/ws` - WebSocket for real-time data