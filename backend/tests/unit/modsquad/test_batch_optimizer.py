"""Unit tests for Batch Optimizer - SUN TZU Squad.

Tests constraint satisfaction solver for maximum parallelization with:
- Max 5 parallel batches
- <10% collision probability
- <0.5% risk per batch
- Topological ordering with cycle detection
"""

import pytest
from unittest.mock import patch, MagicMock
from modsquad.extensions import batch_optimizer


@pytest.fixture
def sample_tasks():
    """Sample task list."""
    return [
        {"id": "task1", "files": ["file1.py"], "dependencies": []},
        {"id": "task2", "files": ["file2.py"], "dependencies": []},
        {"id": "task3", "files": ["file3.py"], "dependencies": ["task1"]},
        {"id": "task4", "files": ["file4.py"], "dependencies": ["task2"]},
    ]


@pytest.fixture
def sample_dependency_graph():
    """Sample dependency graph."""
    return {
        "task1": [],
        "task2": [],
        "task3": ["task1"],
        "task4": ["task2"],
    }


@pytest.fixture
def sample_risk_profiles():
    """Sample risk profiles."""
    return {
        "individual": {
            "task1": 0.1,
            "task2": 0.1,
            "task3": 0.1,
            "task4": 0.1,
        },
        "pairs": {
            "task1+task2": 0.05,
            "task1+task3": 0.9,
            "task1+task4": 0.05,
            "task2+task3": 0.05,
            "task2+task4": 0.9,
            "task3+task4": 0.05,
        },
    }


@pytest.fixture
def mock_config_enabled():
    """Mock configuration."""
    return {"batch_optimizer": {"enabled": True}}


class TestOptimize:
    """Test the main optimize() function."""

    @patch("modsquad.extensions.batch_optimizer.load_extension_config")
    @patch("modsquad.extensions.batch_optimizer.dump_jsonl")
    def test_optimize_success(
        self,
        mock_dump,
        mock_config,
        sample_tasks,
        sample_dependency_graph,
        sample_risk_profiles,
        mock_config_enabled,
    ):
        """Test successful batch optimization."""
        mock_config.return_value = mock_config_enabled

        result = batch_optimizer.optimize(
            sample_tasks, sample_dependency_graph, sample_risk_profiles
        )

        assert result["status"] == "success"
        assert "batches" in result
        assert "levels" in result
        assert "metadata" in result
        assert "validation" in result

    @patch("modsquad.extensions.batch_optimizer.load_extension_config")
    def test_optimize_disabled(
        self, mock_config, sample_tasks, sample_dependency_graph, sample_risk_profiles
    ):
        """Test optimize returns disabled when not enabled."""
        mock_config.return_value = {"batch_optimizer": {"enabled": False}}

        result = batch_optimizer.optimize(
            sample_tasks, sample_dependency_graph, sample_risk_profiles
        )

        assert result["status"] == "disabled"

    @patch("modsquad.extensions.batch_optimizer.load_extension_config")
    @patch("modsquad.extensions.batch_optimizer._has_cycles")
    def test_optimize_circular_dependency_detection(
        self,
        mock_cycles,
        mock_config,
        sample_tasks,
        sample_dependency_graph,
        sample_risk_profiles,
        mock_config_enabled,
    ):
        """Test cycle detection blocks optimization."""
        mock_config.return_value = mock_config_enabled
        mock_cycles.return_value = True

        result = batch_optimizer.optimize(
            sample_tasks, sample_dependency_graph, sample_risk_profiles
        )

        assert result["status"] == "error"
        assert "Circular dependencies" in result["reason"]


class TestCycleDetection:
    """Test cycle detection in dependency graph."""

    def test_has_cycles_simple_cycle(self):
        """Test detection of simple A->B->A cycle."""
        graph = {
            "task1": ["task2"],
            "task2": ["task1"],
        }

        assert batch_optimizer._has_cycles(graph) is True

    def test_has_cycles_self_reference(self):
        """Test detection of self-referencing cycle."""
        graph = {
            "task1": ["task1"],
        }

        assert batch_optimizer._has_cycles(graph) is True

    def test_has_cycles_long_cycle(self):
        """Test detection of longer cycle A->B->C->A."""
        graph = {
            "task1": ["task2"],
            "task2": ["task3"],
            "task3": ["task1"],
        }

        assert batch_optimizer._has_cycles(graph) is True

    def test_has_cycles_no_cycle(self):
        """Test no cycle in valid DAG."""
        graph = {
            "task1": [],
            "task2": [],
            "task3": ["task1", "task2"],
        }

        assert batch_optimizer._has_cycles(graph) is False

    def test_has_cycles_empty_graph(self):
        """Test empty graph has no cycles."""
        assert batch_optimizer._has_cycles({}) is False


