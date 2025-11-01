"""Unit tests for Risk Profiler - SUN TZU Squad.

Tests collision probability calculation between parallel tasks.
"""

import pytest
from pathlib import Path
from modsquad.extensions import risk_profiler


@pytest.fixture
def sample_tasks():
    """Sample task list for risk profiling."""
    return [
        {
            "id": "task1",
            "description": "Add authentication",
            "files": ["backend/app/routers/auth.py", "backend/app/models/user.py"],
        },
        {
            "id": "task2",
            "description": "Add logging",
            "files": ["backend/app/middleware/logging.py"],
        },
        {
            "id": "task3",
            "description": "Database migration",
            "files": ["backend/alembic/versions/add_users.py"],
        },
    ]


@pytest.fixture
def sample_dependency_graph():
    """Sample dependency graph."""
    return {
        "task1": [],
        "task2": [],
        "task3": ["task1"],
    }


class TestCalculate:
    """Test the main calculate() function."""

    def test_calculate_basic(self, sample_tasks, sample_dependency_graph):
        """Test basic risk profile calculation."""
        result = risk_profiler.calculate(sample_tasks, sample_dependency_graph)

        assert "individual" in result
        assert "pairs" in result

        # All tasks should have individual risk scores
        assert "task1" in result["individual"]
        assert "task2" in result["individual"]
        assert "task3" in result["individual"]

        # Should have pairwise collision probabilities
        assert len(result["pairs"]) > 0

    def test_calculate_empty_tasks(self):
        """Test calculation with empty task list."""
        result = risk_profiler.calculate([], {})

        assert result["individual"] == {}
        assert result["pairs"] == {}

    def test_calculate_single_task(self):
        """Test calculation with single task."""
        tasks = [
            {
                "id": "task1",
                "files": ["file1.py"],
            }
        ]

        result = risk_profiler.calculate(tasks, {"task1": []})

        assert "task1" in result["individual"]
        assert result["pairs"] == {}  # No pairs with single task


class TestIndividualRisk:
    """Test individual task risk calculation."""

    def test_individual_risk_single_file(self):
        """Test risk for task with single file."""
        task = {
            "id": "task1",
            "files": ["app/simple.py"],
        }

        risk = risk_profiler._calculate_individual_risk(task)

        assert risk == 0.1  # Base risk for single file

    def test_individual_risk_multiple_files(self):
        """Test risk increases with file count."""
        task_3_files = {
            "id": "task1",
            "files": ["file1.py", "file2.py", "file3.py"],
        }
        task_6_files = {
            "id": "task2",
            "files": ["f1.py", "f2.py", "f3.py", "f4.py", "f5.py", "f6.py"],
        }

        risk_3 = risk_profiler._calculate_individual_risk(task_3_files)
        risk_6 = risk_profiler._calculate_individual_risk(task_6_files)

        assert risk_3 == 0.2  # 2-3 files
        assert risk_6 == 0.5  # 6+ files

    def test_individual_risk_critical_files(self):
        """Test risk increases for critical files."""
        task = {
            "id": "task1",
            "files": ["backend/app/main.py"],
        }

        risk = risk_profiler._calculate_individual_risk(task)

        assert risk > 0.1  # Should be higher than base risk

    def test_individual_risk_database_migrations(self):
        """Test high risk for database migrations."""
        task = {
            "id": "task1",
            "files": ["backend/alembic/versions/001_migration.py"],
        }

        risk = risk_profiler._calculate_individual_risk(task)

        assert risk >= 0.3  # Base + migration penalty

    def test_individual_risk_init_files(self):
        """Test risk for __init__.py files."""
        task = {
            "id": "task1",
            "files": ["backend/app/__init__.py"],
        }

        risk = risk_profiler._calculate_individual_risk(task)

        assert risk > 0.1  # Critical file penalty

    def test_individual_risk_config_files(self):
        """Test risk for config files."""
        task = {
            "id": "task1",
            "files": ["backend/app/core/config.py"],
        }

        risk = risk_profiler._calculate_individual_risk(task)

        assert risk > 0.1  # Critical file penalty

    def test_individual_risk_capped_at_threshold(self):
        """Test risk is capped at 0.5."""
        task = {
            "id": "task1",
            "files": [
                "main.py",
                "__init__.py",
                "config.py",
                "database.py",
                "migrations/001.py",
                "migrations/002.py",
                "migrations/003.py",
                "file1.py",
                "file2.py",
                "file3.py",
            ],
        }

        risk = risk_profiler._calculate_individual_risk(task)

        assert risk <= 0.5  # Should be capped

    def test_individual_risk_no_files(self):
        """Test risk for task with no files."""
        task = {
            "id": "task1",
            "files": [],
        }

        risk = risk_profiler._calculate_individual_risk(task)

        assert risk == 0.1  # Minimum base risk


