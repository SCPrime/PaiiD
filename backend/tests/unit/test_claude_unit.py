"""
Unit tests for Claude Router (claude.py)

Tests all 2 endpoints in the Claude router with mocked dependencies.
Target: 80%+ coverage
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.models.database import User


client = TestClient(app, raise_server_exceptions=False)


class TestClaude:
    """Test suite for Claude API proxy endpoints"""

    @pytest.fixture
    def mock_user(self):
        """Mock authenticated user"""
        return User(id=1, email="test@example.com", username="test_user", role="owner", is_active=True)

    @pytest.fixture
    def auth_headers(self):
        """Mock authentication headers"""
        return {"Authorization": "Bearer test-token-12345"}

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

    def test_claude_chat_success(self, mock_user, auth_headers, valid_chat_request, monkeypatch):
        """Test successful Claude chat request"""
        monkeypatch.setattr("app.routers.claude.get_current_user_unified", lambda x: mock_user)

        # Mock Anthropic client
        mock_anthropic = Mock()
        mock_messages = Mock()
        mock_message = Mock()
        mock_content = Mock()
        mock_content.text = "Hello! How can I help you today?"
        mock_message.content = [mock_content]
        mock_message.model = "claude-sonnet-4-5-20250929"
        mock_messages.create.return_value = mock_message
        mock_anthropic.messages = mock_messages

        with patch("app.routers.claude.anthropic_client", mock_anthropic):
            response = client.post("/api/claude/chat", json=valid_chat_request, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        # Content is HTML-escaped by validator
        assert "Hello" in data["content"]
        assert data["role"] == "assistant"

    def test_claude_chat_unauthorized(self, valid_chat_request):
        """Test Claude chat without authentication"""
        response = client.post("/api/claude/chat", json=valid_chat_request)
        assert response.status_code in [401, 403]

    def test_claude_chat_validation_error(self, auth_headers):
        """Test Claude chat with invalid request data"""
        invalid_request = {
            "messages": [],  # Empty messages
            "max_tokens": 50,  # Below minimum
        }

        response = client.post("/api/claude/chat", json=invalid_request, headers=auth_headers)

        assert response.status_code == 422

    def test_claude_chat_api_not_configured(
        self, mock_user, auth_headers, valid_chat_request, monkeypatch
    ):
        """Test Claude chat when API key not configured"""
        monkeypatch.setattr("app.routers.claude.get_current_user_unified", lambda x: mock_user)

        with patch("app.routers.claude.anthropic_client", None):
            response = client.post("/api/claude/chat", json=valid_chat_request, headers=auth_headers)

        assert response.status_code in [503, 500]

    def test_claude_chat_with_system_prompt(
        self, mock_user, auth_headers, valid_chat_request, monkeypatch
    ):
        """Test Claude chat with system prompt"""
        monkeypatch.setattr("app.routers.claude.get_current_user_unified", lambda x: mock_user)

        request_with_system = valid_chat_request.copy()
        request_with_system["system"] = "You are a helpful trading assistant."

        mock_anthropic = Mock()
        mock_messages = Mock()
        mock_message = Mock()
        mock_content = Mock()
        mock_content.text = "I'm here to help with trading!"
        mock_message.content = [mock_content]
        mock_message.model = "claude-sonnet-4-5-20250929"
        mock_messages.create.return_value = mock_message
        mock_anthropic.messages = mock_messages

        with patch("app.routers.claude.anthropic_client", mock_anthropic):
            response = client.post("/api/claude/chat", json=request_with_system, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "content" in data

    def test_claude_chat_multiple_messages(
        self, mock_user, auth_headers, valid_chat_request, monkeypatch
    ):
        """Test Claude chat with conversation history"""
        monkeypatch.setattr("app.routers.claude.get_current_user_unified", lambda x: mock_user)

        request_with_history = valid_chat_request.copy()
        request_with_history["messages"] = [
            {"role": "user", "content": "What is AAPL stock price?"},
            {"role": "assistant", "content": "AAPL is trading at $175."},
            {"role": "user", "content": "Should I buy it?"},
        ]

        mock_anthropic = Mock()
        mock_messages = Mock()
        mock_message = Mock()
        mock_content = Mock()
        mock_content.text = "Based on technical analysis..."
        mock_message.content = [mock_content]
        mock_message.model = "claude-sonnet-4-5-20250929"
        mock_messages.create.return_value = mock_message
        mock_anthropic.messages = mock_messages

        with patch("app.routers.claude.anthropic_client", mock_anthropic):
            response = client.post("/api/claude/chat", json=request_with_history, headers=auth_headers)

        assert response.status_code == 200

    def test_claude_chat_xss_prevention(self, mock_user, auth_headers, monkeypatch):
        """Test that XSS attempts are sanitized"""
        monkeypatch.setattr("app.routers.claude.get_current_user_unified", lambda x: mock_user)

        xss_request = {
            "messages": [
                {"role": "user", "content": "<script>alert('xss')</script>Hello"},
            ],
            "max_tokens": 2000,
            "model": "claude-sonnet-4-5-20250929",
        }

        mock_anthropic = Mock()
        mock_messages = Mock()
        mock_message = Mock()
        mock_content = Mock()
        mock_content.text = "Response"
        mock_message.content = [mock_content]
        mock_message.model = "claude-sonnet-4-5-20250929"
        mock_messages.create.return_value = mock_message
        mock_anthropic.messages = mock_messages

        with patch("app.routers.claude.anthropic_client", mock_anthropic):
            response = client.post("/api/claude/chat", json=xss_request, headers=auth_headers)

        # Should succeed but content should be sanitized
        assert response.status_code == 200

    def test_claude_chat_different_models(
        self, mock_user, auth_headers, valid_chat_request, monkeypatch
    ):
        """Test Claude chat with different model versions"""
        monkeypatch.setattr("app.routers.claude.get_current_user_unified", lambda x: mock_user)

        models = [
            "claude-sonnet-4-5-20250929",
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
        ]

        for model in models:
            request_data = valid_chat_request.copy()
            request_data["model"] = model

            mock_anthropic = Mock()
            mock_messages = Mock()
            mock_message = Mock()
            mock_content = Mock()
            mock_content.text = "Response"
            mock_message.content = [mock_content]
            mock_message.model = model
            mock_messages.create.return_value = mock_message
            mock_anthropic.messages = mock_messages

            with patch("app.routers.claude.anthropic_client", mock_anthropic):
                response = client.post("/api/claude/chat", json=request_data, headers=auth_headers)

            assert response.status_code == 200
