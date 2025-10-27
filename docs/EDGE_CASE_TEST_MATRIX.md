# Edge Case Test Matrix

**Project:** PaiiD - Personal Artificial Intelligence Investment Dashboard
**Generated:** 2025-10-27
**Purpose:** Comprehensive edge case, error state, and boundary condition testing guide

---

## Table of Contents
1. [Loading States](#loading-states)
2. [Empty States](#empty-states)
3. [Error Handling](#error-handling)
4. [Form Validation](#form-validation)
5. [Boundary Conditions](#boundary-conditions)
6. [Network & API Edge Cases](#network--api-edge-cases)
7. [Race Conditions](#race-conditions)
8. [Data Format Edge Cases](#data-format-edge-cases)

---

## Loading States

### 1. Initial Data Load
| Component | Test Scenario | Expected Behavior | Current Implementation |
|-----------|---------------|-------------------|------------------------|
| ExecuteTradeForm | Symbol lookup while typing | Show "Analyzing [SYMBOL] with PaiiD AI..." with spinner | ✅ Implemented (line 1016) |
| Settings | Risk tolerance update | Show "Updating..." text with disabled state | ✅ Implemented (line 1152) |
| Settings | Account balance fetch | Show loading indicator while fetching | ✅ Implemented (line 1012) |
| ActivePositions | Initial positions load | Display skeleton cards | ⚠️ Needs verification |
| AIRecommendations | Fetching recommendations | Show spinner with loading message | ✅ Implemented |
| MarketScanner | Scanning markets | Display progress indicator | ✅ Implemented |
| NewsReview | Loading articles | Show loading skeletons | ✅ Implemented |

### 2. Async Operations
| Component | Test Scenario | Expected Behavior | Status |
|-----------|---------------|-------------------|--------|
| ExecuteTradeForm | Options chain loading | Disable dropdowns, show "Loading expirations..." | ✅ Implemented (line 1503) |
| ExecuteTradeForm | Template save operation | Show "Saving..." on button, disable form | ✅ Implemented (line 1402) |
| Settings | Telemetry data fetch | Display loading state before data appears | ✅ Implemented |
| OptionsGreeksDisplay | Greeks calculation | Show spinner during calculation | ✅ Implemented |

### 3. Progressive Loading
| Component | Test Scenario | Expected Behavior | Status |
|-----------|---------------|-------------------|--------|
| Analytics | Historical data pagination | Show "Loading more..." at bottom | ⚠️ Needs component verification |
| TradingJournal | Infinite scroll | Display inline spinner when loading more entries | ⚠️ Needs verification |
| WatchlistPanel | Real-time price updates | Show stale data indicator if updates stop | ⚠️ Needs implementation |

---

## Empty States

### 1. No Data Available
| Component | Test Scenario | Expected Behavior | Current Implementation |
|-----------|---------------|-------------------|------------------------|
| ActivePositions | No open positions | "No active positions" message with CTA | ✅ Verified in multiple components |
| AIRecommendations | No recommendations | "No AI recommendations available" with icon | ⚠️ Needs verification |
| OrderHistory | No trade history | "No orders yet" with "Execute Trade" button | ⚠️ Needs verification |
| WatchlistPanel | Empty watchlist | "Add symbols to start tracking" message | ✅ Implemented |
| NewsReview | No news articles | "No news available" placeholder | ✅ Implemented |
| TradingJournal | No journal entries | "Start documenting your trades" CTA | ✅ Implemented |

### 2. Search/Filter Results
| Component | Test Scenario | Expected Behavior | Status |
|-----------|---------------|-------------------|--------|
| MarketScanner | No matching results | "No stocks match your criteria" + reset filters button | ⚠️ Needs verification |
| StockLookup | Invalid symbol search | "Symbol not found" error with suggestions | ✅ Implemented (line 286) |
| Settings (Telemetry) | No events logged | "No telemetry data available" message | ✅ Implemented (line 1610) |

### 3. Permission/Access Denied
| Component | Test Scenario | Expected Behavior | Status |
|-----------|---------------|-------------------|--------|
| Settings (Admin tabs) | Non-admin user viewing | Hide admin-only tabs entirely | ✅ Implemented (line 583) |
| ExecuteTradeForm | Insufficient buying power | Show error with current balance | ⚠️ Needs backend validation |

---

## Error Handling

### 1. API Errors
| Component | Test Scenario | Expected Behavior | Current Implementation |
|-----------|---------------|-------------------|------------------------|
| ExecuteTradeForm | Order submission failure | Show red error banner with specific error message | ✅ Implemented (line 1792-1828) |
| ExecuteTradeForm | AI analysis 404 | Display "Symbol [X] not found" error | ✅ Implemented (line 285-286) |
| Settings | Account fetch failure | Show error with retry button | ⚠️ Missing retry mechanism |
| LoginForm | Invalid credentials | Display "Login failed" error in red banner | ✅ Implemented (line 37) |
| RegisterForm | Duplicate email | Show "Registration failed" with reason | ✅ Implemented (line 75) |
| ActivePositions | Positions fetch failure | Error state with retry button | ⚠️ Needs verification |

### 2. Network Errors
| Component | Test Scenario | Expected Behavior | Status |
|-----------|---------------|-------------------|--------|
| StatusBar | Backend unreachable | Show "Offline" indicator | ✅ Implemented |
| ExecuteTradeForm | Timeout during order | Show timeout error with retry option | ⚠️ Needs explicit timeout handling |
| Settings (Telemetry) | API unreachable | Catch error and show empty state (line 293) | ✅ Implemented |

### 3. Component-Level Errors
| Component | Test Scenario | Expected Behavior | Status |
|-----------|---------------|-------------------|--------|
| ErrorBoundary | React render error | Show fallback UI with "Try Again", "Reload", "Go Back" buttons | ✅ Implemented |
| ErrorBoundary | Recurring errors (>2) | Show warning: "This error has occurred X times" | ✅ Implemented (line 243-258) |
| ErrorBoundary | Sentry integration | Attempt to send error to Sentry if configured | ✅ Implemented (line 62-76) |

### 4. Toast Notifications
| Type | Usage Pattern | Duration | Status |
|------|---------------|----------|--------|
| Success | Order executed, settings saved, template created | 5000ms | ✅ Implemented (lib/toast.ts) |
| Error | API failures, validation errors | 7000ms | ✅ Implemented |
| Warning | Duplicate requests, risky operations | 6000ms | ✅ Implemented |
| Info | General notifications | 4000ms | ✅ Implemented |

---

## Form Validation

### 1. ExecuteTradeForm Validation
| Field | Validation Rule | Error Message | Implementation |
|-------|-----------------|---------------|----------------|
| Symbol | Required, non-empty | "Symbol is required" | ✅ Line 391 |
| Quantity | > 0 | "Quantity must be greater than 0" | ✅ Line 395 |
| Limit Price | Required if orderType = "limit", > 0 | "Limit price is required for limit orders" | ✅ Line 399 |
| Option Type | Required if assetClass = "option" | "Option type (call/put) is required" | ✅ Line 406 |
| Strike Price | Required if assetClass = "option", > 0 | "Strike price is required for options" | ✅ Line 410 |
| Expiration | Required if assetClass = "option" | "Expiration date is required for options" | ✅ Line 414 |

### 2. Settings Form Validation
| Field | Validation Rule | Error Message | Implementation |
|-------|-----------------|---------------|----------------|
| Paper Account Balance | Min: $1,000, Max: $10,000,000 | "Minimum balance is $1,000" / "Maximum balance is $10,000,000" | ✅ Line 412-423 |
| Risk Tolerance | 0-100 | Slider enforced | ✅ Line 1166-1167 |
| Slippage Budget | 0-1% | Input enforced | ✅ Line 1084-1085 |
| Max Reprices | 1-10 | Input enforced | ✅ Line 1101-1102 |

### 3. Authentication Forms
| Form | Field | Validation | Error Message | Status |
|------|-------|------------|---------------|--------|
| LoginForm | Email | Required, non-empty | "Please enter email and password" | ✅ Line 26-28 |
| LoginForm | Password | Required, non-empty | "Please enter email and password" | ✅ Line 26-28 |
| RegisterForm | Email | Required | "Please fill in all required fields" | ✅ Line 44-46 |
| RegisterForm | Password | Min 8 chars | "Password must be at least 8 characters" | ✅ Line 49-52 |
| RegisterForm | Password | Must contain uppercase + number | "Password must contain at least one uppercase letter and one number" | ✅ Line 59-62 |
| RegisterForm | Confirm Password | Must match password | "Passwords do not match" | ✅ Line 54-57 |

### 4. Password Strength Indicator
| Strength | Criteria | Color | Status |
|----------|----------|-------|--------|
| Weak | Length < 8 OR missing uppercase/number/special | Red (#ef4444) | ✅ RegisterForm line 32 |
| Fair | 2 criteria met | Orange (#f59e0b) | ✅ RegisterForm line 33 |
| Good | 3 criteria met | Green (#10b981) | ✅ RegisterForm line 34 |
| Strong | All 4 criteria met | Green (#10b981) | ✅ RegisterForm line 35 |

### 5. Real-Time Validation
| Component | Field | Validation Type | Status |
|-----------|-------|-----------------|--------|
| RegisterForm | Password | Live strength meter | ✅ Implemented |
| ExecuteTradeForm | Symbol | Debounced AI analysis (800ms) | ✅ Line 264 |
| Settings | Risk Tolerance | Real-time risk category update | ✅ Implemented |

---

## Boundary Conditions

### 1. Numeric Boundaries
| Field | Min Value | Max Value | Edge Cases to Test | Status |
|-------|-----------|-----------|-------------------|--------|
| Order Quantity | 1 | No limit | 0, negative, fractional, 1000000+ | ✅ Min enforced (line 1384) |
| Limit Price | $0.01 | No limit | $0, negative, $1000000+ | ✅ Min enforced (line 1575) |
| Paper Account Balance | $1,000 | $10,000,000 | $999, $0, $10,000,001 | ✅ Validated (line 416-421) |
| Risk Tolerance | 0% | 100% | -1%, 101% | ✅ Enforced by slider (line 1166-1167) |
| Slippage Budget | 0% | 1% | -0.1%, 1.5% | ✅ Enforced (line 1084-1085) |
| ML Training Days | 365 | 1825 | 364, 1826 | ✅ Enforced in MLTrainingDashboard |
| Backtest Days | 30 | 730 | 29, 731 | ✅ Enforced in PatternBacktestDashboard |

### 2. String Boundaries
| Field | Min Length | Max Length | Edge Cases | Status |
|-------|-----------|------------|------------|--------|
| Symbol | 1 | ~10 | Empty string, special chars, lowercase | ⚠️ No max length enforced |
| Template Name | 1 | No limit | Empty string, 100+ chars, special chars | ⚠️ No validation (line 326-328) |
| Password | 8 | No limit | 7 chars, 1000+ chars | ✅ Min enforced |
| Email | Valid format | No limit | Invalid format, 200+ chars | ⚠️ Browser-only validation |

### 3. Array/Collection Boundaries
| Data Type | Boundary Case | Expected Behavior | Status |
|-----------|---------------|-------------------|--------|
| Positions Array | Empty array | Show "No positions" message | ✅ Implemented |
| Telemetry Events | 1000+ records | Pagination or virtualization | ⚠️ Needs verification |
| News Articles | 0 articles | Show empty state | ✅ Implemented |
| Watchlist | 100+ symbols | Performance degradation? | ⚠️ Needs load testing |

### 4. Date/Time Boundaries
| Field | Constraint | Edge Case | Status |
|-------|-----------|-----------|--------|
| Options Expiration | Future dates only | Past date, today, 2+ years out | ⚠️ Backend validation assumed |
| Backtest Date Range | Historical only | Future date, missing data range | ⚠️ Backend validation |
| Session Timeout | JWT expiry | Expired token handling | ⚠️ Needs verification |

---

## Network & API Edge Cases

### 1. Slow Network
| Scenario | Expected Behavior | Status |
|----------|-------------------|--------|
| AI analysis request takes >10s | Show loading indicator, don't freeze UI | ✅ Async handling implemented |
| Order submission takes >5s | Show loading state on button, disable resubmit | ✅ Implemented |
| Account data fetch takes >8s | Display stale data + loading indicator | ⚠️ Needs verification |

### 2. Intermittent Connectivity
| Scenario | Expected Behavior | Status |
|----------|-------------------|--------|
| Request fails mid-flight | Catch error, show toast notification | ✅ Try-catch blocks present |
| WebSocket connection drops | Reconnect automatically | ⚠️ Needs verification (tradier_stream.py) |
| Multiple failed retries | Show persistent error banner with manual retry | ⚠️ No retry mechanism |

### 3. Rate Limiting
| API | Scenario | Expected Behavior | Status |
|-----|----------|-------------------|--------|
| Tradier API | 429 Too Many Requests | Show warning toast, queue requests | ⚠️ Needs implementation |
| AI Analysis | Rapid symbol lookups | Debounce requests (800ms) | ✅ Implemented (line 264) |
| Options Chain | Multiple simultaneous requests | Cancel previous request, execute latest | ⚠️ Needs verification |

### 4. Malformed Responses
| Scenario | Expected Behavior | Status |
|----------|-------------------|--------|
| Missing required fields | Handle gracefully, show error | ✅ Try-catch blocks present |
| Unexpected data types | Type validation, fallback values | ⚠️ Limited TypeScript validation |
| Empty response body | Treat as error, show appropriate message | ✅ Response.ok checks present |

---

## Race Conditions

### 1. Concurrent Data Updates
| Scenario | Risk | Mitigation | Status |
|----------|------|------------|--------|
| User changes symbol while AI analysis loading | Stale data displayed | Debounced input + cleanup in useEffect | ✅ Implemented (line 268) |
| Multiple order submissions (double-click) | Duplicate orders | Request ID deduplication | ✅ Implemented (line 451-452) |
| Settings save during background sync | Data conflict | Optimistic UI update + error rollback | ⚠️ Needs verification |

### 2. Component Lifecycle
| Scenario | Risk | Mitigation | Status |
|----------|------|------------|--------|
| Fetch completes after component unmount | Memory leak, setState warning | Cleanup function in useEffect | ⚠️ Needs audit of all components |
| Multiple rapid navigation changes | Orphaned requests | AbortController usage | ⚠️ Needs implementation |

---

## Data Format Edge Cases

### 1. Currency/Financial Data
| Data | Edge Case | Expected Display | Status |
|------|-----------|------------------|--------|
| Stock Price | $0.0001 | "$0.00" (2 decimals) | ⚠️ Needs verification |
| Stock Price | $123456.789 | "$123,456.79" (formatted) | ⚠️ Needs verification |
| P&L | -$0.005 | "-$0.01" or "$0.00"? | ⚠️ Rounding policy needed |
| Percentage | 0.12345% | "0.12%" | ⚠️ Needs verification |
| Large Numbers | $1,000,000,000+ | "$1.00B" or "$1,000,000,000"? | ⚠️ Formatting policy needed |

### 2. Symbol/Ticker Edge Cases
| Input | Expected Handling | Status |
|-------|-------------------|--------|
| Lowercase "spy" | Convert to "SPY" | ✅ toUpperCase() used (line 421) |
| Special chars "BRK.B" | Accept as valid | ⚠️ Needs validation |
| Whitespace " AAPL " | Trim whitespace | ✅ trim() used (line 421) |
| Invalid chars "AA@PL" | Reject or sanitize? | ⚠️ No validation |

### 3. Date/Time Formatting
| Data | Format | Edge Case | Status |
|------|--------|-----------|--------|
| Market Hours | HH:MM timezone | DST transitions | ⚠️ Needs verification |
| Historical Dates | YYYY-MM-DD | Timezone discrepancies | ⚠️ Backend responsibility |
| Timestamps | ISO 8601 | Client/server time skew | ⚠️ Needs verification |

---

## Critical Missing Error Handlers

### High Priority
1. **Network timeout handling** - No explicit timeout configuration in fetch calls
2. **Retry mechanism** - No automatic retry for failed API requests
3. **AbortController usage** - Requests not cancellable on component unmount
4. **Max string length validation** - Template names, user inputs have no max length
5. **Numeric overflow handling** - Very large numbers (>1B) may cause display issues

### Medium Priority
6. **Websocket reconnection logic** - Needs verification in tradier_stream.py
7. **Stale data indicators** - No visual cue when data is outdated
8. **Request deduplication** - Only implemented for order execution, not other APIs
9. **Error message consistency** - Mix of technical errors and user-friendly messages
10. **Loading state timeout** - No max duration for loading states

### Low Priority
11. **Browser compatibility warnings** - No checks for unsupported features (backdrop-filter)
12. **Performance monitoring** - No client-side error tracking beyond Sentry
13. **Input sanitization** - Limited XSS protection on user inputs

---

## Test Execution Checklist

### Loading States Testing
- [ ] Test all components with slow network (throttle to 3G)
- [ ] Verify skeleton screens appear before data loads
- [ ] Confirm loading indicators disappear after data loads
- [ ] Test timeout scenarios (>30s requests)

### Empty States Testing
- [ ] Test all data-driven components with empty arrays
- [ ] Verify empty state messages are user-friendly
- [ ] Confirm CTAs in empty states work correctly
- [ ] Test search/filter with no matching results

### Error Handling Testing
- [ ] Test with backend offline (disconnect network)
- [ ] Test with invalid API tokens
- [ ] Test with malformed API responses
- [ ] Verify error messages are actionable
- [ ] Test ErrorBoundary with intentional render errors

### Form Validation Testing
- [ ] Test all form fields with boundary values
- [ ] Test with invalid data types (strings in number fields)
- [ ] Test password strength indicator with all criteria
- [ ] Verify real-time validation debouncing

### Boundary Conditions Testing
- [ ] Test numeric inputs with min/max values
- [ ] Test string inputs with very long values (1000+ chars)
- [ ] Test with empty strings and whitespace-only strings
- [ ] Test date/time edge cases (leap years, DST transitions)

### Network Edge Cases Testing
- [ ] Test with intermittent connectivity (disconnect/reconnect)
- [ ] Test rate limiting scenarios (rapid API calls)
- [ ] Test request timeouts
- [ ] Test WebSocket reconnection

### Race Condition Testing
- [ ] Test rapid navigation between workflows
- [ ] Test double-click on submit buttons
- [ ] Test concurrent data updates
- [ ] Test component unmount during async operations

---

## Automated Testing Recommendations

### Unit Tests
```typescript
// Example test structure
describe('ExecuteTradeForm Validation', () => {
  it('should reject empty symbol', () => { /* ... */ });
  it('should reject quantity <= 0', () => { /* ... */ });
  it('should require limit price for limit orders', () => { /* ... */ });
  it('should validate options fields when asset class is option', () => { /* ... */ });
});
```

### Integration Tests
- Test full order execution flow with mocked API
- Test authentication flow with invalid credentials
- Test settings persistence across sessions

### E2E Tests (Playwright/Cypress)
- Test complete user workflows (login → trade → view positions)
- Test error recovery flows
- Test browser back/forward navigation

---

## Notes
- Most components have try-catch blocks for async operations
- Toast notification system (react-hot-toast) is consistently used
- ErrorBoundary provides app-wide error handling
- Loading states are generally well-implemented
- Major gaps: timeout handling, retry logic, request cancellation
