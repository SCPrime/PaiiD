"""Unit tests for Integration Validator - ARMANI Squad.

Tests 5-layer validation of woven integrations.
"""

import pytest
from unittest.mock import patch, MagicMock
from modsquad.extensions import integration_validator


@pytest.fixture
def sample_integration_result():
    """Sample integration result."""
    return {
        "integration_id": "integration_1",
        "modified_files": [
            "backend/app/main.py",
            "backend/app/utils.py",
        ],
        "status": "success",
    }


@pytest.fixture
def mock_config_enabled():
    """Mock configuration."""
    return {"integration_validator": {"enabled": True}}


class TestValidate:
    """Test the main validate() function."""

    @patch("modsquad.extensions.integration_validator._validate_syntax")
    @patch("modsquad.extensions.integration_validator._validate_types")
    @patch("modsquad.extensions.integration_validator._validate_imports")
    @patch("modsquad.extensions.integration_validator._validate_signatures")
    @patch("modsquad.extensions.integration_validator._validate_tests")
    def test_validate_all_layers_pass(
        self,
        mock_tests,
        mock_sigs,
        mock_imports,
        mock_types,
        mock_syntax,
        sample_integration_result,
    ):
        """Test validation when all layers pass."""
        # Mock all layers passing
        mock_syntax.return_value = {"status": "passed"}
        mock_types.return_value = {"status": "passed"}
        mock_imports.return_value = {"status": "passed"}
        mock_sigs.return_value = {"status": "passed"}
        mock_tests.return_value = {"status": "passed"}

        result = integration_validator.validate(sample_integration_result)

        assert result["status"] == "passed"
        assert len(result["blocking_issues"]) == 0
        assert "layers" in result

    @patch("modsquad.extensions.integration_validator._validate_syntax")
    @patch("modsquad.extensions.integration_validator._validate_types")
    @patch("modsquad.extensions.integration_validator._validate_imports")
    @patch("modsquad.extensions.integration_validator._validate_signatures")
    @patch("modsquad.extensions.integration_validator._validate_tests")
    def test_validate_syntax_failure_blocks(
        self,
        mock_tests,
        mock_sigs,
        mock_imports,
        mock_types,
        mock_syntax,
        sample_integration_result,
    ):
        """Test syntax failure blocks integration."""
        # Syntax fails (BLOCKING)
        mock_syntax.return_value = {"status": "failed", "error": "Syntax error"}
        mock_types.return_value = {"status": "passed"}
        mock_imports.return_value = {"status": "passed"}
        mock_sigs.return_value = {"status": "passed"}
        mock_tests.return_value = {"status": "passed"}

        result = integration_validator.validate(sample_integration_result)

        assert result["status"] == "failed"
        assert "Syntax errors detected" in result["blocking_issues"]

    @patch("modsquad.extensions.integration_validator._validate_syntax")
    @patch("modsquad.extensions.integration_validator._validate_types")
    @patch("modsquad.extensions.integration_validator._validate_imports")
    @patch("modsquad.extensions.integration_validator._validate_signatures")
    @patch("modsquad.extensions.integration_validator._validate_tests")
    def test_validate_type_failure_warns(
        self,
        mock_tests,
        mock_sigs,
        mock_imports,
        mock_types,
        mock_syntax,
        sample_integration_result,
    ):
        """Test type checking failure generates warning."""
        mock_syntax.return_value = {"status": "passed"}
        mock_types.return_value = {"status": "failed", "error": "Type mismatch"}
        mock_imports.return_value = {"status": "passed"}
        mock_sigs.return_value = {"status": "passed"}
        mock_tests.return_value = {"status": "passed"}

        result = integration_validator.validate(sample_integration_result)

        # Type failure is warning, not blocking
        assert result["status"] == "passed"
        assert len(result["warnings"]) > 0
        assert any("Type checking" in w for w in result["warnings"])

    @patch("modsquad.extensions.integration_validator._validate_syntax")
    @patch("modsquad.extensions.integration_validator._validate_types")
    @patch("modsquad.extensions.integration_validator._validate_imports")
    @patch("modsquad.extensions.integration_validator._validate_signatures")
    @patch("modsquad.extensions.integration_validator._validate_tests")
    def test_validate_import_failure_blocks(
        self,
        mock_tests,
        mock_sigs,
        mock_imports,
        mock_types,
        mock_syntax,
        sample_integration_result,
    ):
        """Test import failure blocks integration."""
        mock_syntax.return_value = {"status": "passed"}
        mock_types.return_value = {"status": "passed"}
        mock_imports.return_value = {"status": "failed", "error": "Import not found"}
        mock_sigs.return_value = {"status": "passed"}
        mock_tests.return_value = {"status": "passed"}

        result = integration_validator.validate(sample_integration_result)

        assert result["status"] == "failed"
        assert "Unresolved imports" in result["blocking_issues"]


