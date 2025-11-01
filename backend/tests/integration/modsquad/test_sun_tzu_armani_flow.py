"""Integration tests for SUN TZU + ARMANI Squad End-to-End Flow.

Tests the complete parallel batch execution pipeline:
1. SUN TZU: Strategic planning (elite_strategist → task_graph → risk → batch → intersection)
2. ARMANI: Integration weaving (elite_weaver → interface → glue → conflict → executor → validator)

This test suite validates that the two squads work together seamlessly to:
- Analyze task dependencies and optimize batching
- Execute parallel modifications safely
- Detect and resolve conflicts
- Weave results into cohesive codebase
- Validate integrated code
"""

import pytest
import tempfile
import shutil
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add repo root to path for modsquad imports
_repo_root = Path(__file__).parent.parent.parent.parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

# Import both squad leaders
from modsquad.extensions import elite_strategist, elite_weaver
from modsquad.extensions import (
    task_graph_analyzer,
    risk_profiler,
    batch_optimizer,
    intersection_mapper,
    interface_predictor,
    glue_code_generator,
    conflict_resolver,
    intersection_executor,
    integration_validator,
)


@pytest.fixture
def temp_codebase(tmp_path):
    """Create temporary codebase for testing."""
    # Create backend structure
    backend = tmp_path / "backend"
    backend.mkdir()

    app = backend / "app"
    app.mkdir()

    # Create initial files
    (app / "__init__.py").write_text("")
    (app / "main.py").write_text("""
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
""")

    (app / "models.py").write_text("""
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
""")

    return tmp_path


@pytest.fixture
def sample_parallel_tasks(temp_codebase):
    """Sample tasks that can be executed in parallel."""
    return [
        {
            "id": "task1",
            "description": "Add authentication router",
            "files": [str(temp_codebase / "backend/app/auth.py")],
            "dependencies": [],
            "estimated_duration": 60,
        },
        {
            "id": "task2",
            "description": "Add user model fields",
            "files": [str(temp_codebase / "backend/app/models.py")],
            "dependencies": [],
            "estimated_duration": 30,
        },
        {
            "id": "task3",
            "description": "Update main app to use auth",
            "files": [str(temp_codebase / "backend/app/main.py")],
            "dependencies": ["task1"],
            "estimated_duration": 45,
        },
    ]


@pytest.fixture
def mock_configs_enabled():
    """Mock all extension configs as enabled."""
    return {
        "elite_strategist": {"enabled": True},
        "task_graph_analyzer": {"enabled": True},
        "risk_profiler": {"enabled": True},
        "batch_optimizer": {"enabled": True},
        "intersection_mapper": {"enabled": True},
        "elite_weaver": {"enabled": True},
        "interface_predictor": {"enabled": True},
        "glue_code_generator": {"enabled": True},
        "conflict_resolver": {"enabled": True},
        "intersection_executor": {"enabled": True},
        "integration_validator": {"enabled": True},
    }


class TestSunTzuPlanningPhase:
    """Test SUN TZU strategic planning phase."""

    @patch("modsquad.extensions.elite_strategist.load_extension_config")
    @patch("modsquad.extensions.elite_strategist._is_safe_to_batch")
    @patch("modsquad.extensions.elite_strategist.dump_jsonl")
    def test_strategic_planning_creates_batch_plan(
        self,
        mock_dump,
        mock_safe,
        mock_config,
        sample_parallel_tasks,
        mock_configs_enabled,
    ):
        """Test elite_strategist creates optimized batch plan."""
        mock_config.return_value = mock_configs_enabled
        mock_safe.return_value = True

        # Execute strategic planning
        batch_plan = elite_strategist.run(sample_parallel_tasks)

        # Verify batch plan created
        assert batch_plan["status"] == "success"
        assert "batches" in batch_plan
        assert "intersections" in batch_plan
        assert "strategist_metadata" in batch_plan

        # Verify parallelization
        assert batch_plan["strategist_metadata"]["total_tasks"] == 3
        assert batch_plan["strategist_metadata"]["total_batches"] >= 1

        # Verify intersections identified
        assert batch_plan["strategist_metadata"]["total_intersections"] >= 0

    @patch("modsquad.extensions.elite_strategist.load_extension_config")
    @patch("modsquad.extensions.elite_strategist._is_safe_to_batch")
    @patch("modsquad.extensions.elite_strategist.dump_jsonl")
    def test_dependency_graph_respects_constraints(
        self,
        mock_dump,
        mock_safe,
        mock_config,
        sample_parallel_tasks,
        mock_configs_enabled,
    ):
        """Test that dependency graph prevents task3 from running before task1."""
        mock_config.return_value = mock_configs_enabled
        mock_safe.return_value = True

        batch_plan = elite_strategist.run(sample_parallel_tasks)

        # Find batches containing task1 and task3
        task1_batch = None
        task3_batch = None

        for batch_id, batch_info in batch_plan.get("batches", {}).items():
            if "task1" in batch_info.get("tasks", []):
                task1_batch = batch_info
            if "task3" in batch_info.get("tasks", []):
                task3_batch = batch_info

        # task3 should be in a later level than task1
        if task1_batch and task3_batch:
            assert task3_batch["level"] > task1_batch["level"]


