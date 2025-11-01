"""
Strategy Execution Service - Business logic for strategy management and execution

This service handles loading, saving, running, and managing trading strategies.
"""

import json
from collections import Counter, deque
from pathlib import Path
from typing import Any

from ..core.logging_utils import get_secure_logger
from ..core.observability import capture_execution_error
from ..db.session import SessionLocal
from ..markets import prepare_market_runtime
from ..markets.services import DexMemeRuntime, StocksOptionsRuntime
from ..strategies.engine import generate_trade_plan
from .execution_audit import AUDIT_FILE, append_execution_audit
from .providers import (
    get_alpaca_options_provider,
    get_alpaca_provider,
    get_dex_wallet_provider,
)


logger = get_secure_logger(__name__)

# Strategy storage path
STRATEGIES_DIR = Path("data/strategies")
STRATEGIES_DIR.mkdir(parents=True, exist_ok=True)

# Optional import for default configs
try:  # pragma: no cover - defensive import
    from strategies.under4_multileg import Under4MultilegConfig
except ImportError:  # pragma: no cover - when strategies package unavailable
    Under4MultilegConfig = None

try:  # pragma: no cover - defensive import
    from strategies.dex_meme_scout import DexMemeScoutConfig
except ImportError:  # pragma: no cover - when strategies package unavailable
    DexMemeScoutConfig = None

MARKET_BY_STRATEGY = {
    "under4-multileg": "stocks_options",
    "dex-meme-scout": "dex_meme_coins",
}