class TestValidationLayers:
    """Test individual validation layers."""

    def test_validate_syntax_valid_python(self, tmp_path):
        """Test syntax validation with valid Python."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")

        result = integration_validator._validate_syntax([str(test_file)])

        assert result["status"] == "passed"

    def test_validate_syntax_invalid_python(self, tmp_path):
        """Test syntax validation with invalid Python."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def test( invalid syntax")

        result = integration_validator._validate_syntax([str(test_file)])

        assert result["status"] == "failed"

    def test_validate_imports_existing_modules(self, tmp_path):
        """Test import validation with standard library."""
        test_file = tmp_path / "test.py"
        test_file.write_text("import os\nimport sys")

        result = integration_validator._validate_imports([str(test_file)])

        assert result["status"] == "passed"


class TestEdgeCases:
    """Test edge cases."""

    @patch("modsquad.extensions.integration_validator._validate_syntax")
    @patch("modsquad.extensions.integration_validator._validate_types")
    @patch("modsquad.extensions.integration_validator._validate_imports")
    @patch("modsquad.extensions.integration_validator._validate_signatures")
    @patch("modsquad.extensions.integration_validator._validate_tests")
    def test_validate_empty_file_list(
        self, mock_tests, mock_sigs, mock_imports, mock_types, mock_syntax
    ):
        """Test validation with no files."""
        mock_syntax.return_value = {"status": "passed"}
        mock_types.return_value = {"status": "passed"}
        mock_imports.return_value = {"status": "passed"}
        mock_sigs.return_value = {"status": "passed"}
        mock_tests.return_value = {"status": "passed"}

        integration_result = {
            "integration_id": "integration_1",
            "modified_files": [],
        }

        result = integration_validator.validate(integration_result)

        assert result["status"] == "passed"

    @patch("modsquad.extensions.integration_validator._validate_syntax")
    @patch("modsquad.extensions.integration_validator._validate_types")
    @patch("modsquad.extensions.integration_validator._validate_imports")
    @patch("modsquad.extensions.integration_validator._validate_signatures")
    @patch("modsquad.extensions.integration_validator._validate_tests")
    def test_validate_multiple_failures(
        self, mock_tests, mock_sigs, mock_imports, mock_types, mock_syntax,
        sample_integration_result
    ):
        """Test validation with multiple failures."""
        # Multiple blocking failures
        mock_syntax.return_value = {"status": "failed", "error": "Syntax error"}
        mock_types.return_value = {"status": "failed", "error": "Type error"}
        mock_imports.return_value = {"status": "failed", "error": "Import error"}
        mock_sigs.return_value = {"status": "passed"}
        mock_tests.return_value = {"status": "failed", "error": "Test failed"}

        result = integration_validator.validate(sample_integration_result)

        assert result["status"] == "failed"
        # Should have multiple blocking issues
        assert len(result["blocking_issues"]) >= 2
        # Should have warnings from non-blocking failures
        assert len(result["warnings"]) >= 1
