# Type Guards Usage Guide

This guide explains how to use the type guard utilities in `typeGuards.ts` for runtime type validation.

## Why Use Type Guards?

TypeScript provides compile-time type safety, but data from external sources (APIs, localStorage, user input) needs **runtime validation**. Type guards provide both compile-time types AND runtime checks.

## Quick Start

```typescript
import { safeJsonParse, isAlpacaPosition } from '@/lib/typeGuards';

// ❌ Unsafe - no runtime validation
const position = JSON.parse(jsonString);  // Could be anything!

// ✅ Safe - validated at runtime
const position = safeJsonParse(jsonString, isAlpacaPosition);
if (position) {
  // TypeScript knows position is AlpacaPosition
  console.log(position.symbol);
}
```

## Common Patterns

### 1. Validating API Responses

```typescript
import { isArrayOf, isAlpacaPosition } from '@/lib/typeGuards';

async function fetchPositions() {
  const response = await fetch('/api/positions');
  const data: unknown = await response.json();

  if (isArrayOf(data, isAlpacaPosition)) {
    // data is typed as AlpacaPosition[]
    return data;
  }

  throw new Error('Invalid positions data from API');
}
```

### 2. Safe localStorage Access

```typescript
import { safeLocalStorageGet, isUser } from '@/lib/typeGuards';

// Type-safe localStorage
const user = safeLocalStorageGet('user-data', isUser);
if (user) {
  // user is properly typed as User
  console.log(user.displayName);
  console.log(user.sessionCount);
} else {
  console.error('Invalid user data in localStorage');
}
```

### 3. Safe sessionStorage Access

```typescript
import { safeSessionStorageGet, isSession } from '@/lib/typeGuards';

const session = safeSessionStorageGet('current-session', isSession);
if (session) {
  // session is properly typed as Session
  console.log(session.sessionId);
}
```

### 4. WebSocket Message Validation

```typescript
import { isWebSocketMessage, isMarketData } from '@/lib/typeGuards';

ws.onmessage = (event) => {
  const data: unknown = JSON.parse(event.data);

  if (isWebSocketMessage(data)) {
    // data is typed as WebSocketMessage
    if (data.type === 'market_data' && isMarketData(data.data)) {
      // data.data is typed as MarketData
      console.log(data.data.symbol, data.data.price);
    }
  }
};
```

### 5. Custom Type Validation

```typescript
import { safeJsonParse } from '@/lib/typeGuards';

interface CustomData {
  id: number;
  name: string;
}

// Define custom type guard
function isCustomData(obj: unknown): obj is CustomData {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'id' in obj &&
    'name' in obj &&
    typeof (obj as CustomData).id === 'number' &&
    typeof (obj as CustomData).name === 'string'
  );
}

// Use with safe parser
const data = safeJsonParse(jsonString, isCustomData);
if (data) {
  // data is typed as CustomData
  console.log(data.id, data.name);
}
```

## Available Type Guards

### Alpaca API Types
- `isAlpacaAccount(obj)` - Validates AlpacaAccount
- `isAlpacaPosition(obj)` - Validates AlpacaPosition
- `isAlpacaOrder(obj)` - Validates AlpacaOrder
- `isAlpacaAsset(obj)` - Validates AlpacaAsset
- `isAlpacaBar(obj)` - Validates AlpacaBar
- `isAlpacaClock(obj)` - Validates AlpacaClock
- `isAlpacaCalendar(obj)` - Validates AlpacaCalendar
- `isAlpacaWatchlist(obj)` - Validates AlpacaWatchlist

### WebSocket Types
- `isWebSocketMessage(obj)` - Validates WebSocketMessage
- `isMarketData(obj)` - Validates MarketData
- `isPortfolioUpdate(obj)` - Validates PortfolioUpdate
- `isPositionUpdate(obj)` - Validates PositionUpdate
- `isTradingAlert(obj)` - Validates TradingAlert

