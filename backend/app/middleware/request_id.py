from collections.abc import Callable
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import uuid

"""
Request ID Middleware

Assigns and propagates a request correlation ID for tracing across logs.
Uses X-Request-ID header if provided; otherwise generates a UUID4.
"""

class RequestIDMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, header_name: str = "X-Request-ID"):
        super().__init__(app)
        self.header_name = header_name

    async def dispatch(self, request: Request, call_next: Callable):
        request_id = request.headers.get(self.header_name) or str(uuid.uuid4())
        # Attach to request.state for handlers/logging
        request.state.request_id = request_id
        response = await call_next(request)
        # Return header to client
        response.headers[self.header_name] = request_id
        return response
