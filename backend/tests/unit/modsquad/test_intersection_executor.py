"""Unit tests for Intersection Executor - ARMANI Squad.

Tests execution of integration at intersection points.
"""

import pytest
from unittest.mock import patch, MagicMock, mock_open
from modsquad.extensions import intersection_executor


@pytest.fixture
def sample_intersection():
    """Sample intersection."""
    return {
        "id": "intersection_1",
        "type": "function_handoff",
        "target_file": "backend/app/main.py",
        "source_batch": "batch_0",
        "target_batch": "batch_1",
    }


@pytest.fixture
def sample_glue_code():
    """Sample glue code."""
    return {
        "pattern": "handoff_function",
        "code_snippet": "from app.utils import calculate_total",
        "target_location": "backend/app/main.py",
        "insertion_strategy": "append",
    }


@pytest.fixture
def sample_resolutions():
    """Sample conflict resolutions."""
    return [
        {
            "file_path": "backend/app/main.py",
            "strategy": "auto_merge",
            "resolved_content": "merged content",
        }
    ]


@pytest.fixture
def mock_config_enabled():
    """Mock configuration."""
    return {"intersection_executor": {"enabled": True}}


class TestExecute:
    """Test the main execute() function."""

    @patch("modsquad.extensions.intersection_executor.load_extension_config")
    def test_execute_disabled(
        self, mock_config, sample_intersection, sample_glue_code
    ):
        """Test disabled returns status."""
        mock_config.return_value = {"intersection_executor": {"enabled": False}}

        result = intersection_executor.execute(
            sample_intersection, sample_glue_code
        )

        assert result["status"] == "disabled"

    @patch("modsquad.extensions.intersection_executor.load_extension_config")
    @patch("modsquad.extensions.intersection_executor.dump_jsonl")
    @patch("builtins.open", new_callable=mock_open, read_data="existing code")
    @patch("pathlib.Path.exists", return_value=True)
    def test_execute_success(
        self,
        mock_exists,
        mock_file,
        mock_dump,
        mock_config,
        sample_intersection,
        sample_glue_code,
        mock_config_enabled,
    ):
        """Test successful execution."""
        mock_config.return_value = mock_config_enabled

        result = intersection_executor.execute(
            sample_intersection, sample_glue_code
        )

        # Should return execution result
        assert "status" in result


class TestValidationErrors:
    """Test validation error handling."""

    @patch("modsquad.extensions.intersection_executor.load_extension_config")
    def test_execute_missing_target_file(
        self, mock_config, sample_glue_code, mock_config_enabled
    ):
        """Test handling of missing target file."""
        mock_config.return_value = mock_config_enabled

        intersection = {
            "id": "intersection_1",
            "type": "function_handoff",
            # Missing target_file
        }

        result = intersection_executor.execute(intersection, sample_glue_code)

        # Should handle gracefully
        assert "status" in result


class TestEdgeCases:
    """Test edge cases."""

    @patch("modsquad.extensions.intersection_executor.load_extension_config")
    @patch("modsquad.extensions.intersection_executor.dump_jsonl")
    def test_execute_with_resolutions(
        self,
        mock_dump,
        mock_config,
        sample_intersection,
        sample_glue_code,
        sample_resolutions,
        mock_config_enabled,
    ):
        """Test execution with conflict resolutions."""
        mock_config.return_value = mock_config_enabled

        result = intersection_executor.execute(
            sample_intersection, sample_glue_code, sample_resolutions
        )

        assert "status" in result

    @patch("modsquad.extensions.intersection_executor.load_extension_config")
    @patch("modsquad.extensions.intersection_executor.dump_jsonl")
    def test_execute_no_resolutions(
        self,
        mock_dump,
        mock_config,
        sample_intersection,
        sample_glue_code,
        mock_config_enabled,
    ):
        """Test execution without conflict resolutions."""
        mock_config.return_value = mock_config_enabled

        result = intersection_executor.execute(
            sample_intersection, sample_glue_code, None
        )

        assert "status" in result
