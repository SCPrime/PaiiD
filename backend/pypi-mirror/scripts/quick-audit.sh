#!/bin/bash
# PaiiD Internal PyPI Mirror - Automated Setup and Audit Script
#
# This script automates the entire process:
# 1. Populates the mirror with packages
# 2. Starts the mirror server
# 3. Installs pip-audit
# 4. Runs security audit on backend dependencies
# 5. Generates a report
#
# Usage:
#   ./quick-audit.sh [--no-download] [--port PORT]
#
# Options:
#   --no-download    Skip downloading packages (use existing mirror)
#   --port PORT      Use custom port (default: 8080)
#   --stop-server    Stop any running mirror servers and exit

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MIRROR_DIR="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$(dirname "$MIRROR_DIR")"
PROJECT_ROOT="$(dirname "$BACKEND_DIR")"
PORT=8080
SKIP_DOWNLOAD=false
STOP_SERVER_ONLY=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-download)
            SKIP_DOWNLOAD=true
            shift
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --stop-server)
            STOP_SERVER_ONLY=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [--no-download] [--port PORT] [--stop-server]"
            echo ""
            echo "Options:"
            echo "  --no-download    Skip downloading packages (use existing mirror)"
            echo "  --port PORT      Use custom port (default: 8080)"
            echo "  --stop-server    Stop any running mirror servers and exit"
            echo "  -h, --help       Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Function to stop mirror server
stop_mirror_server() {
    if [ -f /tmp/mirror-server.pid ]; then
        PID=$(cat /tmp/mirror-server.pid)
        if kill -0 $PID 2>/dev/null; then
            echo -e "${BLUE}🛑 Stopping mirror server (PID: $PID)...${NC}"
            kill $PID 2>/dev/null || true
            rm -f /tmp/mirror-server.pid
            sleep 1
            echo -e "${GREEN}✓ Server stopped${NC}"
        else
            rm -f /tmp/mirror-server.pid
        fi
    fi

    # Also check for any Python processes running serve-mirror.py
    pkill -f "serve-mirror.py" 2>/dev/null || true
}

# If --stop-server is specified, stop and exit
if [ "$STOP_SERVER_ONLY" = true ]; then
    stop_mirror_server
    exit 0
fi

# Cleanup function
cleanup() {
    echo ""
    echo -e "${BLUE}🧹 Cleaning up...${NC}"
    stop_mirror_server
    if [ -n "$VENV_DIR" ] && [ -d "$VENV_DIR" ]; then
        rm -rf "$VENV_DIR"
    fi
}

trap cleanup EXIT

# Print banner
echo "============================================================"
echo -e "${CYAN}🔒 PaiiD Security Audit - Automated Setup${NC}"
echo "============================================================"
echo ""

# Step 1: Populate mirror (if needed)
if [ "$SKIP_DOWNLOAD" = false ]; then
    echo -e "${BLUE}📦 Step 1/5: Populating internal mirror...${NC}"
    cd "$MIRROR_DIR"
    if [ ! -f scripts/download-packages.sh ]; then
        echo -e "${RED}❌ Error: download-packages.sh not found${NC}"
        exit 1
    fi
    bash scripts/download-packages.sh | grep -E '(✓|✅|📊|🚀|Summary)'
    echo -e "${GREEN}✅ Mirror populated${NC}"
    echo ""
else
    echo -e "${YELLOW}⏩ Step 1/5: Skipping package download (using existing mirror)${NC}"
    echo ""
fi

# Step 2: Stop any existing server and start new one
echo -e "${BLUE}🚀 Step 2/5: Starting mirror server on port $PORT...${NC}"
stop_mirror_server

cd "$MIRROR_DIR/simple"
python3 "$MIRROR_DIR/scripts/serve-mirror.py" --port $PORT --host 127.0.0.1 > /tmp/mirror-server.log 2>&1 &
SERVER_PID=$!
echo $SERVER_PID > /tmp/mirror-server.pid

# Wait for server to start
sleep 2

if ! kill -0 $SERVER_PID 2>/dev/null; then
    echo -e "${RED}❌ Failed to start mirror server${NC}"
    cat /tmp/mirror-server.log
    exit 1
fi

if ! curl -f -s "http://127.0.0.1:$PORT/" > /dev/null; then
    echo -e "${RED}❌ Mirror server not accessible${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Mirror server running at http://127.0.0.1:$PORT/${NC}"
echo ""

# Step 3: Create virtual environment and install pip-audit
echo -e "${BLUE}🔧 Step 3/5: Installing pip-audit from mirror...${NC}"
VENV_DIR=$(mktemp -d)
python3 -m venv "$VENV_DIR" > /dev/null 2>&1
source "$VENV_DIR/bin/activate"

export PIP_INDEX_URL="http://127.0.0.1:$PORT/"
export PIP_TRUSTED_HOST="127.0.0.1"
export PIP_DISABLE_PIP_VERSION_CHECK=1

pip install -q pip-audit

PIP_AUDIT_VERSION=$(pip-audit --version 2>&1 | head -n1)
echo -e "${GREEN}✅ Installed: $PIP_AUDIT_VERSION${NC}"
echo ""

# Step 4: Run security audit
echo -e "${BLUE}🔍 Step 4/5: Running security audit on backend dependencies...${NC}"
cd "$BACKEND_DIR"

