# Data Flow Architecture - PaiiD Application

**MOD-2C Audit Report**
**Date:** 2025-10-27
**Auditor:** MOD-2C (MOD SQUAD Batch 2)

---

## Executive Summary

This document maps the complete data flow architecture of the PaiiD (Personal Artificial Intelligence Investment Dashboard) application. It documents all context providers, localStorage usage, API caching strategies, state management patterns, and identifies potential bottlenecks and security concerns.

### Key Findings

- **5 Context Providers** managing global state
- **598 useState** calls across 99 files
- **221 useEffect** calls across 82 files
- **70 useMemo/useCallback** optimizations across 21 files
- **Custom SWR-based caching** with 10 specialized hooks
- **EventSource (SSE)** for real-time market data streaming
- **WebSocket** support for portfolio updates (underutilized)
- **25+ localStorage keys** storing user data and preferences
- **Security Issue:** JWT tokens stored in unencrypted localStorage

---

## Context Providers (Global State Management)

### 1. AuthContext (`frontend/contexts/AuthContext.tsx`)

**Purpose:** Manages user authentication state, JWT tokens, and session lifecycle.

**State Managed:**
- `user: UserProfile | null` - Current authenticated user
- `isAuthenticated: boolean` - Authentication status
- `isLoading: boolean` - Initial session load state

**Key Features:**
- Automatic token refresh every 10 minutes (15-minute expiration)
- Stores tokens in localStorage (`paiid_tokens`)
- Session persistence across page reloads
- Automatic logout on token expiration

**Data Flow:**
```
Login/Register → Backend API → JWT Tokens → localStorage
                                              ↓
                                    AuthContext.user (state)
                                              ↓
                              All protected components via useAuth()
```

**Token Refresh Logic:**
```
Access Token Expiry: 15 minutes
Refresh Interval: 10 minutes (5-minute buffer)
Refresh Token Storage: localStorage (SECURITY RISK - see below)
```

**Security Concerns:**
- ⚠️ **CRITICAL:** JWT tokens stored in unencrypted localStorage
- Vulnerable to XSS attacks (any script can access tokens)
- No token encryption at rest
- Recommendation: Migrate to httpOnly cookies or use SecureStorage wrapper

---

### 2. WorkflowContext (`frontend/contexts/WorkflowContext.tsx`)

**Purpose:** Manages workflow navigation and data passing between 10 workflow stages.

**State Managed:**
- `currentWorkflow: WorkflowType | null` - Active workflow
- `pendingNavigation: WorkflowNavigationData | null` - Navigation intent with data payload

**Workflow Types:**
- morning-routine
- active-positions
- execute-trade
- research
- ai-recommendations
- analytics
- news-review
- strategy-builder
- backtesting
- settings

**Data Flow:**
```
Component A (AI Analysis) → navigateToTrade({ symbol, entryPrice, stopLoss })
                                              ↓
                             WorkflowContext.pendingNavigation
                                              ↓
                          Component B (Execute Trade) consumes data
                                              ↓
                          clearPendingNavigation() after consumption
```

**Cross-Workflow Data Passing:**
```typescript
// Example: AI Recommendations → Execute Trade
navigateToTrade({
  symbol: "AAPL",
  side: "buy",
  quantity: 10,
  entryPrice: 150.00,
  stopLoss: 145.00,
  takeProfit: 160.00
});
```

**Event-Driven Architecture:**
- Dispatches `workflow-navigate` custom event on window
- Allows non-React components to listen for workflow changes

---

### 3. ThemeContext (`frontend/contexts/ThemeContext.tsx`)

**Purpose:** Manages dark/light theme toggle with localStorage persistence.

**State Managed:**
- `theme: 'dark' | 'light'` - Current theme
- `colors: ThemeColors` - Computed color palette

**Persistence:**
- localStorage key: `paiid-theme`
- Falls back to system preference: `prefers-color-scheme`

