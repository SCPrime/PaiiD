# State Consistency Test Plan - PaiiD Application

**MOD-2C Test Plan**
**Date:** 2025-10-27
**Version:** 1.0

---

## Overview

This test plan validates data consistency across components, localStorage persistence, API cache invalidation, and multi-tab synchronization in the PaiiD application.

---

## Test Environment Setup

### Prerequisites

1. **Development Server Running**
   ```bash
   # Backend
   cd backend
   python -m uvicorn app.main:app --reload --port 8001

   # Frontend
   cd frontend
   npm run dev
   ```

2. **Browser Configuration**
   - Chrome/Edge DevTools open
   - Network throttling: Fast 3G (for timing tests)
   - Disable cache during testing

3. **Test Data**
   - Clean localStorage (run `localStorage.clear()` in console)
   - Fresh user session
   - Mock API responses (optional, for isolated tests)

### Test User Setup

```javascript
// Run in browser console
localStorage.setItem('user-id', 'test-user-001');
localStorage.setItem('user-role', 'alpha');
localStorage.setItem('user-setup-complete', 'true');
```

---

## Test Suite 1: Context Provider State Consistency

### Test 1.1: AuthContext - Token Refresh

**Objective:** Verify token refresh updates all components using useAuth()

**Steps:**
1. Login with valid credentials
2. Verify `paiid_tokens` in localStorage
3. Open DevTools → Application → Local Storage
4. Manually modify `expiresAt` to trigger immediate refresh
5. Wait for auto-refresh (should happen within 10 minutes)
6. Verify all components still authenticated

**Expected Result:**
- ✅ All components receive updated user state
- ✅ No logout or 401 errors
- ✅ Token refresh transparent to user

**Test Data:**
```json
// Before refresh
{
  "accessToken": "eyJhbGc...",
  "refreshToken": "refresh_...",
  "expiresAt": 1730000000000
}

// After refresh (new tokens, updated expiresAt)
{
  "accessToken": "eyJhbGc...[NEW]",
  "refreshToken": "refresh_...[NEW]",
  "expiresAt": 1730001000000
}
```

**Pass Criteria:**
- Token refresh occurs within 10 minutes
- User remains authenticated
- All API calls use new access token

---

### Test 1.2: WorkflowContext - Cross-Workflow Data Passing

**Objective:** Verify data passed from AI Recommendations to Execute Trade

**Steps:**
1. Navigate to "AI Recommendations" workflow
2. Click "Execute Trade" button on recommendation
3. Verify ExecuteTradeForm pre-filled with:
   - Symbol
   - Entry price
   - Stop loss
   - Take profit
4. Modify form, submit order
5. Navigate away, return to Execute Trade
6. Verify form cleared (pendingNavigation consumed)

**Expected Result:**
- ✅ Trade form pre-populated with recommendation data
- ✅ Pending navigation cleared after consumption
- ✅ No stale data on subsequent visits

**Test Data:**
```typescript
const tradeData: TradeData = {
  symbol: "AAPL",
  side: "buy",
  quantity: 10,
  entryPrice: 150.00,
  stopLoss: 145.00,
  takeProfit: 160.00,
  orderType: "limit",
  timeInForce: "day"
};
```

**Pass Criteria:**
- All fields pre-populated correctly
- clearPendingNavigation() called after consumption
- No data persistence after navigation away

---

### Test 1.3: ThemeContext - Persistence Across Sessions

**Objective:** Verify theme persists after page reload

**Steps:**
1. Set theme to "light"
2. Verify `paiid-theme` in localStorage = "light"
3. Reload page (hard refresh: Ctrl+Shift+R)
4. Verify theme still "light"
5. Toggle to "dark"
6. Close tab, reopen app
7. Verify theme still "dark"

**Expected Result:**
- ✅ Theme persists across reloads
- ✅ Theme persists across browser sessions
- ✅ document.documentElement has correct class ("dark" or "light")

**Pass Criteria:**
- localStorage updated immediately on toggle
- Theme applied before first paint (no flash)
- Meta theme-color updated for mobile browsers

---

## Test Suite 2: localStorage Persistence Tests

### Test 2.1: JWT Token Storage Security

**Objective:** Verify tokens NOT accessible via simple XSS

