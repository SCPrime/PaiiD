"""Unit tests for Interface Predictor - ARMANI Squad.

Tests interface prediction at intersection points using AST analysis.
"""

import pytest
from unittest.mock import patch
from modsquad.extensions import interface_predictor


@pytest.fixture
def sample_intersection():
    """Sample intersection point."""
    return {
        "type": "function_handoff",
        "source_batch": "batch_0",
        "target_batch": "batch_1",
        "location": "backend/app/utils.py",
    }


@pytest.fixture
def sample_batch_output():
    """Sample batch output with Python code."""
    return {
        "files": {
            "backend/app/utils.py": {
                "content": """
def calculate_total(items: list[dict]) -> float:
    '''Calculate total price.'''
    return sum(item['price'] for item in items)

class PriceCalculator:
    def __init__(self, tax_rate: float):
        self.tax_rate = tax_rate

    def calculate(self, amount: float) -> float:
        return amount * (1 + self.tax_rate)
"""
            }
        }
    }


@pytest.fixture
def mock_config_enabled():
    """Mock configuration."""
    return {"interface_predictor": {"enabled": True}}


class TestPredict:
    """Test the main predict() function."""

    @patch("modsquad.extensions.interface_predictor.load_extension_config")
    def test_predict_success(
        self, mock_config, sample_intersection, sample_batch_output, mock_config_enabled
    ):
        """Test successful interface prediction."""
        mock_config.return_value = mock_config_enabled

        result = interface_predictor.predict(sample_intersection, sample_batch_output)

        assert "predicted_functions" in result
        assert "predicted_classes" in result
        assert "type_hints" in result

    @patch("modsquad.extensions.interface_predictor.load_extension_config")
    def test_predict_disabled(self, mock_config, sample_intersection, sample_batch_output):
        """Test disabled returns status."""
        mock_config.return_value = {"interface_predictor": {"enabled": False}}

        result = interface_predictor.predict(sample_intersection, sample_batch_output)

        assert result["status"] == "disabled"


class TestEdgeCases:
    """Test edge cases."""

    @patch("modsquad.extensions.interface_predictor.load_extension_config")
    def test_predict_empty_output(
        self, mock_config, sample_intersection, mock_config_enabled
    ):
        """Test with empty batch output."""
        mock_config.return_value = mock_config_enabled
        batch_output = {"files": {}}

        result = interface_predictor.predict(sample_intersection, batch_output)

        assert "predicted_functions" in result

    @patch("modsquad.extensions.interface_predictor.load_extension_config")
    def test_predict_invalid_syntax(
        self, mock_config, sample_intersection, mock_config_enabled
    ):
        """Test handling of invalid Python syntax."""
        mock_config.return_value = mock_config_enabled
        batch_output = {
            "files": {
                "file.py": {
                    "content": "invalid python syntax @#$%"
                }
            }
        }

        result = interface_predictor.predict(sample_intersection, batch_output)

        # Should fall back to regex extraction
        assert result["confidence"] == "medium"
