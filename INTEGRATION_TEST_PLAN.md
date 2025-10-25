# Integration Test Plan
**Project**: PaiiD - Personal AI Investment Dashboard  
**Date**: October 24, 2025  
**Version**: 1.0  
**Status**: Active

---

## Test Strategy

### Testing Pyramid
```
         /\
        /  \  E2E Tests (10%)
       /____\
      /      \  Integration Tests (30%)
     /________\
    /          \ Unit Tests (60%)
   /____________\
```

### Test Coverage Goals
- **Unit Tests**: 80%+ coverage on business logic
- **Integration Tests**: 100% coverage on critical API endpoints
- **E2E Tests**: 100% coverage on critical user flows

---

## Critical User Flows

### 1. Authentication Flow
**Priority**: CRITICAL  
**Test ID**: AUTH-001

**Steps**:
1. User navigates to landing page
2. User clicks "Sign Up" button
3. User enters email, password, and user details
4. User submits registration form
5. System creates account and returns session token
6. User is redirected to dashboard

**Expected Results**:
- ✅ Account created in database
- ✅ Session token stored securely
- ✅ User redirected to dashboard
- ✅ User preferences initialized

**Test Data**:
```json
{
  "email": "test@example.com",
  "password": "SecureP@ss123",
  "name": "Test User",
  "risk_tolerance": "moderate"
}
```

