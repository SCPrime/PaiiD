"""Portfolio response schemas"""

from pydantic import BaseModel, Field


class PositionResponse(BaseModel):
    """Single position response"""

    symbol: str = Field(..., description="Stock symbol")
    quantity: float = Field(..., description="Quantity held")
    cost_basis: float = Field(..., description="Cost basis")
    market_value: float = Field(..., description="Current market value")
    unrealized_pl: float = Field(..., description="Unrealized P&L")
    unrealized_plpc: float = Field(..., description="Unrealized P&L percentage")
    change_today: float = Field(0.0, description="Today's price change")

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "AAPL",
                "quantity": 100.0,
                "cost_basis": 15000.0,
                "market_value": 17500.0,
                "unrealized_pl": 2500.0,
                "unrealized_plpc": 16.67,
                "change_today": 1.5,
            }
        }


class PositionsResponse(BaseModel):
    """List of positions response"""

    data: list[PositionResponse] = Field(..., description="List of positions")
    count: int = Field(..., description="Number of positions")
    timestamp: str = Field(..., description="Response timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "data": [
                    {
                        "symbol": "AAPL",
                        "quantity": 100.0,
                        "cost_basis": 15000.0,
                        "market_value": 17500.0,
                        "unrealized_pl": 2500.0,
                        "unrealized_plpc": 16.67,
                        "change_today": 1.5,
                    }
                ],
                "count": 1,
                "timestamp": "2025-10-27T10:30:00Z",
            }
        }


class AccountResponse(BaseModel):
    """Tradier account information response"""

    data: dict = Field(..., description="Account data from Tradier")
    timestamp: str = Field(..., description="Response timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "data": {
                    "account_number": "ABC12345",
                    "total_equity": 100000.0,
                    "total_cash": 50000.0,
                    "option_buying_power": 80000.0,
                },
                "timestamp": "2025-10-27T10:30:00Z",
            }
        }
