# Bulletproof Streaming Architecture for Options Trading Platforms

The PaiiD Options Trading Platform demands rock-solid reliability where even seconds of stale data can lead to catastrophic trading decisions. This guide provides a production-grade, multi-tier fallback architecture with complete implementation details, cost analysis, and operational procedures to achieve 99.99% uptime.

## Architecture overview: Four tiers of resilience

**The core principle**: Never trust a single point of failure. Options trading moves at breakneck speed—implied volatility shifts in seconds, Greeks recalculate constantly, and spreads widen with the slightest hesitation. Your streaming architecture must anticipate and gracefully handle every failure mode.

The recommended architecture implements **four distinct tiers** with automatic failover between each level. Tier 1 provides real-time WebSocket streaming from Tradier with sub-second latency. When Tier 1 falters, Tier 2 activates immediately with Polygon.io's real-time WebSocket feed—maintaining full trading capabilities with imperceptible interruption. If both WebSocket sources fail, Tier 3 engages REST polling against Alpha Vantage at 5-10 second intervals, showing clear staleness warnings but keeping critical data flowing. Finally, Tier 4 serves cached data with prominent "TRADING DISABLED" overlays, allowing position monitoring while preventing dangerous trades on outdated information.

This cascading approach ensures traders always see the freshest data available while the system transparently attempts recovery. The architecture tracks connection health continuously using heartbeat mechanisms, monitors message rates for zombie connection detection, and implements circuit breakers to prevent cascading failures. Each tier transition happens automatically within 1-5 seconds, and the system always attempts to climb back to Tier 1 when connectivity restores.

## Tier 1: Primary WebSocket streaming (Tradier API)

Your existing Tradier WebSocket connection forms the foundation—real-time options chains, Greeks, quotes, and trades with minimal latency. **Target metrics**: 99.99% uptime, \<50ms message latency, automatic reconnection within 2 seconds of disconnection.

### Connection health monitoring implementation

WebSocket connections can fail silently—appearing connected while data stops flowing (zombie connections). Implement aggressive health monitoring using three complementary approaches:

**Heartbeat mechanism** sends ping frames every 30 seconds, expecting pong responses within 10 seconds. After three consecutive missed pongs (90 seconds total), force disconnect and trigger Tier 2 failover. This catches network issues that don't cleanly close the connection.

**Message rate monitoring** tracks updates per second for each symbol. Options data during market hours should arrive at 5-50 messages per second depending on volatility. If message rate drops below 10% of the 5-minute moving average for more than 15 seconds, assume stale connection and reconnect.

**Gap detection** monitors sequence numbers in market data streams. Missing sequence numbers indicate dropped messages—acceptable in small quantities (1-2%) but should trigger reconnection if gap rate exceeds 5% over 30 seconds.

### Python/FastAPI implementation with state machine