**Steps:**
1. Login to application
2. Open DevTools console
3. Execute: `console.log(localStorage.getItem('paiid_tokens'))`
4. Verify tokens visible (CURRENT BEHAVIOR - FAIL)
5. Apply SecureStorage migration
6. Re-test: `console.log(localStorage.getItem('paiid_secure_auth_token'))`
7. Verify encrypted data (Base64 gibberish)

**Expected Result (After Fix):**
- ❌ CURRENT: Plaintext tokens visible
- ✅ TARGET: Encrypted tokens only

**Test Data:**
```javascript
// CURRENT (INSECURE):
{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refreshToken": "refresh_abc123...",
  "expiresAt": 1730000000000
}

// TARGET (SECURE):
{
  "iv": "j3kD9fK2...",
  "data": "Kf8sLmP9qR2t..."  // AES-GCM encrypted
}
```

**Pass Criteria:**
- Tokens encrypted at rest
- Decryption only possible with session key (in sessionStorage)
- Session key cleared on tab close

---

### Test 2.2: Market Data Cache Expiration

**Objective:** Verify stale market data cache expires after 24 hours

**Steps:**
1. Load application, observe market data
2. Verify `paiid-market-data` in localStorage
3. Manually modify timestamp to 25 hours ago:
   ```javascript
   const cache = JSON.parse(localStorage.getItem('paiid-market-data'));
   cache.timestamp = Date.now() - (25 * 60 * 60 * 1000);
   localStorage.setItem('paiid-market-data', JSON.stringify(cache));
   ```
4. Reload page
5. Verify fresh data fetched (not stale cache)

**Expected Result:**
- ✅ Stale cache ignored
- ✅ Fresh data fetched from backend
- ✅ New timestamp in localStorage

**Pass Criteria:**
- Cache used only if < 24 hours old
- Fallback to API fetch if cache expired
- SSE stream continues regardless of cache state

---

### Test 2.3: Order History Persistence

**Objective:** Verify order history persists across sessions

**Steps:**
1. Execute 3 test orders (paper trading)
2. Verify `orderHistory` in localStorage
3. Reload page
4. Navigate to "Analytics" or "Order History" workflow
5. Verify all 3 orders displayed
6. Clear localStorage
7. Reload page
8. Verify order history empty (fresh fetch from backend)

**Expected Result:**
- ✅ Orders persist in localStorage
- ✅ Orders displayed after reload
- ✅ Graceful handling if localStorage cleared

**Pass Criteria:**
- localStorage writes after each order execution
- Order history survives page reloads
- No duplicate orders on concurrent writes

---

### Test 2.4: User Preferences Sync

**Objective:** Verify settings changes persist and sync across app

**Steps:**
1. Navigate to Settings workflow
2. Change 5 settings (e.g., risk tolerance, theme, notifications)
3. Verify `allessandra_settings` in localStorage
4. Navigate to another workflow
5. Return to Settings
6. Verify all 5 changes persisted

**Expected Result:**
- ✅ All settings saved immediately
- ✅ Settings loaded on Settings component mount
- ✅ No settings lost on navigation

**Pass Criteria:**
- localStorage.setItem called on every setting change
- Settings object validated before save
- Default values used if localStorage corrupt

---

## Test Suite 3: API Cache Consistency Tests

### Test 3.1: SWR Cache Deduplication

**Objective:** Verify SWR deduplicates requests within 2-second window

**Steps:**
1. Open DevTools Network tab
2. Clear network log
3. Render 3 components that call `usePositions()` simultaneously
4. Count network requests to `/api/positions`
5. Verify only 1 request made

**Expected Result:**
- ✅ Only 1 API call despite 3 components
- ✅ All 3 components receive data
- ✅ Data served from cache for 5 seconds

**Pass Criteria:**
- Deduplication works within 2000ms window
- All components receive identical data
- No race conditions on concurrent reads

---

### Test 3.2: SWR Revalidation on Focus

**Objective:** Verify SWR revalidates when window regains focus

**Steps:**
1. Load application, observe positions
2. Switch to another app/tab (lose focus)
3. Wait 10 seconds
4. Switch back to PaiiD app
5. Observe Network tab for revalidation request
6. Verify positions updated if data changed

