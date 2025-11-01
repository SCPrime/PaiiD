"""Helpers for bootstrapping market modules at runtime."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict
from typing import Any

from .base import MarketContext
from .registry import bootstrap_market, get_market_strategy


def prepare_market_runtime(
    market_key: str,
    mode: str,
    instruments: Iterable[str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Bootstrap the requested market module and return runtime metadata."""

    context = MarketContext(
        market_key=market_key,
        mode=mode,
        instruments=list(instruments or []),
        metadata=metadata or {},
    )

    bootstrap = bootstrap_market(context)
    strategy = get_market_strategy(market_key)
    readiness = list(strategy.readiness_checks(context))

    return {
        "context": asdict(context),
        "services": bootstrap.services,
        "background_tasks": list(bootstrap.background_tasks),
        "notes": list(bootstrap.notes),
        "readiness_checks": readiness,
    }


__all__ = ["prepare_market_runtime"]
