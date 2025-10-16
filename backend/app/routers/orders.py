from fastapi import APIRouter, HTTPException, Depends, status, Request
from pydantic import BaseModel, validator, Field
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
from ..core.auth import require_bearer
from ..middleware.rate_limit import limiter, rate_limit_strict
from ..core.kill_switch import is_killed, set_kill
from ..core.idempotency import check_and_store
from ..core.config import settings
from ..db.session import get_db
from ..models.database import OrderTemplate
from ..middleware.validation import (
    validate_symbol,
    validate_quantity,
    validate_side,
    validate_order_type,
    validate_limit_price,
    validate_request_id,
    symbol_field,
    quantity_field,
    price_field
)
import requests
import os
import logging
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

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
        self.last_failure_time: Optional[datetime] = None
        self.state = 'CLOSED'

    def record_success(self):
        """Record successful call - reset circuit"""
        self.failure_count = 0
        self.state = 'CLOSED'
        self.last_failure_time = None
        logger.info("[Alpaca Circuit] CLOSED - Normal operation")

    def record_failure(self):
        """Record failed call - increment counter and potentially open circuit"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()

        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
            logger.warning(
                f"[Alpaca Circuit] OPENED after {self.failure_count} failures. "
                f"Cooldown: {self.cooldown_seconds}s"
            )

    def is_available(self) -> bool:
        """Check if requests should be allowed"""
        if self.state == 'CLOSED':
            return True

        if self.state == 'OPEN':
            # Check if cooldown period has elapsed
            if self.last_failure_time:
                elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
                if elapsed >= self.cooldown_seconds:
                    # Move to HALF_OPEN to test Alpaca
                    self.state = 'HALF_OPEN'
                    logger.info("[Alpaca Circuit] HALF_OPEN - testing Alpaca API")
                    return True
            return False

        # HALF_OPEN state - allow one test request
        return True


# Global circuit breaker instance
alpaca_circuit_breaker = AlpacaCircuitBreaker(failure_threshold=3, cooldown_seconds=60)


# Order Model (must be defined before use in function signatures)
class Order(BaseModel):
    """Order model with comprehensive validation"""
    symbol: str = Field(..., min_length=1, max_length=5, pattern=r'^[A-Z]{1,5}$',
                        description="Stock symbol (1-5 uppercase letters)", examples=["AAPL", "SPY"])
    side: str = Field(..., pattern=r'^(buy|sell)$', description="Order side: 'buy' or 'sell'")
    qty: float = Field(..., gt=0, le=10000, description="Order quantity (0.01 to 10,000 shares)")
    type: str = Field(default="market", pattern=r'^(market|limit|stop|stop_limit)$',
                      description="Order type")
    limit_price: Optional[float] = Field(default=None, gt=0, le=1000000,
                                         description="Limit price (required for limit/stop_limit orders)")

    @validator('symbol')
    def validate_symbol_format(cls, v):
        """Validate and normalize symbol"""
        return validate_symbol(v)

    @validator('side')
    def validate_side_value(cls, v):
        """Validate order side"""
        return validate_side(v)

    @validator('qty')
    def validate_quantity_value(cls, v):
        """Validate order quantity"""
        return validate_quantity(v)

    @validator('type')
    def validate_order_type_value(cls, v):
        """Validate order type"""
        return validate_order_type(v)

    @validator('limit_price', always=True)
    def validate_limit_price_value(cls, v, values):
        """Validate limit price based on order type"""
        order_type = values.get('type', 'market')
        return validate_limit_price(v, order_type)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((requests.exceptions.ConnectionError, requests.exceptions.Timeout)),
    before_sleep=before_sleep_log(logger, logging.WARNING)
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
            detail="Alpaca API temporarily unavailable. Please try again later."
        )

    try:
        # Execute order via Alpaca API
        response = requests.post(
            f"{ALPACA_BASE_URL}/v2/orders",
            headers=get_alpaca_headers(),
            json={
                "symbol": order.symbol,
                "qty": order.qty,
                "side": order.side,
                "type": order.type,
                "time_in_force": "day"
            },
            timeout=10
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
            status_code=500,
            detail=f"Failed to execute order for {order.symbol}: {str(e)}"
        )


class ExecRequest(BaseModel):
    """Execute order request with idempotency and validation"""
    dryRun: bool = Field(default=True, description="Dry run mode (no actual execution)")
    requestId: str = Field(..., min_length=8, max_length=64,
                          pattern=r'^[a-zA-Z0-9\-_]{8,64}$',
                          description="Unique request ID for idempotency (8-64 alphanumeric + hyphens/underscores)")
    orders: list[Order] = Field(..., min_items=1, max_items=10,
                                description="List of orders to execute (max 10 per request)")

    @validator('requestId')
    def validate_request_id_format(cls, v):
        """Validate request ID format"""
        return validate_request_id(v)

    @validator('orders')
    def validate_orders_list(cls, v):
        """Validate orders list"""
        if not v:
            raise ValueError("At least one order is required")
        if len(v) > 10:
            raise ValueError("Cannot execute more than 10 orders per request (safety limit)")
        return v

@router.post("/trading/execute")
@limiter.limit("1000/minute" if settings.TESTING else "10/minute")  # Bypass rate limit in tests
async def execute(request: Request, req: ExecRequest, _=Depends(require_bearer)):
    if not req.requestId:
        raise HTTPException(status_code=400, detail="requestId required")

    if not check_and_store(req.requestId):
        return {"accepted": False, "duplicate": True}

    if is_killed():
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail="trading halted")

    # Respect LIVE_TRADING setting
    if req.dryRun or not settings.LIVE_TRADING:
        return {"accepted": True, "dryRun": True, "orders": [o.dict() for o in req.orders]}

    # Execute real trades via Alpaca API with circuit breaker and retry logic
    executed_orders = []
    for order in req.orders:
        # Use new circuit breaker + retry function (handles all error cases)
        alpaca_order = execute_alpaca_order_with_retry(order)
        executed_orders.append({
            **order.dict(),
            "alpaca_order_id": alpaca_order.get("id"),
            "status": alpaca_order.get("status")
        })

    return {"accepted": True, "dryRun": False, "orders": executed_orders}

@router.post("/admin/kill")
def kill(state: bool, _=Depends(require_bearer)):
    set_kill(state)
    return {"tradingHalted": state}


# Order Template Models with Validation
class OrderTemplateCreate(BaseModel):
    """Create order template with validation"""
    name: str = Field(..., min_length=1, max_length=100, description="Template name")
    description: Optional[str] = Field(None, max_length=500, description="Template description")
    symbol: str = Field(..., min_length=1, max_length=5, pattern=r'^[A-Z]{1,5}$',
                        description="Stock symbol")
    side: str = Field(..., pattern=r'^(buy|sell)$', description="Order side")
    quantity: float = Field(..., gt=0, le=10000, description="Order quantity")
    order_type: str = Field(default="market", pattern=r'^(market|limit|stop|stop_limit)$',
                           description="Order type")
    limit_price: Optional[float] = Field(None, gt=0, le=1000000, description="Limit price")

    @validator('symbol')
    def validate_symbol_format(cls, v):
        return validate_symbol(v)

    @validator('side')
    def validate_side_value(cls, v):
        return validate_side(v)

    @validator('quantity')
    def validate_quantity_value(cls, v):
        return validate_quantity(v)

    @validator('order_type')
    def validate_order_type_value(cls, v):
        return validate_order_type(v)

    @validator('limit_price', always=True)
    def validate_limit_price_value(cls, v, values):
        order_type = values.get('order_type', 'market')
        return validate_limit_price(v, order_type)


class OrderTemplateUpdate(BaseModel):
    """Update order template with validation"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    symbol: Optional[str] = Field(None, min_length=1, max_length=5, pattern=r'^[A-Z]{1,5}$')
    side: Optional[str] = Field(None, pattern=r'^(buy|sell)$')
    quantity: Optional[float] = Field(None, gt=0, le=10000)
    order_type: Optional[str] = Field(None, pattern=r'^(market|limit|stop|stop_limit)$')
    limit_price: Optional[float] = Field(None, gt=0, le=1000000)

    @validator('symbol')
    def validate_symbol_format(cls, v):
        if v is not None:
            return validate_symbol(v)
        return v

    @validator('side')
    def validate_side_value(cls, v):
        if v is not None:
            return validate_side(v)
        return v

    @validator('quantity')
    def validate_quantity_value(cls, v):
        if v is not None:
            return validate_quantity(v)
        return v

    @validator('order_type')
    def validate_order_type_value(cls, v):
        if v is not None:
            return validate_order_type(v)
        return v


