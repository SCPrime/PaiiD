"""Domain services for options workflows."""

from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Dict, Iterable, List, Optional
from sqlalchemy.orm import Session

from ..models.database import OptionMultiLegOrder, OptionOrderLeg
from ..services.greeks import days_until_expiration, greeks_calculator
from ..services.tradier_client import get_tradier_client
from .schemas import (
    GreeksRequest,
    GreeksResponse,
    MultiLegOrderCreate,
    MultiLegOrderResponse,
    OptionChainResponse,
    OptionContract,
    OptionExpiration,
    OptionGreeks,
    OptionLegCreate,
    OptionLegResponse,
)

logger = logging.getLogger(__name__)


class TTLCache:
    """Lightweight TTL cache used to avoid repeated API calls."""

    def __init__(self, maxsize: int, ttl: int) -> None:
        self.maxsize = maxsize
        self.ttl = ttl
        self._store: Dict[str, tuple[datetime, OptionChainResponse]] = {}

    def get(self, key: str) -> Optional[OptionChainResponse]:
        entry = self._store.get(key)
        if not entry:
            return None
        timestamp, value = entry
        if (datetime.utcnow() - timestamp).total_seconds() > self.ttl:
            self._store.pop(key, None)
            return None
        return value

    def __contains__(self, key: str) -> bool:  # pragma: no cover - trivial
        return self.get(key) is not None

    def __getitem__(self, key: str) -> OptionChainResponse:
        value = self.get(key)
        if value is None:
            raise KeyError(key)
        return value

    def __setitem__(self, key: str, value: OptionChainResponse) -> None:
        if len(self._store) >= self.maxsize:
            oldest_key = next(iter(self._store))
            self._store.pop(oldest_key, None)
        self._store[key] = (datetime.utcnow(), value)


# Cache up to 128 chains for five minutes
_CHAIN_CACHE: TTLCache = TTLCache(maxsize=128, ttl=300)


def fetch_option_chain(symbol: str, expiration: Optional[str], force_refresh: bool = False) -> OptionChainResponse:
    """Fetch and normalize an option chain from Tradier."""

    normalized_symbol = symbol.upper()
    client = get_tradier_client()

    selected_expiration = expiration
    if not selected_expiration:
        expiry_data = client.get_option_expirations(normalized_symbol)
        expirations = expiry_data.get("expirations", {}).get("date", [])
        if isinstance(expirations, list):
            selected_expiration = expirations[0] if expirations else None
        elif isinstance(expirations, str):
            selected_expiration = expirations

    if not selected_expiration:
        raise ValueError(f"No option expirations available for {normalized_symbol}")

    cache_key = f"{normalized_symbol}:{selected_expiration}"
    if not force_refresh and cache_key in _CHAIN_CACHE:
        return _CHAIN_CACHE[cache_key]

    raw_chain = client.get_option_chains(normalized_symbol, selected_expiration)

    underlying_price = _extract_underlying_price(raw_chain)
    option_items = raw_chain.get("options", {}).get("option", [])
    if isinstance(option_items, dict):
        option_items = [option_items]

    calls: List[OptionContract] = []
    puts: List[OptionContract] = []

    for option in option_items:
        try:
            contract = _build_option_contract(
                normalized_symbol,
                option,
                selected_expiration,
                underlying_price,
            )
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.debug("Skipping malformed option contract: %s", exc, exc_info=True)
            continue

        if contract.option_type == "call":
            calls.append(contract)
        else:
            puts.append(contract)

    response = OptionChainResponse(
        symbol=normalized_symbol,
        expiration_date=datetime.strptime(selected_expiration, "%Y-%m-%d").date(),
        underlying_price=underlying_price,
        calls=calls,
        puts=puts,
        total_contracts=len(calls) + len(puts),
        fetched_at=datetime.utcnow(),
    )

    _CHAIN_CACHE[cache_key] = response
    return response


def list_expiration_dates(symbol: str) -> List[OptionExpiration]:
    """Return available expirations for a symbol."""

    client = get_tradier_client()
    raw = client.get_option_expirations(symbol.upper())

    expirations = raw.get("expirations", {}).get("date", [])
    if isinstance(expirations, str):
        expirations = [expirations]

    parsed: List[OptionExpiration] = []
    for exp in expirations or []:
        parsed.append(
            OptionExpiration(
                date=datetime.strptime(exp, "%Y-%m-%d").date(),
                days_to_expiry=days_until_expiration(exp),
            )
        )
    return parsed


def calculate_greeks_payload(request: GreeksRequest) -> GreeksResponse:
    """Calculate greeks for ad-hoc requests."""

    days = days_until_expiration(request.expiration.isoformat())
    iv = request.implied_volatility

    if iv is None and request.price is not None:
        iv = greeks_calculator.calculate_implied_volatility(
            request.option_type,
            request.price,
            request.underlying_price,
            request.strike_price,
            days,
        )

    if iv is None:
        raise ValueError("Implied volatility could not be derived from the provided inputs")

    greeks = greeks_calculator.calculate_greeks(
        request.option_type,
        request.underlying_price,
        request.strike_price,
        days,
        iv,
    )

    return GreeksResponse(**greeks, implied_volatility=iv)


