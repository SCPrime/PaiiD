"""Unit tests for Task Graph Analyzer - SUN TZU Squad.

Tests dependency tree building from file imports and function calls.
"""

import ast
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open, Mock
from modsquad.extensions import task_graph_analyzer


@pytest.fixture
def sample_tasks():
    """Sample task list with file dependencies."""
    return [
        {
            "id": "task1",
            "description": "Create auth module",
            "files": ["backend/app/routers/auth.py"],
            "dependencies": [],
        },
        {
            "id": "task2",
            "description": "Create user model",
            "files": ["backend/app/models/user.py"],
            "dependencies": [],
        },
        {
            "id": "task3",
            "description": "Update main app",
            "files": ["backend/app/main.py"],
            "dependencies": ["task1"],
        },
    ]


@pytest.fixture
def python_file_with_imports():
    """Sample Python file content with imports."""
    return """
import os
import sys
from pathlib import Path
from typing import Any, Dict
from app.routers import auth
from app.models.user import User

def main():
    pass
"""


@pytest.fixture
def python_file_without_imports():
    """Sample Python file without imports."""
    return """
def simple_function():
    return 42
"""


class TestAnalyze:
    """Test the main analyze() function."""

    def test_analyze_simple_dependencies(self, sample_tasks):
        """Test dependency graph creation with simple task list."""
        result = task_graph_analyzer.analyze(sample_tasks)

        assert isinstance(result, dict)
        assert "task1" in result
        assert "task2" in result
        assert "task3" in result

        # task3 explicitly depends on task1
        assert "task1" in result["task3"]

    def test_analyze_empty_task_list(self):
        """Test analyze with empty task list."""
        result = task_graph_analyzer.analyze([])

        assert result == {}

    @patch("modsquad.extensions.task_graph_analyzer._extract_imports")
    def test_analyze_with_import_dependencies(self, mock_extract):
        """Test dependency detection via import analysis."""
        # Setup: task2 imports from task1's file
        mock_extract.side_effect = lambda file: (
            ["app.routers.auth"] if "main.py" in file else []
        )

        tasks = [
            {
                "id": "task1",
                "files": ["app/routers/auth.py"],
                "dependencies": [],
            },
            {
                "id": "task2",
                "files": ["app/main.py"],
                "dependencies": [],
            },
        ]

        result = task_graph_analyzer.analyze(tasks)

        # task2 should depend on task1 because it imports auth
        assert "task1" in result["task2"]

    def test_analyze_explicit_dependencies_preserved(self):
        """Test that explicit dependencies are preserved."""
        tasks = [
            {
                "id": "task1",
                "files": ["file1.py"],
                "dependencies": [],
            },
            {
                "id": "task2",
                "files": ["file2.py"],
                "dependencies": ["task1"],
            },
        ]

        result = task_graph_analyzer.analyze(tasks)

        assert "task1" in result["task2"]

    def test_analyze_no_self_dependencies(self):
        """Test that tasks don't depend on themselves."""
        tasks = [
            {
                "id": "task1",
                "files": ["file1.py", "file2.py"],
                "dependencies": [],
            },
        ]

        result = task_graph_analyzer.analyze(tasks)

        assert "task1" not in result["task1"]


class TestExtractImports:
    """Test import extraction from Python files."""

    def test_extract_imports_python_file(self, tmp_path, python_file_with_imports):
        """Test extracting imports from valid Python file."""
        test_file = tmp_path / "test.py"
        test_file.write_text(python_file_with_imports)

        result = task_graph_analyzer._extract_imports(str(test_file))

        assert "os" in result
        assert "sys" in result
        assert "pathlib" in result
        assert "typing" in result
        assert "app.routers" in result
        assert "app.models.user" in result

    def test_extract_imports_no_imports(self, tmp_path, python_file_without_imports):
        """Test extracting imports from file without imports."""
        test_file = tmp_path / "test.py"
        test_file.write_text(python_file_without_imports)

        result = task_graph_analyzer._extract_imports(str(test_file))

        assert result == []

    def test_extract_imports_nonexistent_file(self):
        """Test handling of non-existent file."""
        result = task_graph_analyzer._extract_imports("nonexistent.py")

        assert result == []

    def test_extract_imports_non_python_file(self, tmp_path):
        """Test handling of non-Python file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Not Python code")

        result = task_graph_analyzer._extract_imports(str(test_file))

        assert result == []

    def test_extract_imports_invalid_syntax(self, tmp_path):
        """Test handling of invalid Python syntax (fallback to regex)."""
        test_file = tmp_path / "invalid.py"
        test_file.write_text("import os\ninvalid syntax here @#$%")

        # Should fall back to regex-based extraction
        result = task_graph_analyzer._extract_imports(str(test_file))

        # Regex should still find 'import os'
        assert "os" in result

    def test_extract_imports_various_styles(self, tmp_path):
        """Test extraction of various import styles."""
        content = """
