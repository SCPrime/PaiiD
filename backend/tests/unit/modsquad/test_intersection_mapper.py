"""Unit tests for Intersection Mapper - SUN TZU Squad.

Tests pre-identification of exact merge points for batch weaving.
"""

import pytest
from unittest.mock import patch
from modsquad.extensions import intersection_mapper


@pytest.fixture
def sample_batch_plan():
    """Sample batch plan."""
    return {
        "batches": {
            "batch_0": {
                "tasks": ["task1", "task2"],
                "level": 0,
                "files": ["backend/app/routers/auth.py", "backend/app/models/user.py"],
            },
            "batch_1": {
                "tasks": ["task3"],
                "level": 1,
                "files": ["backend/app/main.py"],
            },
            "batch_2": {
                "tasks": ["task4"],
                "level": 0,
                "files": ["backend/app/routers/auth.py"],  # Overlaps with batch_0
            },
        },
    }


@pytest.fixture
def sample_dependency_graph():
    """Sample dependency graph."""
    return {
        "task1": [],
        "task2": [],
        "task3": ["task1"],
        "task4": [],
    }


@pytest.fixture
def mock_config_enabled():
    """Mock configuration."""
    return {"intersection_mapper": {"enabled": True}}


class TestMapIntersections:
    """Test the main map_intersections() function."""

    @patch("modsquad.extensions.intersection_mapper.load_extension_config")
    @patch("modsquad.extensions.intersection_mapper.dump_jsonl")
    def test_map_intersections_success(
        self, mock_dump, mock_config, sample_batch_plan, sample_dependency_graph, mock_config_enabled
    ):
        """Test successful intersection mapping."""
        mock_config.return_value = mock_config_enabled

        result = intersection_mapper.map_intersections(
            sample_batch_plan, sample_dependency_graph
        )

        assert isinstance(result, list)
        assert len(result) > 0

    @patch("modsquad.extensions.intersection_mapper.load_extension_config")
    def test_map_intersections_disabled(
        self, mock_config, sample_batch_plan, sample_dependency_graph
    ):
        """Test returns empty list when disabled."""
        mock_config.return_value = {"intersection_mapper": {"enabled": False}}

        result = intersection_mapper.map_intersections(
            sample_batch_plan, sample_dependency_graph
        )

        assert result == []

    @patch("modsquad.extensions.intersection_mapper.load_extension_config")
    @patch("modsquad.extensions.intersection_mapper.dump_jsonl")
    def test_map_intersections_file_merge_detected(
        self, mock_dump, mock_config, sample_batch_plan, sample_dependency_graph, mock_config_enabled
    ):
        """Test file merge intersection detection."""
        mock_config.return_value = mock_config_enabled

        result = intersection_mapper.map_intersections(
            sample_batch_plan, sample_dependency_graph
        )

        # Should detect file merge for auth.py
        file_merges = [i for i in result if i["type"] == "file_merge"]
        assert len(file_merges) > 0

        auth_merge = [i for i in file_merges if "auth.py" in i["location"]]
        assert len(auth_merge) > 0


class TestBuildBatchFileMapping:
    """Test batch file mapping construction."""

    def test_build_batch_file_mapping(self, sample_batch_plan):
        """Test file to batch mapping."""
        result = intersection_mapper._build_batch_file_mapping(sample_batch_plan)

        assert "backend/app/routers/auth.py" in result
        assert "batch_0" in result["backend/app/routers/auth.py"]
        assert "batch_2" in result["backend/app/routers/auth.py"]

    def test_build_batch_file_mapping_unique_files(self):
        """Test mapping with unique files."""
        batch_plan = {
            "batches": {
                "batch_0": {"files": ["file1.py"]},
                "batch_1": {"files": ["file2.py"]},
            }
        }

        result = intersection_mapper._build_batch_file_mapping(batch_plan)

        assert result["file1.py"] == ["batch_0"]
        assert result["file2.py"] == ["batch_1"]


