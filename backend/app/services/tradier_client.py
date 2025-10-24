"""Tradier API client helpers for market data and trading."""

from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Any, Dict, Iterable, Literal

import requests


logger = logging.getLogger(__name__)


OptionSide = Literal["call", "put"]
OrderSide = Literal["buy", "sell", "buy_to_open", "buy_to_close", "sell_to_open", "sell_to_close"]
OrderType = Literal["market", "limit", "stop", "stop_limit"]
OrderDuration = Literal["day", "gtc", "pre", "post", "gtc_pre", "gtc_post"]


class TradierClient:
    """Tradier API client for production trading"""

    def __init__(self):
        self.api_key = os.getenv("TRADIER_API_KEY")
        self.account_id = os.getenv("TRADIER_ACCOUNT_ID")
        self.base_url = os.getenv("TRADIER_API_BASE_URL", "https://api.tradier.com/v1")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate",  # Enable compression for faster responses
        }

        if not self.api_key or not self.account_id:
            raise ValueError("TRADIER_API_KEY and TRADIER_ACCOUNT_ID must be set in .env")

        logger.info(f"Tradier client initialized for account {self.account_id}")

    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Make authenticated request to Tradier API with compression and timeouts"""
        url = f"{self.base_url}{endpoint}"

        # Set default timeout if not provided
        if "timeout" not in kwargs:
            kwargs["timeout"] = 5  # Reduced from 10s to 5s for faster failures

        try:
            response = requests.request(method=method, url=url, headers=self.headers, **kwargs)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            logger.error(f"Tradier API error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Tradier API error: {e.response.text}")

        except Exception as e:
            logger.error(f"Tradier request failed: {e!s}")
            raise

    # ==================== ACCOUNT ====================

    def get_profile(self) -> dict:
        """Get user profile"""
        return self._request("GET", "/user/profile")

    def get_account(self) -> dict:
        """Get account balances"""
        result = self._request("GET", f"/accounts/{self.account_id}/balances")
        if "balances" in result:
            balances = result["balances"]
            return {
                "account_number": self.account_id,
                "cash": float(balances.get("total_cash", 0)),
                "buying_power": float(balances.get("option_buying_power", 0)),
                "portfolio_value": float(balances.get("total_equity", 0)),
                "equity": float(balances.get("total_equity", 0)),
                "long_market_value": float(balances.get("long_market_value", 0)),
                "short_market_value": float(balances.get("short_market_value", 0)),
                "status": "ACTIVE",
            }
        return result

    def get_positions(self) -> list[dict]:
        """Get all positions"""
        response = self._request("GET", f"/accounts/{self.account_id}/positions")

        if "positions" in response and response["positions"] != "null":
            positions = response["positions"].get("position", [])

            # Normalize to list
            if isinstance(positions, dict):
                positions = [positions]

            return [self._normalize_position(p) for p in positions]

        return []

    def _normalize_position(self, pos: dict) -> dict:
        """Convert Tradier position to standard format"""
        quantity = float(pos.get("quantity", 0))
        cost_basis = float(pos.get("cost_basis", 0))

        return {
            "symbol": pos.get("symbol"),
            "qty": str(abs(quantity)),
            "side": "long" if quantity > 0 else "short",
            "avg_entry_price": str(cost_basis / abs(quantity) if quantity != 0 else 0),
            "market_value": pos.get("market_value"),
            "cost_basis": str(cost_basis),
            "unrealized_pl": pos.get("unrealized_pl"),
            "unrealized_plpc": pos.get("unrealized_plpc"),
            "current_price": pos.get("last"),
            "lastday_price": pos.get("prevclose"),
            "change_today": pos.get("change"),
        }

    # ==================== ORDERS ====================

    def get_orders(self) -> list[dict]:
        """Get all orders"""
        response = self._request("GET", f"/accounts/{self.account_id}/orders")

        if "orders" in response and response["orders"] != "null":
            orders = response["orders"].get("order", [])
            if isinstance(orders, dict):
                orders = [orders]
            return orders

        return []

    def place_order(
        self,
        symbol: str,
        side: str,
        quantity: int,
        order_type: str = "market",
        duration: str = "day",
        price: float | None = None,
        stop: float | None = None,
    ) -> dict:
        """
        Place an order

        Args:
            symbol: Stock symbol
            side: "buy", "sell", "buy_to_open", "sell_to_close", etc.
            quantity: Number of shares
            order_type: "market", "limit", "stop", "stop_limit"
            duration: "day", "gtc", "pre", "post"
            price: Limit price (for limit orders)
            stop: Stop price (for stop orders)
        """
        data = {
            "class": "equity",
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "type": order_type,
            "duration": duration,
        }

        if order_type in ["limit", "stop_limit"] and price:
            data["price"] = price

        if order_type in ["stop", "stop_limit"] and stop:
            data["stop"] = stop

        logger.info(f"Placing order: {data}")
        return self._request("POST", f"/accounts/{self.account_id}/orders", data=data)

    def cancel_order(self, order_id: str) -> dict:
        """Cancel an order"""
        return self._request("DELETE", f"/accounts/{self.account_id}/orders/{order_id}")

    # ==================== MARKET DATA ====================

    def get_quotes(self, symbols: list[str]) -> dict:
        """Get real-time quotes"""
        params = {"symbols": ",".join(symbols), "greeks": "false"}
        return self._request("GET", "/markets/quotes", params=params)

    def get_quote(self, symbol: str) -> dict:
        """Get single quote"""
        response = self.get_quotes([symbol])
        if "quotes" in response and "quote" in response["quotes"]:
            quotes = response["quotes"]["quote"]
            return quotes if isinstance(quotes, dict) else quotes[0]
        return {}

    def get_market_clock(self) -> dict:
        """Get market status"""
        return self._request("GET", "/markets/clock")

    def is_market_open(self) -> bool:
        """Check if market is open"""
        clock = self.get_market_clock()
        if "clock" in clock:
            return clock["clock"].get("state") == "open"
        return False

    def get_historical_bars(
        self,
        symbol: str,
        interval: str = "daily",
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[dict]:
        """
        Get historical OHLCV data from Tradier

        Args:
            symbol: Stock symbol (e.g., "AAPL")
            interval: "daily", "weekly", or "monthly"
            start_date: Start date in YYYY-MM-DD format (optional)
            end_date: End date in YYYY-MM-DD format (optional)

        Returns:
            List of bars with date, open, high, low, close, volume

        Example:
            [
                {
                    "date": "2024-01-15",
                    "open": 185.50,
                    "high": 187.20,
                    "low": 184.30,
                    "close": 186.75,
                    "volume": 45623100
                },
                ...
            ]
        """
        params = {"symbol": symbol, "interval": interval}

        if start_date:
            params["start"] = start_date
        if end_date:
            params["end"] = end_date

        logger.info(f"Fetching historical bars for {symbol} ({interval})")
        response = self._request("GET", "/markets/history", params=params)

        # Parse Tradier response
        if "history" in response and response["history"] != "null":
            bars = response["history"].get("day", [])

            # Tradier returns single bar as dict, multiple as list
            if isinstance(bars, dict):
                bars = [bars]

            # Convert to standard format
            normalized_bars = []
            for bar in bars:
                try:
                    normalized_bars.append(
                        {
                            "date": bar["date"],
                            "open": float(bar["open"]),
                            "high": float(bar["high"]),
                            "low": float(bar["low"]),
                            "close": float(bar["close"]),
                            "volume": int(bar["volume"]),
                        }
                    )
                except (KeyError, ValueError) as e:
                    logger.warning(f"Skipping malformed bar: {bar} - {e}")
                    continue

            logger.info(f"Retrieved {len(normalized_bars)} bars for {symbol}")
            return normalized_bars

        logger.warning(f"No historical data available for {symbol}")
        return []

    # ==================== OPTIONS ====================

    def get_option_chains(
        self,
        symbol: str,
        expiration: str | None = None,
        option_type: OptionSide | Literal["all"] = "all",
        strikes: int | None = None,
        include_greeks: bool = True,
    ) -> dict:
        """Fetch raw option chain data from Tradier."""

        params: dict[str, Any] = {
            "symbol": symbol,
            "greeks": str(include_greeks).lower(),
        }
        if expiration:
            params["expiration"] = expiration
        if option_type in ("call", "put"):
            params["option_type"] = option_type
        if strikes:
            params["strikes"] = strikes

        return self._request("GET", "/markets/options/chains", params=params)

    def get_normalized_option_chain(
        self,
        symbol: str,
        expiration: str | None = None,
        option_type: OptionSide | Literal["all"] = "all",
        strikes: int | None = None,
        min_volume: int | None = None,
        min_open_interest: int | None = None,
    ) -> dict:
        """Return normalized option chain data with aggregated Greeks exposure."""

        raw_chain = self.get_option_chains(
            symbol=symbol,
            expiration=expiration,
            option_type=option_type,
            strikes=strikes,
            include_greeks=True,
        )

        options_payload = raw_chain.get("options", {})
        raw_options: Iterable[dict[str, Any]]
        raw_options = options_payload.get("option", []) if options_payload else []

        if isinstance(raw_options, dict):
            raw_options = [raw_options]

        normalized_calls: list[dict[str, Any]] = []
        normalized_puts: list[dict[str, Any]] = []

        resolved_expiration = expiration
        for option in raw_options:
            contract = self._normalize_option_contract(option, symbol)

            if min_volume is not None and (contract.get("volume") or 0) < min_volume:
                continue
            if min_open_interest is not None and (contract.get("open_interest") or 0) < min_open_interest:
                continue

            resolved_expiration = contract.get("expiration_date") or resolved_expiration

            if contract.get("option_type") == "call":
                normalized_calls.append(contract)
            else:
                normalized_puts.append(contract)

        underlying_price = self._extract_underlying_price(raw_chain)

        greeks_exposure = {
            "calls": self._calculate_greeks_exposure(normalized_calls),
            "puts": self._calculate_greeks_exposure(normalized_puts),
        }
        greeks_exposure["net"] = {
            greek: round(greeks_exposure["calls"].get(greek, 0.0) + greeks_exposure["puts"].get(greek, 0.0), 6)
            for greek in {"delta", "gamma", "theta", "vega", "rho"}
        }

        normalized_payload: dict[str, Any] = {
            "symbol": symbol,
            "expiration_date": resolved_expiration,
            "underlying_price": underlying_price,
            "calls": normalized_calls,
            "puts": normalized_puts,
            "total_contracts": len(normalized_calls) + len(normalized_puts),
            "greeks_exposure": greeks_exposure,
            "as_of": datetime.utcnow().isoformat() + "Z",
            "raw": raw_chain,
        }

        return normalized_payload

    def get_option_expirations(self, symbol: str) -> dict:
        """Get option expiration dates"""
        params = {"symbol": symbol}
        return self._request("GET", "/markets/options/expirations", params=params)

    def place_option_order(
        self,
        symbol: str,
        option_symbol: str,
        side: OrderSide,
        quantity: int,
        order_type: OrderType = "market",
        duration: OrderDuration = "day",
        price: float | None = None,
        stop: float | None = None,
        preview: bool = False,
    ) -> dict:
        """Place a single-leg option order through Tradier."""

        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        payload: dict[str, Any] = {
            "class": "option",
            "symbol": symbol,
            "option_symbol": option_symbol,
            "side": side,
            "quantity": quantity,
            "type": order_type,
            "duration": duration,
        }

        if order_type in {"limit", "stop_limit"}:
            if price is None:
                raise ValueError("price is required for limit and stop_limit orders")
            payload["price"] = price

        if order_type in {"stop", "stop_limit"}:
            if stop is None:
                raise ValueError("stop price is required for stop and stop_limit orders")
            payload["stop"] = stop

        endpoint = f"/accounts/{self.account_id}/orders"
        if preview:
            payload["preview"] = "true"

        logger.info(
            "Placing option order",
            extra={
                "symbol": symbol,
                "option_symbol": option_symbol,
                "side": side,
                "quantity": quantity,
                "order_type": order_type,
                "duration": duration,
                "preview": preview,
            },
        )
        return self._request("POST", endpoint, data=payload)

    # ==================== HELPERS ====================

    def _normalize_option_contract(self, option: dict[str, Any], underlying_symbol: str) -> dict[str, Any]:
        greeks = option.get("greeks", {}) or {}

        def _to_float(value: Any) -> float | None:
            try:
                if value is None or value == "null":
                    return None
                return float(value)
            except (TypeError, ValueError):
                return None

        def _to_int(value: Any) -> int | None:
            try:
                if value is None or value == "null":
                    return None
                return int(value)
            except (TypeError, ValueError):
                return None

        normalized = {
            "symbol": option.get("symbol"),
            "underlying_symbol": underlying_symbol,
            "option_type": option.get("option_type"),
            "strike_price": _to_float(option.get("strike")),
            "expiration_date": option.get("expiration_date"),
            "bid": _to_float(option.get("bid")),
            "ask": _to_float(option.get("ask")),
            "last_price": _to_float(option.get("last")),
            "mid_price": _to_float(option.get("mid")),
            "volume": _to_int(option.get("volume")) or 0,
            "open_interest": _to_int(option.get("open_interest")) or 0,
            "delta": _to_float(greeks.get("delta")),
            "gamma": _to_float(greeks.get("gamma")),
            "theta": _to_float(greeks.get("theta")),
            "vega": _to_float(greeks.get("vega")),
            "rho": _to_float(greeks.get("rho")),
            "implied_volatility": _to_float(greeks.get("mid_iv")) or _to_float(option.get("implied_volatility")),
            "multiplier": _to_int(option.get("multiplier")) or 100,
            "updated_at": option.get("trade_date") or option.get("updated_at"),
        }

        return normalized

    def _calculate_greeks_exposure(self, contracts: Iterable[dict[str, Any]]) -> Dict[str, float]:
        totals: Dict[str, float] = {"delta": 0.0, "gamma": 0.0, "theta": 0.0, "vega": 0.0, "rho": 0.0}

        for contract in contracts:
            multiplier = contract.get("multiplier") or 100
            open_interest = contract.get("open_interest") or 0

            for greek in totals.keys():
                value = contract.get(greek)
                if value is None:
                    continue
                totals[greek] += float(value) * multiplier * open_interest

        return {key: round(val, 6) for key, val in totals.items()}

    def _extract_underlying_price(self, payload: dict[str, Any]) -> float | None:
        try:
            underlying = payload.get("underlying")
            if isinstance(underlying, dict):
                last = underlying.get("last")
                if last is not None:
                    return float(last)
            summary = payload.get("summary")
            if isinstance(summary, dict) and summary.get("last") is not None:
                return float(summary["last"])
        except (TypeError, ValueError):
            logger.debug("Unable to parse underlying price from Tradier payload", exc_info=True)
        return None


# Singleton instance
_tradier_client = None


def get_tradier_client() -> TradierClient:
    """Get singleton Tradier client"""
    global _tradier_client
    if _tradier_client is None:
        _tradier_client = TradierClient()
    return _tradier_client
