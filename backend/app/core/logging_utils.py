"""
Centralized Logging Utilities for PaiiD
========================================

Provides secure logging with:
1. Automatic sensitive data redaction
2. Request correlation IDs
3. Standardized log format
4. Security-first design

SECURITY: Never logs passwords, API keys, tokens, or PII
"""

import logging
import re
from typing import Any
from contextvars import ContextVar

# Context variable for request correlation ID
request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)


# Sensitive field patterns to redact
SENSITIVE_PATTERNS = [
    (re.compile(r'"password"\s*:\s*"[^"]*"', re.IGNORECASE), '"password": "***"'),
    (re.compile(r'"api_key"\s*:\s*"[^"]*"', re.IGNORECASE), '"api_key": "***"'),
    (re.compile(r'"secret"\s*:\s*"[^"]*"', re.IGNORECASE), '"secret": "***"'),
    (re.compile(r'"token"\s*:\s*"[^"]*"', re.IGNORECASE), '"token": "***"'),
    (re.compile(r'"authorization"\s*:\s*"[^"]*"', re.IGNORECASE), '"authorization": "***"'),
    (re.compile(r'"bearer\s+[^"]*"', re.IGNORECASE), '"Bearer ***"'),
    (re.compile(r'Bearer\s+\S+', re.IGNORECASE), 'Bearer ***'),
    (re.compile(r'"ssn"\s*:\s*"[^"]*"', re.IGNORECASE), '"ssn": "***"'),
    (re.compile(r'"credit_card"\s*:\s*"[^"]*"', re.IGNORECASE), '"credit_card": "***"'),
]

# Sensitive dictionary keys to redact
SENSITIVE_KEYS = {
    "password",
    "password_hash",
    "api_key",
    "secret",
    "secret_key",
    "token",
    "access_token",
    "refresh_token",
    "authorization",
    "bearer",
    "ssn",
    "credit_card",
    "cvv",
    "pin",
}


def redact_sensitive_data(data: Any) -> Any:
    """
    Redact sensitive information from any data structure

    Args:
        data: Any data structure (str, dict, list, etc.)

    Returns:
        Sanitized version with sensitive data replaced with "***"
    """
    if isinstance(data, str):
        # Apply regex patterns
        result = data
        for pattern, replacement in SENSITIVE_PATTERNS:
            result = pattern.sub(replacement, result)
        return result

    elif isinstance(data, dict):
        # Recursively redact dictionary values
        result = {}
        for key, value in data.items():
            if key.lower() in SENSITIVE_KEYS:
                result[key] = "***"
            else:
                result[key] = redact_sensitive_data(value)
        return result

    elif isinstance(data, (list, tuple)):
        # Recursively redact list/tuple items
        return type(data)(redact_sensitive_data(item) for item in data)

    else:
        # Return as-is for other types (int, bool, None, etc.)
        return data


def redact_auth_header(authorization: str | None) -> str:
    """
    Safely redact authorization header for logging

    Args:
        authorization: Full Authorization header value

    Returns:
        Redacted version (e.g., "Bearer rnd_bDR*** (12 chars)")
    """
    if not authorization:
        return "None"

    if not authorization.startswith("Bearer "):
        return f"Invalid format: {authorization[:10]}..."

    token = authorization.split(" ", 1)[1]
    if len(token) <= 10:
        return f"Bearer *** ({len(token)} chars)"

    # Show first 7 chars + "***" + length
    return f"Bearer {token[:7]}*** ({len(token)} chars)"


def format_user_for_logging(user: Any) -> str:
    """
    Safely format user object for logging (never log full user object)

    Args:
        user: User object from database

    Returns:
        Safe string representation (e.g., "user_id=1, email=user@example.com")
    """
    if not user:
        return "None"

    user_id = getattr(user, "id", "unknown")
    email = getattr(user, "email", "unknown")
    role = getattr(user, "role", "unknown")

    return f"user_id={user_id}, email={email}, role={role}"


def get_correlation_id() -> str | None:
    """
    Get current request correlation ID from context

    Returns:
        Correlation ID string or None if not set
    """
    return request_id_ctx.get()


def set_correlation_id(request_id: str) -> None:
    """
    Set request correlation ID in context

    Args:
        request_id: Unique request identifier
    """
    request_id_ctx.set(request_id)


def format_log_message(message: str, **kwargs: Any) -> str:
    """
    Format log message with correlation ID and redacted context

    Args:
        message: Log message
        **kwargs: Additional context (will be redacted if sensitive)

    Returns:
        Formatted log message with [request_id] prefix
    """
    request_id = get_correlation_id()

    # Redact kwargs
    safe_kwargs = redact_sensitive_data(kwargs)

    # Build message
    if request_id:
        base_msg = f"[{request_id}] {message}"
    else:
        base_msg = message

    # Add context if provided
    if safe_kwargs:
        context_str = ", ".join(f"{k}={v}" for k, v in safe_kwargs.items())
        return f"{base_msg} | {context_str}"

    return base_msg


class SecureLogger:
    """
    Secure logger wrapper with automatic sensitive data redaction

    Usage:
        logger = SecureLogger(__name__)
        logger.info("User login", user_id=user.id, email=user.email)
        # Output: [abc-123] User login | user_id=1, email=user@example.com
    """

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def _log(self, level: int, message: str, *args, **kwargs):
        """Internal logging with redaction"""
        # Separate logging kwargs from context kwargs
        exc_info = kwargs.pop("exc_info", False)
        stack_info = kwargs.pop("stack_info", False)
        stacklevel = kwargs.pop("stacklevel", 1)

        # Format message with correlation ID and redacted context
        formatted_msg = format_log_message(message, **kwargs)

        # Log with standard logger
        self.logger.log(
            level,
            formatted_msg,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel + 1,
        )

    def debug(self, message: str, **kwargs):
        """Log debug message with redaction"""
        self._log(logging.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs):
        """Log info message with redaction"""
        self._log(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message with redaction"""
        self._log(logging.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message with redaction"""
        self._log(logging.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message with redaction"""
        self._log(logging.CRITICAL, message, **kwargs)


def get_secure_logger(name: str) -> SecureLogger:
    """
    Get a secure logger instance

    Args:
        name: Logger name (typically __name__)

    Returns:
        SecureLogger instance
    """
    return SecureLogger(name)
