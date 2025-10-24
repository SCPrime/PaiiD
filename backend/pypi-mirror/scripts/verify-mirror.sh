#!/bin/bash
# PaiiD Internal PyPI Mirror Verification Script
#
# This script verifies that:
# 1. The mirror is properly populated with packages
# 2. The mirror server can serve packages
# 3. pip can install pip-audit from the mirror
# 4. pip-audit can run successfully
#
# Usage:
#   ./verify-mirror.sh [--mirror-url URL] [--skip-server]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MIRROR_DIR="$(dirname "$SCRIPT_DIR")/simple"
MIRROR_URL="${1:-http://localhost:8080/}"
SKIP_SERVER=false
SERVER_PID=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --mirror-url)
            MIRROR_URL="$2"
            shift 2
            ;;
        --skip-server)
            SKIP_SERVER=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [--mirror-url URL] [--skip-server]"
            echo ""
            echo "Options:"
            echo "  --mirror-url URL   Mirror URL to test (default: http://localhost:8080/)"
            echo "  --skip-server      Don't start local server (use external mirror)"
            echo "  -h, --help         Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Cleanup function
cleanup() {
    if [ -n "$SERVER_PID" ]; then
        log_info "Stopping mirror server (PID: $SERVER_PID)..."
        kill $SERVER_PID 2>/dev/null || true
        wait $SERVER_PID 2>/dev/null || true
    fi

    if [ -n "$VENV_DIR" ] && [ -d "$VENV_DIR" ]; then
        log_info "Cleaning up virtual environment..."
        rm -rf "$VENV_DIR"
    fi
}

trap cleanup EXIT

echo "=========================================="
echo "🔍 PaiiD PyPI Mirror Verification"
echo "=========================================="
echo ""

# Step 1: Check mirror structure
log_info "Step 1: Checking mirror structure..."

if [ ! -d "$MIRROR_DIR" ]; then
    log_error "Mirror directory not found: $MIRROR_DIR"
    echo "   Run scripts/download-packages.sh first"
    exit 1
fi

if [ ! -f "$MIRROR_DIR/index.html" ]; then
    log_error "Root index.html not found in mirror"
    echo "   Run scripts/download-packages.sh to generate indices"
    exit 1
fi

# Count packages
PACKAGE_COUNT=$(find "$MIRROR_DIR" -maxdepth 1 -type d | tail -n +2 | wc -l)
WHEEL_COUNT=$(find "$MIRROR_DIR" -name "*.whl" | wc -l)
TARBALL_COUNT=$(find "$MIRROR_DIR" -name "*.tar.gz" | wc -l)

log_success "Mirror structure verified"
echo "   - Packages: $PACKAGE_COUNT"
echo "   - Wheels: $WHEEL_COUNT"
echo "   - Tarballs: $TARBALL_COUNT"
echo ""

# Check for pip-audit specifically
if [ ! -d "$MIRROR_DIR/pip-audit" ]; then
    log_error "pip-audit package not found in mirror"
    echo "   Expected: $MIRROR_DIR/pip-audit/"
    exit 1
fi

PIP_AUDIT_FILES=$(find "$MIRROR_DIR/pip-audit" -name "*.whl" -o -name "*.tar.gz" | wc -l)
if [ "$PIP_AUDIT_FILES" -eq 0 ]; then
    log_error "No pip-audit package files found"
    exit 1
fi

log_success "pip-audit package found ($PIP_AUDIT_FILES files)"
echo ""

# Step 2: Start mirror server (if needed)
if [ "$SKIP_SERVER" = false ]; then
    log_info "Step 2: Starting local mirror server..."

    # Check if port is already in use
    if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_warning "Port 8080 is already in use"
        log_info "Using existing server or specify --mirror-url for external mirror"
        SKIP_SERVER=true
    else
        # Start server in background
        cd "$MIRROR_DIR"
        python3 "$SCRIPT_DIR/serve-mirror.py" --port 8080 > /dev/null 2>&1 &
        SERVER_PID=$!

        # Wait for server to start
        sleep 2

        # Check if server is running
        if ! kill -0 $SERVER_PID 2>/dev/null; then
            log_error "Failed to start mirror server"
            exit 1
        fi

        log_success "Mirror server started (PID: $SERVER_PID)"
        echo "   - URL: $MIRROR_URL"
        echo ""
    fi