def create_multi_leg_order(db: Session, payload: MultiLegOrderCreate) -> MultiLegOrderResponse:
    """Persist a multi-leg order and enrich legs with analytics."""

    symbol = payload.symbol.upper()
    net_price = _resolve_net_price(payload)
    order_type = _resolve_order_type(payload.order_type, net_price)

    leg_analytics = [
        _analyze_leg(symbol, leg, payload.underlying_price)
        for leg in payload.legs
    ]

    derived_underlying = payload.underlying_price or _average(
        [item["underlying_price"] for item in leg_analytics if item["underlying_price"]]
    )

    order = OptionMultiLegOrder(
        symbol=symbol,
        strategy=payload.strategy,
        order_type=order_type,
        net_price=net_price,
        underlying_price=derived_underlying,
        status="draft",
        notes=payload.notes,
        metadata_json=payload.metadata or {},
    )

    for leg, analytics in zip(payload.legs, leg_analytics):
        order.legs.append(
            OptionOrderLeg(
                action=leg.action,
                option_type=leg.option_type,
                strike_price=leg.strike,
                expiration_date=leg.expiration,
                quantity=leg.quantity,
                limit_price=leg.price,
                implied_volatility=analytics["implied_volatility"],
                delta=analytics["greeks"].get("delta"),
                gamma=analytics["greeks"].get("gamma"),
                theta=analytics["greeks"].get("theta"),
                vega=analytics["greeks"].get("vega"),
                rho=analytics["greeks"].get("rho"),
                underlying_price=analytics["underlying_price"],
                source_symbol=_build_occ_symbol(symbol, leg.expiration, leg.option_type, leg.strike),
                metadata_json=leg.metadata or {},
            )
        )

    db.add(order)
    db.commit()
    db.refresh(order)

    return _serialize_order(order)


def get_multi_leg_order(db: Session, order_id: int) -> Optional[MultiLegOrderResponse]:
    """Fetch a persisted multi-leg order by id."""

    order = db.query(OptionMultiLegOrder).filter(OptionMultiLegOrder.id == order_id).first()
    return _serialize_order(order) if order else None


def list_multi_leg_orders(db: Session, symbol: Optional[str] = None) -> List[MultiLegOrderResponse]:
    """List saved multi-leg orders, optionally filtered by symbol."""

    query = db.query(OptionMultiLegOrder).order_by(OptionMultiLegOrder.created_at.desc())
    if symbol:
        query = query.filter(OptionMultiLegOrder.symbol == symbol.upper())

    return [_serialize_order(order) for order in query.all()]


def _serialize_order(order: OptionMultiLegOrder) -> MultiLegOrderResponse:
    legs = [
        OptionLegResponse(
            id=leg.id,
            action=leg.action,
            option_type=leg.option_type,
            strike=leg.strike_price,
            expiration=leg.expiration_date,
            quantity=leg.quantity,
            price=leg.limit_price,
            underlying_price=leg.underlying_price,
            implied_volatility=leg.implied_volatility,
            metadata=leg.metadata_json or {},
            contract_symbol=leg.source_symbol,
            order_id=leg.order_id,
            delta=leg.delta,
            gamma=leg.gamma,
            theta=leg.theta,
            vega=leg.vega,
            rho=leg.rho,
        )
        for leg in order.legs
    ]

    submission_payload = [
        {
            "symbol": order.symbol,
            "side": "buy" if leg.action == "BUY" else "sell",
            "qty": leg.quantity,
            "type": "limit" if leg.limit_price else "market",
            "asset_class": "option",
            "option_type": leg.option_type,
            "strike_price": leg.strike_price,
            "expiration_date": leg.expiration_date.isoformat(),
            "limit_price": leg.limit_price,
        }
        for leg in order.legs
    ]

    return MultiLegOrderResponse(
        id=order.id,
        symbol=order.symbol,
        strategy=order.strategy,  # type: ignore[arg-type]
        order_type=order.order_type,  # type: ignore[arg-type]
        net_price=order.net_price,
        underlying_price=order.underlying_price,
        status=order.status,
        notes=order.notes,
        metadata=order.metadata_json or {},
        created_at=order.created_at,
        updated_at=order.updated_at,
        legs=legs,
        order_submission=submission_payload,
    )


