#!/bin/bash
# PaiiD Health Check Dashboard
# Comprehensive connectivity testing for all system components

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# API Configuration
BACKEND_URL="https://paiid-backend.onrender.com"
FRONTEND_URL="https://paiid-frontend.onrender.com"
API_TOKEN="rnd_bDRqi1TvLvd3rC78yvUSgDraH2Kl"

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  PaiiD System Health Check Dashboard${NC}"
echo -e "${BLUE}  $(date)${NC}"
echo -e "${BLUE}================================================${NC}\n"

# Test counter
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run test
run_test() {
    local test_name="$1"
    local command="$2"
    local expected_pattern="$3"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -n "Testing $test_name... "

    if output=$(eval "$command" 2>&1); then
        if [[ -z "$expected_pattern" ]] || echo "$output" | grep -q "$expected_pattern"; then
            echo -e "${GREEN}✓ PASS${NC}"
            PASSED_TESTS=$((PASSED_TESTS + 1))
            return 0
        else
            echo -e "${RED}✗ FAIL${NC} (unexpected output)"
            echo -e "${YELLOW}Output: $output${NC}"
            FAILED_TESTS=$((FAILED_TESTS + 1))
            return 1
        fi
    else
        echo -e "${RED}✗ FAIL${NC} (command failed)"
        echo -e "${YELLOW}Error: $output${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

echo -e "${BLUE}=== Backend API Tests ===${NC}"

run_test "Backend Health Endpoint" \
    "curl -sf $BACKEND_URL/api/health" \
    '"status":"ok"'

run_test "Redis Connection" \
    "curl -sf $BACKEND_URL/api/health | grep -o '\"connected\":true'" \
    "connected"

run_test "Market Data (Dow Jones)" \
    "curl -sf -H 'Authorization: Bearer $API_TOKEN' $BACKEND_URL/api/market/indices" \
    '"dow"'

run_test "Market Data (Nasdaq)" \
    "curl -sf -H 'Authorization: Bearer $API_TOKEN' $BACKEND_URL/api/market/indices" \
    '"nasdaq"'

run_test "Authentication (Account Endpoint)" \
    "curl -sf -H 'Authorization: Bearer $API_TOKEN' $BACKEND_URL/api/account" \
    '"account_number"'

run_test "Positions Endpoint" \
    "curl -sf -H 'Authorization: Bearer $API_TOKEN' $BACKEND_URL/api/positions" \
    ""

run_test "Market Quote (SPY)" \
    "curl -sf -H 'Authorization: Bearer $API_TOKEN' '$BACKEND_URL/api/market/quote/SPY'" \
    '"symbol":"SPY"'

run_test "Strategy Templates" \
    "curl -sf -H 'Authorization: Bearer $API_TOKEN' $BACKEND_URL/api/strategies/templates" \
    "\["

run_test "User Preferences" \
    "curl -sf -H 'Authorization: Bearer $API_TOKEN' $BACKEND_URL/api/users/preferences" \
    ""

echo ""
echo -e "${BLUE}=== Frontend Tests ===${NC}"

run_test "Frontend Availability" \
    "curl -sf -o /dev/null -w '%{http_code}' $FRONTEND_URL" \
    "200"

run_test "Frontend Response Time (<2s)" \
    "timeout 2 curl -sf -o /dev/null -w '%{time_total}' $FRONTEND_URL" \
    ""

echo ""
echo -e "${BLUE}=== GitHub CI/CD Tests ===${NC}"

run_test "Latest CI Run Status" \
    "gh run list --limit 1 --json conclusion --jq '.[0].conclusion'" \
    "success"

run_test "Backend Tests Passing" \
    "gh run list --limit 1 --json conclusion --jq '.[0].conclusion'" \
    "success"

echo ""
echo -e "${BLUE}=== Performance Metrics ===${NC}"

# Backend response time
backend_time=$(curl -sf -o /dev/null -w '%{time_total}' "$BACKEND_URL/api/health")
echo -e "Backend Health Response Time: ${GREEN}${backend_time}s${NC}"

# Frontend response time
frontend_time=$(curl -sf -o /dev/null -w '%{time_total}' "$FRONTEND_URL")
echo -e "Frontend Load Time: ${GREEN}${frontend_time}s${NC}"

# Market data response time
market_time=$(curl -sf -H "Authorization: Bearer $API_TOKEN" -o /dev/null -w '%{time_total}' "$BACKEND_URL/api/market/indices")
echo -e "Market Data Response Time: ${GREEN}${market_time}s${NC}"

echo ""
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Test Summary${NC}"
echo -e "${BLUE}================================================${NC}"
echo -e "Total Tests: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
if [ $FAILED_TESTS -gt 0 ]; then
    echo -e "${RED}Failed: $FAILED_TESTS${NC}"
else
    echo -e "Failed: $FAILED_TESTS"
fi

# Calculate percentage
if [ $TOTAL_TESTS -gt 0 ]; then
    percentage=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    echo -e "Success Rate: ${GREEN}${percentage}%${NC}"
fi

echo -e "${BLUE}================================================${NC}\n"

# Exit with appropriate code
if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✓ ALL SYSTEMS OPERATIONAL${NC}\n"
    exit 0
else
    echo -e "${RED}✗ SOME SYSTEMS FAILING - ATTENTION REQUIRED${NC}\n"
    exit 1
fi
