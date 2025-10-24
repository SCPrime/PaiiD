"""
Strategy API Routes
Endpoints for managing trading strategies
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, root_validator, validator
from sqlalchemy.orm import Session

from ..core.auth import require_bearer
from ..db.session import get_db
from ..models.database import Strategy, User
from ..services.strategy_templates import (
    customize_template_for_risk,
    filter_templates_by_risk,
    get_all_templates,
    get_template_by_id,
    get_template_compatibility_score,
)


# Add backend root to path for strategies import
backend_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_root))

from strategies.under4_multileg import Under4MultilegConfig, create_under4_multileg_strategy


router = APIRouter()


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


def _serialize_strategy(strategy: Strategy) -> dict[str, Any]:
    config = strategy.config or {}
    response = {
        "id": strategy.client_strategy_id or config.get("id") or f"strategy-{strategy.id}",
        "dbId": strategy.id,
        "name": strategy.name,
        "description": strategy.description,
        "strategy_type": strategy.strategy_type,
        "config": config,
        "is_active": strategy.is_active,
        "is_autopilot": strategy.is_autopilot,
        "created_at": strategy.created_at.isoformat() if strategy.created_at else None,
        "updated_at": strategy.updated_at.isoformat() if strategy.updated_at else None,
    }
    # Preserve commonly accessed fields for compatibility with frontend code
    for key in ["rules", "riskParams", "entry", "exit", "status", "aiPrompt"]:
        if key in config:
            response[key] = config[key]
    return response


def _get_strategy_by_identifier(
    db: Session, user: User, identifier: str
) -> Strategy | None:
    strategy = (
        db.query(Strategy)
        .filter(Strategy.user_id == user.id, Strategy.client_strategy_id == identifier)
        .first()
    )
    if strategy:
        return strategy

    # Try integer primary key fallback
    try:
        strategy_id = int(identifier)
    except ValueError:
        strategy_id = None

    if strategy_id is not None:
        strategy = (
            db.query(Strategy)
            .filter(Strategy.user_id == user.id, Strategy.id == strategy_id)
            .first()
        )
        if strategy:
            return strategy

    # Fallback by strategy type
    return (
        db.query(Strategy)
        .filter(Strategy.user_id == user.id, Strategy.strategy_type == identifier)
        .first()
    )

class StrategyPayload(BaseModel):
    """Generic strategy payload accepted from the frontend."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    strategy_type: str | None = Field(default="custom", max_length=50)
    symbol: str | None = None
    rules: dict[str, Any] | None = None
    riskParams: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
    config: dict[str, Any] | None = None
    client_id: str | None = Field(default=None, alias="clientId")
    legacy_id: str | None = Field(default=None, alias="id")

    class Config:
        allow_population_by_field_name = True
        extra = "allow"

    @root_validator(pre=True)
    def ensure_config(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Ensure config is always populated with the original payload."""

        if "config" not in values or values.get("config") is None:
            # Store a shallow copy of the payload as config for traceability
            cloned = {k: v for k, v in values.items() if k not in {"config"}}
            values["config"] = cloned
        return values

    @property
    def effective_client_id(self) -> str | None:
        return self.client_id or self.legacy_id


class StrategyRunRequest(BaseModel):
    """Request model for running a strategy with validation"""

    strategy_type: str = Field(
        ...,
        min_length=1,
        max_length=50,
        pattern=r"^[a-z0-9\-]+$",
        description="Strategy type identifier",
    )
    dry_run: bool = Field(
        default=True, description="Dry run mode (no actual execution, default: true)"
    )

    @validator("strategy_type")
    def validate_strategy_type(cls, v):
        """Validate strategy type"""
        allowed_types = [
            "under4-multileg",
            "trend-following",
            "mean-reversion",
            "momentum",
            "custom",
        ]
        if v not in allowed_types:
            raise ValueError(f"Invalid strategy type. Allowed: {', '.join(allowed_types)}")
        return v


@router.post("/strategies/save", status_code=status.HTTP_201_CREATED)
def save_strategy(
    request: StrategyPayload,
    _=Depends(require_bearer),
    db: Session = Depends(get_db),
):
    """Create or update a strategy using database persistence."""

    user = _get_or_create_default_user(db)
    client_id = request.effective_client_id

    existing = None
    if client_id:
        existing = _get_strategy_by_identifier(db, user, client_id)

    payload_config = request.config or {}
    payload_config.setdefault("id", client_id or request.legacy_id)
    payload_config.setdefault("clientId", client_id)

    if existing:
        merged_config = dict(existing.config or {})
        merged_config.update(payload_config)

        existing.name = request.name
        existing.description = request.description
        existing.strategy_type = request.strategy_type or existing.strategy_type
        existing.client_strategy_id = client_id or existing.client_strategy_id
        existing.config = merged_config
        existing.updated_at = datetime.utcnow()

        db.add(existing)
        db.commit()
        db.refresh(existing)
        return _serialize_strategy(existing)

    strategy = Strategy(
        user_id=user.id,
        name=request.name,
        description=request.description,
        strategy_type=request.strategy_type or "custom",
        client_strategy_id=client_id,
        config=payload_config,
        is_active=payload_config.get("status") == "active",
        is_autopilot=bool(payload_config.get("is_autopilot")),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(strategy)
    db.commit()
    db.refresh(strategy)
    return _serialize_strategy(strategy)


@router.get("/strategies/load/{strategy_identifier}")
def load_strategy(
    strategy_identifier: str,
    _=Depends(require_bearer),
    db: Session = Depends(get_db),
):
    """Load a specific strategy configuration."""

    user = _get_or_create_default_user(db)
    strategy = _get_strategy_by_identifier(db, user, strategy_identifier)

    if strategy:
        return {
            "strategy_type": strategy.strategy_type,
            "config": strategy.config or {},
            "is_default": False,
        }

    if strategy_identifier == "under4-multileg":
        default_config = Under4MultilegConfig()
        return {
            "strategy_type": strategy_identifier,
            "config": default_config.model_dump(),
            "is_default": True,
        }

    raise HTTPException(status_code=404, detail=f"Strategy '{strategy_identifier}' not found")


@router.get("/strategies/list")
def list_strategies(
    limit: int = 100,
    offset: int = 0,
    _=Depends(require_bearer),
    db: Session = Depends(get_db),
):
    """List saved strategies with pagination support."""

    user = _get_or_create_default_user(db)
    query = (
        db.query(Strategy)
        .filter(Strategy.user_id == user.id)
        .order_by(Strategy.updated_at.desc())
    )
    total = query.count()
    strategies = query.offset(offset).limit(limit).all()

    return {
        "strategies": [_serialize_strategy(strategy) for strategy in strategies],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.post("/strategies/run")
def run_strategy(
    request: StrategyRunRequest,
    _=Depends(require_bearer),
    db: Session = Depends(get_db),
):
    """
    Run a strategy (execute morning routine)

    POST /api/strategies/run
    Body: {
        "strategy_type": "under4-multileg",
        "dry_run": true
    }
    """
    user = _get_or_create_default_user(db)

    try:
        strategy_record = _get_strategy_by_identifier(db, user, request.strategy_type)
        config_dict: dict[str, Any] | None = None
        if strategy_record and isinstance(strategy_record.config, dict):
            config_dict = strategy_record.config.get("config") or strategy_record.config

        # Create strategy instance
        if request.strategy_type == "under4-multileg":
            validated = None
            if config_dict:
                try:
                    validated = Under4MultilegConfig(**config_dict).model_dump()
                except Exception:
                    validated = Under4MultilegConfig().model_dump()
            else:
                validated = Under4MultilegConfig().model_dump()

            strategy = create_under4_multileg_strategy(validated)
        else:
            raise HTTPException(
                status_code=400, detail=f"Unknown strategy type: {request.strategy_type}"
            )

        # TODO: Get Alpaca client from user's credentials
        # For now, return mock results

        if request.dry_run:
            return {
                "success": True,
                "dry_run": True,
                "message": "Strategy dry run completed",
                "results": {
                    "candidates": ["SNDL", "NOK", "SOFI", "PLUG"],
                    "proposals": [
                        {
                            "type": "BUY_CALL",
                            "symbol": "SNDL",
                            "strike": 3.50,
                            "expiry": "2025-11-15",
                            "delta": 0.60,
                            "qty": 3,
                        },
                        {
                            "type": "SELL_PUT",
                            "symbol": "NOK",
                            "strike": 3.00,
                            "expiry": "2025-11-15",
                            "delta": 0.20,
                            "qty": 2,
                        },
                    ],
                    "approved_trades": 2,
                },
            }
        else:
            # TODO: Implement actual execution
            raise HTTPException(status_code=501, detail="Live execution not yet implemented")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/strategies/{strategy_id}")
def get_strategy(
    strategy_id: str,
    _=Depends(require_bearer),
    db: Session = Depends(get_db),
):
    """Fetch a single strategy by identifier."""

    user = _get_or_create_default_user(db)
    strategy = _get_strategy_by_identifier(db, user, strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return _serialize_strategy(strategy)


@router.put("/strategies/{strategy_id}")
def update_strategy(
    strategy_id: str,
    request: StrategyPayload,
    _=Depends(require_bearer),
    db: Session = Depends(get_db),
):
    """Update an existing strategy."""

    user = _get_or_create_default_user(db)
    strategy = _get_strategy_by_identifier(db, user, strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    payload_config = request.config or {}
    payload_config.setdefault("id", request.effective_client_id or strategy.client_strategy_id)
    payload_config.setdefault("clientId", request.effective_client_id or strategy.client_strategy_id)

    merged_config = dict(strategy.config or {})
    merged_config.update(payload_config)

    strategy.name = request.name
    strategy.description = request.description
    strategy.strategy_type = request.strategy_type or strategy.strategy_type
    strategy.client_strategy_id = request.effective_client_id or strategy.client_strategy_id
    strategy.config = merged_config
    strategy.updated_at = datetime.utcnow()

    db.add(strategy)
    db.commit()
    db.refresh(strategy)
    return _serialize_strategy(strategy)


@router.delete("/strategies/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_strategy(
    strategy_id: str,
    _=Depends(require_bearer),
    db: Session = Depends(get_db),
):
    """Delete a strategy from the database."""

    user = _get_or_create_default_user(db)
    strategy = _get_strategy_by_identifier(db, user, strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    db.delete(strategy)
    db.commit()
    return None


# ========================================
# STRATEGY TEMPLATES ENDPOINTS
# ========================================


@router.get("/strategies/templates")
async def get_strategy_templates(
    filter_by_risk: bool | None = True, _=Depends(require_bearer), db: Session = Depends(get_db)
):
    """
    Get all available strategy templates

    Query params:
    - filter_by_risk: If true, filter templates by user's risk tolerance (default: true)

    Returns list of templates with metadata and compatibility scores.
    """
    try:
        # Get user preferences
        user = db.query(User).filter(User.id == 1).first()
        preferences = user.preferences if user else {}
        risk_tolerance = preferences.get("risk_tolerance", 50)

        # Get templates
        if filter_by_risk:
            templates = filter_templates_by_risk(risk_tolerance)
        else:
            templates = get_all_templates()

        # Format response with compatibility scores
        # For market volatility, we'd normally fetch from market data API
        # For now, use a default value
        market_volatility = "Medium"  # TODO: Get from market data service
        portfolio_value = 100000  # TODO: Get from account API

        response = []
        for template in templates:
            compatibility_score = get_template_compatibility_score(
                template, risk_tolerance, market_volatility, portfolio_value
            )

            response.append(
                {
                    "id": template.id,
                    "name": template.name,
                    "description": template.description,
                    "strategy_type": template.strategy_type,
                    "risk_level": template.risk_level,
                    "expected_win_rate": template.expected_win_rate,
                    "avg_return_percent": template.avg_return_percent,
                    "max_drawdown_percent": template.max_drawdown_percent,
                    "recommended_for": template.recommended_for,
                    "compatibility_score": round(compatibility_score, 1),
                    "config": template.config,
                }
            )

        # Sort by compatibility score (highest first)
        response.sort(key=lambda x: x["compatibility_score"], reverse=True)

        return {
            "templates": response,
            "user_risk_tolerance": risk_tolerance,
            "market_volatility": market_volatility,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch strategy templates: {e!s}")


@router.get("/strategies/templates/{template_id}")
async def get_strategy_template(
    template_id: str,
    customize: bool | None = True,
    _=Depends(require_bearer),
    db: Session = Depends(get_db),
):
    """
    Get a specific strategy template by ID

    Query params:
    - customize: If true, customize config parameters based on user's risk tolerance

    Returns template with full configuration.
    """
    try:
        # Get template
        template = get_template_by_id(template_id)

        # Get user preferences for customization
        config = template.config
        if customize:
            user = db.query(User).filter(User.id == 1).first()
            preferences = user.preferences if user else {}
            risk_tolerance = preferences.get("risk_tolerance", 50)
            config = customize_template_for_risk(template, risk_tolerance)

        return {
            "id": template.id,
            "name": template.name,
            "description": template.description,
            "strategy_type": template.strategy_type,
            "risk_level": template.risk_level,
            "expected_win_rate": template.expected_win_rate,
            "avg_return_percent": template.avg_return_percent,
            "max_drawdown_percent": template.max_drawdown_percent,
            "recommended_for": template.recommended_for,
            "config": config,
            "customized": customize,
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch template: {e!s}")


class CloneTemplateRequest(BaseModel):
    """Request model for cloning a template with validation"""

    custom_name: str | None = Field(
        None,
        min_length=1,
        max_length=100,
        description="Custom name for the cloned strategy (1-100 characters)",
    )
    customize_config: bool | None = Field(
        True, description="Customize based on risk tolerance (default: true)"
    )
    config_overrides: dict[str, Any] | None = Field(
        None, description="Manual config overrides (key-value pairs)"
    )

    @validator("custom_name")
    def validate_custom_name(cls, v):
        """Validate custom name"""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Custom name cannot be empty or whitespace")
            if len(v) > 100:
                raise ValueError("Custom name cannot exceed 100 characters")
        return v


@router.post("/strategies/templates/{template_id}/clone")
async def clone_strategy_template(
    template_id: str,
    request: CloneTemplateRequest,
    _=Depends(require_bearer),
    db: Session = Depends(get_db),
):
    """
    Clone a strategy template to user's strategies

    Creates a new Strategy database entry from the template.

    POST /api/strategies/templates/trend-following-macd/clone
    Body: {
        "custom_name": "My Trend Strategy",
        "customize_config": true,
        "config_overrides": {"position_size_percent": 8.0}
    }
    """
    try:
        # Get template
        template = get_template_by_id(template_id)

        # Get or create user
        user = db.query(User).filter(User.id == 1).first()
        if not user:
            user = User(id=1, email="default@paiid.com", preferences={"risk_tolerance": 50})
            db.add(user)
            db.commit()
            db.refresh(user)

        # Prepare config
        config = template.config.copy()

        # Customize based on risk tolerance
        if request.customize_config:
            preferences = user.preferences or {}
            risk_tolerance = preferences.get("risk_tolerance", 50)
            config = customize_template_for_risk(template, risk_tolerance)

        # Apply manual overrides
        if request.config_overrides:
            config.update(request.config_overrides)

        # Generate name
        strategy_name = request.custom_name or f"{template.name} (Cloned)"

        # Create Strategy database entry
        new_strategy = Strategy(
            user_id=user.id,
            name=strategy_name,
            description=template.description,
            strategy_type=template.strategy_type,
            config=config,
            is_active=False,  # User must activate manually
            is_autopilot=False,
        )

        db.add(new_strategy)
        db.commit()
        db.refresh(new_strategy)

        return {
            "success": True,
            "message": f"Template '{template.name}' cloned successfully",
            "strategy": {
                "id": new_strategy.id,
                "name": new_strategy.name,
                "description": new_strategy.description,
                "strategy_type": new_strategy.strategy_type,
                "config": new_strategy.config,
                "is_active": new_strategy.is_active,
                "created_at": new_strategy.created_at.isoformat(),
            },
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clone template: {e!s}")
