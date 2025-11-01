"""Runtime helpers for stocks/options strategy modules."""

from __future__ import annotations

# ruff: noqa: I001
from collections.abc import Iterable
from datetime import UTC, datetime
import logging
from typing import Any

from ...services.tradier_client import ProviderHTTPError, get_tradier_client

logger = logging.getLogger(__name__)


class StocksOptionsRuntime:
    """Collect account, position, and quote snapshots for stocks/options strategies."""

    def __init__(self) -> None:
        self._client = None

    def snapshot(self, instruments: Iterable[str] | None = None) -> dict[str, Any]:
        """Return latest account/position overview."""

        timestamp = datetime.now(UTC).isoformat().replace("+00:00", "Z")
        try:
            client = self._resolve_client()
        except Exception as exc:  # pragma: no cover - environment dependent
            return {
                "status": "unavailable",
                "timestamp": timestamp,
                "reason": str(exc),
            }

        account = self._safe_call(client.get_account, "account")
        positions = self._safe_call(client.get_positions, "positions", default=[])
        orders = self._safe_call(client.get_orders, "orders", default=[])

        symbols = self._collect_symbols(positions, instruments)
        quotes = self._safe_quotes(client, symbols)

        return {
            "status": "ok",
            "timestamp": timestamp,
            "account": account,
            "positions": positions,
            "orders": orders,
            "quotes": quotes,
        }

    # ------------------------------------------------------------------
    def _resolve_client(self):
        if self._client is None:
            self._client = get_tradier_client()
        return self._client

    def _safe_call(self, func, label: str, default: Any | None = None) -> Any:
        try:
            return func()
        except ProviderHTTPError as exc:  # pragma: no cover - network specific
            logger.warning("Tradier provider error during %s: %s", label, exc)
            return {
                "status": "error",
                "reason": "provider_error",
                "message": str(exc),
            }
        except Exception as exc:  # pragma: no cover - environment specific
            logger.warning("Tradier call failed during %s: %s", label, exc)
            return (
                default
                if default is not None
                else {
                    "status": "error",
                    "reason": "exception",
                    "message": str(exc),
                }
            )

    def _safe_quotes(self, client, symbols: list[str]) -> dict[str, Any]:
        if not symbols:
            return {"status": "empty"}
        try:
            response = client.get_quotes(symbols)
            quotes = response.get("quotes", {}).get("quote", [])
            if isinstance(quotes, dict):
                quotes = [quotes]
            return {
                "status": "ok",
                "items": quotes,
            }
        except ProviderHTTPError as exc:  # pragma: no cover - network specific
            logger.warning("Tradier quotes error: %s", exc)
            return {
                "status": "error",
                "reason": "provider_error",
                "message": str(exc),
            }
        except Exception as exc:  # pragma: no cover - environment specific
            logger.warning("Tradier quotes exception: %s", exc)
            return {
                "status": "error",
                "reason": "exception",
                "message": str(exc),
            }

    def _collect_symbols(
        self, positions: Iterable[dict[str, Any]], extra: Iterable[str] | None
    ) -> list[str]:
        symbols: set[str] = set()
        for position in positions or []:
            symbol = position.get("symbol")
            if isinstance(symbol, str):
                symbols.add(symbol.upper())
        for symbol in extra or []:
            if isinstance(symbol, str):
                symbols.add(symbol.upper())
        return sorted(symbols)


__all__ = ["StocksOptionsRuntime"]
