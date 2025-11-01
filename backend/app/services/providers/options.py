"""Options order provider for Alpaca."""

from __future__ import annotations

import logging
import os
from typing import Any

import requests


logger = logging.getLogger(__name__)


class AlpacaOptionsProvider:
    """Minimal wrapper to submit options orders via Alpaca REST API."""

    BASE_URL = os.getenv("ALPACA_PAPER_API_BASE", "https://paper-api.alpaca.markets")

    def __init__(self) -> None:
        self.api_key = os.getenv("ALPACA_PAPER_API_KEY")
        self.secret_key = os.getenv("ALPACA_PAPER_SECRET_KEY")
        if not self.api_key or not self.secret_key:
            raise ValueError(
                "ALPACA_PAPER_API_KEY and ALPACA_PAPER_SECRET_KEY must be set in .env"
            )

    def submit_option_order(
        self,
        symbol: str,
        qty: int,
        side: str,
        order_type: str = "market",
        time_in_force: str = "day",
        limit_price: float | None = None,
    ) -> dict[str, Any]:
        endpoint = f"{self.BASE_URL}/v2/options/orders"
        payload: dict[str, Any] = {
            "symbol": symbol,
            "qty": qty,
            "side": side.lower(),
            "type": order_type.lower(),
            "time_in_force": time_in_force.lower(),
        }

        if limit_price is not None and order_type.lower() == "limit":
            payload["limit_price"] = limit_price

        headers = {
            "APCA-API-KEY-ID": self.api_key,
            "APCA-API-SECRET-KEY": self.secret_key,
            "Content-Type": "application/json",
        }

        logger.info(
            "Submitting options order", extra={"symbol": symbol, "qty": qty, "side": side}
        )

        response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
        try:
            response.raise_for_status()
        except requests.RequestException as exc:  # pragma: no cover - network dependent
            logger.error("Options order failed: %s", exc)
            return {
                "status": "error",
                "message": str(exc),
                "payload": payload,
                "response": response.text,
            }

        return {
            "status": "submitted",
            "order": response.json(),
            "payload": payload,
        }


_alpaca_options_provider: AlpacaOptionsProvider | None = None


def get_alpaca_options_provider() -> AlpacaOptionsProvider:
    global _alpaca_options_provider
    if _alpaca_options_provider is None:
        _alpaca_options_provider = AlpacaOptionsProvider()
    return _alpaca_options_provider


__all__ = ["AlpacaOptionsProvider", "get_alpaca_options_provider"]