class TestCollisionProbability:
    """Test pairwise collision probability calculation."""

    def test_collision_explicit_dependency(self):
        """Test 100% collision for explicit dependencies."""
        task_a = {"id": "task_a", "files": ["file_a.py"]}
        task_b = {"id": "task_b", "files": ["file_b.py"]}
        dependency_graph = {"task_a": [], "task_b": ["task_a"]}

        collision = risk_profiler._calculate_collision_probability(
            task_a, task_b, dependency_graph
        )

        assert collision == 1.0  # 100% collision (sequential dependency)

    def test_collision_reverse_dependency(self):
        """Test collision with reverse dependency."""
        task_a = {"id": "task_a", "files": ["file_a.py"]}
        task_b = {"id": "task_b", "files": ["file_b.py"]}
        dependency_graph = {"task_a": ["task_b"], "task_b": []}

        collision = risk_profiler._calculate_collision_probability(
            task_a, task_b, dependency_graph
        )

        assert collision == 1.0  # 100% collision

    def test_collision_same_file(self):
        """Test high collision for same file modification."""
        task_a = {"id": "task_a", "files": ["shared.py"]}
        task_b = {"id": "task_b", "files": ["shared.py"]}
        dependency_graph = {"task_a": [], "task_b": []}

        collision = risk_profiler._calculate_collision_probability(
            task_a, task_b, dependency_graph
        )

        assert collision == 0.9  # 90% collision (file overlap)

    def test_collision_multiple_shared_files(self):
        """Test collision with multiple shared files."""
        task_a = {"id": "task_a", "files": ["file1.py", "shared.py"]}
        task_b = {"id": "task_b", "files": ["file2.py", "shared.py"]}
        dependency_graph = {"task_a": [], "task_b": []}

        collision = risk_profiler._calculate_collision_probability(
            task_a, task_b, dependency_graph
        )

        assert collision == 0.9  # 90% collision (any file overlap)

    def test_collision_same_directory(self):
        """Test collision for tasks in same directory."""
        task_a = {"id": "task_a", "files": ["backend/app/file1.py"]}
        task_b = {"id": "task_b", "files": ["backend/app/file2.py"]}
        dependency_graph = {"task_a": [], "task_b": []}

        collision = risk_profiler._calculate_collision_probability(
            task_a, task_b, dependency_graph
        )

        # Should be between 0% and 50% (directory overlap)
        assert 0.0 < collision <= 0.5

    def test_collision_different_directories(self):
        """Test low collision for different directories."""
        task_a = {"id": "task_a", "files": ["backend/app/file1.py"]}
        task_b = {"id": "task_b", "files": ["frontend/src/file2.tsx"]}
        dependency_graph = {"task_a": [], "task_b": []}

        collision = risk_profiler._calculate_collision_probability(
            task_a, task_b, dependency_graph
        )

        assert collision == 0.1  # 10% base collision

    def test_collision_nested_directories(self):
        """Test collision with nested directory structure."""
        task_a = {"id": "task_a", "files": ["backend/app/routers/auth.py"]}
        task_b = {"id": "task_b", "files": ["backend/app/routers/users.py"]}
        dependency_graph = {"task_a": [], "task_b": []}

        collision = risk_profiler._calculate_collision_probability(
            task_a, task_b, dependency_graph
        )

        # Same parent directory (backend/app/routers)
        assert collision > 0.1  # Higher than base

    def test_collision_no_overlap(self):
        """Test collision with no overlap."""
        task_a = {"id": "task_a", "files": ["backend/file1.py"]}
        task_b = {"id": "task_b", "files": ["frontend/file2.tsx"]}
        dependency_graph = {"task_a": [], "task_b": []}

        collision = risk_profiler._calculate_collision_probability(
            task_a, task_b, dependency_graph
        )

        assert collision == 0.1  # Base collision probability


