"""Strategy automation engine for stocks/options workflows."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from typing import Any

from .dex_meme_scout import DexMemeScoutConfig
from .under4_multileg import Under4MultilegConfig


@dataclass(slots=True)
class TradeProposal:
    symbol: str
    type: str
    strike: float
    price: float
    expiry: str
    delta: float
    notes: list[str]
    option_symbol: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "symbol": self.symbol,
            "type": self.type,
            "strike": self.strike,
            "price": self.price,
            "expiry": self.expiry,
            "delta": self.delta,
            "notes": self.notes,
        }
        if self.option_symbol:
            payload["option_symbol"] = self.option_symbol
        return payload


def generate_trade_plan(
    strategy_type: str,
    config: dict[str, Any],
    market_snapshot: dict[str, Any],
) -> dict[str, Any]:
    """Generate trade plan for the requested strategy."""

    if strategy_type == "under4-multileg":
        cfg = Under4MultilegConfig(**config)
        return _under4_multileg_plan(cfg, market_snapshot)

    if strategy_type == "dex-meme-scout":
        cfg = DexMemeScoutConfig(**config)
        return _dex_meme_plan(cfg, market_snapshot)

    return {
        "candidates": [],
        "proposals": [],
        "approved_trades": [],
        "analytics": {"status": "unsupported_strategy"},
    }


def _under4_multileg_plan(
    config: Under4MultilegConfig,
    market_snapshot: dict[str, Any],
) -> dict[str, Any]:
    quotes = _extract_quotes(market_snapshot)
    account = market_snapshot.get("account", {})
    positions = market_snapshot.get("positions", [])

    candidates: list[str] = []
    proposals: list[dict[str, Any]] = []

    for quote in quotes:
        symbol = quote.get("symbol") or quote.get("Symbol")
        if not isinstance(symbol, str):
            continue

        last_price = _float_or_none(
            quote.get("last")
            or quote.get("lastPrice")
            or quote.get("close")
            or quote.get("prevClose")
        )
        avg_volume = _int_or_zero(
            quote.get("average_volume")
            or quote.get("averageVolume")
            or quote.get("volume")
        )

        if last_price is None:
            continue

        if not (config.min_last_price <= last_price <= config.price_ceiling):
            continue

        if avg_volume < config.min_avg_volume:
            continue

        candidates.append(symbol)

        expiry = _format_expiry(config.options_filters.min_days_to_expiry)

        call_price = round(last_price * 0.04, 2)
        put_credit = round(last_price * 0.03, 2)
        strike_call = round(last_price * 1.05, 2)
        strike_put = round(last_price * 0.95, 2)

        proposals.append(
            TradeProposal(
                symbol=symbol,
                type="BUY_CALL",
                strike=strike_call,
                price=call_price,
                expiry=expiry,
                delta=config.buy_call.delta_target,
                notes=["Target 50% profit", "Stop loss 35%"],
            ).to_dict()
        )

        proposals.append(
            TradeProposal(
                symbol=symbol,
                type="SELL_PUT",
                strike=strike_put,
                price=put_credit,
                expiry=expiry,
                delta=config.sell_put.delta_target,
                notes=["Target 50% buyback", "Monitor collateral"],
                option_symbol=_build_option_symbol(symbol, expiry, "put", strike_put),
            ).to_dict()
        )

    approved = _apply_risk_management(proposals, account, positions, config)

    return {
        "candidates": candidates,
        "proposals": proposals,
        "approved_trades": approved,
        "analytics": {
            "proposals": len(proposals),
            "approved": len(approved),
            "cash": account.get("cash"),
            "equity": account.get("portfolio_value") or account.get("equity"),
        },
    }


def _apply_risk_management(
    proposals: Iterable[dict[str, Any]],
    account: dict[str, Any],
    positions: Iterable[dict[str, Any]],
    config: Under4MultilegConfig,
) -> list[dict[str, Any]]:
    current_positions = len(list(positions or []))
    approved: list[dict[str, Any]] = []

    cash = _float_or_none(account.get("cash")) or 0.0
    equity = (
        _float_or_none(account.get("portfolio_value") or account.get("equity")) or 0.0
    )

    for proposal in proposals:
        if current_positions >= config.max_positions:
            break

        if len(approved) >= config.max_new_positions_per_day:
            break

        sized = _size_trade(proposal, cash, equity, config)
        if sized:
            approved.append(sized)
            current_positions += 1

    return approved


def _size_trade(
    proposal: dict[str, Any],
    cash: float,
    equity: float,
    config: Under4MultilegConfig,
) -> dict[str, Any] | None:
    per_trade_cap = equity * (config.sizing.per_trade_cash_pct / 100)
    buffer = equity * (config.cash_buffer_pct / 100)
    usable_cash = max(0.0, cash - config.sizing.min_cash_reserve_usd - buffer)
    allocation = min(per_trade_cap, usable_cash)

    if proposal["type"] == "BUY_CALL":
        price = proposal["price"]
        contracts = int(allocation / (price * 100))
        contracts = min(contracts, config.sizing.max_contracts_per_leg)
        if contracts >= 1:
            return {
                **proposal,
                "qty": contracts,
                "cost": round(contracts * price * 100, 2),
            }

    if proposal["type"] == "SELL_PUT":
        strike = proposal["strike"]
        collateral_cap = equity * (
            config.risk.max_notional_short_put_collateral_pct / 100
        )
        contracts = int(collateral_cap / (strike * 100))
        contracts = min(contracts, config.sizing.max_contracts_per_leg)
        if contracts >= 1:
            return {
                **proposal,
                "qty": contracts,
                "collateral": round(contracts * strike * 100, 2),
                "option_symbol": _build_option_symbol(
                    proposal["symbol"], proposal["expiry"], "put", strike
                ),
                "order_side": "sell_to_open",
            }

    return None


def _extract_quotes(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    quotes = snapshot.get("quotes", {})
    if isinstance(quotes, dict):
        items = quotes.get("items") or quotes.get("quote")
        if isinstance(items, list):
            return [item for item in items if isinstance(item, dict)]
        if isinstance(items, dict):
            return [items]
    if isinstance(quotes, list):
        return [item for item in quotes if isinstance(item, dict)]
    return []


def _format_expiry(min_days: int) -> str:
    target = datetime.now(UTC) + timedelta(days=max(min_days, 14))
    return date(target.year, target.month, target.day).isoformat()


def _float_or_none(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _int_or_zero(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _dex_meme_plan(
    config: DexMemeScoutConfig,
    market_snapshot: dict[str, Any],
) -> dict[str, Any]:
    prices = market_snapshot.get("prices", {})
    items = prices.get("items", {}) if isinstance(prices, dict) else {}

    candidates: list[str] = []
    proposals: list[dict[str, Any]] = []

    for token in config.tokens:
        token_upper = token.upper()
        price_info = items.get(token_upper)
        usd_price = _float_or_none(price_info.get("usd") if price_info else None)
        if usd_price is None:
            continue

        candidates.append(token_upper)
        proposals.append(
            {
                "type": "BUY_TOKEN",
                "symbol": token_upper,
                "price": usd_price,
                "allocation_usd": config.allocation_usd,
                "notes": [
                    "Allocate fixed USD amount",
                    f"Momentum window {config.momentum_window_minutes}m",
                ],
            }
        )

    return {
        "candidates": candidates,
        "proposals": proposals,
        "approved_trades": proposals[: config.max_new_positions],
        "analytics": {
            "proposals": len(proposals),
            "approved": min(len(proposals), config.max_new_positions),
            "tokens": config.tokens,
        },
    }


def _build_option_symbol(
    underlying: str, expiry: str, option_type: str, strike: float
) -> str:
    yy = expiry[2:4]
    mm = expiry[5:7]
    dd = expiry[8:10]
    type_code = "C" if option_type.lower() == "call" else "P"
    strike_int = round(strike * 1000)
    strike_str = f"{strike_int:08d}"
    return f"{underlying.upper()}{yy}{mm}{dd}{type_code}{strike_str}"


__all__ = ["generate_trade_plan"]
