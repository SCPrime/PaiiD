# ruff: noqa: I001
"""Markets package exposes registry helpers for MOD SQUAD orchestration."""

from . import modules as _modules  # noqa: F401  (import for side effects)
from .manager import prepare_market_runtime
from .registry import (
    bootstrap_market,
    get_market_strategy,
    list_market_keys,
    register_market_strategy,
)

__all__ = [
    "bootstrap_market",
    "get_market_strategy",
    "list_market_keys",
    "prepare_market_runtime",
    "register_market_strategy",
]
