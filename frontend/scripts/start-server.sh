#!/bin/bash
# Frontend Server Wrapper Script
# Uses backend process-manager.sh for robust lifecycle management
# Version: 1.0.0

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_ROOT="$(cd "$FRONTEND_ROOT/.." && pwd)"
PROCESS_NAME="frontend-server"
PORT=${PORT:-3000}

# Source process manager from backend
PROCESS_MANAGER="$PROJECT_ROOT/backend/scripts/process-manager.sh"
if [ ! -f "$PROCESS_MANAGER" ]; then
    echo "ERROR: process-manager.sh not found at $PROCESS_MANAGER"
    exit 1
fi

source "$PROCESS_MANAGER"

echo "======================================"
echo "Frontend Server Startup (Wrapper)"
echo "======================================"
echo "Process: $PROCESS_NAME"
echo "Port: $PORT"
echo "Frontend root: $FRONTEND_ROOT"
echo ""

# Change to frontend directory
cd "$FRONTEND_ROOT"

# Check if already running
EXISTING_PID=$(get_registered_pid "$PROCESS_NAME")
if [ -n "$EXISTING_PID" ] && is_process_running "$EXISTING_PID"; then
    echo "ERROR: Frontend server already running (PID: $EXISTING_PID)"
    echo "Stop it first: bash $PROCESS_MANAGER stop $PROCESS_NAME"
    exit 1
fi

# Cleanup any stale PID file
unregister_process_pid "$PROCESS_NAME"

# Start using process manager
echo "Starting frontend server with process manager..."
start_process "$PROCESS_NAME" "npm run dev"

# Wait a moment for startup
sleep 5

# Verify it's running
FRONTEND_PID=$(get_registered_pid "$PROCESS_NAME")
if [ -n "$FRONTEND_PID" ] && is_process_running "$FRONTEND_PID"; then
    echo ""
    echo "======================================"
    echo "Frontend Server Started"
    echo "======================================"
    echo "  PID: $FRONTEND_PID"
    echo "  Port: $PORT"
    echo "  URL: http://localhost:$PORT"
    echo ""
    echo "To stop: bash $PROCESS_MANAGER stop $PROCESS_NAME"
    echo "======================================"
    exit 0
else
    echo "ERROR: Frontend server failed to start"
    exit 1
fi
