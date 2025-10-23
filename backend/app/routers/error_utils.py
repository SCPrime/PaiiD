"""Shared utilities for consistent router error handling."""

from __future__ import annotations

import inspect
import logging
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any, TypeVar, cast

from fastapi import HTTPException


ReturnType = TypeVar("ReturnType")


def log_and_sanitize_exceptions(
    logger: logging.Logger,
    *,
    public_message: str,
    log_message: str | None = None,
    status_code: int = 500,
) -> Callable[[Callable[..., Awaitable[ReturnType] | ReturnType]], Callable[..., Awaitable[ReturnType] | ReturnType]]:
    """Wrap a path operation to provide consistent logging and sanitized errors."""

    def decorator(
        func: Callable[..., Awaitable[ReturnType] | ReturnType]
    ) -> Callable[..., Awaitable[ReturnType] | ReturnType]:
        if inspect.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> ReturnType:
                try:
                    result = func(*args, **kwargs)
                    return await cast(Awaitable[ReturnType], result)
                except HTTPException:
                    raise
                except Exception as exc:
                    logger.error(
                        "%s: %s",
                        log_message or public_message,
                        exc,
                        exc_info=True,
                    )
                    raise HTTPException(status_code=status_code, detail=public_message) from exc

            return async_wrapper

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> ReturnType:
            try:
                return cast(ReturnType, func(*args, **kwargs))
            except HTTPException:
                raise
            except Exception as exc:
                logger.error(
                    "%s: %s",
                    log_message or public_message,
                    exc,
                    exc_info=True,
                )
                raise HTTPException(status_code=status_code, detail=public_message) from exc

        return sync_wrapper

    return decorator

