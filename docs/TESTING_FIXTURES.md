# Testing Fixtures Documentation

## Overview

The PaiiD application supports deterministic testing through a comprehensive fixture system. When `USE_TEST_FIXTURES=true`, the application uses pre-defined test data instead of making external API calls, ensuring consistent and reliable test results.

## Enabling Fixture Mode

### Environment Variable

Set the environment variable to enable fixture mode:

```bash
export USE_TEST_FIXTURES=true
```

### Playwright Configuration

The Playwright configuration automatically enables fixture mode for the backend:

```typescript
// frontend/playwright.config.ts
webServer: [
  {
    command: "USE_TEST_FIXTURES=true python -m uvicorn app.main:app --port 8002",
    cwd: "../backend",
    // ...
  }
]
```

## Available Fixtures

### Options Chain Fixtures

**Location**: `backend/data/fixtures/options/`

**Symbols Available**:
- `SPY` - Large option chain for comprehensive testing
- `OPTT` - Small option chain for basic testing

**Usage**:
```typescript
// Frontend test
await page.fill('input[placeholder*="Enter symbol"]', "SPY");
await page.click('button:has-text("Load Options Chain")');
```

**API Endpoints**:
- `GET /api/options/expirations/{symbol}` - Returns fixture expiration dates
- `GET /api/options/chain/{symbol}` - Returns fixture option chain with Greeks

### Market Data Fixtures

**Location**: `backend/data/fixtures/market/`

**Symbols Available**:
- `SPY` - S&P 500 ETF
- `QQQ` - NASDAQ 100 ETF  
- `AAPL` - Apple Inc.
- `MSFT` - Microsoft Corp.

**Usage**:
```typescript
// API call returns fixture data
const response = await fetch('/api/market/quote/SPY');
const quote = await response.json();
// quote.test_fixture === true
```

**API Endpoints**:
- `GET /api/market/quote/{symbol}` - Returns fixture quote data
- `GET /api/market/quotes?symbols=SPY,QQQ` - Returns multiple fixture quotes

### Positions Fixtures

**Location**: `backend/data/fixtures/positions/`

**Sample Positions**:
- SPY position: 100 shares, entry $445, current $450.05
- AAPL position: 50 shares, entry $170, current $175.05

**API Endpoints**:
- `GET /api/positions` - Returns fixture position data

### Account Fixtures

**Location**: `backend/data/fixtures/account/`

**Sample Account**:
- Account ID: test_account_001
- Buying Power: $50,000
- Portfolio Value: $75,000

## Fixture Data Structure

### Options Chain Fixture

```json
{
  "symbol": "SPY",
  "underlying_price": 450.0,
  "expiration_dates": [
    {
      "date": "2025-11-15",
      "days_to_expiry": 23,
      "calls": [...],
      "puts": [...]
    }
  ]
}
```

### Market Quote Fixture

```json
{
  "SPY": {
    "bid": 450.0,
    "ask": 450.1,
    "last": 450.05,
    "volume": 50000000,
    "timestamp": "2025-10-23T15:30:00Z"
  }
}
```

### Position Fixture

```json
[
  {
    "id": "pos_001",
    "symbol": "SPY",
    "quantity": 100,
    "entry_price": 445.0,
    "current_price": 450.05,
    "unrealized_pnl": 505.0,
    "delta": 0.95,
    "gamma": 0.02,
    "theta": -0.15,
    "vega": 0.08,
    "rho": 0.01
  }
]
```

## Running Playwright Tests with Fixtures

### Prerequisites

1. Backend running with `USE_TEST_FIXTURES=true`
2. Frontend running on port 3000
3. Playwright installed

### Command

```bash
# From frontend directory
npx playwright test

# Run specific test file
npx playwright test market-data.spec.ts

# Run with UI mode
npx playwright test --ui
```

### Test Files

- `tests/options-chain.spec.ts` - Options chain functionality
- `tests/market-data.spec.ts` - Market data fixtures
- `tests/fixtures/options.ts` - Test symbols and data shapes

