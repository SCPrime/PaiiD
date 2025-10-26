# PaiiD System Architecture

## Overview

PaiiD (Personal Artificial Intelligence Investment Dashboard) is a full-stack AI-powered trading application featuring real-time market data integration, intelligent trade execution, and a unique 10-stage radial workflow interface. The system follows a modern monorepo architecture with clear separation of concerns between frontend presentation, backend business logic, and external service integrations.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            CLIENT LAYER                                  │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │  Next.js 14 Frontend (TypeScript + React 18)                   │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │    │
│  │  │ Radial Menu  │  │ Trading Forms│  │  Analytics   │         │    │
│  │  │   (D3.js)    │  │  Components  │  │  Dashboard   │         │    │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │    │
│  │         │                 │                  │                  │    │
│  │         └─────────────────┴──────────────────┘                  │    │
│  │                           │                                      │    │
│  │                    API Proxy Layer                              │    │
│  │                 /api/proxy/[...path]                            │    │
│  └────────────────────────────┼───────────────────────────────────┘    │
└─────────────────────────────────┼──────────────────────────────────────┘
                                  │ HTTPS
                                  │
┌─────────────────────────────────┼──────────────────────────────────────┐
│                          SERVER LAYER                                   │
│  ┌───────────────────────────────────────────────────────────────┐    │
│  │  FastAPI Backend (Python 3.10+)                                │    │
│  │  ┌──────────────────────────────────────────────────────────┐ │    │
│  │  │              Router Layer (25 modules)                    │ │    │
│  │  │  auth • portfolio • orders • market • ai • ml • ...      │ │    │
│  │  └────────────┬───────────────────────┬─────────────────────┘ │    │
│  │               │                       │                        │    │
│  │  ┌────────────┴─────────┐  ┌─────────┴──────────┐            │    │
│  │  │   Service Layer      │  │   Database Layer   │            │    │
│  │  │  • Tradier Client    │  │  • PostgreSQL      │            │    │
│  │  │  • Alpaca Client     │  │  • SQLAlchemy ORM  │            │    │
│  │  │  • Anthropic Client  │  │  • Alembic         │            │    │
│  │  │  • Cache Service     │  │                    │            │    │
│  │  │  • WebSocket Stream  │  │                    │            │    │
│  │  └──────────────────────┘  └────────────────────┘            │    │
│  └───────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────┼──────────────────────────────────────┘
                                  │
┌─────────────────────────────────┼──────────────────────────────────────┐
│                        EXTERNAL SERVICES                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                │
│  │   Tradier    │  │    Alpaca    │  │  Claude AI   │                │
│  │  (Market     │  │  (Paper      │  │  (Anthropic) │                │
│  │   Data)      │  │   Trading)   │  │              │                │
│  └──────────────┘  └──────────────┘  └──────────────┘                │
│  • Real-time quotes  • Order execution  • AI recommendations          │
│  • Options chains    • Position data    • Chat interface              │
│  • Historical data   • Account balance  • Strategy suggestions        │
│  • Streaming SSE     • Paper trading    • Pattern recognition         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Architecture

### 1. Market Data Flow (Tradier → Frontend)

```
┌──────────┐       ┌──────────┐       ┌──────────┐       ┌──────────┐
│ Frontend │──1──▶ │   API    │──2──▶ │  Cache   │──3──▶ │  Tradier │
│  Request │       │  Proxy   │       │  Service │       │   API    │
└──────────┘       └──────────┘       └──────────┘       └──────────┘
     ▲                                       │                   │
     │                                       │                   │
     └────────────6─────────────────────────┴────────5──────────┘
                  Response with data

Flow Steps:
1. User requests quote for AAPL
2. Frontend calls /api/proxy/api/market/quote/AAPL
3. Backend checks Redis cache (TTL: 5 seconds)
4. Cache miss → Fetch from Tradier API
5. Store in cache with TTL
6. Return JSON response to frontend
```

### 2. Trade Execution Flow (Frontend → Alpaca)

