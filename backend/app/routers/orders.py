import logging
from datetime import UTC, datetime

import requests
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from ..core.config import settings
from ..core.idempotency import check_and_store
from ..core.jwt import get_current_user
from ..core.kill_switch import is_killed, set_kill
from ..db.session import get_db
from ..middleware.validation import (
    validate_limit_price,
    validate_order_type,
    validate_quantity,
    validate_request_id,
    validate_side,
    validate_symbol,
)
from ..models.database import OrderTemplate, User


logger = logging.getLogger(__name__)

router = APIRouter()

# Alpaca API configuration
ALPACA_BASE_URL = "https://paper-api.alpaca.markets"  # Paper trading


def get_alpaca_headers():
    """Get headers for Alpaca API requests"""
    return {
        "APCA-API-KEY-ID": settings.ALPACA_API_KEY,
        "APCA-API-SECRET-KEY": settings.ALPACA_SECRET_KEY,
    }


# Circuit Breaker for Alpaca API (Phase 3: Bulletproof Reliability)
class AlpacaCircuitBreaker:
    """
    Circuit breaker pattern to prevent hammering Alpaca API when it's down.

    States:
    - CLOSED: Normal operation
    - OPEN: Alpaca is failing, block requests for cooldown period
    - HALF_OPEN: Testing if Alpaca recovered
    """

    def __init__(self, failure_threshold: int = 3, cooldown_seconds: int = 60):
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self.failure_count = 0
        self.last_failure_time: datetime | None = None
        self.state = "CLOSED"

    def record_success(self):
        """Record successful call - reset circuit"""
        self.failure_count = 0
        self.state = "CLOSED"
        self.last_failure_time = None
        logger.info("[Alpaca Circuit] CLOSED - Normal operation")

    def record_failure(self):
        """Record failed call - increment counter and potentially open circuit"""
        self.failure_count += 1
        self.last_failure_time = datetime.now(UTC)

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(
                f"[Alpaca Circuit] OPENED after {self.failure_count} failures. "
                f"Cooldown: {self.cooldown_seconds}s"
            )

    def is_available(self) -> bool:
        """Check if requests should be allowed"""
        if self.state == "CLOSED":
            return True

        if self.state == "OPEN":
            # Check if cooldown period has elapsed
            if self.last_failure_time:
                elapsed = (datetime.now(UTC) - self.last_failure_time).total_seconds()
                if elapsed >= self.cooldown_seconds:
                    # Move to HALF_OPEN to test Alpaca
                    self.state = "HALF_OPEN"
                    logger.info("[Alpaca Circuit] HALF_OPEN - testing Alpaca API")
                    return True
            return False

        # HALF_OPEN state - allow one test request
        return True


# Global circuit breaker instance
alpaca_circuit_breaker = AlpacaCircuitBreaker(failure_threshold=3, cooldown_seconds=60)