**Expected Result:**
- ✅ Revalidation triggered on focus
- ✅ Fresh data fetched in background
- ✅ UI updates if data changed

**Pass Criteria:**
- Revalidation occurs within 500ms of focus
- No loading spinner (background fetch)
- Stale data shown until revalidation completes

---

### Test 3.3: SWR Cache Invalidation on Mutation

**Objective:** Verify cache invalidates after order execution

**Steps:**
1. Load Active Positions (caches `/api/positions`)
2. Execute new order via Execute Trade workflow
3. Immediately navigate back to Active Positions
4. Verify positions list includes new order
5. Check Network tab for fresh `/api/positions` call

**Expected Result:**
- ✅ Cache invalidated after mutation
- ✅ Fresh data fetched automatically
- ✅ New position visible immediately

**Pass Criteria:**
- Mutation triggers cache invalidation
- Revalidation happens without user action
- No stale data displayed

**Implementation Note:**
```typescript
// After order execution
import { mutate } from 'swr';
await mutate('/api/proxy/api/positions');
```

---

### Test 3.4: Polling Interval Accuracy

**Objective:** Verify polling intervals match specifications

**Steps:**
1. Open DevTools Network tab
2. Enable "Preserve log"
3. Let app run for 5 minutes
4. Filter network log for `/api/positions`
5. Measure time between consecutive requests
6. Verify interval = 5 seconds (±500ms tolerance)

**Expected Result:**
- ✅ Requests at 5-second intervals
- ✅ No request spikes or gaps
- ✅ Polling stops when component unmounts

**Test Data:**
```
Expected Timeline:
T+0s:    /api/positions (initial)
T+5s:    /api/positions (poll 1)
T+10s:   /api/positions (poll 2)
T+15s:   /api/positions (poll 3)
```

**Pass Criteria:**
- Interval within ±500ms of target
- No duplicate requests in same interval
- Cleanup on component unmount

---

## Test Suite 4: Real-Time Streaming Tests

### Test 4.1: EventSource Reconnection

**Objective:** Verify SSE reconnects after network interruption

**Steps:**
1. Load application, observe market data streaming
2. Open DevTools Network tab
3. Simulate network disconnect:
   - DevTools → Network → Offline checkbox
4. Wait 5 seconds
5. Re-enable network
6. Observe EventSource reconnection attempts
7. Verify market data resumes

**Expected Result:**
- ✅ Reconnection attempts with exponential backoff
- ✅ Max 10 attempts before giving up
- ✅ Data streaming resumes after reconnection

**Test Data:**
```
Reconnection Timeline:
T+0s:  Disconnect detected
T+2s:  Retry attempt 1
T+4s:  Retry attempt 2
T+8s:  Retry attempt 3
T+16s: Retry attempt 4
...
```

**Pass Criteria:**
- Backoff delay: 2s, 4s, 8s, 16s, 32s, 64s, 128s (max)
- User notified of connection status
- Cached data displayed during reconnection

---

### Test 4.2: EventSource Throttling

**Objective:** Verify market data updates throttled to prevent animation glitches

**Steps:**
1. Open DevTools Console
2. Monitor log messages: `[useMarketData] Market data updated (throttled)`
3. Let app run for 1 minute
4. Count number of log messages
5. Verify max 6 updates (1 per 10 seconds)

**Expected Result:**
- ✅ Max 1 update per 10 seconds
- ✅ Logo animation not interrupted
- ✅ All incoming data cached (immediate localStorage write)

**Pass Criteria:**
- Throttle interval: 10000ms
- Logo glow animation smooth (60fps)
- Data always cached regardless of throttle

---

### Test 4.3: WebSocket Connection Lifecycle

**Objective:** Verify WebSocket connects, subscribes, and cleans up correctly

**Steps:**
1. Render component using `useWebSocket()` (e.g., AIRecommendations)
2. Verify WebSocket connection established
3. Subscribe to symbols: ['AAPL', 'MSFT', 'GOOGL']
4. Verify subscription confirmed message received
5. Unmount component
6. Verify WebSocket closed (Network tab)

**Expected Result:**
- ✅ Connection established on mount
- ✅ Subscription confirmed within 1 second
- ✅ Connection closed on unmount

**Pass Criteria:**
- No orphaned WebSocket connections
- Subscriptions tracked in Set
- Cleanup function called on unmount

