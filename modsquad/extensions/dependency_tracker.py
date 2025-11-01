"""Dependency tracker for MOD SQUAD API contract synchronization."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .utils import CONFIG_PATH

DEPENDENCY_GRAPH_FILE = CONFIG_PATH.parent.parent / "logs" / "dependency-graph.json"
TRACKER_LOG = CONFIG_PATH.parent.parent / "logs" / "run-history" / "dependency_tracker.jsonl"


def register_dependency(consumer: str, provider: str, contract: str) -> None:
    """Register a dependency relationship."""
    graph = _load_graph()
    
    if consumer not in graph:
        graph[consumer] = []
    
    dependency = {
        "provider": provider,
        "contract": contract,
        "registered_at": datetime.utcnow().isoformat() + "Z",
    }
    
    # Avoid duplicates
    if not any(d["provider"] == provider and d["contract"] == contract for d in graph[consumer]):
        graph[consumer].append(dependency)
    
    _save_graph(graph)
    _log_event("register", consumer, provider, contract)


def get_dependents(provider: str) -> list[str]:
    """Get all consumers depending on a provider."""
    graph = _load_graph()
    dependents = []
    
    for consumer, deps in graph.items():
        for dep in deps:
            if dep["provider"] == provider:
                dependents.append(consumer)
                break
    
    return dependents


def alert_contract_change(provider: str, contract: str, change_description: str) -> None:
    """Alert all dependents that a contract changed."""
    dependents = get_dependents(provider)
    
    for dependent in dependents:
        _log_event(
            "alert",
            dependent,
            provider,
            contract,
            extra={"change": change_description},
        )


def _load_graph() -> dict[str, list[dict[str, Any]]]:
    DEPENDENCY_GRAPH_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DEPENDENCY_GRAPH_FILE.exists():
        return {}
    return json.loads(DEPENDENCY_GRAPH_FILE.read_text(encoding="utf-8"))


def _save_graph(graph: dict[str, list[dict[str, Any]]]) -> None:
    DEPENDENCY_GRAPH_FILE.write_text(json.dumps(graph, indent=2), encoding="utf-8")


def _log_event(
    action: str,
    consumer: str,
    provider: str,
    contract: str,
    extra: dict[str, Any] | None = None,
) -> None:
    TRACKER_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "action": action,
        "consumer": consumer,
        "provider": provider,
        "contract": contract,
        **(extra or {}),
    }
    with TRACKER_LOG.open("a", encoding="utf-8") as handle:
        json.dump(entry, handle)
        handle.write("\n")


# Pre-register known dependencies for PaiiD/PaiiD-2mx
def init_paiid_dependencies() -> None:
    """Initialize known dependencies for PaiiD applications."""
    register_dependency(
        consumer="frontend/components/ExecutionDashboard",
        provider="backend/app/routers/strategies",
        contract="/api/strategies/execution-history",
    )
    register_dependency(
        consumer="frontend/components/SchedulerUI",
        provider="backend/app/routers/scheduler",
        contract="/api/schedules",
    )
    register_dependency(
        consumer="frontend/components/ExecuteTradeForm",
        provider="backend/app/routers/strategies",
        contract="/api/strategies/run",
    )


__all__ = ["alert_contract_change", "get_dependents", "init_paiid_dependencies", "register_dependency"]