class TestBuildBatchDependencies:
    """Test batch dependency mapping."""

    def test_build_batch_dependencies(self, sample_batch_plan, sample_dependency_graph):
        """Test batch dependency construction from task dependencies."""
        result = intersection_mapper._build_batch_dependencies(
            sample_batch_plan, sample_dependency_graph
        )

        # task3 depends on task1, so batch_1 depends on batch_0
        assert "batch_0" in result["batch_1"]

    def test_build_batch_dependencies_no_deps(self):
        """Test with no dependencies."""
        batch_plan = {
            "batches": {
                "batch_0": {"tasks": ["task1"]},
                "batch_1": {"tasks": ["task2"]},
            }
        }
        dependency_graph = {"task1": [], "task2": []}

        result = intersection_mapper._build_batch_dependencies(batch_plan, dependency_graph)

        assert result == {}


class TestAnalyzeFileIntersections:
    """Test file-level intersection analysis."""

    def test_analyze_file_intersections_merge_required(self):
        """Test detection of file merge intersection."""
        batch_files = {
            "file.py": ["batch_0", "batch_1"],
        }
        batch_deps = {}

        result = intersection_mapper._analyze_file_intersections(
            "file.py", "batch_0", 0, batch_files, batch_deps
        )

        assert len(result) == 1
        assert result[0]["type"] == "file_merge"
        assert result[0]["requires_conflict_resolution"] is True

    def test_analyze_file_intersections_no_overlap(self):
        """Test no intersection for unique file."""
        batch_files = {
            "file.py": ["batch_0"],
        }
        batch_deps = {}

        result = intersection_mapper._analyze_file_intersections(
            "file.py", "batch_0", 0, batch_files, batch_deps
        )

        assert len(result) == 0


class TestAnalyzeImportIntersections:
    """Test import chain intersection analysis."""

    def test_analyze_import_intersections_detected(self):
        """Test detection of import chain intersections."""
        batch_deps = {"batch_1": ["batch_0"]}
        batches = {
            "batch_0": {"files": ["app/module.py"]},
            "batch_1": {"files": ["app/main.py"]},
        }

        result = intersection_mapper._analyze_import_intersections(
            "batch_1", 1, ["task1"], batch_deps, batches
        )

        assert len(result) > 0
        assert result[0]["type"] == "import_chain"

    def test_analyze_import_intersections_no_deps(self):
        """Test no intersections without dependencies."""
        batch_deps = {}
        batches = {}

        result = intersection_mapper._analyze_import_intersections(
            "batch_0", 0, [], batch_deps, batches
        )

        assert len(result) == 0


class TestAnalyzeHandoffIntersections:
    """Test function handoff intersection analysis."""

    def test_analyze_handoff_intersections_detected(self):
        """Test detection of function handoff intersections."""
        batch_deps = {"batch_1": ["batch_0"]}
        batches = {
            "batch_0": {"level": 0},
            "batch_1": {"level": 1},
        }

        result = intersection_mapper._analyze_handoff_intersections(
            "batch_0", 0, [], batch_deps, batches
        )

        assert len(result) > 0
        assert result[0]["type"] == "function_handoff"
        assert result[0]["source_batch"] == "batch_0"
        assert result[0]["target_batch"] == "batch_1"

    def test_analyze_handoff_intersections_same_level(self):
        """Test no handoff for same-level batches."""
        batch_deps = {"batch_1": ["batch_0"]}
        batches = {
            "batch_0": {"level": 0},
            "batch_1": {"level": 0},  # Same level
        }

        result = intersection_mapper._analyze_handoff_intersections(
            "batch_0", 0, [], batch_deps, batches
        )

        # Should not create handoff for same-level batches
        assert len(result) == 0


