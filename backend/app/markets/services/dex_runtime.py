"""Runtime helpers for DEX meme coin strategies."""

from __future__ import annotations

import logging
from collections.abc import Iterable
from datetime import UTC, datetime
from typing import Any

from ...services.providers import get_dex_price_provider


logger = logging.getLogger(__name__)


class DexMemeRuntime:
    """Collect token prices and synthetic account metrics for DEX strategies."""

    def __init__(self) -> None:
        self.provider = get_dex_price_provider()

    def snapshot(self, tokens: Iterable[str] | None = None) -> dict[str, Any]:
        timestamp = datetime.now(UTC).isoformat().replace("+00:00", "Z")
        tickers = list(tokens or [])
        prices = self.provider.get_prices(tickers)

        return {
            "status": "ok" if prices.get("status") == "ok" else "degraded",
            "timestamp": timestamp,
            "prices": prices,
        }


__all__ = ["DexMemeRuntime"]
