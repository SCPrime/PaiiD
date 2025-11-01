"""Execution audit logging helpers."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy.exc import SQLAlchemyError

from ..db.session import SessionLocal
from ..models.database import StrategyExecutionRecord


logger = logging.getLogger(__name__)

AUDIT_DIR = Path("data/executions")
AUDIT_DIR.mkdir(parents=True, exist_ok=True)
AUDIT_FILE = AUDIT_DIR / "history.jsonl"


def append_execution_audit(record: dict[str, Any]) -> None:
    """Append an execution record to the audit log."""

    entry = {
        "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        **record,
    }

    _write_file(entry)
    _write_db(entry)


def _write_file(entry: dict[str, Any]) -> None:
    with AUDIT_FILE.open("a", encoding="utf-8") as handle:
        json.dump(entry, handle)
        handle.write("\n")


def _write_db(entry: dict[str, Any]) -> None:
    session = SessionLocal()
    try:
        timestamp = entry.get("timestamp")
        if timestamp:
            created_at = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        else:
            created_at = datetime.now(UTC)

        db_record = StrategyExecutionRecord(
            user_id=int(entry.get("user_id", 0)),
            strategy_type=entry.get("strategy_type", "unknown"),
            market_key=entry.get("market_key", "unknown"),
            trade_summary=entry.get("trade_summary", {}),
            execution_summary=entry.get("execution_summary", {}),
            execution=entry.get("execution", []),
            created_at=created_at.replace(tzinfo=None),
        )
        session.add(db_record)
        session.commit()
    except (SQLAlchemyError, ValueError) as exc:  # pragma: no cover - DB safety
        session.rollback()
        logger.warning("Execution audit DB insert failed: %s", exc)
    finally:
        session.close()


__all__ = ["AUDIT_FILE", "append_execution_audit"]
