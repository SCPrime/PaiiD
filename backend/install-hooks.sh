#!/bin/bash

# ====================================
# PAIID BACKEND PRE-COMMIT HOOKS INSTALLER
# ====================================
# This script installs pre-commit hooks for the Python backend
#
# Usage:
#   bash install-hooks.sh
#
# What it does:
#   1. Installs pre-commit package (if not already installed)
#   2. Installs the git hooks from .pre-commit-config.yaml
#   3. Runs hooks on all files to verify setup
#
# Requirements:
#   - Python 3.11+
#   - pip

set -e

echo "🔧 PaiiD Backend Pre-commit Hooks Installation"
echo "=============================================="
echo ""

# Check if we're in the backend directory
if [ ! -f "pyproject.toml" ] || [ ! -f ".pre-commit-config.yaml" ]; then
  echo "❌ Error: Must run from backend/ directory"
  echo "   Current directory: $(pwd)"
  echo ""
  echo "Usage:"
  echo "   cd backend"
  echo "   bash install-hooks.sh"
  exit 1
fi

echo "📦 Step 1: Installing pre-commit package..."
echo ""

# Check if pre-commit is already installed
if pip show pre-commit > /dev/null 2>&1; then
  echo "✅ pre-commit already installed: $(pip show pre-commit | grep Version)"
else
  echo "📥 Installing pre-commit..."
  pip install pre-commit
  echo "✅ pre-commit installed successfully"
fi

echo ""
echo "🔗 Step 2: Installing git hooks..."
echo ""

# Install the hooks from .pre-commit-config.yaml
pre-commit install

echo ""
echo "🧪 Step 3: Running hooks on sample files (dry run)..."
echo ""

# Run on a few files to test (not all files - that would be slow)
# Find a few Python files to test
SAMPLE_FILES=$(find app -name "*.py" -type f | head -5)

if [ -n "$SAMPLE_FILES" ]; then
  echo "Testing on sample files:"
  echo "$SAMPLE_FILES" | sed 's/^/  - /'
  echo ""

  # Run hooks on sample files
  if pre-commit run --files $SAMPLE_FILES; then
    echo ""
    echo "✅ Sample validation passed!"
  else
    echo ""
    echo "⚠️  Some hooks made changes or found issues."
    echo "   This is normal - the hooks will auto-fix most issues."
  fi
else
  echo "⏭️  No Python files found to test"
fi

echo ""
echo "=============================================="
echo "✅ Backend Pre-commit Hooks Installed!"
echo "=============================================="
echo ""
echo "📋 What happens now:"
echo ""
echo "  1. Every time you commit Python code, hooks will run automatically"
echo "  2. Black will format your code (100 char lines)"
echo "  3. Ruff will lint and fix common issues"
echo "  4. Files will be auto-formatted to match project standards"
echo ""
echo "🔧 Manual commands:"
echo ""
echo "  # Run hooks on all files (slow, use sparingly):"
echo "  pre-commit run --all-files"
echo ""
echo "  # Run hooks on specific files:"
echo "  pre-commit run --files app/main.py app/routers/health.py"
echo ""
echo "  # Update hook versions:"
echo "  pre-commit autoupdate"
echo ""
echo "  # Bypass hooks for one commit (NOT recommended):"
echo "  SKIP_HOOKS=1 git commit -m \"message\""
echo "  git commit --no-verify -m \"message\""
echo ""
echo "✅ Done! Your backend now has automated code quality checks."
echo ""
