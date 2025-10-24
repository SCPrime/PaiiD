"""Helpers for loading deterministic fixture data used in automated tests."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


FIXTURE_ROOT = Path(__file__).resolve().parents[2] / "data" / "fixtures"


class FixtureNotFoundError(FileNotFoundError):
    """Raised when a requested fixture is missing."""


def _load_json(path: Path) -> dict:
    if not path.exists():
        raise FixtureNotFoundError(f"Fixture not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_options_fixture(symbol: str) -> dict:
    """Load the options fixture for ``symbol`` (case insensitive)."""

    normalised = symbol.lower()
    path = FIXTURE_ROOT / "options" / f"{normalised}.json"
    return _load_json(path)


def list_available_option_symbols() -> List[str]:
    """Return the set of option fixture symbols available on disk."""

    directory = FIXTURE_ROOT / "options"
    if not directory.exists():
        return []
    return sorted(file.stem.upper() for file in directory.glob("*.json"))


def get_options_chain(symbol: str, expiration: Optional[str]) -> Optional[dict]:
    """Return fixture chain for ``symbol`` and ``expiration`` if available."""

    try:
        fixture = load_options_fixture(symbol)
    except FixtureNotFoundError:
        return None

    chains: Dict[str, dict] = fixture.get("chains", {})
    if not chains:
        return None

    if expiration and expiration in chains:
        return {"meta": fixture, "chain": chains[expiration], "expiration": expiration}

    # Fall back to the first available expiration if not provided
    expirations: List[dict] = fixture.get("expirations", [])
    if not expirations:
        return None

    default_expiration = expirations[0]["date"]
    chain = chains.get(default_expiration)
    if not chain:
        return None

    return {"meta": fixture, "chain": chain, "expiration": default_expiration}
