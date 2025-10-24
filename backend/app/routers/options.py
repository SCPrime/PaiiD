"""Options endpoints: chains, greeks, and multi-leg orders."""

from __future__ import annotations

import asyncio
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..core.auth import require_bearer
from ..db.session import get_db
from ..options.schemas import (
    GreeksRequest,
    GreeksResponse,
    MultiLegOrderCreate,
    MultiLegOrderResponse,
    OptionChainResponse,
    OptionExpiration,
)
from ..options.service import (
    calculate_greeks_payload,
    create_multi_leg_order,
    fetch_option_chain,
    get_multi_leg_order,
    list_expiration_dates,
    list_multi_leg_orders,
)

router = APIRouter(prefix="/options", tags=["options"])
logger = logging.getLogger(__name__)


@router.get(
    "/chains/{symbol}",
    response_model=OptionChainResponse,
    dependencies=[Depends(require_bearer)],
)
async def get_options_chain(
    symbol: str,
    expiration: Optional[str] = Query(
        default=None,
        description="Expiration in YYYY-MM-DD format. Defaults to nearest expiration when omitted.",
    ),
    force_refresh: bool = Query(False, description="Ignore cached values and re-fetch from provider"),
) -> OptionChainResponse:
    """Return an options chain with computed greeks and implied volatilities."""

    try:
        return await asyncio.to_thread(fetch_option_chain, symbol, expiration, force_refresh)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Failed to fetch options chain", exc_info=exc)
        raise HTTPException(status_code=500, detail="Failed to fetch options chain") from exc


@router.get(
    "/chain/{symbol}",
    response_model=OptionChainResponse,
    dependencies=[Depends(require_bearer)],
)
async def get_options_chain_alias(
    symbol: str,
    expiration: Optional[str] = Query(None),
    force_refresh: bool = Query(False),
) -> OptionChainResponse:
    """Backward compatible alias for legacy clients."""

    return await get_options_chain(symbol=symbol, expiration=expiration, force_refresh=force_refresh)


@router.get(
    "/expirations/{symbol}",
    response_model=List[OptionExpiration],
    dependencies=[Depends(require_bearer)],
)
async def get_expirations(symbol: str) -> List[OptionExpiration]:
    """Return available expiration dates with days-to-expiry."""

    try:
        return await asyncio.to_thread(list_expiration_dates, symbol)
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Failed to fetch expirations", exc_info=exc)
        raise HTTPException(status_code=500, detail="Failed to fetch expirations") from exc


@router.post(
    "/greeks",
    response_model=GreeksResponse,
    dependencies=[Depends(require_bearer)],
)
async def calculate_greeks(request: GreeksRequest) -> GreeksResponse:
    """Calculate greeks using py_vollib for the supplied contract parameters."""

    try:
        return await asyncio.to_thread(calculate_greeks_payload, request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Failed to calculate greeks", exc_info=exc)
        raise HTTPException(status_code=500, detail="Failed to calculate greeks") from exc


@router.post(
    "/multi-leg/orders",
    response_model=MultiLegOrderResponse,
)
def create_multi_leg(
    payload: MultiLegOrderCreate,
    db: Session = Depends(get_db),
    _=Depends(require_bearer),
) -> MultiLegOrderResponse:
    """Persist a multi-leg order template with analytics."""

    try:
        return create_multi_leg_order(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Failed to create multi-leg order", exc_info=exc)
        raise HTTPException(status_code=500, detail="Failed to create multi-leg order") from exc


@router.get(
    "/multi-leg/orders",
    response_model=List[MultiLegOrderResponse],
)
def list_multi_leg(
    symbol: Optional[str] = Query(None, description="Filter orders by underlying symbol"),
    db: Session = Depends(get_db),
    _=Depends(require_bearer),
) -> List[MultiLegOrderResponse]:
    """List saved multi-leg orders."""

    return list_multi_leg_orders(db, symbol)


@router.get(
    "/multi-leg/orders/{order_id}",
    response_model=MultiLegOrderResponse,
)
def get_multi_leg(order_id: int, db: Session = Depends(get_db), _=Depends(require_bearer)) -> MultiLegOrderResponse:
    """Fetch a specific multi-leg order by identifier."""

    order = get_multi_leg_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Multi-leg order not found")
    return order
