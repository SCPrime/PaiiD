"""Alpaca passthrough endpoints exposed via FastAPI."""

from __future__ import annotations

import logging
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..core.auth import require_bearer
from ..core.config import settings
from ..services.alpaca_client import get_alpaca_client

logger = logging.getLogger(__name__)

router = APIRouter(tags=["alpaca"])


class WatchlistCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    symbols: list[str] = Field(default_factory=list)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


_STUB_ASSETS: list[dict[str, Any]] = [
    {
        "id": "asset-AAPL",
        "class": "us_equity",
        "exchange": "NASDAQ",
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "status": "active",
        "tradable": True,
        "marginable": True,
        "shortable": True,
        "easy_to_borrow": True,
        "fractionable": True,
    },
    {
        "id": "asset-MSFT",
        "class": "us_equity",
        "exchange": "NASDAQ",
        "symbol": "MSFT",
        "name": "Microsoft Corporation",
        "status": "active",
        "tradable": True,
        "marginable": True,
        "shortable": True,
        "easy_to_borrow": True,
        "fractionable": True,
    },
]

_STUB_CLOCK = {
    "timestamp": _utc_now(),
    "is_open": False,
    "next_open": _utc_now(),
    "next_close": _utc_now(),
}

_STUB_CALENDAR: list[dict[str, Any]] = [
    {
        "date": "2024-01-02",
        "open": "2024-01-02T09:30:00-05:00",
        "close": "2024-01-02T16:00:00-05:00",
    },
    {
        "date": "2024-01-03",
        "open": "2024-01-03T09:30:00-05:00",
        "close": "2024-01-03T16:00:00-05:00",
    },
]

_STUB_WATCHLISTS: list[dict[str, Any]] = [
    {
        "id": "demo-watchlist",
        "account_id": "paper-account",
        "name": "Tech Leaders",
        "created_at": _utc_now(),
        "updated_at": _utc_now(),
        "symbols": ["AAPL", "MSFT"],
        "assets": deepcopy(_STUB_ASSETS),
    }
]


def _build_stub_asset(symbol: str) -> dict[str, Any]:
    normalized = symbol.upper()
    for asset in _STUB_ASSETS:
        if asset["symbol"] == normalized:
            return deepcopy(asset)
    return {
        "id": f"asset-{normalized}",
        "class": "us_equity",
        "exchange": "NYSE",
        "symbol": normalized,
        "name": normalized,
        "status": "active",
        "tradable": True,
        "marginable": True,
        "shortable": False,
        "easy_to_borrow": False,
        "fractionable": False,
    }


def _use_stub_data() -> bool:
    return settings.TESTING


@router.get("/assets", dependencies=[Depends(require_bearer)])
async def list_assets(status: str | None = None, asset_class: str | None = None):
    """List Alpaca assets (passthrough to SDK or stub in testing)."""

    if _use_stub_data():
        assets = deepcopy(_STUB_ASSETS)
        if status:
            assets = [asset for asset in assets if asset.get("status") == status]
        if asset_class:
            assets = [asset for asset in assets if asset.get("class") == asset_class]
        return assets

    try:
        client = get_alpaca_client()
        return client.list_assets(status=status, asset_class=asset_class)
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.error("❌ list_assets failed: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/assets/{symbol}", dependencies=[Depends(require_bearer)])
async def get_asset(symbol: str):
    """Fetch a single asset by symbol."""

    if _use_stub_data():
        for asset in _STUB_ASSETS:
            if asset["symbol"] == symbol.upper():
                return deepcopy(asset)
        raise HTTPException(status_code=404, detail=f"Asset {symbol} not found")

    try:
        client = get_alpaca_client()
        return client.get_asset(symbol)
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.error("❌ get_asset failed for %s: %s", symbol, exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/clock", dependencies=[Depends(require_bearer)])
async def get_clock():
    """Return Alpaca market clock."""

    if _use_stub_data():
        return deepcopy(_STUB_CLOCK)

    try:
        client = get_alpaca_client()
        return client.get_clock()
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.error("❌ get_clock failed: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/calendar", dependencies=[Depends(require_bearer)])
async def get_calendar(start: str | None = None, end: str | None = None):
    """Return Alpaca market calendar entries."""

    if _use_stub_data():
        events = deepcopy(_STUB_CALENDAR)
        if start:
            events = [event for event in events if event["date"] >= start]
        if end:
            events = [event for event in events if event["date"] <= end]
        return events

    try:
        client = get_alpaca_client()
        return client.get_calendar(start=start, end=end)
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.error("❌ get_calendar failed: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/watchlists", dependencies=[Depends(require_bearer)])
async def list_watchlists():
    """List Alpaca watchlists."""

    if _use_stub_data():
        return deepcopy(_STUB_WATCHLISTS)

    try:
        client = get_alpaca_client()
        return client.get_watchlists()
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.error("❌ get_watchlists failed: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/watchlists", dependencies=[Depends(require_bearer)])
async def create_watchlist(payload: WatchlistCreateRequest):
    """Create a new Alpaca watchlist."""

    if _use_stub_data():
        now = _utc_now()
        watchlist = {
            "id": str(uuid4()),
            "account_id": "paper-account",
            "name": payload.name,
            "created_at": now,
            "updated_at": now,
            "symbols": [symbol.upper() for symbol in payload.symbols],
            "assets": [_build_stub_asset(symbol) for symbol in payload.symbols],
        }
        _STUB_WATCHLISTS.append(watchlist)
        return deepcopy(watchlist)

    try:
        client = get_alpaca_client()
        return client.create_watchlist(payload.name, payload.symbols)
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.error("❌ create_watchlist failed: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.delete("/watchlists/{watchlist_id}", dependencies=[Depends(require_bearer)])
async def delete_watchlist(watchlist_id: str):
    """Delete a watchlist."""

    if _use_stub_data():
        for index, watchlist in enumerate(_STUB_WATCHLISTS):
            if watchlist["id"] == watchlist_id:
                del _STUB_WATCHLISTS[index]
                return {"status": "deleted", "watchlist_id": watchlist_id}
        raise HTTPException(status_code=404, detail=f"Watchlist {watchlist_id} not found")

    try:
        client = get_alpaca_client()
        client.delete_watchlist(watchlist_id)
        return {"status": "deleted", "watchlist_id": watchlist_id}
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.error("❌ delete_watchlist failed for %s: %s", watchlist_id, exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
