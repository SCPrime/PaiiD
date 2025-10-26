# Secure Logging Quick Reference Guide

## Overview

PaiiD uses a secure logging system that automatically redacts sensitive data and provides request correlation IDs for tracing.

---

## Quick Start

### 1. Import Secure Logger

```python
from app.core.logging_utils import get_secure_logger, format_user_for_logging

logger = get_secure_logger(__name__)
```

### 2. Log Messages with Context

```python
# Good - structured logging with context
logger.info("User action", user_id=user.id, action="trade", symbol="AAPL")

# Good - error with details
logger.error(
    "API call failed",
    endpoint="/api/market/quote",
    error_type=type(e).__name__,
    error_msg=str(e)
)

# Good - user info (redacted automatically)
logger.info("User login", user=format_user_for_logging(user))
```

---

## What Gets Redacted Automatically

The secure logger automatically redacts:

- ✅ `password` → `"***"`
- ✅ `api_key` → `"***"`
- ✅ `secret` → `"***"`
- ✅ `token` → `"***"`
- ✅ `authorization` → `"***"`
- ✅ `bearer` → `"***"`
- ✅ `ssn` → `"***"`
- ✅ `credit_card` → `"***"`
- ✅ Authorization headers → `"Bearer rnd_bDR*** (12 chars)"`

---

## DO ✅ and DON'T ❌

### User Objects

```python
# ❌ DON'T - logs entire user object
logger.info(f"User logged in: {user}")

# ✅ DO - use format_user_for_logging()
logger.info("User logged in", user=format_user_for_logging(user))
# Output: user=user_id=1, email=user@example.com, role=owner
```

### Tokens and API Keys

```python
# ❌ DON'T - exposes token
logger.debug(f"Token: {token}")

# ✅ DO - log only metadata
logger.debug("Token received", token_length=len(token))

# ✅ DO - use redact_auth_header()
from app.core.logging_utils import redact_auth_header
logger.debug("Auth header", header=redact_auth_header(authorization))
# Output: header=Bearer rnd_bDR*** (40 chars)
```

### Errors and Exceptions

```python
# ❌ DON'T - may expose sensitive data in exception message
logger.error(f"Error: {str(e)}")

# ✅ DO - separate error type and message
logger.error(
    "Database operation failed",
    error_type=type(e).__name__,
    error_msg=str(e),
    exc_info=True  # Adds stack trace
)
```

### Request Data

```python
# ❌ DON'T - may contain passwords or tokens
logger.info(f"Request data: {request_data}")

# ✅ DO - redaction happens automatically
from app.core.logging_utils import redact_sensitive_data
safe_data = redact_sensitive_data(request_data)
logger.info("Request received", data=safe_data)
```

---

## Log Levels

Use appropriate log levels:

```python
# DEBUG - Development/troubleshooting info
logger.debug("Cache hit", key="positions:AAPL", ttl=30)

# INFO - Normal application flow
logger.info("Trade executed", symbol="AAPL", quantity=10, price=175.50)

# WARNING - Something unexpected but not critical
logger.warning("High latency detected", endpoint="/api/market", latency_ms=2500)

# ERROR - Something failed but app continues
logger.error("Failed to fetch quote", symbol="INVALID", error_msg="Symbol not found")

# CRITICAL - System-level failure
logger.critical("Database connection lost", error_type="ConnectionError")
```

---

## Correlation IDs

Every request automatically gets a unique correlation ID:

### In Logs
```
[abc-123-def-456] User login | user_id=1
[abc-123-def-456] Fetching positions | user_id=1
[abc-123-def-456] Retrieved positions | count=5
```

### In Code
```python
from app.core.logging_utils import get_correlation_id

# Get current request ID
request_id = get_correlation_id()
logger.info("Processing", request_id=request_id)
```

### In HTTP Responses
All responses include `X-Request-ID` header for client-side tracing.

---

## Common Patterns

### API Endpoint Logging

```python
@router.get("/market/{symbol}")
async def get_market_data(symbol: str, current_user: User = Depends(...)):
    logger.debug("Market data request", symbol=symbol, user_id=current_user.id)

    try:
        data = fetch_data(symbol)
        logger.info("Market data retrieved", symbol=symbol, price=data.price)
        return data
    except Exception as e:
        logger.error(
            "Failed to fetch market data",
            symbol=symbol,
            error_type=type(e).__name__,
            error_msg=str(e),
            exc_info=True
        )
        raise
```

### Database Operations

```python
try:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning("User not found", user_id=user_id)
        return None

    logger.debug("User fetched", user=format_user_for_logging(user))
    return user
except Exception as e:
    logger.error(
        "Database query failed",
        table="users",
        user_id=user_id,
        error_type=type(e).__name__,
        error_msg=str(e)
    )
    raise
```

### External API Calls

```python
try:
    response = tradier_client.get_quote(symbol)
    logger.info("External API success", provider="Tradier", symbol=symbol)
except Exception as e:
    logger.error(
        "External API failed",
        provider="Tradier",
        endpoint="get_quote",
        symbol=symbol,
        error_type=type(e).__name__,
        error_msg=str(e)
    )
    # Try fallback
```

---

## Migration Guide

### Old Style → New Style

```python
# OLD - standard logger
import logging
logger = logging.getLogger(__name__)
logger.info(f"User {user.email} logged in")

# NEW - secure logger
from app.core.logging_utils import get_secure_logger, format_user_for_logging
logger = get_secure_logger(__name__)
logger.info("User logged in", user=format_user_for_logging(user))
```

### Removing Emojis

```python
# OLD - emoji-based logging
logger.info(f"✅ Retrieved stock info for {symbol}")
logger.error(f"❌ Tradier API failed: {e}")

# NEW - clear text
logger.info("Retrieved stock info", symbol=symbol)
logger.error("Tradier API failed", error_type=type(e).__name__)
```

### Removing Print Statements

```python
# OLD - debug prints
print(f"Token: {token}", flush=True)
print(f"[AUTH] Match: {token == settings.API_TOKEN}", flush=True)

# NEW - secure logging
logger.debug("Token received", token_length=len(token))
logger.debug("Auth check passed")
```

---

## Testing Your Logs

### Check for Sensitive Data

```python
from app.core.logging_utils import redact_sensitive_data

# Test redaction
data = {
    "username": "john@example.com",
    "password": "secret123",
    "api_key": "abc123xyz"
}

safe_data = redact_sensitive_data(data)
print(safe_data)
# {'username': 'john@example.com', 'password': '***', 'api_key': '***'}
```

### Verify Correlation ID

```python
from app.core.logging_utils import get_correlation_id

# Should return request ID (or None if outside request context)
request_id = get_correlation_id()
print(f"Current request: {request_id}")
```

---

## Performance Considerations

The secure logger has minimal overhead:
- Redaction only happens when logging (lazy evaluation)
- Context variables are thread-safe
- No impact on production performance

---

## Need Help?

- **Security Question:** Contact security team before logging any user data
- **Implementation Question:** See examples in `backend/app/routers/users.py`
- **Bug Report:** Include correlation ID from `X-Request-ID` header

---

**Last Updated:** 2025-10-26
**Version:** 1.0