```
┌──────────┐       ┌──────────┐       ┌──────────┐       ┌──────────┐
│  User    │──1──▶ │ Execute  │──2──▶ │  Orders  │──3──▶ │  Alpaca  │
│  Input   │       │  Form    │       │  Router  │       │  Paper   │
└──────────┘       └──────────┘       └──────────┘       └──────────┘
                         │                  │                   │
                         │                  │                   │
                         └────────6─────────┴────────5──────────┘
                              Order confirmation

Flow Steps:
1. User fills order form (symbol, qty, side)
2. Frontend validates and sends POST /api/proxy/api/orders
3. Backend authenticates user (JWT or API token)
4. Backend sends order to Alpaca Paper Trading API
5. Alpaca executes order and returns fill data
6. Backend caches result and returns to frontend
7. Frontend displays order confirmation
```

### 3. AI Recommendation Flow (Claude AI Integration)

```
┌──────────┐       ┌──────────┐       ┌──────────┐       ┌──────────┐
│  Market  │──1──▶ │    ML    │──2──▶ │   AI     │──3──▶ │  Claude  │
│   Data   │       │  Analysis│       │  Router  │       │   API    │
└──────────┘       └──────────┘       └──────────┘       └──────────┘
                         │                  │                   │
                         │                  │                   │
                         └────────6─────────┴────────5──────────┘
                           AI recommendation response

Flow Steps:
1. User requests AI recommendation
2. Backend fetches market data (Tradier)
3. ML service analyzes patterns (scikit-learn)
4. AI router sends context to Claude API
5. Claude generates recommendation with confidence score
6. Backend returns recommendation to frontend
7. Frontend displays in AIRecommendations component
```

## Technology Stack

### Frontend Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **Next.js** | 14.2.33 | React framework with Pages Router |
| **React** | 18.3.1 | UI component library |
| **TypeScript** | 5.9.2 | Type-safe JavaScript |
| **D3.js** | 7.9.0 | Radial menu visualization |
| **Anthropic SDK** | 0.65.0 | AI chat integration |
| **SWR** | 2.2.4 | Data fetching and caching |
| **React Split** | 2.0.14 | Split-screen layout |
| **Chart.js** | 4.5.1 | Financial charts |
| **Lightweight Charts** | 5.0.9 | Trading view charts |

**Styling Approach:**
- Inline styles only (no CSS frameworks)
- Glassmorphism dark theme
- Color palette: `#0f172a`, `#1f2937`, `#1e293b`
- Teal accents: `#10b981`, `#1a7560`

### Backend Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **FastAPI** | 0.109.0+ | Web framework |
| **Uvicorn** | 0.27.0+ | ASGI server |
| **Python** | 3.10+ | Programming language |
| **SQLAlchemy** | 2.0.0+ | ORM for database |
| **Alembic** | 1.13.0+ | Database migrations |
| **PostgreSQL** | - | Production database |
| **Redis** | 5.0.0+ | Caching layer |
| **Pydantic** | 2.5.0+ | Data validation |
| **APScheduler** | 3.10.4+ | Background tasks |
| **Sentry SDK** | 1.40.0+ | Error tracking |

**Key Libraries:**
- `alpaca-py` (0.21.0+) - Paper trading execution
- `anthropic` (0.18.0+) - AI integration
- `scikit-learn` (1.3.0+) - ML algorithms
- `pandas` (2.0.0+) - Data analysis
- `py_vollib` (1.0.1+) - Options Greeks
- `tenacity` (8.2.0+) - Retry logic

### External Services

**1. Tradier API (Market Data)**
- **Purpose:** Real-time market quotes, options chains, historical data
- **Type:** Live production account (NO delay)
- **Base URL:** `https://api.tradier.com/v1`
- **Authentication:** Bearer token
- **Features:**
  - Real-time quotes (5-second cache)
  - Options chains with Greeks
  - Historical OHLCV bars
  - Market news and fundamentals
  - Streaming quotes via WebSocket

**2. Alpaca API (Trade Execution)**
- **Purpose:** Paper trading execution ONLY
- **Type:** Paper trading account
- **Base URL:** `https://paper-api.alpaca.markets`
- **Authentication:** API Key + Secret
- **Features:**
  - Paper trade execution
  - Position management
  - Account balance tracking
  - Order status monitoring

**3. Anthropic Claude API (AI Features)**
- **Purpose:** AI recommendations, chat interface
- **Model:** Claude 3.5 Sonnet
- **Features:**
  - Strategy recommendations
  - Market analysis
  - Conversational onboarding
  - Pattern recognition insights

## Key Architectural Decisions

### 1. Data Source Separation

