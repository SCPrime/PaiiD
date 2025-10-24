"""
Position Tracking Service - Monitor open positions and calculate P&L
"""

import logging
from datetime import datetime, timezone

from pydantic import BaseModel

from app.services.alpaca_client import get_alpaca_client
from app.services.greeks import GreeksCalculator
from app.services.tradier_client import get_tradier_client

from app.core.time_utils import utc_now


logger = logging.getLogger(__name__)


class PositionGreeks(BaseModel):
    delta: float
    gamma: float
    theta: float
    vega: float


class Position(BaseModel):
    id: str
    symbol: str
    option_symbol: str
    qty: int
    avg_entry_price: float
    current_price: float
    unrealized_pl: float
    unrealized_pl_percent: float
    market_value: float
    cost_basis: float
    greeks: PositionGreeks
    expiration: str
    days_to_expiry: int
    status: str  # "open", "closing", "closed"


class PortfolioGreeks(BaseModel):
    total_delta: float
    total_gamma: float
    total_theta: float
    total_vega: float
    position_count: int


class PositionTrackerService:
    def __init__(self):
        self.alpaca = get_alpaca_client()
        self.tradier = get_tradier_client()
        self.greeks_calc = GreeksCalculator(risk_free_rate=0.05)

    async def get_open_positions(self) -> list[Position]:
        """Get all open option positions with real-time data"""
        try:
            # Get positions from Alpaca
            alpaca_positions = self.alpaca.get_positions()

            positions = []
            for pos in alpaca_positions:
                # Only process options
                if pos.asset_class != "option":
                    continue

                # Get current market data from Tradier
                quote = self.tradier.get_option_quote(pos.symbol)

                # Calculate Greeks
                greeks = self._calculate_position_greeks(pos, quote)

                # Calculate P&L
                current_price = quote.get("last", pos.current_price)
                unrealized_pl = (current_price - pos.avg_entry_price) * pos.qty * 100
                cost_basis = pos.avg_entry_price * pos.qty * 100
                unrealized_pl_percent = (
                    (unrealized_pl / cost_basis) * 100 if cost_basis else 0
                )

                position = Position(
                    id=pos.asset_id,
                    symbol=self._parse_underlying(pos.symbol),
                    option_symbol=pos.symbol,
                    qty=int(pos.qty),
                    avg_entry_price=float(pos.avg_entry_price),
                    current_price=current_price,
                    unrealized_pl=unrealized_pl,
                    unrealized_pl_percent=unrealized_pl_percent,
                    market_value=float(pos.market_value),
                    cost_basis=cost_basis,
                    greeks=greeks,
                    expiration=self._parse_expiration(pos.symbol),
                    days_to_expiry=self._calculate_dte(pos.symbol),
                    status="open",
                )

                positions.append(position)

            return positions

        except Exception as e:
            logger.error(f"Failed to fetch positions: {e}")
            return []

    async def get_portfolio_greeks(self) -> PortfolioGreeks:
        """Calculate aggregate portfolio Greeks"""
        positions = await self.get_open_positions()

        total_delta = sum(p.greeks.delta * p.qty for p in positions)
        total_gamma = sum(p.greeks.gamma * p.qty for p in positions)
        total_theta = sum(p.greeks.theta * p.qty for p in positions)
        total_vega = sum(p.greeks.vega * p.qty for p in positions)

        return PortfolioGreeks(
            total_delta=total_delta,
            total_gamma=total_gamma,
            total_theta=total_theta,
            total_vega=total_vega,
            position_count=len(positions),
        )

    async def close_position(
        self, position_id: str, limit_price: float | None = None
    ) -> dict:
        """Close an open position"""
        try:
            # Get position details
            position = self.alpaca.get_position(position_id)

            # Create closing order (opposite side)
            side = "sell" if int(position.qty) > 0 else "buy"
            qty = abs(int(position.qty))

            order_data = {
                "symbol": position.symbol,
                "qty": qty,
                "side": side,
                "type": "limit" if limit_price else "market",
                "time_in_force": "day",
                "order_class": "simple",
            }

            if limit_price:
                order_data["limit_price"] = limit_price

            # Submit closing order
            order = self.alpaca.submit_order(**order_data)

            logger.info(f"Closing order submitted: {order.id}")

            return {
                "status": "submitted",
                "order_id": order.id,
                "symbol": position.symbol,
                "qty": qty,
                "side": side,
            }

        except Exception as e:
            logger.error(f"Failed to close position: {e}")
            raise

    def _calculate_position_greeks(self, position, quote) -> PositionGreeks:
        """Calculate Greeks for a position"""
        try:
            # Parse option symbol
            option_type, strike, expiration = self._parse_option_symbol(position.symbol)

            # Get underlying price
            underlying_price = quote.get("underlying_price", 0)

            # Calculate Greeks
            days_to_expiry = self._calculate_dte(position.symbol)
            iv = quote.get("greeks", {}).get("mid_iv", 0.3)

            greeks = self.greeks_calc.calculate_greeks(
                option_type=option_type,
                underlying_price=underlying_price,
                strike_price=strike,
                days_to_expiry=days_to_expiry,
                implied_volatility=iv,
            )

            return PositionGreeks(**greeks)

        except Exception as e:
            logger.warning(f"Failed to calculate Greeks: {e}")
            return PositionGreeks(delta=0, gamma=0, theta=0, vega=0)

    def _parse_underlying(self, option_symbol: str) -> str:
        """Extract underlying symbol from option symbol"""
        # OCC format: SPY250117C00590000
        return option_symbol[
            : option_symbol.index(next(c for c in option_symbol if c.isdigit()))
        ]

    def _parse_expiration(self, option_symbol: str) -> str:
        """Extract expiration date from option symbol"""
        # OCC format: SPY250117C00590000 -> 2025-01-17
        date_part = option_symbol[
            option_symbol.index(
                next(c for c in option_symbol if c.isdigit())
            ) : option_symbol.index(next(c for c in option_symbol if c in "CP"))
        ]
        return f"20{date_part[:2]}-{date_part[2:4]}-{date_part[4:6]}"

    def _parse_option_symbol(self, option_symbol: str):
        """Parse option symbol into components"""
        # Extract type
        option_type = "call" if "C" in option_symbol else "put"

        # Extract strike
        strike_part = option_symbol[
            option_symbol.index(next(c for c in option_symbol if c in "CP")) + 1 :
        ]
        strike = float(strike_part) / 1000

        # Extract expiration
        expiration = self._parse_expiration(option_symbol)

        return option_type, strike, expiration

    def _calculate_dte(self, option_symbol: str) -> int:
        """Calculate days to expiration"""
        expiration_str = self._parse_expiration(option_symbol)
        expiration = datetime.strptime(expiration_str, "%Y-%m-%d").replace(
            tzinfo=timezone.utc
        )
        return (expiration - utc_now()).days
