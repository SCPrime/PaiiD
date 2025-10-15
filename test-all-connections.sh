#!/bin/bash

# PaiiD Comprehensive Connection Test Suite
# Tests all connections between services, databases, and external systems

set +e  # Don't exit on errors, we want to test everything

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Test result tracking
declare -a FAILED_TEST_NAMES

# Helper functions
pass() {
    echo -e "${GREEN}✅ PASS${NC}: $1"
    ((PASSED_TESTS++))
    ((TOTAL_TESTS++))
}

fail() {
    echo -e "${RED}❌ FAIL${NC}: $1"
    FAILED_TEST_NAMES+=("$1")
    ((FAILED_TESTS++))
    ((TOTAL_TESTS++))
}

warn() {
    echo -e "${YELLOW}⚠️  WARN${NC}: $1"
}

info() {
    echo -e "${BLUE}ℹ️  INFO${NC}: $1"
}

section() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
}

# Start
echo ""
echo "🧪 PaiiD Comprehensive Connection Test Suite"
echo "=============================================="
echo "Testing all connections between:"
echo "  - GitHub ↔ Render (CI/CD)"
echo "  - Frontend ↔ Backend (API)"
echo "  - Backend ↔ Redis (Cache)"
echo "  - Backend ↔ PostgreSQL (Database)"
echo "  - Browser ↔ Services (HTTPS)"
echo "  - GitHub Actions ↔ SonarCloud"
echo ""

# ═══════════════════════════════════════════════════
section "A. Frontend Service Tests"
# ═══════════════════════════════════════════════════

info "Testing https://paiid-frontend.onrender.com"

# A1: Frontend reachability
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://paiid-frontend.onrender.com" --max-time 15 2>/dev/null || echo "000")
if [ "$FRONTEND_STATUS" == "200" ]; then
    pass "Frontend HTTP 200 OK"
elif [ "$FRONTEND_STATUS" == "502" ]; then
    fail "Frontend HTTP 502 Bad Gateway (service down)"
elif [ "$FRONTEND_STATUS" == "000" ]; then
    fail "Frontend timeout or unreachable"
else
    fail "Frontend HTTP $FRONTEND_STATUS"
fi

# A2: Frontend SSL certificate
if curl -s -I "https://paiid-frontend.onrender.com" --max-time 10 2>&1 | grep -q "HTTP/2 200\|HTTP/1.1 200"; then
    pass "Frontend SSL certificate valid"
else
    fail "Frontend SSL issues"
fi

# A3: Frontend contains PaiiD branding
if [ "$FRONTEND_STATUS" == "200" ]; then
    FRONTEND_HTML=$(curl -s "https://paiid-frontend.onrender.com" --max-time 15 2>/dev/null)
    if echo "$FRONTEND_HTML" | grep -iq "PaiiD\|paiid"; then
        pass "Frontend contains PaiiD branding"
    else
        fail "Frontend missing PaiiD branding (may be error page)"
    fi
fi

# A4: Frontend Next.js metadata
if echo "$FRONTEND_HTML" | grep -q "__NEXT_DATA__\|nextjs"; then
    pass "Frontend is Next.js application"
else
    warn "Frontend may not be Next.js app (could be error page)"
fi

# ═══════════════════════════════════════════════════
section "B. Backend Service Tests"
# ═══════════════════════════════════════════════════

info "Testing https://paiid-backend.onrender.com"

# B1: Backend health endpoint
BACKEND_RESPONSE=$(curl -s "https://paiid-backend.onrender.com/api/health" --max-time 30 2>/dev/null || echo "ERROR")
BACKEND_STATUS=$(echo "$BACKEND_RESPONSE" | jq -r '.status' 2>/dev/null || echo "ERROR")

if [ "$BACKEND_STATUS" == "ok" ]; then
    pass "Backend health check returns 'ok'"
elif [ "$BACKEND_STATUS" == "ERROR" ]; then
    fail "Backend health check failed or timeout"
else
    fail "Backend health check unexpected response: $BACKEND_STATUS"
fi

# B2: Backend Redis connection
if [ "$BACKEND_STATUS" == "ok" ]; then
    REDIS_CONNECTED=$(echo "$BACKEND_RESPONSE" | jq -r '.redis.connected' 2>/dev/null)
    if [ "$REDIS_CONNECTED" == "true" ]; then
        pass "Backend → Redis connection successful"

        # Redis latency check
        REDIS_LATENCY=$(echo "$BACKEND_RESPONSE" | jq -r '.redis.latency_ms' 2>/dev/null)
        if [ ! -z "$REDIS_LATENCY" ] && [ "$REDIS_LATENCY" -lt "100" ]; then
            pass "Redis latency acceptable (${REDIS_LATENCY}ms)"
        else
            warn "Redis latency high or unknown (${REDIS_LATENCY}ms)"
        fi
    else
        fail "Backend → Redis connection failed"
    fi
