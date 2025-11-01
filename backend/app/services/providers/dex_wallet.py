"""DEX wallet routing provider.

Transforms approved DEX trades into actionable swap instructions while
validating required environment configuration. The actual signing/broadcasting
is delegated to the operator (kept manual by design).
"""

from __future__ import annotations

import os
from typing import Any


class DexWalletProvider:
    """Prepare swap instructions for DEX token purchases."""

    def __init__(self) -> None:
        self.rpc_url = os.getenv("DEX_RPC_URL")
        self.wallet_address = os.getenv("DEX_WALLET_ADDRESS")
        self.router_contract = os.getenv("DEX_ROUTER_CONTRACT", "uniswapV3")
        self.chain_id = os.getenv("DEX_CHAIN_ID", "137")  # default Polygon
        self.slippage_bps = int(os.getenv("DEX_SLIPPAGE_BPS", "75"))

    def readiness(self) -> dict[str, Any]:
        missing: list[str] = []
        if not self.rpc_url:
            missing.append("DEX_RPC_URL")
        if not self.wallet_address:
            missing.append("DEX_WALLET_ADDRESS")
        return {
            "is_ready": not missing,
            "missing": missing,
            "router": self.router_contract,
            "chain_id": self.chain_id,
        }

    def prepare_token_purchase(self, trade: dict[str, Any]) -> dict[str, Any]:
        readiness = self.readiness()
        allocation_usd = float(trade.get("allocation_usd") or 0)
        price = float(trade.get("price") or 0)
        symbol = trade.get("symbol")

        if not readiness["is_ready"]:
            return {
                "status": "manual_required",
                "reason": "dex_wallet_not_configured",
                "missing": readiness["missing"],
            }

        if not symbol or allocation_usd <= 0 or price <= 0:
            return {
                "status": "manual_required",
                "reason": "invalid_trade_payload",
            }

        estimated_tokens = round(allocation_usd / price, 8)

        instructions = {
            "wallet_address": self.wallet_address,
            "rpc_url": self.rpc_url,
            "router": self.router_contract,
            "chain_id": self.chain_id,
            "slippage_bps": self.slippage_bps,
            "token_symbol": symbol,
            "usd_allocation": allocation_usd,
            "reference_price_usd": price,
            "estimated_token_amount": estimated_tokens,
            "notes": [
                "Submit swap via preferred DEX aggregator",
                "Confirm gas cost and slippage tolerance prior to signing",
            ],
        }

        return {
            "status": "pending_signature",
            "instructions": instructions,
        }


_dex_wallet_provider: DexWalletProvider | None = None


def get_dex_wallet_provider() -> DexWalletProvider:
    global _dex_wallet_provider
    if _dex_wallet_provider is None:
        _dex_wallet_provider = DexWalletProvider()
    return _dex_wallet_provider


__all__ = ["DexWalletProvider", "get_dex_wallet_provider"]
