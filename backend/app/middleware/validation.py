from datetime import datetime, time
from fastapi import HTTPException
from pydantic import Field
import re

"""
Input Validation Middleware

Provides comprehensive validation utilities for API inputs.

Phase 3: Bulletproof Reliability
"""



# Regex Patterns
SYMBOL_PATTERN = re.compile(r"^[A-Z]{1,5}$")  # 1-5 uppercase letters
REQUEST_ID_PATTERN = re.compile(r"^[a-zA-Z0-9\-_]{8,64}$")  # Alphanumeric + hyphens/underscores

def validate_symbol(symbol: str) -> str:
    """
    Validate stock symbol format.

    Rules:
    - 1-5 uppercase letters only
    - No special characters or numbers

    Raises:
        ValueError: If symbol is invalid
    """
    if not symbol:
        raise ValueError("Symbol cannot be empty")

    symbol = symbol.upper().strip()

    if not SYMBOL_PATTERN.match(symbol):
        raise ValueError(
            f"Invalid symbol '{symbol}'. Must be 1-5 uppercase letters (e.g., AAPL, SPY)"
        )

    return symbol

def validate_quantity(qty: float, min_qty: float = 0.01, max_qty: float = 10000) -> float:
    """
    Validate order quantity.

    Args:
        qty: Order quantity
        min_qty: Minimum allowed quantity (default: 0.01 for fractional shares)
        max_qty: Maximum allowed quantity (default: 10,000 shares)

    Raises:
        ValueError: If quantity is out of bounds
    """
    if qty <= 0:
        raise ValueError("Quantity must be greater than 0")

    if qty < min_qty:
        raise ValueError(f"Quantity must be at least {min_qty}")

    if qty > max_qty:
        raise ValueError(f"Quantity cannot exceed {max_qty} (safety limit)")

    return qty

def validate_side(side: str) -> str:
    """
    Validate order side (buy/sell).

    Raises:
        ValueError: If side is not 'buy' or 'sell'
    """
    side = side.lower().strip()

    if side not in ["buy", "sell"]:
        raise ValueError(f"Invalid side '{side}'. Must be 'buy' or 'sell'")

    return side

def validate_order_type(order_type: str) -> str:
    """
    Validate order type.

    Raises:
        ValueError: If order type is not supported
    """
    order_type = order_type.lower().strip()

    valid_types = ["market", "limit", "stop", "stop_limit"]

    if order_type not in valid_types:
        raise ValueError(
            f"Invalid order type '{order_type}'. Must be one of: {', '.join(valid_types)}"
        )

    return order_type

def validate_limit_price(limit_price: float | None, order_type: str) -> float | None:
    """
    Validate limit price (required for limit/stop_limit orders).

    Raises:
        ValueError: If limit price is invalid
    """
    if order_type in ["limit", "stop_limit"]:
        if limit_price is None:
            raise ValueError(f"Limit price is required for {order_type} orders")

        if limit_price <= 0:
            raise ValueError("Limit price must be greater than 0")

        if limit_price > 1000000:
            raise ValueError("Limit price cannot exceed $1,000,000")

    return limit_price

def validate_request_id(request_id: str) -> str:
    """
    Validate request ID for idempotency.

    Rules:
    - 8-64 characters
    - Alphanumeric + hyphens/underscores only

    Raises:
        ValueError: If request ID is invalid
    """
    if not request_id:
        raise ValueError("Request ID cannot be empty")

    request_id = request_id.strip()

    if not REQUEST_ID_PATTERN.match(request_id):
        raise ValueError(
            "Invalid request ID. Must be 8-64 alphanumeric characters (hyphens/underscores allowed)"
        )

    return request_id

def is_market_open() -> bool:
    """
    Check if US stock market is currently open.

    Market hours: 9:30 AM - 4:00 PM ET, Monday-Friday

    Note: This is a simple time-based check and does NOT account for:
    - Market holidays
    - Early closures
    - Pre-market/after-hours trading

    Returns:
        True if within market hours, False otherwise
    """
    now = datetime.now()

    # Check if weekend (Saturday=5, Sunday=6)
    if now.weekday() >= 5:
        return False

    # Check if within market hours (9:30 AM - 4:00 PM ET)
    # Note: This uses local time, should be converted to ET in production
    market_open = time(9, 30)
    market_close = time(16, 0)
    current_time = now.time()

    return market_open <= current_time <= market_close

def validate_market_hours(allow_after_hours: bool = False) -> None:
    """
    Validate that trading is allowed based on market hours.

    Args:
        allow_after_hours: If True, skip market hours check

    Raises:
        HTTPException: If market is closed and after-hours trading not allowed
    """
    if not allow_after_hours and not is_market_open():
        raise HTTPException(
            status_code=400,
            detail="Market is currently closed. Trading hours: 9:30 AM - 4:00 PM ET, Monday-Friday",
        )

# Pydantic Field Validators (use with Field() in models)

def symbol_field(description: str = "Stock symbol") -> Field:
    """Create a validated symbol field for Pydantic models"""
    return Field(
        ...,
        description=description,
        min_length=1,
        max_length=5,
        pattern=r"^[A-Z]{1,5}$",
        examples=["AAPL", "SPY", "TSLA"],
    )

def quantity_field(min_value: float = 0.01, max_value: float = 10000) -> Field:
    """Create a validated quantity field for Pydantic models"""
    return Field(
        ...,
        description="Order quantity (shares)",
        gt=0,
        ge=min_value,
        le=max_value,
        examples=[100, 10.5, 1],
    )

def price_field(description: str = "Price") -> Field:
    """Create a validated price field for Pydantic models"""
    return Field(..., description=description, gt=0, le=1000000, examples=[150.50, 50.00, 1000.00])

__all__ = [
    "is_market_open",
    "price_field",
    "quantity_field",
    "symbol_field",
    "validate_limit_price",
    "validate_market_hours",
    "validate_order_type",
    "validate_quantity",
    "validate_request_id",
    "validate_side",
    "validate_symbol",
]
