"""Alpaca provider wrapper for strategy execution."""

from __future__ import annotations

import logging
from typing import Any

from ..alpaca_client import AlpacaClient, get_alpaca_client


logger = logging.getLogger(__name__)


class AlpacaProvider:
    """High-level broker interactions for Alpaca."""

    def __init__(self) -> None:
        self.client: AlpacaClient = get_alpaca_client()

    async def get_account(self) -> dict[str, Any]:
        account = await self.client.get_account()
        return {
            "equity": float(account.equity),
            "cash": float(account.cash),
            "buying_power": float(account.buying_power),
            "portfolio_value": float(account.portfolio_value),
        }

    async def get_positions(self) -> list[dict[str, Any]]:
        positions = await self.client.get_positions()
        normalized: list[dict[str, Any]] = []
        for position in positions:
            normalized.append(
                {
                    "symbol": position.symbol,
                    "qty": float(position.qty),
                    "avg_entry_price": float(position.avg_entry_price),
                    "market_value": float(position.market_value),
                    "unrealized_pl": float(position.unrealized_pl),
                }
            )
        return normalized

    async def submit_order(
        self,
        symbol: str,
        qty: int,
        side: str,
        order_type: str,
        time_in_force: str,
        limit_price: float | None = None,
    ) -> dict[str, Any]:
        logger.info(
            "Submitting Alpaca order",
            extra={
                "symbol": symbol,
                "qty": qty,
                "side": side,
                "type": order_type,
                "time_in_force": time_in_force,
                "limit_price": limit_price,
            },
        )
        return await self.client.submit_order(
            symbol=symbol,
            qty=qty,
            side=side,
            type_=order_type,
            time_in_force=time_in_force,
            limit_price=limit_price,
        )


_alpaca_provider: AlpacaProvider | None = None


def get_alpaca_provider() -> AlpacaProvider:
    global _alpaca_provider
    if _alpaca_provider is None:
        _alpaca_provider = AlpacaProvider()
    return _alpaca_provider


__all__ = ["AlpacaProvider", "get_alpaca_provider"]
