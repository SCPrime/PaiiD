from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

_DEFAULTS: Dict[str, Any] = {
    "environments": {
        "prod_url": "https://paiid-frontend.onrender.com",
        "staging_url": "https://paiid-frontend.onrender.com",
    },
    "timeouts": {
        "page_load_ms": 30000,
        "network_idle_ms": 10000,
        "live_update_expectation_s": 30,
    },
    "branding": {"aria_label": "PaiiD"},
    "reports": {"dir": "reports"},
}


def _load_yaml(path: Path) -> Dict[str, Any]:
    try:
        import yaml  # type: ignore

        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def _load_json(path: Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(a)
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge(out[k], v)  # type: ignore[index]
        else:
            out[k] = v
    return out


def get_config() -> Dict[str, Any]:
    root = Path(__file__).resolve().parents[1]
    cfg_yaml = root / "scripts" / "mod_squad_config.yaml"
    cfg_json = root / "scripts" / "mod_squad_config.json"

    cfg: Dict[str, Any] = dict(_DEFAULTS)
    if cfg_yaml.exists():
        cfg = _merge(cfg, _load_yaml(cfg_yaml))
    elif cfg_json.exists():
        cfg = _merge(cfg, _load_json(cfg_json))
    return cfg


def get_base_url() -> str:
    # Env var wins first
    env = os.getenv("PRODUCTION_URL") or os.getenv("BASE_URL")
    if env:
        return env.rstrip("/")
    cfg = get_config()
    return str(
        cfg.get("environments", {}).get(
            "prod_url", _DEFAULTS["environments"]["prod_url"]
        )
    ).rstrip("/")


def get_reports_dir() -> str:
    cfg = get_config()
    return str(cfg.get("reports", {}).get("dir", _DEFAULTS["reports"]["dir"]))


def get_timeout_ms() -> int:
    cfg = get_config()
    return int(
        cfg.get("timeouts", {}).get(
            "page_load_ms", _DEFAULTS["timeouts"]["page_load_ms"]
        )
    )



