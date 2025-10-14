# Tradier Real-Time Streaming Implementation Guide

**Status:** NOT YET IMPLEMENTED
**Priority:** HIGH
**Estimated Time:** 8-12 hours
**Phase:** 2.A - Real-Time Market Data

---

## Overview

This guide documents the implementation plan for real-time market data streaming using Tradier API.

**Architecture Decision:**
- **Tradier API:** ALL market data (quotes, bars, options, analysis, streaming)
- **Alpaca API:** ONLY paper trade execution (orders, positions, account)

**Why Tradier?**
- Tradier is the primary data provider for this application
- Consistent data source for all market intelligence
- Alpaca Paper Trading has limited/delayed market data
- Future-proof for live trading migration (Tradier supports live trades)

---

## Phase 1: Research Tradier Streaming Capabilities (2 hours)

### Investigation Points:

1. **Does Tradier have WebSocket support?**
   - Check: https://documentation.tradier.com/brokerage-api/streaming
   - Look for WebSocket endpoints
   - Identify authentication requirements
   - Understand message format (JSON, binary, etc.)

2. **Does Tradier have SSE (Server-Sent Events)?**
   - Check if Tradier offers HTTP/SSE streaming
   - Identify connection limits
   - Check latency vs WebSocket

3. **Polling Alternative (if no streaming)**
   - If Tradier doesn't offer streaming, implement smart polling:
     - Poll `/markets/quotes` every 1-5 seconds
     - Use Redis caching (5s TTL) to distribute to multiple clients
     - Add jitter to prevent thundering herd
     - Monitor rate limits closely

### Deliverable:
- Document Tradier streaming capabilities in this file
- Choose implementation approach (WebSocket, SSE, or polling)
- Identify any API limitations or costs

---

## Phase 2: Implement Core Streaming Service (4 hours)

### File: `backend/app/services/tradier_stream.py`

**Implementation Checklist:**

- [ ] **Connection Management**
  - Initialize connection to Tradier streaming endpoint
  - Handle authentication (API key, token refresh if needed)
  - Implement auto-reconnection with exponential backoff
  - Add connection status monitoring

- [ ] **Quote Subscription**
  - `subscribe_quotes(symbols: List[str])` - Subscribe to real-time quotes
  - Track active subscriptions in `Set[str]`
  - Handle subscription errors gracefully
  - Log subscription events

- [ ] **Quote Unsubscription**
  - `unsubscribe_quotes(symbols: List[str])` - Unsubscribe from quotes
  - Clean up resources when no clients are subscribed
  - Prevent memory leaks from abandoned subscriptions

- [ ] **Message Handling**
  - Parse incoming messages from Tradier
  - Extract: symbol, price (bid/ask/last), volume, timestamp
  - Validate data before caching
  - Handle malformed messages

- [ ] **Redis Caching**
  - Cache latest quote in Redis: `price:{symbol}` (5s TTL)
  - Store: price, bid, ask, volume, timestamp
  - Use JSON format for easy SSE consumption
  - Monitor cache hit/miss rates

- [ ] **Error Handling**
  - Handle network errors (retry logic)
  - Handle API errors (rate limits, authentication)
  - Log all errors with context
  - Emit connection status events

### Example Structure:
```python
class TradierStreamService:
    def __init__(self):
        self.connection = None  # WebSocket or HTTP connection
        self.active_symbols: Set[str] = set()
        self.cache = get_cache()
        self.running = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5

    async def start(self):
        # Connect to Tradier streaming endpoint
        # Register message handlers
        # Run event loop
        pass

    async def stop(self):
        # Gracefully close connection
        # Clean up resources
        pass

    async def _handle_message(self, message: dict):
        # Parse and validate
        # Cache in Redis
        # Notify callbacks (if any)
        pass

    async def _handle_reconnect(self):
        # Exponential backoff: 2^attempts seconds (max 60s)
        # Reset attempts counter on successful connection
        pass
```

---

## Phase 3: Update SSE Endpoints (2 hours)

### File: `backend/app/routers/stream.py`

**Changes Needed:**

1. **Replace Alpaca imports:**
   ```python
   # OLD (REMOVED):
   # from app.services.alpaca_stream import get_alpaca_stream

   # NEW:
   from app.services.tradier_stream import get_tradier_stream
   ```

2. **Update `/stream/prices` endpoint:**
   - Use `get_tradier_stream()` instead of `get_alpaca_stream()`
   - Subscribe to Tradier quotes: `tradier_stream.subscribe_quotes(symbol_list)`
   - Read prices from Redis cache (same pattern as before)
   - Update docstrings to reference Tradier

3. **Update `/stream/status` endpoint:**
   - Return Tradier connection status
   - Show active symbols subscribed to Tradier
   - Include provider name: "Tradier"

4. **Update `/stream/positions` endpoint:**
   - Keep position streaming logic (positions come from Alpaca)
   - BUT: Market prices for P&L calculation come from Tradier
   - Clarify in docstring: "Positions from Alpaca, prices from Tradier"

### Example Updated Endpoint:
```python
@router.get("/stream/prices")
async def stream_prices(
    symbols: str = Query(...),
    _=Depends(require_bearer),
    cache: CacheService = Depends(get_cache)
):
    """
    Stream real-time price updates via Tradier API

    Uses Tradier WebSocket/polling for live market data.
    """
    symbol_list = [s.strip().upper() for s in symbols.split(',')]

    # Subscribe to Tradier streaming
    tradier_stream = get_tradier_stream()
    await tradier_stream.subscribe_quotes(symbol_list)

    # Rest of SSE logic (read from Redis, stream to client)
    # ...
```

---

## Phase 4: Integration & Testing (2 hours)

### Backend Integration:

1. **Update `main.py` startup:**
   ```python
   @app.on_event("startup")
   async def startup_event():
       # ... existing code ...

       # Start Tradier streaming service
       try:
           from .services.tradier_stream import start_tradier_stream
           await start_tradier_stream()
           print("[OK] Tradier streaming initialized", flush=True)
       except Exception as e:
           print(f"[ERROR] Failed to start Tradier stream: {e}", flush=True)
   ```

2. **Update `main.py` shutdown:**
   ```python
   @app.on_event("shutdown")
   async def shutdown_event():
       # ... existing code ...

       # Stop Tradier streaming
       try:
           from .services.tradier_stream import stop_tradier_stream
           await stop_tradier_stream()
           print("[OK] Tradier stream stopped", flush=True)
       except Exception as e:
           print(f"[ERROR] Tradier shutdown error: {e}", flush=True)
   ```

### Testing Checklist:

- [ ] **Unit Tests** (`backend/tests/test_tradier_stream.py`)
  - Test connection initialization
  - Test subscription/unsubscription
  - Test message parsing
  - Test reconnection logic
  - Test error handling

- [ ] **Integration Tests** (`backend/tests/test_streaming_integration.py`)
  - Test full streaming flow (Tradier → Redis → SSE)
  - Test multiple concurrent clients
  - Test subscription management
  - Test disconnection handling

- [ ] **Manual Testing**
  - Start backend with Tradier API keys
  - Check logs for "[OK] Tradier streaming initialized"
  - Test `/api/stream/status` - should show Tradier connected
  - Test `/api/stream/prices?symbols=AAPL,MSFT` - should stream live prices
  - Monitor Redis keys: `redis-cli GET price:AAPL`
  - Check for memory leaks (run for 1 hour, monitor memory)

- [ ] **Load Testing**
  - Simulate 10 concurrent SSE clients
  - Monitor CPU usage (should be < 20%)
  - Monitor memory usage (should be < 500MB)
  - Check latency (price updates should be < 5s)

---

## Phase 5: Frontend Integration (2 hours)

### File: `frontend/hooks/useMarketStream.ts`

**No changes needed!** The frontend SSE hook should work with the updated backend transparently.

**Verification:**
1. Open PositionsTable with active positions
2. Watch for "LIVE" indicator (green badge)
3. Observe prices updating in real-time
4. Check browser console for connection status

---

## Phase 6: Documentation & Deployment (1 hour)

### Documentation Updates:

- [ ] Update `CLAUDE.md`:
  - Confirm Tradier handles ALL market data
  - Document streaming implementation

- [ ] Update `README.md`:
  - Add note about Tradier streaming
  - Update environment variables section

- [ ] Create `TRADIER_STREAMING_GUIDE.md`:
  - Setup instructions for local development
  - Troubleshooting common issues
  - Performance tuning tips

### Deployment:

- [ ] **Render Environment Variables:**
  ```bash
  TRADIER_API_KEY=your_key
  TRADIER_ACCOUNT_ID=your_account_id
  TRADIER_API_BASE_URL=https://api.tradier.com/v1
  REDIS_URL=your_redis_url  # Required for streaming
  ```

- [ ] **Deploy to Render:**
  - Push changes to `main` branch
  - Wait for auto-deploy
  - Monitor logs for streaming initialization

- [ ] **Verify Production:**
  - Test `/api/stream/status` on production
  - Test `/api/stream/prices?symbols=AAPL` on production
  - Monitor Sentry for errors
  - Check Redis usage in Render dashboard

---

## Success Criteria

**MVP Requirements:**
- ✅ Real-time price updates for user's positions
- ✅ < 5 second latency for price updates
- ✅ Auto-reconnection on network issues
- ✅ Multiple concurrent clients supported
- ✅ Memory usage < 500MB
- ✅ CPU usage < 20% (1 core)

**Nice-to-Have:**
- Real-time trade volume
- Bid/ask spread display
- Level 2 order book (if Tradier supports)
- Historical bar streaming (1min, 5min bars)

---

## Known Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Tradier doesn't offer streaming | HIGH | Implement smart polling with Redis caching (1-5s intervals) |
| Rate limits hit during polling | MEDIUM | Add jitter, backoff, monitor usage closely |
| WebSocket connection drops | MEDIUM | Auto-reconnect with exponential backoff |
| Memory leak from abandoned subscriptions | LOW | Implement cleanup on client disconnect, periodic subscription audit |
| Redis unavailable | LOW | Graceful fallback to in-memory cache |

---

## Resources

**Tradier API Documentation:**
- Streaming: https://documentation.tradier.com/brokerage-api/streaming
- Market Data: https://documentation.tradier.com/brokerage-api/markets/get-quotes
- Quotes Endpoint: https://documentation.tradier.com/brokerage-api/markets/get-quotes

**Related Files:**
- `backend/app/services/tradier_stream.py` - Main implementation (placeholder)
- `backend/app/routers/stream.py` - SSE endpoints
- `backend/app/services/cache.py` - Redis caching service
- `frontend/hooks/useMarketStream.ts` - Frontend SSE consumer

**Similar Implementations:**
- Look at deleted `backend/app/services/alpaca_stream.py` for pattern reference (check git history)
- SSE-starlette examples: https://github.com/sysid/sse-starlette

---

## Next Steps

1. Start with Phase 1 (Research) - 2 hours
2. Document findings in this file
3. Get approval on implementation approach
4. Proceed with Phases 2-6

**Estimated Total Time:** 8-12 hours
**Priority:** HIGH
**Blocking:** Phase 5.B.2 (Real-time SSE Updates)

---

**Last Updated:** 2025-10-14
**Status:** ⚠️ NOT YET IMPLEMENTED - Ready for development