---

## Test Suite 5: Multi-Tab Consistency Tests

### Test 5.1: localStorage Sync Across Tabs

**Objective:** Verify settings changes sync to other tabs

**Steps:**
1. Open PaiiD in Tab A
2. Open PaiiD in Tab B (new tab)
3. In Tab A: Change theme to "light"
4. Switch to Tab B
5. Verify theme DOES NOT auto-update (CURRENT BEHAVIOR)
6. Manually reload Tab B
7. Verify theme updated to "light"

**Expected Result (Current):**
- ❌ Tab B does not auto-update (no `storage` event listener)

**Expected Result (Target):**
- ✅ Tab B auto-updates within 100ms
- ✅ No page reload required

**Implementation Needed:**
```typescript
// Add to _app.tsx
useEffect(() => {
  const handleStorageChange = (e: StorageEvent) => {
    if (e.key === 'paiid-theme') {
      setTheme(e.newValue as Theme);
    }
  };
  window.addEventListener('storage', handleStorageChange);
  return () => window.removeEventListener('storage', handleStorageChange);
}, []);
```

**Pass Criteria (Target):**
- Theme updates across tabs without reload
- No conflicting writes
- User sees consistent UI in all tabs

---

### Test 5.2: Token Refresh Race Condition

**Objective:** Verify only one token refresh happens when multiple tabs expire

**Steps:**
1. Open PaiiD in 3 tabs
2. Manually set token expiry to 1 minute ago in all tabs
3. Trigger API call in each tab simultaneously
4. Observe Network tab in all tabs
5. Count number of `/api/auth/refresh` requests

**Expected Result (Current):**
- ❌ 3 refresh requests (one per tab)

**Expected Result (Target):**
- ✅ 1 refresh request (first tab wins)
- ✅ Other tabs wait for result
- ✅ All tabs update with new tokens

**Implementation Needed:**
```typescript
// Token refresh lock using localStorage
const REFRESH_LOCK_KEY = 'paiid_refresh_lock';

async function refreshToken() {
  const now = Date.now();
  const lock = localStorage.getItem(REFRESH_LOCK_KEY);

  if (lock && now - parseInt(lock) < 5000) {
    // Another tab is refreshing, wait
    await new Promise(resolve => setTimeout(resolve, 1000));
    return; // Use updated tokens from localStorage
  }

  localStorage.setItem(REFRESH_LOCK_KEY, now.toString());
  // Proceed with refresh...
}
```

**Pass Criteria (Target):**
- Only 1 refresh request across all tabs
- All tabs receive updated tokens
- No token corruption

---

### Test 5.3: WebSocket Multi-Tab Behavior

**Objective:** Verify WebSocket connections isolated per tab (no shared state)

**Steps:**
1. Open PaiiD in Tab A
2. Subscribe to AAPL in Tab A
3. Open PaiiD in Tab B
4. Subscribe to MSFT in Tab B
5. Verify 2 separate WebSocket connections (Network tab)
6. Close Tab A
7. Verify Tab B WebSocket unaffected

**Expected Result:**
- ✅ Each tab has independent WebSocket connection
- ✅ Subscriptions isolated per tab
- ✅ No shared state between tabs

**Pass Criteria:**
- 2 WebSocket connections in Network tab
- Closing one tab doesn't affect other
- No message cross-contamination

**Future Enhancement:**
- Use SharedWorker for single shared connection
- BroadcastChannel for message distribution
- Reduces server load

---

## Test Suite 6: Race Condition Tests

### Test 6.1: Concurrent localStorage Writes

**Objective:** Verify no data loss when multiple components write to same key

**Steps:**
1. Open DevTools Console
2. Execute 10 concurrent writes to `orderHistory`:
   ```javascript
   for (let i = 0; i < 10; i++) {
     setTimeout(() => {
       const orders = JSON.parse(localStorage.getItem('orderHistory') || '[]');
       orders.push({ id: i, symbol: 'TEST' });
       localStorage.setItem('orderHistory', JSON.stringify(orders));
     }, 0);
   }
   ```
3. Retrieve final orderHistory
4. Count number of orders
5. Verify all 10 orders present

**Expected Result (Current):**
- ❌ Data loss likely (race condition)

