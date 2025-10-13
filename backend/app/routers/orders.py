from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
from ..core.auth import require_bearer
from ..core.kill_switch import is_killed, set_kill
from ..core.idempotency import check_and_store
from ..core.config import settings
from ..db.session import get_db
from ..models.database import OrderTemplate
import requests
import os

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

class Order(BaseModel):
    symbol: str
    side: str
    qty: float
    type: str = "market"

class ExecRequest(BaseModel):
    dryRun: bool = True
    requestId: str
    orders: list[Order]

@router.post("/trading/execute")
def execute(req: ExecRequest, _=Depends(require_bearer)):
    if not req.requestId:
        raise HTTPException(status_code=400, detail="requestId required")

    if not check_and_store(req.requestId):
        return {"accepted": False, "duplicate": True}

    if is_killed():
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail="trading halted")

    # Respect LIVE_TRADING setting
    if req.dryRun or not settings.LIVE_TRADING:
        return {"accepted": True, "dryRun": True, "orders": [o.dict() for o in req.orders]}

    # Execute real trades via Alpaca API
    executed_orders = []
    for order in req.orders:
        try:
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
            alpaca_order = response.json()
            executed_orders.append({
                **order.dict(),
                "alpaca_order_id": alpaca_order.get("id"),
                "status": alpaca_order.get("status")
            })
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to execute order for {order.symbol}: {str(e)}"
            )

    return {"accepted": True, "dryRun": False, "orders": executed_orders}

@router.post("/admin/kill")
def kill(state: bool, _=Depends(require_bearer)):
    set_kill(state)
    return {"tradingHalted": state}


# Order Template Models
class OrderTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    symbol: str
    side: str
    quantity: float
    order_type: str = "market"
    limit_price: Optional[float] = None


class OrderTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    symbol: Optional[str] = None
    side: Optional[str] = None
    quantity: Optional[float] = None
    order_type: Optional[str] = None
    limit_price: Optional[float] = None


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