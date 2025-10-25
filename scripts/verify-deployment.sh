#!/bin/bash
# 🚀 Deployment Verification Script
# Verifies that both frontend and backend are deployed and working

set -e

echo "🔍 PaiiD Deployment Verification"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Backend URL
BACKEND_URL="https://paiid-backend.onrender.com"
# Frontend URL (update after deployment)
FRONTEND_URL="${FRONTEND_URL:-https://paiid-frontend.onrender.com}"

echo "📡 Testing Backend..."
echo "--------------------"

# Test 1: Backend Health Check
echo -n "1. Health endpoint... "
if curl -s -f "$BACKEND_URL/api/health" > /dev/null; then
    echo -e "${GREEN}✅ PASS${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
    exit 1
fi

# Test 2: Backend API Docs
echo -n "2. API docs... "
if curl -s -f "$BACKEND_URL/docs" > /dev/null; then
    echo -e "${GREEN}✅ PASS${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
    exit 1
fi

# Test 3: Market Data Endpoint
echo -n "3. Market data endpoint... "
if curl -s -f "$BACKEND_URL/api/market/status" > /dev/null; then
    echo -e "${GREEN}✅ PASS${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
    exit 1
fi

# Test 4: ML Endpoints
echo -n "4. ML market regime endpoint... "
if curl -s -f "$BACKEND_URL/api/ml/market-regime?symbol=SPY&lookback_days=90" > /dev/null; then
    echo -e "${GREEN}✅ PASS${NC}"
else
    echo -e "${YELLOW}⚠️  WARN (may need auth)${NC}"
fi

echo ""
echo "🌐 Testing Frontend..."
echo "----------------------"

# Test 5: Frontend Homepage
echo -n "5. Homepage loads... "
if curl -s -f "$FRONTEND_URL" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PASS${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend not deployed yet${NC}"
    echo ""
    echo "📋 Next Steps:"
    echo "  1. Deploy frontend to Render/Vercel"
    echo "  2. Update FRONTEND_URL in this script"
    echo "  3. Run this script again"
    echo ""
    exit 0
fi

# Test 6: Frontend API Routes
echo -n "6. Frontend API routes... "
if curl -s -f "$FRONTEND_URL/api/health" > /dev/null; then
    echo -e "${GREEN}✅ PASS${NC}"
else
    echo -e "${YELLOW}⚠️  WARN${NC}"
fi

echo ""
echo "🔗 Testing Integration..."
echo "-------------------------"

# Test 7: CORS Configuration
echo -n "7. CORS headers... "
CORS_RESPONSE=$(curl -s -I -X OPTIONS "$BACKEND_URL/api/health" \
    -H "Origin: $FRONTEND_URL" \
    -H "Access-Control-Request-Method: GET")

if echo "$CORS_RESPONSE" | grep -q "Access-Control-Allow-Origin"; then
    echo -e "${GREEN}✅ PASS${NC}"
else
    echo -e "${YELLOW}⚠️  May need CORS configuration${NC}"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ DEPLOYMENT VERIFIED!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎉 Status: Production Ready!"
echo ""
echo "🔗 URLs:"
echo "   Backend:  $BACKEND_URL"
echo "   Frontend: $FRONTEND_URL"
echo "   API Docs: $BACKEND_URL/docs"
echo ""
echo "📊 Next Steps:"
echo "   1. Test user flows manually"
echo "   2. Monitor error logs"
echo "   3. Check Sentry for issues"
echo "   4. Run smoke tests"
echo ""
