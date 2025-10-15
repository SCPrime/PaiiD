#!/bin/bash

# PaiiD Deployment Verification Script
# Tests live deployment and reports status

set -e

echo "🧪 PaiiD Deployment Verification"
echo "================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0

# Helper functions
pass() {
    echo -e "${GREEN}✅ PASS${NC}: $1"
    ((PASSED++))
}

fail() {
    echo -e "${RED}❌ FAIL${NC}: $1"
    ((FAILED++))
}

warn() {
    echo -e "${YELLOW}⚠️  WARN${NC}: $1"
}

# Test 1: Frontend Reachability
echo "Test 1: Frontend Reachability"
echo "------------------------------"
FRONTEND_URL="https://paiid-frontend.onrender.com"
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL" --max-time 10 || echo "000")

if [ "$FRONTEND_STATUS" == "200" ]; then
    pass "Frontend is reachable (HTTP 200)"
else
    fail "Frontend failed (HTTP $FRONTEND_STATUS)"
fi

echo ""

# Test 2: Backend Health Check
echo "Test 2: Backend Health Check"
echo "-----------------------------"
BACKEND_URL="https://paiid-backend.onrender.com/api/health"
BACKEND_RESPONSE=$(curl -s "$BACKEND_URL" --max-time 10 || echo "TIMEOUT")

if echo "$BACKEND_RESPONSE" | grep -q '"status":"ok"'; then
    pass "Backend health check returns 'ok'"
else
    fail "Backend health check failed"
fi

echo ""
echo "📊 Summary: $PASSED passed, $FAILED failed"
