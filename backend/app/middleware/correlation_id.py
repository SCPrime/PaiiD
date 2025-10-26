"""
Request Correlation ID Middleware
==================================

Automatically adds correlation IDs to all requests for log tracing

Every request gets a unique ID that can be traced through logs:
- Auto-generated UUID for each request
- Uses X-Request-ID header if provided
- Sets correlation ID in logging context
"""

import logging
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..core.logging_utils import set_correlation_id


logger = logging.getLogger(__name__)


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add correlation ID to all requests

    Adds X-Request-ID header to response and sets correlation ID in logging context
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and add correlation ID

        Args:
            request: FastAPI request
            call_next: Next middleware/route handler

        Returns:
            Response with X-Request-ID header
        """
        # Get or generate correlation ID
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = str(uuid.uuid4())

        # Set in logging context
        set_correlation_id(request_id)

        # Log request (without sensitive headers)
        safe_headers = {}
        for key, value in request.headers.items():
            if key.lower() in {"authorization", "cookie", "x-api-key"}:
                safe_headers[key] = "***"
            else:
                safe_headers[key] = value

        logger.debug(
            f"[{request_id}] {request.method} {request.url.path} | "
            f"headers={safe_headers}"
        )

        # Process request
        try:
            response = await call_next(request)

            # Add correlation ID to response headers
            response.headers["X-Request-ID"] = request_id

            logger.debug(
                f"[{request_id}] Response: status={response.status_code}"
            )

            return response

        except Exception as e:
            logger.error(
                f"[{request_id}] Request failed: {type(e).__name__}: {str(e)}"
            )
            raise