**API Endpoints Tested**:
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/session`

---

### 2. Dashboard Load & Data Fetch
**Priority**: CRITICAL  
**Test ID**: DASH-001

**Steps**:
1. Authenticated user lands on dashboard
2. System fetches user portfolio
3. System fetches active positions
4. System fetches market data for watchlist
5. Dashboard renders with all data

**Expected Results**:
- ✅ Portfolio data loads within 2 seconds
- ✅ Position data displays correctly
- ✅ Market data refreshes automatically
- ✅ No console errors

**API Endpoints Tested**:
- `GET /api/portfolio/{user_id}`
- `GET /api/positions/{user_id}`
- `GET /api/market-data/quotes`

---

### 3. Trade Execution Flow
**Priority**: CRITICAL  
**Test ID**: TRADE-001

**Steps**:
1. User selects "Execute Trade" workflow
2. User enters symbol, quantity, side (buy/sell)
3. System validates order parameters
4. User confirms trade
5. System submits order to broker API
6. System updates portfolio and positions

**Expected Results**:
- ✅ Order validation works correctly
- ✅ Trade executes successfully
- ✅ Portfolio updates reflect trade
- ✅ Position created/updated in database
- ✅ Trade confirmation displayed to user

**Test Data**:
```json
{
  "symbol": "AAPL",
  "quantity": 10,
  "side": "buy",
  "order_type": "market"
}
```

**API Endpoints Tested**:
- `POST /api/trading/validate`
- `POST /api/trading/execute`
- `GET /api/portfolio/{user_id}`
- `GET /api/positions/{user_id}`

---

### 4. AI Recommendations Flow
**Priority**: HIGH  
**Test ID**: AI-001

**Steps**:
1. User navigates to AI Recommendations
2. System fetches AI-generated insights
3. User views recommendation details
4. User can accept/reject recommendations
5. System tracks user decisions

**Expected Results**:
- ✅ AI insights load within 3 seconds
- ✅ Recommendations display with confidence scores
- ✅ User actions recorded correctly
- ✅ Feedback improves future recommendations

**API Endpoints Tested**:
- `GET /api/ai/recommendations`
- `POST /api/ai/feedback`
- `GET /api/ai/insights/{symbol}`

---

### 5. Position Monitoring & Real-Time Updates
**Priority**: HIGH  
**Test ID**: MONITOR-001

**Steps**:
1. User navigates to Active Positions
2. WebSocket connection established
3. Real-time price updates stream to frontend
4. P&L calculations update automatically
5. Alerts trigger on price thresholds

**Expected Results**:
- ✅ WebSocket connects successfully
- ✅ Price updates within 1 second
- ✅ P&L calculations accurate
- ✅ Alerts trigger correctly

**API Endpoints Tested**:
- `WS /ws/market-data`
- `GET /api/positions/{user_id}`
- `POST /api/alerts/create`

---

### 6. Market Research & Scanner
**Priority**: MEDIUM  
**Test ID**: RESEARCH-001

**Steps**:
1. User navigates to Market Scanner
2. User sets scan criteria (filters)
3. System queries market data
4. Results displayed with sorting/filtering
5. User adds symbols to watchlist

**Expected Results**:
- ✅ Scanner returns results within 5 seconds
- ✅ Filters apply correctly
- ✅ Results can be sorted
- ✅ Watchlist updates successfully

**API Endpoints Tested**:
- `POST /api/market-data/scan`
- `GET /api/market-data/search`
- `POST /api/watchlist/add`

---

### 7. Portfolio Analytics & Reporting
**Priority**: MEDIUM  
**Test ID**: ANALYTICS-001

**Steps**:
1. User navigates to Analytics
2. System generates performance charts
3. User selects date range
4. System calculates metrics (ROI, Sharpe ratio, etc.)
5. User exports report

**Expected Results**:
- ✅ Charts render correctly
- ✅ Metrics calculated accurately
- ✅ Date range filtering works
- ✅ Export generates valid file

**API Endpoints Tested**:
- `GET /api/analytics/performance`
- `GET /api/analytics/metrics`
- `POST /api/analytics/export`

---

### 8. Settings & Profile Management
**Priority**: MEDIUM  
**Test ID**: SETTINGS-001

**Steps**:
1. User navigates to Settings
2. User updates profile information
3. User changes API keys
4. User updates trading preferences
5. System saves changes

**Expected Results**:
- ✅ Profile updates persist
- ✅ API keys encrypted in storage
- ✅ Preferences apply immediately
- ✅ Validation prevents invalid inputs

**API Endpoints Tested**:
- `GET /api/users/{user_id}`
- `PUT /api/users/{user_id}`
- `POST /api/users/api-keys`

---

## API Endpoint Coverage

### Authentication Endpoints
| Endpoint             | Method | Test Coverage | Priority |
| -------------------- | ------ | ------------- | -------- |
| `/api/auth/register` | POST   | ✅ AUTH-001    | CRITICAL |
| `/api/auth/login`    | POST   | ✅ AUTH-001    | CRITICAL |
| `/api/auth/logout`   | POST   | ⚠️ TODO        | HIGH     |
| `/api/auth/session`  | GET    | ✅ AUTH-001    | CRITICAL |
| `/api/auth/refresh`  | POST   | ⚠️ TODO        | HIGH     |

### Trading Endpoints
| Endpoint                | Method | Test Coverage | Priority |
| ----------------------- | ------ | ------------- | -------- |
| `/api/trading/validate` | POST   | ✅ TRADE-001   | CRITICAL |
| `/api/trading/execute`  | POST   | ✅ TRADE-001   | CRITICAL |
| `/api/trading/cancel`   | POST   | ⚠️ TODO        | HIGH     |
| `/api/trading/history`  | GET    | ⚠️ TODO        | MEDIUM   |

### Portfolio Endpoints
| Endpoint                   | Method | Test Coverage           | Priority |
| -------------------------- | ------ | ----------------------- | -------- |
| `/api/portfolio/{user_id}` | GET    | ✅ DASH-001, TRADE-001   | CRITICAL |
| `/api/positions/{user_id}` | GET    | ✅ DASH-001, MONITOR-001 | CRITICAL |
| `/api/positions/{id}`      | PUT    | ⚠️ TODO                  | MEDIUM   |
| `/api/positions/{id}`      | DELETE | ⚠️ TODO                  | MEDIUM   |

### Market Data Endpoints
| Endpoint                      | Method | Test Coverage  | Priority |
| ----------------------------- | ------ | -------------- | -------- |
| `/api/market-data/quotes`     | GET    | ✅ DASH-001     | CRITICAL |
| `/api/market-data/scan`       | POST   | ✅ RESEARCH-001 | MEDIUM   |
| `/api/market-data/search`     | GET    | ✅ RESEARCH-001 | MEDIUM   |
| `/api/market-data/historical` | GET    | ⚠️ TODO         | LOW      |

### AI Endpoints
| Endpoint                    | Method | Test Coverage | Priority |
| --------------------------- | ------ | ------------- | -------- |
| `/api/ai/recommendations`   | GET    | ✅ AI-001      | HIGH     |
| `/api/ai/insights/{symbol}` | GET    | ✅ AI-001      | HIGH     |
| `/api/ai/feedback`          | POST   | ✅ AI-001      | HIGH     |
| `/api/ai/chat`              | POST   | ⚠️ TODO        | MEDIUM   |

---

## Test Data Management

### Test Users
```json
{
  "test_user_1": {
    "email": "trader@test.com",
    "password": "TestP@ss123",
    "role": "user",
    "balance": 100000
  },
  "test_user_2": {
    "email": "admin@test.com",
    "password": "AdminP@ss123",
    "role": "admin",
    "balance": 1000000
  }
}
```

### Test Positions
```json
{
  "position_1": {
    "symbol": "AAPL",
    "quantity": 10,
    "cost_basis": 150.00,
    "current_price": 155.00
  },
  "position_2": {
    "symbol": "MSFT",
    "quantity": 5,
    "cost_basis": 300.00,
    "current_price": 305.00
  }
}
```

---

## Performance Benchmarks

### API Response Times
| Endpoint Category | Target | Acceptable | Fail |
| ----------------- | ------ | ---------- | ---- |
| Authentication    | <200ms | <500ms     | >1s  |
| Data Fetch        | <500ms | <1s        | >2s  |
| Trade Execution   | <1s    | <2s        | >3s  |
| AI Insights       | <2s    | <3s        | >5s  |

### Frontend Performance
| Metric                   | Target | Acceptable | Fail  |
| ------------------------ | ------ | ---------- | ----- |
| Time to Interactive      | <2s    | <3s        | >5s   |
| First Contentful Paint   | <1s    | <1.5s      | >2s   |
| Largest Contentful Paint | <2s    | <2.5s      | >4s   |
| Cumulative Layout Shift  | <0.1   | <0.25      | >0.25 |

---

## Test Environment Setup

### Prerequisites
```bash
# Backend
- PostgreSQL database (test instance)
- Redis cache (test instance)
- API keys for external services (sandbox)

