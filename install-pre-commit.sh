#!/bin/bash

# ====================================
# PAIID MONOREPO PRE-COMMIT HOOKS INSTALLER
# ====================================
# Installs pre-commit hooks for both frontend and backend
#
# Usage:
#   bash install-pre-commit.sh [frontend|backend|all]
#
# Examples:
#   bash install-pre-commit.sh all       # Install both frontend and backend hooks
#   bash install-pre-commit.sh frontend  # Install only frontend hooks
#   bash install-pre-commit.sh backend   # Install only backend hooks

set -e

# Default to installing everything
TARGET="${1:-all}"

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  PaiiD Pre-commit Hooks Installation                      ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# ====================================
# FRONTEND HOOKS (Husky + lint-staged)
# ====================================

install_frontend_hooks() {
  echo "📦 Installing Frontend Hooks (Husky + lint-staged)..."
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""

  cd frontend

  # Check if node_modules exists
  if [ ! -d "node_modules" ]; then
    echo "📥 Installing npm dependencies first..."
    npm install
    echo ""
  fi

  # Check if husky is installed
  if [ ! -d "../.husky" ]; then
    echo "⚠️  Husky directory not found!"
    echo "   Run 'npm run prepare' from frontend directory"
  else
    echo "✅ Husky hooks already configured in .husky/"
  fi

  # Check if lint-staged is configured
  if [ ! -f ".lintstagedrc.json" ]; then
    echo "❌ .lintstagedrc.json not found!"
    exit 1
  else
    echo "✅ lint-staged configuration found"
  fi

  echo ""
  echo "🧪 Testing frontend linters..."
  echo ""

  # Test if prettier and eslint work
  if npm run format:check > /dev/null 2>&1; then
    echo "✅ Prettier is configured"
  else
    echo "⚠️  Prettier check had issues (this is OK if files need formatting)"
  fi

  if npm run lint > /dev/null 2>&1; then
    echo "✅ ESLint is configured"
  else
    echo "⚠️  ESLint found issues (they will be auto-fixed on commit)"
  fi

  cd ..

  echo ""
  echo "✅ Frontend hooks are ready!"
  echo ""
}

# ====================================
# BACKEND HOOKS (pre-commit framework)
# ====================================

install_backend_hooks() {
  echo "🐍 Installing Backend Hooks (pre-commit framework)..."
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""

  cd backend

  # Check if .pre-commit-config.yaml exists
  if [ ! -f ".pre-commit-config.yaml" ]; then
    echo "❌ .pre-commit-config.yaml not found!"
    exit 1
  else
    echo "✅ .pre-commit-config.yaml found"
  fi

  # Check if pre-commit is installed
  if pip show pre-commit > /dev/null 2>&1; then
    echo "✅ pre-commit already installed: $(pip show pre-commit | grep Version | cut -d' ' -f2)"
  else
    echo "📥 Installing pre-commit package..."
    pip install pre-commit
    echo "✅ pre-commit installed"
  fi

  echo ""
  echo "🔗 Installing git hooks from .pre-commit-config.yaml..."
  pre-commit install

  echo ""
  echo "🧪 Testing hooks on sample files..."
  echo ""

  # Find a few Python files to test
  SAMPLE_FILES=$(find app -name "*.py" -type f | head -3 | tr '\n' ' ')

  if [ -n "$SAMPLE_FILES" ]; then
    # Run hooks on sample files (show output)
    if pre-commit run --files $SAMPLE_FILES; then
      echo ""
      echo "✅ Backend hooks validated successfully!"
    else
      echo ""
      echo "⚠️  Some hooks made changes (this is normal - they auto-fix issues)"
    fi
  else
    echo "⏭️  No Python files found to test"
  fi

  cd ..

  echo ""
  echo "✅ Backend hooks are ready!"
  echo ""
}

# ====================================
# MAIN INSTALLATION LOGIC
# ====================================

case "$TARGET" in
  frontend)
    install_frontend_hooks
    ;;
  backend)
    install_backend_hooks
    ;;
  all)
    install_frontend_hooks
    install_backend_hooks
    ;;
  *)
    echo "❌ Invalid target: $TARGET"
    echo ""
    echo "Usage: bash install-pre-commit.sh [frontend|backend|all]"
    exit 1
    ;;
esac

# ====================================
# SUMMARY
# ====================================

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  ✅ Pre-commit Hooks Installed Successfully!              ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "📋 What happens now:"
echo ""
echo "  • Every git commit will trigger validation:"
echo "    - Frontend: ESLint + Prettier (via lint-staged)"
echo "    - Backend: Black + Ruff (via pre-commit framework)"
echo ""
echo "  • TypeScript errors are WARNING ONLY (won't block commits)"
echo "  • Code will be auto-formatted to match project standards"
echo "  • LOCKED FINAL files are protected from modification"
echo ""
echo "🔧 Bypass mechanism (for orchestrator/emergency):"
echo ""
echo "  # Skip all hooks:"
echo "  SKIP_HOOKS=1 git commit -m \"message\""
echo ""
echo "  # Or use --no-verify:"
echo "  git commit --no-verify -m \"message\""
echo ""
echo "📚 Manual validation commands:"
echo ""
echo "  # Frontend:"
echo "  cd frontend"
echo "  npm run lint:fix         # Fix ESLint issues"
echo "  npm run format           # Format with Prettier"
echo "  npm run type-check       # Check TypeScript"
echo ""
echo "  # Backend:"
echo "  cd backend"
echo "  pre-commit run --all-files  # Run all hooks"
echo "  black .                     # Format with Black"
echo "  ruff check --fix .          # Lint with Ruff"
echo ""
echo "✨ Happy coding! Your code quality is now protected."
echo ""
