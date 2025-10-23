import logging

from fastapi import APIRouter, Depends

from ..core.jwt import get_current_user
from ..models.database import User
from .error_utils import log_and_sanitize_exceptions


logger = logging.getLogger(__name__)

router = APIRouter()

_settings = {"stop_loss": 2.0, "take_profit": 5.0, "position_size": 1000, "max_positions": 10}


@router.get("/settings")
@log_and_sanitize_exceptions(
    logger,
    public_message="Failed to fetch settings",
    log_message="Unable to fetch settings",
)
def get_settings(_current_user: User = Depends(get_current_user)):
    return _settings


@router.post("/settings")
@log_and_sanitize_exceptions(
    logger,
    public_message="Failed to update settings",
    log_message="Unable to update settings",
)
def set_settings(
    payload: dict,
    _current_user: User = Depends(get_current_user),
):
    _settings.update({k: float(payload.get(k, v)) for k, v in _settings.items()})
    return _settings
