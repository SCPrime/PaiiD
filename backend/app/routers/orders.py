import logging
import os
from datetime import datetime

import requests
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field, model_validator, validator
from sqlalchemy.orm import Session
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from ..core.auth import require_bearer
from ..core.config import settings
from ..core.idempotency import check_and_store
from ..core.kill_switch import is_killed, set_kill
from ..db.session import get_db
from ..middleware.validation import (
    validate_limit_price,
    validate_order_class,
    validate_order_type,
    validate_price_range,
    validate_quantity,
    validate_request_id,
    validate_side,
    validate_symbol,
)
from ..models.database import OrderTemplate


logger = logging.getLogger(__name__)

router = APIRouter()

# Alpaca API configuration
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
ALPACA_BASE_URL = "https://paper-api.alpaca.markets"  # Paper trading


def get_alpaca_headers():
    """Get headers for Alpaca API requests"""
    return {
        "APCA-API-KEY-ID": ALPACA_API_KEY,
        "APCA-API-SECRET-KEY": ALPACA_SECRET_KEY,
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
        self.last_failure_time = datetime.utcnow()

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
                elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
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


def _validate_advanced_order_requirements(
    order_class: str,
    take_profit: "TakeProfitConfig | None",
    stop_loss: "StopLossConfig | None",
    trail_price: float | None,
    trail_percent: float | None,
):
    """Shared validation rules for advanced order legs."""

    if order_class == "bracket" and not (take_profit or stop_loss):
        raise ValueError("Bracket orders require at least a take-profit or stop-loss configuration")

    if order_class == "oco":
        if not take_profit or not stop_loss:
            raise ValueError("OCO orders require both take-profit and stop-loss configurations")

    if trail_price and trail_percent:
        raise ValueError("Specify either trail_price or trail_percent, not both")


# Advanced order configuration models
class TakeProfitConfig(BaseModel):
    """Configuration for take-profit legs."""

    limit_price: float = Field(
        ...,
        gt=0,
        le=1_000_000,
        description="Target price that will close the position for profit",
    )

    @validator("limit_price")
    def validate_limit_price_value(cls, v):
        return validate_price_range(v, field_name="Take-profit limit price")


class StopLossConfig(BaseModel):
    """Configuration for stop-loss legs."""

    stop_price: float = Field(
        ...,
        gt=0,
        le=1_000_000,
        description="Price at which the stop loss triggers",
    )
    limit_price: float | None = Field(
        None,
        gt=0,
        le=1_000_000,
        description="Optional limit price for stop-limit exits",
    )

    @validator("stop_price")
    def validate_stop_price(cls, v):
        return validate_price_range(v, field_name="Stop-loss price")

    @validator("limit_price")
    def validate_limit_price(cls, v, values):
        if v is None:
            return v

        validated_value = validate_price_range(v, field_name="Stop-loss limit price")
        stop_price = values.get("stop_price")
        if stop_price is not None and validated_value < stop_price:
            raise ValueError("Stop-loss limit price must be greater than or equal to stop price")
        return validated_value


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
        ..., gt=0, le=10000, description="Order quantity (0.01 to 10,000 shares/contracts)"
    )
    type: str = Field(
        default="market", pattern=r"^(market|limit|stop|stop_limit)$", description="Order type"
    )
    limit_price: float | None = Field(
        default=None,
        gt=0,
        le=1000000,
        description="Limit price (required for limit/stop_limit orders)",
    )

    # Options-specific fields
    asset_class: str = Field(
        default="stock", pattern=r"^(stock|option)$", description="Asset class: 'stock' or 'option'"
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
    order_class: str = Field(
        default="simple",
        description="Order class defining advanced legs (simple, bracket, oco)",
    )
    take_profit: TakeProfitConfig | None = Field(
        default=None, description="Take-profit configuration for bracket/OCO orders"
    )
    stop_loss: StopLossConfig | None = Field(
        default=None, description="Stop-loss configuration for bracket/OCO orders"
    )
    trail_price: float | None = Field(
        default=None,
        gt=0,
        le=1_000_000,
        description="Trailing stop amount in dollars",
    )
    trail_percent: float | None = Field(
        default=None,
        gt=0,
        le=100,
        description="Trailing stop percentage (0-100)",
    )

    @validator("symbol")
    def validate_symbol_format(cls, v):
        """Validate and normalize symbol"""
        return validate_symbol(v)

    @validator("side")
    def validate_side_value(cls, v):
        """Validate order side"""
        return validate_side(v)

    @validator("qty")
    def validate_quantity_value(cls, v):
        """Validate order quantity"""
        return validate_quantity(v)

    @validator("type")
    def validate_order_type_value(cls, v):
        """Validate order type"""
        return validate_order_type(v)

    @validator("order_class")
    def validate_order_class_value(cls, v):
        """Validate order class"""
        return validate_order_class(v)

    @validator("limit_price", always=True)
    def validate_limit_price_value(cls, v, values):
        """Validate limit price based on order type"""
        order_type = values.get("type", "market")
        return validate_limit_price(v, order_type)

    @validator("option_type", always=True)
    def validate_option_type_required(cls, v, values):
        """Validate that option_type is provided for options orders"""
        asset_class = values.get("asset_class", "stock")
        if asset_class == "option" and not v:
            raise ValueError("option_type is required for options orders (call or put)")
        return v

    @validator("strike_price", always=True)
    def validate_strike_price_required(cls, v, values):
        """Validate that strike_price is provided for options orders"""
        asset_class = values.get("asset_class", "stock")
        if asset_class == "option" and not v:
            raise ValueError("strike_price is required for options orders")
        return v

    @validator("expiration_date", always=True)
    def validate_expiration_date_required(cls, v, values):
        """Validate that expiration_date is provided for options orders"""
        asset_class = values.get("asset_class", "stock")
        if asset_class == "option" and not v:
            raise ValueError("expiration_date is required for options orders (YYYY-MM-DD format)")
        return v

    @validator("trail_price")
    def validate_trail_price_value(cls, v):
        if v is not None:
            return validate_price_range(v, field_name="Trail price")
        return v

    @validator("trail_percent")
    def validate_trail_percent_value(cls, v):
        if v is not None:
            if v <= 0 or v > 100:
                raise ValueError("Trail percent must be between 0 and 100")
        return v

    @model_validator(mode="after")
    def validate_order_class_requirements(self):
        _validate_advanced_order_requirements(
            self.order_class,
            self.take_profit,
            self.stop_loss,
            self.trail_price,
            self.trail_percent,
        )
        return self


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
            status_code=503, detail="Alpaca API temporarily unavailable. Please try again later."
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

        # Attach advanced order parameters (bracket/OCO/trailing)
        if order.order_class and order.order_class != "simple":
            order_payload["order_class"] = order.order_class

        if order.take_profit:
            order_payload["take_profit"] = order.take_profit.dict()

        if order.stop_loss:
            order_payload["stop_loss"] = order.stop_loss.dict()

        if order.trail_price is not None:
            order_payload["trail_price"] = order.trail_price

        if order.trail_percent is not None:
            order_payload["trail_percent"] = order.trail_percent

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
        ..., min_items=1, max_items=10, description="List of orders to execute (max 10 per request)"
    )

    @validator("requestId")
    def validate_request_id_format(cls, v):
        """Validate request ID format"""
        return validate_request_id(v)

    @validator("orders")
    def validate_orders_list(cls, v):
        """Validate orders list"""
        if not v:
            raise ValueError("At least one order is required")
        if len(v) > 10:
            raise ValueError("Cannot execute more than 10 orders per request (safety limit)")
        return v


