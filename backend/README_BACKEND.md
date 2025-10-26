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

#### Core Application Settings
- `API_TOKEN`: Authentication token for API access (required)
- `LIVE_TRADING`: Enable live trading mode (default: false)
- `IDMP_TTL_SECONDS`: Idempotency key TTL in seconds (default: 600)
- `ALLOW_ORIGIN`: Allowed CORS origin for frontend
- `TESTING`: Enable testing mode (default: false)
- `LOG_LEVEL`: Logging level (default: INFO)

#### Trading API Credentials
**Tradier API (Market Data & Quotes)**
- `TRADIER_API_KEY`: Tradier API key for market data access (required)
- `TRADIER_ACCOUNT_ID`: Tradier account ID for trading operations (required)
- `TRADIER_API_BASE_URL`: Tradier API base URL (default: https://api.tradier.com/v1)

**Alpaca API (Paper Trading Execution)**
- `ALPACA_PAPER_API_KEY`: Alpaca paper trading API key (required)
- `ALPACA_PAPER_SECRET_KEY`: Alpaca paper trading secret key (required)

#### AI & External Services
- `ANTHROPIC_API_KEY`: Anthropic API key for AI fallback services
- `GITHUB_WEBHOOK_SECRET`: GitHub webhook secret for repository monitoring

#### Database & Caching
- `DATABASE_URL`: Database connection URL (SQLite/PostgreSQL)
- `REDIS_URL`: Redis connection URL for caching and sessions

#### Error Tracking & Monitoring
- `SENTRY_DSN`: Sentry DSN for error tracking (required for production)
- `SENTRY_ENVIRONMENT`: Sentry environment (default: development)

#### JWT Authentication (Multi-User System)
- `JWT_SECRET_KEY`: Secret key for JWT token signing (required)
- `JWT_ALGORITHM`: JWT algorithm (default: HS256)
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`: Access token expiration (default: 15)
- `JWT_REFRESH_TOKEN_EXPIRE_DAYS`: Refresh token expiration (default: 7)

#### Health Monitoring Requirements
For accurate health signals, ensure these environment variables are properly configured:
- All trading API credentials must be set for dependency health checks
- Database and Redis URLs for comprehensive readiness probes
- Sentry DSN for production error monitoring

## Endpoints

### Health & Monitoring
- `GET /api/health` - Basic health check (public)
- `GET /api/health/detailed` - Detailed health metrics (authenticated)
- `GET /api/health/ready` - Kubernetes-style readiness probe
- `GET /api/health/liveness` - Kubernetes-style liveness probe
- `GET /api/health/ready/full` - Comprehensive readiness check (DB, Redis, streaming, AI)

### Trading & Portfolio
- `GET /api/settings` - Get trading settings
- `POST /api/settings` - Update trading settings (authenticated)
- `GET /api/portfolio/positions` - Get portfolio positions (authenticated)
- `POST /api/trading/execute` - Execute trades (authenticated)
- `POST /api/admin/kill` - Toggle kill switch (authenticated)

### Real-time Data
- `WS /api/ws` - WebSocket for real-time market data