### User Management Types
- `isUser(obj)` - Validates User
- `isSession(obj)` - Validates Session

### Trade History Types
- `isTradeRecord(obj)` - Validates TradeRecord
- `isStrategyPerformance(obj)` - Validates StrategyPerformance

## Utility Functions

### safeJsonParse<T>()
Safe JSON parsing with type validation.

```typescript
const user = safeJsonParse(jsonString, isUser);
// Returns User | null
```

### safeLocalStorageGet<T>()
Type-safe localStorage access.

```typescript
const data = safeLocalStorageGet('key', isUser);
// Returns User | null
```

### safeSessionStorageGet<T>()
Type-safe sessionStorage access.

```typescript
const data = safeSessionStorageGet('key', isSession);
// Returns Session | null
```

### isArrayOf<T>()
Validates array elements.

```typescript
if (isArrayOf(data, isAlpacaPosition)) {
  // data is AlpacaPosition[]
  data.forEach(pos => console.log(pos.symbol));
}
```

### isApiResponse<T>()
Validates API response structure.

```typescript
interface ApiResponse<T> {
  data: T;
  timestamp: string;
  status: 'success' | 'error';
}

if (isApiResponse(response, isAlpacaPosition)) {
  // response.data is AlpacaPosition
  console.log(response.data.symbol);
}
```

## Best Practices

### 1. Always Validate External Data
```typescript
// ❌ BAD - No validation
const user = JSON.parse(localStorage.getItem('user'));

// ✅ GOOD - Validated
const user = safeLocalStorageGet('user', isUser);
```

### 2. Use Type Guards in API Handlers
```typescript
async function fetchData() {
  const response = await fetch('/api/data');
  const data: unknown = await response.json();

  // Validate before using
  if (!isExpectedType(data)) {
    throw new Error('Invalid API response');
  }

  return data;  // Now properly typed
}
```

### 3. Handle Validation Failures Gracefully
```typescript
const user = safeLocalStorageGet('user', isUser);
if (!user) {
  // Fallback behavior
  console.warn('Invalid user data, using default');
  return defaultUser;
}
```

### 4. Combine with Error Boundaries
```typescript
try {
  const data = await fetchData();
  if (!isValidData(data)) {
    throw new TypeError('Invalid data structure');
  }
  processData(data);
} catch (error) {
  // Error boundary will catch this
  throw error;
}
```

## Performance Considerations

Type guards have minimal runtime overhead:
- Simple property checks (no loops for basic validation)
- Guards are only called when validating external data
- TypeScript removes guards in production builds (type annotations only)

## Migration Guide

### Migrating Existing Code

**Before:**
```typescript
function getUser() {
  const data = localStorage.getItem('user');
  return data ? JSON.parse(data) : null;
}
```

**After:**
```typescript
import { safeLocalStorageGet, isUser } from '@/lib/typeGuards';

function getUser() {
  return safeLocalStorageGet('user', isUser);
}
```

**Benefits:**
- Runtime type safety
- Better error handling
- TypeScript knows the return type
- Invalid data is caught early

## Troubleshooting

### "Type guard returns false for valid data"
Check that your data structure exactly matches the interface:
```typescript
// Debug the type guard
const obj = JSON.parse(data);
console.log(obj);  // Inspect structure
console.log(isUser(obj));  // See which check fails
```

### "TypeScript doesn't narrow the type"
Make sure you're using the type guard in an if statement:
```typescript
// ❌ Type not narrowed
const valid = isUser(data);
console.log(data.displayName);  // Error

// ✅ Type narrowed
if (isUser(data)) {
  console.log(data.displayName);  // OK
}
```

## Additional Resources

- [TypeScript Type Guards Documentation](https://www.typescriptlang.org/docs/handbook/2/narrowing.html#using-type-predicates)
- [Runtime Type Checking Best Practices](https://www.typescriptlang.org/docs/handbook/2/narrowing.html)
- See `frontend/lib/typeGuards.ts` for implementation details
