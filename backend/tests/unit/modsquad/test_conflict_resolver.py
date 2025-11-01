"""Unit tests for Conflict Resolver - ARMANI Squad.

Tests auto-merge strategies for parallel modifications.
"""

import pytest
from modsquad.extensions import conflict_resolver
from modsquad.extensions.conflict_resolver import (
    Resolution,
    ResolutionStrategy,
    ChangeType,
)
from unittest.mock import patch


@pytest.fixture
def sample_old_content():
    """Original file content."""
    return """
import os
import sys

def existing_function():
    pass
"""


@pytest.fixture
def sample_content_a():
    """Changes from batch A - adds import."""
    return """
import os
import sys
from pathlib import Path

def existing_function():
    pass
"""


@pytest.fixture
def sample_content_b():
    """Changes from batch B - adds different import."""
    return """
import os
import sys
from typing import Any

def existing_function():
    pass
"""


@pytest.fixture
def mock_config_enabled():
    """Mock configuration."""
    return {"conflict_resolver": {"enabled": True}}


class TestResolve:
    """Test the main resolve() function."""

    @patch("modsquad.extensions.conflict_resolver.load_extension_config")
    @patch("modsquad.extensions.conflict_resolver.dump_jsonl")
    def test_resolve_auto_merge_imports(
        self,
        mock_dump,
        mock_config,
        sample_old_content,
        sample_content_a,
        sample_content_b,
        mock_config_enabled,
    ):
        """Test auto-merge of import statements."""
        mock_config.return_value = mock_config_enabled

        batch_a = {
            "file_path": "test.py",
            "old_content": sample_old_content,
            "content": sample_content_a,
        }
        batch_b = {
            "file_path": "test.py",
            "old_content": sample_old_content,
            "content": sample_content_b,
        }

        result = conflict_resolver.resolve(batch_a, batch_b)

        assert isinstance(result, Resolution)
        assert result.success is True
        # Imports can be auto-merged
        assert result.strategy in [
            ResolutionStrategy.AUTO_MERGE,
            ResolutionStrategy.THREE_WAY_MERGE,
        ]

    @patch("modsquad.extensions.conflict_resolver.load_extension_config")
    def test_resolve_disabled(
        self, mock_config, sample_old_content, sample_content_a, sample_content_b
    ):
        """Test disabled returns fail strategy."""
        mock_config.return_value = {"conflict_resolver": {"enabled": False}}

        batch_a = {
            "file_path": "test.py",
            "old_content": sample_old_content,
            "content": sample_content_a,
        }
        batch_b = {
            "file_path": "test.py",
            "old_content": sample_old_content,
            "content": sample_content_b,
        }

        result = conflict_resolver.resolve(batch_a, batch_b)

        assert result.success is False
        assert result.strategy == ResolutionStrategy.FAIL


class TestConflictTypes:
    """Test different conflict types."""

    @patch("modsquad.extensions.conflict_resolver.load_extension_config")
    @patch("modsquad.extensions.conflict_resolver.dump_jsonl")
    def test_resolve_same_line_modification(
        self, mock_dump, mock_config, mock_config_enabled
    ):
        """Test conflict when same line modified."""
        mock_config.return_value = mock_config_enabled

        old = "value = 10"
        content_a = "value = 20"
        content_b = "value = 30"

        batch_a = {"file_path": "test.py", "old_content": old, "content": content_a}
        batch_b = {"file_path": "test.py", "old_content": old, "content": content_b}

        result = conflict_resolver.resolve(batch_a, batch_b)

        # Same line modification should require manual review
        assert result.manual_review_required is True

    @patch("modsquad.extensions.conflict_resolver.load_extension_config")
    @patch("modsquad.extensions.conflict_resolver.dump_jsonl")
    def test_resolve_non_overlapping_changes(
        self, mock_dump, mock_config, mock_config_enabled
    ):
        """Test auto-merge of non-overlapping changes."""
        mock_config.return_value = mock_config_enabled

        old = """
def func1():
    pass

def func2():
    pass
"""
        content_a = """
def func1():
    return 1

def func2():
    pass
"""
        content_b = """
def func1():
    pass

def func2():
    return 2
"""

        batch_a = {"file_path": "test.py", "old_content": old, "content": content_a}
        batch_b = {"file_path": "test.py", "old_content": old, "content": content_b}

        result = conflict_resolver.resolve(batch_a, batch_b)

        # Non-overlapping changes should auto-merge or three-way merge
        assert result.strategy in [
            ResolutionStrategy.AUTO_MERGE,
            ResolutionStrategy.THREE_WAY_MERGE,
        ]


class TestEdgeCases:
    """Test edge cases."""

    @patch("modsquad.extensions.conflict_resolver.load_extension_config")
    @patch("modsquad.extensions.conflict_resolver.dump_jsonl")
    def test_resolve_identical_changes(
        self, mock_dump, mock_config, mock_config_enabled
    ):
        """Test resolution when both batches make identical changes."""
        mock_config.return_value = mock_config_enabled

        old = "value = 10"
        new = "value = 20"  # Same change in both batches

        batch_a = {"file_path": "test.py", "old_content": old, "content": new}
        batch_b = {"file_path": "test.py", "old_content": old, "content": new}

        result = conflict_resolver.resolve(batch_a, batch_b)

        # Identical changes should auto-merge
        assert result.success is True

    @patch("modsquad.extensions.conflict_resolver.load_extension_config")
    @patch("modsquad.extensions.conflict_resolver.dump_jsonl")
    def test_resolve_empty_changes(self, mock_dump, mock_config, mock_config_enabled):
        """Test with no actual changes."""
        mock_config.return_value = mock_config_enabled

        content = "unchanged content"

        batch_a = {"file_path": "test.py", "old_content": content, "content": content}
        batch_b = {"file_path": "test.py", "old_content": content, "content": content}

        result = conflict_resolver.resolve(batch_a, batch_b)

        assert result.success is True
        assert len(result.conflicts) == 0