class PreviewOrder(Order):
    """Order definition with optional estimated price for preview calculations."""

    estimated_price: float | None = Field(
        default=None,
        alias="estimatedPrice",
        gt=0,
        le=1_000_000,
        description="Estimated execution price for preview calculations",
    )

    class Config:
        allow_population_by_field_name = True


class OrderPreviewRequest(BaseModel):
    orders: list[PreviewOrder] = Field(
        ..., min_items=1, max_items=10, description="Orders to preview"
    )


class OrderPreviewBreakdown(BaseModel):
    symbol: str
    side: str
    quantity: float
    order_type: str
    order_class: str
    entry_price: float | None
    notional: float | None
    take_profit_price: float | None
    stop_loss_price: float | None
    max_profit: float | None
    max_loss: float | None
    risk_reward_ratio: float | None


class OrderPreviewResponse(BaseModel):
    total_notional: float
    total_max_profit: float
    total_max_loss: float
    orders: list[OrderPreviewBreakdown]


@router.post("/trading/execute")
async def execute(request: Request, req: ExecRequest, _=Depends(require_bearer)):
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
            return {"accepted": True, "dryRun": True, "orders": [o.model_dump() for o in req.orders]}

        # Execute real trades via Alpaca API with circuit breaker and retry logic
        logger.info(f"[Trading Execute] Executing {len(req.orders)} live orders")
        executed_orders = []
        for order in req.orders:
            # Use new circuit breaker + retry function (handles all error cases)
            alpaca_order = execute_alpaca_order_with_retry(order)
            executed_orders.append(
                {
                    **order.model_dump(),
                    "alpaca_order_id": alpaca_order.get("id"),
                    "status": alpaca_order.get("status"),
                }
            )

        return {"accepted": True, "dryRun": False, "orders": executed_orders}

    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.error(
            f"[Trading Execute] UNEXPECTED ERROR: {type(e).__name__}: {e!s}", exc_info=True
        )
        raise HTTPException(status_code=500, detail=f"Internal server error: {e!s}")