**Data Flow:**
```
User toggles theme → setTheme() → localStorage.setItem('paiid-theme')
                                              ↓
                             document.documentElement.classList (CSS variables)
                                              ↓
                        meta[name="theme-color"] (mobile browser chrome)
```

**Theme Colors:**
- Dark: Background #0f172a, Primary #10b981
- Light: Background #ffffff, Primary #10b981
- Glassmorphism: `backdrop-filter: blur(10px)`

---

### 4. GlowStyleContext (`frontend/contexts/GlowStyleContext.tsx`)

**Purpose:** Manages logo glow effect style (radial vs halo).

**State Managed:**
- `glowStyle: 'radial' | 'halo'` - Active glow effect

**Configuration:**
- URL parameter: `?glow=halo` switches to halo mode
- Default: radial glow (green animated)

**Data Flow:**
```
URL Query Param (?glow=halo) → useEffect → setGlowStyle('halo')
                                                  ↓
                                      Logo component consumes
```

**Note:** Lightweight context with minimal re-renders.

---

### 5. ChatContext (`frontend/components/ChatContext.tsx`)

**Purpose:** Controls AI chat interface open/close state.

**State Managed:**
- `isChatOpen: boolean` - Chat visibility

**Data Flow:**
```
User clicks chat button → openChat() → isChatOpen = true
                                              ↓
                          AIChatBot renders with isOpen prop
```

**Integration Points:**
- StatusBar toggle button
- Floating chat icon
- Keyboard shortcut (potential)

---

## localStorage Usage Inventory

### Authentication & Session Management

| Key | Purpose | Data Type | Security Risk |
|-----|---------|-----------|--------------|
| `paiid_tokens` | JWT access + refresh tokens | `{ accessToken, refreshToken, expiresAt }` | 🔴 HIGH - Plaintext tokens |
| `user-id` | Auto-generated user ID | string | 🟡 MEDIUM - Can be used for tracking |
| `user-role` | User role (owner/beta/alpha/user) | string | 🟢 LOW |

### User Preferences & Onboarding

| Key | Purpose | Data Type | Security Risk |
|-----|---------|-----------|--------------|
| `user-setup-complete` | Onboarding completion flag | "true" | 🟢 LOW |
| `admin-bypass` | Dev bypass flag | "true" | 🟡 MEDIUM - Should be removed in prod |
| `bypass-timestamp` | Bypass timestamp | ISO string | 🟢 LOW |
| `manual-skip` | Manual onboarding skip | "true" | 🟢 LOW |

### Theme & UI State

| Key | Purpose | Data Type | Security Risk |
|-----|---------|-----------|--------------|
| `paiid-theme` | Dark/light theme | "dark" \| "light" | 🟢 LOW |

### Trading & Market Data

| Key | Purpose | Data Type | Security Risk |
|-----|---------|-----------|--------------|
| `paiid-market-data` | Cached market indices | `{ data: MarketDataState, timestamp }` | 🟢 LOW |
| `orderHistory` | Order execution history | Order[] | 🟡 MEDIUM - Contains trade data |
| `paiid_trading_journal` | Manual journal entries | JournalEntry[] | 🟢 LOW |
| `trading-mode` | Paper vs live mode | "paper" \| "live" | 🟢 LOW |

### Strategy & AI Data

| Key | Purpose | Data Type | Security Risk |
|-----|---------|-----------|--------------|
| `ai_trader_strategies` | Saved AI strategies | Strategy[] | 🟢 LOW |
| `allessandra_settings` | Settings config | Settings object | 🟡 MEDIUM - May contain API keys |

### User Profile & Management

| Key | Purpose | Data Type | Security Risk |
|-----|---------|-----------|--------------|
| `paid_user_profile` | User profile data | UserProfile | 🟡 MEDIUM - PII concerns |
| `paiid_user_data` | User management data | User object | 🟡 MEDIUM - PII concerns |

### Trade History & Performance

