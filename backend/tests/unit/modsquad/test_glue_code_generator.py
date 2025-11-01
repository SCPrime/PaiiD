"""Unit tests for Glue Code Generator - ARMANI Squad.

Tests glue code generation for intersection points.
"""

import pytest
from unittest.mock import patch
from modsquad.extensions import glue_code_generator
from modsquad.extensions.glue_code_generator import GlueCode


@pytest.fixture
def sample_intersection():
    """Sample intersection."""
    return {
        "type": "function_handoff",
        "integration_pattern": "handoff_function",
        "source_batch": "batch_0",
        "target_batch": "batch_1",
    }


@pytest.fixture
def sample_predicted_interface():
    """Sample predicted interface."""
    return {
        "predicted_functions": [
            {
                "name": "calculate_total",
                "parameters": ["items"],
                "return_type": "float",
            }
        ],
        "predicted_imports": ["from typing import List"],
    }


@pytest.fixture
def mock_config_enabled():
    """Mock configuration."""
    return {"glue_code_generator": {"enabled": True}}


class TestGenerate:
    """Test the main generate() function."""

    @patch("modsquad.extensions.glue_code_generator.load_extension_config")
    @patch("modsquad.extensions.glue_code_generator.dump_jsonl")
    def test_generate_success(
        self,
        mock_dump,
        mock_config,
        sample_intersection,
        sample_predicted_interface,
        mock_config_enabled,
    ):
        """Test successful glue code generation."""
        mock_config.return_value = mock_config_enabled

        result = glue_code_generator.generate(
            sample_intersection, sample_predicted_interface
        )

        assert isinstance(result, GlueCode)
        assert len(result.code_snippet) > 0
        assert result.integration_pattern != "disabled"

    @patch("modsquad.extensions.glue_code_generator.load_extension_config")
    def test_generate_disabled(
        self, mock_config, sample_intersection, sample_predicted_interface
    ):
        """Test disabled returns empty glue code."""
        mock_config.return_value = {"glue_code_generator": {"enabled": False}}

        result = glue_code_generator.generate(
            sample_intersection, sample_predicted_interface
        )

        assert result.integration_pattern == "disabled"
        assert result.code_snippet == ""


class TestEdgeCases:
    """Test edge cases."""

    @patch("modsquad.extensions.glue_code_generator.load_extension_config")
    @patch("modsquad.extensions.glue_code_generator.dump_jsonl")
    def test_generate_import_prediction(
        self, mock_dump, mock_config, sample_predicted_interface, mock_config_enabled
    ):
        """Test import prediction pattern."""
        mock_config.return_value = mock_config_enabled
        intersection = {
            "type": "import_chain",
            "integration_pattern": "import_prediction",
        }

        result = glue_code_generator.generate(intersection, sample_predicted_interface)

        assert isinstance(result, GlueCode)
        assert len(result.imports) > 0

    @patch("modsquad.extensions.glue_code_generator.load_extension_config")
    @patch("modsquad.extensions.glue_code_generator.dump_jsonl")
    def test_generate_unknown_pattern(
        self, mock_dump, mock_config, sample_predicted_interface, mock_config_enabled
    ):
        """Test handling of unknown integration pattern."""
        mock_config.return_value = mock_config_enabled
        intersection = {
            "type": "unknown",
            "integration_pattern": "unknown_pattern",
        }

        result = glue_code_generator.generate(intersection, sample_predicted_interface)

        # Should fall back to simple import
        assert isinstance(result, GlueCode)