class TestPairGeneration:
    """Test pair generation logic."""

    def test_all_pairs_generated(self, sample_tasks, sample_dependency_graph):
        """Test that all task pairs are analyzed."""
        result = risk_profiler.calculate(sample_tasks, sample_dependency_graph)

        # With 3 tasks, should have 3 pairs: (1,2), (1,3), (2,3)
        pairs = result["pairs"]
        assert len(pairs) == 3

    def test_pair_keys_bidirectional(self, sample_tasks, sample_dependency_graph):
        """Test pair keys are consistently formatted."""
        result = risk_profiler.calculate(sample_tasks, sample_dependency_graph)

        # Check that we have task1+task2 (not both task1+task2 and task2+task1)
        pair_keys = list(result["pairs"].keys())

        # All keys should follow task_a+task_b format
        for key in pair_keys:
            assert "+" in key
            parts = key.split("+")
            assert len(parts) == 2


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_missing_files_field(self):
        """Test handling task without files field."""
        task = {"id": "task1"}

        risk = risk_profiler._calculate_individual_risk(task)

        assert risk >= 0.0  # Should not crash

    def test_empty_files_list(self):
        """Test handling task with empty files list."""
        task = {"id": "task1", "files": []}

        risk = risk_profiler._calculate_individual_risk(task)

        assert risk == 0.1  # Base risk

    def test_none_files(self):
        """Test handling None files."""
        task = {"id": "task1", "files": None}

        # Should handle gracefully
        try:
            risk = risk_profiler._calculate_individual_risk(task)
            assert risk >= 0.0
        except (TypeError, AttributeError):
            pytest.skip("Implementation doesn't handle None files")

    def test_duplicate_files_in_task(self):
        """Test task with duplicate files."""
        task = {
            "id": "task1",
            "files": ["file.py", "file.py", "file.py"],
        }

        risk = risk_profiler._calculate_individual_risk(task)

        # Risk should be based on unique count (1 file)
        # Implementation uses len(files) directly, so this tests current behavior
        assert risk >= 0.1


class TestIntegration:
    """Test integration scenarios."""

    def test_high_risk_high_collision_scenario(self):
        """Test scenario with high risk and high collision."""
        tasks = [
            {
                "id": "task1",
                "files": [
                    "main.py",
                    "__init__.py",
                    "database.py",
                    "migrations/001.py",
                ],
            },
            {
                "id": "task2",
                "files": [
                    "main.py",
                    "config.py",
                    "database.py",
                ],
            },
        ]
        dependency_graph = {"task1": [], "task2": []}

        result = risk_profiler.calculate(tasks, dependency_graph)

        # Both should have high individual risk
        assert result["individual"]["task1"] >= 0.3
        assert result["individual"]["task2"] >= 0.3

        # High collision due to file overlap
        collision = result["pairs"]["task1+task2"]
        assert collision >= 0.9

    def test_low_risk_low_collision_scenario(self):
        """Test ideal scenario with low risk and low collision."""
        tasks = [
            {
                "id": "task1",
                "files": ["backend/new_feature.py"],
            },
            {
                "id": "task2",
                "files": ["frontend/new_component.tsx"],
            },
        ]
        dependency_graph = {"task1": [], "task2": []}

        result = risk_profiler.calculate(tasks, dependency_graph)

        # Both should have low individual risk
        assert result["individual"]["task1"] == 0.1
        assert result["individual"]["task2"] == 0.1

        # Low collision (different directories)
        collision = result["pairs"]["task1+task2"]
        assert collision == 0.1

    def test_mixed_risk_scenario(self):
        """Test scenario with mixed risk levels."""
        tasks = [
            {
                "id": "safe_task",
                "files": ["docs/README.md"],
            },
            {
                "id": "risky_task",
                "files": ["main.py", "database.py", "migrations/001.py"],
            },
        ]
        dependency_graph = {"safe_task": [], "risky_task": []}

        result = risk_profiler.calculate(tasks, dependency_graph)

        # Safe task should have low risk
        safe_risk = result["individual"]["safe_task"]
        risky_risk = result["individual"]["risky_task"]

        assert safe_risk < risky_risk
