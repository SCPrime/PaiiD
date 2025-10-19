# CLAUDE.md - AI Code Review Standards for PaiiD Trading Platform

This file provides guidance to Claude Code Action when reviewing pull requests for the PaiiD (Personal AI Investment Dashboard) trading platform.

## Project Overview

**PaiiD** is an AI-first trading platform with real-time market data, intelligent trade execution, and a 10-stage radial workflow interface. The platform integrates with Tradier API for market data, Alpaca Paper Trading API for order execution, and Claude AI for conversational intelligence.

## CRITICAL Security & Financial Standards

### 🔴 CRITICAL: Financial Precision
- **ALL financial calculations MUST use `Decimal` types (Python) or proper decimal handling (TypeScript)**
- ❌ NEVER use `float` for money, prices, quantities, or percentages
- ❌ NEVER use floating-point arithmetic for P&L calculations
- ✅ Python: `from decimal import Decimal`
- ✅ TypeScript: Use `number` with proper rounding to 2 decimal places for display only
- Example violations:
  ```python
  # ❌ REJECT THIS
  total_value = position.qty * position.current_price

  # ✅ APPROVE THIS
  total_value = Decimal(str(position.qty)) * Decimal(str(position.current_price))
  ```

### 🔴 CRITICAL: Order Execution Atomicity
- **ALL order execution MUST be atomic with database transactions**
- ❌ NEVER allow partial order execution without rollback capability
- ❌ NEVER commit trades to database before API confirmation
- ✅ Use SQLAlchemy transactions with proper rollback on API failures
- ✅ Validate order state before and after execution
- Example violations:
  ```python
  # ❌ REJECT THIS - No transaction
  db.add(order)
  db.commit()
  alpaca.submit_order(...)

  # ✅ APPROVE THIS - Atomic with rollback
  try:
      with db.begin():
          order = Order(...)
          db.add(order)
          result = alpaca.submit_order(...)
          order.status = result.status
          db.commit()
  except Exception:
      db.rollback()
      raise
  ```

### 🔴 CRITICAL: Data Privacy & Logging
- **NEVER log sensitive financial data to console or files**
- ❌ NO account balances in logs
- ❌ NO API keys in logs (even truncated)
- ❌ NO personal information (names, emails) in logs
- ✅ Log transaction IDs, symbols, order types (non-sensitive metadata)
- ✅ Use structured logging with sanitization
- Example violations:
  ```python
  # ❌ REJECT THIS
  logger.info(f"User balance: ${account.cash}")
  logger.debug(f"API key: {api_key[:10]}...")

  # ✅ APPROVE THIS
  logger.info(f"Account updated", extra={"account_id": account.id})
  logger.debug("API authentication successful")
  ```

### 🔴 CRITICAL: SQL Injection Prevention
- **ALL database queries MUST be parameterized**
- ❌ NEVER use f-strings or string concatenation in SQL queries
- ❌ NEVER trust user input in raw SQL
- ✅ Use SQLAlchemy ORM or parameterized queries
- ✅ Validate and sanitize ALL user inputs
- Example violations:
  ```python
  # ❌ REJECT THIS
  db.execute(f"SELECT * FROM orders WHERE symbol = '{symbol}'")

  # ✅ APPROVE THIS
  db.query(Order).filter(Order.symbol == symbol).all()
  ```

## FOCUS Areas for Review

### 1. Error Handling for External APIs
- **Tradier API**, **Alpaca API**, and **Anthropic API** can fail
- ✅ MUST have try/except blocks around ALL external API calls
- ✅ MUST return user-friendly error messages (NO raw API errors to frontend)
- ✅ MUST implement retry logic with exponential backoff for transient failures
- ✅ MUST handle rate limiting (429 errors)
- Example:
  ```python
  try:
      response = tradier_client.get_quote(symbol)
      if not response or "last" not in response:
          raise ValueError(f"Invalid quote data for {symbol}")
  except requests.exceptions.RequestException as e:
      logger.error(f"Tradier API error for {symbol}: {str(e)}")
      raise HTTPException(status_code=503, detail="Market data unavailable")
  ```

### 2. Data Validation
- **ALL API inputs MUST be validated**
- ✅ Stock symbols: Uppercase, 1-5 letters, no special characters
- ✅ Quantities: Positive integers only
- ✅ Prices: Positive decimals, max 2 decimal places
- ✅ Dates: Valid ISO format, not in the past (for orders)
- ✅ Use Pydantic models for request validation
- Example:
  ```python
  class OrderRequest(BaseModel):
      symbol: str = Field(..., regex="^[A-Z]{1,5}$")
      qty: int = Field(..., gt=0, le=10000)
      side: Literal["buy", "sell"]
      type: Literal["market", "limit"]
      limit_price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
  ```

### 3. Type Safety
- **Frontend (TypeScript)**: Strict typing, NO `any` types
- **Backend (Python)**: Type hints for ALL functions
- ✅ Use TypeScript interfaces for API responses
- ✅ Use Pydantic models for request/response validation
- ❌ NO implicit type coercion
- Example violations:
  ```typescript
  // ❌ REJECT THIS
  function calculatePL(position: any): number {
      return position.qty * position.price;
  }

  // ✅ APPROVE THIS
  interface Position {
      qty: number;
      avgEntryPrice: number;
      currentPrice: number;
  }
  function calculatePL(position: Position): number {
      return position.qty * (position.currentPrice - position.avgEntryPrice);
  }
  ```

## Architecture-Specific Rules

