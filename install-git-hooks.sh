#!/bin/bash

# Install Git Hooks for PaiiD
#
# This script installs the pre-commit hook that prevents
# commits with broken Python package structures.
#
# Usage: bash install-git-hooks.sh

set -e

echo "🔧 Installing Git hooks for PaiiD..."
echo ""

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository"
    echo "Run this script from the root of the ai-Trader repository"
    exit 1
fi

# Create hooks directory if it doesn't exist
mkdir -p .git/hooks

# Install pre-commit hook
if [ -f "pre-commit-hook.sh" ]; then
    echo "📋 Installing pre-commit hook..."
    cp pre-commit-hook.sh .git/hooks/pre-commit
    chmod +x .git/hooks/pre-commit
    echo "✅ Pre-commit hook installed at .git/hooks/pre-commit"
else
    echo "❌ Error: pre-commit-hook.sh not found"
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════"
echo "✅ Git hooks installed successfully!"
echo "═══════════════════════════════════════════════════"
echo ""
echo "The pre-commit hook will now:"
echo "  1. Check for missing __init__.py files"
echo "  2. Verify Python syntax in staged files"
echo "  3. Run import verification tests"
echo "  4. Check for forbidden patterns (debugger, etc.)"
echo ""
echo "To bypass the hook (use sparingly):"
echo "  git commit --no-verify"
echo ""
