"""Authentication helpers shared across API routers."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status

from ..models.database import User
from .jwt import get_current_user as _get_current_user


# ---------------------------------------------------------------------------
# Shared dependency helpers
# ---------------------------------------------------------------------------

# typing.Annotated allows us to attach dependencies to type hints so handlers can
# simply declare ``current_user: CurrentUser`` to receive the authenticated user.
CurrentUser = Annotated[User, Depends(_get_current_user)]


def require_current_user(current_user: CurrentUser) -> User:
    """Return the authenticated user for a request."""

    return current_user


def require_active_user(current_user: CurrentUser) -> User:
    """Ensure the authenticated user account is active."""

    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )
    return current_user


# ---------------------------------------------------------------------------
# Backwards compatibility
# ---------------------------------------------------------------------------
#
# Older routers still import ``require_bearer`` from the legacy API token guard.
# Re-export it so imports continue to work while routing through the JWT flow.
require_bearer = require_current_user

__all__ = [
    "CurrentUser",
    "require_active_user",
    "require_current_user",
    "require_bearer",
]