@router.post("/orders/preview", response_model=OrderPreviewResponse)
def preview_orders(req: OrderPreviewRequest, _=Depends(require_bearer)):
    """Provide risk and exposure preview for pending orders."""

    breakdowns: list[OrderPreviewBreakdown] = []
    total_notional = 0.0
    total_max_profit = 0.0
    total_max_loss = 0.0

    for order in req.orders:
        # Determine entry price preference: limit price -> estimated price -> None
        entry_price: float | None = None
        if order.type in {"limit", "stop_limit"} and order.limit_price:
            entry_price = order.limit_price
        elif order.estimated_price:
            entry_price = order.estimated_price
        elif order.limit_price:
            entry_price = order.limit_price

        notional: float | None = None
        if entry_price is not None:
            notional = round(order.qty * entry_price, 2)
            total_notional += notional

        take_profit_price = order.take_profit.limit_price if order.take_profit else None
        stop_loss_price = order.stop_loss.stop_price if order.stop_loss else None

        max_profit: float | None = None
        if entry_price is not None and take_profit_price is not None:
            price_diff = (
                take_profit_price - entry_price
                if order.side == "buy"
                else entry_price - take_profit_price
            )
            max_profit = round(max(price_diff * order.qty, 0.0), 2)
            if max_profit is not None:
                total_max_profit += max_profit

        max_loss: float | None = None
        if entry_price is not None and stop_loss_price is not None:
            price_diff = (
                entry_price - stop_loss_price
                if order.side == "buy"
                else stop_loss_price - entry_price
            )
            max_loss = round(max(price_diff * order.qty, 0.0), 2)
            if max_loss is not None:
                total_max_loss += max_loss

        risk_reward: float | None = None
        if max_profit and max_profit > 0 and max_loss and max_loss > 0:
            risk_reward = round(max_profit / max_loss, 2)

        breakdowns.append(
            OrderPreviewBreakdown(
                symbol=order.symbol,
                side=order.side,
                quantity=order.qty,
                order_type=order.type,
                order_class=order.order_class,
                entry_price=entry_price,
                notional=notional,
                take_profit_price=take_profit_price,
                stop_loss_price=stop_loss_price,
                max_profit=max_profit,
                max_loss=max_loss,
                risk_reward_ratio=risk_reward,
            )
        )

    return OrderPreviewResponse(
        total_notional=round(total_notional, 2),
        total_max_profit=round(total_max_profit, 2),
        total_max_loss=round(total_max_loss, 2),
        orders=breakdowns,
    )