# Order Model (must be defined before use in function signatures)
class Order(BaseModel):
    """Order model with comprehensive validation (supports stocks and options)"""

    symbol: str = Field(
        ...,
        min_length=1,
        max_length=5,
        pattern=r"^[A-Z]{1,5}$",
        description="Stock symbol (1-5 uppercase letters)",
        examples=["AAPL", "SPY"],
    )
    side: str = Field(..., pattern=r"^(buy|sell)$", description="Order side: 'buy' or 'sell'")
    qty: float = Field(
        ...,
        gt=0,
        le=10000,
        description="Order quantity (0.01 to 10,000 shares/contracts)",
    )
    type: str = Field(
        default="market",
        pattern=r"^(market|limit|stop|stop_limit)$",
        description="Order type",
    )
    limit_price: float | None = Field(
        default=None,
        gt=0,
        le=1000000,
        description="Limit price (required for limit/stop_limit orders)",
    )

    # Options-specific fields
    asset_class: str = Field(
        default="stock",
        pattern=r"^(stock|option)$",
        description="Asset class: 'stock' or 'option'",
    )
    option_type: str | None = Field(
        default=None,
        pattern=r"^(call|put)$",
        description="Option type: 'call' or 'put' (required for options)",
    )
    strike_price: float | None = Field(
        default=None, gt=0, le=100000, description="Strike price (required for options)"
    )
    expiration_date: str | None = Field(
        default=None,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Expiration date in YYYY-MM-DD format (required for options)",
    )

    @field_validator("symbol")
    @classmethod
    def validate_symbol_format(cls, v, info=None):
        """Validate and normalize symbol"""
        return validate_symbol(v)

    @field_validator("side")
    @classmethod
    def validate_side_value(cls, v, info=None):
        """Validate order side"""
        return validate_side(v)

    @field_validator("qty")
    @classmethod
    def validate_quantity_value(cls, v, info=None):
        """Validate order quantity"""
        return validate_quantity(v)

    @field_validator("type")
    @classmethod
    def validate_order_type_value(cls, v, info=None):
        """Validate order type"""
        return validate_order_type(v)

    @field_validator("limit_price", mode="before")
    @classmethod
    def validate_limit_price_value(cls, v, info=None):
        """Validate limit price based on order type"""
        order_type = info.data.get("type", "market")
        return validate_limit_price(v, order_type)

    @field_validator("option_type", mode="before")
    @classmethod
    def validate_option_type_required(cls, v, info=None):
        """Validate that option_type is provided for options orders"""
        asset_class = info.data.get("asset_class", "stock")
        if asset_class == "option" and not v:
            raise ValueError("option_type is required for options orders (call or put)")
        return v

    @field_validator("strike_price", mode="before")
    @classmethod
    def validate_strike_price_required(cls, v, info=None):
        """Validate that strike_price is provided for options orders"""
        asset_class = info.data.get("asset_class", "stock")
        if asset_class == "option" and not v:
            raise ValueError("strike_price is required for options orders")
        return v

    @field_validator("expiration_date", mode="before")
    @classmethod
    def validate_expiration_date_required(cls, v, info=None):
        """Validate that expiration_date is provided for options orders"""
        asset_class = info.data.get("asset_class", "stock")
        if asset_class == "option" and not v:
            raise ValueError("expiration_date is required for options orders (YYYY-MM-DD format)")
        return v


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(
        (requests.exceptions.ConnectionError, requests.exceptions.Timeout)
    ),
    before_sleep=before_sleep_log(logger, logging.WARNING),
)
def execute_alpaca_order_with_retry(order: Order) -> dict:
    """
    Execute order on Alpaca with retry logic and circuit breaker.

    Retries: 3 attempts with exponential backoff (1s, 2s, 4s)
    Circuit Breaker: Opens after 3 consecutive failures, cooldown 60s

    Returns:
        Alpaca order response dict

    Raises:
        HTTPException: If all retries fail or circuit breaker is open
    """
    # Check circuit breaker
    if not alpaca_circuit_breaker.is_available():
        logger.error("[Alpaca Circuit] Circuit is OPEN - refusing request")
        raise HTTPException(
            status_code=503,
            detail="Alpaca API temporarily unavailable. Please try again later.",
        )

    try:
        # Build order payload based on asset class
        order_payload = {
            "symbol": order.symbol,
            "qty": order.qty,
            "side": order.side,
            "type": order.type,
            "time_in_force": "day",
        }

        # For options orders, construct option symbol and set class
        if order.asset_class == "option":
            # Alpaca options symbol format: SPY251219C00450000
            # Format: SYMBOL + YYMMDD + C/P + 00000000 (strike * 1000, 8 digits)
            from datetime import datetime

            expiry_dt = datetime.strptime(order.expiration_date, "%Y-%m-%d")
            expiry_str = expiry_dt.strftime("%y%m%d")  # YYMMDD
            call_put = "C" if order.option_type == "call" else "P"
            strike_int = int(order.strike_price * 1000)
            option_symbol = f"{order.symbol}{expiry_str}{call_put}{strike_int:08d}"

            order_payload["symbol"] = option_symbol
            order_payload["class"] = "option"

            logger.info(
                f"[Alpaca] Submitting OPTIONS order: {option_symbol} "
                f"({order.symbol} ${order.strike_price} {order.option_type} exp:{order.expiration_date})"
            )
        else:
            logger.info(f"[Alpaca] Submitting STOCK order: {order.symbol} {order.qty} {order.side}")

        # Execute order via Alpaca API
        response = requests.post(
            f"{ALPACA_BASE_URL}/v2/orders",
            headers=get_alpaca_headers(),
            json=order_payload,
            timeout=10,
        )
        response.raise_for_status()

        # Success - reset circuit breaker
        alpaca_circuit_breaker.record_success()

        return response.json()

    except requests.exceptions.RequestException as e:
        # Record failure in circuit breaker
        alpaca_circuit_breaker.record_failure()

        logger.error(
            f"[Alpaca] Order execution failed for {order.symbol}: {e} "
            f"(Circuit: {alpaca_circuit_breaker.state})"
        )

        # Re-raise for retry logic (if retryable exception)
        if isinstance(e, (requests.exceptions.ConnectionError, requests.exceptions.Timeout)):
            raise

        # For non-retryable errors (4xx, 5xx), fail immediately
        raise HTTPException(
            status_code=500, detail=f"Failed to execute order for {order.symbol}: {e!s}"
        )


