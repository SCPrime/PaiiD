"""Task Graph Analyzer - Builds dependency trees from file imports and function calls.

Part of SUN TZU Squad for strategic batch planning.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any


def analyze(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Analyze task dependencies by parsing Python imports and function calls.

    Args:
        tasks: List of task dicts with 'files' to analyze

    Returns:
        Dependency graph: {task_id: [dependent_task_ids]}
    """
    # Convert tasks to JSON for consistent hashing and caching
    tasks_json = json.dumps(tasks, sort_keys=True, default=str)
    return _analyze_cached(tasks_json)


@lru_cache(maxsize=128)
def _analyze_cached(tasks_json: str) -> dict[str, Any]:
    """
    Cached analysis of task dependencies.

    Args:
        tasks_json: JSON-serialized list of tasks

    Returns:
        Dependency graph: {task_id: [dependent_task_ids]}
    """
    tasks = json.loads(tasks_json)
    dependency_graph = {}
    task_file_map = {}  # Map files to tasks

    # Build file → task mapping
    for task in tasks:
        task_id = task.get("id", "unknown")
        files = task.get("files", [])
        for file_path in files:
            if file_path not in task_file_map:
                task_file_map[file_path] = []
            task_file_map[file_path].append(task_id)

    # Analyze each task's dependencies
    for task in tasks:
        task_id = task.get("id", "unknown")
        dependencies = set()

        # Parse files for imports
        for file_path in task.get("files", []):
            imported_modules = _extract_imports(file_path)

            # Check if imported modules are modified by other tasks
            for imported_module in imported_modules:
                for other_file, task_ids in task_file_map.items():
                    if imported_module in other_file and task_id not in task_ids:
                        dependencies.update(task_ids)

        # Add explicit dependencies from task definition
        explicit_deps = task.get("dependencies", [])
        dependencies.update(explicit_deps)

        dependency_graph[task_id] = list(dependencies)

    return dependency_graph


def _extract_imports(file_path: str) -> list[str]:
    """Extract import statements from Python file."""
    try:
        path = Path(file_path)
        if not path.exists() or path.suffix != ".py":
            return []

        with path.open("r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

        return imports

    except Exception:
        # Fallback: regex-based import extraction
        return _extract_imports_regex(file_path)


def _extract_imports_regex(file_path: str) -> list[str]:
    """Fallback import extraction using regex."""
    try:
        path = Path(file_path)
        if not path.exists():
            return []

        with path.open("r", encoding="utf-8") as f:
            content = f.read()

        # Match: import foo, from foo import bar
        import_pattern = r"(?:from\s+([\w.]+)\s+import|import\s+([\w.]+))"
        matches = re.findall(import_pattern, content)

        imports = []
        for match in matches:
            imports.append(match[0] or match[1])

        return imports

    except Exception:
        return []
