"""
Fixture Loader Service

Provides deterministic test data for Playwright testing when USE_TEST_FIXTURES=true.
This ensures consistent test results regardless of external API availability.
"""

import json
import logging
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any


logger = logging.getLogger(__name__)


class FixtureLoader:
    """
    Loads and provides test fixtures for deterministic testing.

    Fixtures are stored in backend/data/fixtures/ and provide:
    - Sample option chain data
    - Mock market data
    - Test user accounts
    - Expected API responses
    """

    def __init__(self):
        self.fixtures_dir = Path(__file__).parent.parent.parent / "data" / "fixtures"
        self.fixtures_dir.mkdir(parents=True, exist_ok=True)

        # Create options fixtures directory
        self.options_dir = self.fixtures_dir / "options"
        self.options_dir.mkdir(exist_ok=True)

        # Initialize fixtures if they don't exist
        self._ensure_fixtures_exist()

    def _ensure_fixtures_exist(self):
        """Create default fixtures if they don't exist"""

        # OPTT fixture (smaller option chain for testing)
        optt_fixture = self.options_dir / "optt.json"
        if not optt_fixture.exists():
            self._create_optt_fixture(optt_fixture)

        # SPY fixture (larger option chain for comprehensive testing)
        spy_fixture = self.options_dir / "spy.json"
        if not spy_fixture.exists():
            self._create_spy_fixture(spy_fixture)

        # Summary fixture (metadata about available fixtures)
        summary_fixture = self.fixtures_dir / "summary.playwright.json"
        if not summary_fixture.exists():
            self._create_summary_fixture(summary_fixture)

    def _create_optt_fixture(self, file_path: Path):
        """Create OPTT option chain fixture"""
        fixture_data = {
            "symbol": "OPTT",
            "underlying_price": 12.45,
            "expiration_dates": [
                {
                    "date": "2025-11-15",
                    "days_to_expiry": 23,
                    "calls": [
                        {
                            "symbol": "OPTT251115C00012500",
                            "strike": 12.50,
                            "bid": 0.15,
                            "ask": 0.20,
                            "last": 0.18,
                            "volume": 150,
                            "open_interest": 1200,
                            "delta": 0.45,
                            "gamma": 0.12,
                            "theta": -0.05,
                            "vega": 0.08,
                            "implied_volatility": 0.35,
                        }
                    ],
                    "puts": [
                        {
                            "symbol": "OPTT251115P00012500",
                            "strike": 12.50,
                            "bid": 0.10,
                            "ask": 0.15,
                            "last": 0.12,
                            "volume": 200,
                            "open_interest": 800,
                            "delta": -0.55,
                            "gamma": 0.12,
                            "theta": -0.04,
                            "vega": 0.08,
                            "implied_volatility": 0.38,
                        }
                    ],
                }
            ],
            "generated_at": datetime.now(UTC).isoformat(),
            "test_fixture": True,
        }

        with open(file_path, "w") as f:
            json.dump(fixture_data, f, indent=2)

        logger.info(f"Created OPTT fixture: {file_path}")

    def _create_spy_fixture(self, file_path: Path):
        """Create SPY option chain fixture"""
        # Generate multiple expiration dates
        base_date = datetime.now(UTC) + timedelta(days=7)
        expirations = []

        for i in range(3):  # 3 expiration dates
            exp_date = base_date + timedelta(days=i * 7)
            exp_date_str = exp_date.strftime("%Y-%m-%d")
            days_to_expiry = (exp_date - datetime.now(UTC)).days

            # Generate calls and puts around current price (assume SPY at $450)
            current_price = 450.0
            strikes = [
                current_price - 10,
                current_price - 5,
                current_price,
                current_price + 5,
                current_price + 10,
            ]

            calls = []
            puts = []

            for strike in strikes:
                # Call option
                calls.append(
                    {
                        "symbol": f"SPY{exp_date.strftime('%y%m%d')}C{int(strike * 1000):08d}",
                        "strike": strike,
                        "bid": max(0.01, abs(strike - current_price) * 0.1),
                        "ask": max(0.02, abs(strike - current_price) * 0.1 + 0.01),
                        "last": max(0.015, abs(strike - current_price) * 0.1 + 0.005),
                        "volume": int(abs(strike - current_price) * 10),
                        "open_interest": int(abs(strike - current_price) * 100),
                        "delta": 0.5
                        if strike == current_price
                        else (0.8 if strike < current_price else 0.2),
                        "gamma": 0.01,
                        "theta": -0.05,
                        "vega": 0.1,
                        "implied_volatility": 0.20,
                    }
                )

                # Put option
                puts.append(
                    {
                        "symbol": f"SPY{exp_date.strftime('%y%m%d')}P{int(strike * 1000):08d}",
                        "strike": strike,
                        "bid": max(0.01, abs(strike - current_price) * 0.1),
                        "ask": max(0.02, abs(strike - current_price) * 0.1 + 0.01),
                        "last": max(0.015, abs(strike - current_price) * 0.1 + 0.005),
                        "volume": int(abs(strike - current_price) * 10),
                        "open_interest": int(abs(strike - current_price) * 100),
                        "delta": -0.5
                        if strike == current_price
                        else (-0.8 if strike > current_price else -0.2),
                        "gamma": 0.01,
                        "theta": -0.04,
                        "vega": 0.1,
                        "implied_volatility": 0.22,
                    }
                )

            expirations.append(
                {
                    "date": exp_date_str,
                    "days_to_expiry": days_to_expiry,
                    "calls": calls,
                    "puts": puts,
                }
            )

        fixture_data = {
            "symbol": "SPY",
            "underlying_price": 450.0,
            "expiration_dates": expirations,
            "generated_at": datetime.now(UTC).isoformat(),
            "test_fixture": True,
        }

        with open(file_path, "w") as f:
            json.dump(fixture_data, f, indent=2)

        logger.info(f"Created SPY fixture: {file_path}")

    def _create_summary_fixture(self, file_path: Path):
        """Create summary fixture with metadata"""
        summary_data = {
            "fixtures": {
                "options": {
                    "optt": {
                        "symbol": "OPTT",
                        "description": "Small option chain for basic testing",
                        "expirations": 1,
                        "total_contracts": 2,
                    },
                    "spy": {
                        "symbol": "SPY",
                        "description": "Large option chain for comprehensive testing",
                        "expirations": 3,
                        "total_contracts": 30,
                    },
                }
            },
            "test_symbols": ["OPTT", "SPY"],
            "test_expirations": ["2025-11-15", "2025-11-22", "2025-11-29"],
            "generated_at": datetime.now(UTC).isoformat(),
            "version": "1.0.0",
        }

        with open(file_path, "w") as f:
            json.dump(summary_data, f, indent=2)

        logger.info(f"Created summary fixture: {file_path}")

    def load_options_chain(self, symbol: str) -> dict[str, Any] | None:
        """
        Load option chain fixture for a symbol.

        Args:
            symbol: Stock symbol (e.g., 'SPY', 'OPTT')

        Returns:
            Option chain data or None if not found
        """
        fixture_file = self.options_dir / f"{symbol.lower()}.json"

        if not fixture_file.exists():
            logger.warning(f"No fixture found for symbol: {symbol}")
            return None

        try:
            with open(fixture_file) as f:
                data = json.load(f)

            logger.info(
                f"Loaded fixture for {symbol}: {len(data.get('expiration_dates', []))} expirations"
            )
            return data

        except Exception as e:
            logger.error(f"Failed to load fixture for {symbol}: {e}")
            return None

    def load_expiration_dates(self, symbol: str) -> list[dict[str, Any]] | None:
        """
        Load expiration dates for a symbol.

        Args:
            symbol: Stock symbol

        Returns:
            List of expiration date objects
        """
        chain_data = self.load_options_chain(symbol)
        if not chain_data:
            return None

        return chain_data.get("expiration_dates", [])

    def get_available_symbols(self) -> list[str]:
        """Get list of symbols with available fixtures"""
        symbols = []
        for fixture_file in self.options_dir.glob("*.json"):
            symbol = fixture_file.stem.upper()
            symbols.append(symbol)
        return symbols

    def load_market_quotes(self, symbols: list[str]) -> dict[str, Any]:
        """
        Load market quote fixtures for symbols.

        Args:
            symbols: List of stock symbols

        Returns:
            Dictionary of quote data keyed by symbol
        """
        # Create market fixtures directory
        market_dir = self.fixtures_dir / "market"
        market_dir.mkdir(exist_ok=True)

        quotes_file = market_dir / "quotes.json"

        # Create quotes fixture if it doesn't exist
        if not quotes_file.exists():
            self._create_quotes_fixture(quotes_file)

        try:
            with open(quotes_file) as f:
                all_quotes = json.load(f)

            # Filter to requested symbols
            result = {}
            for symbol in symbols:
                symbol_upper = symbol.upper()
                if symbol_upper in all_quotes:
                    result[symbol_upper] = all_quotes[symbol_upper]
                else:
                    logger.warning(f"No fixture quote found for symbol: {symbol}")

            return result

        except Exception as e:
            logger.error(f"Failed to load quote fixtures: {e}")
            return {}

    def load_positions(self) -> list[dict[str, Any]]:
        """
        Load position fixtures.

        Returns:
            List of position data dictionaries
        """
        # Create positions fixtures directory
        positions_dir = self.fixtures_dir / "positions"
        positions_dir.mkdir(exist_ok=True)

        positions_file = positions_dir / "sample.json"

        # Create positions fixture if it doesn't exist
        if not positions_file.exists():
            self._create_positions_fixture(positions_file)

        try:
            with open(positions_file) as f:
                positions = json.load(f)

            return positions

        except Exception as e:
            logger.error(f"Failed to load position fixtures: {e}")
            return []

    def load_account_info(self) -> dict[str, Any]:
        """
        Load account info fixture.

        Returns:
            Account information dictionary
        """
        # Create account fixtures directory
        account_dir = self.fixtures_dir / "account"
        account_dir.mkdir(exist_ok=True)

        account_file = account_dir / "sample.json"

        # Create account fixture if it doesn't exist
        if not account_file.exists():
            self._create_account_fixture(account_file)

        try:
            with open(account_file) as f:
                account_data = json.load(f)

            return account_data

        except Exception as e:
            logger.error(f"Failed to load account fixture: {e}")
            return {}

    def _create_quotes_fixture(self, file_path: Path):
        """Create market quotes fixture"""
        quotes_data = {
            "SPY": {
                "bid": 450.0,
                "ask": 450.1,
                "last": 450.05,
                "volume": 50000000,
                "timestamp": datetime.now(UTC).isoformat(),
            },
            "QQQ": {
                "bid": 380.0,
                "ask": 380.1,
                "last": 380.05,
                "volume": 30000000,
                "timestamp": datetime.now(UTC).isoformat(),
            },
            "AAPL": {
                "bid": 175.0,
                "ask": 175.1,
                "last": 175.05,
                "volume": 40000000,
                "timestamp": datetime.now(UTC).isoformat(),
            },
            "MSFT": {
                "bid": 350.0,
                "ask": 350.1,
                "last": 350.05,
                "volume": 25000000,
                "timestamp": datetime.now(UTC).isoformat(),
            },
        }

        with open(file_path, "w") as f:
            json.dump(quotes_data, f, indent=2)

        logger.info(f"Created quotes fixture: {file_path}")

    def _create_positions_fixture(self, file_path: Path):
        """Create positions fixture"""
        positions_data = [
            {
                "id": "pos_001",
                "symbol": "SPY",
                "quantity": 100,
                "entry_price": 445.0,
                "current_price": 450.05,
                "unrealized_pnl": 505.0,
                "delta": 0.95,
                "gamma": 0.02,
                "theta": -0.15,
                "vega": 0.08,
                "rho": 0.01,
            },
            {
                "id": "pos_002",
                "symbol": "AAPL",
                "quantity": 50,
                "entry_price": 170.0,
                "current_price": 175.05,
                "unrealized_pnl": 252.5,
                "delta": 0.85,
                "gamma": 0.03,
                "theta": -0.20,
                "vega": 0.12,
                "rho": 0.02,
            },
        ]

        with open(file_path, "w") as f:
            json.dump(positions_data, f, indent=2)

        logger.info(f"Created positions fixture: {file_path}")

    def _create_account_fixture(self, file_path: Path):
        """Create account info fixture"""
        account_data = {
            "account_id": "test_account_001",
            "buying_power": 50000.0,
            "cash": 25000.0,
            "portfolio_value": 75000.0,
            "day_trading_buying_power": 100000.0,
            "regt_buying_power": 50000.0,
            "daytrading_buying_power": 100000.0,
            "non_marginable_buying_power": 25000.0,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        with open(file_path, "w") as f:
            json.dump(account_data, f, indent=2)

        logger.info(f"Created account fixture: {file_path}")


# Global fixture loader instance
_fixture_loader: FixtureLoader | None = None


def get_fixture_loader() -> FixtureLoader:
    """Get the global fixture loader instance"""
    global _fixture_loader
    if _fixture_loader is None:
        _fixture_loader = FixtureLoader()
    return _fixture_loader
