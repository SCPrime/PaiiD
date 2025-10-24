# PaiiD Backend

FastAPI backend service for the PaiiD application.

## Features

- JWT-based authentication with refresh tokens, session tracking, and reusable dependency helpers
- Idempotency key support for safe order execution
- Global kill-switch for emergency trading halt
- WebSocket support for real-time market data
- Health, readiness, and telemetry endpoints
- Options chain and expiration data enriched with `source` metadata

## Deployment

This backend is designed to be deployed on Render or Fly.io.

### Render Deployment

1. Connect your repository to Render
2. Create a new Web Service
3. Set Root Directory to `backend/`
4. Configure environment variables:
   - `JWT_SECRET_KEY`: Secret key used to sign access and refresh tokens
   - `LIVE_TRADING`: Set to "false" for safety (default)
   - `ALLOW_ORIGIN`: Your Vercel frontend URL

### Environment Variables

- `JWT_SECRET_KEY`: Secret key used to sign access and refresh tokens (required)
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`: Access token lifetime in minutes (default: 15)
- `JWT_REFRESH_TOKEN_EXPIRE_DAYS`: Refresh token lifetime in days (default: 7)
- `LIVE_TRADING`: Enable live trading (default: false)
- `IDMP_TTL_SECONDS`: Idempotency key TTL in seconds (default: 600)
- `ALLOW_ORIGIN`: Allowed CORS origin for frontend

## Endpoints

- `POST /auth/login` - Authenticate and receive access + refresh token pair
- `POST /auth/refresh` - Exchange refresh token for a new token pair
- `POST /auth/logout` - Invalidate all sessions for the current user
- `GET /api/health` - Public health check
- `GET /api/health/detailed` - Authenticated health metrics
- `GET /api/options/chains/{symbol}` - Options chain data with Greeks (authenticated)
- `GET /api/options/expirations/{symbol}` - Available expirations (authenticated)
- `GET /api/portfolio/summary` - Portfolio summary analytics (authenticated)
- `GET /api/portfolio/positions` - Get portfolio positions (authenticated)
- `POST /api/trading/execute` - Execute paper trades via Tradier/Alpaca (authenticated, idempotent)
- `WS /api/stream/*` - Server-Sent Events and streaming endpoints