**Expected Result (Target):**
- ✅ All 10 orders present
- ✅ No overwrites

**Implementation Needed:**
```typescript
// Atomic localStorage update
function atomicUpdate(key: string, updateFn: (current: any) => any) {
  const lock = `${key}_lock`;
  const acquire = () => {
    if (sessionStorage.getItem(lock)) {
      setTimeout(acquire, 10);
      return;
    }
    sessionStorage.setItem(lock, '1');
  };

  acquire();
  const current = JSON.parse(localStorage.getItem(key) || 'null');
  const updated = updateFn(current);
  localStorage.setItem(key, JSON.stringify(updated));
  sessionStorage.removeItem(lock);
}
```

**Pass Criteria (Target):**
- No lost writes
- All updates applied
- Correct final state

---

### Test 6.2: API Call Race Condition

**Objective:** Verify correct data displayed when rapid API calls return out of order

**Steps:**
1. Render component with fast polling (1 second)
2. Simulate slow API responses:
   - Request 1 (T+0s): Returns at T+3s
   - Request 2 (T+1s): Returns at T+2s
3. Verify component displays data from Request 2 (most recent)
4. When Request 1 returns, verify data NOT overwritten

**Expected Result:**
- ✅ Only most recent data displayed
- ✅ Stale responses ignored

**Implementation Pattern:**
```typescript
const [latestRequestId, setLatestRequestId] = useState(0);

const fetchData = async () => {
  const requestId = Date.now();
  setLatestRequestId(requestId);

  const data = await fetch('/api/data');

  // Only update if this is still the latest request
  if (requestId === latestRequestId) {
    setData(data);
  }
};
```

**Pass Criteria:**
- Out-of-order responses handled correctly
- No UI flicker from stale data
- Latest data always wins

---

## Test Suite 7: Component State Sync Tests

### Test 7.1: Prop Drilling Consistency

**Objective:** Verify deeply nested props remain consistent

**Steps:**
1. Render index.tsx → ActivePositions → PositionsTable
2. Pass `positions` prop down 3 levels
3. Update positions in parent
4. Verify all child components re-render with new data
5. Check no stale data in any child

**Expected Result:**
- ✅ All children receive updated props
- ✅ No intermediate layer caching stale data

**Pass Criteria:**
- React.memo doesn't block necessary updates
- No prop transformation errors
- Consistent data at all levels

---

### Test 7.2: Context Consumer Consistency

**Objective:** Verify all AuthContext consumers update on user change

**Steps:**
1. Identify all components using `useAuth()`
2. Login as User A
3. Verify all components show User A data
4. Logout
5. Login as User B
6. Verify all components immediately show User B data

**Expected Result:**
- ✅ All consumers update within 100ms
- ✅ No components showing stale user data

**Pass Criteria:**
- No cached user data in components
- All consumers re-render on context change
- No memory leaks from old subscriptions

---

## Test Suite 8: Performance Tests

### Test 8.1: localStorage Write Performance

**Objective:** Measure localStorage write latency for large data

**Steps:**
1. Generate 1000 mock orders
2. Measure time to write to localStorage:
   ```javascript
   const start = performance.now();
   localStorage.setItem('orderHistory', JSON.stringify(largeArray));
   const end = performance.now();
   console.log(`Write time: ${end - start}ms`);
   ```
3. Verify write time < 50ms (target)

**Expected Result:**
- ✅ Write completes in < 50ms
- ✅ No UI blocking

**Pass Criteria:**
- Write time acceptable for UX
- Consider debouncing if > 50ms
- Consider IndexedDB if > 100ms

---

### Test 8.2: D3 Chart Re-render Performance

**Objective:** Measure chart re-render time

**Steps:**
1. Load Analytics workflow with D3 charts
2. Open DevTools Performance tab
3. Record performance while updating chart data
4. Measure time from data update to render complete
5. Verify < 16ms (60fps target)

**Expected Result:**
- ✅ Re-render in < 16ms
- ✅ Smooth animations

**Pass Criteria:**
- Frame rate maintained at 60fps
- No dropped frames during update
- React.memo prevents unnecessary re-renders

---

## Test Execution Checklist

