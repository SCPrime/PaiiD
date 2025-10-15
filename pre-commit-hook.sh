#!/bin/bash

# Pre-Commit Hook: Python Package Structure Validator
#
# This hook prevents commits that would break Python imports by:
# 1. Checking for missing __init__.py files in Python packages
# 2. Running import verification tests
# 3. Checking for common Python errors
#
# Installation:
#   cp pre-commit-hook.sh .git/hooks/pre-commit
#   chmod +x .git/hooks/pre-commit
#
# To bypass (use sparingly):
#   git commit --no-verify

set -e

echo "🔍 Running pre-commit checks..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track if any checks fail
CHECKS_FAILED=0

# ═══════════════════════════════════════════════════════════
# CHECK 1: Python Package Structure
# ═══════════════════════════════════════════════════════════

echo "📦 Checking Python package structure..."

# Find all directories in backend/app/ that contain .py files
# but don't have __init__.py

missing_init=()

if [ -d "backend/app" ]; then
    for dir in backend/app/*/; do
        if [ -d "$dir" ]; then
            # Skip __pycache__ and other special directories
            if [[ $(basename "$dir") == __* ]]; then
                continue
            fi

            # Check if directory contains .py files
            py_count=$(find "$dir" -maxdepth 1 -name "*.py" 2>/dev/null | wc -l)

            if [ "$py_count" -gt 0 ]; then
                # Check if __init__.py exists
                if [ ! -f "$dir/__init__.py" ]; then
                    missing_init+=("$dir")
                fi
            fi
        fi
    done
fi

if [ ${#missing_init[@]} -gt 0 ]; then
    echo -e "${RED}❌ FAILED: Missing __init__.py files${NC}"
    echo ""
    echo "The following directories contain Python files but are missing __init__.py:"
    for dir in "${missing_init[@]}"; do
        echo -e "  ${RED}✗${NC} $dir"
    done
    echo ""
    echo "Python requires __init__.py files to treat directories as packages."
    echo "Without them, imports will fail and the backend will crash on startup."
    echo ""
    echo "To fix this, create empty __init__.py files:"
    for dir in "${missing_init[@]}"; do
        echo "  touch ${dir}__init__.py"
    done
    echo ""
    CHECKS_FAILED=1
else
    echo -e "${GREEN}✅ PASSED: All Python packages have __init__.py${NC}"
fi

echo ""

# ═══════════════════════════════════════════════════════════
# CHECK 2: Python Syntax Errors
# ═══════════════════════════════════════════════════════════

echo "🐍 Checking Python syntax..."

# Get list of staged Python files
STAGED_PY_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$' || true)

if [ -n "$STAGED_PY_FILES" ]; then
    SYNTAX_ERRORS=0

    for file in $STAGED_PY_FILES; do
        if [ -f "$file" ]; then
            # Check syntax with python -m py_compile
            if ! python -m py_compile "$file" 2>/dev/null; then
                echo -e "${RED}❌ Syntax error in: $file${NC}"
                python -m py_compile "$file" 2>&1 | head -5
                SYNTAX_ERRORS=1
            fi
        fi
    done

    if [ $SYNTAX_ERRORS -eq 0 ]; then
        echo -e "${GREEN}✅ PASSED: No Python syntax errors${NC}"
    else
        echo -e "${RED}❌ FAILED: Python syntax errors found${NC}"
        CHECKS_FAILED=1
    fi
else
    echo -e "${YELLOW}⏭️  SKIPPED: No Python files staged${NC}"
fi

echo ""

# ═══════════════════════════════════════════════════════════
# CHECK 3: Import Verification Tests (if pytest available)
# ═══════════════════════════════════════════════════════════

echo "🧪 Running import verification tests..."

if command -v pytest &> /dev/null; then
    if [ -f "backend/tests/test_imports.py" ]; then
        # Run import tests (fast, no need to start services)
        if pytest backend/tests/test_imports.py -q --tb=line 2>/dev/null; then
            echo -e "${GREEN}✅ PASSED: Import verification tests${NC}"
        else
            echo -e "${RED}❌ FAILED: Import verification tests${NC}"
            echo ""
            echo "Running tests with verbose output:"
            pytest backend/tests/test_imports.py -v --tb=short
            CHECKS_FAILED=1
        fi
    else
        echo -e "${YELLOW}⏭️  SKIPPED: test_imports.py not found${NC}"
    fi
else
    echo -e "${YELLOW}⏭️  SKIPPED: pytest not installed${NC}"
fi

echo ""

# ═══════════════════════════════════════════════════════════
# CHECK 4: Forbidden Patterns
# ═══════════════════════════════════════════════════════════

echo "🚫 Checking for forbidden patterns..."

FORBIDDEN_FOUND=0

# Check for debugger statements
if git diff --cached | grep -E "^\+.*\b(debugger|pdb\.set_trace|breakpoint)\(" > /dev/null; then
    echo -e "${RED}❌ Found debugger statement in staged code${NC}"
    echo "Remove debugger/pdb.set_trace()/breakpoint() before committing"
    FORBIDDEN_FOUND=1
fi

# Check for hardcoded secrets (basic patterns)
if git diff --cached | grep -iE "^\+.*(password|secret|api_key|token)\s*=\s*['\"][^'\"]{8,}['\"]" > /dev/null; then
    echo -e "${YELLOW}⚠️  WARNING: Possible hardcoded secret detected${NC}"
    echo "Verify no secrets are being committed. Use environment variables instead."
    # Don't fail the commit, just warn
fi

if [ $FORBIDDEN_FOUND -eq 0 ]; then
    echo -e "${GREEN}✅ PASSED: No forbidden patterns found${NC}"
else
    CHECKS_FAILED=1
fi

echo ""

# ═══════════════════════════════════════════════════════════
# FINAL RESULT
# ═══════════════════════════════════════════════════════════

if [ $CHECKS_FAILED -eq 1 ]; then
    echo -e "${RED}═══════════════════════════════════════════════════${NC}"
    echo -e "${RED}❌ PRE-COMMIT CHECKS FAILED${NC}"
    echo -e "${RED}═══════════════════════════════════════════════════${NC}"
    echo ""
    echo "Your commit has been blocked to prevent breaking the build."
    echo ""
    echo "To fix:"
    echo "  1. Address the errors listed above"
    echo "  2. Stage your fixes: git add <files>"
    echo "  3. Try committing again"
    echo ""
    echo "To bypass (NOT recommended):"
    echo "  git commit --no-verify"
    echo ""
    exit 1
else
    echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ ALL PRE-COMMIT CHECKS PASSED${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
    echo ""
    echo "Proceeding with commit..."
    exit 0
fi
