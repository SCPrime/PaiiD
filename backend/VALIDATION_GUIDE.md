# Input Validation Quick Reference Guide

This guide provides examples of how to use the validation utilities created in BATCH 2B.

## Import Statements

```python
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from pydantic import BaseModel, Field, field_validator
from ..core.validators import InputSanitizer, SymbolValidator, NumericValidator, TextValidator
```

---

## Common Validation Patterns

### 1. Stock Symbol Validation

**Path Parameter**:
```python
@router.get("/quote/{symbol}")
async def get_quote(
    symbol: str = Path(..., min_length=1, max_length=10, pattern="^[A-Z0-9$.:^-]+$")
):
    symbol = InputSanitizer.normalize_symbol(symbol)
    # ... rest of endpoint
```

**Pydantic Model**:
```python
class TradeRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10)

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, v: str) -> str:
        return InputSanitizer.normalize_symbol(v)
```

---

### 2. Text Input Sanitization

**Short Text (Names, Titles)**:
```python
class ArticleRequest(BaseModel):
    title: str = Field(..., max_length=255)

    @field_validator("title")
    @classmethod
    def sanitize_title(cls, v: str) -> str:
        return InputSanitizer.sanitize_text(v)
```

**Long Text (Descriptions, Reasoning)**:
```python
class RecommendationRequest(BaseModel):
    reasoning: str = Field(..., max_length=5000)

    @field_validator("reasoning")
    @classmethod
    def sanitize_reasoning(cls, v: str) -> str:
        return InputSanitizer.sanitize_text(v)
```

---

### 3. Numeric Range Validation

**Prices (Must be positive)**:
```python
class OrderRequest(BaseModel):
    entry_price: float = Field(..., gt=0)
    stop_loss: float | None = Field(None, gt=0)
    take_profit: float | None = Field(None, gt=0)
```

**Percentages (0-100)**:
```python
class RiskRequest(BaseModel):
    risk_tolerance: float = Field(..., ge=0, le=100)
    position_size_percent: float = Field(..., ge=1, le=100)
```

**Confidence Scores (0-1)**:
```python
class SignalResponse(BaseModel):
    confidence: float = Field(..., ge=0.0, le=1.0)
```

**Quantities**:
```python
class TradeRequest(BaseModel):
    quantity: int = Field(..., gt=0, le=10000)
    max_positions: int = Field(1, ge=1, le=10)
```

---

### 4. Email Validation

```python
from pydantic import EmailStr

class UserRegister(BaseModel):
    email: EmailStr

    @field_validator("email")
    @classmethod
    def sanitize_email(cls, v: str) -> str:
        return InputSanitizer.sanitize_email(v)
```

---

### 5. Password Validation

```python
class UserRegister(BaseModel):
    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        return v
```

---

### 6. Query Parameter Validation

**Pagination**:
```python
@router.get("/items")
async def get_items(
    limit: int = Query(50, ge=1, le=200, description="Number of items"),
    offset: int = Query(0, ge=0, description="Starting offset")
):
    # ... endpoint logic
```

**Date Range**:
```python
@router.get("/history")
async def get_history(
    lookback_days: int = Query(30, ge=1, le=365, description="Days to look back")
):
    # ... endpoint logic
```

**Enum Validation**:
```python
from typing import Literal

@router.get("/data")
async def get_data(
    timeframe: str = Query("daily", pattern="^(1Min|5Min|15Min|1Hour|1Day|daily|weekly|monthly)$")
):
    # ... endpoint logic
```

---

### 7. List Input Validation

**Fixed Size Lists**:
```python
class BatchRequest(BaseModel):
    symbols: list[str] = Field(..., min_length=1, max_length=10)

    @field_validator("symbols")
    @classmethod
    def normalize_symbols(cls, v: list[str]) -> list[str]:
        return [InputSanitizer.normalize_symbol(s) for s in v]
```

**Message Lists**:
```python
class ChatRequest(BaseModel):
    messages: list[Message] = Field(..., min_length=1, max_length=50)
```

---

### 8. Optional Fields with Validation

