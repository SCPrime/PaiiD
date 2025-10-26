#!/bin/bash

# Backend Startup Script with Process Management Integration
# Version: 2.0.0 - Integrates with process-manager.sh for robust lifecycle management
# This script runs validation, cleanup, migrations, registers PID, then starts FastAPI

set -euo pipefail  # Exit on error, undefined variables, pipe failures

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PID_DIR="${PROJECT_ROOT}/backend/.run"
LOG_DIR="${PROJECT_ROOT}/backend/.logs"
PROCESS_NAME="backend-server"
PORT=${PORT:-8002}  # Default to 8002 (8001 has unkillable zombies from previous sessions)

# Ensure directories exist
mkdir -p "$PID_DIR" "$LOG_DIR"

# Import process manager functions
PROCESS_MANAGER="${SCRIPT_DIR}/scripts/process-manager.sh"
if [ -f "$PROCESS_MANAGER" ]; then
    source "$PROCESS_MANAGER"
else
    echo "ERROR: process-manager.sh not found at $PROCESS_MANAGER"
    exit 1
fi

# Global variable to track uvicorn PID
UVICORN_PID=""

# Cleanup function called on EXIT, INT, TERM
cleanup_on_exit() {
    local exit_code=$?
    echo ""
    echo "======================================"
    echo "Backend Shutdown Initiated"
    echo "======================================"

    # Kill uvicorn process if it's running
    if [ -n "$UVICORN_PID" ] && is_process_running "$UVICORN_PID"; then
        echo "Stopping uvicorn process (PID: $UVICORN_PID)..."
        
        # Try graceful shutdown first (SIGTERM)
        kill -TERM "$UVICORN_PID" 2>/dev/null || true
        
        # Wait up to 10 seconds for graceful shutdown
        local waited=0
        while [ $waited -lt 10 ]; do
            if ! is_process_running "$UVICORN_PID"; then
                echo "Uvicorn stopped gracefully"
                break
            fi
            sleep 1
            waited=$((waited + 1))
        done
        
        # Force kill if still running
        if is_process_running "$UVICORN_PID"; then
            echo "Forcing uvicorn shutdown (SIGKILL)..."
            kill -KILL "$UVICORN_PID" 2>/dev/null || true
            sleep 1
        fi
    fi

    # Get PID file path
    local pid_file=$(get_pid_file "$PROCESS_NAME")

    # Remove PID file if it exists
    if [ -f "$pid_file" ]; then
        local pid=$(read_pid "$pid_file")
        echo "Cleaning up PID file for process $pid"
        remove_pid "$pid_file"
    fi

    echo "Shutdown complete (exit code: $exit_code)"
    exit $exit_code
}

# Signal handler to forward signals to uvicorn
signal_handler() {
    local signal=$1
    echo "Received signal: $signal"
    
    if [ -n "$UVICORN_PID" ] && is_process_running "$UVICORN_PID"; then
        echo "Forwarding $signal to uvicorn (PID: $UVICORN_PID)"
        kill -$signal "$UVICORN_PID" 2>/dev/null || true
    fi
    
    # Exit after signal handling
    exit 0
}

# Register cleanup handlers
trap cleanup_on_exit EXIT
trap 'signal_handler TERM' TERM
trap 'signal_handler INT' INT

echo "======================================"
echo "PaiiD Backend Startup (Managed)"
echo "======================================"
echo "Process name: $PROCESS_NAME"
echo "Target port: $PORT"
echo "PID directory: $PID_DIR"
echo ""

# Step 0: Process cleanup (prevent zombie processes)
echo "[0/5] Cleaning up existing processes..."
echo "--------------------------------------"

if [ -f "scripts/cleanup.sh" ]; then
    bash scripts/cleanup.sh $PORT || true  # Don't fail if cleanup has issues
    echo "Process cleanup completed"
else
    echo "WARNING: Cleanup script not found, skipping process cleanup"
fi

# Step 0.5: Clean up orphaned PID files
echo ""
echo "[0.5/5] Cleaning up orphaned PID files..."
echo "--------------------------------------"

cleanup_orphans

# Step 1: Pre-launch validation
echo ""
echo "[1/5] Running pre-launch validation..."
echo "--------------------------------------"

if python -m app.core.prelaunch --strict; then
    echo "SUCCESS: Pre-launch validation passed"
else
    echo "ERROR: Pre-launch validation failed!"
    exit 1
fi

# Step 2: Database migrations (if alembic available)
echo ""
echo "[2/5] Running database migrations..."
echo "--------------------------------------"

if command -v alembic &> /dev/null; then
    if alembic upgrade head; then
        echo "SUCCESS: Database migrations completed"
    else
        echo "ERROR: Database migration failed!"
        exit 1
    fi
else
    echo "INFO: Alembic not found, skipping migrations"
fi

# Step 3: Final port validation
echo ""
echo "[3/5] Final port availability check..."
echo "--------------------------------------"

if is_port_in_use "$PORT"; then
    echo "ERROR: Port $PORT is still occupied after cleanup!"
    echo "Attempting emergency port cleanup..."

    if cleanup_port "$PORT" 3; then
        echo "SUCCESS: Port $PORT freed after retry"
    else
        echo "ERROR: Port $PORT still occupied. Manual intervention required."
        echo "Run: bash scripts/cleanup.sh $PORT"
        exit 1
    fi
else
    echo "SUCCESS: Port $PORT is available"
fi

# Step 4: Register process (PID will be written after uvicorn starts)
echo ""
echo "[4/5] Preparing process registration..."
echo "--------------------------------------"

# Note: PID registration happens in background after uvicorn starts
# We use a background monitor to capture the PID

# Step 5: Start the FastAPI server with PID tracking
echo ""
echo "[5/5] Starting FastAPI server with PID tracking..."
echo "--------------------------------------"

echo "Starting uvicorn on port $PORT"
echo "Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT"

# Start uvicorn in background and capture PID
uvicorn app.main:app --host 0.0.0.0 --port $PORT &
UVICORN_PID=$!
BACKEND_PID=$UVICORN_PID

# Register PID immediately
write_pid "$BACKEND_PID" "$(get_pid_file "$PROCESS_NAME")"
echo "Backend process started with PID: $BACKEND_PID"

# Wait a moment to verify startup
sleep 2

if is_process_running "$BACKEND_PID"; then
    echo "SUCCESS: Backend is running (PID: $BACKEND_PID)"
    echo ""
    echo "======================================"
    echo "Backend Started Successfully"
    echo "======================================"
    echo "  URL: http://localhost:$PORT"
    echo "  API Docs: http://localhost:$PORT/docs"
    echo "  Health: http://localhost:$PORT/api/health"
    echo "  PID: $BACKEND_PID"
    echo "  PID File: $(get_pid_file "$PROCESS_NAME")"
    echo "======================================"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""

    # Wait for the backend process (foreground)
    # This ensures signals are properly caught and forwarded
    wait $BACKEND_PID
    
    # Capture exit code from uvicorn
    UVICORN_EXIT_CODE=$?
    echo "Uvicorn exited with code: $UVICORN_EXIT_CODE"
    exit $UVICORN_EXIT_CODE
else
    echo "ERROR: Backend failed to start"
    UVICORN_PID=""  # Clear PID so cleanup doesn't try to kill non-existent process
    exit 1
fi