## Adding New Fixtures

### 1. Create Fixture File

```bash
# Create new options fixture
touch backend/data/fixtures/options/TSLA.json
```

### 2. Add Fixture Data

```json
{
  "symbol": "TSLA",
  "underlying_price": 250.0,
  "expiration_dates": [
    {
      "date": "2025-11-15",
      "days_to_expiry": 23,
      "calls": [...],
      "puts": [...]
    }
  ]
}
```

### 3. Update Fixture Loader

The `FixtureLoader` class automatically creates fixtures if they don't exist. For custom fixtures, add creation logic to `_ensure_fixtures_exist()`.

### 4. Update Tests

Add the new symbol to your Playwright tests:

```typescript
test("should load TSLA options chain", async ({ page }) => {
  await page.fill('input[placeholder*="Enter symbol"]', "TSLA");
  await page.click('button:has-text("Load Options Chain")');
  // ... test implementation
});
```

## Troubleshooting Fixture Issues

### Common Issues

1. **Fixture not found**: Check file path and naming convention
2. **Invalid JSON**: Validate JSON syntax in fixture files
3. **Missing symbols**: Ensure symbol is in available fixtures list

### Debug Commands

```bash
# Check fixture files exist
ls -la backend/data/fixtures/options/

# Validate JSON syntax
python -c "import json; json.load(open('backend/data/fixtures/options/spy.json'))"

# Test fixture loader directly
python -c "from backend.app.services.fixture_loader import get_fixture_loader; print(get_fixture_loader().get_available_symbols())"
```

### Logging

Enable debug logging to see fixture loading:

```python
import logging
logging.getLogger("backend.app.services.fixture_loader").setLevel(logging.DEBUG)
```

## Best Practices

### Fixture Design

1. **Realistic Data**: Use realistic market data that reflects actual trading scenarios
2. **Consistent Timestamps**: Use consistent timestamps across related fixtures
3. **Complete Data**: Include all required fields for API responses
4. **Edge Cases**: Include fixtures for edge cases (no data, errors, etc.)

### Test Organization

1. **Group by Feature**: Organize tests by feature (options, market data, positions)
2. **Use Descriptive Names**: Test names should clearly describe what they verify
3. **Independent Tests**: Each test should be independent and not rely on others
4. **Cleanup**: Tests should clean up after themselves

### Performance

1. **Minimal Fixtures**: Keep fixture files as small as possible while maintaining completeness
2. **Lazy Loading**: Fixtures are loaded on-demand to improve performance
3. **Caching**: Fixture data is cached in memory during test runs

## Integration with CI/CD

### GitHub Actions

The CI pipeline automatically runs Playwright tests with fixtures:

```yaml
# .github/workflows/ci.yml
- name: Run Playwright tests
  run: |
    cd frontend
    npx playwright test
  env:
    USE_TEST_FIXTURES: true
```

### Local Development

For local development, ensure both backend and frontend are running:

```bash
# Terminal 1: Backend with fixtures
cd backend
USE_TEST_FIXTURES=true python -m uvicorn app.main:app --port 8002

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Run tests
cd frontend
npx playwright test
```

## Monitoring and Maintenance

### Fixture Health Checks

Regularly verify fixtures are working:

```bash
# Check all fixtures load correctly
python -c "
from backend.app.services.fixture_loader import get_fixture_loader
loader = get_fixture_loader()
for symbol in loader.get_available_symbols():
    data = loader.load_options_chain(symbol)
    print(f'{symbol}: {len(data.get(\"expiration_dates\", []))} expirations')
"
```

### Updating Fixtures

When API responses change, update fixtures accordingly:

1. Capture new API response format
2. Update fixture files to match new format
3. Update tests to handle new data structure
4. Verify all tests still pass

## Conclusion

The fixture system provides a robust foundation for deterministic testing of the PaiiD application. By using pre-defined test data, tests run consistently regardless of external API availability, network conditions, or market hours.

For questions or issues with the fixture system, refer to the test files or contact the development team.