```python
import asyncio
import websockets
from enum import Enum
from datetime import datetime, timedelta
import json

class ConnectionState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    CLOSING = "closing"
    FAILED = "failed"

class TradierWebSocketClient:
    def __init__(self, api_token, on_message_callback, on_state_change):
        self.api_token = api_token
        self.on_message = on_message_callback
        self.on_state_change = on_state_change
        self.state = ConnectionState.DISCONNECTED
        self.ws = None
        self.last_message_time = None
        self.last_pong_time = None
        self.message_count = 0
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10

    async def connect(self):
        """Establish WebSocket connection with exponential backoff"""
        self._set_state(ConnectionState.CONNECTING)

        while self.reconnect_attempts < self.max_reconnect_attempts:
            try:
                self.ws = await asyncio.wait_for(
                    websockets.connect(
                        "wss://ws.tradier.com/v1/markets/events",
                        extra_headers={"Authorization": f"Bearer {self.api_token}"}
                    ),
                    timeout=10.0
                )

                self._set_state(ConnectionState.CONNECTED)
                self.reconnect_attempts = 0
                self.last_message_time = datetime.now()
                self.last_pong_time = datetime.now()

                # Start parallel tasks
                await asyncio.gather(
                    self._receive_messages(),
                    self._heartbeat_loop(),
                    self._health_monitor()
                )

            except (asyncio.TimeoutError, websockets.exceptions.WebSocketException) as e:
                self.reconnect_attempts += 1
                backoff = min(2 ** self.reconnect_attempts, 60)  # Cap at 60 seconds
                jitter = backoff * 0.1 * (0.5 + 0.5 * hash(str(datetime.now())) % 100 / 100)
                wait_time = backoff + jitter

                print(f"Connection failed (attempt {self.reconnect_attempts}): {e}. Retry in {wait_time:.1f}s")
                self._set_state(ConnectionState.RECONNECTING)
                await asyncio.sleep(wait_time)

        self._set_state(ConnectionState.FAILED)
        # Trigger Tier 2 failover
        await self._trigger_failover()

    async def _receive_messages(self):
        """Main message receiving loop"""
        try:
            async for message in self.ws:
                self.last_message_time = datetime.now()
                self.message_count += 1

                data = json.loads(message)
                await self.on_message(data)

        except websockets.exceptions.ConnectionClosed:
            print("WebSocket connection closed")
            self._set_state(ConnectionState.DISCONNECTED)
            asyncio.create_task(self.connect())

    async def _heartbeat_loop(self):
        """Send ping every 30 seconds, track pong responses"""
        while self.state == ConnectionState.CONNECTED:
            try:
                await self.ws.ping()
                await asyncio.sleep(30)

                # Check if we received pong in last 45 seconds
                if datetime.now() - self.last_pong_time > timedelta(seconds=45):
                    print("No pong received, assuming zombie connection")
                    await self.ws.close()
                    self._set_state(ConnectionState.DISCONNECTED)
                    asyncio.create_task(self.connect())
                    break

            except Exception as e:
                print(f"Heartbeat error: {e}")
                break

    async def _health_monitor(self):
        """Monitor message rates and detect stalled connections"""
        message_rate_window = []

        while self.state == ConnectionState.CONNECTED:
            await asyncio.sleep(5)

            # Calculate messages per second
            current_count = self.message_count
            message_rate_window.append(current_count)
            if len(message_rate_window) > 12:  # 60 second window
                message_rate_window.pop(0)

            # Check if current rate dropped significantly
            if len(message_rate_window) >= 6:
                avg_rate = sum(message_rate_window[:-1]) / len(message_rate_window[:-1])
                current_rate = message_rate_window[-1]

                if current_rate < avg_rate * 0.1 and avg_rate > 5:  # 90% drop
                    print(f"Message rate dropped significantly: {current_rate} vs avg {avg_rate}")
                    await self.ws.close()
                    self._set_state(ConnectionState.DISCONNECTED)
                    asyncio.create_task(self.connect())
                    break

            # Check for complete stall
            if datetime.now() - self.last_message_time > timedelta(seconds=30):
                print("No messages received for 30 seconds, reconnecting")
                await self.ws.close()
                self._set_state(ConnectionState.DISCONNECTED)
                asyncio.create_task(self.connect())
                break

    def _set_state(self, new_state):
        """Update state and trigger callbacks"""
        old_state = self.state
        self.state = new_state
        self.on_state_change(old_state, new_state)

    async def _trigger_failover(self):
        """Activate Tier 2 backup"""
        print("Tier 1 failed, activating Tier 2 (Polygon.io)")
        # Implement Tier 2 activation logic
```

### Circuit breaker pattern

Implement circuit breakers to prevent overwhelming a failing service with connection attempts. The circuit has three states: **Closed** (normal operation, all requests pass through), **Open** (service assumed down, requests fail immediately for 30 seconds), and **Half-Open** (testing recovery with limited requests).