@router.post("/admin/kill")
def kill(state: bool, _=Depends(require_bearer)):
    set_kill(state)
    return {"tradingHalted": state}


# Order Template Models with Validation
class OrderTemplateCreate(BaseModel):
    """Create order template with validation"""

    name: str = Field(..., min_length=1, max_length=100, description="Template name")
    description: str | None = Field(None, max_length=500, description="Template description")
    symbol: str = Field(
        ..., min_length=1, max_length=5, pattern=r"^[A-Z]{1,5}$", description="Stock symbol"
    )
    side: str = Field(..., pattern=r"^(buy|sell)$", description="Order side")
    quantity: float = Field(..., gt=0, le=10000, description="Order quantity")
    order_type: str = Field(
        default="market", pattern=r"^(market|limit|stop|stop_limit)$", description="Order type"
    )
    limit_price: float | None = Field(None, gt=0, le=1000000, description="Limit price")
    asset_class: str = Field(
        default="stock", pattern=r"^(stock|option)$", description="Asset class"
    )
    option_type: str | None = Field(
        default=None, pattern=r"^(call|put)$", description="Option type for option templates"
    )
    strike_price: float | None = Field(
        default=None, gt=0, le=100000, description="Strike price for option templates"
    )
    expiration_date: str | None = Field(
        default=None,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Expiration date (YYYY-MM-DD) for option templates",
    )
    order_class: str = Field(
        default="simple",
        description="Advanced order class (simple, bracket, oco)",
    )
    take_profit: TakeProfitConfig | None = Field(
        default=None, description="Take-profit configuration"
    )
    stop_loss: StopLossConfig | None = Field(
        default=None, description="Stop-loss configuration"
    )
    trail_price: float | None = Field(
        default=None,
        gt=0,
        le=1_000_000,
        description="Trailing stop amount in dollars",
    )
    trail_percent: float | None = Field(
        default=None,
        gt=0,
        le=100,
        description="Trailing stop percentage",
    )

    @validator("symbol")
    def validate_symbol_format(cls, v):
        return validate_symbol(v)

    @validator("side")
    def validate_side_value(cls, v):
        return validate_side(v)

    @validator("quantity")
    def validate_quantity_value(cls, v):
        return validate_quantity(v)

    @validator("order_type")
    def validate_order_type_value(cls, v):
        return validate_order_type(v)

    @validator("limit_price", always=True)
    def validate_limit_price_value(cls, v, values):
        order_type = values.get("order_type", "market")
        return validate_limit_price(v, order_type)

    @validator("asset_class")
    def validate_asset_class(cls, v):
        return v.lower()

    @validator("option_type")
    def validate_option_type(cls, v, values):
        asset_class = values.get("asset_class", "stock")
        if asset_class == "option" and not v:
            raise ValueError("option_type is required when asset_class is option")
        return v

    @validator("strike_price")
    def validate_strike_price(cls, v, values):
        asset_class = values.get("asset_class", "stock")
        if asset_class == "option" and v is None:
            raise ValueError("strike_price is required when asset_class is option")
        if v is not None:
            validate_price_range(v, field_name="Strike price")
        return v

    @validator("expiration_date")
    def validate_expiration_date(cls, v, values):
        asset_class = values.get("asset_class", "stock")
        if asset_class == "option" and not v:
            raise ValueError("expiration_date is required when asset_class is option")
        return v

    @validator("order_class")
    def validate_order_class(cls, v):
        return validate_order_class(v)

    @validator("trail_price")
    def validate_template_trail_price(cls, v):
        if v is not None:
            return validate_price_range(v, field_name="Trail price")
        return v

    @validator("trail_percent")
    def validate_template_trail_percent(cls, v):
        if v is not None and (v <= 0 or v > 100):
            raise ValueError("Trail percent must be between 0 and 100")
        return v

    @model_validator(mode="after")
    def validate_advanced_requirements(self):
        _validate_advanced_order_requirements(
            self.order_class or "simple",
            self.take_profit,
            self.stop_loss,
            self.trail_price,
            self.trail_percent,
        )
        return self


