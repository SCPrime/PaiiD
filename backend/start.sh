#!/bin/bash

# Backend Startup Script with Database Migrations
# This script runs Alembic migrations before starting the FastAPI server

set -e  # Exit on error

echo "======================================"
echo "PaiiD Backend Startup"
echo "======================================"

# Run pre-launch validation to catch issues early
echo ""
echo "[0/3] Running pre-launch validation..."
echo "--------------------------------------"
python -m app.core.prelaunch

# Run database migrations
echo ""
echo "[1/3] Running database migrations..."
echo "--------------------------------------"

if alembic upgrade head; then
    echo "✅ Database migrations completed successfully"
else
    echo "❌ Database migration failed!"
    exit 1
fi

# Start the FastAPI server
echo ""
echo "[2/3] Starting FastAPI server..."
echo "--------------------------------------"

exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