class StrategyExecutionService:
    """Service for managing and executing trading strategies"""

    def __init__(self, strategies_dir: Path = STRATEGIES_DIR):
        """
        Initialize strategy execution service

        Args:
            strategies_dir: Directory path for storing strategy configurations
        """
        self.strategies_dir = strategies_dir
        self.strategies_dir.mkdir(parents=True, exist_ok=True)

    def _get_strategy_file_path(self, user_id: int, strategy_type: str) -> Path:
        """Get the file path for a user's strategy"""
        return self.strategies_dir / f"{user_id}_{strategy_type}.json"

    def save_strategy(
        self, user_id: int, strategy_type: str, config: dict[str, Any]
    ) -> dict:
        """
        Save strategy configuration to file

        Args:
            user_id: User ID who owns the strategy
            strategy_type: Type of strategy (e.g., "under4-multileg")
            config: Strategy configuration dictionary

        Returns:
            Success response dictionary

        Raises:
            ValueError: If strategy type is unknown or config is invalid
        """
        strategy_file = self._get_strategy_file_path(user_id, strategy_type)

        # Note: Validation should be done at router level before calling this service
        # This service focuses on storage logic

        # Save to file
        try:
            with open(strategy_file, "w") as f:
                json.dump(
                    {"strategy_type": strategy_type, "config": config}, f, indent=2
                )

            logger.info(
                "Strategy saved successfully",
                user_id=user_id,
                strategy_type=strategy_type,
            )

            return {
                "success": True,
                "message": f"Strategy '{strategy_type}' saved successfully",
            }
        except OSError as e:
            logger.error(
                "Failed to save strategy file",
                user_id=user_id,
                strategy_type=strategy_type,
                error_type=type(e).__name__,
                error_msg=str(e),
            )
            raise ValueError(f"Failed to save strategy: {e}") from e

    def load_strategy(
        self, user_id: int, strategy_type: str, default_config: dict | None = None
    ) -> dict:
        """
        Load strategy configuration from file

        Args:
            user_id: User ID who owns the strategy
            strategy_type: Type of strategy to load
            default_config: Default configuration if file doesn't exist

        Returns:
            Dictionary with strategy_type, config, and is_default flag

        Raises:
            ValueError: If strategy not found and no default provided
        """
        strategy_file = self._get_strategy_file_path(user_id, strategy_type)

        if not strategy_file.exists():
            # Return default configuration if provided
            if default_config is not None:
                logger.info(
                    "Strategy not found, returning default config",
                    user_id=user_id,
                    strategy_type=strategy_type,
                )
                return {
                    "strategy_type": strategy_type,
                    "config": default_config,
                    "is_default": True,
                }
            else:
                raise ValueError(f"Strategy '{strategy_type}' not found")

        try:
            with open(strategy_file) as f:
                data = json.load(f)

            logger.info(
                "Strategy loaded successfully",
                user_id=user_id,
                strategy_type=strategy_type,
            )

            return {**data, "is_default": False}

        except (json.JSONDecodeError, OSError) as e:
            logger.error(
                "Failed to load strategy file",
                user_id=user_id,
                strategy_type=strategy_type,
                error_type=type(e).__name__,
                error_msg=str(e),
            )
            raise ValueError(f"Failed to load strategy: {e}") from e

    def list_strategies(self, user_id: int) -> list[dict]:
        """
        List all strategies for a user

        Args:
            user_id: User ID to list strategies for

        Returns:
            List of dictionaries with strategy_type and has_config flags
        """
        strategies = []

        # Check for saved strategies
        for strategy_file in self.strategies_dir.glob(f"{user_id}_*.json"):
            try:
                with open(strategy_file) as f:
                    data = json.load(f)
                strategies.append(
                    {"strategy_type": data["strategy_type"], "has_config": True}
                )
            except (json.JSONDecodeError, KeyError, OSError) as e:
                logger.warning(
                    "Failed to read strategy file",
                    file=strategy_file.name,
                    error_type=type(e).__name__,
                )
                continue

        # Add available strategies that haven't been configured
        available_strategies = ["under4-multileg", "custom"]
        for strategy_type in available_strategies:
            if not any(s["strategy_type"] == strategy_type for s in strategies):
                strategies.append({"strategy_type": strategy_type, "has_config": False})

        logger.info("Listed strategies", user_id=user_id, count=len(strategies))

        return strategies

    def delete_strategy(self, user_id: int, strategy_type: str) -> dict:
        """
        Delete a saved strategy configuration

        Args:
            user_id: User ID who owns the strategy
            strategy_type: Type of strategy to delete

        Returns:
            Success response dictionary

        Raises:
            ValueError: If strategy not found
        """
        strategy_file = self._get_strategy_file_path(user_id, strategy_type)

        if not strategy_file.exists():
            raise ValueError(f"Strategy '{strategy_type}' not found")

        try:
            strategy_file.unlink()
            logger.info(
                "Strategy deleted successfully",
                user_id=user_id,
                strategy_type=strategy_type,
            )
            return {
                "success": True,
                "message": f"Strategy '{strategy_type}' deleted successfully",
            }
        except OSError as e:
            logger.error(
                "Failed to delete strategy file",
                user_id=user_id,
                strategy_type=strategy_type,
                error_type=type(e).__name__,
                error_msg=str(e),
            )
            raise ValueError(f"Failed to delete strategy: {e}") from e

    def execute_strategy_dry_run(
        self, user_id: int, strategy_type: str, config: dict | None = None
    ) -> dict:
        """
        Execute a strategy in dry run mode (simulation only)

        Args:
            user_id: User ID running the strategy
            strategy_type: Type of strategy to run
            config: Optional config override (uses saved config if None)

        Returns:
            Dictionary with dry run results

        Note:
            Currently returns mock results. Real execution logic would:
            1. Load strategy configuration
            2. Fetch market data
            3. Run strategy logic
            4. Generate trade proposals
            5. Return candidates and proposals
        """
        logger.info(
            "Executing strategy dry run",
            user_id=user_id,
            strategy_type=strategy_type,
        )

        strategy_config = self._resolve_strategy_config(user_id, strategy_type, config)
        market_key = MARKET_BY_STRATEGY.get(strategy_type, "stocks_options")
        instruments = self._extract_instruments(strategy_config)

        runtime = prepare_market_runtime(
            market_key=market_key,
            mode="paper",
            instruments=instruments,
            metadata={"strategy_type": strategy_type, "user_id": user_id},
        )

        market_snapshot = self._collect_market_snapshot(market_key, instruments)
        insights = self._generate_insights(strategy_config)
        trade_plan = generate_trade_plan(
            strategy_type=strategy_type,
            config=strategy_config,
            market_snapshot=market_snapshot,
        )
        trade_summary = self._summarize_trade_plan(trade_plan)

        return {
            "success": True,
            "dry_run": True,
            "message": f"Strategy '{strategy_type}' dry run prepared",
            "results": {
                "strategy_type": strategy_type,
                "market_key": market_key,
                "config": strategy_config,
                "instruments": instruments,
                "runtime": runtime,
                "market_snapshot": market_snapshot,
                "insights": insights,
                "trade_plan": trade_plan,
                "trade_summary": trade_summary,
            },
        }

    def execute_strategy_live(
        self,
        user_id: int,
        strategy_type: str,
        config: dict | None = None,
    ) -> dict:
        """Execute strategy using broker integration."""

        try:
            dry_run = self.execute_strategy_dry_run(
                user_id=user_id,
                strategy_type=strategy_type,
                config=config,
            )
            trade_plan = dry_run["results"].get("trade_plan", {})
            market_key = dry_run["results"].get("market_key", "stocks_options")
            approved = trade_plan.get("approved_trades", [])
            trade_summary = dry_run["results"].get(
                "trade_summary"
            ) or self._summarize_trade_plan(trade_plan)

            provider = self._resolve_provider(market_key)
            execution_results = []
            collateral_committed = 0.0
            premium_spent = 0.0
            dex_allocation = 0.0
            dex_tokens: set[str] = set()

            for trade in approved:
                outcome = self._submit_trade(provider, trade)
                execution_results.append(outcome)
                trade_type = trade.get("type")

                if trade_type == "SELL_PUT":
                    collateral_committed += float(trade.get("collateral") or 0)
                if trade_type == "BUY_CALL":
                    premium_spent += float(trade.get("cost") or 0)
                if trade_type == "BUY_TOKEN":
                    dex_allocation += float(trade.get("allocation_usd") or 0)
                    symbol = trade.get("symbol")
                    if isinstance(symbol, str):
                        dex_tokens.add(symbol.upper())

            status_counts = Counter(
                outcome.get("status", "unknown") for outcome in execution_results
            )

            results_payload = {
                "success": True,
                "dry_run": False,
                "message": f"Strategy '{strategy_type}' live execution attempted",
            "results": {
                    **dry_run["results"],
                    "execution": execution_results,
                    "trade_summary": trade_summary,
                    "execution_summary": {
                        "status_counts": dict(status_counts),
                        "options": {
                            "collateral_committed": round(collateral_committed, 2),
                            "premium_spent_usd": round(premium_spent, 2),
                        },
                        "dex": {
                            "usd_allocation": round(dex_allocation, 2),
                            "tokens": sorted(dex_tokens),
                        },
                    },
                },
            }

            self._record_execution_audit(
                user_id=user_id,
                strategy_type=strategy_type,
                market_key=market_key,
                trade_summary=trade_summary,
                execution_summary=results_payload["results"]["execution_summary"],
                execution_results=execution_results,
            )

            return results_payload

        except Exception as exc:
            capture_execution_error(
                strategy_type=strategy_type,
                market_key=MARKET_BY_STRATEGY.get(strategy_type, "unknown"),
                user_id=user_id,
                error=exc,
                context={
                    "config": config,
                    "phase": "execution",
                },
            )
            raise

    def _resolve_strategy_config(
        self, user_id: int, strategy_type: str, override: dict | None
    ) -> dict[str, Any]:
        if override is not None:
            return override

        default_config = None
        if strategy_type == "under4-multileg" and Under4MultilegConfig is not None:
            default_config = Under4MultilegConfig().model_dump()
        elif strategy_type == "dex-meme-scout" and DexMemeScoutConfig is not None:
            default_config = DexMemeScoutConfig().model_dump()

        loaded = self.load_strategy(
            user_id=user_id,
            strategy_type=strategy_type,
            default_config=default_config,
        )
        return loaded.get("config", {})

    def _extract_instruments(self, config: dict[str, Any]) -> list[str]:
        symbols: set[str] = set()

        symbol = config.get("symbol")
        if isinstance(symbol, str):
            symbols.add(symbol.upper())

        for leg in config.get("legs", []):
            leg_symbol = leg.get("symbol")
            if isinstance(leg_symbol, str):
                symbols.add(leg_symbol.upper())

        for rule in config.get("rules", []):
            if isinstance(rule, dict):
                ticker = rule.get("symbol")
                if isinstance(ticker, str):
                    symbols.add(ticker.upper())

        tokens = config.get("tokens")
        if isinstance(tokens, list):
            for token in tokens:
                if isinstance(token, str):
                    symbols.add(token.upper())

        return sorted(symbols)

    def _generate_insights(self, config: dict[str, Any]) -> dict[str, Any]:
        risk = config.get("riskParams", {})
        legs = config.get("legs", [])
        return {
            "risk_profile": {
                "stop_loss": risk.get("stopLoss"),
                "take_profit": risk.get("takeProfit"),
                "position_size": risk.get("positionSize"),
                "max_open_positions": risk.get("maxOpenPositions"),
            },
            "structure": {
                "legs": legs,
                "entry_conditions": config.get("entryConditions")
                or config.get("rules", {}).get("entryConditions"),
                "exit_conditions": config.get("exitConditions")
                or config.get("rules", {}).get("exitConditions"),
            },
        }

    def _collect_market_snapshot(
        self, market_key: str, instruments: list[str]
    ) -> dict[str, Any]:
        try:
            if market_key == "dex_meme_coins":
                runtime = DexMemeRuntime()
                return runtime.snapshot(instruments)

            runtime = StocksOptionsRuntime()
            return runtime.snapshot(instruments)
        except Exception as exc:  # pragma: no cover - environment dependent
            logger.warning("Failed to collect market snapshot: %s", exc)
            return {
                "status": "unavailable",
                "reason": str(exc),
            }

    def _resolve_provider(self, market_key: str):
        if market_key == "stocks_options":
            return get_alpaca_provider()
        if market_key == "dex_meme_coins":
            return get_dex_wallet_provider()
        raise ValueError(f"No provider configured for market '{market_key}'")

    def _submit_trade(self, provider, trade: dict[str, Any]) -> dict[str, Any]:
        try:
            if provider is None:
                return {
                    "trade": trade,
                    "status": "manual_required",
                    "reason": "provider_unavailable",
                }

            if trade["type"] == "BUY_CALL":
                qty = int(trade.get("qty", 0))
                if qty <= 0:
                    return {
                        "trade": trade,
                        "status": "skipped",
                        "reason": "invalid_qty",
                    }
                shares = qty * 100
                order = provider.submit_order(
                    symbol=trade["symbol"],
                    qty=shares,
                    side="buy",
                    order_type="market",
                    time_in_force="day",
                )
                return {"trade": trade, "status": "submitted", "order": order}

            if trade["type"] == "SELL_PUT":
                option_provider = get_alpaca_options_provider()
                option_symbol = trade.get("option_symbol")
                qty = int(trade.get("qty", 0))
                if not option_symbol or qty <= 0:
                    return {
                        "trade": trade,
                        "status": "skipped",
                        "reason": "invalid_option_contract",
                    }
                order_side = trade.get("order_side", "sell_to_open")
                order = option_provider.submit_option_order(
                    symbol=option_symbol,
                    qty=qty,
                    side=order_side,
                    order_type="market",
                    time_in_force="day",
                )
                return {
                    "trade": trade,
                    "status": order.get("status", "submitted"),
                    "order": order.get("order"),
                }

            if trade["type"] == "BUY_TOKEN":
                dex_plan = provider.prepare_token_purchase(trade)
                return {
                    "trade": trade,
                    "status": dex_plan.get("status", "manual_required"),
                    "instructions": dex_plan.get("instructions"),
                    "reason": dex_plan.get("reason"),
                    "missing": dex_plan.get("missing"),
                }

            return {
                "trade": trade,
                "status": "skipped",
                "reason": "unknown_trade_type",
            }
        except Exception as exc:  # pragma: no cover - network/broker dependent
            logger.error("Trade submission failed: %s", exc)
            return {
                "trade": trade,
                "status": "error",
                "reason": str(exc),
            }

    def _summarize_trade_plan(self, trade_plan: dict[str, Any]) -> dict[str, Any]:
        approved = (
            trade_plan.get("approved_trades", [])
            if isinstance(trade_plan, dict)
            else []
        )
        summary = {
            "counts": {
                "total": 0,
                "buy_call": 0,
                "sell_put": 0,
                "buy_token": 0,
            },
            "options": {
                "collateral_required": 0.0,
                "premium_estimate_usd": 0.0,
            },
            "dex": {
                "usd_allocation": 0.0,
                "tokens": set(),
            },
        }

        for trade in approved:
            if not isinstance(trade, dict):
                continue
            summary["counts"]["total"] += 1
            trade_type = trade.get("type")

            if trade_type == "BUY_CALL":
                summary["counts"]["buy_call"] += 1
                summary["options"]["premium_estimate_usd"] += float(
                    trade.get("cost") or 0
                )

            elif trade_type == "SELL_PUT":
                summary["counts"]["sell_put"] += 1
                summary["options"]["collateral_required"] += float(
                    trade.get("collateral") or 0
                )

            elif trade_type == "BUY_TOKEN":
                summary["counts"]["buy_token"] += 1
                summary["dex"]["usd_allocation"] += float(
                    trade.get("allocation_usd") or 0
                )
                symbol = trade.get("symbol")
                if isinstance(symbol, str):
                    summary["dex"]["tokens"].add(symbol.upper())

        summary["options"]["collateral_required"] = round(
            summary["options"]["collateral_required"], 2
        )
        summary["options"]["premium_estimate_usd"] = round(
            summary["options"]["premium_estimate_usd"], 2
        )
        summary["dex"]["usd_allocation"] = round(summary["dex"]["usd_allocation"], 2)
        summary["dex"]["tokens"] = sorted(summary["dex"]["tokens"])
        return summary

    def _record_execution_audit(
        self,
        user_id: int,
        strategy_type: str,
        market_key: str,
        trade_summary: dict[str, Any],
        execution_summary: dict[str, Any],
        execution_results: list[dict[str, Any]],
    ) -> None:
        try:
            append_execution_audit(
                {
                    "user_id": user_id,
                    "strategy_type": strategy_type,
                    "market_key": market_key,
                    "trade_summary": trade_summary,
                    "execution_summary": execution_summary,
                    "execution": execution_results,
                }
            )
        except Exception as exc:  # pragma: no cover - best effort logging
            logger.warning("Failed to record execution audit: %s", exc)

    def list_execution_history(
        self, user_id: int, limit: int = 50
    ) -> list[dict[str, Any]]:
        if limit <= 0:
            return []

        db_history = self._fetch_execution_history_db(user_id=user_id, limit=limit)
        if db_history:
            return db_history

        return self._fetch_execution_history_file(user_id=user_id, limit=limit)

    def _fetch_execution_history_db(
        self, user_id: int, limit: int
    ) -> list[dict[str, Any]]:
        try:
            from ..models.database import StrategyExecutionRecord

            session = SessionLocal()
            try:
                rows = (
                    session.query(StrategyExecutionRecord)
                    .filter(StrategyExecutionRecord.user_id == user_id)
                    .order_by(StrategyExecutionRecord.created_at.desc())
                    .limit(limit)
                    .all()
                )
                return [
                    {
                        **row.to_dict(),
                        "timestamp": row.created_at.isoformat() + "Z",
                    }
                    for row in rows
                ]
            finally:
                session.close()
        except Exception as exc:  # pragma: no cover - DB safety
            logger.warning("Falling back to file execution history: %s", exc)
            return []

    def _fetch_execution_history_file(
        self, user_id: int, limit: int
    ) -> list[dict[str, Any]]:
        records: deque[dict[str, Any]] = deque(maxlen=limit)

        if not AUDIT_FILE.exists():
            return []

        try:
            with AUDIT_FILE.open(encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if int(entry.get("user_id", -1)) != user_id:
                        continue
                    records.append(entry)
        except Exception as exc:  # pragma: no cover - file IO safety
            logger.warning("Failed to read execution history file: %s", exc)
            return []

        return list(records)


# Singleton instance
_strategy_execution_service: StrategyExecutionService | None = None


def get_strategy_execution_service() -> StrategyExecutionService:
    """Get or create the singleton strategy execution service instance"""
    global _strategy_execution_service
    if _strategy_execution_service is None:
        _strategy_execution_service = StrategyExecutionService()
    return _strategy_execution_service
