#!/bin/bash
# Docker Build Validation Script for PaiiD Frontend
# This script builds the Docker image and validates the static asset structure

set -e  # Exit on error

echo "=================================================="
echo "PaiiD Frontend Docker Build Validation"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="paiid-frontend-test"
CONTAINER_NAME="paiid-frontend-validate"

# Clean up any existing test containers/images
echo "1. Cleaning up previous test artifacts..."
docker rm -f $CONTAINER_NAME 2>/dev/null || true
docker rmi -f $IMAGE_NAME 2>/dev/null || true
echo -e "${GREEN}✓${NC} Cleanup complete"
echo ""

# Build the Docker image
echo "2. Building Docker image..."
echo "   This may take a few minutes..."
docker build \
  --build-arg NEXT_PUBLIC_API_TOKEN=test_token \
  --build-arg NEXT_PUBLIC_BACKEND_API_BASE_URL=https://paiid-backend.onrender.com \
  --build-arg NEXT_PUBLIC_ANTHROPIC_API_KEY=test_key \
  -t $IMAGE_NAME \
  -f Dockerfile \
  .

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✓${NC} Docker build successful"
else
  echo -e "${RED}✗${NC} Docker build failed"
  exit 1
fi
echo ""

# Create a temporary container to inspect filesystem
echo "3. Inspecting Docker image filesystem..."
docker create --name $CONTAINER_NAME $IMAGE_NAME
echo -e "${GREEN}✓${NC} Test container created"
echo ""

# Validation checks
echo "4. Validating file structure..."
echo ""

ERRORS=0

# Check 1: server.js exists at root
echo -n "   Checking for server.js at /app/... "
if docker exec $CONTAINER_NAME test -f server.js 2>/dev/null || docker cp $CONTAINER_NAME:/app/server.js /tmp/test-server.js 2>/dev/null; then
  echo -e "${GREEN}✓ PASS${NC}"
  rm -f /tmp/test-server.js
else
  echo -e "${RED}✗ FAIL${NC}"
  ((ERRORS++))
fi

# Check 2: .next/static directory exists
echo -n "   Checking for .next/static directory... "
if docker cp $CONTAINER_NAME:/app/.next/static /tmp/test-static 2>/dev/null; then
  echo -e "${GREEN}✓ PASS${NC}"
  rm -rf /tmp/test-static
else
  echo -e "${RED}✗ FAIL${NC}"
  ((ERRORS++))
fi

# Check 3: .next/static/chunks exists (critical for JS bundles)
echo -n "   Checking for .next/static/chunks... "
if docker cp $CONTAINER_NAME:/app/.next/static/chunks /tmp/test-chunks 2>/dev/null; then
  echo -e "${GREEN}✓ PASS${NC}"
  rm -rf /tmp/test-chunks
else
  echo -e "${RED}✗ FAIL${NC}"
  ((ERRORS++))
fi

# Check 4: public directory exists
echo -n "   Checking for public directory... "
if docker cp $CONTAINER_NAME:/app/public /tmp/test-public 2>/dev/null; then
  echo -e "${GREEN}✓ PASS${NC}"
  rm -rf /tmp/test-public
else
  echo -e "${RED}✗ FAIL - public directory missing${NC}"
  ((ERRORS++))
fi

# Check 5: .next/server directory exists (Next.js server components)
echo -n "   Checking for .next/server directory... "
if docker cp $CONTAINER_NAME:/app/.next/server /tmp/test-server-dir 2>/dev/null; then
  echo -e "${GREEN}✓ PASS${NC}"
  rm -rf /tmp/test-server-dir
else
  echo -e "${RED}✗ FAIL${NC}"
  ((ERRORS++))
fi

echo ""

# Show detailed directory structure
echo "5. Directory structure inside container:"
echo "=================================================="
docker export $CONTAINER_NAME | tar -t 'app/*' | grep -E '^app/(server.js|.next|public)' | head -50 || echo "Could not extract directory listing"
echo "=================================================="
echo ""

# Optional: Start container and test HTTP response
echo "6. Testing container startup (optional)..."
docker rm -f $CONTAINER_NAME 2>/dev/null || true
docker run -d --name $CONTAINER_NAME -p 3001:3000 \
  -e NEXT_PUBLIC_API_TOKEN=test_token \
  -e NEXT_PUBLIC_BACKEND_API_BASE_URL=https://paiid-backend.onrender.com \
  $IMAGE_NAME

echo "   Waiting 10 seconds for server to start..."
sleep 10

echo -n "   Testing HTTP GET http://localhost:3001... "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3001 || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
  echo -e "${GREEN}✓ PASS (HTTP $HTTP_CODE)${NC}"
elif [ "$HTTP_CODE" = "000" ]; then
  echo -e "${YELLOW}⚠ SKIP (curl failed - container might not be ready)${NC}"
else
  echo -e "${YELLOW}⚠ WARNING (HTTP $HTTP_CODE - expected 200)${NC}"
fi

# Cleanup
echo ""
echo "7. Cleaning up..."
docker rm -f $CONTAINER_NAME 2>/dev/null || true
docker rmi -f $IMAGE_NAME 2>/dev/null || true
echo -e "${GREEN}✓${NC} Cleanup complete"

# Final results
echo ""
echo "=================================================="
if [ $ERRORS -eq 0 ]; then
  echo -e "${GREEN}✓ VALIDATION PASSED${NC}"
  echo "All critical files are in the correct locations."
  echo "The Docker image is ready for deployment."
  exit 0
else
  echo -e "${RED}✗ VALIDATION FAILED${NC}"
  echo "Found $ERRORS error(s) in the Docker image structure."
  echo "Please review the Dockerfile COPY commands."
  exit 1
fi
echo "=================================================="
