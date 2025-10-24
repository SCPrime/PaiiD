"""Utility helpers for working with timezone-aware timestamps."""
from __future__ import annotations

from datetime import datetime, timezone

UTC = timezone.utc


def utc_now() -> datetime:
    """Return the current UTC time as a timezone-aware ``datetime``."""
    return datetime.now(tz=UTC)


def ensure_utc(dt: datetime) -> datetime:
    """Ensure that the provided ``datetime`` is timezone-aware in UTC."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def utc_now_isoformat(*, use_z_suffix: bool = True) -> str:
    """Return the current UTC time encoded as an ISO 8601 string."""
    iso_value = utc_now().isoformat()
    if use_z_suffix:
        return iso_value.replace("+00:00", "Z")
    return iso_value


def to_isoformat(dt: datetime, *, use_z_suffix: bool = True) -> str:
    """Serialise ``datetime`` values as ISO 8601 strings with optional ``Z`` suffix."""
    iso_value = ensure_utc(dt).isoformat()
    if use_z_suffix:
        return iso_value.replace("+00:00", "Z")
    return iso_value