fi

# B3: Backend SSL certificate
if curl -s -I "https://paiid-backend.onrender.com/api/health" --max-time 10 2>&1 | grep -q "HTTP/2 200\|HTTP/1.1 200\|HTTP/1.1 405"; then
    pass "Backend SSL certificate valid"
else
    fail "Backend SSL issues"
fi

# ═══════════════════════════════════════════════════
section "C. API Endpoint Tests"
# ═══════════════════════════════════════════════════

# C1: Market data endpoint
MARKET_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://paiid-backend.onrender.com/api/market/indices" --max-time 15 2>/dev/null || echo "000")
if [ "$MARKET_STATUS" == "200" ]; then
    pass "Market data endpoint accessible (HTTP 200)"
elif [ "$MARKET_STATUS" == "401" ]; then
    warn "Market data requires authentication (HTTP 401)"
else
    fail "Market data endpoint failed (HTTP $MARKET_STATUS)"
fi

# C2: Strategy templates endpoint
STRATEGY_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://paiid-backend.onrender.com/api/strategies/templates" --max-time 15 2>/dev/null || echo "000")
if [ "$STRATEGY_STATUS" == "200" ]; then
    pass "Strategy templates endpoint accessible"
elif [ "$STRATEGY_STATUS" == "401" ]; then
    warn "Strategy templates require authentication"
else
    fail "Strategy templates endpoint failed (HTTP $STRATEGY_STATUS)"
fi

# ═══════════════════════════════════════════════════
section "D. CORS Configuration Tests"
# ═══════════════════════════════════════════════════

# D1: CORS headers present
CORS_HEADER=$(curl -s -I -H "Origin: https://paiid-frontend.onrender.com" "https://paiid-backend.onrender.com/api/health" --max-time 10 2>/dev/null | grep -i "access-control-allow-origin" || echo "NONE")

if echo "$CORS_HEADER" | grep -q "https://paiid-frontend.onrender.com\|*"; then
    pass "CORS configured for frontend origin"
else
    fail "CORS not configured correctly"
fi

# D2: CORS credentials allowed
if curl -s -I -H "Origin: https://paiid-frontend.onrender.com" "https://paiid-backend.onrender.com/api/health" --max-time 10 2>/dev/null | grep -qi "access-control-allow-credentials: true"; then
    pass "CORS credentials allowed"
else
    warn "CORS credentials not explicitly allowed"
fi

# ═══════════════════════════════════════════════════
section "E. GitHub Integration Tests"
# ═══════════════════════════════════════════════════

# E1: GitHub repository accessible
if gh api repos/SCPrime/PaiiD >/dev/null 2>&1; then
    pass "GitHub repository accessible via API"
else
    warn "GitHub API not accessible (gh CLI may not be configured)"
fi

# E2: GitHub Actions status
if command -v gh >/dev/null 2>&1; then
    LATEST_RUN_STATUS=$(gh api repos/SCPrime/PaiiD/actions/runs --jq '.workflow_runs[0].status' 2>/dev/null || echo "ERROR")
    LATEST_RUN_CONCLUSION=$(gh api repos/SCPrime/PaiiD/actions/runs --jq '.workflow_runs[0].conclusion' 2>/dev/null || echo "ERROR")

    if [ "$LATEST_RUN_STATUS" == "completed" ]; then
        if [ "$LATEST_RUN_CONCLUSION" == "success" ]; then
            pass "Latest GitHub Actions workflow succeeded"
        elif [ "$LATEST_RUN_CONCLUSION" == "failure" ]; then
            fail "Latest GitHub Actions workflow failed"
        else
            warn "Latest GitHub Actions workflow: $LATEST_RUN_CONCLUSION"
        fi
    elif [ "$LATEST_RUN_STATUS" == "in_progress" ]; then
        info "GitHub Actions workflow currently running"
    else
        warn "Cannot determine GitHub Actions status"
    fi
fi

# ═══════════════════════════════════════════════════
section "F. SonarCloud Integration Tests"
# ═══════════════════════════════════════════════════

# F1: SonarCloud project exists (frontend)
SONAR_FRONTEND=$(curl -s "https://sonarcloud.io/api/components/show?component=SCPrime_PaiiD:frontend" --max-time 10 2>/dev/null)
if echo "$SONAR_FRONTEND" | grep -q '"key":"SCPrime_PaiiD:frontend"'; then
    pass "SonarCloud frontend project exists"