| Key | Purpose | Data Type | Security Risk |
|-----|---------|-----------|--------------|
| `paiid_trade_history` | Historical trades | Trade[] | 🟡 MEDIUM - Financial data |
| `paiid_performance_cache` | Performance metrics cache | PerformanceMetrics | 🟢 LOW |

### Telemetry & Analytics

| Key | Purpose | Data Type | Security Risk |
|-----|---------|-----------|--------------|
| `userId` | Telemetry user ID | string | 🟢 LOW |
| `userRole` | Telemetry role | string | 🟢 LOW |

### Secure Storage (Encrypted)

| Key Prefix | Purpose | Security Status |
|-----------|---------|----------------|
| `paiid_secure_*` | AES-GCM encrypted data | 🟢 SECURE - Web Crypto API |

**Secure Storage Implementation:**
- AES-GCM 256-bit encryption
- Initialization vectors stored per-item
- Session-based keys (regenerated per session)
- Key material in sessionStorage (cleared on tab close)

---

## API Caching Architecture

### SWR (Stale-While-Revalidate) Strategy

**Implementation:** `frontend/hooks/useSWR.ts`

**Global Configuration:**
```typescript
{
  dedupingInterval: 2000,        // Dedupe requests within 2 seconds
  revalidateOnFocus: true,       // Refresh when tab gains focus
  revalidateOnReconnect: true,   // Refresh on network reconnect
  shouldRetryOnError: false,     // No automatic retries
  errorRetryCount: 0             // Let error boundaries handle
}
```

### SWR Hooks & Refresh Intervals

| Hook | Endpoint | Refresh Interval | Use Case |
|------|----------|-----------------|----------|
| `usePositions()` | `/api/positions` | 5s | Real-time position tracking |
| `useAccount()` | `/api/account` | 10s | Account balance updates |
| `useMarketData()` | `/api/market/indices` | 10s | Market indices (SPY, QQQ) |
| `useQuote(symbol)` | `/api/quotes/{symbol}` | 10s | Individual stock quotes |
| `useNews(category)` | `/api/news/market` | 5min | Market news feed |
| `useCompanyNews(symbol)` | `/api/news/company/{symbol}` | 5min | Company-specific news |
| `useStrategyTemplates()` | `/api/strategies/templates` | On focus | Strategy templates |
| `useUserPreferences()` | `/api/users/preferences` | On focus | User settings |
| `useAnalytics(timeframe)` | `/api/analytics` | 30s | P&L analytics |
| `useOrderHistory()` | `/api/orders/history` | 15s | Order execution history |

**Benefits:**
- 70% reduction in API calls (estimated)
- Instant perceived load times (serve stale data)
- Automatic background revalidation
- Shared cache across components

---

## Custom Polling & Auto-Refresh Patterns

### Component-Level Polling

**Pattern:** `setInterval` within `useEffect`

| Component | Data Source | Interval | Purpose |
|-----------|------------|----------|---------|
| `AIRecommendations` | `/api/ai/recommendations` | 5min | AI trade recommendations |
| `SentimentDashboard` | `/api/sentiment` | 5min | Market sentiment analysis |
| `PerformanceDashboard` | `/api/metrics` | 30s | Admin performance metrics |
| `ApprovalQueue` | `/api/trades/pending` | 10s | Trade approval queue |
| `GitHubActionsMonitor` | GitHub API | 30s | CI/CD workflow status |
| `MonitorDashboard` | `/api/monitor` | 30s | System health monitoring |
| `NewsReview` | `/api/news` | 5min | News feed updates |
| `StatusBar` | `/api/health` | 30s | Backend health checks |
| `PLComparisonChart` | Live position data | 10s | P&L comparison (live mode) |
| `WatchlistPanel` | `/api/quotes` | Configurable | Watchlist quote updates |

**Common Pattern:**
```typescript
useEffect(() => {
  if (autoRefresh) {
    const interval = setInterval(fetchData, refreshInterval);
    return () => clearInterval(interval);
  }
}, [autoRefresh, refreshInterval]);
```

---

## Real-Time Data Streaming

