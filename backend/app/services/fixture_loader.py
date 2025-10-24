"""Utilities for loading deterministic fixtures for backend services."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any


class FixtureLoader:
    """Simple JSON fixture loader with in-memory caching."""

    def __init__(self, base_path: Path | None = None):
        env_base = os.getenv("BACKEND_FIXTURE_PATH")
        if base_path is None:
            if env_base:
                base_path = Path(env_base)
            else:
                base_path = Path(__file__).resolve().parents[2] / "tests" / "fixtures"
        self.base_path = Path(base_path)
        self._cache: dict[Path, Any] = {}

    def load_json(self, *relative_path: str | Path) -> Any:
        path = self.base_path.joinpath(*(str(part) for part in relative_path))
        if path.suffix != ".json":
            path = path.with_suffix(".json")
        if not path.exists():
            raise FileNotFoundError(path)
        if path not in self._cache:
            self._cache[path] = json.loads(path.read_text(encoding="utf-8"))
        return self._cache[path]


@lru_cache(maxsize=1)
def get_fixture_loader() -> FixtureLoader:
    return FixtureLoader()


def should_use_fixture_mode(explicit_flag: bool, header_value: str | None) -> bool:
    if explicit_flag:
        return True
    if header_value and header_value.lower() == "options":
        return True
    return os.getenv("USE_FIXTURE_DATA", "false").lower() == "true"


def load_options_fixture(symbol: str, expiration: str | None = None) -> Any:
    loader = get_fixture_loader()
    normalized_symbol = symbol.upper()
    candidates = []
    if expiration:
        sanitized = expiration.replace("-", "")
        candidates.extend(
            [
                Path("options") / f"{normalized_symbol}_{sanitized}",
                Path("options") / f"{normalized_symbol}_{expiration}",
            ]
        )
    candidates.append(Path("options") / normalized_symbol)

    for candidate in candidates:
        try:
            return loader.load_json(candidate)
        except FileNotFoundError:
            continue
    raise FileNotFoundError(
        f"No fixture available for symbol={symbol} expiration={expiration}"
    )
