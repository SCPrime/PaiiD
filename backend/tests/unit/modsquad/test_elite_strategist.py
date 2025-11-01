"""Unit tests for Elite Strategist - SUN TZU Squad Leader.

Tests strategic batch planning orchestration, safety checks, and coordination.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, Mock
from modsquad.extensions import elite_strategist


@pytest.fixture
def sample_tasks():
    """Sample task list for testing."""
    return [
        {
            "id": "task1",
            "description": "Add user authentication",
            "files": ["backend/app/routers/auth.py", "backend/app/models/user.py"],
            "dependencies": [],
            "estimated_duration": 120,
        },
        {
            "id": "task2",
            "description": "Add logging middleware",
            "files": ["backend/app/middleware/logging.py"],
            "dependencies": [],
            "estimated_duration": 60,
        },
        {
            "id": "task3",
            "description": "Update API documentation",
            "files": ["backend/app/main.py"],
            "dependencies": ["task1"],
            "estimated_duration": 30,
        },
    ]


@pytest.fixture
def mock_config_enabled():
    """Mock configuration with elite_strategist enabled."""
    return {
        "elite_strategist": {
            "enabled": True,
            "max_parallel_batches": 5,
            "max_collision_probability": 0.10,
        }
    }


@pytest.fixture
def mock_config_disabled():
    """Mock configuration with elite_strategist disabled."""
    return {
        "elite_strategist": {
            "enabled": False,
        }
    }


class TestEliteStrategistRun:
    """Test the main run() orchestration function."""

    @patch("modsquad.extensions.elite_strategist.load_extension_config")
    @patch("modsquad.extensions.elite_strategist._is_safe_to_batch")
    @patch("modsquad.extensions.elite_strategist.task_graph_analyzer")
    @patch("modsquad.extensions.elite_strategist.risk_profiler")
    @patch("modsquad.extensions.elite_strategist.batch_optimizer")
    @patch("modsquad.extensions.elite_strategist.intersection_mapper")
    @patch("modsquad.extensions.elite_strategist.dump_jsonl")
    def test_run_success(
        self,
        mock_dump,
        mock_mapper,
        mock_optimizer,
        mock_profiler,
        mock_analyzer,
        mock_safe,
        mock_config,
        sample_tasks,
        mock_config_enabled,
    ):
        """Test successful batch planning orchestration."""
        # Setup mocks
        mock_config.return_value = mock_config_enabled
        mock_safe.return_value = True

        mock_dependency_graph = {"task1": [], "task2": [], "task3": ["task1"]}
        mock_analyzer.analyze.return_value = mock_dependency_graph

        mock_risk_profiles = {
            "individual": {"task1": 0.2, "task2": 0.1, "task3": 0.1},
            "pairs": {"task1+task2": 0.05, "task1+task3": 0.9, "task2+task3": 0.05},
        }
        mock_profiler.calculate.return_value = mock_risk_profiles

        mock_batch_plan = {
            "status": "success",
            "batches": {
                "batch_0": {"tasks": ["task1", "task2"], "level": 0},
                "batch_1": {"tasks": ["task3"], "level": 1},
            },
        }
        mock_optimizer.optimize.return_value = mock_batch_plan

        mock_intersections = [
            {
                "type": "function_handoff",
                "source_batch": "batch_0",
                "target_batch": "batch_1",
            }
        ]
        mock_mapper.map_intersections.return_value = mock_intersections

        # Execute
        result = elite_strategist.run(sample_tasks)

        # Verify
        assert result["status"] == "success"
        assert "intersections" in result
        assert "strategist_metadata" in result
        assert result["strategist_metadata"]["total_tasks"] == 3
        assert result["strategist_metadata"]["total_batches"] == 2

        # Verify squad member calls
        mock_analyzer.analyze.assert_called_once_with(sample_tasks)
        mock_profiler.calculate.assert_called_once_with(sample_tasks, mock_dependency_graph)
        mock_optimizer.optimize.assert_called_once()
        mock_mapper.map_intersections.assert_called_once()

    @patch("modsquad.extensions.elite_strategist.load_extension_config")
    def test_run_disabled(self, mock_config, sample_tasks, mock_config_disabled):
        """Test run() returns disabled status when not enabled."""
        mock_config.return_value = mock_config_disabled

        result = elite_strategist.run(sample_tasks)

        assert result["status"] == "disabled"
        assert "reason" in result

    @patch("modsquad.extensions.elite_strategist.load_extension_config")
    @patch("modsquad.extensions.elite_strategist._is_safe_to_batch")
    def test_run_blocked_by_server(
        self, mock_safe, mock_config, sample_tasks, mock_config_enabled
    ):
        """Test run() blocks when servers are running."""
        mock_config.return_value = mock_config_enabled
        mock_safe.return_value = False

        result = elite_strategist.run(sample_tasks)

        assert result["status"] == "blocked"
        assert "Backend or frontend server running" in result["reason"]
        assert "fix" in result


class TestSafetyChecks:
    """Test server safety detection."""

    @patch("modsquad.extensions.elite_strategist.requests.get")
    def test_is_safe_backend_running(self, mock_get):
        """Test safety check detects running backend."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = elite_strategist._is_safe_to_batch()

        assert result is False
        mock_get.assert_called_with("http://localhost:8001/api/health", timeout=1)

    @patch("modsquad.extensions.elite_strategist.requests.get")
    def test_is_safe_frontend_running(self, mock_get):
        """Test safety check detects running frontend."""
        def side_effect(url, timeout):
            if "8001" in url:
                raise Exception("Connection refused")
            else:
                mock_response = Mock()
                mock_response.status_code = 200
                return mock_response

        mock_get.side_effect = side_effect

        result = elite_strategist._is_safe_to_batch()

        assert result is False

    @patch("modsquad.extensions.elite_strategist.requests.get")
    def test_is_safe_no_servers_running(self, mock_get):
        """Test safety check passes when no servers running."""
        mock_get.side_effect = Exception("Connection refused")

        result = elite_strategist._is_safe_to_batch()

        assert result is True

    @patch.dict("os.environ", {"MODSQUAD_ALLOW_LIVE_BATCHING": "true"})
    def test_is_safe_environment_override(self):
        """Test environment variable override allows batching."""
        result = elite_strategist._is_safe_to_batch()

        assert result is True


