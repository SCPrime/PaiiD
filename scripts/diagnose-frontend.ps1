# Frontend Diagnostic Script
# Purpose: Check frontend SSE endpoint and proxy configuration

Write-Host ""
Write-Host "=== PaiiD Frontend Diagnostics ===" -ForegroundColor Cyan
Write-Host ""

$frontendUrl = "http://localhost:3001"
$backendUrl = "http://127.0.0.1:8001"

# 1. Check if frontend is running
Write-Host "1. Checking frontend (port 3001)..." -ForegroundColor Yellow
try {
    $frontendResponse = Invoke-WebRequest -Uri $frontendUrl -TimeoutSec 5 -UseBasicParsing
    Write-Host "   ✅ Frontend is running (HTTP $($frontendResponse.StatusCode))" -ForegroundColor Green
}
catch {
    Write-Host "   ❌ Frontend is NOT accessible: $_" -ForegroundColor Red
    exit 1
}

# 2. Check if backend is running
Write-Host ""
Write-Host "2. Checking backend (port 8001)..." -ForegroundColor Yellow
try {
    $backendResponse = Invoke-WebRequest -Uri "$backendUrl/api/health" -TimeoutSec 5 -UseBasicParsing
    Write-Host "   ✅ Backend is running (HTTP $($backendResponse.StatusCode))" -ForegroundColor Green
}
catch {
    Write-Host "   ❌ Backend is NOT accessible: $_" -ForegroundColor Red
    exit 1
}

# 3. Test SSE endpoint through proxy
Write-Host ""
Write-Host "3. Testing SSE endpoint through proxy..." -ForegroundColor Yellow
try {
    $sseUrl = "$frontendUrl/api/proxy/stream/market-indices"
    Write-Host "   Testing: $sseUrl" -ForegroundColor Gray

    $response = Invoke-WebRequest -Uri $sseUrl -TimeoutSec 5 -UseBasicParsing
    Write-Host "   ✅ SSE endpoint accessible (HTTP $($response.StatusCode))" -ForegroundColor Green
    Write-Host "   Content-Type: $($response.Headers['Content-Type'])" -ForegroundColor Gray
}
catch {
    Write-Host "   ❌ SSE endpoint failed: $_" -ForegroundColor Red
    Write-Host "   Error details: $($_.Exception.Message)" -ForegroundColor Red
}

# 4. Test direct backend SSE endpoint
Write-Host ""
Write-Host "4. Testing direct backend SSE endpoint..." -ForegroundColor Yellow
try {
    $directSseUrl = "$backendUrl/api/stream/market-indices"
    Write-Host "   Testing: $directSseUrl" -ForegroundColor Gray

    $response = Invoke-WebRequest -Uri $directSseUrl -TimeoutSec 5 -UseBasicParsing
    Write-Host "   ✅ Direct backend SSE works (HTTP $($response.StatusCode))" -ForegroundColor Green
}
catch {
    Write-Host "   ❌ Direct backend SSE failed: $_" -ForegroundColor Red
}

# 5. Check proxy health
Write-Host ""
Write-Host "5. Testing proxy health endpoint..." -ForegroundColor Yellow
try {
    $proxyHealthUrl = "$frontendUrl/api/proxy/health"
    $response = Invoke-WebRequest -Uri $proxyHealthUrl -TimeoutSec 5 -UseBasicParsing
    Write-Host "   ✅ Proxy health check passed (HTTP $($response.StatusCode))" -ForegroundColor Green
    Write-Host "   Response: $($response.Content.Substring(0, [Math]::Min(100, $response.Content.Length)))" -ForegroundColor Gray
}
catch {
    Write-Host "   ❌ Proxy health check failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Diagnostic Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Check browser console (F12) for exact error messages" -ForegroundColor Gray
Write-Host "2. Look for CORS errors, 403 Forbidden, or connection refused" -ForegroundColor Gray
Write-Host "3. Share the console errors with Claude for analysis" -ForegroundColor Gray
Write-Host ""
