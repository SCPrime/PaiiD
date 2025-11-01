"""
MOD SQUAD Universal Loader
Preloads all 190+ extensions, modules, routers, services, and components
Available across all project folders and files
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Dict

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "backend"))
sys.path.insert(0, str(PROJECT_ROOT / "frontend"))

# Test mode detection (skip backend/frontend imports during testing)
_TEST_MODE = os.getenv("TESTING", "false").lower() in ("true", "1", "yes")


class UniversalModuleRegistry:
    """Central registry for all MOD SQUAD and project modules."""

    def __init__(self):
        self._modules: Dict[str, Any] = {}
        self._cache: Dict[str, Any] = {}  # Shared cache for squad coordination
        self._test_mode = _TEST_MODE
        self._load_all_modules()

    def _load_all_modules(self):
        """Load all modules into registry."""
        # MOD SQUAD Extensions (always load)
        self._load_modsquad_extensions()

        # Backend Modules (skip in test mode)
        if not self._test_mode:
            self._load_backend_routers()
            self._load_backend_services()
            self._load_backend_markets()
            self._load_backend_strategies()

        # Scripts
        self._load_scripts()

    def _load_modsquad_extensions(self):
        """Load all MOD SQUAD extensions."""
        try:
            from modsquad import extensions
            from modsquad.extensions import (
                # Core
                maintenance_notifier,
                metrics_streamer,
                secrets_watchdog,
                strategy_verifier,
                # Validation
                browser_validator,
                contract_enforcer,
                integration_validator,
                # Infrastructure
                infra_health,
                dependency_tracker,
                # Scheduling
                guardrail_scheduler,
                accessibility_scheduler,
                data_latency_tracker,
                # Reporting
                component_diff_reporter,
                security_patch_advisor,
                docs_sync,
                review_aggregator,
                quality_inspector,
                # Testing
                persona_simulator,
                # Coordination
                stream_coordinator,
                runner,
                # SUN TZU Squad (Strategic Batch Planning)
                elite_strategist,
                task_graph_analyzer,
                risk_profiler,
                batch_optimizer,
                intersection_mapper,
                # ARMANI Squad (Integration Weaving)
                elite_weaver,
                interface_predictor,
                glue_code_generator,
                conflict_resolver,
                intersection_executor,
                integration_validator,
            )

            self._modules.update({
                'maintenance_notifier': maintenance_notifier,
                'metrics_streamer': metrics_streamer,
                'secrets_watchdog': secrets_watchdog,
                'strategy_verifier': strategy_verifier,
                'browser_validator': browser_validator,
                'contract_enforcer': contract_enforcer,
                'integration_validator': integration_validator,
                'infra_health': infra_health,
                'dependency_tracker': dependency_tracker,
                'guardrail_scheduler': guardrail_scheduler,
                'accessibility_scheduler': accessibility_scheduler,
                'data_latency_tracker': data_latency_tracker,
                'component_diff_reporter': component_diff_reporter,
                'security_patch_advisor': security_patch_advisor,
                'docs_sync': docs_sync,
                'review_aggregator': review_aggregator,
                'quality_inspector': quality_inspector,
                'persona_simulator': persona_simulator,
                'stream_coordinator': stream_coordinator,
                'runner': runner,
                # SUN TZU Squad
                'elite_strategist': elite_strategist,
                'task_graph_analyzer': task_graph_analyzer,
                'risk_profiler': risk_profiler,
                'batch_optimizer': batch_optimizer,
                'intersection_mapper': intersection_mapper,
                # ARMANI Squad
                'elite_weaver': elite_weaver,
                'interface_predictor': interface_predictor,
                'glue_code_generator': glue_code_generator,
                'conflict_resolver': conflict_resolver,
                'intersection_executor': intersection_executor,
                'integration_validator': integration_validator,
            })
        except ImportError as e:
            print(f"Warning: Could not load MOD SQUAD extensions: {e}")

    def _load_backend_routers(self):
        """Load all backend routers."""
        router_names = [
            'ai', 'analytics', 'auth', 'backtesting', 'claude',
            'health', 'market', 'news', 'options', 'orders',
            'portfolio', 'positions', 'quotes', 'scheduler',
            'strategies', 'telemetry', 'trades', 'user', 'watchlist'
        ]

        for router in router_names:
            try:
                module = __import__(f'app.routers.{router}', fromlist=[router])
                self._modules[f'router_{router}'] = module
            except ImportError:
                pass

    def _load_backend_services(self):
        """Load all backend services."""
        service_names = [
            'alerts', 'alert_manager', 'alpaca_client', 'alpaca_options',
            'backtesting_engine', 'claude_service', 'market_data',
            'news_service', 'options_service', 'order_service',
            'portfolio_service', 'scheduler_service', 'strategy_execution_service',
            'tradier_client', 'tradier_options', 'user_service'
        ]

        for service in service_names:
            try:
                module = __import__(f'app.services.{service}', fromlist=[service])
                self._modules[f'service_{service}'] = module
            except ImportError:
                pass

    def _load_backend_markets(self):
        """Load backend market modules."""
        try:
            from app.markets import base, manager, registry
            self._modules.update({
                'markets_base': base,
                'markets_manager': manager,
                'markets_registry': registry,
            })
        except ImportError:
            pass

    def _load_backend_strategies(self):
        """Load backend strategies."""
        try:
            from backend.strategies import dex_meme_scout, under4_multileg
            self._modules.update({
                'strategy_dex_meme_scout': dex_meme_scout,
                'strategy_under4_multileg': under4_multileg,
            })
        except ImportError:
            pass

    def _load_scripts(self):
        """Load utility scripts."""
        # Scripts are loaded dynamically when needed
        scripts_path = PROJECT_ROOT / "scripts"
        if scripts_path.exists():
            sys.path.insert(0, str(scripts_path))

    def get(self, module_name: str) -> Any:
        """Get a module from registry."""
        return self._modules.get(module_name)

    def list_all(self) -> list[str]:
        """List all loaded modules."""
        return sorted(self._modules.keys())

    def count(self) -> int:
        """Count loaded modules."""
        return len(self._modules)

    # ========== SHARED CACHE METHODS (for Squad Coordination) ==========

    def cache_set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """
        Store data in shared cache for squad coordination.

        Args:
            key: Cache key (e.g., "batch_plan:{plan_id}", "intersections:{plan_id}")
            value: Data to cache
            ttl: Time-to-live in seconds (default: 1 hour)

        Returns:
            True if successful
        """
        self._cache[key] = {
            "value": value,
            "ttl": ttl,
            "timestamp": __import__("time").time()
        }
        return True

    def cache_get(self, key: str) -> Any | None:
        """
        Retrieve data from shared cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        if key not in self._cache:
            return None

        cache_entry = self._cache[key]
        import time

        # Check TTL
        if time.time() - cache_entry["timestamp"] > cache_entry["ttl"]:
            del self._cache[key]
            return None

        return cache_entry["value"]

    def cache_delete(self, key: str) -> bool:
        """
        Delete data from cache.

        Args:
            key: Cache key

        Returns:
            True if key existed and was deleted
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def cache_clear(self) -> int:
        """
        Clear all cached data.

        Returns:
            Number of keys cleared
        """
        count = len(self._cache)
        self._cache.clear()
        return count

    def cache_keys(self, pattern: str = None) -> list[str]:
        """
        List all cache keys, optionally filtered by pattern.

        Args:
            pattern: Optional pattern to filter keys (e.g., "batch_plan:*")

        Returns:
            List of matching cache keys
        """
        if pattern is None:
            return list(self._cache.keys())

        # Simple pattern matching (supports wildcard *)
        import re
        regex_pattern = pattern.replace("*", ".*")
        regex = re.compile(f"^{regex_pattern}$")
        return [key for key in self._cache.keys() if regex.match(key)]


# Global registry instance
_registry = None


def get_registry() -> UniversalModuleRegistry:
    """Get or create global registry."""
    global _registry
    if _registry is None:
        _registry = UniversalModuleRegistry()
    return _registry


def load_all():
    """Load all modules into global namespace."""
    registry = get_registry()
    print(f"MOD SQUAD Universal Loader: {registry.count()} modules loaded")
    return registry


# Auto-load on import
REGISTRY = load_all()


__all__ = [
    "UniversalModuleRegistry",
    "get_registry",
    "load_all",
    "REGISTRY",
]