```python
from datetime import datetime, timedelta
import asyncio

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout_seconds=30, recovery_threshold=3):
        self.failure_threshold = failure_threshold
        self.timeout = timedelta(seconds=timeout_seconds)
        self.recovery_threshold = recovery_threshold

        self.failures = 0
        self.successes = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == "OPEN":
            if datetime.now() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
                self.successes = 0
            else:
                raise Exception("Circuit breaker OPEN - service unavailable")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result

        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        self.failures = 0

        if self.state == "HALF_OPEN":
            self.successes += 1
            if self.successes >= self.recovery_threshold:
                self.state = "CLOSED"
                print("Circuit breaker CLOSED - service recovered")

    def _on_failure(self):
        self.failures += 1
        self.last_failure_time = datetime.now()

        if self.failures >= self.failure_threshold:
            self.state = "OPEN"
            print(f"Circuit breaker OPEN - {self.failures} failures detected")
```

**Usage with Tradier connection**: Wrap connection attempts in circuit breaker to avoid hammering a dead endpoint for minutes. After 5 consecutive failures, stop attempting for 30 seconds and immediately activate Tier 2 failover.

## Tier 2: Backup WebSocket (Polygon.io Advanced)

When Tradier fails, instantly pivot to Polygon.io's real-time WebSocket feed. **Cost**: $199/month for Advanced plan with real-time data, unlimited API calls, and full options support including Greeks. This tier maintains production-quality trading capabilities with negligible interruption.

### Why Polygon.io for Tier 2

**Best-in-class infrastructure**: Co-located with OPRA data center for minimal latency (\<20ms). Processes 3TB of options data daily with direct fiber connections to exchanges. The platform handles 300,000 messages per second for options quotes—sufficient for any retail trading volume.

**Complete options support**: Full US options market coverage from OPRA feed with Delta, Gamma, Theta, Vega calculations (market hours only). Access entire options chains for all US equities with 5+ years of historical tick data. Open interest and implied volatility included.

**WebSocket streaming**: One WebSocket connection per subscription handles unlimited symbols. Real-time trades and quotes stream continuously. Average latency \<20ms makes this suitable as primary production feed, not just backup.

### Polygon.io WebSocket implementation

```python
import asyncio
import websockets
import json

class PolygonWebSocketClient:
    def __init__(self, api_key, symbols, on_message_callback):
        self.api_key = api_key
        self.symbols = symbols  # e.g., ["O:SPY250117C00575000"]
        self.on_message = on_message_callback
        self.ws = None

    async def connect(self):
        """Connect to Polygon.io WebSocket with authentication"""
        uri = "wss://socket.polygon.io/options"

        try:
            self.ws = await websockets.connect(uri)

            # Authenticate
            auth_message = {"action": "auth", "params": self.api_key}
            await self.ws.send(json.dumps(auth_message))

            # Subscribe to symbols
            subscribe_message = {
                "action": "subscribe",
                "params": ",".join(self.symbols)
            }
            await self.ws.send(json.dumps(subscribe_message))

            print(f"Polygon.io connected, subscribed to {len(self.symbols)} symbols")

            # Receive messages
            async for message in self.ws:
                data = json.loads(message)

                if data[0]["ev"] == "status":
                    print(f"Polygon status: {data[0]['message']}")
                else:
                    await self.on_message(data)

        except Exception as e:
            print(f"Polygon.io connection error: {e}")
            # Trigger Tier 3 failover (REST polling)
            await self._trigger_tier3()

    async def _trigger_tier3(self):
        """Activate Tier 3 REST polling fallback"""
        print("Tier 2 failed, activating Tier 3 (REST polling)")
```

### Automatic failover logic

The system should seamlessly transition between Tradier and Polygon.io without user intervention or data interruption. When Tier 1 circuit breaker opens, immediately establish Tier 2 connection while continuing reconnection attempts to Tier 1 in the background.

**Failover sequence**: Detect Tier 1 failure (3 missed heartbeats or 30s message stall) → Open circuit breaker → Start Tier 2 connection (target \<2s) → Display subtle status change ("Backup feed active") → Continue serving data with \<1s interruption → Attempt Tier 1 reconnection every 60 seconds → When Tier 1 recovers, validate health for 30 seconds → Gracefully transition back to Tier 1.

