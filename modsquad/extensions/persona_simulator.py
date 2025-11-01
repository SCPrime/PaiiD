"""Persona simulator for MOD SQUAD user workflow testing."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .utils import CONFIG_PATH, dump_jsonl, load_extension_config

ARTIFACT_DIR = CONFIG_PATH.parent.parent / "logs" / "run-history" / "persona_simulator"


def run() -> None:
    """Simulate persona workflows for testing."""

    config = load_extension_config()
    settings = config.get("persona_simulator")
    if not settings or not settings.get("enabled", False):
        return

    personas: list[str] = settings.get("personas", [])
    results: list[dict[str, Any]] = []

    for persona in personas:
        result = _simulate_persona(persona)
        results.append(result)

    dump_jsonl(
        ARTIFACT_DIR / "persona_simulator.jsonl",
        {
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "personas": personas,
            "results": results,
        },
    )


def _simulate_persona(persona: str) -> dict[str, Any]:
    """Simulate workflow for given persona."""

    # Persona workflow definitions
    workflows = {
        "hedge_trader": [
            "view_positions",
            "check_market_data",
            "execute_trade",
            "review_analytics",
        ],
        "mobile_novice": [
            "onboarding",
            "simple_trade",
            "view_news",
            "check_portfolio",
        ],
    }

    workflow = workflows.get(persona, [])

    return {
        "persona": persona,
        "status": "simulated",
        "workflow_steps": workflow,
        "steps_count": len(workflow),
        "note": "Placeholder for actual browser automation",
    }


def cli() -> None:
    run()


__all__ = ["run"]
