"""
Import Verification Tests

Prevents incidents like commit 2e048fe by verifying:
1. All Python packages have __init__.py files
2. Critical imports work correctly
3. No circular dependencies exist

These tests run in CI to catch import issues before deployment.
"""

from pathlib import Path

import pytest


APP_DIR = Path(__file__).resolve().parents[1] / "app"


class TestPackageStructure:
    """Verify Python package structure is valid"""

    def test_middleware_package_has_init(self):
        """Verify middleware package has __init__.py"""
        init_file = APP_DIR / "middleware" / "__init__.py"
        assert init_file.exists(), (
            "app/middleware/__init__.py is REQUIRED for Python to treat "
            "the directory as a package. Without it, imports like "
            "'from .middleware.rate_limit import limiter' will fail."
        )

    def test_services_package_has_init(self):
        """Verify services package has __init__.py"""
        init_file = APP_DIR / "services" / "__init__.py"
        assert init_file.exists(), (
            "app/services/__init__.py is REQUIRED. "
            "Missing this file caused 16+ hours of downtime in Oct 2025."
        )

    def test_routers_package_has_init(self):
        """Verify routers package has __init__.py"""
        init_file = APP_DIR / "routers" / "__init__.py"
        assert init_file.exists(), "app/routers/__init__.py is required for router imports"

    def test_core_package_has_init(self):
        """Verify core package has __init__.py"""
        init_file = APP_DIR / "core" / "__init__.py"
        assert init_file.exists(), "app/core/__init__.py is required for core imports"

    def test_all_app_subdirectories_have_init(self):
        """Verify ALL subdirectories in app/ have __init__.py"""
        app_dir = APP_DIR

        if not app_dir.exists():
            pytest.skip("app directory not found (may be running from different location)")

        missing_init = []
        for subdir in app_dir.iterdir():
            if subdir.is_dir() and not subdir.name.startswith("__"):
                init_file = subdir / "__init__.py"
                if not init_file.exists():
                    missing_init.append(str(subdir))

        assert len(missing_init) == 0, (
            f"The following directories are missing __init__.py files:\n"
            f"{chr(10).join(missing_init)}\n\n"
            f"Every Python package directory must have an __init__.py file."
        )


class TestCriticalImports:
    """Verify critical imports work correctly"""

    def test_middleware_imports(self):
        """Verify middleware imports work"""
        try:
            from app.middleware.cache_control import CacheControlMiddleware
            from app.middleware.rate_limit import custom_rate_limit_exceeded_handler, limiter
            from app.middleware.sentry import SentryContextMiddleware

            # Verify objects exist
            assert limiter is not None
            assert custom_rate_limit_exceeded_handler is not None
            assert CacheControlMiddleware is not None
            assert SentryContextMiddleware is not None
        except ImportError as e:
            pytest.fail(f"Failed to import middleware: {e}")

    def test_services_imports(self):
        """Verify services imports work"""
        try:
            from app.services.cache import init_cache
            from app.services.tradier_stream import start_tradier_stream, stop_tradier_stream

            # Verify functions exist
            assert init_cache is not None
            assert start_tradier_stream is not None
            assert stop_tradier_stream is not None
        except ImportError as e:
            pytest.fail(f"Failed to import services: {e}")

    def test_routers_imports(self):
        """Verify all routers can be imported"""
        try:
            from app.routers import (
                ai,
                claude,
                health,
                market,
                news,
                orders,
                portfolio,
                scheduler,
                strategies,
                stream,
                telemetry,
            )

            # Verify all routers have a router object
            assert hasattr(health, "router")
            assert hasattr(portfolio, "router")
            assert hasattr(orders, "router")
            assert hasattr(market, "router")
        except ImportError as e:
            pytest.fail(f"Failed to import routers: {e}")

    def test_main_app_imports(self):
        """Verify main FastAPI app can be imported"""
        try:
            from app.main import app

            assert app is not None
            assert hasattr(app, "routes")
        except ImportError as e:
            pytest.fail(f"Failed to import main app: {e}")

    def test_config_imports(self):
        """Verify config can be imported"""
        try:
            from app.core.config import settings

            assert settings is not None
        except ImportError as e:
            pytest.fail(f"Failed to import config: {e}")


class TestImportOrdering:
    """Verify imports don't have circular dependencies"""

    def test_middleware_has_no_circular_imports(self):
        """Verify middleware imports don't create circular dependencies"""
        try:
            # Import in the order main.py does
            from app.middleware.cache_control import CacheControlMiddleware
            from app.middleware.rate_limit import limiter
            from app.middleware.sentry import SentryContextMiddleware

            # If we get here, no circular imports
            assert True
        except ImportError as e:
            if "circular import" in str(e).lower():
                pytest.fail(f"Circular import detected in middleware: {e}")
            else:
                pytest.fail(f"Import error in middleware: {e}")

    def test_services_has_no_circular_imports(self):
        """Verify services imports don't create circular dependencies"""
        try:
            from app.services.cache import init_cache
            from app.services.tradier_stream import start_tradier_stream

            assert True
        except ImportError as e:
            if "circular import" in str(e).lower():
                pytest.fail(f"Circular import detected in services: {e}")
            else:
                pytest.fail(f"Import error in services: {e}")


class TestExportLists:
    """Verify __all__ exports are defined correctly"""

    def test_middleware_exports(self):
        """Verify middleware __init__.py exports correct items"""
        from app import middleware

        # Check __all__ is defined
        assert hasattr(middleware, "__all__"), "middleware/__init__.py should define __all__ list"

        # Check expected exports
        expected_exports = [
            "limiter",
            "custom_rate_limit_exceeded_handler",
            "CacheControlMiddleware",
            "SentryContextMiddleware",
        ]

        for export in expected_exports:
            assert export in middleware.__all__, f"'{export}' should be in middleware.__all__"
            assert hasattr(middleware, export), f"middleware.{export} should be importable"

    def test_services_exports(self):
        """Verify services __init__.py exports correct items"""
        from app import services

        # Check __all__ is defined
        assert hasattr(services, "__all__"), "services/__init__.py should define __all__ list"

        # Check expected exports
        expected_exports = ["init_cache", "start_tradier_stream", "stop_tradier_stream"]

        for export in expected_exports:
            assert export in services.__all__, f"'{export}' should be in services.__all__"
            assert hasattr(services, export), f"services.{export} should be importable"


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])
