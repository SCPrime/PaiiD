"""DEX meme coin module placeholder for PaiiD."""

from __future__ import annotations

from collections.abc import Iterable

from ..base import MarketBootstrapResult, MarketContext, MarketStrategy
from ..registry import register_market_strategy


class DexMemeCoinStrategy(MarketStrategy):
    market_key = "dex_meme_coins"
    supported_modes = ("paper",)

    def bootstrap(self, context: MarketContext) -> MarketBootstrapResult:
        services = {
            "price_oracle": "TODO: wire DEX oracle",
            "execution_router": "TODO: connect wallet execution",
        }
        notes: Iterable[str] = (
            "Shared architecture with PaiiD-2mx; enable once DEX services are ready",
        )
        return MarketBootstrapResult(
            services=services,
            background_tasks=("dex-stream",),
            notes=notes,
        )

    def readiness_checks(self, context: MarketContext) -> Iterable[str]:
        return (
            "dex.rpc.health",
            "wallet.signer",
        )


register_market_strategy(DexMemeCoinStrategy.market_key, DexMemeCoinStrategy)
