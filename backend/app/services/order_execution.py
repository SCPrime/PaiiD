"""
Order Execution Service - Handles options trade proposal and execution
"""

import logging
from dataclasses import asdict
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel

from app.services.alpaca_client import get_alpaca_client
from app.services.options_greeks import GreeksCalculator
from app.services.tradier_client import get_tradier_client


logger = logging.getLogger(__name__)


class OptionsProposal(BaseModel):
    """Options trade proposal with risk analysis"""

    symbol: str
    option_symbol: str
    contract_type: str  # "call" or "put"
    strike: float
    expiration: str
    premium: float
    quantity: int
    underlying_price: float
    greeks: dict[str, float]
    max_risk: float
    max_profit: float
    breakeven: float
    probability_of_profit: float
    iv_rank: Optional[float] = None
    risk_reward_ratio: float
    margin_requirement: float


class OrderExecutionService:
    """Service for creating and executing options orders with risk analysis"""

    def __init__(self):
        self.tradier = get_tradier_client()
        self.alpaca = get_alpaca_client()

    async def create_proposal(
        self,
        symbol: str,
        option_symbol: str,
        quantity: int,
        order_type: str = "limit",
    ) -> OptionsProposal:
        """
        Create a detailed options trade proposal with risk analysis

        Args:
            symbol: Underlying stock symbol (e.g., "SPY")
            option_symbol: Full option symbol (e.g., "SPY250117C00590000")
            quantity: Number of contracts
            order_type: "limit" or "market"

        Returns:
            OptionsProposal with greeks, risk metrics, and breakeven analysis
        """
        try:
            # Get option chain data from Tradier
            chain_data = await self._get_option_data(symbol, option_symbol)

            if not chain_data:
                raise ValueError(f"Could not find option data for {option_symbol}")

            # Parse option symbol to extract contract details
            contract_type, strike, expiration = self._parse_option_symbol(option_symbol)

            # Get underlying stock price
            quote = await self.tradier.get_quote(symbol)
            underlying_price = quote.get("last", 0)

            # Get premium (bid/ask midpoint for limit orders)
            premium = self._get_premium(chain_data, order_type)

            # Calculate Greeks
            calculator = GreeksCalculator(risk_free_rate=0.05)
            days_to_expiry = int(self._calculate_dte(expiration) * 365)
            time_to_expiry_years = max(days_to_expiry, 1) / 365
            iv = chain_data.get("greeks", {}).get("mid_iv", 0.3)
            greeks_obj = calculator.calculate_greeks(
                spot_price=underlying_price,
                strike_price=strike,
                time_to_expiry=time_to_expiry_years,
                volatility=iv if iv else 0.3,
                option_type=contract_type,
            )
            greeks = asdict(greeks_obj)

            # Calculate risk metrics
            risk_metrics = self._calculate_risk_metrics(
                contract_type=contract_type,
                strike=strike,
                premium=premium,
                quantity=quantity,
                underlying_price=underlying_price,
                greeks=greeks,
            )

            return OptionsProposal(
                symbol=symbol,
                option_symbol=option_symbol,
                contract_type=contract_type,
                strike=strike,
                expiration=expiration,
                premium=premium,
                quantity=quantity,
                underlying_price=underlying_price,
                greeks=greeks,
                **risk_metrics,
            )

        except Exception as e:
            logger.error(f"Failed to create proposal for {option_symbol}: {e}")
            raise

    async def execute_proposal(
        self,
        proposal: OptionsProposal,
        limit_price: Optional[float] = None,
    ) -> dict[str, Any]:
        """
        Execute an approved options trade proposal

        Args:
            proposal: Validated OptionsProposal
            limit_price: Optional limit price override

        Returns:
            Order confirmation with fill details
        """
        try:
            # Use Alpaca for paper trade execution
            order_data = {
                "symbol": proposal.option_symbol,
                "qty": proposal.quantity,
                "side": "buy",  # TODO: Support sell orders
                "type": "limit" if limit_price else "market",
                "time_in_force": "day",
                "order_class": "simple",
            }

            if limit_price:
                order_data["limit_price"] = limit_price
            elif proposal.premium:
                # Use proposal premium as limit price
                order_data["limit_price"] = proposal.premium

            # Submit order via Alpaca
            logger.info(f"Submitting order: {order_data}")
            order = await self.alpaca.submit_order(**order_data)

            return {
                "success": True,
                "order_id": order.get("id"),
                "status": order.get("status"),
                "filled_qty": order.get("filled_qty", 0),
                "filled_avg_price": order.get("filled_avg_price"),
                "submitted_at": order.get("submitted_at"),
                "proposal": proposal.dict(),
            }

        except Exception as e:
            logger.error(f"Failed to execute proposal: {e}")
            return {
                "success": False,
                "error": str(e),
                "proposal": proposal.dict(),
            }

    async def _get_option_data(self, symbol: str, option_symbol: str) -> dict:
        """Get option contract data from Tradier"""
        try:
            # Get expiration date from option symbol
            exp_date = self._parse_option_symbol(option_symbol)[2]

            # Fetch option chain
            chain = await self.tradier.get_option_chain(symbol, exp_date)

            # Find specific contract
            for contract in chain.get("options", {}).get("option", []):
                if contract.get("symbol") == option_symbol:
                    return contract

            return {}
        except Exception as e:
            logger.error(f"Error fetching option data: {e}")
            return {}

    def _parse_option_symbol(self, option_symbol: str) -> tuple[str, float, str]:
        """
        Parse OCC option symbol format
        Example: SPY250117C00590000
        - SPY: underlying
        - 250117: expiration (YYMMDD)
        - C: call/put
        - 00590000: strike price * 1000
        """
        # Find where the date starts (6 digits: YYMMDD)
        # OCC format: TICKER + YYMMDD + C/P + 8-digit strike
        import re

        match = re.match(r"([A-Z]+)(\d{6})([CP])(\d{8})", option_symbol)
        if not match:
            raise ValueError(f"Invalid option symbol format: {option_symbol}")

        ticker, exp_date, contract_type, strike_str = match.groups()

        # Parse expiration
        exp_year = f"20{exp_date[:2]}"
        exp_month = exp_date[2:4]
        exp_day = exp_date[4:6]
        expiration = f"{exp_year}-{exp_month}-{exp_day}"

        # Parse strike price (8 digits, divided by 1000)
        strike = float(strike_str) / 1000

        # Map contract type
        contract_type = "call" if contract_type == "C" else "put"

        return contract_type, strike, expiration

    def _calculate_dte(self, expiration: str) -> float:
        """Calculate days to expiration as a fraction of a year"""
        exp_date = datetime.strptime(expiration, "%Y-%m-%d")
        now = datetime.now()
        days = (exp_date - now).days
        return max(days / 365.0, 0.001)  # Avoid division by zero

    def _get_premium(self, chain_data: dict, order_type: str) -> float:
        """Get premium based on order type"""
        if order_type == "market":
            return chain_data.get("ask", 0)
        else:
            # Use midpoint for limit orders
            bid = chain_data.get("bid", 0)
            ask = chain_data.get("ask", 0)
            return (bid + ask) / 2 if (bid and ask) else ask

    def _calculate_risk_metrics(
        self,
        contract_type: str,
        strike: float,
        premium: float,
        quantity: int,
        underlying_price: float,
        greeks: dict,
    ) -> dict[str, float]:
        """Calculate comprehensive risk metrics"""

        # Max risk (premium paid)
        max_risk = premium * 100 * quantity  # Options are 100 shares per contract

        if contract_type == "call":
            # Call option metrics
            max_profit = float("inf")  # Theoretically unlimited
            breakeven = strike + premium
            probability_of_profit = max(0, min(100, greeks.get("delta", 0.5) * 100))
        else:
            # Put option metrics
            max_profit = (strike - premium) * 100 * quantity
            breakeven = strike - premium
            probability_of_profit = max(0, min(100, abs(greeks.get("delta", -0.5)) * 100))

        # Risk/reward ratio
        risk_reward_ratio = (
            max_profit / max_risk if max_risk > 0 and max_profit != float("inf") else 0
        )

        # Margin requirement (same as max risk for long options)
        margin_requirement = max_risk

        return {
            "max_risk": max_risk,
            "max_profit": max_profit if max_profit != float("inf") else 999999,
            "breakeven": breakeven,
            "probability_of_profit": probability_of_profit,
            "risk_reward_ratio": risk_reward_ratio,
            "margin_requirement": margin_requirement,
        }


# Singleton instance
_order_execution_service: Optional[OrderExecutionService] = None


def get_order_execution_service() -> OrderExecutionService:
    """Get or create the order execution service singleton"""
    global _order_execution_service
    if _order_execution_service is None:
        _order_execution_service = OrderExecutionService()
    return _order_execution_service