# Run audit and capture output
AUDIT_OUTPUT=$(pip-audit -r requirements.txt 2>&1 || true)
AUDIT_EXIT_CODE=$?

# Generate report filename with timestamp
REPORT_FILE="security-audit-$(date +%Y%m%d-%H%M%S).txt"
REPORT_PATH="$BACKEND_DIR/$REPORT_FILE"

# Save full report
cat > "$REPORT_PATH" <<EOF
PaiiD Backend Security Audit Report
Generated: $(date '+%Y-%m-%d %H:%M:%S')
Audited by: pip-audit $PIP_AUDIT_VERSION
Source: Internal PyPI Mirror (http://127.0.0.1:$PORT/)

Requirements File: $BACKEND_DIR/requirements.txt

========================================
AUDIT RESULTS
========================================

$AUDIT_OUTPUT

========================================
SUMMARY
========================================

EOF

# Count vulnerabilities
VULN_COUNT=$(echo "$AUDIT_OUTPUT" | grep -c "^Found.*vulnerability" || echo "0")

if [ "$VULN_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Found $VULN_COUNT known vulnerabilities${NC}"
    echo ""
    echo "$AUDIT_OUTPUT"
    echo ""
    echo -e "${YELLOW}Status: VULNERABILITIES DETECTED${NC}" >> "$REPORT_PATH"
else
    echo -e "${GREEN}✅ No known vulnerabilities found${NC}"
    echo -e "${GREEN}Status: CLEAN${NC}" >> "$REPORT_PATH"
fi

echo ""

# Step 5: Generate summary
echo -e "${BLUE}📊 Step 5/5: Generating summary...${NC}"

# Count packages audited
PACKAGE_COUNT=$(echo "$AUDIT_OUTPUT" | grep -oE '[0-9]+ package' | head -n1 | grep -oE '[0-9]+' || echo "unknown")

cat >> "$REPORT_PATH" <<EOF

Packages Audited: $PACKAGE_COUNT
Vulnerabilities Found: $VULN_COUNT

========================================
RECOMMENDATIONS
========================================

EOF

if [ "$VULN_COUNT" -gt 0 ]; then
    cat >> "$REPORT_PATH" <<EOF
1. Review each vulnerability and assess impact on your application
2. Check if updated versions are available that fix the issues
3. Update requirements.txt with patched versions
4. Re-run this audit after updates to verify fixes
5. Consider using alternative packages if no fix is available
6. Document any accepted risks for vulnerabilities without fixes

For timing attack vulnerabilities (like ecdsa):
- Assess if the attack vector applies to your use case
- Consider if the affected functionality is exposed to untrusted input
- Implement additional security controls if necessary

EOF
else
    cat >> "$REPORT_PATH" <<EOF
✅ All dependencies are up to date with no known vulnerabilities.

Continue to:
1. Run this audit regularly (weekly or before each release)
2. Keep dependencies updated
3. Monitor security advisories for your dependencies
4. Consider setting up automated security scanning in CI/CD

EOF
fi

cat >> "$REPORT_PATH" <<EOF
========================================
NEXT STEPS
========================================

1. Review this report: $REPORT_PATH
2. Update vulnerable packages in requirements.txt
3. Test application after updates
4. Re-run audit: ./quick-audit.sh --no-download
5. Commit updated requirements.txt

For CI/CD integration, see:
$MIRROR_DIR/README.md

For production deployment, see:
$MIRROR_DIR/README.md#production-deployment

========================================
EOF

echo -e "${GREEN}✅ Report saved: $REPORT_PATH${NC}"
echo ""

# Print summary
echo "============================================================"
echo -e "${CYAN}📋 AUDIT SUMMARY${NC}"
echo "============================================================"
echo ""
echo -e "Packages Audited:        ${CYAN}$PACKAGE_COUNT${NC}"
if [ "$VULN_COUNT" -gt 0 ]; then
    echo -e "Vulnerabilities Found:   ${YELLOW}$VULN_COUNT${NC}"
else
    echo -e "Vulnerabilities Found:   ${GREEN}$VULN_COUNT${NC}"
fi
echo -e "Report Location:         ${CYAN}$REPORT_PATH${NC}"
echo -e "Mirror Server:           ${CYAN}http://127.0.0.1:$PORT/${NC} (PID: $SERVER_PID)"
echo ""

if [ "$VULN_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  ACTION REQUIRED: Review vulnerabilities and update dependencies${NC}"
    echo ""
    echo "To view details:"
    echo "  cat $REPORT_PATH"
    echo ""
    echo "To stop mirror server:"
    echo "  $0 --stop-server"
    echo ""
else
    echo -e "${GREEN}✅ No vulnerabilities found - your dependencies are secure!${NC}"
    echo ""
    echo "To stop mirror server:"
    echo "  $0 --stop-server"
    echo ""
fi

echo "============================================================"
echo ""

# Keep script running until user presses Ctrl+C
echo -e "${BLUE}ℹ️  Mirror server is running in the background${NC}"
echo -e "${BLUE}ℹ️  Press Ctrl+C to stop the server and exit${NC}"
echo ""

# Wait indefinitely
wait $SERVER_PID 2>/dev/null || true
