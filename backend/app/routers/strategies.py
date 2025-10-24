"""Strategy API Routes
Endpoints for managing trading strategies
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session

from ..core.auth import require_bearer
from ..db.session import get_db
from ..models.database import Strategy, User
from ..strategies.repository import (
    DEFAULT_FEATURE_FLAGS,
    DEFAULT_MODEL_KEY,
    delete_strategy_config,
    get_strategy_config,
    get_strategy_history,
    get_strategy_performance_logs,
    list_strategy_configs,
    record_strategy_run,
    save_strategy_config,
    summarise_performance,
    summarise_versions,
)
from ..strategies.schemas import (
    StrategyConfigSchema,
    StrategyListEntry,
    StrategyPerformanceLogSchema,
    StrategySaveResponse,
    StrategyVersionSchema,
)
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


SUPPORTED_STRATEGY_TYPES = ["under4-multileg", "custom"]
AVAILABLE_STRATEGIES = ["under4-multileg", "custom"]
ALLOWED_MODEL_KEYS = ["paiid-pro", "paiid-lite", "gpt-4o-mini"]


def _merge_feature_flags(flags: Dict[str, Any] | None) -> Dict[str, bool]:
    merged = dict(DEFAULT_FEATURE_FLAGS)
    if flags:
        for key, value in flags.items():
            merged[key] = bool(value)
    return merged


def _default_config(strategy_type: str) -> Dict[str, Any]:
    if strategy_type == "under4-multileg":
        return Under4MultilegConfig().model_dump()
    if strategy_type == "custom":
        return {"name": "Custom Strategy", "parameters": {}, "notes": ""}
    raise HTTPException(status_code=404, detail=f"Strategy '{strategy_type}' not found")


def _build_strategy_schema(
    *,
    strategy_type: str,
    config: Dict[str, Any],
    model_key: str | None,
    feature_flags: Dict[str, Any] | None,
    version: int,
    history_models=None,
    performance_models=None,
    is_default: bool = False,
) -> StrategyConfigSchema:
    history_models = history_models or []
    performance_models = performance_models or []
    history = [
        StrategyVersionSchema(**data)
        for data in summarise_versions(history_models)
    ]
    performance = [
        StrategyPerformanceLogSchema(**data)
        for data in summarise_performance(performance_models)
    ]

    return StrategyConfigSchema(
        strategy_type=strategy_type,
        config=config,
        model_key=model_key or DEFAULT_MODEL_KEY,
        feature_flags=_merge_feature_flags(feature_flags),
        version=version,
        history=history,
        performance=performance,
        is_default=is_default,
    )


class StrategyConfigRequest(BaseModel):
    """Request model for saving strategy configuration with validation"""

    strategy_type: str = Field(
        ...,
        min_length=1,
        max_length=50,
        pattern=r"^[a-z0-9\-]+$",
        description="Strategy type identifier (lowercase, alphanumeric + hyphens)",
        examples=["under4-multileg", "custom"],
    )
    config: Dict[str, Any] = Field(..., description="Strategy configuration parameters")
    model_key: str = Field(
        default=DEFAULT_MODEL_KEY,
        description="Model identifier used to power the strategy",
        examples=ALLOWED_MODEL_KEYS,
    )
    feature_flags: Dict[str, bool] = Field(
        default_factory=dict,
        description="Feature toggle overrides for the strategy",
    )
    changes_summary: str | None = Field(
        default=None,
        max_length=500,
        description="Optional description of configuration updates",
    )

    @validator("strategy_type")
    def validate_strategy_type(cls, v: str) -> str:
        if v not in SUPPORTED_STRATEGY_TYPES:
            raise ValueError(
                f"Invalid strategy type. Allowed: {', '.join(SUPPORTED_STRATEGY_TYPES)}"
            )
        return v

    @validator("model_key")
    def validate_model_key(cls, v: str) -> str:
        if v not in ALLOWED_MODEL_KEYS:
            raise ValueError(
                f"Invalid model. Allowed models: {', '.join(ALLOWED_MODEL_KEYS)}"
            )
        return v

    @validator("feature_flags")
    def validate_feature_flags(cls, v: Dict[str, bool]) -> Dict[str, bool]:
        return {key: bool(value) for key, value in v.items()}


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
    notes: str | None = Field(
        default=None, description="Optional notes attached to the run request"
    )

    @validator("strategy_type")
    def validate_strategy_type(cls, v: str) -> str:
        if v not in SUPPORTED_STRATEGY_TYPES:
            raise ValueError(
                f"Invalid strategy type. Allowed: {', '.join(SUPPORTED_STRATEGY_TYPES)}"
            )
        return v


@router.post("/strategies/save")
async def save_strategy(
    request: StrategyConfigRequest,
    db: Session = Depends(get_db),
    _=Depends(require_bearer),
):
    """
    Save strategy configuration

    POST /api/strategies/save
    Body: {
        "strategy_type": "under4-multileg",
        "config": { ... }
    }
    """
    owner_id = "default"  # TODO: Get from auth

    try:
        if request.strategy_type == "under4-multileg":
            config_model = Under4MultilegConfig(**request.config)
            validated_config = config_model.model_dump()
        elif request.strategy_type == "custom":
            validated_config = request.config
        else:
            raise HTTPException(
                status_code=400, detail=f"Unknown strategy type: {request.strategy_type}"
            )

        record, version = save_strategy_config(
            db,
            owner_id=owner_id,
            strategy_key=request.strategy_type,
            config=validated_config,
            model_key=request.model_key,
            feature_flags=request.feature_flags,
            changes_summary=request.changes_summary,
            created_by=owner_id,
        )

        history_models = get_strategy_history(db, strategy_config_id=record.id, limit=10)
        performance_models = get_strategy_performance_logs(
            db, strategy_config_id=record.id, limit=10
        )

        strategy_schema = _build_strategy_schema(
            strategy_type=record.strategy_key,
            config=record.current_config or {},
            model_key=record.model_key,
            feature_flags=record.feature_flags or {},
            version=record.current_version or 1,
            history_models=history_models,
            performance_models=performance_models,
            is_default=False,
        )

        response = StrategySaveResponse(
            success=True,
            message=f"Strategy '{request.strategy_type}' saved (v{version.version_number})",
            strategy=strategy_schema,
            version=version.version_number,
        )
        return response.model_dump(mode="json")

    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive logging
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/strategies/load/{strategy_type}")
async def load_strategy(
    strategy_type: str,
    db: Session = Depends(get_db),
    _=Depends(require_bearer),
):
    """
    Load strategy configuration

    GET /api/strategies/load/under4-multileg
    """
    owner_id = "default"  # TODO: Get from auth

    try:
        record = get_strategy_config(db, owner_id=owner_id, strategy_key=strategy_type)
        if record is None:
            default_schema = _build_strategy_schema(
                strategy_type=strategy_type,
                config=_default_config(strategy_type),
                model_key=DEFAULT_MODEL_KEY,
                feature_flags=DEFAULT_FEATURE_FLAGS,
                version=1,
                is_default=True,
            )
            return default_schema.model_dump(mode="json")

        history_models = get_strategy_history(db, strategy_config_id=record.id, limit=10)
        performance_models = get_strategy_performance_logs(
            db, strategy_config_id=record.id, limit=10
        )

        schema = _build_strategy_schema(
            strategy_type=record.strategy_key,
            config=record.current_config or {},
            model_key=record.model_key,
            feature_flags=record.feature_flags or {},
            version=record.current_version or 1,
            history_models=history_models,
            performance_models=performance_models,
            is_default=False,
        )
        return schema.model_dump(mode="json")

    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/strategies/list")
async def list_strategies(
    db: Session = Depends(get_db),
    _=Depends(require_bearer),
):
    """
    List all available strategies

    GET /api/strategies/list
    """
    owner_id = "default"  # TODO: Get from auth

    records = list_strategy_configs(db, owner_id=owner_id)
    entries: List[StrategyListEntry] = [
        StrategyListEntry(
            strategy_type=record.strategy_key,
            has_config=True,
            model_key=record.model_key,
            updated_at=record.updated_at,
        )
        for record in records
    ]

    configured = {entry.strategy_type for entry in entries}
    for strategy_type in AVAILABLE_STRATEGIES:
        if strategy_type not in configured:
            entries.append(StrategyListEntry(strategy_type=strategy_type, has_config=False))

    return {"strategies": [entry.model_dump(mode="json") for entry in entries]}


@router.post("/strategies/run")
async def run_strategy(
    request: StrategyRunRequest,
    db: Session = Depends(get_db),
    _=Depends(require_bearer),
):
    """
    Run a strategy (execute morning routine)

    POST /api/strategies/run
    Body: {
        "strategy_type": "under4-multileg",
        "dry_run": true
    }
    """
    owner_id = "default"  # TODO: Get from auth

    try:
        record = get_strategy_config(db, owner_id=owner_id, strategy_key=request.strategy_type)
        if record is None:
            raise HTTPException(status_code=404, detail=f"Strategy '{request.strategy_type}' not found")

        config_payload = record.current_config or {}
        if request.strategy_type == "under4-multileg":
            validated = Under4MultilegConfig(**config_payload).model_dump()
            create_under4_multileg_strategy(validated)
        elif request.strategy_type != "custom":
            raise HTTPException(status_code=400, detail=f"Unknown strategy type: {request.strategy_type}")

        run_type = "dry-run" if request.dry_run else "live"
        metrics = {
            "status": "queued" if request.dry_run else "pending-execution",
            "requested_at": datetime.utcnow().isoformat(),
        }

        log = record_strategy_run(
            db,
            strategy_config_id=record.id,
            version_number=record.current_version or 1,
            run_type=run_type,
            metrics=metrics,
            notes=request.notes,
        )

        return {
            "success": True,
            "dry_run": request.dry_run,
            "message": "Strategy run recorded",
            "log_id": log.id,
            "version": record.current_version,
        }

    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=str(exc))


@router.delete("/strategies/{strategy_type}")
async def delete_strategy(
    strategy_type: str,
    db: Session = Depends(get_db),
    _=Depends(require_bearer),
):
    """
    Delete a saved strategy configuration

    DELETE /api/strategies/under4-multileg
    """
    owner_id = "default"  # TODO: Get from auth

    try:
        removed = delete_strategy_config(db, owner_id=owner_id, strategy_key=strategy_type)
        if not removed:
            raise HTTPException(status_code=404, detail=f"Strategy '{strategy_type}' not found")
        return {"success": True, "message": f"Strategy '{strategy_type}' deleted successfully"}
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/strategies/history/{strategy_type}")
async def strategy_history(
    strategy_type: str,
    db: Session = Depends(get_db),
    _=Depends(require_bearer),
):
    owner_id = "default"  # TODO: Get from auth

    record = get_strategy_config(db, owner_id=owner_id, strategy_key=strategy_type)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Strategy '{strategy_type}' not found")

    history_models = get_strategy_history(db, strategy_config_id=record.id)
    history = [
        StrategyVersionSchema(**data).model_dump(mode="json")
        for data in summarise_versions(history_models)
    ]
    return {"strategy_type": strategy_type, "history": history}


@router.get("/strategies/performance/{strategy_type}")
async def strategy_performance(
    strategy_type: str,
    db: Session = Depends(get_db),
    _=Depends(require_bearer),
):
    owner_id = "default"  # TODO: Get from auth

    record = get_strategy_config(db, owner_id=owner_id, strategy_key=strategy_type)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Strategy '{strategy_type}' not found")

    performance_models = get_strategy_performance_logs(db, strategy_config_id=record.id)
    performance = [
        StrategyPerformanceLogSchema(**data).model_dump(mode="json")
        for data in summarise_performance(performance_models)
    ]
    return {"strategy_type": strategy_type, "performance": performance}


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
