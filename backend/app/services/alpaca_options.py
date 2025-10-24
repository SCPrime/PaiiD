"""
Alpaca Options API Client
Handles: Options chains, contract details, and options-specific data
Integrates with Greeks calculation for enriched options data
"""

import logging
import os
from datetime import datetime

from alpaca.data.historical import OptionHistoricalDataClient
from alpaca.data.requests import OptionChainRequest, OptionSnapshotRequest
from alpaca.trading.client import TradingClient

from .greeks import GreeksCalculator


logger = logging.getLogger(__name__)


class AlpacaOptionsClient:
    """Alpaca Options client for options chains and contract details"""

    def __init__(self):
        self.api_key = os.getenv("ALPACA_PAPER_API_KEY")
        self.secret_key = os.getenv("ALPACA_PAPER_SECRET_KEY")

        if not self.api_key or not self.secret_key:
            raise ValueError("ALPACA_PAPER_API_KEY and ALPACA_PAPER_SECRET_KEY must be set in .env")

        # Initialize Alpaca Options Data Client
        self.data_client = OptionHistoricalDataClient(
            api_key=self.api_key, secret_key=self.secret_key
        )

        # Initialize Trading Client for options trading
        self.trading_client = TradingClient(
            api_key=self.api_key, secret_key=self.secret_key, paper=True
        )

        # Initialize Greeks calculator
        self.greeks_calculator = GreeksCalculator(risk_free_rate=0.05)

        logger.info("✅ Alpaca Options client initialized (paper trading mode)")

    async def get_options_chain(
        self,
        symbol: str,
        expiration_date: str | None = None,
        option_type: str | None = None,
    ) -> dict:
        """
        Get options chain for a symbol with Greeks calculation

        Args:
            symbol: Underlying stock symbol (e.g., "AAPL")
            expiration_date: Optional expiration filter (YYYY-MM-DD)
            option_type: Optional filter ("call" or "put")

        Returns:
            Dict with enriched options chain including Greeks
        """
        try:
            logger.info(
                f"📊 Fetching options chain for {symbol} "
                f"(expiration={expiration_date}, type={option_type})"
            )

            # Build request for options chain
            request_params = {
                "symbol_or_symbols": symbol,
            }

            # Note: Alpaca's OptionChainRequest may not support all filters
            # We'll fetch and filter client-side if needed
            request = OptionChainRequest(**request_params)

            # Fetch options chain from Alpaca
            chain_data = self.data_client.get_option_chain(request)

            # Parse and enrich with Greeks
            calls = []
            puts = []

            # Get current underlying price for Greeks calculation
            # Note: In production, fetch from Tradier for real-time price
            underlying_price = 100.0  # Placeholder - will integrate with Tradier

            for contract_symbol, contract_data in chain_data.items():
                # Parse contract details from symbol
                # Alpaca option format: {underlying}{YYMMDD}{C/P}{price}
                # Example: AAPL250117C00150000
                parsed = self._parse_option_symbol(contract_symbol)

                if not parsed:
                    continue

                # Filter by expiration if specified
                if expiration_date and parsed["expiration"] != expiration_date:
                    continue

                # Filter by type if specified
                if option_type and parsed["type"].lower() != option_type.lower():
                    continue

                # Calculate Greeks
                days_to_expiry = self._days_to_expiration(parsed["expiration"])
                implied_vol = contract_data.get("implied_volatility", 0.3) or 0.3  # Default 30%

                greeks = self.greeks_calculator.calculate_greeks(
                    option_type=parsed["type"],
                    underlying_price=underlying_price,
                    strike_price=parsed["strike"],
                    days_to_expiry=days_to_expiry,
                    implied_volatility=implied_vol,
                )

                # Build enriched contract object
                enriched_contract = {
                    "option_symbol": contract_symbol,
                    "underlying_symbol": parsed["underlying"],
                    "strike_price": parsed["strike"],
                    "expiration_date": parsed["expiration"],
                    "option_type": parsed["type"],
                    "last_price": float(contract_data.get("last_price", 0) or 0),
                    "bid": float(contract_data.get("bid", 0) or 0),
                    "ask": float(contract_data.get("ask", 0) or 0),
                    "volume": int(contract_data.get("volume", 0) or 0),
                    "open_interest": int(contract_data.get("open_interest", 0) or 0),
                    "implied_volatility": implied_vol,
                    "delta": greeks["delta"],
                    "gamma": greeks["gamma"],
                    "theta": greeks["theta"],
                    "vega": greeks["vega"],
                    "in_the_money": self._is_itm(
                        parsed["type"], underlying_price, parsed["strike"]
                    ),
                }

                # Add to appropriate list
                if parsed["type"].lower() == "call":
                    calls.append(enriched_contract)
                else:
                    puts.append(enriched_contract)

            # Sort by strike price
            calls.sort(key=lambda x: x["strike_price"])
            puts.sort(key=lambda x: x["strike_price"])

            logger.info(f"✅ Options chain retrieved: {len(calls)} calls, {len(puts)} puts")

            return {
                "symbol": symbol,
                "underlying_price": underlying_price,
                "calls": calls,
                "puts": puts,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }

        except Exception as e:
            logger.error(f"❌ Failed to fetch options chain for {symbol}: {e!s}")
            raise

    async def get_contract_details(self, option_symbol: str) -> dict:
        """
        Get detailed information for a specific option contract

        Args:
            option_symbol: Full option symbol (e.g., "AAPL250117C00150000")

        Returns:
            Dict with contract details including Greeks
        """
        try:
            logger.info(f"📝 Fetching contract details for {option_symbol}")

            # Parse option symbol
            parsed = self._parse_option_symbol(option_symbol)
            if not parsed:
                raise ValueError(f"Invalid option symbol format: {option_symbol}")

            # Fetch contract snapshot from Alpaca
            request = OptionSnapshotRequest(symbol_or_symbols=option_symbol)
            snapshot = self.data_client.get_option_snapshot(request)

            contract_data = snapshot.get(option_symbol, {})

            # Get current underlying price (placeholder - integrate with Tradier)
            underlying_price = 100.0

            # Calculate Greeks
            days_to_expiry = self._days_to_expiration(parsed["expiration"])
            implied_vol = contract_data.get("implied_volatility", 0.3) or 0.3

            greeks = self.greeks_calculator.calculate_greeks(
                option_type=parsed["type"],
                underlying_price=underlying_price,
                strike_price=parsed["strike"],
                days_to_expiry=days_to_expiry,
                implied_volatility=implied_vol,
            )

            # Build detailed response
            details = {
                "option_symbol": option_symbol,
                "underlying_symbol": parsed["underlying"],
                "strike_price": parsed["strike"],
                "expiration_date": parsed["expiration"],
                "option_type": parsed["type"],
                "underlying_price": underlying_price,
                "last_price": float(contract_data.get("last_price", 0) or 0),
                "bid": float(contract_data.get("bid", 0) or 0),
                "ask": float(contract_data.get("ask", 0) or 0),
                "volume": int(contract_data.get("volume", 0) or 0),
                "open_interest": int(contract_data.get("open_interest", 0) or 0),
                "implied_volatility": implied_vol,
                "delta": greeks["delta"],
                "gamma": greeks["gamma"],
                "theta": greeks["theta"],
                "vega": greeks["vega"],
                "in_the_money": self._is_itm(parsed["type"], underlying_price, parsed["strike"]),
                "days_to_expiration": days_to_expiry,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }

            logger.info(f"✅ Contract details retrieved for {option_symbol}")
            return details

        except Exception as e:
            logger.error(f"❌ Failed to fetch contract details for {option_symbol}: {e!s}")
            raise

    async def get_expirations(self, symbol: str) -> list[str]:
        """
        Get available expiration dates for a symbol

        Args:
            symbol: Underlying stock symbol

        Returns:
            List of expiration dates in YYYY-MM-DD format
        """
        try:
            logger.info(f"📅 Fetching expirations for {symbol}")

            # Fetch full chain and extract unique expirations
            chain = await self.get_options_chain(symbol)

            expirations = set()
            for contract in chain["calls"] + chain["puts"]:
                expirations.add(contract["expiration_date"])

            expiration_list = sorted(expirations)

            logger.info(f"✅ Found {len(expiration_list)} expirations for {symbol}")
            return expiration_list

        except Exception as e:
            logger.error(f"❌ Failed to fetch expirations for {symbol}: {e!s}")
            raise

    def _parse_option_symbol(self, option_symbol: str) -> dict | None:
        """
        Parse Alpaca option symbol format

        Format: {underlying}{YYMMDD}{C/P}{price*1000 padded to 8 digits}
        Example: AAPL250117C00150000 = AAPL, exp 2025-01-17, Call, $150

        Returns:
            Dict with parsed components or None if invalid
        """
        try:
            # Find the date portion (6 digits YYMMDD)
            # Find C or P
            # Everything before is underlying
            # Everything after C/P is strike

            # Simple regex approach for common cases
            import re

            # Match pattern: {letters}{YYMMDD}{C|P}{8digits}
            match = re.match(r"([A-Z]+)(\d{6})([CP])(\d{8})", option_symbol)

            if not match:
                return None

            underlying = match.group(1)
            date_str = match.group(2)
            option_type = "call" if match.group(3) == "C" else "put"
            strike_str = match.group(4)

            # Parse date: YYMMDD -> YYYY-MM-DD
            year = int("20" + date_str[0:2])
            month = int(date_str[2:4])
            day = int(date_str[4:6])
            expiration = f"{year:04d}-{month:02d}-{day:02d}"

            # Parse strike: divide by 1000
            strike = float(strike_str) / 1000.0

            return {
                "underlying": underlying,
                "expiration": expiration,
                "type": option_type,
                "strike": strike,
            }

        except Exception as e:
            logger.warning(f"Failed to parse option symbol {option_symbol}: {e!s}")
            return None

    def _days_to_expiration(self, expiration_date: str) -> int:
        """Calculate days remaining until expiration"""
        try:
            exp_date = datetime.strptime(expiration_date, "%Y-%m-%d")
            today = datetime.utcnow()
            days = (exp_date - today).days
            return max(0, days)  # Never return negative
        except Exception:
            return 0

    def _is_itm(self, option_type: str, underlying_price: float, strike: float) -> bool:
        """Check if option is in-the-money"""
        if option_type.lower() == "call":
            return underlying_price > strike
        else:  # put
            return underlying_price < strike


# Singleton instance
_alpaca_options_client: AlpacaOptionsClient | None = None


def get_alpaca_options_client() -> AlpacaOptionsClient:
    """Get or create Alpaca Options client singleton"""
    global _alpaca_options_client
    if _alpaca_options_client is None:
        _alpaca_options_client = AlpacaOptionsClient()
    return _alpaca_options_client
