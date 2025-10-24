"""Database helpers for strategy persistence"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Tuple

from sqlalchemy import desc
from sqlalchemy.orm import Session

from ..models.database import (
    StrategyConfigModel,
    StrategyPerformanceLogModel,
    StrategyVersionModel,
)

DEFAULT_MODEL_KEY = "paiid-pro"
DEFAULT_FEATURE_FLAGS: Dict[str, bool] = {
    "autoRebalance": True,
    "riskOverlay": True,
    "notifyOnDrift": True,
}


def _normalise_feature_flags(flags: Optional[Dict[str, Any]]) -> Dict[str, bool]:
    if not flags:
        return dict(DEFAULT_FEATURE_FLAGS)
    cleaned: Dict[str, bool] = {}
    for key, value in {**DEFAULT_FEATURE_FLAGS, **flags}.items():
        cleaned[key] = bool(value)
    return cleaned


def get_strategy_config(
    db: Session, *, owner_id: str, strategy_key: str
) -> Optional[StrategyConfigModel]:
    return (
        db.query(StrategyConfigModel)
        .filter(StrategyConfigModel.owner_id == owner_id)
        .filter(StrategyConfigModel.strategy_key == strategy_key)
        .one_or_none()
    )


def list_strategy_configs(db: Session, *, owner_id: str) -> List[StrategyConfigModel]:
    return (
        db.query(StrategyConfigModel)
        .filter(StrategyConfigModel.owner_id == owner_id)
        .order_by(desc(StrategyConfigModel.updated_at))
        .all()
    )


def save_strategy_config(
    db: Session,
    *,
    owner_id: str,
    strategy_key: str,
    config: Dict[str, Any],
    model_key: Optional[str],
    feature_flags: Optional[Dict[str, Any]],
    changes_summary: Optional[str],
    created_by: Optional[str],
) -> Tuple[StrategyConfigModel, StrategyVersionModel]:
    now = datetime.utcnow()
    normalised_flags = _normalise_feature_flags(feature_flags)
    model_key = model_key or DEFAULT_MODEL_KEY

    record = get_strategy_config(db, owner_id=owner_id, strategy_key=strategy_key)

    if record is None:
        record = StrategyConfigModel(
            owner_id=owner_id,
            strategy_key=strategy_key,
            name=strategy_key.replace("-", " ").title(),
            model_key=model_key,
            feature_flags=normalised_flags,
            current_config=config,
            current_version=1,
            created_at=now,
            updated_at=now,
        )
        db.add(record)
        db.flush()
        version_number = 1
    else:
        version_number = (record.current_version or 0) + 1
        record.model_key = model_key
        record.feature_flags = normalised_flags
        record.current_config = config
        record.current_version = version_number
        record.updated_at = now

    version = StrategyVersionModel(
        strategy_config_id=record.id,
        version_number=version_number,
        config_snapshot=config,
        changes_summary=changes_summary or "Configuration updated",
        created_by=created_by,
        created_at=now,
    )

    db.add(version)
    db.commit()
    db.refresh(record)
    db.refresh(version)
    return record, version


def delete_strategy_config(db: Session, *, owner_id: str, strategy_key: str) -> bool:
    record = get_strategy_config(db, owner_id=owner_id, strategy_key=strategy_key)
    if record is None:
        return False
    db.delete(record)
    db.commit()
    return True


def get_strategy_history(
    db: Session, *, strategy_config_id: int, limit: Optional[int] = None
) -> List[StrategyVersionModel]:
    query = (
        db.query(StrategyVersionModel)
        .filter(StrategyVersionModel.strategy_config_id == strategy_config_id)
        .order_by(desc(StrategyVersionModel.version_number))
    )
    if limit is not None:
        query = query.limit(limit)
    return query.all()


def record_strategy_run(
    db: Session,
    *,
    strategy_config_id: int,
    version_number: int,
    run_type: str,
    metrics: Dict[str, Any],
    notes: Optional[str] = None,
    started_at: Optional[datetime] = None,
    completed_at: Optional[datetime] = None,
) -> StrategyPerformanceLogModel:
    log = StrategyPerformanceLogModel(
        strategy_config_id=strategy_config_id,
        version_number=version_number,
        run_type=run_type,
        metrics=metrics,
        notes=notes,
        started_at=started_at,
        completed_at=completed_at,
        created_at=datetime.utcnow(),
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_strategy_performance_logs(
    db: Session, *, strategy_config_id: int, limit: Optional[int] = None
) -> List[StrategyPerformanceLogModel]:
    query = (
        db.query(StrategyPerformanceLogModel)
        .filter(StrategyPerformanceLogModel.strategy_config_id == strategy_config_id)
        .order_by(desc(StrategyPerformanceLogModel.created_at))
    )
    if limit is not None:
        query = query.limit(limit)
    return query.all()


def summarise_versions(versions: Iterable[StrategyVersionModel]) -> List[Dict[str, Any]]:
    return [
        {
            "version_number": version.version_number,
            "created_at": version.created_at,
            "created_by": version.created_by,
            "changes_summary": version.changes_summary,
        }
        for version in versions
    ]


def summarise_performance(
    logs: Iterable[StrategyPerformanceLogModel],
) -> List[Dict[str, Any]]:
    return [
        {
            "id": log.id,
            "version_number": log.version_number,
            "run_type": log.run_type,
            "metrics": log.metrics or {},
            "notes": log.notes,
            "started_at": log.started_at,
            "completed_at": log.completed_at,
            "created_at": log.created_at,
        }
        for log in logs
    ]
