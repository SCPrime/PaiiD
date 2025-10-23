#!/usr/bin/env bash

# Backend Startup Script with Database Migrations
# This script runs Alembic migrations before starting the FastAPI server

set -euo pipefail  # Exit on error and propagate failures

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
KILL_SCRIPT="$SCRIPT_DIR/scripts/kill-uvicorn.sh"
PORT="${PORT:-8001}"

echo "======================================"
echo "PaiiD Backend Startup"
echo "======================================"

echo ""
echo "[1/3] Ensuring development ports are available..."
echo "--------------------------------------"
if [ -x "$KILL_SCRIPT" ]; then
    "$KILL_SCRIPT" --quiet
else
    echo "⚠️  Cleanup script not found at $KILL_SCRIPT"
    echo "    Continuing without terminating existing uvicorn processes."
fi

echo ""
echo "[2/3] Running database migrations..."
echo "--------------------------------------"
if alembic upgrade head; then
    echo "✅ Database migrations completed successfully"
else
    echo "❌ Database migration failed!"
    exit 1
fi

echo ""
echo "[3/3] Starting FastAPI server on port $PORT..."
echo "--------------------------------------"
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
