"""Health check response schemas"""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Basic health check response"""

    status: str = Field(..., description="Health status (ok/error)")
    time: str = Field(..., description="Current timestamp")

    class Config:
        json_schema_extra = {
            "example": {"status": "ok", "time": "2025-10-27T15:30:00.123456"}
        }


class DetailedHealthResponse(BaseModel):
    """Detailed health metrics response"""

    status: str = Field(..., description="Overall status (healthy/degraded/unhealthy)")
    timestamp: str = Field(..., description="Health check timestamp")
    components: dict = Field(..., description="Component health status")
    metrics: dict | None = Field(None, description="System metrics")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2025-10-27T15:30:00Z",
                "components": {
                    "database": {"status": "up"},
                    "redis": {"status": "up"},
                    "streaming": {"status": "up", "active_symbols": 2},
                },
                "metrics": {
                    "cpu_percent": 25.5,
                    "memory_percent": 45.2,
                    "disk_percent": 60.0,
                },
            }
        }
