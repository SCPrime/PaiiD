"""Expose deterministic fixtures required by Playwright tests."""
from __future__ import annotations

import json
import sys
from pathlib import Path

BACKEND_SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = BACKEND_SCRIPT_DIR.parent
REPO_ROOT = BACKEND_ROOT.parent
sys.path.insert(0, str(BACKEND_ROOT))

from app.services.fixture_loader import list_available_option_symbols, load_options_fixture


def main() -> None:
    output = {
        "available_symbols": list_available_option_symbols(),
        "fixtures": {},
    }

    for symbol in output["available_symbols"]:
        fixture = load_options_fixture(symbol)
        output["fixtures"][symbol] = {
            "expirations": fixture.get("expirations", []),
            "chain_keys": sorted(fixture.get("chains", {}).keys()),
        }

    target = BACKEND_ROOT / "data" / "fixtures" / "summary.playwright.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Wrote Playwright fixture summary to {target.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
