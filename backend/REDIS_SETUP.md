# Redis Cache Setup Guide

## Overview

Redis is used for caching frequently accessed data to reduce API load and improve response times. The application works without Redis (graceful fallback), but performance is significantly improved with it enabled.

## Setup Steps

### 1. Create Redis Instance on Render

1. Go to Render Dashboard: https://dashboard.render.com
2. Click **"New +"** → **"Redis"**
3. Configure:
   - **Name**: `paiid-redis`
   - **Plan**: **Free** (25MB, perfect for development)
   - **Region**: Same as your PostgreSQL (e.g., Oregon)
4. Click **"Create Redis"**

### 2. Get Redis Connection URL

1. Once created, click on your Redis instance
2. Find **"Internal Redis URL"** or **"External Redis URL"**
   - For local development: Use **External URL**
   - For Render-hosted backend: Use **Internal URL** (faster, free bandwidth)

Format: `redis://default:password@hostname:port`

### 3. Add REDIS_URL to Environment

Edit `backend/.env` and add:

```bash
# ========================================
# REDIS CACHE (Phase 2.5)
# ========================================
REDIS_URL=redis://default:your_password@your_host:port
```

**Production (Render)**: Add REDIS_URL as environment variable in Render backend service settings.

### 4. Restart Backend

```bash
# Local development
cd backend
python -m uvicorn app.main:app --reload --port 8001
```

Expected startup logs:
```
[OK] Redis cache connected
[OK] Cache service initialized
```

If Redis is unavailable:
```
[WARNING] Redis connection failed: ... - caching disabled
[OK] Cache service initialized
```

## Verification

### Check Cache is Working

1. **Test market indices endpoint**:
   ```bash
   # First request (cache miss - hits Tradier API)
   curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8001/api/market/indices

   # Second request within 60s (cache hit - instant response)
   curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8001/api/market/indices
   ```

2. **Check backend logs**:
   ```
   First request:
   [Market] ✅ Fetched live data from Tradier for Dow/NASDAQ

   Second request:
   [Market] ✅ Cache HIT for indices
   ```

### Cached Endpoints

| Endpoint | TTL | Purpose |
|----------|-----|---------|
| `/api/market/indices` | 60s | Dow Jones & NASDAQ data |
| `/api/positions` | 30s | Portfolio positions |
| `/api/market/quote/{symbol}` | 15s | Real-time quotes |

## Monitoring & Instrumentation

### 1. Render Redis Dashboard