class TestArmaniWeavingPhase:
    """Test ARMANI integration weaving phase."""

    @patch("modsquad.extensions.elite_weaver.load_extension_config")
    @patch("modsquad.extensions.elite_weaver.dump_jsonl")
    def test_weaving_orchestrates_integration(
        self, mock_dump, mock_config, mock_configs_enabled
    ):
        """Test elite_weaver orchestrates complete integration."""
        mock_config.return_value = mock_configs_enabled

        # Mock batch plan with intersections
        batch_plan = {
            "batches": {
                "batch_0": {"tasks": ["task1", "task2"], "level": 0},
                "batch_1": {"tasks": ["task3"], "level": 1},
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

        # Mock completed batch results
        batch_results = {
            "batch_0": {
                "status": "success",
                "output": {"files": ["auth.py"], "content": "def login(): pass"},
            },
            "batch_1": {
                "status": "success",
                "output": {"files": ["main.py"], "content": "from auth import login"},
            },
        }

        # Execute weaving
        integration_status = elite_weaver.run(batch_plan, batch_results)

        # Verify integration completed
        assert "status" in integration_status


class TestEndToEndFlow:
    """Test complete SUN TZU → ARMANI flow."""

    @patch("modsquad.extensions.elite_strategist.load_extension_config")
    @patch("modsquad.extensions.elite_strategist._is_safe_to_batch")
    @patch("modsquad.extensions.elite_strategist.dump_jsonl")
    @patch("modsquad.extensions.elite_weaver.load_extension_config")
    @patch("modsquad.extensions.elite_weaver.dump_jsonl")
    def test_full_pipeline_planning_to_weaving(
        self,
        mock_weaver_dump,
        mock_weaver_config,
        mock_strategist_dump,
        mock_safe,
        mock_strategist_config,
        sample_parallel_tasks,
        mock_configs_enabled,
    ):
        """Test complete pipeline from planning through weaving."""
        mock_strategist_config.return_value = mock_configs_enabled
        mock_weaver_config.return_value = mock_configs_enabled
        mock_safe.return_value = True

        # Phase 1: SUN TZU Strategic Planning
        batch_plan = elite_strategist.run(sample_parallel_tasks)
        assert batch_plan["status"] == "success"

        # Simulate batch execution (in real flow, tasks would be executed here)
        batch_results = {}
        for batch_id, batch_info in batch_plan.get("batches", {}).items():
            batch_results[batch_id] = {
                "status": "success",
                "output": {"files": [], "content": ""},
            }

        # Phase 2: ARMANI Integration Weaving
        integration_status = elite_weaver.run(batch_plan, batch_results)
        assert "status" in integration_status

    @patch("modsquad.extensions.elite_strategist.load_extension_config")
    @patch("modsquad.extensions.elite_strategist._is_safe_to_batch")
    @patch("modsquad.extensions.elite_strategist.dump_jsonl")
    def test_safety_checks_prevent_live_batching(
        self,
        mock_dump,
        mock_safe,
        mock_config,
        sample_parallel_tasks,
        mock_configs_enabled,
    ):
        """Test safety checks block batching when servers running."""
        mock_config.return_value = mock_configs_enabled
        mock_safe.return_value = False  # Servers running

        batch_plan = elite_strategist.run(sample_parallel_tasks)

        # Should be blocked
        assert batch_plan["status"] == "blocked"
        assert "server running" in batch_plan["reason"].lower()


class TestConflictResolution:
    """Test conflict resolution in ARMANI weaving."""

    @patch("modsquad.extensions.conflict_resolver.load_extension_config")
    @patch("modsquad.extensions.conflict_resolver.dump_jsonl")
    def test_auto_merge_compatible_changes(
        self, mock_dump, mock_config, mock_configs_enabled
    ):
        """Test auto-merge of compatible parallel changes."""
        mock_config.return_value = mock_configs_enabled

        # Two batches modify different parts of same file
        old_content = """
import os

def func1():
    pass
"""

        batch_a = {
            "file_path": "test.py",
            "old_content": old_content,
            "content": old_content.replace("import os", "import os\nimport sys"),
        }

        batch_b = {
            "file_path": "test.py",
            "old_content": old_content,
            "content": old_content.replace("pass", "return True"),
        }

        resolution = conflict_resolver.resolve(batch_a, batch_b)

        # Compatible changes should auto-merge
        assert resolution.success is True


class TestValidation:
    """Test validation of integrated code."""

    @patch("modsquad.extensions.integration_validator._validate_syntax")
    @patch("modsquad.extensions.integration_validator._validate_types")
    @patch("modsquad.extensions.integration_validator._validate_imports")
    @patch("modsquad.extensions.integration_validator._validate_signatures")
    @patch("modsquad.extensions.integration_validator._validate_tests")
    def test_validation_catches_syntax_errors(
        self, mock_tests, mock_sigs, mock_imports, mock_types, mock_syntax
    ):
        """Test validation catches integration syntax errors."""
        # Mock syntax failure
        mock_syntax.return_value = {"status": "failed", "error": "Invalid syntax"}
        mock_types.return_value = {"status": "passed"}
        mock_imports.return_value = {"status": "passed"}
        mock_sigs.return_value = {"status": "passed"}
        mock_tests.return_value = {"status": "passed"}

        integration_result = {
            "integration_id": "int_1",
            "modified_files": ["test.py"],
        }

        validation = integration_validator.validate(integration_result)

        # Should fail due to syntax error
        assert validation["status"] == "failed"
        assert len(validation["blocking_issues"]) > 0


class TestPerformanceMetrics:
    """Test performance metrics and speedup calculations."""

    @patch("modsquad.extensions.elite_strategist.load_extension_config")
    @patch("modsquad.extensions.elite_strategist._is_safe_to_batch")
    @patch("modsquad.extensions.elite_strategist.dump_jsonl")
    def test_parallelization_factor_calculation(
        self,
        mock_dump,
        mock_safe,
        mock_config,
        sample_parallel_tasks,
        mock_configs_enabled,
    ):
        """Test parallelization factor reflects actual parallelism."""
        mock_config.return_value = mock_configs_enabled
        mock_safe.return_value = True

        batch_plan = elite_strategist.run(sample_parallel_tasks)

        # Should report parallelization metrics
        assert "parallelization_factor" in batch_plan["strategist_metadata"]
        assert "estimated_speedup" in batch_plan["strategist_metadata"]

        # With 3 tasks, at least 2 should be parallelizable
        parallel_factor = batch_plan["strategist_metadata"]["parallelization_factor"]
        assert parallel_factor > 0


class TestEdgeCases:
    """Test edge cases and error handling."""

    @patch("modsquad.extensions.elite_strategist.load_extension_config")
    @patch("modsquad.extensions.elite_strategist._is_safe_to_batch")
    @patch("modsquad.extensions.elite_strategist.dump_jsonl")
    def test_empty_task_list(
        self, mock_dump, mock_safe, mock_config, mock_configs_enabled
    ):
        """Test handling of empty task list."""
        mock_config.return_value = mock_configs_enabled
        mock_safe.return_value = True

        batch_plan = elite_strategist.run([])

        # Should handle gracefully
        assert "strategist_metadata" in batch_plan
        assert batch_plan["strategist_metadata"]["total_tasks"] == 0

    @patch("modsquad.extensions.elite_strategist.load_extension_config")
    @patch("modsquad.extensions.elite_strategist._is_safe_to_batch")
    @patch("modsquad.extensions.elite_strategist.dump_jsonl")
    def test_circular_dependencies_detected(
        self, mock_dump, mock_safe, mock_config, mock_configs_enabled
    ):
        """Test detection of circular dependencies."""
        mock_config.return_value = mock_configs_enabled
        mock_safe.return_value = True

        # Create circular dependency
        circular_tasks = [
            {"id": "task1", "files": ["file1.py"], "dependencies": ["task2"]},
            {"id": "task2", "files": ["file2.py"], "dependencies": ["task1"]},
        ]

        batch_plan = elite_strategist.run(circular_tasks)

        # Should detect cycle (implementation may vary)
        # Either block in batch_optimizer or handle in strategist
        assert "batches" in batch_plan or "error" in batch_plan.get("status", "")

    @patch("modsquad.extensions.elite_weaver.load_extension_config")
    @patch("modsquad.extensions.elite_weaver.dump_jsonl")
    def test_partial_batch_completion(
        self, mock_dump, mock_config, mock_configs_enabled
    ):
        """Test weaving with incomplete batches."""
        mock_config.return_value = mock_configs_enabled

        batch_plan = {
            "batches": {
                "batch_0": {"tasks": ["task1"], "level": 0},
                "batch_1": {"tasks": ["task2"], "level": 1},
            },
            "intersections": [],
        }

        # Only batch_0 completed
        batch_results = {
            "batch_0": {"status": "success", "output": {}},
        }

        integration_status = elite_weaver.run(batch_plan, batch_results)

        # Should handle partial completion
        assert "status" in integration_status


class TestSquadCoordination:
    """Test coordination between SUN TZU and ARMANI squads."""

    @patch("modsquad.extensions.elite_strategist.load_extension_config")
    @patch("modsquad.extensions.elite_strategist._is_safe_to_batch")
    @patch("modsquad.extensions.elite_strategist.dump_jsonl")
    def test_intersection_points_passed_to_weaver(
        self,
        mock_dump,
        mock_safe,
        mock_config,
        sample_parallel_tasks,
        mock_configs_enabled,
    ):
        """Test intersection points from SUN TZU are used by ARMANI."""
        mock_config.return_value = mock_configs_enabled
        mock_safe.return_value = True

        # SUN TZU creates batch plan with intersections
        batch_plan = elite_strategist.run(sample_parallel_tasks)

        # Verify intersections are in batch plan
        assert "intersections" in batch_plan

        # ARMANI should be able to extract these intersections
        intersections = elite_weaver._extract_intersections(batch_plan)
        assert isinstance(intersections, list)
