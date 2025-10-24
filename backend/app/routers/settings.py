from fastapi import APIRouter, Depends

from ..core.dependencies import require_user


router = APIRouter(dependencies=[Depends(require_user)])

_settings = {"stop_loss": 2.0, "take_profit": 5.0, "position_size": 1000, "max_positions": 10}


@router.get("/settings")
def get_settings():
    return _settings


@router.post("/settings")
def set_settings(payload: dict):
    _settings.update({k: float(payload.get(k, v)) for k, v in _settings.items()})
    return _settings