```python
class RecommendationRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10)
    target_price: float | None = Field(None, gt=0)
    reasoning: str | None = Field(None, max_length=5000)

    @field_validator("reasoning")
    @classmethod
    def sanitize_reasoning(cls, v: str | None) -> str | None:
        if v:
            return InputSanitizer.sanitize_text(v)
        return v
```

---

### 9. Pattern Matching

**Stock Symbol Pattern**:
```python
symbol: str = Field(..., pattern="^[A-Z0-9$.:^-]+$")
```

**Role Pattern (user/assistant)**:
```python
role: str = Field(..., pattern="^(user|assistant)$")
```

**Model Name Pattern**:
```python
model: str = Field("claude-sonnet-4-5-20250929", pattern="^claude-.*")
```

---

### 10. Custom Validators

**Multiple Field Validation**:
```python
class TradeRequest(BaseModel):
    entry_price: float = Field(..., gt=0)
    stop_loss: float = Field(..., gt=0)
    take_profit: float = Field(..., gt=0)

    @field_validator("stop_loss")
    @classmethod
    def validate_stop_loss(cls, v: float, info) -> float:
        if 'entry_price' in info.data:
            if v >= info.data['entry_price']:
                raise ValueError("Stop loss must be below entry price")
        return v
```

---

## InputSanitizer Methods

### sanitize_text(value: str) -> str
- Strips whitespace
- HTML escapes special characters
- Removes null bytes

**Example**:
```python
input = "<script>alert('xss')</script>"
output = InputSanitizer.sanitize_text(input)
# output: "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"
```

### normalize_symbol(value: str) -> str
- Uppercase
- Strip whitespace
- Remove invalid characters
- Max 10 characters

**Example**:
```python
input = "  aapl  "
output = InputSanitizer.normalize_symbol(input)
# output: "AAPL"
```

### sanitize_email(value: str) -> str
- Strip whitespace
- Lowercase

**Example**:
```python
input = "  USER@EXAMPLE.COM  "
output = InputSanitizer.sanitize_email(input)
# output: "user@example.com"
```

---

## Error Handling

Pydantic validation errors are automatically caught by FastAPI and return 422 status code:

```json
{
  "detail": [
    {
      "type": "greater_than",
      "loc": ["body", "entry_price"],
      "msg": "Input should be greater than 0",
      "input": -10.5
    }
  ]
}
```

---

## Best Practices

1. **Always validate at the edge** - Use Pydantic models for all POST/PUT requests
2. **Sanitize early** - Apply sanitization in field validators
3. **Use descriptive constraints** - Add descriptions to Field() for API docs
4. **Normalize consistently** - Use InputSanitizer methods across all routers
5. **Test edge cases** - Verify validation with empty strings, null bytes, XSS attempts
6. **Document patterns** - Use pattern parameter for regex validation
7. **Limit list sizes** - Always add min/max length to list fields
8. **Use Literal types** - For enum-like fields (buy/sell, low/medium/high)

---

## Testing Validation

### Manual Testing Examples

```bash
# Test symbol validation
curl -X POST http://localhost:8001/api/recommendations/save \
  -H "Content-Type: application/json" \
  -d '{"symbol": "<script>", "recommendation_type": "buy", "confidence_score": 75}'
# Expected: 422 error

# Test price validation
curl -X POST http://localhost:8001/api/recommendations/save \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "recommendation_type": "buy", "confidence_score": 75, "suggested_entry_price": -10}'
# Expected: 422 error (price must be > 0)

# Test confidence validation
curl -X POST http://localhost:8001/api/recommendations/save \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "recommendation_type": "buy", "confidence_score": 150}'
# Expected: 422 error (confidence must be 0-100)
```

---

## Migration Checklist

When adding validation to a new endpoint:

- [ ] Import Field and field_validator from pydantic
- [ ] Import InputSanitizer from core.validators
- [ ] Add Field constraints to all parameters
- [ ] Add custom validators for symbols
- [ ] Add sanitization for text inputs
- [ ] Add range validation for numbers
- [ ] Test with invalid inputs
- [ ] Update API documentation

---

## References

- Pydantic Documentation: https://docs.pydantic.dev/
- FastAPI Validation: https://fastapi.tiangolo.com/tutorial/body-fields/
- OWASP XSS Prevention: https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html
