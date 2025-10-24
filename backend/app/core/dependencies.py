"""Shared FastAPI dependency helpers."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from ..db.session import get_db
from ..models.database import User
from .jwt import get_current_user, require_owner


CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentOwner = Annotated[User, Depends(require_owner)]
DatabaseSession = Annotated[Session, Depends(get_db)]


def require_user(current_user: User = Depends(get_current_user)) -> User:
    """Ensure the request is authenticated and return the user."""
    return current_user


def require_owner_user(current_user: User = Depends(require_owner)) -> User:
    """Ensure the authenticated user has owner permissions."""
    return current_user


__all__ = [
    "CurrentUser",
    "CurrentOwner",
    "DatabaseSession",
    "require_user",
    "require_owner_user",
]