class OrderTemplateResponse(BaseModel):
    id: int
    user_id: Optional[int]
    name: str
    description: Optional[str]
    symbol: str
    side: str
    quantity: float
    order_type: str
    limit_price: Optional[float]
    created_at: datetime
    updated_at: datetime
    last_used_at: Optional[datetime]

    class Config:
        from_attributes = True


# Order Template CRUD Endpoints
@router.post("/order-templates", response_model=OrderTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_order_template(
    template: OrderTemplateCreate,
    db: Session = Depends(get_db),
    _=Depends(require_bearer)
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
        user_id=None  # For now, templates are global (not user-specific)
    )
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


@router.get("/order-templates", response_model=List[OrderTemplateResponse])
def list_order_templates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _=Depends(require_bearer)
):
    """List all order templates"""
    templates = db.query(OrderTemplate).offset(skip).limit(limit).all()
    return templates


@router.get("/order-templates/{template_id}", response_model=OrderTemplateResponse)
def get_order_template(
    template_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_bearer)
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
    _=Depends(require_bearer)
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

    db_template.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_template)
    return db_template


@router.delete("/order-templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order_template(
    template_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_bearer)
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
    _=Depends(require_bearer)
):
    """Mark template as used (updates last_used_at timestamp)"""
    db_template = db.query(OrderTemplate).filter(OrderTemplate.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Order template not found")

    db_template.last_used_at = datetime.utcnow()
    db.commit()
    db.refresh(db_template)
    return db_template