class TestDeduplication:
    """Test intersection deduplication."""

    def test_deduplicate_intersections(self):
        """Test deduplication of identical intersections."""
        intersections = [
            {
                "type": "file_merge",
                "source_batch": "batch_0",
                "target_batch": "batch_1",
                "location": "file.py",
            },
            {
                "type": "file_merge",
                "source_batch": "batch_0",
                "target_batch": "batch_1",
                "location": "file.py",
            },
            {
                "type": "import_chain",
                "source_batch": "batch_0",
                "target_batch": "batch_1",
                "location": "module.py",
            },
        ]

        result = intersection_mapper._deduplicate_intersections(intersections)

        assert len(result) == 2  # Duplicate file_merge removed

    def test_deduplicate_intersections_all_unique(self):
        """Test deduplication with all unique intersections."""
        intersections = [
            {
                "type": "file_merge",
                "source_batch": "batch_0",
                "target_batch": "batch_1",
                "location": "file1.py",
            },
            {
                "type": "file_merge",
                "source_batch": "batch_0",
                "target_batch": "batch_1",
                "location": "file2.py",
            },
        ]

        result = intersection_mapper._deduplicate_intersections(intersections)

        assert len(result) == 2  # All unique


class TestPrioritization:
    """Test intersection prioritization."""

    def test_prioritize_intersections_by_priority(self):
        """Test sorting by priority level."""
        intersections = [
            {"type": "import", "priority": "low", "level": 0},
            {"type": "merge", "priority": "high", "level": 0},
            {"type": "handoff", "priority": "medium", "level": 0},
        ]

        result = intersection_mapper._prioritize_intersections(intersections)

        assert result[0]["priority"] == "high"
        assert result[1]["priority"] == "medium"
        assert result[2]["priority"] == "low"

    def test_prioritize_intersections_by_level(self):
        """Test sorting by level when priority equal."""
        intersections = [
            {"type": "a", "priority": "high", "level": 2},
            {"type": "b", "priority": "high", "level": 0},
            {"type": "c", "priority": "high", "level": 1},
        ]

        result = intersection_mapper._prioritize_intersections(intersections)

        assert result[0]["level"] == 0
        assert result[1]["level"] == 1
        assert result[2]["level"] == 2

    def test_prioritize_intersections_conflict_resolution(self):
        """Test conflict resolution flag affects priority."""
        intersections = [
            {
                "type": "a",
                "priority": "high",
                "level": 0,
                "requires_conflict_resolution": False,
            },
            {
                "type": "b",
                "priority": "high",
                "level": 0,
                "requires_conflict_resolution": True,
            },
        ]

        result = intersection_mapper._prioritize_intersections(intersections)

        # Conflict resolution required should come first
        assert result[0]["requires_conflict_resolution"] is True


class TestEdgeCases:
    """Test edge cases."""

    @patch("modsquad.extensions.intersection_mapper.load_extension_config")
    def test_map_intersections_empty_batches(self, mock_config, mock_config_enabled):
        """Test with empty batch plan."""
        mock_config.return_value = mock_config_enabled

        batch_plan = {"batches": {}}
        dependency_graph = {}

        result = intersection_mapper.map_intersections(batch_plan, dependency_graph)

        assert result == []

    @patch("modsquad.extensions.intersection_mapper.load_extension_config")
    @patch("modsquad.extensions.intersection_mapper.dump_jsonl")
    def test_map_intersections_no_overlaps(
        self, mock_dump, mock_config, mock_config_enabled
    ):
        """Test with no file overlaps."""
        mock_config.return_value = mock_config_enabled

        batch_plan = {
            "batches": {
                "batch_0": {"tasks": ["task1"], "level": 0, "files": ["file1.py"]},
                "batch_1": {"tasks": ["task2"], "level": 0, "files": ["file2.py"]},
            }
        }
        dependency_graph = {"task1": [], "task2": []}

        result = intersection_mapper.map_intersections(batch_plan, dependency_graph)

        # Should have no file merge intersections
        file_merges = [i for i in result if i["type"] == "file_merge"]
        assert len(file_merges) == 0
