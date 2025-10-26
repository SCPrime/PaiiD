# Services package - Central Service Registry

# Legacy services (existing)
from .cache import init_cache

# NEW Wave 4 Services - Service Extraction Layer
from .cache_service import CacheService, get_cache_service, init_cache_service
from .market_analysis_service import (
    MarketAnalysisService,
    get_market_analysis_service,
)
from .notification_service import (
    Notification,
    NotificationPreferences,
    NotificationPriority,
    NotificationService,
    NotificationType,
    get_notification_service,
)
from .portfolio_analytics_service import (
    PortfolioAnalyticsService,
    get_portfolio_analytics_service,
)
from .tradier_stream import start_tradier_stream, stop_tradier_stream


# Service Registry - Singleton Instances
# Use these getter functions for dependency injection in routers
_services_initialized = False


def init_all_services():
    """
    Initialize all services on application startup.

    This should be called in main.py during app startup.
    Ensures all singletons are created and ready.

    Example:
        from app.services import init_all_services

        @app.on_event("startup")
        async def startup():
            init_all_services()
    """
    global _services_initialized

    if _services_initialized:
        return

    # Initialize legacy cache
    init_cache()

    # Initialize new cache service
    init_cache_service()

    # Initialize other services (lazy-loaded on first use)
    get_market_analysis_service()
    get_portfolio_analytics_service()
    get_notification_service()

    _services_initialized = True
    print("[OK] All services initialized", flush=True)


# Service Dependency Injection Helpers
def get_all_services() -> dict[str, object]:
    """
    Get all service instances (for dependency injection).

    Returns:
        Dictionary mapping service names to instances

    Example:
        services = get_all_services()
        market_service = services["market_analysis"]
    """
    return {
        "cache": get_cache_service(),
        "market_analysis": get_market_analysis_service(),
        "portfolio_analytics": get_portfolio_analytics_service(),
        "notification": get_notification_service(),
    }


__all__ = [
    # Legacy exports
    "init_cache",
    "start_tradier_stream",
    "stop_tradier_stream",
    # New service classes
    "CacheService",
    "MarketAnalysisService",
    "PortfolioAnalyticsService",
    "NotificationService",
    "Notification",
    "NotificationPreferences",
    "NotificationType",
    "NotificationPriority",
    # Service getters (dependency injection)
    "get_cache_service",
    "get_market_analysis_service",
    "get_portfolio_analytics_service",
    "get_notification_service",
    # Initialization
    "init_cache_service",
    "init_all_services",
    "get_all_services",
]
