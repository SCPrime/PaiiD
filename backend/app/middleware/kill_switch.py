from ..core.kill_switch import is_killed
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

"""
Kill Switch Middleware

Blocks mutating HTTP methods when the global kill switch is active.
"""

class KillSwitchMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            if is_killed():
                return JSONResponse(
                    status_code=423,
                    content={
                        "error": "trading halted",
                        "message": "Kill switch active - mutations are disabled",
                    },
                )
        return await call_next(request)
