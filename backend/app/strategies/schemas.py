"""Pydantic schemas for strategy persistence"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class StrategyVersionSchema(BaseModel):
    """Historical version metadata"""

    version_number: int = Field(..., description="Sequential version number")
    created_at: datetime = Field(..., description="When the version was created")
    created_by: Optional[str] = Field(None, description="User who created the version")
    changes_summary: Optional[str] = Field(
        None, description="Summary of the changes introduced in this version"
    )


class StrategyPerformanceLogSchema(BaseModel):
    """Performance run metrics"""

    id: int
    version_number: int
    run_type: str
    metrics: Dict[str, Any]
    notes: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime


class StrategyConfigSchema(BaseModel):
    """Full strategy configuration payload"""

    strategy_type: str
    config: Dict[str, Any]
    model_key: Optional[str] = None
    feature_flags: Dict[str, bool] = Field(default_factory=dict)
    version: int
    history: List[StrategyVersionSchema] = Field(default_factory=list)
    performance: List[StrategyPerformanceLogSchema] = Field(default_factory=list)
    is_default: bool = False


class StrategySaveResponse(BaseModel):
    """Response returned when saving a strategy"""

    success: bool
    message: str
    strategy: StrategyConfigSchema
    version: int


class StrategyListEntry(BaseModel):
    """Entry for strategy list endpoint"""

    strategy_type: str
    has_config: bool
    model_key: Optional[str] = None
    updated_at: Optional[datetime] = None
