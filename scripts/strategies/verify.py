"""Strategy verification runner for MOD SQUAD."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def _bootstrap_backend() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    backend_path = repo_root / "backend"
    if str(backend_path) not in sys.path:
        sys.path.insert(0, str(backend_path))


def _summary(result: dict, dex_readiness: dict | None = None) -> dict:
    details = result["results"]
    plan = details.get("trade_plan", {})
    market_snapshot = details.get("market_snapshot", {})
    runtime = details.get("runtime", {})
    status = "ok"
    reasons: list[str] = []

    if not result.get("success", False):
        status = "error"
        reasons.append("strategy_error")

    if market_snapshot.get("status") not in {"ok", "degraded"}:
        status = "error"
        reasons.append("market_snapshot_unavailable")

    summary = {
        "strategy": details.get("strategy_type"),
        "status": status,
        "reasons": reasons,
        "market_status": market_snapshot.get("status"),
        "approved_trades": len(plan.get("approved_trades", [])),
        "proposals": len(plan.get("proposals", [])),
        "instruments": details.get("instruments", []),
        "runtime": runtime,
    }

    if dex_readiness is not None:
        summary["env"] = {"dex_wallet": dex_readiness}

    return summary


def main() -> None:
    _bootstrap_backend()

    from app.services.providers.dex_wallet import DexWalletProvider
    from app.services.strategy_execution_service import get_strategy_execution_service

    service = get_strategy_execution_service()

    strategies = ["under4-multileg", "dex-meme-scout"]
    summaries = []
    exit_code = 0

    for strategy in strategies:
        try:
            result = service.execute_strategy_dry_run(
                user_id=0,
                strategy_type=strategy,
            )
            dex_readiness = None
            if strategy == "dex-meme-scout":
                try:
                    dex_readiness = DexWalletProvider().readiness()
                except Exception as exc:  # pragma: no cover - defensive
                    dex_readiness = {
                        "is_ready": False,
                        "missing": [f"dex_wallet_exception:{exc}"],
                    }

            summary = _summary(result, dex_readiness)
        except Exception as exc:  # pragma: no cover - safety
            summary = {
                "strategy": strategy,
                "status": "error",
                "reasons": [f"exception:{exc}"],
                "approved_trades": 0,
                "proposals": 0,
                "instruments": [],
                "runtime": {},
            }
        summaries.append(summary)
        if summary["status"] != "ok":
            exit_code = 1

    payload = {
        "summaries": summaries,
    }
    print(json.dumps(payload, indent=2))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