class TestTopologicalLevels:
    """Test topological level computation."""

    def test_compute_topological_levels_simple(self, sample_tasks, sample_dependency_graph):
        """Test simple topological sorting."""
        result = batch_optimizer._compute_topological_levels(
            sample_tasks, sample_dependency_graph
        )

        # task1 and task2 have no dependencies (level 0)
        # task3 and task4 depend on level 0 (level 1)
        assert len(result) == 2
        assert set(result[0]) == {"task1", "task2"}
        assert set(result[1]) == {"task3", "task4"}

    def test_compute_topological_levels_linear(self):
        """Test linear dependency chain."""
        tasks = [
            {"id": "task1", "dependencies": []},
            {"id": "task2", "dependencies": []},
            {"id": "task3", "dependencies": []},
        ]
        graph = {
            "task1": [],
            "task2": ["task1"],
            "task3": ["task2"],
        }

        result = batch_optimizer._compute_topological_levels(tasks, graph)

        # Should create 3 levels
        assert len(result) == 3
        assert result[0] == ["task1"]
        assert result[1] == ["task2"]
        assert result[2] == ["task3"]

    def test_compute_topological_levels_parallel(self):
        """Test all independent tasks in same level."""
        tasks = [
            {"id": f"task{i}", "dependencies": []} for i in range(5)
        ]
        graph = {f"task{i}": [] for i in range(5)}

        result = batch_optimizer._compute_topological_levels(tasks, graph)

        # All tasks should be in level 0
        assert len(result) == 1
        assert len(result[0]) == 5


class TestBatchCreation:
    """Test batch creation from topological levels."""

    def test_create_batches_respects_risk_constraint(
        self, sample_tasks, sample_risk_profiles
    ):
        """Test batches respect MAX_BATCH_RISK constraint."""
        levels = [["task1", "task2", "task3", "task4"]]

        # Set high individual risk to force splitting
        high_risk_profiles = {
            "individual": {
                "task1": 0.004,
                "task2": 0.004,
                "task3": 0.004,
                "task4": 0.004,
            },
            "pairs": {
                "task1+task2": 0.05,
                "task1+task3": 0.05,
                "task1+task4": 0.05,
                "task2+task3": 0.05,
                "task2+task4": 0.05,
                "task3+task4": 0.05,
            },
        }

        result = batch_optimizer._create_batches(levels, high_risk_profiles, sample_tasks)

        # Each batch should be under 0.005 (0.5%) risk
        for batch_info in result.values():
            assert batch_info["risk"] <= batch_optimizer.MAX_BATCH_RISK

    def test_create_batches_respects_collision_constraint(self, sample_tasks):
        """Test batches respect MAX_COLLISION_PROBABILITY constraint."""
        levels = [["task1", "task2"]]
        task_map = {task["id"]: task for task in sample_tasks}

        # Set high collision probability
        risk_profiles = {
            "individual": {"task1": 0.1, "task2": 0.1},
            "pairs": {"task1+task2": 0.95},  # Very high collision
        }

        result = batch_optimizer._create_batches(levels, risk_profiles, sample_tasks)

        # task1 and task2 should be in different batches due to high collision
        task1_batch = None
        task2_batch = None

        for batch_id, batch_info in result.items():
            if "task1" in batch_info["tasks"]:
                task1_batch = batch_id
            if "task2" in batch_info["tasks"]:
                task2_batch = batch_id

        assert task1_batch != task2_batch


class TestCanAddToBatch:
    """Test constraint checking for adding tasks to batches."""

    def test_can_add_to_batch_risk_violation(self):
        """Test rejection when risk constraint violated."""
        task_map = {"task1": {"id": "task1"}}
        risk_profiles = {
            "individual": {"task1": 0.004},
            "pairs": {},
        }

        # Current batch risk is 0.004, adding 0.004 would exceed 0.005 threshold
        result = batch_optimizer._can_add_to_batch(
            "task1", [], 0.004, risk_profiles, task_map
        )

        assert result is False

    def test_can_add_to_batch_collision_violation(self):
        """Test rejection when collision probability too high."""
        task_map = {"task1": {"id": "task1"}, "task2": {"id": "task2"}}
        risk_profiles = {
            "individual": {"task1": 0.001, "task2": 0.001},
            "pairs": {"task1+task2": 0.95},  # 95% collision
        }

        result = batch_optimizer._can_add_to_batch(
            "task2", ["task1"], 0.001, risk_profiles, task_map
        )

        assert result is False

    def test_can_add_to_batch_success(self):
        """Test successful addition when constraints satisfied."""
        task_map = {"task1": {"id": "task1"}, "task2": {"id": "task2"}}
        risk_profiles = {
            "individual": {"task1": 0.001, "task2": 0.001},
            "pairs": {"task1+task2": 0.05},  # Low collision
        }

        result = batch_optimizer._can_add_to_batch(
            "task2", ["task1"], 0.001, risk_profiles, task_map
        )

        assert result is True