### EventSource (Server-Sent Events)

**Implementation:** `frontend/hooks/useMarketData.ts`

**Endpoint:** `/api/proxy/stream/market-indices`

**Features:**
- Exponential backoff retry (2s → 128s max)
- Max 10 retry attempts
- Automatic reconnection on disconnect
- Heartbeat monitoring

**Data Flow:**
```
Backend SSE Stream → EventSource → indices_update event
                                              ↓
                              Throttled setState (max 10s interval)
                                              ↓
                     localStorage cache (immediate, not throttled)
                                              ↓
                            RadialMenu logo display (SPY/QQQ)
```

**Retry Logic:**
```typescript
// Exponential backoff: 2s, 4s, 8s, 16s, 32s, 64s, 128s
const delay = Math.min(baseDelay * Math.pow(2, retryAttempt), 128000);
```

**Force Field Confidence Calculation:**
```typescript
const confidence =
  dataFreshness * 0.4 +        // 40% - How recent is the data
  stabilityScore * 0.4 +        // 40% - Market volatility (lower = higher confidence)
  connectionScore * 0.2;        // 20% - Connection quality (retry count)
```

---

### WebSocket (Underutilized)

**Implementation:** `frontend/hooks/useWebSocket.ts`

**Endpoint:** `ws://localhost:8001/ws?user_id={userId}`

**Message Types Supported:**
- `market_data` - Real-time stock quotes
- `portfolio_update` - Portfolio value changes
- `position_update` - Individual position updates
- `trading_alert` - Price/volume/news alerts
- `subscription_confirmed` - Symbol subscription acknowledgment

**Current Usage:**
- Implemented but NOT actively used in production components
- `AIRecommendations`, `AIChatInterface`, `SentimentDashboard` have WebSocket integration hooks
- Most components use REST API polling instead

**Opportunity:**
- Replace polling with WebSocket push for:
  - Active positions updates
  - Portfolio P&L real-time tracking
  - Trade execution notifications

**Data Flow (If Enabled):**
```
Backend WebSocket → ws.onmessage → handleMessage() → setState()
                                              ↓
                              marketData Map (by symbol)
                              portfolioUpdate (total value)
                              positionUpdates Map (by symbol)
                              tradingAlerts Array (last 50)
```

---

## State Management Analysis

### useState Distribution

**Total:** 598 occurrences across 99 files

**Heavily Stateful Components (10+ useState calls):**
- `Analytics.tsx` - 14 state variables (chart data, filters, date ranges)
- `ExecuteTradeForm.tsx` - 29 state variables (form fields, validation, order types)
- `MorningRoutineAI.tsx` - 21 state variables (AI checklist, market data)
- `NewsReview.tsx` - 19 state variables (news feed, filters, sentiment)
- `Settings.tsx` - 18 state variables (all user preferences)
- `StrategyBuilderAI.tsx` - 15 state variables (strategy wizard, AI suggestions)
- `trading/ResearchDashboard.tsx` - 19 state variables (research tools, data)

**Potential Optimization:**
- Group related state into single objects (e.g., `formState`, `filterState`)
- Use `useReducer` for complex state logic (especially ExecuteTradeForm)
- Extract form state to custom hooks

---

### useEffect Distribution

**Total:** 221 occurrences across 82 files

**Effect-Heavy Components (4+ useEffect calls):**
- `ActivePositions.tsx` - 4 effects (polling, SSE, cleanup)
- `AIAnalysisModal.tsx` - 4 effects (fetch, subscription, modal lifecycle)
- `useWebSocket.ts` - 4 effects (connect, reconnect, heartbeat, cleanup)
- `RadialMenu.ORIGINAL.tsx` - 6 effects (D3 rendering, market data, resize)

**Common Effect Patterns:**
1. **Data Fetching on Mount:**
   ```typescript
   useEffect(() => { fetchData(); }, []);
   ```

2. **Polling with Cleanup:**
   ```typescript
   useEffect(() => {
     const interval = setInterval(fetchData, 5000);
     return () => clearInterval(interval);
   }, []);
   ```