### Pre-Test Setup
- [ ] Development servers running
- [ ] Browser DevTools open
- [ ] localStorage cleared (fresh state)
- [ ] Network tab monitoring
- [ ] Console logging enabled

### Test Execution
- [ ] Run Test Suite 1: Context Providers
- [ ] Run Test Suite 2: localStorage Persistence
- [ ] Run Test Suite 3: API Cache Consistency
- [ ] Run Test Suite 4: Real-Time Streaming
- [ ] Run Test Suite 5: Multi-Tab Consistency
- [ ] Run Test Suite 6: Race Conditions
- [ ] Run Test Suite 7: Component State Sync
- [ ] Run Test Suite 8: Performance

### Post-Test Analysis
- [ ] Document failed tests
- [ ] Identify root causes
- [ ] Prioritize fixes (Critical → High → Medium → Low)
- [ ] Create GitHub issues for each failure
- [ ] Schedule fix implementation

---

## Automated Testing Recommendations

### Jest Unit Tests

```typescript
// Example: AuthContext token refresh test
describe('AuthContext', () => {
  it('should refresh token when expired', async () => {
    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider
    });

    // Mock token expiry
    act(() => {
      localStorage.setItem('paiid_tokens', JSON.stringify({
        accessToken: 'old_token',
        refreshToken: 'refresh_token',
        expiresAt: Date.now() - 1000 // Expired
      }));
    });

    await waitFor(() => {
      expect(result.current.isAuthenticated).toBe(true);
    });

    const newTokens = JSON.parse(localStorage.getItem('paiid_tokens'));
    expect(newTokens.accessToken).not.toBe('old_token');
  });
});
```

### Cypress E2E Tests

```typescript
// Example: Multi-workflow data passing test
describe('Workflow Navigation', () => {
  it('should pass trade data from AI Recommendations to Execute Trade', () => {
    cy.visit('/');
    cy.get('[data-workflow="ai-recommendations"]').click();
    cy.get('[data-recommendation-id="1"]').find('[data-action="execute"]').click();

    // Verify Execute Trade form pre-filled
    cy.get('[name="symbol"]').should('have.value', 'AAPL');
    cy.get('[name="entryPrice"]').should('have.value', '150.00');
  });
});
```

### Playwright Multi-Tab Tests

```typescript
// Example: Multi-tab localStorage sync test
test('should sync theme across tabs', async ({ context }) => {
  const page1 = await context.newPage();
  const page2 = await context.newPage();

  await page1.goto('http://localhost:3000');
  await page2.goto('http://localhost:3000');

  // Change theme in page1
  await page1.click('[data-testid="theme-toggle"]');

  // Verify theme updated in page2
  await page2.waitForTimeout(200);
  const theme = await page2.evaluate(() =>
    document.documentElement.classList.contains('light')
  );
  expect(theme).toBe(true);
});
```

---

## Continuous Monitoring

### Metrics to Track

1. **API Call Frequency**
   - Track unique endpoint calls per minute
   - Alert if > 100 calls/min per user

2. **localStorage Size**
   - Monitor total size of stored data
   - Alert if > 5MB (browser limits: 10MB)

3. **WebSocket Connection Health**
   - Track connection uptime %
   - Alert if < 95% uptime

4. **Token Refresh Success Rate**
   - Track successful vs failed refresh attempts
   - Alert if < 99% success rate

5. **Multi-Tab Incidents**
   - Track auth conflicts across tabs
   - Alert on token corruption events

---

## Success Criteria Summary

**Test Suite Pass Rate:** ≥ 95% (all critical tests must pass)

**Critical Tests (Must Pass):**
- Test 1.1: AuthContext token refresh
- Test 2.1: JWT token security
- Test 3.1: SWR cache deduplication
- Test 5.2: Token refresh race condition
- Test 6.1: Concurrent localStorage writes

**Performance Targets:**
- localStorage write: < 50ms
- API cache hit rate: > 70%
- D3 chart re-render: < 16ms (60fps)
- Multi-tab sync latency: < 100ms

**Security Requirements:**
- All sensitive data encrypted in localStorage
- No XSS vulnerabilities in token storage
- HTTPS-only cookies for production

---

**End of Test Plan**

**Author:** MOD-2C
**Date:** 2025-10-27
**Next Update:** After test execution and results analysis
