#!/bin/bash

# Backend Startup Script with Database Migrations
# This script runs Alembic migrations before starting the FastAPI server

set -e  # Exit on error

echo "======================================"
echo "PaiiD Backend Startup"
echo "======================================"

# Run database migrations
echo ""
echo "[1/3] Validating runtime requirements..."
echo "--------------------------------------"

python -m app.core.prelaunch

echo ""
echo "[2/3] Running database migrations..."
echo "--------------------------------------"

if alembic upgrade head; then
    echo "✅ Database migrations completed successfully"
else
    echo "❌ Database migration failed!"
    exit 1
fi

# Start the FastAPI server
echo ""
echo "[3/3] Starting FastAPI server..."
echo "--------------------------------------"

exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