class OrderTemplateUpdate(BaseModel):
    """Update order template with validation"""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    symbol: str | None = Field(None, min_length=1, max_length=5, pattern=r"^[A-Z]{1,5}$")
    side: str | None = Field(None, pattern=r"^(buy|sell)$")
    quantity: float | None = Field(None, gt=0, le=10000)
    order_type: str | None = Field(None, pattern=r"^(market|limit|stop|stop_limit)$")
    limit_price: float | None = Field(None, gt=0, le=1000000)
    asset_class: str | None = Field(None, pattern=r"^(stock|option)$")
    option_type: str | None = Field(None, pattern=r"^(call|put)$")
    strike_price: float | None = Field(None, gt=0, le=100000)
    expiration_date: str | None = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    order_class: str | None = Field(None, pattern=r"^(simple|bracket|oco)$")
    take_profit: TakeProfitConfig | None = None
    stop_loss: StopLossConfig | None = None
    trail_price: float | None = Field(None, gt=0, le=1_000_000)
    trail_percent: float | None = Field(None, gt=0, le=100)

    @validator("symbol")
    def validate_symbol_format(cls, v):
        if v is not None:
            return validate_symbol(v)
        return v

    @validator("side")
    def validate_side_value(cls, v):
        if v is not None:
            return validate_side(v)
        return v

    @validator("quantity")
    def validate_quantity_value(cls, v):
        if v is not None:
            return validate_quantity(v)
        return v

    @validator("order_type")
    def validate_order_type_value(cls, v):
        if v is not None:
            return validate_order_type(v)
        return v

    @validator("limit_price")
    def validate_limit_price_value(cls, v, values):
        if v is not None:
            order_type = values.get("order_type", "limit")
            return validate_limit_price(v, order_type)
        return v

    @validator("asset_class")
    def validate_asset_class(cls, v):
        if v is not None:
            return v.lower()
        return v

    @validator("option_type")
    def validate_option_type(cls, v, values):
        asset_class = values.get("asset_class")
        if asset_class == "option" and not v:
            raise ValueError("option_type is required when asset_class is option")
        return v

    @validator("strike_price")
    def validate_strike_price(cls, v, values):
        asset_class = values.get("asset_class")
        if asset_class == "option" and v is None:
            raise ValueError("strike_price is required when asset_class is option")
        if v is not None:
            validate_price_range(v, field_name="Strike price")
        return v

    @validator("expiration_date")
    def validate_expiration_date(cls, v, values):
        asset_class = values.get("asset_class")
        if asset_class == "option" and not v:
            raise ValueError("expiration_date is required when asset_class is option")
        return v

    @validator("order_class")
    def validate_order_class_value(cls, v):
        if v is not None:
            return validate_order_class(v)
        return v

    @validator("trail_price")
    def validate_trail_price(cls, v):
        if v is not None:
            return validate_price_range(v, field_name="Trail price")
        return v

    @validator("trail_percent")
    def validate_trail_percent(cls, v):
        if v is not None and (v <= 0 or v > 100):
            raise ValueError("Trail percent must be between 0 and 100")
        return v

    @model_validator(mode="after")
    def validate_advanced_requirements(self):
        order_class = self.order_class
        take_profit = self.take_profit
        stop_loss = self.stop_loss
        trail_price = self.trail_price
        trail_percent = self.trail_percent

        if order_class:
            _validate_advanced_order_requirements(
                order_class, take_profit, stop_loss, trail_price, trail_percent
            )
        elif take_profit or stop_loss or trail_price or trail_percent:
            _validate_advanced_order_requirements(
                "bracket", take_profit, stop_loss, trail_price, trail_percent
            )

        return self


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
    asset_class: str
    option_type: str | None
    strike_price: float | None
    expiration_date: str | None
    order_class: str
    take_profit: dict | None
    stop_loss: dict | None
    trail_price: float | None
    trail_percent: float | None
    created_at: datetime
    updated_at: datetime
    last_used_at: datetime | None

    class Config:
        from_attributes = True