**Decision:** Use Tradier for ALL market data, Alpaca ONLY for paper trading.

**Rationale:**
- Tradier provides real-time data with NO delay (live account)
- Alpaca's market data has 15-minute delay on free tier
- Clear separation of concerns (data vs execution)
- Future flexibility to switch execution providers

**Implementation:**
```python
# backend/app/routers/market.py - Market data from Tradier
@router.get("/market/quote/{symbol}")
async def get_quote(symbol: str):
    return tradier_client.get_quote(symbol)

# backend/app/routers/orders.py - Trade execution via Alpaca
@router.post("/orders")
async def create_order(order: OrderRequest):
    return alpaca_client.submit_order(order)
```

### 2. API Proxy Pattern

**Decision:** Route all backend requests through frontend API proxy.

**Rationale:**
- Avoids CORS configuration issues
- Centralizes authentication token injection
- Simplifies frontend API calls
- Enables request/response transformation

**Implementation:**
```typescript
// frontend/pages/api/proxy/[...path].ts
export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const path = (req.query.path as string[]).join('/');
  const backendUrl = `${process.env.NEXT_PUBLIC_BACKEND_API_BASE_URL}/${path}`;

  const response = await fetch(backendUrl, {
    headers: {
      'Authorization': `Bearer ${process.env.NEXT_PUBLIC_API_TOKEN}`
    }
  });

  return res.status(response.status).json(await response.json());
}
```

### 3. Caching Strategy

**Decision:** Redis for production, in-memory fallback for development.

**TTL Configuration:**
| Data Type | TTL | Rationale |
|-----------|-----|-----------|
| Quotes | 5s | Near real-time updates |
| Options Chains | 60s | Moderate update frequency |
| Historical Bars | 1hr | Static past data |
| News Articles | 5min | Moderate freshness |
| Company Info | 24hr | Rarely changes |

**Implementation:**
```python
# backend/app/services/cache.py
class CacheService:
    def __init__(self):
        self.redis = redis.Redis() if REDIS_URL else None
        self.memory_cache = {}  # Fallback

    def get(self, key: str) -> Optional[str]:
        if self.redis:
            return self.redis.get(key)
        return self.memory_cache.get(key)
```

### 4. Monorepo Structure

**Decision:** Separate frontend/ and backend/ directories with independent dependencies.

**Rationale:**
- Clear separation of concerns
- Independent deployment to Render
- Different technology stacks (Node vs Python)
- Simplified CI/CD pipelines

**Structure:**
```
PaiiD/
├── frontend/          # Next.js app (Node.js)
│   ├── package.json
│   └── Dockerfile
├── backend/           # FastAPI app (Python)
│   ├── requirements.txt
│   └── app/
└── docs/              # Shared documentation
```

### 5. Authentication Strategy

**Decision:** Dual authentication (JWT for users, API token for admin).

**Rationale:**
- JWT tokens for multi-user system (future-proof)
- API tokens for admin/service authentication
- Unified auth middleware handles both types
- Security best practices (short-lived JWTs)

**Implementation:**
```python
# backend/app/core/unified_auth.py
async def get_current_user_unified(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    # Try JWT first
    if token.startswith("eyJ"):
        return verify_jwt_token(token)
    # Fall back to API token
    return verify_api_token(token)
```

## Component Architecture

### Frontend Component Hierarchy

```
pages/index.tsx (Dashboard)
├── RadialMenu.tsx (D3.js visualization)
│   ├── 10 workflow segments
│   └── Center logo with live data
├── Split Layout (react-split)
│   ├── Left Panel
│   │   ├── CompletePaiiDLogo
│   │   ├── TradingModeIndicator
│   │   └── Scaled RadialMenu (0.5x)
│   └── Right Panel
│       └── Dynamic Workflow Content
│           ├── MorningRoutineAI
│           ├── PositionManager
│           ├── ExecuteTradeForm
│           ├── RiskCalculator
│           ├── MarketScanner
│           ├── AIRecommendations
│           ├── Settings
│           ├── NewsReview
│           ├── StrategyBuilderAI
│           └── Backtesting
├── UserSetupAI (onboarding modal)
├── AIChat (floating chat widget)
├── CommandPalette (Cmd+K)
├── HelpPanel (contextual help)
└── ToastContainer (notifications)
```