3. **Event Listeners:**
   ```typescript
   useEffect(() => {
     window.addEventListener('resize', handleResize);
     return () => window.removeEventListener('resize', handleResize);
   }, []);
   ```

4. **WebSocket/SSE Connections:**
   ```typescript
   useEffect(() => {
     const ws = new WebSocket(url);
     return () => ws.close();
   }, [url]);
   ```

---

### Memoization Usage

**Total:** 70 occurrences across 21 files

**Well-Optimized Hooks:**
- `useWebSocket.ts` - 7 memoizations (callbacks for connect, disconnect, subscribe)
- `useMarketData.ts` - 2 memoizations (throttled state updates)
- `AuthContext.tsx` - 7 memoizations (auth functions)

**Optimization Patterns:**
1. **Callback Memoization:**
   ```typescript
   const handleSubmit = useCallback(() => {
     // Expensive operation
   }, [dependencies]);
   ```

2. **Computed Values:**
   ```typescript
   const filteredData = useMemo(() =>
     data.filter(condition), [data]
   );
   ```

3. **Component Memoization:**
   ```typescript
   export default React.memo(Component);
   ```

**Missing Optimizations:**
- Many components pass inline functions as props (causes re-renders)
- Large data transformations not memoized
- D3 chart rendering not optimized (re-render on every parent update)

---

## Cross-Component Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         _app.tsx (Root)                             │
│  ┌─────────────────────────────────────────────────────────┐        │
│  │ ErrorBoundary                                            │        │
│  │  ┌───────────────────────────────────────────────────┐  │        │
│  │  │ ThemeProvider (theme state)                        │  │        │
│  │  │  ┌─────────────────────────────────────────────┐  │  │        │
│  │  │  │ GlowStyleProvider (glow style)              │  │  │        │
│  │  │  │  ┌───────────────────────────────────────┐  │  │  │        │
│  │  │  │  │ AuthProvider (user, tokens)           │  │  │  │        │
│  │  │  │  │  ┌─────────────────────────────────┐  │  │  │  │        │
│  │  │  │  │  │ ChatProvider (chat open/close)  │  │  │  │  │        │
│  │  │  │  │  │  ┌───────────────────────────┐  │  │  │  │  │        │
│  │  │  │  │  │  │ WorkflowProvider          │  │  │  │  │  │        │
│  │  │  │  │  │  │  (workflow navigation)     │  │  │  │  │  │        │
│  │  │  │  │  │  │   │                        │  │  │  │  │  │        │
│  │  │  │  │  │  │   ↓                        │  │  │  │  │  │        │
│  │  │  │  │  │  │ TelemetryProvider         │  │  │  │  │  │        │
│  │  │  │  │  │  │  (event tracking)          │  │  │  │  │  │        │
│  │  │  │  │  │  │   │                        │  │  │  │  │  │        │
│  │  │  │  │  │  │   ↓                        │  │  │  │  │  │        │
│  │  │  │  │  │  │ Component (page)           │  │  │  │  │  │        │
│  │  │  │  │  │  └───────────────────────────┘  │  │  │  │  │        │
│  │  │  │  │  └─────────────────────────────────┘  │  │  │  │        │
│  │  │  │  └───────────────────────────────────────┘  │  │  │        │
│  │  │  └─────────────────────────────────────────────┘  │  │        │
│  │  └───────────────────────────────────────────────────┘  │        │
│  └─────────────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────────┘

                            ↓ ↓ ↓