# Frontend
- Node.js 20+
- npm or yarn
- Browser testing tools (Playwright/Cypress)
```

### Environment Variables
```env
# Test environment
NODE_ENV=test
DATABASE_URL=postgresql://test:test@localhost:5432/paiid_test
REDIS_URL=redis://localhost:6379/1
API_BASE_URL=http://localhost:8000

# Test API keys (sandbox)
TRADIER_ACCESS_TOKEN=test_token
ALPHA_VANTAGE_API_KEY=test_key
ANTHROPIC_API_KEY=test_key
```

---

## Test Execution

### Running Tests

#### Unit Tests
```bash
# Frontend
cd frontend
npm run test

# Backend
cd backend
pytest tests/unit/
```

#### Integration Tests
```bash
# API Integration Tests
cd backend
pytest tests/integration/

# Frontend-Backend Integration
npm run test:integration
```

#### E2E Tests
```bash
# Playwright E2E
cd frontend
npm run playwright:test

# With UI
npm run playwright:test:headed
```

### CI/CD Integration
```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Run Unit Tests
      - name: Run Integration Tests
      - name: Run E2E Tests
      - name: Generate Coverage Report
```

---

## Manual Testing Checklist

### Pre-Release Testing
- [ ] Complete authentication flow
- [ ] Execute test trade (sandbox)
- [ ] Verify portfolio calculations
- [ ] Test AI recommendations
- [ ] Verify WebSocket connections
- [ ] Test on multiple browsers
- [ ] Test on mobile devices
- [ ] Verify all API endpoints
- [ ] Load test with 100 concurrent users
- [ ] Security penetration test

### Regression Testing
- [ ] Run full test suite after each deployment
- [ ] Verify no console errors
- [ ] Check performance benchmarks
- [ ] Validate database migrations
- [ ] Verify cache invalidation

---

## Bug Tracking

### Issue Template
```markdown
**Test ID**: [TEST-001]
**Severity**: [CRITICAL/HIGH/MEDIUM/LOW]
**Environment**: [DEV/STAGING/PROD]

**Description**:
[Clear description of the issue]

**Steps to Reproduce**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Expected Result**:
[What should happen]

**Actual Result**:
[What actually happened]

**Screenshots/Logs**:
[Attach relevant evidence]
```

---

## Test Coverage Goals

### Current Status
- Unit Tests: ⚠️ TODO
- Integration Tests: ⚠️ TODO
- E2E Tests: ⚠️ TODO

### Target (End of Batch 16)
- Unit Tests: ✅ 60% coverage
- Integration Tests: ✅ 80% coverage
- E2E Tests: ✅ 100% critical flows

---

## Success Criteria

✅ **Phase 2 Complete When**:
- All CRITICAL flows have automated tests
- All HIGH priority flows have automated tests
- Test suite runs in < 10 minutes
- All tests passing in CI/CD
- Coverage reports generated
- Performance benchmarks met

---

**Document Owner**: Dr. Cursor Claude  
**Last Updated**: October 24, 2025  
**Next Review**: After Phase 2 completion