### Backend Router Architecture

**25 API Routers:**

| Router | Prefix | Purpose |
|--------|--------|---------|
| `auth.py` | `/api/auth` | User authentication (JWT) |
| `health.py` | `/api/health` | Health checks |
| `portfolio.py` | `/api/portfolio` | Portfolio data |
| `positions.py` | `/api/positions` | Position management |
| `orders.py` | `/api/orders` | Trade execution |
| `market.py` | `/api/market` | Market data (Tradier) |
| `market_data.py` | `/api/market-data` | Extended market data |
| `options.py` | `/api/options` | Options chains and Greeks |
| `proposals.py` | `/api/proposals` | Trade proposals |
| `ai.py` | `/api/ai` | AI recommendations |
| `claude.py` | `/api/claude` | Claude chat |
| `ml.py` | `/api/ml` | ML models |
| `ml_sentiment.py` | `/api/ml-sentiment` | Sentiment analysis |
| `news.py` | `/api/news` | Market news |
| `stock.py` | `/api/stock` | Stock fundamentals |
| `screening.py` | `/api/screening` | Stock screener |
| `strategies.py` | `/api/strategies` | Strategy management |
| `backtesting.py` | `/api/backtesting` | Backtest engine |
| `analytics.py` | `/api/analytics` | P&L analytics |
| `scheduler.py` | `/api/scheduler` | Background tasks |
| `stream.py` | `/api/stream` | WebSocket streaming |
| `monitoring.py` | `/api/monitoring` | System monitoring |
| `telemetry.py` | `/api/telemetry` | Event tracking |
| `users.py` | `/api/users` | User management |
| `settings.py` | `/api/settings` | User settings |

## Database Schema

### Core Tables

**users** - User accounts
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);
```

**user_sessions** - Active sessions
```sql
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    session_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**strategies** - Trading strategies
```sql
CREATE TABLE strategies (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(100) NOT NULL,
    config JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**trades** - Trade history
```sql
CREATE TABLE trades (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    symbol VARCHAR(10) NOT NULL,
    quantity INTEGER NOT NULL,
    side VARCHAR(10) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    executed_at TIMESTAMP DEFAULT NOW()
);
```

**ai_recommendations** - AI suggestions
```sql
CREATE TABLE ai_recommendations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    symbol VARCHAR(10) NOT NULL,
    action VARCHAR(20) NOT NULL,
    confidence DECIMAL(5, 2) NOT NULL,
    reasoning TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Security Architecture

### Authentication Flow

```
1. User Login
   ├─▶ POST /api/auth/login
   │   └─▶ Validate credentials (bcrypt)
   ├─▶ Generate JWT tokens
   │   ├─▶ Access Token (15 min TTL)
   │   └─▶ Refresh Token (7 day TTL)
   └─▶ Return tokens to client

2. Authenticated Request
   ├─▶ Client sends Authorization: Bearer <jwt>
   ├─▶ Middleware validates JWT
   │   ├─▶ Verify signature (HS256)
   │   ├─▶ Check expiration
   │   └─▶ Extract user_id
   └─▶ Inject User object into request

3. Token Refresh
   ├─▶ POST /api/auth/refresh
   ├─▶ Validate refresh token
   └─▶ Issue new access token
```

### Security Layers

**1. CORS Protection**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://paiid-frontend.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
```

**2. CSRF Protection**
```python
app.add_middleware(CSRFProtectionMiddleware)
```

**3. Rate Limiting**
```python
@router.get("/api/market/quote/{symbol}")
@limiter.limit("100/minute")
async def get_quote(symbol: str):
    pass
```

**4. Security Headers**
```python
app.add_middleware(SecurityHeadersMiddleware)
# Adds: X-Frame-Options, X-Content-Type-Options, etc.
```

**5. Input Validation**
```python
class OrderRequest(BaseModel):
    symbol: str = Field(..., regex=r"^[A-Z]{1,5}$")
    quantity: int = Field(..., gt=0, le=10000)
    side: Literal["buy", "sell"]
