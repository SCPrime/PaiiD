"""Unit tests for Elite Weaver - ARMANI Squad Leader.

Tests strategic integration orchestration of parallel batch results.
"""

import pytest
from unittest.mock import patch, MagicMock
from modsquad.extensions import elite_weaver


@pytest.fixture
def sample_batch_plan():
    """Sample batch plan with intersections."""
    return {
        "batches": {
            "batch_0": {"tasks": ["task1"], "level": 0},
            "batch_1": {"tasks": ["task2"], "level": 1},
        },
        "intersections": [
            {
                "type": "function_handoff",
                "source_batch": "batch_0",
                "target_batch": "batch_1",
                "priority": "high",
            }
        ],
    }


@pytest.fixture
def sample_batch_results():
    """Sample completed batch results."""
    return {
        "batch_0": {
            "status": "success",
            "output": {"files": ["file1.py"], "content": "def test(): pass"},
        },
        "batch_1": {
            "status": "success",
            "output": {"files": ["file2.py"], "content": "import file1"},
        },
    }


@pytest.fixture
def mock_config_enabled():
    """Mock configuration."""
    return {"elite_weaver": {"enabled": True}}


class TestRun:
    """Test the main run() orchestration function."""

    @patch("modsquad.extensions.elite_weaver.load_extension_config")
    @patch("modsquad.extensions.elite_weaver.dump_jsonl")
    @patch("modsquad.extensions.elite_weaver._extract_intersections")
    @patch("modsquad.extensions.elite_weaver._monitor_batch_completion")
    @patch("modsquad.extensions.elite_weaver._predict_interfaces")
    @patch("modsquad.extensions.elite_weaver._generate_glue_code")
    @patch("modsquad.extensions.elite_weaver._resolve_conflicts")
    @patch("modsquad.extensions.elite_weaver._execute_intersections")
    @patch("modsquad.extensions.elite_weaver._validate_integrations")
    @patch("modsquad.extensions.elite_weaver._compile_status")
    def test_run_success(
        self,
        mock_status,
        mock_validate,
        mock_execute,
        mock_resolve,
        mock_glue,
        mock_predict,
        mock_monitor,
        mock_extract,
        mock_dump,
        mock_config,
        sample_batch_plan,
        sample_batch_results,
        mock_config_enabled,
    ):
        """Test successful integration orchestration."""
        mock_config.return_value = mock_config_enabled
        mock_extract.return_value = sample_batch_plan["intersections"]
        mock_monitor.return_value = sample_batch_plan["intersections"]
        mock_predict.return_value = {}
        mock_glue.return_value = {}
        mock_resolve.return_value = {}
        mock_execute.return_value = {"completed": [], "failed": []}
        mock_validate.return_value = {"passed": True}
        mock_status.return_value = {"status": "success"}

        result = elite_weaver.run(sample_batch_plan, sample_batch_results)

        assert result["status"] == "success"
        mock_extract.assert_called_once()
        mock_monitor.assert_called_once()

    @patch("modsquad.extensions.elite_weaver.load_extension_config")
    def test_run_disabled(
        self, mock_config, sample_batch_plan, sample_batch_results
    ):
        """Test run returns disabled when not enabled."""
        mock_config.return_value = {"elite_weaver": {"enabled": False}}

        result = elite_weaver.run(sample_batch_plan, sample_batch_results)

        assert result["status"] == "disabled"


class TestExtractIntersections:
    """Test intersection extraction from batch plan."""

    def test_extract_intersections(self, sample_batch_plan):
        """Test extraction of intersections."""
        result = elite_weaver._extract_intersections(sample_batch_plan)

        assert len(result) == 1
        assert result[0]["type"] == "function_handoff"

    def test_extract_intersections_empty(self):
        """Test with no intersections."""
        batch_plan = {"batches": {}}

        result = elite_weaver._extract_intersections(batch_plan)

        assert result == []


class TestMonitorBatchCompletion:
    """Test batch completion monitoring."""

    def test_monitor_batch_completion_ready(self, sample_batch_results):
        """Test detection of ready intersections."""
        intersections = [
            {
                "type": "function_handoff",
                "source_batch": "batch_0",
                "target_batch": "batch_1",
            }
        ]

        result = elite_weaver._monitor_batch_completion(
            intersections, sample_batch_results
        )

        assert len(result) == 1

    def test_monitor_batch_completion_not_ready(self):
        """Test filtering of not-ready intersections."""
        intersections = [
            {
                "type": "function_handoff",
                "source_batch": "batch_0",
                "target_batch": "batch_1",
            }
        ]
        batch_results = {
            "batch_0": {"status": "running"},  # Not complete
        }

        result = elite_weaver._monitor_batch_completion(
            intersections, batch_results
        )

        assert len(result) == 0

    def test_monitor_batch_completion_file_merge_requires_both(self):
        """Test file merge requires both batches complete."""
        intersections = [
            {
                "type": "file_merge",
                "source_batch": "batch_0",
                "target_batch": "batch_1",
            }
        ]
        batch_results = {
            "batch_0": {"status": "success"},
            # batch_1 missing
        }

        result = elite_weaver._monitor_batch_completion(
            intersections, batch_results
        )

        assert len(result) == 0


class TestEdgeCases:
    """Test edge cases and error handling."""

    @patch("modsquad.extensions.elite_weaver.load_extension_config")
    @patch("modsquad.extensions.elite_weaver.dump_jsonl")
    def test_run_empty_intersections(
        self, mock_dump, mock_config, mock_config_enabled
    ):
        """Test with no intersections."""
        mock_config.return_value = mock_config_enabled
        batch_plan = {"batches": {}, "intersections": []}
        batch_results = {}

        result = elite_weaver.run(batch_plan, batch_results)

        # Should complete without errors
        assert "status" in result

    @patch("modsquad.extensions.elite_weaver.load_extension_config")
    @patch("modsquad.extensions.elite_weaver.dump_jsonl")
    def test_run_partial_batch_completion(
        self, mock_dump, mock_config, sample_batch_plan, mock_config_enabled
    ):
        """Test with some batches incomplete."""
        mock_config.return_value = mock_config_enabled
        batch_results = {
            "batch_0": {"status": "success"},
            # batch_1 missing
        }

        result = elite_weaver.run(sample_batch_plan, batch_results)

        # Should handle gracefully
        assert "status" in result
