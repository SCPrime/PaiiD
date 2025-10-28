"""
Alpaca Paper Trading API Client
Handles: Account, Positions, Orders for Paper Trading ONLY
Market Data comes from Tradier API
"""

import logging
import os

from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import LimitOrderRequest, MarketOrderRequest


logger = logging.getLogger(__name__)


class AlpacaClient:
    """Alpaca Paper Trading client for account and position management"""

    def __init__(self):
        self.api_key = os.getenv("ALPACA_PAPER_API_KEY")
        self.secret_key = os.getenv("ALPACA_PAPER_SECRET_KEY")

        if not self.api_key or not self.secret_key:
            raise ValueError("ALPACA_PAPER_API_KEY and ALPACA_PAPER_SECRET_KEY must be set in .env")

        # Initialize Alpaca Trading Client for Paper Trading
        self.client = TradingClient(
            api_key=self.api_key,
            secret_key=self.secret_key,
            paper=True,  # CRITICAL: Paper trading mode
        )

        logger.info("Alpaca Paper Trading client initialized")

    def get_account(self) -> dict:
        """Get Alpaca paper trading account information"""
        try:
            account = self.client.get_account()
            logger.info(f"✅ Alpaca account retrieved: {account.account_number}")

            # Convert to dict format matching frontend expectations
            return {
                "account_number": account.account_number,
                "status": account.status.value,
                "currency": account.currency,
                "cash": float(account.cash),
                "portfolio_value": float(account.portfolio_value),
                "buying_power": float(account.buying_power),
                "equity": float(account.equity),
                "last_equity": float(account.last_equity),
                "long_market_value": float(account.long_market_value),
                "short_market_value": float(account.short_market_value),
                "initial_margin": float(account.initial_margin),
                "maintenance_margin": float(account.maintenance_margin),
                "daytrade_count": account.daytrade_count,
                "daytrading_buying_power": float(account.daytrading_buying_power),
                "regt_buying_power": float(account.regt_buying_power),
                "pattern_day_trader": account.pattern_day_trader,
                "trading_blocked": account.trading_blocked,
                "transfers_blocked": account.transfers_blocked,
                "account_blocked": account.account_blocked,
                "created_at": account.created_at.isoformat() if account.created_at else None,
            }

        except Exception as e:
            logger.error(f"❌ Alpaca get_account failed: {e!s}")
            raise Exception(f"Alpaca account request failed: {e!s}")

    def get_positions(self) -> list[dict]:
        """Get all open positions from Alpaca paper trading account"""
        try:
            positions = self.client.get_all_positions()
            logger.info(f"✅ Alpaca positions retrieved: {len(positions)} positions")

            # Convert to dict format matching frontend expectations
            positions_data = []
            for pos in positions:
                positions_data.append(
                    {
                        "symbol": pos.symbol,
                        "qty": float(pos.qty),
                        "side": pos.side.value,
                        "market_value": float(pos.market_value),
                        "cost_basis": float(pos.cost_basis),
                        "unrealized_pl": float(pos.unrealized_pl),
                        "unrealized_plpc": float(pos.unrealized_plpc),
                        "current_price": float(pos.current_price),
                        "avg_entry_price": float(pos.avg_entry_price),
                        "lastday_price": float(pos.lastday_price),
                        "change_today": float(pos.change_today),
                        "asset_id": str(pos.asset_id),
                        "exchange": pos.exchange.value if pos.exchange else None,
                        "asset_class": pos.asset_class.value,
                    }
                )

            return positions_data

        except Exception as e:
            logger.error(f"❌ Alpaca get_positions failed: {e!s}")
            raise Exception(f"Alpaca positions request failed: {e!s}")

    def place_market_order(self, symbol: str, qty: float, side: str) -> dict:
        """Place a market order on Alpaca paper trading account"""
        try:
            order_side = OrderSide.BUY if side.upper() == "BUY" else OrderSide.SELL

            market_order_data = MarketOrderRequest(
                symbol=symbol, qty=qty, side=order_side, time_in_force=TimeInForce.DAY
            )

            order = self.client.submit_order(order_data=market_order_data)
            logger.info(f"✅ Market order placed: {order.id} - {side} {qty} {symbol}")

            return {
                "id": str(order.id),
                "client_order_id": order.client_order_id,
                "symbol": order.symbol,
                "qty": float(order.qty),
                "side": order.side.value,
                "type": order.type.value,
                "status": order.status.value,
                "filled_qty": float(order.filled_qty) if order.filled_qty else 0,
                "filled_avg_price": float(order.filled_avg_price)
                if order.filled_avg_price
                else None,
                "created_at": order.created_at.isoformat() if order.created_at else None,
                "updated_at": order.updated_at.isoformat() if order.updated_at else None,
            }

        except Exception as e:
            logger.error(f"❌ Alpaca place_market_order failed: {e!s}")
            raise Exception(f"Failed to place market order: {e!s}")

    def place_limit_order(self, symbol: str, qty: float, side: str, limit_price: float) -> dict:
        """Place a limit order on Alpaca paper trading account"""
        try:
            order_side = OrderSide.BUY if side.upper() == "BUY" else OrderSide.SELL

            limit_order_data = LimitOrderRequest(
                symbol=symbol,
                qty=qty,
                side=order_side,
                time_in_force=TimeInForce.DAY,
                limit_price=limit_price,
            )

            order = self.client.submit_order(order_data=limit_order_data)
            logger.info(
                f"✅ Limit order placed: {order.id} - {side} {qty} {symbol} @ ${limit_price}"
            )

            return {
                "id": str(order.id),
                "client_order_id": order.client_order_id,
                "symbol": order.symbol,
                "qty": float(order.qty),
                "side": order.side.value,
                "type": order.type.value,
                "limit_price": float(order.limit_price) if order.limit_price else None,
                "status": order.status.value,
                "filled_qty": float(order.filled_qty) if order.filled_qty else 0,
                "filled_avg_price": float(order.filled_avg_price)
                if order.filled_avg_price
                else None,
                "created_at": order.created_at.isoformat() if order.created_at else None,
                "updated_at": order.updated_at.isoformat() if order.updated_at else None,
            }

        except Exception as e:
            logger.error(f"❌ Alpaca place_limit_order failed: {e!s}")
            raise Exception(f"Failed to place limit order: {e!s}")

    def get_orders(self, status: str | None = None, limit: int = 100) -> list[dict]:
        """Get orders from Alpaca paper trading account"""
        try:
            from alpaca.trading.enums import QueryOrderStatus
            from alpaca.trading.requests import GetOrdersRequest

            # Map status string to enum
            status_filter = None
            if status:
                status_map = {
                    "open": QueryOrderStatus.OPEN,
                    "closed": QueryOrderStatus.CLOSED,
                    "all": QueryOrderStatus.ALL,
                }
                status_filter = status_map.get(status.lower(), QueryOrderStatus.ALL)
            else:
                status_filter = QueryOrderStatus.ALL

            request_params = GetOrdersRequest(status=status_filter, limit=limit)

            orders = self.client.get_orders(filter=request_params)
            logger.info(f"✅ Alpaca orders retrieved: {len(orders)} orders")

            orders_data = []
            for order in orders:
                orders_data.append(
                    {
                        "id": str(order.id),
                        "client_order_id": order.client_order_id,
                        "symbol": order.symbol,
                        "qty": float(order.qty),
                        "side": order.side.value,
                        "type": order.type.value,
                        "status": order.status.value,
                        "filled_qty": float(order.filled_qty) if order.filled_qty else 0,
                        "filled_avg_price": float(order.filled_avg_price)
                        if order.filled_avg_price
                        else None,
                        "limit_price": float(order.limit_price) if order.limit_price else None,
                        "stop_price": float(order.stop_price) if order.stop_price else None,
                        "created_at": order.created_at.isoformat() if order.created_at else None,
                        "updated_at": order.updated_at.isoformat() if order.updated_at else None,
                        "submitted_at": order.submitted_at.isoformat()
                        if order.submitted_at
                        else None,
                        "filled_at": order.filled_at.isoformat() if order.filled_at else None,
                    }
                )

            return orders_data

        except Exception as e:
            logger.error(f"❌ Alpaca get_orders failed: {e!s}")
            raise Exception(f"Failed to get orders: {e!s}")

    def cancel_order(self, order_id: str) -> dict:
        """Cancel an order by ID"""
        try:
            self.client.cancel_order_by_id(order_id)
            logger.info(f"✅ Order cancelled: {order_id}")
            return {"status": "cancelled", "order_id": order_id}

        except Exception as e:
            logger.error(f"❌ Alpaca cancel_order failed: {e!s}")
            raise Exception(f"Failed to cancel order: {e!s}")


