"""
Middleware to track request metrics
"""
import time

from fastapi import Request

from app.services.health_monitor import health_monitor


async def metrics_middleware(request: Request, call_next):
    """Track request metrics"""
    start_time = time.time()

    try:
        response = await call_next(request)
        response_time = time.time() - start_time

        # Record metrics
        is_error = response.status_code >= 400
        health_monitor.record_request(response_time, is_error)

        # Add metrics headers
        response.headers["X-Response-Time"] = f"{response_time:.3f}s"

        return response

    except Exception:
        response_time = time.time() - start_time
        health_monitor.record_request(response_time, is_error=True)
        raise
