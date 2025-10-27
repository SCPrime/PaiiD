"""
Contract test configuration and shared fixtures
"""

import pytest
from httpx import AsyncClient

from app.main import app


@pytest.fixture
def auth_headers():
    """Authentication headers for contract tests"""
    return {"Authorization": "Bearer rnd_bDRqi1TvLvd3rC78yvUSgDraH2Kl"}


@pytest.fixture
async def client():
    """Async HTTP client for API testing"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def base_url():
    """Base URL for contract tests"""
    return "http://127.0.0.1:8001"
