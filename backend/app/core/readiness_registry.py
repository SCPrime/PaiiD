"""
Readiness Registry - Feature Availability Management

Provides centralized registry for optional service availability.
Prevents import-time failures when services are unavailable.

PATTERN: Services register themselves at initialization time.
If registration fails, service is marked as unavailable and endpoints
gracefully degrade instead of crashing.

Example:
    from app.core.readiness_registry import get_readiness_registry

    registry = get_readiness_registry()

    try:
        news_service = NewsAggregator()
        registry.register("news", available=True)
    except Exception as e:
        registry.register("news", available=False, reason=str(e))

    # In endpoint:
    if not registry.is_available("news"):
        raise HTTPException(503, "News service unavailable")
"""

from typing import Dict, Optional


class ReadinessRegistry:
    """
    Centralized registry for optional service availability

    Tracks which services are available and why they might be unavailable.
    Used by endpoints to gracefully degrade when dependencies are missing.
    """

    def __init__(self):
        self._services: Dict[str, dict] = {}

    def register(self, service_name: str, available: bool, reason: Optional[str] = None):
        """
        Register a service's availability status

        Args:
            service_name: Unique identifier for the service
            available: Whether the service is available
            reason: Optional reason why service is unavailable
        """
        self._services[service_name] = {
            "available": available,
            "reason": reason
        }

    def is_available(self, service_name: str) -> bool:
        """
        Check if a service is available

        Args:
            service_name: Service to check

        Returns:
            True if service is registered and available, False otherwise
        """
        service = self._services.get(service_name)
        if service is None:
            # Service not registered - assume unavailable
            return False
        return service["available"]

    def get_reason(self, service_name: str) -> Optional[str]:
        """
        Get the reason why a service is unavailable

        Args:
            service_name: Service to check

        Returns:
            Reason string if service is unavailable, None otherwise
        """
        service = self._services.get(service_name)
        if service is None:
            return "Service not registered"
        return service.get("reason")

    def get_all_services(self) -> Dict[str, dict]:
        """
        Get all registered services and their status

        Returns:
            Dictionary mapping service names to their status
        """
        return self._services.copy()


# Singleton instance
_readiness_registry: Optional[ReadinessRegistry] = None


def get_readiness_registry() -> ReadinessRegistry:
    """
    Get the singleton readiness registry instance

    Returns:
        The global ReadinessRegistry instance
    """
    global _readiness_registry
    if _readiness_registry is None:
        _readiness_registry = ReadinessRegistry()
    return _readiness_registry
