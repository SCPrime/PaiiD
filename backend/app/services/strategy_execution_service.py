"""
Strategy Execution Service - Business logic for strategy management and execution

This service handles loading, saving, running, and managing trading strategies.
"""

import json
from pathlib import Path
from typing import Any

from ..core.logging_utils import get_secure_logger


logger = get_secure_logger(__name__)

# Strategy storage path
STRATEGIES_DIR = Path("data/strategies")
STRATEGIES_DIR.mkdir(parents=True, exist_ok=True)


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

        # PHASE 1: Mock results for testing
        # Future: Integrate with actual strategy execution engine
        return {
            "success": True,
            "dry_run": True,
            "message": "Strategy dry run completed",
            "results": {
                "candidates": ["SNDL", "NOK", "SOFI", "PLUG"],
                "proposals": [
                    {
                        "type": "BUY_CALL",
                        "symbol": "SNDL",
                        "strike": 3.50,
                        "expiry": "2025-11-15",
                        "delta": 0.60,
                        "qty": 3,
                    },
                    {
                        "type": "SELL_PUT",
                        "symbol": "NOK",
                        "strike": 3.00,
                        "expiry": "2025-11-15",
                        "delta": 0.20,
                        "qty": 2,
                    },
                ],
                "approved_trades": 2,
            },
        }


# Singleton instance
_strategy_execution_service: StrategyExecutionService | None = None


def get_strategy_execution_service() -> StrategyExecutionService:
    """Get or create the singleton strategy execution service instance"""
    global _strategy_execution_service
    if _strategy_execution_service is None:
        _strategy_execution_service = StrategyExecutionService()
    return _strategy_execution_service