┌─────────────────────────────────────────────────────────────────────┐
│                      DATA FLOW LAYERS                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. API LAYER (Backend Communication)                               │
│     ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│     │ REST API     │  │ WebSocket    │  │ EventSource  │           │
│     │ (SWR cached) │  │ (unused)     │  │ (SSE)        │           │
│     └──────────────┘  └──────────────┘  └──────────────┘           │
│            ↓                  ↓                  ↓                  │
│                                                                     │
│  2. CACHING LAYER                                                   │
│     ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│     │ SWR Cache    │  │ localStorage │  │ Memory State │           │
│     │ (auto-expire)│  │ (persistent) │  │ (transient)  │           │
│     └──────────────┘  └──────────────┘  └──────────────┘           │
│            ↓                  ↓                  ↓                  │
│                                                                     │
│  3. STATE MANAGEMENT LAYER                                          │
│     ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│     │ Context API  │  │ Component    │  │ Custom Hooks │           │
│     │ (global)     │  │ State        │  │ (shared)     │           │
│     └──────────────┘  └──────────────┘  └──────────────┘           │
│            ↓                  ↓                  ↓                  │
│                                                                     │
│  4. COMPONENT LAYER                                                 │
│     ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│     │ Workflow     │  │ Dashboards   │  │ Modals/Forms │           │
│     │ Components   │  │              │  │              │           │
│     └──────────────┘  └──────────────┘  └──────────────┘           │
│            ↓                  ↓                  ↓                  │
│                                                                     │
│  5. UI RENDER LAYER                                                 │
│     ┌──────────────────────────────────────────────────┐            │
│     │  React Reconciliation → DOM Updates              │            │
│     └──────────────────────────────────────────────────┘            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow: Typical User Action

### Example: User Loads "Active Positions" Workflow

```
1. User clicks "Active Positions" wedge in RadialMenu
   ↓
2. RadialMenu.tsx calls setCurrentWorkflow("active-positions")
   ↓
3. WorkflowContext updates currentWorkflow state
   ↓
4. index.tsx detects workflow change, renders ActivePositions.tsx
   ↓
5. ActivePositions.tsx mounts, triggers useEffect
   ↓
6. useEffect calls fetchPositions()
   ↓
7. fetchPositions() → fetch("/api/proxy/api/positions")
   ↓
8. Next.js API proxy forwards to backend FastAPI
   ↓
9. Backend queries Alpaca Paper Trading API
   ↓
10. Response: { positions: [...] }
   ↓
11. SWR caches response (5-second TTL)
   ↓
12. setPositions(response.positions)
   ↓
13. React re-renders ActivePositions with new data
   ↓
14. PositionsTable.tsx receives positions as props
   ↓
15. D3/Chart components render visualization
   ↓
16. User sees updated positions in UI

Background (concurrent):
- SWR revalidates every 5 seconds (silently)
- EventSource streams market data to logo (every 10s throttled)
- StatusBar polls /api/health every 30s
```

---

## Bottleneck Analysis

### Identified Performance Bottlenecks

1. **Excessive Polling**
   - **Issue:** 10+ components polling independently
   - **Impact:** High API load, redundant network requests
   - **Solution:** Consolidate into global polling service, use WebSocket push

2. **Unthrottled Market Data Updates**
   - **Issue:** EventSource updates trigger re-renders
   - **Impact:** Logo animation interruptions
   - **Solution:** ✅ Already implemented (10s throttle via lodash)

3. **D3 Re-renders**
   - **Issue:** D3 charts re-render on every parent update
   - **Impact:** Janky animations, high CPU usage
   - **Solution:** Wrap D3 components in React.memo, compare props

4. **localStorage Blocking Operations**
   - **Issue:** Synchronous localStorage.setItem in hot paths
   - **Impact:** UI freezes on large data writes
   - **Solution:** Debounce writes, use IndexedDB for large data

5. **Prop Drilling**
   - **Issue:** Props passed 3+ levels deep (index.tsx → Workflow → Subcomponent)
   - **Impact:** Unnecessary re-renders, hard to maintain
   - **Solution:** Extract to context or custom hooks

6. **No Request Deduplication Outside SWR**
   - **Issue:** Polling-based components make redundant requests
   - **Impact:** Multiple identical API calls in short timeframes
   - **Solution:** Add global request deduplication layer

---

## Race Condition Analysis

### Identified Race Conditions

