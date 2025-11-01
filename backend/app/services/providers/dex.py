"""DEX price provider using public APIs."""

from __future__ import annotations

import logging
from collections.abc import Iterable
from typing import Any

import requests


logger = logging.getLogger(__name__)


class DexPriceProvider:
    """Fetches token prices from public DEX/market APIs (Coingecko fallback)."""

    COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"

    def __init__(self, session: requests.Session | None = None) -> None:
        self.session = session or requests.Session()

    def get_prices(self, tickers: Iterable[str]) -> dict[str, Any]:
        ids = [self._coingecko_id(ticker) for ticker in tickers]
        ids = [token for token in ids if token]
        if not ids:
            return {"status": "empty"}

        params = {"ids": ",".join(ids), "vs_currencies": "usd"}
        try:
            response = self.session.get(self.COINGECKO_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            quotes = {
                ticker.upper(): {
                    "usd": data.get(token, {}).get("usd"),
                    "source": "coingecko",
                }
                for ticker, token in zip(tickers, ids, strict=False)
            }
            return {"status": "ok", "items": quotes}
        except requests.RequestException as exc:  # pragma: no cover - network specific
            logger.warning("DEX price fetch failed: %s", exc)
            return {"status": "error", "reason": str(exc)}

    def _coingecko_id(self, ticker: str) -> str | None:
        slug = ticker.lower()
        mapping: dict[str, str] = {
            "weth": "weth",
            "usdc": "usd-coin",
            "pepe": "pepe",
            "bonk": "bonk",
            "shib": "shiba-inu",
            "doge": "dogecoin",
        }
        return mapping.get(slug, slug)


_dex_provider: DexPriceProvider | None = None


def get_dex_price_provider() -> DexPriceProvider:
    global _dex_provider
    if _dex_provider is None:
        _dex_provider = DexPriceProvider()
    return _dex_provider


__all__ = ["DexPriceProvider", "get_dex_price_provider"]