class TestValidation:
    """Test constraint validation."""

    def test_validate_constraints_success(self):
        """Test validation passes with valid batches."""
        batches = {
            "batch_0": {
                "tasks": ["task1", "task2"],
                "risk": 0.002,
            }
        }
        risk_profiles = {
            "individual": {"task1": 0.001, "task2": 0.001},
            "pairs": {"task1+task2": 0.05},
        }

        result = batch_optimizer._validate_constraints(batches, risk_profiles)

        assert result["passed"] is True
        assert len(result["violations"]) == 0

    def test_validate_constraints_too_many_batches(self):
        """Test violation when batch count exceeds limit."""
        batches = {f"batch_{i}": {"tasks": [f"task{i}"], "risk": 0.001} for i in range(10)}
        risk_profiles = {"individual": {}, "pairs": {}}

        result = batch_optimizer._validate_constraints(batches, risk_profiles)

        assert result["passed"] is False
        assert any("MAX_PARALLEL_BATCHES" in v for v in result["violations"])

    def test_validate_constraints_risk_violation(self):
        """Test violation when batch risk exceeds limit."""
        batches = {
            "batch_0": {
                "tasks": ["task1"],
                "risk": 0.010,  # Exceeds 0.005 limit
            }
        }
        risk_profiles = {"individual": {}, "pairs": {}}

        result = batch_optimizer._validate_constraints(batches, risk_profiles)

        assert result["passed"] is False
        assert any("MAX_BATCH_RISK" in v for v in result["violations"])


class TestMetadata:
    """Test metadata computation."""

    def test_compute_metadata(self, sample_tasks):
        """Test metadata calculation."""
        batches = {
            "batch_0": {
                "tasks": ["task1", "task2"],
                "level": 0,
                "task_count": 2,
                "files": ["file1.py", "file2.py"],
            },
            "batch_1": {
                "tasks": ["task3", "task4"],
                "level": 1,
                "task_count": 2,
                "files": ["file3.py", "file4.py"],
            },
        }
        validation = {"passed": True}

        result = batch_optimizer._compute_metadata(batches, sample_tasks, validation)

        assert result["total_tasks"] == 4
        assert result["total_batches"] == 2
        assert result["total_levels"] == 2
        assert result["max_parallel_tasks"] == 2
        assert result["constraints_satisfied"] is True
        assert result["total_files"] == 4


class TestEdgeCases:
    """Test edge cases and error handling."""

    @patch("modsquad.extensions.batch_optimizer.load_extension_config")
    def test_optimize_empty_tasks(self, mock_config, mock_config_enabled):
        """Test optimize with empty task list."""
        mock_config.return_value = mock_config_enabled

        result = batch_optimizer.optimize([], {}, {"individual": {}, "pairs": {}})

        assert result["status"] == "success"
        assert len(result["batches"]) == 0

    def test_collect_batch_files(self):
        """Test file collection from tasks."""
        task_map = {
            "task1": {"id": "task1", "files": ["file1.py", "file2.py"]},
            "task2": {"id": "task2", "files": ["file3.py"]},
        }

        result = batch_optimizer._collect_batch_files(["task1", "task2"], task_map)

        assert sorted(result) == ["file1.py", "file2.py", "file3.py"]

    def test_collect_batch_files_deduplicated(self):
        """Test file collection deduplicates files."""
        task_map = {
            "task1": {"id": "task1", "files": ["shared.py", "file1.py"]},
            "task2": {"id": "task2", "files": ["shared.py", "file2.py"]},
        }

        result = batch_optimizer._collect_batch_files(["task1", "task2"], task_map)

        # Should deduplicate shared.py
        assert sorted(result) == ["file1.py", "file2.py", "shared.py"]
        assert result.count("shared.py") == 1