class ExecRequest(BaseModel):
    """Execute order request with idempotency and validation"""

    dryRun: bool = Field(default=True, description="Dry run mode (no actual execution)")
    requestId: str = Field(
        ...,
        min_length=8,
        max_length=64,
        pattern=r"^[a-zA-Z0-9\-_]{8,64}$",
        description="Unique request ID for idempotency (8-64 alphanumeric + hyphens/underscores)",
    )
    orders: list[Order] = Field(
        ...,
        min_items=1,
        max_items=10,
        description="List of orders to execute (max 10 per request)",
    )

    @field_validator("requestId")
    @classmethod
    def validate_request_id_format(cls, v, info=None):
        """Validate request ID format"""
        return validate_request_id(v)

    @field_validator("orders")
    @classmethod
    def validate_orders_list(cls, v, info=None):
        """Validate orders list"""
        if not v:
            raise ValueError("At least one order is required")
        if len(v) > 10:
            raise ValueError("Cannot execute more than 10 orders per request (safety limit)")
        return v


@router.post("/trading/execute")
async def execute(
    request: Request, req: ExecRequest, current_user: User = Depends(get_current_user)
):
    """
    Execute trading orders with idempotency and dry-run support.

    NOTE: Rate limiting disabled temporarily due to Redis dependency issues.
    Will re-enable once Redis is properly configured.
    """
    try:
        logger.info(f"[Trading Execute] Received request: {req.requestId}")

        if not req.requestId:
            raise HTTPException(status_code=400, detail="requestId required")

        if not check_and_store(req.requestId):
            logger.info(f"[Trading Execute] Duplicate request: {req.requestId}")
            return {"accepted": False, "duplicate": True}

        if is_killed():
            raise HTTPException(status_code=status.HTTP_423_LOCKED, detail="trading halted")

        # Respect LIVE_TRADING setting
        if req.dryRun or not settings.LIVE_TRADING:
            logger.info(f"[Trading Execute] Dry-run mode: {len(req.orders)} orders")
            return {
                "accepted": True,
                "dryRun": True,
                "orders": [o.dict() for o in req.orders],
            }

        # Execute real trades via Alpaca API with circuit breaker and retry logic
        logger.info(f"[Trading Execute] Executing {len(req.orders)} live orders")
        executed_orders = []
        for order in req.orders:
            # Use new circuit breaker + retry function (handles all error cases)
            alpaca_order = execute_alpaca_order_with_retry(order)
            executed_orders.append(
                {
                    **order.dict(),
                    "alpaca_order_id": alpaca_order.get("id"),
                    "status": alpaca_order.get("status"),
                }
            )

        return {"accepted": True, "dryRun": False, "orders": executed_orders}

    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.error(
            f"[Trading Execute] UNEXPECTED ERROR: {type(e).__name__}: {e!s}",
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=f"Internal server error: {e!s}")


@router.post("/admin/kill")
def kill(state: bool, current_user: User = Depends(get_current_user)):
    set_kill(state)
    return {"tradingHalted": state}


# Order Template Models with Validation
class OrderTemplateCreate(BaseModel):
    """Create order template with validation"""

    name: str = Field(..., min_length=1, max_length=100, description="Template name")
    description: str | None = Field(None, max_length=500, description="Template description")
    symbol: str = Field(
        ...,
        min_length=1,
        max_length=5,
        pattern=r"^[A-Z]{1,5}$",
        description="Stock symbol",
    )
    side: str = Field(..., pattern=r"^(buy|sell)$", description="Order side")
    quantity: float = Field(..., gt=0, le=10000, description="Order quantity")
    order_type: str = Field(
        default="market",
        pattern=r"^(market|limit|stop|stop_limit)$",
        description="Order type",
    )
    limit_price: float | None = Field(None, gt=0, le=1000000, description="Limit price")

    @field_validator("symbol")
    @classmethod
    def validate_symbol_format(cls, v, info=None):
        return validate_symbol(v)

    @field_validator("side")
    @classmethod
    def validate_side_value(cls, v, info=None):
        return validate_side(v)

    @field_validator("quantity")
    @classmethod
    def validate_quantity_value(cls, v, info=None):
        return validate_quantity(v)

    @field_validator("order_type")
    @classmethod
    def validate_order_type_value(cls, v, info=None):
        return validate_order_type(v)

    @field_validator("limit_price", mode="before")
    @classmethod
    def validate_limit_price_value(cls, v, info=None):
        order_type = info.data.get("order_type", "market")
        return validate_limit_price(v, order_type)