The key is **maintaining data continuity** during transitions. Buffer the last 60 seconds of messages in memory to detect gaps. When switching feeds, compare timestamps and sequence numbers to ensure no missing data. If gaps detected, fetch missing data via REST API to backfill.

## Tier 3: REST polling fallback (Alpha Vantage + Polygon.io delayed)

When both WebSocket sources fail—perhaps a network partition affecting your infrastructure—fall back to REST polling. This tier trades latency for reliability, fetching market data every 5-10 seconds via synchronous HTTP requests.

### Polling strategy and rate limit management

**Optimal polling interval for options**: 5 seconds during high volatility (earnings, market open/close), 10 seconds during normal conditions, 30 seconds after-hours. More frequent polling wastes rate limits while providing minimal value—options chains don't change significantly in sub-5-second windows for most retail strategies.

**Rate limit budget management**: Track API calls per minute/day across all tiers. If approaching limits, increase polling intervals exponentially (10s → 20s → 30s → 60s). Prioritize symbols actively in positions or with open orders. Pause polling for symbols merely being watched when rate limits constrain.

### Implementation with httpx and caching

```python
import httpx
from datetime import datetime, timedelta
import asyncio
from typing import Dict, Any
import hashlib

class RESTPollingFallback:
    def __init__(self, polygon_api_key, alpha_vantage_key):
        self.polygon_key = polygon_api_key
        self.alpha_key = alpha_vantage_key
        self.client = httpx.AsyncClient(timeout=10.0, limits=httpx.Limits(max_connections=20))
        self.cache: Dict[str, tuple[datetime, Any]] = {}
        self.cache_ttl = timedelta(seconds=10)
        self.poll_interval = 5  # seconds
        self.symbols = []

    async def start_polling(self, symbols):
        """Begin polling loop for given symbols"""
        self.symbols = symbols

        while True:
            tasks = [self._fetch_symbol(symbol) for symbol in symbols]
            await asyncio.gather(*tasks, return_exceptions=True)
            await asyncio.sleep(self.poll_interval)

    async def _fetch_symbol(self, symbol):
        """Fetch single symbol with caching and rate limiting"""
        cache_key = f"options_chain:{symbol}"

        # Check cache first
        if cache_key in self.cache:
            cached_time, cached_data = self.cache[cache_key]
            if datetime.now() - cached_time < self.cache_ttl:
                return cached_data

        # Try Polygon.io first (delayed data on lower tiers)
        try:
            response = await self.client.get(
                f"https://api.polygon.io/v3/snapshot/options/{symbol}",
                params={"apiKey": self.polygon_key}
            )

            if response.status_code == 200:
                data = response.json()
                self.cache[cache_key] = (datetime.now(), data)
                return data
            elif response.status_code == 429:  # Rate limited
                print(f"Polygon rate limited, increasing poll interval")
                self.poll_interval = min(self.poll_interval * 2, 60)

        except httpx.TimeoutException:
            print(f"Polygon timeout for {symbol}")

        # Fallback to Alpha Vantage
        try:
            response = await self.client.get(
                f"https://www.alphavantage.co/query",
                params={
                    "function": "REALTIME_OPTIONS",
                    "symbol": symbol.split(":")[1][:3],  # Extract ticker from O:SPY...
                    "apikey": self.alpha_key
                }
            )

            if response.status_code == 200:
                data = response.json()
                self.cache[cache_key] = (datetime.now(), data)
                return data

        except Exception as e:
            print(f"Alpha Vantage error: {e}")

        # Both failed, serve stale cache if available
        if cache_key in self.cache:
            cached_time, cached_data = self.cache[cache_key]
            print(f"Serving stale cache ({(datetime.now() - cached_time).seconds}s old)")
            return cached_data

        return None
```

### Exponential backoff for failed requests

When REST requests fail, implement intelligent retry logic with exponential backoff and jitter to avoid retry storms.

