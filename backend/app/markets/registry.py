# ruff: noqa: I001
"""Registry for PaiiD market strategies."""

from __future__ import annotations

from collections.abc import Callable, Iterable

from .base import MarketContext, MarketStrategy

MarketFactory = Callable[[], MarketStrategy]

_REGISTRY: dict[str, MarketFactory] = {}


def register_market_strategy(key: str, factory: MarketFactory) -> None:
    _REGISTRY[key] = factory


def get_market_strategy(key: str) -> MarketStrategy:
    try:
        factory = _REGISTRY[key]
    except KeyError as exc:  # pragma: no cover
        available = ", ".join(sorted(_REGISTRY)) or "<none>"
        raise KeyError(
            f"No market strategy registered for '{key}'. Available: {available}"
        ) from exc
    return factory()


def list_market_keys() -> Iterable[str]:
    return tuple(sorted(_REGISTRY))


def bootstrap_market(context: MarketContext):
    strategy = get_market_strategy(context.market_key)
    if context.mode not in strategy.supported_modes:
        supported = ", ".join(strategy.supported_modes)
        raise ValueError(
            f"Mode '{context.mode}' not supported for {context.market_key}. "
            f"Expected one of: {supported}."
        )
    return strategy.bootstrap(context)
