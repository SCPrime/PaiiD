"""
Strategy API Routes
Endpoints for managing trading strategies
"""
# ruff: noqa: I001, E402 - sys.path modification must occur before import

import sys
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from ..core.unified_auth import get_current_user_unified
from ..db.session import get_db
from ..models.database import Strategy, User
from ..services.strategy_templates import (
    customize_template_for_risk,
    filter_templates_by_risk,
    get_all_templates,
    get_template_by_id,
    get_template_compatibility_score,
)

# Add backend root to path for strategies import (must be before import)
backend_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_root))

from strategies.under4_multileg import Under4MultilegConfig

router = APIRouter()


class StrategyConfigRequest(BaseModel):
    """Request model for saving strategy configuration with validation"""

    strategy_type: str = Field(
        ...,
        min_length=1,
        max_length=50,
        pattern=r"^[a-z0-9\-]+$",
        description="Strategy type identifier (lowercase, alphanumeric + hyphens)",
        examples=["under4-multileg", "trend-following", "custom"],
    )
    config: dict = Field(..., description="Strategy configuration parameters")

    @field_validator("strategy_type")
    @classmethod
    def validate_strategy_type(cls, v):
        """Validate strategy type"""
        allowed_types = [
            "under4-multileg",
            "dex-meme-scout",
            "trend-following",
            "mean-reversion",
            "momentum",
            "custom",
        ]
        if v not in allowed_types:
            raise ValueError(
                f"Invalid strategy type. Allowed: {', '.join(allowed_types)}"
            )
        return v


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

    @field_validator("strategy_type")
    @classmethod
    def validate_strategy_type(cls, v):
        """Validate strategy type"""
        allowed_types = [
            "under4-multileg",
            "dex-meme-scout",
            "trend-following",
            "mean-reversion",
            "momentum",
            "custom",
        ]
        if v not in allowed_types:
            raise ValueError(
                f"Invalid strategy type. Allowed: {', '.join(allowed_types)}"
            )
        return v


@router.post("/strategies/save")
async def save_strategy(
    request: StrategyConfigRequest,
    current_user: User = Depends(get_current_user_unified),
):
    """
    Save strategy configuration

    POST /api/strategies/save
    Body: {
        "strategy_type": "under4-multileg",
        "config": { ... }
    }
    """
    try:
        # Validate config based on strategy type
        if request.strategy_type == "under4-multileg":
            # Validate against Pydantic model
            config = Under4MultilegConfig(**request.config)
            validated_config = config.model_dump()
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown strategy type: {request.strategy_type}",
            )

        # Use service to save strategy
        from ..services.strategy_execution_service import get_strategy_execution_service

        strategy_service = get_strategy_execution_service()
        result = strategy_service.save_strategy(
            user_id=current_user.id,
            strategy_type=request.strategy_type,
            config=validated_config,
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/strategies/load/{strategy_type}")
async def load_strategy(
    strategy_type: str, current_user: User = Depends(get_current_user_unified)
):
    """
    Load strategy configuration

    GET /api/strategies/load/under4-multileg
    """
    try:
        from ..services.strategy_execution_service import get_strategy_execution_service

        strategy_service = get_strategy_execution_service()

        # Provide default config if strategy type is under4-multileg
        default_config = None
        if strategy_type == "under4-multileg":
            default_config = Under4MultilegConfig().model_dump()

        result = strategy_service.load_strategy(
            user_id=current_user.id,
            strategy_type=strategy_type,
            default_config=default_config,
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/strategies/list")
async def list_strategies(current_user: User = Depends(get_current_user_unified)):
    """
    List all available strategies

    GET /api/strategies/list
    """
    try:
        from ..services.strategy_execution_service import get_strategy_execution_service

        strategy_service = get_strategy_execution_service()

        strategies = strategy_service.list_strategies(user_id=current_user.id)
        return {"strategies": strategies}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/strategies/run")
async def run_strategy(
    request: StrategyRunRequest, current_user: User = Depends(get_current_user_unified)
):
    """
    Run a strategy (execute morning routine)

    POST /api/strategies/run
    Body: {
        "strategy_type": "under4-multileg",
        "dry_run": true
    }
    """
    try:
        from ..services.strategy_execution_service import get_strategy_execution_service

        strategy_service = get_strategy_execution_service()

        # Create strategy instance for validation (if needed)
        if request.strategy_type == "under4-multileg":
            # This is just for validation, the service handles execution
            pass
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown strategy type: {request.strategy_type}",
            )

        if request.dry_run:
            return strategy_service.execute_strategy_dry_run(
                user_id=current_user.id,
                strategy_type=request.strategy_type,
            )

        return strategy_service.execute_strategy_live(
            user_id=current_user.id,
            strategy_type=request.strategy_type,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete("/strategies/{strategy_type}")
async def delete_strategy(
    strategy_type: str, current_user: User = Depends(get_current_user_unified)
):
    """
    Delete a saved strategy configuration

    DELETE /api/strategies/under4-multileg
    """
    try:
        from ..services.strategy_execution_service import get_strategy_execution_service

        strategy_service = get_strategy_execution_service()

        result = strategy_service.delete_strategy(
            user_id=current_user.id,
            strategy_type=strategy_type,
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/strategies/execution-history")
async def get_strategy_execution_history(
    limit: int = 50, current_user: User = Depends(get_current_user_unified)
):
    """Return recent execution history for the authenticated user."""

    if limit <= 0:
        raise HTTPException(status_code=400, detail="limit must be positive")

    try:
        from ..services.strategy_execution_service import get_strategy_execution_service

        service = get_strategy_execution_service()
        history = service.list_execution_history(user_id=current_user.id, limit=limit)
        return {"history": history}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch execution history: {exc!s}",
        ) from exc


# ========================================
# STRATEGY TEMPLATES ENDPOINTS
# ========================================


@router.get("/strategies/templates")
async def get_strategy_templates(
    filter_by_risk: bool | None = True,
    current_user: User = Depends(get_current_user_unified),
    db: Session = Depends(get_db),
):
    """
    Get all available strategy templates

    Query params:
    - filter_by_risk: If true, filter templates by user's risk tolerance (default: true)

    Returns list of templates with metadata and compatibility scores.
    """
    try:
        # Get user preferences from authenticated user
        user = db.query(User).filter(User.id == current_user.id).first()
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
        market_volatility = "Medium"  # PHASE 1: Get from VIX/market data service
        portfolio_value = 100000  # PHASE 1: Get from Alpaca account.portfolio_value

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
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch strategy templates: {e!s}"
        ) from e


@router.get("/strategies/templates/{template_id}")
async def get_strategy_template(
    template_id: str,
    customize: bool | None = True,
    current_user: User = Depends(get_current_user_unified),
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

        # Get user preferences for customization from authenticated user
        config = template.config
        if customize:
            user = db.query(User).filter(User.id == current_user.id).first()
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
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch template: {e!s}"
        ) from e


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

    @field_validator("custom_name")
    @classmethod
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
    current_user: User = Depends(get_current_user_unified),
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

        # Use authenticated user from JWT
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

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
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to clone template: {e!s}"
        ) from e