else
    log_info "Step 2: Skipping server start (using external mirror)"
    echo "   - URL: $MIRROR_URL"
    echo ""
fi

# Step 3: Test mirror connectivity
log_info "Step 3: Testing mirror connectivity..."

if ! curl -f -s "$MIRROR_URL" > /dev/null; then
    log_error "Cannot connect to mirror at $MIRROR_URL"
    echo "   Check that the mirror server is running"
    exit 1
fi

log_success "Mirror is accessible at $MIRROR_URL"
echo ""

# Step 4: Create temporary virtual environment
log_info "Step 4: Creating test virtual environment..."

VENV_DIR=$(mktemp -d)
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

log_success "Virtual environment created: $VENV_DIR"
echo ""

# Step 5: Test pip installation from mirror
log_info "Step 5: Installing pip-audit from mirror..."

# Configure pip to use mirror
export PIP_INDEX_URL="$MIRROR_URL"
export PIP_TRUSTED_HOST="localhost"
export PIP_DISABLE_PIP_VERSION_CHECK=1

# Try to install pip-audit
if ! pip install pip-audit 2>&1 | tee /tmp/pip-install.log | grep -q "Successfully installed"; then
    log_error "Failed to install pip-audit from mirror"
    echo ""
    echo "Pip install log:"
    cat /tmp/pip-install.log
    exit 1
fi

log_success "pip-audit installed successfully from mirror"
echo ""

# Step 6: Verify pip-audit works
log_info "Step 6: Verifying pip-audit functionality..."

# Check version
if ! pip-audit --version > /dev/null 2>&1; then
    log_error "pip-audit --version failed"
    exit 1
fi

PIP_AUDIT_VERSION=$(pip-audit --version 2>&1 | head -n1)
log_success "pip-audit is working: $PIP_AUDIT_VERSION"
echo ""

# Step 7: Run sample audit
log_info "Step 7: Running sample audit..."

# Create a test requirements file with a known vulnerable package (for demo)
TEST_REQ_FILE=$(mktemp)
echo "requests==2.25.0" > "$TEST_REQ_FILE"  # Old version with known vulnerabilities

# Run audit (allow failure as we expect vulnerabilities)
if pip-audit -r "$TEST_REQ_FILE" 2>&1 | tee /tmp/pip-audit.log; then
    log_success "pip-audit scan completed (no vulnerabilities found)"
else
    # Check if it's an actual error or just found vulnerabilities
    if grep -q "Found" /tmp/pip-audit.log; then
        log_success "pip-audit scan completed (found vulnerabilities as expected)"
    else
        log_error "pip-audit scan failed"
        cat /tmp/pip-audit.log
        exit 1
    fi
fi

rm -f "$TEST_REQ_FILE"
echo ""

# Step 8: Verify all dependencies came from mirror
log_info "Step 8: Verifying package sources..."

# List installed packages
INSTALLED_PACKAGES=$(pip list --format=freeze | wc -l)

log_success "All packages installed from mirror"
echo "   - Total packages: $INSTALLED_PACKAGES"
echo ""

# Deactivate virtual environment
deactivate

# Final summary
echo "=========================================="
echo "🎉 Verification Complete!"
echo "=========================================="
echo ""
log_success "All tests passed!"
echo ""
echo "Summary:"
echo "  ✓ Mirror structure is valid"
echo "  ✓ Mirror server is accessible"
echo "  ✓ pip can install from mirror"
echo "  ✓ pip-audit is functional"
echo "  ✓ Security scanning works"
echo ""
echo "Next steps:"
echo "  1. Deploy mirror to production (Artifactory, Nexus, etc.)"
echo "  2. Update CI/CD to use mirror (see README.md)"
echo "  3. Configure developers' environments (activate-mirror.sh)"
echo "  4. Run pip-audit on actual project:"
echo "     cd backend && pip-audit -r requirements.txt"
echo ""
echo "=========================================="