```

## Performance Optimizations

### Frontend Optimizations

**1. Code Splitting**
```typescript
// Dynamic imports for large components
const MorningRoutineAI = dynamic(() => import('../components/MorningRoutineAI'), {
  loading: () => <Spinner />
});
```

**2. SWR Data Fetching**
```typescript
// Automatic caching and revalidation
const { data, error } = useSWR('/api/proxy/api/positions', fetcher, {
  refreshInterval: 30000  // 30 seconds
});
```

**3. Image Optimization**
- Next.js Image component for automatic optimization
- Lazy loading for below-fold images

### Backend Optimizations

**1. Redis Caching**
- 5s TTL for real-time quotes
- 1hr TTL for historical data
- Reduces external API calls by 90%

**2. Database Indexing**
```sql
CREATE INDEX idx_trades_user_symbol ON trades(user_id, symbol);
CREATE INDEX idx_sessions_token ON user_sessions(session_token);
```

**3. Connection Pooling**
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20
)
```

**4. GZIP Compression**
```python
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

## Deployment Architecture

### Production Infrastructure (Render)

```
┌─────────────────────────────────────────────────────────────┐
│                        Render Cloud                          │
│                                                               │
│  ┌────────────────────────┐  ┌────────────────────────┐    │
│  │   Frontend Service     │  │   Backend Service      │    │
│  │  ┌──────────────────┐  │  │  ┌──────────────────┐  │    │
│  │  │  Next.js (Docker)│  │  │  │ FastAPI (Python) │  │    │
│  │  │  Port: 3000      │  │  │  │ Port: $PORT      │  │    │
│  │  └──────────────────┘  │  │  └──────────────────┘  │    │
│  │  Auto-deploy: main     │  │  Auto-deploy: main     │    │
│  └────────────────────────┘  └────────────────────────┘    │
│           │                             │                    │
│           │                             │                    │
│  ┌────────┴─────────────────────────────┴────────────┐     │
│  │            PostgreSQL Database                     │     │
│  │          (Managed Render PostgreSQL)               │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

**Frontend Deployment:**
- Dockerfile with standalone Next.js build
- Environment variables via Render dashboard
- Custom domain support
- Automatic SSL/TLS

**Backend Deployment:**
- Python runtime with requirements.txt
- Uvicorn ASGI server
- Environment variables for secrets
- Health check endpoint: `/api/health`

**Database:**
- Managed PostgreSQL instance
- Automatic backups
- Connection pooling
- SSL connections

## Monitoring and Observability

### Error Tracking (Sentry)

```python
sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    environment="production",
    traces_sample_rate=0.1,
    profiles_sample_rate=0.1
)
```

### Logging Strategy

```python
import logging

logger = logging.getLogger(__name__)

# Structured logging with context
logger.info(
    "Trade executed",
    extra={
        "user_id": user.id,
        "symbol": "AAPL",
        "quantity": 10,
        "side": "buy"
    }
)
```

### Health Checks

```python
@router.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "services": {
            "database": check_database(),
            "redis": check_redis(),
            "tradier": check_tradier(),
            "alpaca": check_alpaca()
        }
    }
```

## Future Architecture Considerations

### Planned Enhancements

**1. Microservices Split**
- Separate ML service for pattern recognition
- Dedicated streaming service for WebSocket
- Independent scaling per service

**2. Event-Driven Architecture**
- Kafka for event streaming
- Event sourcing for trade history
- CQRS pattern for read/write separation

**3. GraphQL API**
- Replace REST with GraphQL
- Reduce over-fetching
- Better client-side caching

**4. Serverless Functions**
- AWS Lambda for background tasks
- Scheduled jobs via cron
- Auto-scaling for peak loads

## Appendix: Key Files Reference

### Frontend Entry Points
- `frontend/pages/index.tsx` - Main dashboard
- `frontend/pages/_app.tsx` - Global layout
- `frontend/components/RadialMenu.tsx` - D3.js menu
- `frontend/pages/api/proxy/[...path].ts` - API proxy

### Backend Entry Points
- `backend/app/main.py` - FastAPI app initialization
- `backend/app/core/config.py` - Settings and configuration
- `backend/app/routers/` - API endpoint modules (25 routers)
- `backend/app/services/` - Business logic services

### Configuration Files
- `frontend/next.config.js` - Next.js configuration
- `frontend/tsconfig.json` - TypeScript compiler options
- `backend/requirements.txt` - Python dependencies
- `.env` files - Environment variables (not committed)

---

**Document Version:** 1.0.0
**Last Updated:** October 26, 2025
**Maintainer:** PaiiD Development Team
