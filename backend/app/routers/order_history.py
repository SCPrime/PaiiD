"""Order history persistence endpoints."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..core.auth import require_bearer
from ..db.session import get_db
from ..models.database import OrderHistory, User


router = APIRouter()


class OrderHistoryPayload(BaseModel):
    """Payload for recording order history events."""

    symbol: str = Field(..., min_length=1, max_length=20)
    side: str = Field(..., pattern=r"^(buy|sell)$")
    qty: float = Field(..., gt=0)
    type: str = Field("market", alias="orderType")
    limitPrice: float | None = Field(default=None)
    status: str | None = Field(default="pending")
    dryRun: bool | None = Field(default=False)
    timestamp: datetime | None = None
    clientId: str | None = None

    class Config:
        allow_population_by_field_name = True
        extra = "allow"


def _get_or_create_default_user(db: Session) -> User:
    user = db.query(User).filter(User.id == 1).first()
    if user:
        return user

    user = User(
        id=1,
        email="owner@paiid.local",
        password_hash="migrated",
        role="owner",
        preferences={"risk_tolerance": 50},
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _serialize_history(record: OrderHistory) -> dict:
    return {
        "id": record.client_order_id or f"order-{record.id}",
        "dbId": record.id,
        "symbol": record.symbol,
        "side": record.side,
        "qty": record.quantity,
        "type": record.order_type,
        "limitPrice": record.limit_price,
        "status": record.status,
        "dryRun": record.is_dry_run,
        "timestamp": record.created_at.isoformat() if record.created_at else None,
    }


@router.get("/orders/history")
def list_order_history(
    limit: int = 100,
    offset: int = 0,
    _=Depends(require_bearer),
    db: Session = Depends(get_db),
):
    """Return stored order history records."""

    user = _get_or_create_default_user(db)
    query = (
        db.query(OrderHistory)
        .filter(OrderHistory.user_id == user.id)
        .order_by(OrderHistory.created_at.desc())
    )
    total = query.count()
    records = query.offset(offset).limit(limit).all()

    return {
        "orders": [_serialize_history(record) for record in records],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.post("/orders/history", status_code=status.HTTP_201_CREATED)
def create_order_history(
    payload: OrderHistoryPayload,
    _=Depends(require_bearer),
    db: Session = Depends(get_db),
):
    """Record a new order history entry."""

    user = _get_or_create_default_user(db)

    timestamp = payload.timestamp or datetime.utcnow()

    history = OrderHistory(
        user_id=user.id,
        client_order_id=payload.clientId,
        symbol=payload.symbol.upper(),
        side=payload.side,
        quantity=float(payload.qty),
        order_type=payload.type,
        limit_price=payload.limitPrice,
        status=payload.status or "pending",
        is_dry_run=bool(payload.dryRun),
        executed_at=timestamp,
        created_at=timestamp,
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    return _serialize_history(history)


@router.delete("/orders/history", status_code=status.HTTP_204_NO_CONTENT)
def clear_order_history(
    _=Depends(require_bearer),
    db: Session = Depends(get_db),
):
    """Remove all stored order history entries for the default user."""

    user = _get_or_create_default_user(db)
    db.query(OrderHistory).filter(OrderHistory.user_id == user.id).delete()
    db.commit()
    return None