# Order Template CRUD Endpoints
@router.post(
    "/order-templates", response_model=OrderTemplateResponse, status_code=status.HTTP_201_CREATED
)
def create_order_template(
    template: OrderTemplateCreate, db: Session = Depends(get_db), _=Depends(require_bearer)
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
        asset_class=template.asset_class,
        option_type=template.option_type,
        strike_price=template.strike_price,
        expiration_date=template.expiration_date,
        order_class=template.order_class,
        take_profit=template.take_profit.model_dump() if template.take_profit else None,
        stop_loss=template.stop_loss.model_dump() if template.stop_loss else None,
        trail_price=template.trail_price,
        trail_percent=template.trail_percent,
        user_id=None,  # For now, templates are global (not user-specific)
    )
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


@router.get("/order-templates", response_model=list[OrderTemplateResponse])
def list_order_templates(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _=Depends(require_bearer)
):
    """List all order templates"""
    templates = db.query(OrderTemplate).offset(skip).limit(limit).all()
    return templates


@router.get("/order-templates/{template_id}", response_model=OrderTemplateResponse)
def get_order_template(template_id: int, db: Session = Depends(get_db), _=Depends(require_bearer)):
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
    _=Depends(require_bearer),
):
    """Update an existing order template"""
    db_template = db.query(OrderTemplate).filter(OrderTemplate.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Order template not found")

    # Update fields if provided
    fields_set = template_update.__fields_set__
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
    if template_update.asset_class is not None:
        db_template.asset_class = template_update.asset_class
        if template_update.asset_class == "stock":
            db_template.option_type = None
            db_template.strike_price = None
            db_template.expiration_date = None
    if template_update.option_type is not None:
        db_template.option_type = template_update.option_type
    if template_update.strike_price is not None:
        db_template.strike_price = template_update.strike_price
    if template_update.expiration_date is not None:
        db_template.expiration_date = template_update.expiration_date
    if template_update.order_class is not None:
        db_template.order_class = template_update.order_class
    if "take_profit" in fields_set:
        db_template.take_profit = (
            template_update.take_profit.dict()
            if template_update.take_profit
            else None
        )
    if "stop_loss" in fields_set:
        db_template.stop_loss = (
            template_update.stop_loss.dict() if template_update.stop_loss else None
        )
    if template_update.trail_price is not None or "trail_price" in fields_set:
        db_template.trail_price = template_update.trail_price
    if template_update.trail_percent is not None or "trail_percent" in fields_set:
        db_template.trail_percent = template_update.trail_percent

    db_template.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_template)
    return db_template


@router.delete("/order-templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order_template(
    template_id: int, db: Session = Depends(get_db), _=Depends(require_bearer)
):
    """Delete an order template"""
    db_template = db.query(OrderTemplate).filter(OrderTemplate.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Order template not found")

    db.delete(db_template)
    db.commit()
    return


@router.post("/order-templates/{template_id}/use", response_model=OrderTemplateResponse)
def use_order_template(template_id: int, db: Session = Depends(get_db), _=Depends(require_bearer)):
    """Mark template as used (updates last_used_at timestamp)"""
    db_template = db.query(OrderTemplate).filter(OrderTemplate.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Order template not found")

    db_template.last_used_at = datetime.utcnow()
    db.commit()
    db.refresh(db_template)
    return db_template
