from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..core.auth import require_bearer
from ..db.session import get_db
from ..models.database import User, UserSettings


router = APIRouter()


DEFAULT_SETTINGS: dict[str, Any] = {
    "defaultExecutionMode": "requires_approval",
    "enableSMSAlerts": True,
    "enableEmailAlerts": True,
    "enablePushNotifications": False,
    "enablePerformanceTracking": True,
    "minTradesForPerformanceData": 10,
    "defaultSlippageBudget": 0.4,
    "defaultMaxReprices": 4,
}


class SettingsPayload(BaseModel):
    """Payload for updating owner settings."""

    defaultExecutionMode: str | None = Field(
        None, description="Execution mode preference", pattern=r"^(requires_approval|autopilot)$"
    )
    enableSMSAlerts: bool | None = None
    enableEmailAlerts: bool | None = None
    enablePushNotifications: bool | None = None
    enablePerformanceTracking: bool | None = None
    minTradesForPerformanceData: int | None = Field(None, ge=0)
    defaultSlippageBudget: float | None = Field(None, ge=0)
    defaultMaxReprices: int | None = Field(None, ge=0)


def _get_or_create_default_user(db: Session) -> User:
    user = db.query(User).filter(User.id == 1).first()
    if user:
        return user

    user = User(
        id=1,
        email="owner@paiid.local",
        password_hash="migrated",
        role="owner",
        preferences={"risk_tolerance": 50},
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _get_or_create_settings(db: Session, user: User) -> UserSettings:
    record = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
    if record:
        return record

    record = UserSettings(user_id=user.id, settings=DEFAULT_SETTINGS.copy())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/settings")
def get_settings(db: Session = Depends(get_db)) -> dict[str, Any]:
    """Return persisted settings, falling back to defaults."""

    user = _get_or_create_default_user(db)
    record = _get_or_create_settings(db, user)
    return record.settings or DEFAULT_SETTINGS


@router.post("/settings")
def set_settings(
    payload: SettingsPayload,
    _=Depends(require_bearer),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Update persisted settings for the authenticated owner."""

    try:
        user = _get_or_create_default_user(db)
        record = _get_or_create_settings(db, user)

        updated = dict(DEFAULT_SETTINGS)
        updated.update(record.settings or {})

        for key, value in payload.model_dump(exclude_unset=True).items():
            updated[key] = value

        record.settings = updated
        db.add(record)
        db.commit()
        db.refresh(record)
        return record.settings
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Failed to persist settings: {exc!s}")
