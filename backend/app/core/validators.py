"""
Shared Input Validation and Sanitization Utilities

Provides common validators and sanitizers for use across all routers.
Ensures consistent input validation and XSS prevention.
"""

import html
import re
from typing import Any

from pydantic import field_validator


class InputSanitizer:
    """Input sanitization utilities"""

    @staticmethod
    def sanitize_text(value: str) -> str:
        """
        Sanitize text input to prevent XSS attacks

        - Strips whitespace
        - HTML escapes special characters
        - Removes null bytes
        """
        if not value:
            return value

        # Remove null bytes
        sanitized = value.replace("\x00", "")

        # Strip whitespace
        sanitized = sanitized.strip()

        # HTML escape to prevent XSS
        sanitized = html.escape(sanitized)

        return sanitized

    @staticmethod
    def normalize_symbol(value: str) -> str:
        """
        Normalize stock symbol

        - Uppercase
        - Strip whitespace
        - Remove invalid characters
        - Max 10 characters
        """
        if not value:
            return value

        # Strip and uppercase
        normalized = value.strip().upper()

        # Remove invalid characters (allow only A-Z, 0-9, $, ., :, -)
        normalized = re.sub(r"[^A-Z0-9$.:^-]", "", normalized)

        # Limit length
        normalized = normalized[:10]

        return normalized

    @staticmethod
    def sanitize_email(value: str) -> str:
        """
        Sanitize email input

        - Strip whitespace
        - Lowercase
        """
        if not value:
            return value

        return value.strip().lower()


class SymbolValidator:
    """Validator for stock symbols"""

    @staticmethod
    def validate_symbol(cls, v: str) -> str:
        """Validate and normalize stock symbol"""
        if not v:
            raise ValueError("Symbol cannot be empty")

        normalized = InputSanitizer.normalize_symbol(v)

        if not normalized:
            raise ValueError("Symbol contains only invalid characters")

        if len(normalized) < 1:
            raise ValueError("Symbol too short (minimum 1 character)")

        return normalized


class NumericValidator:
    """Validator for numeric inputs"""

    @staticmethod
    def validate_positive(cls, v: float | int) -> float | int:
        """Validate that number is positive"""
        if v <= 0:
            raise ValueError("Value must be positive")
        return v

    @staticmethod
    def validate_percentage(cls, v: float) -> float:
        """Validate percentage (0-100)"""
        if not 0 <= v <= 100:
            raise ValueError("Percentage must be between 0 and 100")
        return v

    @staticmethod
    def validate_confidence(cls, v: float) -> float:
        """Validate confidence score (0-1)"""
        if not 0 <= v <= 1:
            raise ValueError("Confidence must be between 0 and 1")
        return v


class TextValidator:
    """Validator for text inputs"""

    @staticmethod
    def validate_and_sanitize(cls, v: str) -> str:
        """Validate and sanitize text input"""
        if not v:
            return v

        # Sanitize
        sanitized = InputSanitizer.sanitize_text(v)

        # Check length
        if len(sanitized) > 10000:
            raise ValueError("Text too long (maximum 10000 characters)")

        return sanitized

    @staticmethod
    def validate_short_text(cls, v: str, max_length: int = 255) -> str:
        """Validate and sanitize short text (e.g., titles, names)"""
        if not v:
            return v

        sanitized = InputSanitizer.sanitize_text(v)

        if len(sanitized) > max_length:
            raise ValueError(f"Text too long (maximum {max_length} characters)")

        return sanitized


# Reusable field validator decorators
def sanitize_text_field(func):
    """Decorator to sanitize text fields"""
    @field_validator("*", mode="before")
    def wrapper(cls, v: Any) -> Any:
        if isinstance(v, str):
            return InputSanitizer.sanitize_text(v)
        return v
    return wrapper


def normalize_symbol_field(func):
    """Decorator to normalize symbol fields"""
    @field_validator("symbol", "symbols", mode="before")
    def wrapper(cls, v: Any) -> Any:
        if isinstance(v, str):
            return InputSanitizer.normalize_symbol(v)
        return v
    return wrapper