else
    fail "SonarCloud frontend project not found"
fi

# F2: SonarCloud project exists (backend)
SONAR_BACKEND=$(curl -s "https://sonarcloud.io/api/components/show?component=SCPrime_PaiiD:backend" --max-time 10 2>/dev/null)
if echo "$SONAR_BACKEND" | grep -q '"key":"SCPrime_PaiiD:backend"'; then
    pass "SonarCloud backend project exists"
else
    fail "SonarCloud backend project not found"
fi

# ═══════════════════════════════════════════════════
section "G. Deployment Verification"
# ═══════════════════════════════════════════════════

# G1: Check for expected features in frontend
if [ ! -z "$FRONTEND_HTML" ]; then
    # Check for radial menu
    if echo "$FRONTEND_HTML" | grep -qi "radial\|workflow"; then
        pass "Radial menu references found in HTML"
    else
        warn "Radial menu not detected (may load dynamically)"
    fi

    # Check for user setup
    if echo "$FRONTEND_HTML" | grep -qi "setup\|onboarding"; then
        pass "User setup/onboarding references found"
    else
        warn "User setup not detected (may load conditionally)"
    fi
fi

# G2: Backend version/build info
BACKEND_VERSION=$(curl -s "https://paiid-backend.onrender.com/docs" --max-time 10 2>/dev/null | grep -o '"version":"[^"]*"' || echo "NOT_FOUND")
if [ "$BACKEND_VERSION" != "NOT_FOUND" ]; then
    info "Backend API version: $BACKEND_VERSION"
fi

# ═══════════════════════════════════════════════════
section "H. Performance Tests"
# ═══════════════════════════════════════════════════

# H1: Frontend response time
START_TIME=$(date +%s%N)
curl -s -o /dev/null "https://paiid-frontend.onrender.com" --max-time 30 2>/dev/null
END_TIME=$(date +%s%N)
RESPONSE_TIME=$(( ($END_TIME - $START_TIME) / 1000000 ))

if [ $RESPONSE_TIME -lt 2000 ]; then
    pass "Frontend response time: ${RESPONSE_TIME}ms (excellent)"
elif [ $RESPONSE_TIME -lt 5000 ]; then
    pass "Frontend response time: ${RESPONSE_TIME}ms (acceptable)"
else
    warn "Frontend response time: ${RESPONSE_TIME}ms (slow)"
fi

# H2: Backend response time
START_TIME=$(date +%s%N)
curl -s -o /dev/null "https://paiid-backend.onrender.com/api/health" --max-time 30 2>/dev/null
END_TIME=$(date +%s%N)
BACKEND_TIME=$(( ($END_TIME - $START_TIME) / 1000000 ))

if [ $BACKEND_TIME -lt 1000 ]; then
    pass "Backend response time: ${BACKEND_TIME}ms (excellent)"
elif [ $BACKEND_TIME -lt 3000 ]; then
    pass "Backend response time: ${BACKEND_TIME}ms (acceptable)"
else
    warn "Backend response time: ${BACKEND_TIME}ms (may be cold start)"
fi

# ═══════════════════════════════════════════════════
section "📊 Test Summary"
# ═══════════════════════════════════════════════════

echo ""
echo "Total Tests: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
echo -e "${RED}Failed: $FAILED_TESTS${NC}"
echo ""

# Calculate success rate
if [ $TOTAL_TESTS -gt 0 ]; then
    SUCCESS_RATE=$(( ($PASSED_TESTS * 100) / $TOTAL_TESTS ))
    echo "Success Rate: ${SUCCESS_RATE}%"
    echo ""
fi

# Show failed tests
if [ ${#FAILED_TEST_NAMES[@]} -gt 0 ]; then
    echo -e "${RED}Failed Tests:${NC}"
    for test_name in "${FAILED_TEST_NAMES[@]}"; do
        echo -e "  ${RED}❌${NC} $test_name"
    done
    echo ""
fi

# Overall result
if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed! PaiiD is fully operational.${NC}"
    echo ""
    echo "✅ Next steps:"
    echo "   1. Open https://paiid-frontend.onrender.com in browser"
    echo "   2. Test all 10 workflow stages"
    echo "   3. Verify data loads correctly"
    exit 0
else
    echo -e "${RED}❌ Some tests failed. Review the output above for details.${NC}"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "   1. Check Render dashboard for service status"
    echo "   2. Review deployment logs for errors"
    echo "   3. Verify environment variables are set"
    echo "   4. See DEPLOYMENT_VERIFICATION_CHECKLIST.md"
    exit 1
fi