class TestMetadataCalculations:
    """Test metadata calculation utilities."""

    def test_calculate_parallelization(self):
        """Test parallelization factor calculation."""
        batch_plan = {
            "batches": [
                {"tasks": ["task1", "task2", "task3"]},
                {"tasks": ["task4"]},
                {"tasks": ["task5", "task6"]},
            ]
        }

        result = elite_strategist._calculate_parallelization(batch_plan)

        # Max parallel = 3, total = 6, factor = 3/6 * 100 = 50%
        assert result == 50.0

    def test_calculate_parallelization_empty(self):
        """Test parallelization factor with empty batches."""
        batch_plan = {"batches": []}

        result = elite_strategist._calculate_parallelization(batch_plan)

        assert result == 0.0

    def test_calculate_speedup(self):
        """Test speedup estimation calculation."""
        batch_plan = {
            "batches": [
                {
                    "tasks": [
                        {"estimated_duration": 60},
                        {"estimated_duration": 120},
                    ]
                },
                {
                    "tasks": [
                        {"estimated_duration": 30},
                    ]
                },
            ]
        }

        result = elite_strategist._calculate_speedup(batch_plan)

        # Sequential: 60 + 120 + 30 = 210
        # Parallel: max(60, 120) + 30 = 150
        # Speedup: (1 - 150/210) * 100 = 28.6%
        assert "28" in result or "29" in result  # Allow for rounding

    def test_calculate_speedup_empty(self):
        """Test speedup with no batches."""
        batch_plan = {"batches": []}

        result = elite_strategist._calculate_speedup(batch_plan)

        assert result == "0%"


class TestPublicAPI:
    """Test public API functions."""

    @patch("modsquad.extensions.elite_strategist.run")
    def test_strategize(self, mock_run, sample_tasks):
        """Test strategize() public API."""
        mock_run.return_value = {"status": "success"}

        result = elite_strategist.strategize(sample_tasks)

        assert result["status"] == "success"
        mock_run.assert_called_once_with(sample_tasks)


class TestErrorHandling:
    """Test error handling and edge cases."""

    @patch("modsquad.extensions.elite_strategist.load_extension_config")
    @patch("modsquad.extensions.elite_strategist._is_safe_to_batch")
    def test_run_empty_task_list(self, mock_safe, mock_config, mock_config_enabled):
        """Test run() handles empty task list."""
        mock_config.return_value = mock_config_enabled
        mock_safe.return_value = True

        # Should not crash with empty tasks
        result = elite_strategist.run([])

        assert "strategist_metadata" in result

    @patch("modsquad.extensions.elite_strategist.load_extension_config")
    @patch("modsquad.extensions.elite_strategist._is_safe_to_batch")
    def test_run_none_task_list(self, mock_safe, mock_config, mock_config_enabled):
        """Test run() handles None task list."""
        mock_config.return_value = mock_config_enabled
        mock_safe.return_value = True

        # Should not crash with None
        result = elite_strategist.run(None)

        assert "strategist_metadata" in result