import module1
import module2, module3
from package1 import func1
from package2.subpackage import Class1, Class2
from . import relative
from .. import parent_relative
"""
        test_file = tmp_path / "imports.py"
        test_file.write_text(content)

        result = task_graph_analyzer._extract_imports(str(test_file))

        assert "module1" in result
        assert "module2" in result
        assert "package1" in result
        assert "package2.subpackage" in result


class TestExtractImportsRegex:
    """Test regex-based import extraction fallback."""

    def test_extract_imports_regex_basic(self, tmp_path):
        """Test regex extraction with basic imports."""
        content = """
import os
import sys
from pathlib import Path
"""
        test_file = tmp_path / "test.py"
        test_file.write_text(content)

        result = task_graph_analyzer._extract_imports_regex(str(test_file))

        assert "os" in result
        assert "sys" in result
        assert "pathlib" in result

    def test_extract_imports_regex_complex(self, tmp_path):
        """Test regex extraction with complex imports."""
        content = """
from app.routers.auth import router as auth_router
from app.models.user import User, UserCreate
import backend.config
"""
        test_file = tmp_path / "test.py"
        test_file.write_text(content)

        result = task_graph_analyzer._extract_imports_regex(str(test_file))

        assert "app.routers.auth" in result
        assert "app.models.user" in result
        assert "backend.config" in result

    def test_extract_imports_regex_nonexistent_file(self):
        """Test regex extraction with non-existent file."""
        result = task_graph_analyzer._extract_imports_regex("nonexistent.py")

        assert result == []

    def test_extract_imports_regex_multiline_imports(self, tmp_path):
        """Test regex extraction handles single-line imports only."""
        content = """
import module1
from package import (
    Class1,
    Class2
)
import module2
"""
        test_file = tmp_path / "test.py"
        test_file.write_text(content)

        result = task_graph_analyzer._extract_imports_regex(str(test_file))

        assert "module1" in result
        assert "module2" in result
        # Multiline imports might not be fully captured by simple regex


class TestComplexDependencies:
    """Test complex dependency scenarios."""

    @patch("modsquad.extensions.task_graph_analyzer._extract_imports")
    def test_circular_detection_not_in_scope(self, mock_extract):
        """Test that circular dependencies are detected (graph has them)."""
        # Note: The analyzer doesn't prevent circular deps, just builds the graph
        mock_extract.return_value = []

        tasks = [
            {
                "id": "task1",
                "files": ["file1.py"],
                "dependencies": ["task2"],
            },
            {
                "id": "task2",
                "files": ["file2.py"],
                "dependencies": ["task1"],
            },
        ]

        result = task_graph_analyzer.analyze(tasks)

        # Both should reference each other
        assert "task2" in result["task1"]
        assert "task1" in result["task2"]

    def test_multiple_files_per_task(self):
        """Test tasks with multiple files."""
        tasks = [
            {
                "id": "task1",
                "files": ["file1.py", "file2.py", "file3.py"],
                "dependencies": [],
            },
        ]

        result = task_graph_analyzer.analyze(tasks)

        assert "task1" in result
        assert isinstance(result["task1"], list)

    def test_overlapping_files(self):
        """Test tasks that modify overlapping files."""
        tasks = [
            {
                "id": "task1",
                "files": ["shared.py"],
                "dependencies": [],
            },
            {
                "id": "task2",
                "files": ["shared.py"],
                "dependencies": [],
            },
        ]

        result = task_graph_analyzer.analyze(tasks)

        # No automatic dependency from file overlap
        # (that's handled by risk_profiler)
        assert "task1" in result
        assert "task2" in result


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_missing_id_field(self):
        """Test handling of tasks without ID field."""
        tasks = [
            {
                "description": "No ID task",
                "files": ["file.py"],
                "dependencies": [],
            },
        ]

        result = task_graph_analyzer.analyze(tasks)

        assert "unknown" in result

    def test_missing_files_field(self):
        """Test handling of tasks without files field."""
        tasks = [
            {
                "id": "task1",
                "description": "No files",
                "dependencies": [],
            },
        ]

        result = task_graph_analyzer.analyze(tasks)

        assert "task1" in result
        assert result["task1"] == []

    def test_missing_dependencies_field(self):
        """Test handling of tasks without dependencies field."""
        tasks = [
            {
                "id": "task1",
                "files": ["file.py"],
            },
        ]

        result = task_graph_analyzer.analyze(tasks)

        assert "task1" in result
        assert result["task1"] == []

    def test_unicode_in_files(self, tmp_path):
        """Test handling of unicode characters in file paths."""
        test_file = tmp_path / "файл.py"
        test_file.write_text("import os")

        result = task_graph_analyzer._extract_imports(str(test_file))

        assert "os" in result
