"""Shared market strategy interfaces for PaiiD."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(slots=True)
class MarketContext:
    """Runtime context describing which market module to load."""

    market_key: str
    mode: str
    instruments: Iterable[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class MarketBootstrapResult:
    """Container for services and tasks returned by market strategies."""

    services: dict[str, Any]
    background_tasks: Iterable[str]
    notes: Iterable[str] = field(default_factory=list)


class MarketStrategy(Protocol):
    """Protocol describing the minimum contract for strategy modules."""

    market_key: str
    supported_modes: tuple[str, ...]

    def bootstrap(self, context: MarketContext) -> MarketBootstrapResult:
        """Return dependency wiring and startup tasks for the requested mode."""

    def readiness_checks(self, context: MarketContext) -> Iterable[str]:
        """Return identifiers for health checks required before activation."""