def _build_option_contract(
    symbol: str,
    option: Dict[str, object],
    expiration: str,
    underlying_price: Optional[float],
) -> OptionContract:
    option_type = str(option.get("option_type", "")).lower()
    strike = float(option.get("strike", 0))

    expiry_str = str(option.get("expiration_date") or expiration)
    expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
    dte = days_until_expiration(expiry_str)

    bid = _safe_float(option.get("bid"))
    ask = _safe_float(option.get("ask"))
    last = _safe_float(option.get("last"))
    mark = _mid_price(bid, ask)

    greeks_data = option.get("greeks", {}) or {}
    iv = greeks_data.get("mid_iv")
    normalized_iv = _normalize_iv(iv)

    underlying_for_contract = _safe_float(option.get("underlying_price")) or underlying_price
    price_for_iv = mark or last

    if normalized_iv is None and price_for_iv and underlying_for_contract:
        normalized_iv = greeks_calculator.calculate_implied_volatility(
            option_type,
            price_for_iv,
            underlying_for_contract,
            strike,
            dte,
        )

    greeks_payload: Dict[str, float] = {}
    if normalized_iv and underlying_for_contract:
        try:
            greeks_payload = greeks_calculator.calculate_greeks(
                option_type,
                underlying_for_contract,
                strike,
                dte,
                normalized_iv,
            )
        except ValueError:
            greeks_payload = {}

    return OptionContract(
        symbol=str(option.get("symbol") or _build_occ_symbol(symbol, expiry_date, option_type, strike)),
        underlying_symbol=symbol,
        option_type=option_type,  # type: ignore[arg-type]
        strike_price=strike,
        expiration_date=expiry_date,
        bid=bid,
        ask=ask,
        last_price=last,
        mark_price=mark,
        volume=_safe_int(option.get("volume")),
        open_interest=_safe_int(option.get("open_interest")),
        implied_volatility=normalized_iv,
        greeks=OptionGreeks(**greeks_payload),
        days_to_expiration=dte,
        updated_at=_parse_datetime(option.get("trade_date")) or datetime.utcnow(),
    )


def _analyze_leg(symbol: str, leg: OptionLegCreate, fallback_underlying: Optional[float]) -> Dict[str, object]:
    expiry_str = leg.expiration.isoformat()
    days = days_until_expiration(expiry_str)

    underlying = leg.underlying_price or fallback_underlying
    normalized_iv = _normalize_iv(leg.implied_volatility)

    if normalized_iv is None and leg.price and underlying:
        normalized_iv = greeks_calculator.calculate_implied_volatility(
            leg.option_type,
            leg.price,
            underlying,
            leg.strike,
            days,
        )

    greeks_payload: Dict[str, float] = {}
    if normalized_iv and underlying:
        try:
            greeks_payload = greeks_calculator.calculate_greeks(
                leg.option_type,
                underlying,
                leg.strike,
                days,
                normalized_iv,
            )
        except ValueError:
            greeks_payload = {}

    return {
        "underlying_price": underlying,
        "implied_volatility": normalized_iv,
        "greeks": greeks_payload,
        "symbol": _build_occ_symbol(symbol, leg.expiration, leg.option_type, leg.strike),
    }


def _resolve_net_price(payload: MultiLegOrderCreate) -> float:
    if payload.net_price is not None:
        return float(payload.net_price)

    total = 0.0
    for leg in payload.legs:
        price = leg.price or 0.0
        multiplier = 1 if leg.action == "BUY" else -1
        total += multiplier * price * leg.quantity
    return total


def _resolve_order_type(order_type: Optional[str], net_price: float) -> str:
    if order_type:
        return order_type
    if net_price > 0:
        return "debit"
    if net_price < 0:
        return "credit"
    return "even"


def _extract_underlying_price(raw_chain: Dict[str, object]) -> Optional[float]:
    underlying = raw_chain.get("underlying") or {}
    if isinstance(underlying, dict):
        for key in ("last", "close", "price"):
            price = underlying.get(key)
            if price is not None:
                return _safe_float(price)
    return None


def _mid_price(bid: Optional[float], ask: Optional[float]) -> Optional[float]:
    if bid is None or ask is None:
        return None
    if bid <= 0 and ask <= 0:
        return None
    return round((bid + ask) / 2.0, 4)


def _normalize_iv(value: Optional[object]) -> Optional[float]:
    if value is None:
        return None
    try:
        iv = float(value)
    except (TypeError, ValueError):  # pragma: no cover - defensive
        return None

    if iv <= 0:
        return None
    if iv > 1.5:
        iv = iv / 100.0
    return iv


def _safe_float(value: Optional[object]) -> Optional[float]:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):  # pragma: no cover
        return None


def _safe_int(value: Optional[object]) -> Optional[int]:
    try:
        if value is None:
            return None
        return int(value)
    except (TypeError, ValueError):  # pragma: no cover
        return None


def _parse_datetime(value: Optional[object]) -> Optional[datetime]:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
    return None


def _build_occ_symbol(symbol: str, expiration: date | datetime, option_type: str, strike: float) -> str:
    if isinstance(expiration, datetime):
        expiry_date = expiration.date()
    else:
        expiry_date = expiration
    expiry_str = expiry_date.strftime("%y%m%d")
    call_put = "C" if option_type.lower().startswith("c") else "P"
    strike_int = int(round(strike * 1000))
    return f"{symbol.upper()}{expiry_str}{call_put}{strike_int:08d}"


def _average(values: Iterable[Optional[float]]) -> Optional[float]:
    nums = [v for v in values if v is not None]
    if not nums:
        return None
    return sum(nums) / len(nums)