1. **Token Refresh Race Condition**
   - **Scenario:** Multiple API calls trigger refresh simultaneously
   - **Impact:** Multiple refresh requests, token overwrites
   - **Current State:** NOT HANDLED
   - **Solution:** Add token refresh lock (only one refresh at a time)

2. **WebSocket Reconnection Race**
   - **Scenario:** Multiple reconnect attempts trigger concurrently
   - **Impact:** Multiple WebSocket connections
   - **Current State:** ✅ HANDLED (reconnectAttemptsRef prevents duplicates)

3. **Concurrent localStorage Writes**
   - **Scenario:** Multiple components write to same key
   - **Impact:** Data loss, inconsistent state
   - **Current State:** NOT HANDLED
   - **Solution:** Add mutex lock or use atomic operations library

4. **SSE Reconnection + Manual Fetch**
   - **Scenario:** EventSource reconnects while manual fetch is in progress
   - **Impact:** Duplicate data updates, stale data overwrites
   - **Current State:** PARTIALLY HANDLED (timestamp check)

---

## Multi-Tab Concurrency Issues

### Current State: NO MULTI-TAB SYNCHRONIZATION

**Issues:**
1. **localStorage updates don't sync across tabs**
   - User edits settings in Tab A → Tab B still shows old settings
   - Solution: Add `storage` event listener

2. **Token refresh in one tab doesn't update others**
   - Tab A refreshes token → Tab B still uses expired token
   - Solution: Broadcast token updates via `storage` event

3. **WebSocket connections per tab**
   - Multiple tabs = multiple WebSocket connections
   - Impact: Unnecessary server load
   - Solution: Use SharedWorker for single shared connection

4. **No optimistic updates coordination**
   - Tab A submits order → Tab B doesn't see it until next poll
   - Solution: BroadcastChannel API for cross-tab messaging

**Recommendation:**
```typescript
// Add to _app.tsx
useEffect(() => {
  const handleStorageChange = (e: StorageEvent) => {
    if (e.key === 'paiid_tokens' && e.newValue) {
      // Update AuthContext with new tokens
      refreshSession();
    }
  };
  window.addEventListener('storage', handleStorageChange);
  return () => window.removeEventListener('storage', handleStorageChange);
}, []);
```

---

## Security Audit: localStorage

### CRITICAL Security Issues

#### 1. Plaintext JWT Token Storage

**Issue:** `paiid_tokens` stores JWT tokens in plaintext localStorage

**Vulnerability:**
```javascript
// Any script can access tokens (XSS vulnerability)
const tokens = localStorage.getItem('paiid_tokens');
console.log(JSON.parse(tokens)); // { accessToken, refreshToken }
```

**Attack Vector:**
- XSS injection in any component
- Malicious browser extension
- Compromised third-party script

**Recommendation:**
```typescript
// Option 1: httpOnly cookies (backend sets, frontend can't access)
// Backend: Set-Cookie: access_token=...; HttpOnly; Secure; SameSite=Strict

// Option 2: Use SecureStorage wrapper (already exists in codebase!)
import { secureStorage } from '@/lib/secureStorage';
await secureStorage.setItem('auth_token', tokens.access_token);
```

**Mitigation Priority:** 🔴 CRITICAL - Fix immediately

---

#### 2. Potential API Keys in Settings

**Issue:** `allessandra_settings` localStorage key may contain API keys

**Vulnerability:**
- If user inputs API keys in settings, they're stored plaintext
- Accessible via XSS

**Recommendation:**
```typescript
// Use SecureStorage for any user-provided sensitive data
await secureStorageHelpers.storeApiKey('alpaca', apiKey);
```

**Mitigation Priority:** 🟡 MEDIUM - Audit settings schema

---

#### 3. PII in User Profile Storage

**Issue:** `paid_user_profile` may contain personally identifiable information

**Data at Risk:**
- Email address
- Full name
- Phone number (if collected)