# Singleton instance
_alpaca_client = None
_alpaca_available = False
_alpaca_unavailable_reason = None


def get_alpaca_client() -> AlpacaClient:
    """
    Get or create Alpaca client singleton with readiness registration

    Returns:
        AlpacaClient instance if available

    Raises:
        Exception: If Alpaca client is unavailable (registers reason in readiness registry)
    """
    global _alpaca_client, _alpaca_available, _alpaca_unavailable_reason

    if _alpaca_client is None:
        # Import here to avoid circular dependency
        from app.core.readiness_registry import get_readiness_registry
        registry = get_readiness_registry()

        try:
            _alpaca_client = AlpacaClient()
            _alpaca_available = True
            _alpaca_unavailable_reason = None
            registry.register("alpaca", available=True)
            logger.info("[OK] Alpaca Paper Trading client initialized and registered as available")
        except Exception as e:
            _alpaca_available = False
            _alpaca_unavailable_reason = str(e)
            registry.register("alpaca", available=False, reason=str(e))
            logger.error(f"[FAIL] Alpaca Paper Trading client initialization failed: {e}")
            raise Exception(f"Alpaca client unavailable: {e}")

    # Check if client is available
    if not _alpaca_available:
        raise Exception(f"Alpaca client unavailable: {_alpaca_unavailable_reason}")

    return _alpaca_client
