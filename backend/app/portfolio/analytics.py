"""Portfolio level analytics helpers."""

from __future__ import annotations

import math
from typing import Any, Iterable, Mapping

from pydantic import BaseModel, Field

GREEK_FIELDS = ("delta", "gamma", "theta", "vega", "rho")


class PortfolioGreekTotals(BaseModel):
    """Aggregate Greek exposure across the entire portfolio."""

    delta: float = Field(default=0.0, description="Net delta exposure")
    gamma: float = Field(default=0.0, description="Net gamma exposure")
    theta: float = Field(default=0.0, description="Net theta exposure")
    vega: float = Field(default=0.0, description="Net vega exposure")
    rho: float = Field(default=0.0, description="Net rho exposure")

    def add(self, other: Mapping[str, float]) -> None:
        for greek in GREEK_FIELDS:
            setattr(self, greek, getattr(self, greek) + float(other.get(greek, 0.0)))


class PortfolioGreekBreakdown(BaseModel):
    """Per-position Greek snapshot including scaled exposures."""

    symbol: str
    quantity: float
    side: str
    multiplier: float
    greeks: dict[str, float]
    exposures: dict[str, float]


class PortfolioGreekAnalytics(BaseModel):
    """Complete view of portfolio Greeks."""

    totals: PortfolioGreekTotals
    breakdown: list[PortfolioGreekBreakdown]


def aggregate_greeks(positions: Iterable[Mapping[str, Any]]) -> PortfolioGreekAnalytics:
    """Aggregate Greeks across all holdings.

    Args:
        positions: Iterable of position payloads returned by the broker client.

    Returns:
        PortfolioGreekAnalytics summarising per-position exposures and portfolio totals.
    """

    totals = PortfolioGreekTotals()
    breakdown: list[PortfolioGreekBreakdown] = []

    for position in positions:
        if position is None:
            continue

        symbol = str(position.get("symbol", "UNKNOWN"))
        side = str(position.get("side", "long")).lower()
        direction = -1.0 if side in {"short", "sell", "sell_short", "sell-to-open"} else 1.0

        quantity = _safe_float(position.get("qty") or position.get("quantity") or 0.0)
        multiplier = _resolve_multiplier(position)

        greeks = _extract_greeks(position)

        exposures: dict[str, float] = {}
        for greek in GREEK_FIELDS:
            exposures[greek] = greeks[greek] * quantity * multiplier * direction

        totals.add(exposures)
        breakdown.append(
            PortfolioGreekBreakdown(
                symbol=symbol,
                quantity=quantity * direction,
                side=side,
                multiplier=multiplier,
                greeks=greeks,
                exposures=exposures,
            )
        )

    return PortfolioGreekAnalytics(totals=totals, breakdown=breakdown)


def _extract_greeks(position: Mapping[str, Any]) -> dict[str, float]:
    """Extract raw Greeks for a position with sensible defaults."""

    raw_greeks: Mapping[str, Any]
    candidate = position.get("greeks")
    if isinstance(candidate, Mapping):
        raw_greeks = candidate
    else:
        raw_greeks = position

    greeks: dict[str, float] = {}
    for greek in GREEK_FIELDS:
        value = _safe_float(raw_greeks.get(greek, 0.0))
        greeks[greek] = value

    # Provide an implied delta of 1 for equity holdings when Greeks are missing
    if _should_assume_equity_delta(position, greeks):
        greeks["delta"] = 1.0

    return greeks


def _resolve_multiplier(position: Mapping[str, Any]) -> float:
    """Infer the contract multiplier for the holding."""

    explicit = position.get("multiplier") or position.get("contract_multiplier")
    if explicit is not None:
        return abs(_safe_float(explicit)) or 1.0

    if _is_option(position):
        return 100.0

    return 1.0


def _is_option(position: Mapping[str, Any]) -> bool:
    asset_type = str(
        position.get("asset_type")
        or position.get("asset_class")
        or position.get("class")
        or position.get("security_type")
        or ""
    ).lower()
    if "option" in asset_type:
        return True

    symbol = str(position.get("symbol", ""))
    return any(token in symbol for token in (":", ".P", ".C", "-C", "-P"))


def _should_assume_equity_delta(position: Mapping[str, Any], greeks: Mapping[str, float]) -> bool:
    """Return True when we should fall back to delta=1 for equity holdings."""

    if _is_option(position):
        return False

    if any(not math.isclose(greeks[g], 0.0, abs_tol=1e-9) for g in GREEK_FIELDS):
        return False

    quantity = _safe_float(position.get("qty") or position.get("quantity") or 0.0)
    return quantity != 0.0


def _safe_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0
