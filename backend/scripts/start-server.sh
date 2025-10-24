#!/bin/bash
# Backend Server Wrapper Script
# Uses process-manager.sh for robust lifecycle management
# Version: 1.0.0

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_ROOT="$(cd "$BACKEND_ROOT/.." && pwd)"
PROCESS_NAME="backend-server"
PORT=${PORT:-8002}

# Source process manager
PROCESS_MANAGER="$SCRIPT_DIR/process-manager.sh"
if [ ! -f "$PROCESS_MANAGER" ]; then
    echo "ERROR: process-manager.sh not found at $PROCESS_MANAGER"
    exit 1
fi

source "$PROCESS_MANAGER"

echo "======================================"
echo "Backend Server Startup (Wrapper)"
echo "======================================"
echo "Process: $PROCESS_NAME"
echo "Port: $PORT"
echo "Backend root: $BACKEND_ROOT"
echo ""

# Change to backend directory
cd "$BACKEND_ROOT"

# Check if already running
EXISTING_PID=$(get_registered_pid "$PROCESS_NAME")
if [ -n "$EXISTING_PID" ] && is_process_running "$EXISTING_PID"; then
    echo "ERROR: Backend server already running (PID: $EXISTING_PID)"
    echo "Stop it first: bash $SCRIPT_DIR/process-manager.sh stop $PROCESS_NAME"
    exit 1
fi

# Cleanup any stale PID file
unregister_process_pid "$PROCESS_NAME"

# Start using process manager
echo "Starting backend server with process manager..."
start_process "$PROCESS_NAME" "uvicorn app.main:app --host 0.0.0.0 --port $PORT"

# Wait a moment for startup
sleep 3

# Verify it's running
BACKEND_PID=$(get_registered_pid "$PROCESS_NAME")
if [ -n "$BACKEND_PID" ] && is_process_running "$BACKEND_PID"; then
    echo ""
    echo "======================================"
    echo "Backend Server Started"
    echo "======================================"
    echo "  PID: $BACKEND_PID"
    echo "  Port: $PORT"
    echo "  URL: http://localhost:$PORT"
    echo "  API Docs: http://localhost:$PORT/docs"
    echo "  Health: http://localhost:$PORT/api/health"
    echo ""
    echo "To stop: bash $SCRIPT_DIR/process-manager.sh stop $PROCESS_NAME"
    echo "======================================"
    exit 0
else
    echo "ERROR: Backend server failed to start"
    exit 1
fi
