#!/usr/bin/env python3
"""
Automated Import Validation
Tests all critical imports work before deployment
Run this to catch ModuleNotFoundError and AttributeError issues early
"""

import sys
import traceback


def test_imports():
    """Test all critical imports"""
    tests = [
        ("Main app", "from app.main import app"),
        ("Core config", "from app.core.config import settings"),
        ("WebSocket router", "from routers.websocket import router"),
        ("WebSocket service", "from services.websocket_service import WebSocketService"),
        ("Market data service", "from services.market_data_service import MarketDataService"),
        ("AI service", "from services.ai_service import AIService"),
        ("Sentiment analyzer", "from services.sentiment_analyzer import SentimentAnalyzer"),
        ("Rate limiter", "from middleware.rate_limiter import RateLimiter"),
        ("DB optimizer", "from optimization.database_optimizer import DatabaseOptimizer"),
        ("Cache service", "from app.services.cache import CacheService"),
    ]

    passed = 0
    failed = 0
    errors = []

    print("=" * 70)
    print("🧪 AUTOMATED IMPORT VALIDATION")
    print("=" * 70)
    print()

    for name, import_stmt in tests:
        try:
            exec(import_stmt)
            print(f"✅ {name}")
            passed += 1
        except Exception as e:
            print(f"❌ {name}")
            print(f"   Error: {e}")
            errors.append((name, e, traceback.format_exc()))
            failed += 1

    print()
    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70)

    if failed > 0:
        print()
        print("🚨 DETAILED ERRORS:")
        print()
        for name, error, tb in errors:
            print(f"❌ {name}:")
            print(tb)
            print()

        print("=" * 70)
        print("🚨 IMPORT VALIDATION FAILED!")
        print("=" * 70)
        sys.exit(1)
    else:
        print()
        print("✅ ALL IMPORTS VALID - SAFE TO DEPLOY!")
        print()
        sys.exit(0)


if __name__ == "__main__":
    test_imports()