1. Open the Redis service in the [Render dashboard](https://dashboard.render.com).
2. Confirm the instance status is **Live** and review the **Uptime** chart for drops.
3. Inspect **Connections** and **Memory Usage** metrics; sustained spikes usually mean cache churn.
4. If metrics appear stale, use the **Manual Refresh** button in the top-right corner of the dashboard.
5. Capture a screenshot of the graphs after incidents so the team can compare trends during postmortems.

> ℹ️ The Render dashboard is the source of truth for availability. The local development environment used for these docs does not have access to hosted metrics, so always verify directly in Render before assuming Redis is healthy.

### 2. Backend Runtime Logs

- Cache initialization now emits structured log entries such as `Redis cache connected` and `Redis URL not configured`.
- Every interaction is instrumented:
  - `Redis GET hit/miss` entries confirm cache utilization per key.
  - `Redis SET succeeded` includes TTL metadata for validation.
  - `Redis unavailable during ...` entries highlight fallback events when Redis is down.
- Use `docker logs`, `uvicorn` output, or your Render service logs to review these messages in real time. Filtering for `Redis` quickly surfaces cache behaviour during incidents.

### 3. Alerting Hooks (Optional)

- Forward the Redis logs to your monitoring stack (e.g., Datadog, Grafana Loki) to build automated alerts on repeated failures.
- Render Pro plans expose metrics via Prometheus; connect them to Grafana for long-term trend analysis if you outgrow the free dashboard.

## Fallback Behaviour

- If `REDIS_URL` is missing or invalid, the backend logs `Redis URL not configured; cache service disabled` and continues serving requests without caching.
- When Redis becomes unavailable at runtime, cache operations short-circuit, log `Redis unavailable during ...`, and return safe defaults (`None`/`False`) so API handlers proceed without raising errors.
- Serialization issues (e.g., attempting to cache non-JSON data) are caught and logged as `Redis SET serialization error`, preventing malformed payloads from poisoning the cache.
- Use these logs to decide when to switch the frontend to reduced polling modes or when to trigger manual cache flushes once Redis is restored.

## Performance Metrics

### API Call Reduction

**Scenario**: Frontend polls `/api/market/indices` every 5 seconds

| Period | Without Cache | With Cache (60s TTL) | Reduction |
|--------|---------------|----------------------|-----------|
| 1 minute | 12 API calls | 1 API call | 92% |
| 1 hour | 720 API calls | 60 API calls | 92% |
| 1 day | 17,280 API calls | 1,440 API calls | 92% |

### Response Time Improvement

| Endpoint | Without Cache | With Cache | Improvement |
|----------|---------------|------------|-------------|
| Market indices | ~300-500ms | ~5-10ms | 95% |
| Positions | ~200-400ms | ~5-10ms | 97% |
| Quotes | ~150-300ms | ~5-10ms | 96% |

## Cache Management

### Clear Cache Manually

```python
# In backend console or route
from app.services.cache import get_cache

cache = get_cache()

# Clear specific key
cache.delete("market:indices")

# Clear all market data
cache.clear_pattern("market:*")

# Clear all quotes
cache.clear_pattern("quote:*")
```

### Cache TTL Strategy

- **60s (Market Indices)**: Dow/NASDAQ change slowly, 1-minute lag acceptable
- **30s (Positions)**: Balance between freshness and API load
- **15s (Quotes)**: Near real-time for active trading decisions

### Adjust TTL

Edit TTL values in route files:

```python
# backend/app/routers/market.py
cache.set(cache_key, result, ttl=60)  # Change to 120 for 2 minutes

# backend/app/routers/portfolio.py
cache.set(cache_key, positions, ttl=30)  # Change to 60 for 1 minute

# backend/app/routers/market_data.py
cache.set(cache_key, result, ttl=15)  # Change to 30 for 30 seconds
```

## Troubleshooting

### "Redis connection failed" on startup

**Cause**: REDIS_URL not set or incorrect

**Fix**:
1. Verify REDIS_URL in `.env`
2. Test connection manually:
   ```python
   import redis
   r = redis.from_url("redis://...")
   r.ping()  # Should return True
   ```

### Cache not working (always cache miss)

**Possible causes**:
1. Redis not connected (check startup logs)
2. TTL too short (data expires before second request)
3. Cache key mismatch (check cache keys in code)

**Debug**:
```python
# Add to route
print(f"Cache available: {cache.available}")
print(f"Cache get result: {cache.get(cache_key)}")
```

### High memory usage

**Cause**: Too many cached keys or TTL too long

**Fix**:
1. Reduce TTL values
2. Clear old cache patterns
3. Upgrade Redis plan (Render free tier = 25MB)

### Render free tier limits

- **Storage**: 25MB
- **Connections**: 10 concurrent
- **Eviction**: LRU (least recently used)

For production with heavy traffic, upgrade to Starter plan ($7/month, 256MB).

## Redis CLI Access

### Install Redis CLI

**macOS**:
```bash
brew install redis
```

**Windows**:
```bash
# Use WSL or download from https://github.com/microsoftarchive/redis/releases
```

**Linux**:
```bash
sudo apt-get install redis-tools
```

### Connect to Render Redis

```bash
redis-cli -u redis://default:password@hostname:port

# Test connection
> PING
PONG

# List all keys
> KEYS *

# Get cached value
> GET market:indices

# Check TTL
> TTL market:indices

# Clear all cache
> FLUSHALL
```

## Next Phase

Once Redis is working, proceed with:
- **Task 3**: Sentry Error Tracking
- **Task 4**: Critical Backend Tests

---

**Questions?** Check logs for `[WARNING]` or `[ERROR]` messages related to cache.