**Recommendation:**
- Minimize PII storage in localStorage
- Use SecureStorage for unavoidable PII
- Add data retention policy (auto-clear after N days)

**Mitigation Priority:** 🟡 MEDIUM - Audit profile schema

---

### SecureStorage Implementation Review

**Status:** ✅ AVAILABLE BUT UNDERUTILIZED

**Features:**
- AES-GCM 256-bit encryption
- Session-based keys (cleared on tab close)
- Web Crypto API (browser-native)

**Current Usage:**
- Defined in `lib/secureStorage.ts`
- Helper functions available
- NOT USED FOR JWT TOKENS (critical miss)

**Recommended Migration Plan:**
1. Migrate `paiid_tokens` to SecureStorage
2. Migrate `allessandra_settings` to SecureStorage
3. Migrate `paid_user_profile` to SecureStorage
4. Add migration script for existing users

---

## Recommendations Summary

### High Priority (Immediate Action Required)

1. **Migrate JWT tokens to SecureStorage or httpOnly cookies**
   - Risk: Active security vulnerability
   - Effort: 2-4 hours
   - Impact: HIGH

2. **Add token refresh lock to prevent race conditions**
   - Risk: Token corruption, auth failures
   - Effort: 1-2 hours
   - Impact: MEDIUM

3. **Implement multi-tab token synchronization**
   - Risk: Poor UX, auth inconsistencies
   - Effort: 2-3 hours
   - Impact: MEDIUM

### Medium Priority (Next Sprint)

4. **Replace polling with WebSocket push for active components**
   - Components: ActivePositions, Analytics, StatusBar
   - Benefit: 60% reduction in API calls
   - Effort: 1 week

5. **Add request deduplication layer**
   - Benefit: Prevent duplicate API calls
   - Effort: 1 day

6. **Optimize D3 chart re-renders**
   - Use React.memo with deep prop comparison
   - Effort: 2 days

### Low Priority (Backlog)

7. **Migrate large localStorage data to IndexedDB**
   - Keys: trade history, performance cache
   - Benefit: Non-blocking storage
   - Effort: 3 days

8. **Add BroadcastChannel for cross-tab messaging**
   - Benefit: Real-time multi-tab sync
   - Effort: 2 days

9. **Implement SharedWorker for WebSocket connections**
   - Benefit: Single connection for all tabs
   - Effort: 1 week

---

## Appendix: Data Flow Quick Reference

### Context Provider Hierarchy (Top to Bottom)
1. ErrorBoundary
2. ThemeProvider
3. GlowStyleProvider
4. AuthProvider
5. ChatProvider
6. WorkflowProvider
7. TelemetryProvider
8. Component (page)

### localStorage Keys by Category

**Auth:** paiid_tokens, user-id, user-role
**Onboarding:** user-setup-complete, admin-bypass, bypass-timestamp, manual-skip
**Theme:** paiid-theme
**Market Data:** paiid-market-data
**Trading:** orderHistory, paiid_trading_journal, trading-mode, paiid_trade_history, paiid_performance_cache
**Strategy:** ai_trader_strategies
**Settings:** allessandra_settings
**User Profile:** paid_user_profile, paiid_user_data
**Telemetry:** userId, userRole
**Secure:** paiid_secure_* (encrypted)

### Polling Intervals

- **5 seconds:** Positions (SWR)
- **10 seconds:** Account (SWR), Market data (SWR), Quotes (SWR), Approval queue, P&L live
- **15 seconds:** Order history (SWR)
- **30 seconds:** Analytics (SWR), Performance dashboard, GitHub Actions, Monitor, StatusBar
- **5 minutes:** News (SWR), Company news (SWR), AI recommendations, Sentiment, News review

### Real-Time Streaming

- **EventSource (SSE):** Market indices (10s throttled updates)
- **WebSocket:** Available but unused (market_data, portfolio_update, position_update, trading_alert)

---

**End of Report**

**Auditor:** MOD-2C
**Date:** 2025-10-27
**Next Review:** Scheduled after security fixes implementation