class OrderTemplateUpdate(BaseModel):
    """Update order template with validation"""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    symbol: str | None = Field(None, min_length=1, max_length=5, pattern=r"^[A-Z]{1,5}$")
    side: str | None = Field(None, pattern=r"^(buy|sell)$")
    quantity: float | None = Field(None, gt=0, le=10000)
    order_type: str | None = Field(None, pattern=r"^(market|limit|stop|stop_limit)$")
    limit_price: float | None = Field(None, gt=0, le=1000000)

    @field_validator("symbol")
    @classmethod
    def validate_symbol_format(cls, v, info=None):
        if v is not None:
            return validate_symbol(v)
        return v

    @field_validator("side")
    @classmethod
    def validate_side_value(cls, v, info=None):
        if v is not None:
            return validate_side(v)
        return v

    @field_validator("quantity")
    @classmethod
    def validate_quantity_value(cls, v, info=None):
        if v is not None:
            return validate_quantity(v)
        return v

    @field_validator("order_type")
    @classmethod
    def validate_order_type_value(cls, v, info=None):
        if v is not None:
            return validate_order_type(v)
        return v


class OrderTemplateResponse(BaseModel):
    id: int
    user_id: int | None
    name: str
    description: str | None
    symbol: str
    side: str
    quantity: float
    order_type: str
    limit_price: float | None
    created_at: datetime
    updated_at: datetime
    last_used_at: datetime | None

    class Config:
        from_attributes = True


# Order Template CRUD Endpoints
@router.post(
    "/order-templates",
    response_model=OrderTemplateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_order_template(
    template: OrderTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new order template"""
    db_template = OrderTemplate(
        name=template.name,
        description=template.description,
        symbol=template.symbol.upper(),
        side=template.side,
        quantity=template.quantity,
        order_type=template.order_type,
        limit_price=template.limit_price,
        user_id=None,  # For now, templates are global (not user-specific)
    )
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


@router.get("/order-templates", response_model=list[OrderTemplateResponse])
def list_order_templates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all order templates"""
    templates = db.query(OrderTemplate).offset(skip).limit(limit).all()
    return templates


@router.get("/order-templates/{template_id}", response_model=OrderTemplateResponse)
def get_order_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific order template by ID"""
    template = db.query(OrderTemplate).filter(OrderTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Order template not found")
    return template


@router.put("/order-templates/{template_id}", response_model=OrderTemplateResponse)
def update_order_template(
    template_id: int,
    template_update: OrderTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing order template"""
    db_template = db.query(OrderTemplate).filter(OrderTemplate.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Order template not found")

    # Update fields if provided
    if template_update.name is not None:
        db_template.name = template_update.name
    if template_update.description is not None:
        db_template.description = template_update.description
    if template_update.symbol is not None:
        db_template.symbol = template_update.symbol.upper()
    if template_update.side is not None:
        db_template.side = template_update.side
    if template_update.quantity is not None:
        db_template.quantity = template_update.quantity
    if template_update.order_type is not None:
        db_template.order_type = template_update.order_type
    if template_update.limit_price is not None:
        db_template.limit_price = template_update.limit_price

    db_template.updated_at = datetime.now(UTC)
    db.commit()
    db.refresh(db_template)
    return db_template


@router.delete("/order-templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an order template"""
    db_template = db.query(OrderTemplate).filter(OrderTemplate.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Order template not found")

    db.delete(db_template)
    db.commit()
    return


@router.post("/order-templates/{template_id}/use", response_model=OrderTemplateResponse)
def use_order_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark template as used (updates last_used_at timestamp)"""
    db_template = db.query(OrderTemplate).filter(OrderTemplate.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Order template not found")

    db_template.last_used_at = datetime.now(UTC)
    db.commit()
    db.refresh(db_template)
    return db_template
