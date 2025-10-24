"""Pydantic schemas for options endpoints."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, validator

StrategyKey = Literal[
    "iron_condor",
    "butterfly",
    "vertical_call",
    "vertical_put",
    "straddle",
    "strangle",
    "custom",
]


class OptionGreeks(BaseModel):
    """Normalized greek payload."""

    delta: Optional[float] = Field(default=None, description="Price sensitivity to the underlying")
    gamma: Optional[float] = Field(default=None, description="Rate of change of delta")
    theta: Optional[float] = Field(default=None, description="Time decay (per day)")
    vega: Optional[float] = Field(default=None, description="Sensitivity to 1% volatility change")
    rho: Optional[float] = Field(default=None, description="Sensitivity to rate changes")

    class Config:
        json_encoders = {
            float: lambda v: None if v is None else float(round(v, 6)),
        }


class OptionContract(BaseModel):
    """Single option contract quote with analytics."""

    symbol: str = Field(..., description="Occ option symbol (OCC format)")
    underlying_symbol: str = Field(..., description="Underlying equity symbol")
    option_type: Literal["call", "put"]
    strike_price: float = Field(..., gt=0)
    expiration_date: date
    bid: Optional[float] = Field(default=None, ge=0)
    ask: Optional[float] = Field(default=None, ge=0)
    last_price: Optional[float] = Field(default=None, ge=0)
    mark_price: Optional[float] = Field(default=None, ge=0, description="Midpoint between bid/ask")
    volume: Optional[int] = Field(default=None, ge=0)
    open_interest: Optional[int] = Field(default=None, ge=0)
    implied_volatility: Optional[float] = Field(default=None, ge=0)
    greeks: OptionGreeks = Field(default_factory=OptionGreeks)
    days_to_expiration: int = Field(..., ge=0)
    updated_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat() if v else None,
        }


class OptionChainResponse(BaseModel):
    """Options chain response for a symbol/expiration."""

    symbol: str
    expiration_date: date
    underlying_price: Optional[float] = None
    calls: List[OptionContract]
    puts: List[OptionContract]
    total_contracts: int
    fetched_at: datetime

    class Config:
        json_encoders = {
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat(),
        }


class OptionExpiration(BaseModel):
    """Available expiration with computed DTE."""

    date: date
    days_to_expiry: int

    class Config:
        json_encoders = {
            date: lambda v: v.isoformat(),
        }


class GreeksRequest(BaseModel):
    """Parameters for ad-hoc greeks calculation."""

    option_type: Literal["call", "put"]
    underlying_price: float = Field(..., gt=0)
    strike_price: float = Field(..., gt=0)
    expiration: date
    price: Optional[float] = Field(default=None, gt=0)
    implied_volatility: Optional[float] = Field(default=None, gt=0)
    risk_free_rate: Optional[float] = Field(default=None)

    @validator("risk_free_rate", pre=True, always=True)
    def _default_rate(cls, value: Optional[float]) -> Optional[float]:
        return value


class GreeksResponse(OptionGreeks):
    """Greeks payload augmented with implied volatility."""

    implied_volatility: Optional[float] = Field(default=None, ge=0)


class OptionLegCreate(BaseModel):
    """Incoming request payload for a single leg."""

    action: Literal["BUY", "SELL"]
    option_type: Literal["call", "put"]
    strike: float = Field(..., gt=0)
    expiration: date
    quantity: int = Field(..., gt=0)
    price: Optional[float] = Field(default=None, gt=0)
    underlying_price: Optional[float] = Field(default=None, gt=0)
    implied_volatility: Optional[float] = Field(default=None, gt=0)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_encoders = {
            date: lambda v: v.isoformat(),
        }


class OptionLegResponse(OptionLegCreate):
    """Persisted leg response."""

    id: int
    contract_symbol: str
    order_id: Optional[int] = None
    delta: Optional[float] = None
    gamma: Optional[float] = None
    theta: Optional[float] = None
    vega: Optional[float] = None
    rho: Optional[float] = None


class MultiLegOrderCreate(BaseModel):
    """Payload for multi-leg order persistence."""

    symbol: str = Field(..., min_length=1, max_length=20)
    strategy: StrategyKey = Field(default="custom")
    order_type: Optional[Literal["debit", "credit", "even"]] = None
    net_price: Optional[float] = None
    underlying_price: Optional[float] = Field(default=None, gt=0)
    legs: List[OptionLegCreate] = Field(..., min_items=1)
    notes: Optional[str] = Field(default=None, max_length=500)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    submit: bool = Field(default=False)

    @validator("legs")
    def _require_multiple_legs(cls, value: List[OptionLegCreate]) -> List[OptionLegCreate]:
        if len(value) < 2:
            raise ValueError("Multi-leg orders require at least two legs")
        return value


class MultiLegOrderResponse(BaseModel):
    """Response for persisted multi-leg order."""

    id: int
    symbol: str
    strategy: StrategyKey
    order_type: Literal["debit", "credit", "even"]
    net_price: float
    underlying_price: Optional[float]
    status: str
    notes: Optional[str]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    legs: List[OptionLegResponse]
    order_submission: List[Dict[str, Any]]

    class Config:
        json_encoders = {
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat(),
        }
