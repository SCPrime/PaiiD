"""Orders response schemas"""

from datetime import datetime

from pydantic import BaseModel, Field


class OrderResponse(BaseModel):
    """Order execution response"""

    accepted: bool = Field(..., description="Whether order was accepted")
    dryRun: bool = Field(False, description="Whether this was a dry run")
    duplicate: bool = Field(False, description="Whether request was duplicate")
    orders: list[dict] = Field([], description="List of submitted orders")

    class Config:
        json_schema_extra = {
            "example": {
                "accepted": True,
                "dryRun": False,
                "duplicate": False,
                "orders": [
                    {
                        "symbol": "AAPL",
                        "side": "buy",
                        "qty": 10,
                        "type": "limit",
                        "limit_price": 174.50,
                        "alpaca_order_id": "abc123",
                        "status": "accepted",
                    }
                ],
            }
        }


class OrderTemplateResponse(BaseModel):
    """Order template response"""

    id: int = Field(..., description="Template ID")
    user_id: int | None = Field(None, description="User ID (null for global templates)")
    name: str = Field(..., description="Template name")
    description: str | None = Field(None, description="Template description")
    symbol: str = Field(..., description="Stock symbol")
    side: str = Field(..., description="Order side (buy/sell)")
    quantity: float = Field(..., description="Order quantity")
    order_type: str = Field(..., description="Order type (market/limit/stop)")
    limit_price: float | None = Field(None, description="Limit price")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    last_used_at: datetime | None = Field(None, description="Last used timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": None,
                "name": "Quick Buy AAPL",
                "description": "Buy 10 shares of Apple at limit",
                "symbol": "AAPL",
                "side": "buy",
                "quantity": 10.0,
                "order_type": "limit",
                "limit_price": 174.50,
                "created_at": "2025-10-27T10:00:00Z",
                "updated_at": "2025-10-27T10:00:00Z",
                "last_used_at": None,
            }
        }
