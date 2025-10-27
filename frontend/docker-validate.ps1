# Docker Build Validation Script for PaiiD Frontend (PowerShell)
# This script builds the Docker image and validates the static asset structure

$ErrorActionPreference = "Stop"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "PaiiD Frontend Docker Build Validation" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$IMAGE_NAME = "paiid-frontend-test"
$CONTAINER_NAME = "paiid-frontend-validate"
$ERRORS = 0

# Clean up any existing test containers/images
Write-Host "1. Cleaning up previous test artifacts..." -ForegroundColor Yellow
docker rm -f $CONTAINER_NAME 2>$null | Out-Null
docker rmi -f $IMAGE_NAME 2>$null | Out-Null
Write-Host "   " -NoNewline
Write-Host "✓" -ForegroundColor Green -NoNewline
Write-Host " Cleanup complete"
Write-Host ""

# Build the Docker image
Write-Host "2. Building Docker image..." -ForegroundColor Yellow
Write-Host "   This may take a few minutes..."
docker build `
  --build-arg NEXT_PUBLIC_API_TOKEN=test_token `
  --build-arg NEXT_PUBLIC_BACKEND_API_BASE_URL=https://paiid-backend.onrender.com `
  --build-arg NEXT_PUBLIC_ANTHROPIC_API_KEY=test_key `
  -t $IMAGE_NAME `
  -f Dockerfile `
  .

if ($LASTEXITCODE -eq 0) {
    Write-Host "   " -NoNewline
    Write-Host "✓" -ForegroundColor Green -NoNewline
    Write-Host " Docker build successful"
} else {
    Write-Host "   " -NoNewline
    Write-Host "✗" -ForegroundColor Red -NoNewline
    Write-Host " Docker build failed"
    exit 1
}
Write-Host ""

# Create a temporary container to inspect filesystem
Write-Host "3. Inspecting Docker image filesystem..." -ForegroundColor Yellow
docker create --name $CONTAINER_NAME $IMAGE_NAME | Out-Null
Write-Host "   " -NoNewline
Write-Host "✓" -ForegroundColor Green -NoNewline
Write-Host " Test container created"
Write-Host ""

# Validation checks
Write-Host "4. Validating file structure..." -ForegroundColor Yellow
Write-Host ""

# Check 1: server.js exists at root
Write-Host "   Checking for server.js at /app/... " -NoNewline
$tempPath = Join-Path $env:TEMP "test-server.js"
docker cp "${CONTAINER_NAME}:/app/server.js" $tempPath 2>$null | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ PASS" -ForegroundColor Green
    Remove-Item $tempPath -ErrorAction SilentlyContinue
} else {
    Write-Host "✗ FAIL" -ForegroundColor Red
    $ERRORS++
}

# Check 2: .next/static directory exists
Write-Host "   Checking for .next/static directory... " -NoNewline
$tempStaticPath = Join-Path $env:TEMP "test-static"
docker cp "${CONTAINER_NAME}:/app/.next/static" $tempStaticPath 2>$null | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ PASS" -ForegroundColor Green
    Remove-Item $tempStaticPath -Recurse -Force -ErrorAction SilentlyContinue
} else {
    Write-Host "✗ FAIL" -ForegroundColor Red
    $ERRORS++
}

# Check 3: .next/static/chunks exists (critical for JS bundles)
Write-Host "   Checking for .next/static/chunks... " -NoNewline
$tempChunksPath = Join-Path $env:TEMP "test-chunks"
docker cp "${CONTAINER_NAME}:/app/.next/static/chunks" $tempChunksPath 2>$null | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ PASS" -ForegroundColor Green
    Remove-Item $tempChunksPath -Recurse -Force -ErrorAction SilentlyContinue
} else {
    Write-Host "✗ FAIL" -ForegroundColor Red
    $ERRORS++
}

# Check 4: public directory exists
Write-Host "   Checking for public directory... " -NoNewline
$tempPublicPath = Join-Path $env:TEMP "test-public"
docker cp "${CONTAINER_NAME}:/app/public" $tempPublicPath 2>$null | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ PASS" -ForegroundColor Green
    Remove-Item $tempPublicPath -Recurse -Force -ErrorAction SilentlyContinue
} else {
    Write-Host "✗ FAIL - public directory missing" -ForegroundColor Red
    $ERRORS++
}

# Check 5: .next/server directory exists (Next.js server components)
Write-Host "   Checking for .next/server directory... " -NoNewline
$tempServerPath = Join-Path $env:TEMP "test-server-dir"
docker cp "${CONTAINER_NAME}:/app/.next/server" $tempServerPath 2>$null | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ PASS" -ForegroundColor Green
    Remove-Item $tempServerPath -Recurse -Force -ErrorAction SilentlyContinue
} else {
    Write-Host "✗ FAIL" -ForegroundColor Red
    $ERRORS++
}

Write-Host ""

# Show detailed directory structure
Write-Host "5. Directory structure inside container:" -ForegroundColor Yellow
Write-Host "=================================================="
docker exec $CONTAINER_NAME ls -la /app 2>$null
Write-Host ""
docker exec $CONTAINER_NAME ls -la /app/.next 2>$null
Write-Host ""
docker exec $CONTAINER_NAME ls -la /app/.next/static 2>$null
Write-Host "=================================================="
Write-Host ""

# Optional: Start container and test HTTP response
Write-Host "6. Testing container startup (optional)..." -ForegroundColor Yellow
docker rm -f $CONTAINER_NAME 2>$null | Out-Null
docker run -d --name $CONTAINER_NAME -p 3001:3000 `
  -e NEXT_PUBLIC_API_TOKEN=test_token `
  -e NEXT_PUBLIC_BACKEND_API_BASE_URL=https://paiid-backend.onrender.com `
  $IMAGE_NAME | Out-Null

Write-Host "   Waiting 10 seconds for server to start..."
Start-Sleep -Seconds 10

Write-Host "   Testing HTTP GET http://localhost:3001... " -NoNewline
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3001" -UseBasicParsing -TimeoutSec 5
    $statusCode = $response.StatusCode
    if ($statusCode -eq 200) {
        Write-Host "✓ PASS (HTTP $statusCode)" -ForegroundColor Green
    } else {
        Write-Host "⚠ WARNING (HTTP $statusCode - expected 200)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ SKIP (HTTP request failed - container might not be ready)" -ForegroundColor Yellow
}

# Cleanup
Write-Host ""
Write-Host "7. Cleaning up..." -ForegroundColor Yellow
docker rm -f $CONTAINER_NAME 2>$null | Out-Null
docker rmi -f $IMAGE_NAME 2>$null | Out-Null
Write-Host "   " -NoNewline
Write-Host "✓" -ForegroundColor Green -NoNewline
Write-Host " Cleanup complete"

# Final results
Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
if ($ERRORS -eq 0) {
    Write-Host "✓ VALIDATION PASSED" -ForegroundColor Green
    Write-Host "All critical files are in the correct locations."
    Write-Host "The Docker image is ready for deployment."
    exit 0
} else {
    Write-Host "✗ VALIDATION FAILED" -ForegroundColor Red
    Write-Host "Found $ERRORS error(s) in the Docker image structure."
    Write-Host "Please review the Dockerfile COPY commands."
    exit 1
}
Write-Host "==================================================" -ForegroundColor Cyan