```python
import asyncio
import random

async def fetch_with_retry(func, max_retries=5):
    """Execute async function with exponential backoff"""
    base_delay = 1
    max_delay = 60

    for attempt in range(max_retries):
        try:
            return await func()

        except Exception as e:
            if attempt == max_retries - 1:
                raise e

            delay = min(base_delay * (2 ** attempt), max_delay)
            jitter = delay * 0.25 * random.random()
            wait_time = delay + jitter

            print(f"Request failed (attempt {attempt + 1}/{max_retries}), retry in {wait_time:.1f}s")
            await asyncio.sleep(wait_time)
```

**Usage**: `data = await fetch_with_retry(lambda: client.get(url))`. This pattern prevents overwhelming recovering services and distributes retry attempts across time to avoid thundering herd problems.

### Transitioning back to WebSocket

Continuously attempt WebSocket reconnection while polling REST. Every 60 seconds, try establishing WebSocket connection with short timeout (5s). If successful, run health validation for 30 seconds—verify message rates are normal, heartbeats work, no gaps in data. Only after validation passes, transition from polling back to WebSocket.

**Graceful transition**: Don't immediately stop polling when WebSocket connects. Run both in parallel for 30 seconds to verify consistency. Compare data from both sources—if timestamps and values match within acceptable tolerance, safely disable polling and rely on WebSocket.

## Tier 4: Cached data with trading disabled

The final safety net serves last-known-good cached data when all live sources fail. This tier prevents complete application failure while protecting users from trading on dangerously stale information.

### Cache architecture with Redis

**Two-tier caching**: Level 1 in-memory Python dict for ultra-fast access (\<1ms lookup), Level 2 in Redis for persistence and cross-instance sharing. Store last 5 minutes of market data per symbol with microsecond timestamps.

```python
import redis
import json
from datetime import datetime, timedelta
import pickle

class MarketDataCache:
    def __init__(self, redis_host='localhost', redis_port=6379):
        self.memory_cache = {}  # symbol -> (timestamp, data)
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=False)
        self.max_age = timedelta(minutes=5)

    def set(self, symbol: str, data: dict):
        """Store data in both cache levels"""
        timestamp = datetime.now()

        # Level 1: Memory cache
        self.memory_cache[symbol] = (timestamp, data)

        # Level 2: Redis with expiration
        cache_key = f"market_data:{symbol}"
        cache_value = pickle.dumps((timestamp, data))
        self.redis_client.setex(cache_key, 300, cache_value)  # 5 minute TTL

    def get(self, symbol: str) -> tuple[datetime, dict, bool]:
        """
        Retrieve cached data, returns (timestamp, data, is_stale)
        is_stale=True if data older than max_age
        """
        # Try memory cache first
        if symbol in self.memory_cache:
            timestamp, data = self.memory_cache[symbol]
            age = datetime.now() - timestamp
            return timestamp, data, age > self.max_age

        # Fallback to Redis
        cache_key = f"market_data:{symbol}"
        cached = self.redis_client.get(cache_key)

        if cached:
            timestamp, data = pickle.loads(cached)
            age = datetime.now() - timestamp

            # Populate memory cache for next access
            self.memory_cache[symbol] = (timestamp, data)

            return timestamp, data, age > self.max_age

        return None, None, True

    def get_staleness_level(self, timestamp: datetime) -> str:
        """Classify data staleness"""
        age = (datetime.now() - timestamp).total_seconds()

        if age < 5:
            return "LIVE"
        elif age < 15:
            return "DELAYED"
        elif age < 30:
            return "STALE"
        elif age < 300:
            return "VERY_STALE"
        else:
            return "CRITICAL"
```

### Trading restrictions by staleness

Automatically disable trading features when data becomes dangerously stale. This prevents users from executing trades on information that no longer reflects reality.

**Staleness thresholds**:
- **0-5 seconds (GREEN)**: All trading permitted, no warnings
- **5-15 seconds (YELLOW)**: Show warning modal for market orders—"Data is X seconds old. Continue?"
- **15-30 seconds (ORANGE)**: Disable market orders entirely, allow limit orders only with confirmation
- **30-60 seconds (RED)**: Disable all new orders, allow cancellations only
- **60+ seconds (CRITICAL)**: Complete lockout, display "STALE DATA - DO NOT TRADE"

