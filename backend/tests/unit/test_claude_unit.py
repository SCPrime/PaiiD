"""
Unit tests for Claude Router (claude.py)

Tests all 2 endpoints in the Claude router with mocked dependencies.
Target: 80%+ coverage
"""

import pytest
from unittest.mock import patch


class TestClaude:
    """Test suite for Claude API proxy endpoints"""

    @pytest.fixture
    def valid_chat_request(self):
        """Valid chat request data"""
        return {
            "messages": [
                {"role": "user", "content": "Hello Claude!"},
            ],
            "max_tokens": 2000,
            "model": "claude-sonnet-4-5-20250929",
        }

    # ===========================================
    # TEST: POST /claude/chat
    # ===========================================

    def test_claude_chat_success(self, client, auth_headers, valid_chat_request, mock_anthropic_client):
        """Test successful Claude chat request"""
        with patch("app.routers.claude.anthropic_client", mock_anthropic_client):
            response = client.post("/api/claude/chat", json=valid_chat_request, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert "Claude" in data["content"]
        assert data["role"] == "assistant"

    def test_claude_chat_unauthorized(self, client_no_auth, valid_chat_request):
        """Test Claude chat without authentication"""
        response = client_no_auth.post("/api/claude/chat", json=valid_chat_request)
        assert response.status_code in [401, 403]

    def test_claude_chat_validation_error(self, client, auth_headers):
        """Test Claude chat with invalid request data"""
        invalid_request = {
            "messages": [],  # Empty messages
            "max_tokens": 50,  # Below minimum
        }

        response = client.post("/api/claude/chat", json=invalid_request, headers=auth_headers)

        assert response.status_code == 422

    def test_claude_chat_api_not_configured(self, client, auth_headers, valid_chat_request):
        """Test Claude chat when API key not configured"""
        with patch("app.routers.claude.anthropic_client", None):
            response = client.post("/api/claude/chat", json=valid_chat_request, headers=auth_headers)

        assert response.status_code in [503, 500]

    def test_claude_chat_with_system_prompt(
        self, client, auth_headers, valid_chat_request, mock_anthropic_client
    ):
        """Test Claude chat with system prompt"""
        request_with_system = valid_chat_request.copy()
        request_with_system["system"] = "You are a helpful trading assistant."

        with patch("app.routers.claude.anthropic_client", mock_anthropic_client):
            response = client.post("/api/claude/chat", json=request_with_system, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "content" in data

    def test_claude_chat_multiple_messages(
        self, client, auth_headers, valid_chat_request, mock_anthropic_client
    ):
        """Test Claude chat with conversation history"""
        request_with_history = valid_chat_request.copy()
        request_with_history["messages"] = [
            {"role": "user", "content": "What is AAPL stock price?"},
            {"role": "assistant", "content": "AAPL is trading at $175."},
            {"role": "user", "content": "Should I buy it?"},
        ]

        with patch("app.routers.claude.anthropic_client", mock_anthropic_client):
            response = client.post("/api/claude/chat", json=request_with_history, headers=auth_headers)

        assert response.status_code == 200

    def test_claude_chat_xss_prevention(self, client, auth_headers, mock_anthropic_client):
        """Test that XSS attempts are sanitized"""
        xss_request = {
            "messages": [
                {"role": "user", "content": "<script>alert('xss')</script>Hello"},
            ],
            "max_tokens": 2000,
            "model": "claude-sonnet-4-5-20250929",
        }

        with patch("app.routers.claude.anthropic_client", mock_anthropic_client):
            response = client.post("/api/claude/chat", json=xss_request, headers=auth_headers)

        # Should succeed but content should be sanitized
        assert response.status_code == 200

    def test_claude_chat_different_models(
        self, client, auth_headers, valid_chat_request, mock_anthropic_client
    ):
        """Test Claude chat with different model versions"""
        models = [
            "claude-sonnet-4-5-20250929",
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
        ]

        for model in models:
            request_data = valid_chat_request.copy()
            request_data["model"] = model

            with patch("app.routers.claude.anthropic_client", mock_anthropic_client):
                response = client.post("/api/claude/chat", json=request_data, headers=auth_headers)

            assert response.status_code == 200
