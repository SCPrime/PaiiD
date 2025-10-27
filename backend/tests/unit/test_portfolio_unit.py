"""
Unit tests for Portfolio Router (portfolio.py)

Tests all 3 endpoints in the portfolio router with mocked dependencies.
Target: 80%+ coverage
"""

import pytest
from unittest.mock import Mock


class TestPortfolio:
    """Test suite for portfolio endpoints"""

    def test_get_account_success(self, client, auth_headers):
        """Test successful account retrieval"""
        response = client.get("/api/account", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "data" in data

    def test_get_account_unauthorized(self, client_no_auth):
        """Test account retrieval without authentication"""
        response = client_no_auth.get("/api/account")
        assert response.status_code in [401, 403]

    def test_get_positions_success(self, client, auth_headers):
        """Test successful positions retrieval"""
        response = client.get("/api/positions", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["symbol"] == "AAPL"

    def test_get_position_by_symbol_success(self, client, auth_headers):
        """Test successful position retrieval by symbol"""
        response = client.get("/api/positions/AAPL", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "AAPL"