```python
from enum import Enum

class TradingMode(Enum):
    FULL = "full"
    LIMITED = "limited"
    CANCEL_ONLY = "cancel_only"
    DISABLED = "disabled"

def get_trading_mode(staleness_seconds: float) -> TradingMode:
    """Determine allowed trading actions based on data age"""
    if staleness_seconds < 15:
        return TradingMode.FULL
    elif staleness_seconds < 30:
        return TradingMode.LIMITED  # Limit orders only
    elif staleness_seconds < 60:
        return TradingMode.CANCEL_ONLY
    else:
        return TradingMode.DISABLED
```

### UI indicators for stale data

Display data freshness prominently using color-coded badges and timestamps. **Never allow trading to proceed on stale data without explicit, aggressive warnings**.

**Visual indicators**:
- **Green pill badge**: "● LIVE" with pulsing green dot animation
- **Yellow badge**: "⚠ DELAYED 8s" with static warning icon
- **Orange badge**: "⚠ STALE 25s ago" with timestamp
- **Red banner**: Full-width banner "🚫 CONNECTION LOST - Last update 2:45:30 PM ET (3 minutes ago) - TRADING DISABLED"

**Timestamp formats**:
- \<60 seconds: Relative time ("Updated 8s ago")
- 1-5 minutes: Relative with absolute ("Updated 2m ago • 2:45 PM ET")
- \>5 minutes: Absolute only ("Last update: 2:45:30 PM ET")

**Accessibility**: Never use color alone—include icons (✓, ⚠, ✕) and text labels for color-blind users (6-8% of males). Use distinct visual patterns beyond just hue changes.

## Complete implementation checklist

**Phase 1 - Foundation (Week 1-2)**:
- [ ] Implement Tier 1 WebSocket with state machine (disconnected, connecting, connected, reconnecting, failed)
- [ ] Add heartbeat mechanism (30s ping interval, 3 missed pongs trigger reconnect)
- [ ] Implement message rate monitoring (track msgs/sec, alert on 90% drop)
- [ ] Add gap detection for sequence numbers
- [ ] Set up circuit breaker for Tier 1 (5 failures open circuit for 30s)
- [ ] Create unified data model to abstract different API responses
- [ ] Implement in-memory caching for all market data
- [ ] Add connection state callbacks for UI updates

**Phase 2 - Tier 2 Backup (Week 3)**:
- [ ] Sign up for Polygon.io Advanced ($199/month)
- [ ] Implement Polygon WebSocket client with authentication
- [ ] Add automatic failover when Tier 1 circuit opens
- [ ] Test manual failover (disconnect Tier 1, verify Tier 2 activates \<2s)
- [ ] Implement data continuity checks (detect gaps during transition)
- [ ] Add background Tier 1 reconnection attempts (every 60s)
- [ ] Validate data consistency between Tier 1 and Tier 2

**Phase 3 - REST Polling (Week 4)**:
- [ ] Implement REST polling with httpx AsyncClient
- [ ] Add rate limit tracking and adaptive polling intervals
- [ ] Configure exponential backoff for failed requests (1s, 2s, 4s... max 60s)
- [ ] Add jitter to prevent thundering herd (10-25% of backoff delay)
- [ ] Implement connection pooling (max 20 concurrent connections)
- [ ] Set timeouts (10s request timeout, 5s connection timeout)
- [ ] Add fallback between Polygon REST and Alpha Vantage REST

**Phase 4 - Caching & Staleness (Week 5)**:
- [ ] Set up Redis instance (AWS ElastiCache or self-hosted)
- [ ] Implement two-tier caching (memory + Redis)
- [ ] Add staleness classification (LIVE, DELAYED, STALE, VERY_STALE, CRITICAL)
- [ ] Create trading mode restrictions based on staleness
- [ ] Implement cache TTL (5 minutes for market data)
- [ ] Add cache warming on startup (fetch recent data immediately)

This reference document covers the full streaming architecture. **For Phase 1 implementation, focus on the Tradier-specific code in TRADIER_IMPLEMENTATION.md**.