### Frontend (Next.js 14 Pages Router)
- ✅ ALL API calls MUST go through `/api/proxy/[...path]` (NO direct backend calls)
- ✅ Use `useState` + `useEffect` for state management (NO Redux)
- ✅ All styles MUST be inline React style objects (NO CSS files, NO Tailwind)
- ✅ Components MUST be functional with TypeScript interfaces
- ❌ NO App Router patterns (this is Pages Router)
- ❌ NO server components (client-side only)

### Backend (FastAPI + SQLAlchemy)
- ✅ ALL routes MUST use dependency injection for DB sessions
- ✅ ALL routes MUST require bearer token auth (except /health)
- ✅ Use Pydantic for request/response models
- ✅ Tradier API for ALL market data (NOT Alpaca)
- ✅ Alpaca API for paper trade execution ONLY
- ❌ NO hardcoded credentials (use environment variables)
- ❌ NO synchronous blocking calls (use async/await)

### Database (PostgreSQL + SQLAlchemy)
- ✅ ALL models MUST have `created_at` and `updated_at` timestamps
- ✅ Use Alembic migrations for ALL schema changes
- ✅ Foreign keys MUST have `ondelete` behavior specified
- ❌ NO raw SQL queries (use ORM)
- ❌ NO N+1 queries (use `joinedload` or `selectinload`)

## AI Integration Standards

### Claude AI Usage
- ✅ ALL AI calls MUST go through `/api/proxy/claude/chat` endpoint
- ✅ Use `claudeAI` adapter from `frontend/lib/aiAdapter.ts`
- ✅ Set reasonable `max_tokens` limits (default 2000)
- ✅ Handle AI errors gracefully (show fallback UI, don't crash)
- ❌ NO direct Anthropic SDK calls from frontend (exposes API key)
- ❌ NO AI calls without user-facing loading states

### AI Prompt Quality
- ✅ Provide financial context in prompts (e.g., "As a financial advisor...")
- ✅ Include relevant data (positions, portfolio value, risk tolerance)
- ✅ Request structured output when parsing responses
- ❌ NO vague prompts ("analyze this stock")
- ❌ NO prompts without error handling for malformed AI responses

## Code Review Checklist

When reviewing PRs, focus on:

1. **Financial Safety**
   - [ ] No `float` used for money calculations
   - [ ] Decimal precision maintained throughout
   - [ ] Order execution is atomic

2. **Security**
   - [ ] No sensitive data in logs
   - [ ] All SQL queries parameterized
   - [ ] API keys in environment variables only
   - [ ] Bearer token auth on protected routes

3. **Error Handling**
   - [ ] Try/except around ALL external API calls
   - [ ] User-friendly error messages
   - [ ] Proper HTTP status codes
   - [ ] Frontend shows loading/error states

4. **Data Validation**
   - [ ] Pydantic models for API requests
   - [ ] TypeScript interfaces for responses
   - [ ] Input sanitization
   - [ ] Type safety (NO `any` types)

5. **Architecture Compliance**
   - [ ] Frontend uses Pages Router (NOT App Router)
   - [ ] All API calls through `/api/proxy`
   - [ ] Backend uses async/await
   - [ ] Tradier for market data, Alpaca for trades

6. **Testing**
   - [ ] Critical paths have error handling
   - [ ] Edge cases considered (empty data, API failures)
   - [ ] No hardcoded test data in production code

## Common Violations to Flag

### 🚨 HIGH SEVERITY (Block PR)
- Using `float` for financial calculations
- SQL injection vulnerabilities (non-parameterized queries)
- Logging sensitive financial data
- Missing auth on protected endpoints
- Order execution without transactions

### ⚠️ MEDIUM SEVERITY (Request changes)
- Missing error handling on API calls
- Using `any` types in TypeScript
- No input validation
- Synchronous blocking calls in backend
- Missing loading states in frontend

### 💡 LOW SEVERITY (Suggest improvements)
- Code duplication
- Missing type hints
- Suboptimal performance (N+1 queries)
- Inconsistent naming conventions
- Missing comments on complex logic

## Example Review Comments

### Approve with Suggestions ✅
```
This PR correctly uses Decimal for price calculations and implements proper error handling. Great work!

Minor suggestions:
- Consider adding a retry mechanism for the Tradier API call (line 45)
- The error message on line 78 could be more user-friendly
```

### Request Changes ⚠️
```
Please address these critical issues before merging:

1. Line 23: Using float for price calculation - MUST use Decimal
2. Line 56: SQL query is not parameterized - security risk
3. Line 89: Missing error handling for Alpaca API call
4. Line 112: Logging account balance - violates privacy standards

See CLAUDE.md for details on each requirement.
```

### Block PR 🚨
```
CRITICAL SECURITY ISSUE - Cannot merge until resolved:

Line 34: SQL injection vulnerability detected. This query uses f-string interpolation with user input.

❌ Current:
db.execute(f"SELECT * FROM orders WHERE symbol = '{symbol}'")

✅ Required:
db.query(Order).filter(Order.symbol == symbol).all()

This is a critical security violation per CLAUDE.md Section 4.
```

## Additional Resources

- Main documentation: `README.md`
- Architecture details: `CLAUDE.md` (this file is also in project root)
- Data sources: `DATA_SOURCES.md`
- Implementation status: `IMPLEMENTATION_STATUS.md`
- Frontend entry: `frontend/pages/index.tsx`
- Backend entry: `backend/app/main.py`

---

**Remember**: PaiiD is an AI-FIRST trading platform. Every feature should leverage AI to provide intelligent, personalized financial guidance. Code quality is critical because users are trusting this platform with real financial decisions (even if paper trading for now).
