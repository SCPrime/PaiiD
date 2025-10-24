from fastapi import APIRouter, Depends

from ..core.jwt import get_current_user


router = APIRouter()

_settings = {"stop_loss": 2.0, "take_profit": 5.0, "position_size": 1000, "max_positions": 10}


@router.get("/settings")
def get_settings():
    return _settings


@router.post("/settings")
def set_settings(payload: dict, _=Depends(get_current_user)):
    _settings.update({k: float(payload.get(k, v)) for k, v in _settings.items()})
    return _settings
