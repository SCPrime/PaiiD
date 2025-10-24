"""Tradier API client with optional mock data for testing environments."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List

import requests

from app.core.config import settings


logger = logging.getLogger(__name__)


class TradierClient:
    """Tradier REST client with automatic mock fallbacks when credentials are absent."""

    def __init__(self) -> None:
        self.api_key = os.getenv("TRADIER_API_KEY", "")
        self.account_id = os.getenv("TRADIER_ACCOUNT_ID", "")
        self.base_url = os.getenv("TRADIER_API_BASE_URL", "https://api.tradier.com/v1")

        # In local development/CI we often do not have live Tradier credentials.
        # When TESTING mode is enabled (or credentials are missing) we provide a
        # deterministic mock implementation so the rest of the application can run.
        self.use_mock_data = settings.TESTING or not (self.api_key and self.account_id)

        if self.use_mock_data:
            self.account_id = self.account_id or "TEST-ACCOUNT"
            logger.warning(
                "Tradier client initialised in MOCK mode – no external API calls will be made."
            )
        else:
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json",
                "Accept-Encoding": "gzip, deflate",
            }
            logger.info("Tradier client initialised for account %s", self.account_id)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _request(self, method: str, endpoint: str, **kwargs: Any) -> Dict[str, Any]:
        """Perform an authenticated HTTP request to the Tradier API."""
        if self.use_mock_data:
            raise RuntimeError("Mock mode does not support raw HTTP requests")

        url = f"{self.base_url}{endpoint}"
        kwargs.setdefault("timeout", 5)

        try:
            response = requests.request(method=method, url=url, headers=self.headers, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as exc:  # pragma: no cover - network error path
            logger.error("Tradier API error: %s - %s", exc.response.status_code, exc.response.text)
            raise Exception(f"Tradier API error: {exc.response.text}") from exc
        except Exception as exc:  # pragma: no cover - network error path
            logger.error("Tradier request failed: %s", exc)
            raise

    def _mock_underlying_price(self, symbol: str) -> float:
        base_prices = {
            "SPY": 430.0,
            "AAPL": 185.0,
            "QQQ": 370.0,
            "TSLA": 250.0,
        }
        return base_prices.get(symbol.upper(), 100.0)

    def _mock_expirations(self, symbol: str) -> Dict[str, Dict[str, List[str]]]:
        today = datetime.utcnow().date()
        expirations = [
            (today + timedelta(days=7)).isoformat(),
            (today + timedelta(days=30)).isoformat(),
            (today + timedelta(days=60)).isoformat(),
        ]
        return {"expirations": {"date": expirations}}

    def _mock_chain(self, symbol: str, expiration: str | None = None) -> Dict[str, Any]:
        expiration = expiration or self._mock_expirations(symbol)["expirations"]["date"][0]
        underlying_price = self._mock_underlying_price(symbol)
        strikes = [underlying_price + offset for offset in (-10, -5, 0, 5, 10)]

        iv_base = 0.24
        options: List[Dict[str, Any]] = []

        for index, strike in enumerate(strikes):
            moneyness = (underlying_price - strike) / max(underlying_price, 1)
            delta_call = max(0.1, min(0.9, 0.55 + moneyness * 4 - index * 0.05))
            delta_put = delta_call - 1
            gamma = 0.01 + 0.002 * (1 - abs(moneyness))
            theta = -0.05 - abs(moneyness) * 0.03
            vega = 0.08 - 0.01 * abs(moneyness)
            rho_call = 0.04 - 0.005 * index
            rho_put = -rho_call

            bid_call = max(0.5, underlying_price - strike + 1.5)
            ask_call = bid_call + 0.35
            bid_put = max(0.4, strike - underlying_price + 1.2)
            ask_put = bid_put + 0.3

            options.append(
                {
                    "symbol": f"{symbol.upper()}-{expiration.replace('-', '')}-C-{int(round(strike))}",
                    "option_type": "call",
                    "strike": strike,
                    "expiration_date": expiration,
                    "bid": round(bid_call, 2),
                    "ask": round(ask_call, 2),
                    "last": round((bid_call + ask_call) / 2, 2),
                    "volume": int(800 - index * 45),
                    "open_interest": int(4800 - index * 320),
                    "greeks": {
                        "delta": round(delta_call, 4),
                        "gamma": round(gamma, 4),
                        "theta": round(theta, 4),
                        "vega": round(vega, 4),
                        "rho": round(rho_call, 4),
                        "mid_iv": round(iv_base, 4),
                    },
                }
            )

            options.append(
                {
                    "symbol": f"{symbol.upper()}-{expiration.replace('-', '')}-P-{int(round(strike))}",
                    "option_type": "put",
                    "strike": strike,
                    "expiration_date": expiration,
                    "bid": round(bid_put, 2),
                    "ask": round(ask_put, 2),
                    "last": round((bid_put + ask_put) / 2, 2),
                    "volume": int(700 - index * 40),
                    "open_interest": int(4200 - index * 280),
                    "greeks": {
                        "delta": round(delta_put, 4),
                        "gamma": round(gamma, 4),
                        "theta": round(theta, 4),
                        "vega": round(vega, 4),
                        "rho": round(rho_put, 4),
                        "mid_iv": round(iv_base + 0.01, 4),
                    },
                }
            )

        return {
            "underlying_price": underlying_price,
            "options": {"option": options},
        }

    def _mock_quote(self, symbol: str) -> Dict[str, Any]:
        price = self._mock_underlying_price(symbol)
        return {
            "symbol": symbol.upper(),
            "last": price,
            "bid": price - 0.35,
            "ask": price + 0.35,
            "close": price,
        }

    def _mock_history(self, symbol: str, interval: str) -> List[Dict[str, Any]]:
        base_price = self._mock_underlying_price(symbol)
        bars: List[Dict[str, Any]] = []
        today = datetime.utcnow().date()
        step = 1 if interval == "daily" else 5

        for idx in range(30):
            date = today - timedelta(days=idx * step)
            price = base_price + (idx % 5 - 2) * 0.75
            bars.append(
                {
                    "date": date.isoformat(),
                    "open": round(price - 0.4, 2),
                    "high": round(price + 0.6, 2),
                    "low": round(price - 0.8, 2),
                    "close": round(price, 2),
                    "volume": 1_000_000 + idx * 12_000,
                }
            )
        return list(reversed(bars))

    # ------------------------------------------------------------------
    # Public API - Account and positions
    # ------------------------------------------------------------------

    def get_profile(self) -> Dict[str, Any]:
        if self.use_mock_data:
            return {
                "profile": {
                    "account": self.account_id,
                    "name": "Mock Trader",
                    "status": "ACTIVE",
                }
            }
        return self._request("GET", "/user/profile")

    def get_account(self) -> Dict[str, Any]:
        if self.use_mock_data:
            balance = self._mock_underlying_price("SPY") * 1000
            return {
                "account_number": self.account_id,
                "cash": balance,
                "buying_power": balance * 2,
                "portfolio_value": balance * 2.5,
                "equity": balance * 2.5,
                "long_market_value": balance * 1.5,
                "short_market_value": 0.0,
                "status": "ACTIVE",
            }

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

    def get_positions(self) -> List[Dict[str, Any]]:
        if self.use_mock_data:
            return []

        response = self._request("GET", f"/accounts/{self.account_id}/positions")
        if "positions" in response and response["positions"] != "null":
            positions = response["positions"].get("position", [])
            if isinstance(positions, dict):
                positions = [positions]
            return [self._normalize_position(pos) for pos in positions]
        return []

    def _normalize_position(self, pos: Dict[str, Any]) -> Dict[str, Any]:
        quantity = float(pos.get("quantity", 0))
        cost_basis = float(pos.get("cost_basis", 0))
        return {
            "symbol": pos.get("symbol"),
            "qty": str(abs(quantity)),
            "side": "long" if quantity > 0 else "short",
            "avg_entry_price": str(cost_basis / abs(quantity) if quantity else 0),
            "market_value": pos.get("market_value"),
            "cost_basis": str(cost_basis),
            "unrealized_pl": pos.get("unrealized_pl"),
            "unrealized_plpc": pos.get("unrealized_plpc"),
            "current_price": pos.get("last"),
            "lastday_price": pos.get("prevclose"),
            "change_today": pos.get("change"),
        }

    def get_orders(self) -> List[Dict[str, Any]]:
        if self.use_mock_data:
            return []

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
    ) -> Dict[str, Any]:
        if self.use_mock_data:
            return {
                "id": "MOCK-ORDER",
                "symbol": symbol,
                "side": side,
                "quantity": quantity,
                "type": order_type,
                "status": "accepted",
                "submitted_at": datetime.utcnow().isoformat() + "Z",
            }

        data = {
            "class": "equity",
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "type": order_type,
            "duration": duration,
        }
        if order_type in {"limit", "stop_limit"} and price is not None:
            data["price"] = price
        if order_type in {"stop", "stop_limit"} and stop is not None:
            data["stop"] = stop

        logger.info("Placing Tradier order: %s", data)
        return self._request("POST", f"/accounts/{self.account_id}/orders", data=data)

    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        if self.use_mock_data:
            return {"status": "cancelled", "order_id": order_id}

        return self._request("DELETE", f"/accounts/{self.account_id}/orders/{order_id}")

    # ------------------------------------------------------------------
    # Market data
    # ------------------------------------------------------------------

    def get_quotes(self, symbols: List[str]) -> Dict[str, Any]:
        if self.use_mock_data:
            quotes = [self._mock_quote(sym) for sym in symbols]
            return {"quotes": {"quote": quotes if len(quotes) > 1 else quotes[0]}}

        params = {"symbols": ",".join(symbols), "greeks": "false"}
        return self._request("GET", "/markets/quotes", params=params)

    def get_quote(self, symbol: str) -> Dict[str, Any]:
        if self.use_mock_data:
            return self._mock_quote(symbol)

        response = self.get_quotes([symbol])
        if "quotes" in response and "quote" in response["quotes"]:
            quotes = response["quotes"]["quote"]
            return quotes if isinstance(quotes, dict) else quotes[0]
        return {}

    def get_market_clock(self) -> Dict[str, Any]:
        if self.use_mock_data:
            now = datetime.utcnow()
            return {
                "clock": {
                    "date": now.date().isoformat(),
                    "description": "Regular Market",
                    "state": "open",
                    "timestamp": now.isoformat() + "Z",
                }
            }

        return self._request("GET", "/markets/clock")

    def is_market_open(self) -> bool:
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
    ) -> List[Dict[str, Any]]:
        if self.use_mock_data:
            return self._mock_history(symbol, interval)

        params = {"symbol": symbol, "interval": interval}
        if start_date:
            params["start"] = start_date
        if end_date:
            params["end"] = end_date

        response = self._request("GET", "/markets/history", params=params)
        if "history" in response and response["history"] != "null":
            bars = response["history"].get("day", [])
            if isinstance(bars, dict):
                bars = [bars]

            normalized: List[Dict[str, Any]] = []
            for bar in bars:
                try:
                    normalized.append(
                        {
                            "date": bar["date"],
                            "open": float(bar["open"]),
                            "high": float(bar["high"]),
                            "low": float(bar["low"]),
                            "close": float(bar["close"]),
                            "volume": int(bar["volume"]),
                        }
                    )
                except (KeyError, ValueError) as exc:
                    logger.warning("Skipping malformed bar: %s - %s", bar, exc)
            return normalized
        return []

    # ------------------------------------------------------------------
    # Options data
    # ------------------------------------------------------------------

    def get_option_chains(self, symbol: str, expiration: str | None = None) -> Dict[str, Any]:
        if self.use_mock_data:
            return self._mock_chain(symbol, expiration)

        params = {"symbol": symbol, "greeks": "true"}
        if expiration:
            params["expiration"] = expiration
        return self._request("GET", "/markets/options/chains", params=params)

    def get_option_expirations(self, symbol: str) -> Dict[str, Any]:
        if self.use_mock_data:
            return self._mock_expirations(symbol)

        params = {"symbol": symbol}
        return self._request("GET", "/markets/options/expirations", params=params)


_tradier_client: TradierClient | None = None


def get_tradier_client() -> TradierClient:
    """Return a singleton Tradier client instance."""
    global _tradier_client
    if _tradier_client is None:
        _tradier_client = TradierClient()
    return _tradier_client
