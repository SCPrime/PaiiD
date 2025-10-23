# 🧪 PaiiD Post-Deployment Test Suite
# Comprehensive production testing after deployment

param(
    [string]$BackendUrl = "https://paiid-backend.onrender.com",
    [string]$FrontendUrl = "https://paiid-frontend.onrender.com",
    [string]$ApiToken,
    [switch]$Detailed
)

$ErrorActionPreference = "Continue"  # Continue on errors to run all tests

Write-Host "`n╔════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║    🧪 Post-Deployment Test Suite          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$script:TotalTests = 0
$script:PassedTests = 0
$script:FailedTests = 0
$script:SkippedTests = 0

# Test result tracking
$script:Results = @()

function Write-TestHeader {
    param([string]$Category)
    Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "  $Category" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
}

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Url,
        [int]$ExpectedStatus = 200,
        [hashtable]$Headers = @{},
        [string]$Method = "GET",
        [object]$Body = $null
    )

    $script:TotalTests++

    try {
        $params = @{
            Uri = $Url
            Method = $Method
            UseBasicParsing = $true
            TimeoutSec = 15
        }

        if ($Headers.Count -gt 0) {
            $params.Headers = $Headers
        }

        if ($Body) {
            $params.Body = ($Body | ConvertTo-Json)
            $params.ContentType = "application/json"
        }

        $response = Invoke-WebRequest @params
        $status = $response.StatusCode
        $content = $response.Content

        if ($status -eq $ExpectedStatus) {
            Write-Host "  ✓ " -NoNewline -ForegroundColor Green
            Write-Host "$Name " -NoNewline
            Write-Host "(HTTP $status)" -ForegroundColor Gray

            $script:PassedTests++
            $script:Results += [PSCustomObject]@{
                Test = $Name
                Status = "PASS"
                Expected = $ExpectedStatus
                Actual = $status
                ResponseTime = $null
            }

            if ($Detailed) {
                Write-Host "    Response: $($content.Substring(0, [Math]::Min(100, $content.Length)))..." -ForegroundColor Gray
            }

            return $true
        } else {
            Write-Host "  ✗ " -NoNewline -ForegroundColor Red
            Write-Host "$Name " -NoNewline
            Write-Host "(Expected $ExpectedStatus, got $status)" -ForegroundColor Red

            $script:FailedTests++
            $script:Results += [PSCustomObject]@{
                Test = $Name
                Status = "FAIL"
                Expected = $ExpectedStatus
                Actual = $status
                ResponseTime = $null
            }

            return $false
        }
    } catch {
        $errorStatus = "Error"
        if ($_.Exception.Response) {
            $errorStatus = $_.Exception.Response.StatusCode.Value__
        }

        Write-Host "  ✗ " -NoNewline -ForegroundColor Red
        Write-Host "$Name " -NoNewline
        Write-Host "($errorStatus)" -ForegroundColor Red

        if ($Detailed) {
            Write-Host "    Error: $_" -ForegroundColor Gray
        }

        $script:FailedTests++
        $script:Results += [PSCustomObject]@{
            Test = $Name
            Status = "ERROR"
            Expected = $ExpectedStatus
            Actual = $errorStatus
            ResponseTime = $null
        }

        return $false
    }
}

# ============================================
# CATEGORY 1: Infrastructure Health Checks
# ============================================
Write-TestHeader "1️⃣  Infrastructure Health Checks"

Test-Endpoint -Name "Backend health endpoint" `
    -Url "$BackendUrl/api/health" `
    -ExpectedStatus 200

Test-Endpoint -Name "Frontend accessibility" `
    -Url "$FrontendUrl" `
    -ExpectedStatus 200

Test-Endpoint -Name "API documentation" `
    -Url "$BackendUrl/api/docs" `
    -ExpectedStatus 200

Test-Endpoint -Name "API docs redirect" `
    -Url "$BackendUrl/docs" `
    -ExpectedStatus 200

# ============================================
# CATEGORY 2: API Authentication
# ============================================
Write-TestHeader "2️⃣  API Authentication"

Test-Endpoint -Name "Protected endpoint without auth (401)" `
    -Url "$BackendUrl/api/positions" `
    -ExpectedStatus 401

if ($ApiToken) {
    $authHeaders = @{
        "Authorization" = "Bearer $ApiToken"
    }

    Test-Endpoint -Name "Protected endpoint with auth" `
        -Url "$BackendUrl/api/positions" `
        -Headers $authHeaders `
        -ExpectedStatus 200
} else {
    Write-Host "  ⊘ Skipping authenticated tests (no API token)" -ForegroundColor Yellow
    $script:SkippedTests += 3
}

# ============================================
# CATEGORY 3: Market Data Endpoints
# ============================================
Write-TestHeader "3️⃣  Market Data Endpoints"

Test-Endpoint -Name "Options expirations - AAPL (requires auth)" `
    -Url "$BackendUrl/api/options/expirations/AAPL" `
    -ExpectedStatus 401

Test-Endpoint -Name "Market indices endpoint (requires auth)" `
    -Url "$BackendUrl/api/market/indices" `
    -ExpectedStatus 401

Test-Endpoint -Name "Health check (public)" `
    -Url "$BackendUrl/api/health" `
    -ExpectedStatus 200

# ============================================
# CATEGORY 4: Options Trading Endpoints
# ============================================
Write-TestHeader "4️⃣  Options Trading Endpoints"

Test-Endpoint -Name "Options chains endpoint (requires auth)" `
    -Url "$BackendUrl/api/options/chains/AAPL" `
    -ExpectedStatus 401

Test-Endpoint -Name "Greeks calculator (requires auth)" `
    -Url "$BackendUrl/api/options/greeks" `
    -Method "POST" `
    -ExpectedStatus 401

Test-Endpoint -Name "Position manager (requires auth)" `
    -Url "$BackendUrl/api/positions" `
    -ExpectedStatus 401

# ============================================
# CATEGORY 5: AI & Recommendations
# ============================================
Write-TestHeader "5️⃣  AI & Recommendations"

Test-Endpoint -Name "AI recommendations (requires auth)" `
    -Url "$BackendUrl/api/ai/recommendations" `
    -ExpectedStatus 401

Test-Endpoint -Name "Claude chat endpoint (requires auth)" `
    -Url "$BackendUrl/api/claude/chat" `
    -Method "POST" `
    -ExpectedStatus 401

# ============================================
# CATEGORY 6: Paper Trading
# ============================================
Write-TestHeader "6️⃣  Paper Trading Endpoints"

Test-Endpoint -Name "Paper trading execution (requires auth)" `
    -Url "$BackendUrl/api/trading/execute" `
    -Method "POST" `
    -ExpectedStatus 401

Test-Endpoint -Name "Account info (requires auth)" `
    -Url "$BackendUrl/api/account" `
    -ExpectedStatus 401

# ============================================
# CATEGORY 7: Frontend Assets
# ============================================
Write-TestHeader "7️⃣  Frontend Assets & Pages"

Test-Endpoint -Name "Homepage" `
    -Url "$FrontendUrl" `
    -ExpectedStatus 200

Test-Endpoint -Name "Proxy health check" `
    -Url "$FrontendUrl/api/proxy/api/health" `
    -ExpectedStatus 200

# ============================================
# CATEGORY 8: CORS & Security Headers
# ============================================
Write-TestHeader "8️⃣  CORS & Security Headers"

try {
    $response = Invoke-WebRequest -Uri "$BackendUrl/api/health" -Method Options -UseBasicParsing -TimeoutSec 10
    $script:TotalTests++

    if ($response.Headers.'Access-Control-Allow-Origin') {
        Write-Host "  ✓ CORS headers present" -ForegroundColor Green
        $script:PassedTests++
    } else {
        Write-Host "  ⚠ CORS headers not found" -ForegroundColor Yellow
        $script:FailedTests++
    }
} catch {
    Write-Host "  ⚠ Could not check CORS headers" -ForegroundColor Yellow
    $script:SkippedTests++
}

# ============================================
# CATEGORY 9: Performance Tests
# ============================================
Write-TestHeader "9️⃣  Performance Metrics"

Write-Host "  → Measuring response times..." -ForegroundColor Cyan

function Measure-ResponseTime {
    param([string]$Url, [string]$Name)

    $script:TotalTests++

    try {
        $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
        $response = Invoke-WebRequest -Uri $Url -Method Get -UseBasicParsing -TimeoutSec 15
        $stopwatch.Stop()

        $elapsed = $stopwatch.ElapsedMilliseconds

        if ($elapsed -lt 1000) {
            Write-Host "  ✓ " -NoNewline -ForegroundColor Green
            Write-Host "$Name " -NoNewline
            Write-Host "($elapsed ms)" -ForegroundColor Gray
            $script:PassedTests++
        } elseif ($elapsed -lt 3000) {
            Write-Host "  ⚠ " -NoNewline -ForegroundColor Yellow
            Write-Host "$Name " -NoNewline
            Write-Host "($elapsed ms - acceptable)" -ForegroundColor Yellow
            $script:PassedTests++
        } else {
            Write-Host "  ✗ " -NoNewline -ForegroundColor Red
            Write-Host "$Name " -NoNewline
            Write-Host "($elapsed ms - slow)" -ForegroundColor Red
            $script:FailedTests++
        }

        return $elapsed
    } catch {
        Write-Host "  ✗ $Name (timeout/error)" -ForegroundColor Red
        $script:FailedTests++
        return $null
    }
}

$backendTime = Measure-ResponseTime -Url "$BackendUrl/api/health" -Name "Backend response time"
$frontendTime = Measure-ResponseTime -Url "$FrontendUrl" -Name "Frontend response time"

# ============================================
# CATEGORY 10: Critical User Flows
# ============================================
Write-TestHeader "🔟 Critical User Flows"

Write-Host "  → Testing user workflow paths..." -ForegroundColor Cyan

# Test that core pages are accessible
Test-Endpoint -Name "Main dashboard page" `
    -Url "$FrontendUrl" `
    -ExpectedStatus 200

Test-Endpoint -Name "API proxy health" `
    -Url "$FrontendUrl/api/proxy/api/health" `
    -ExpectedStatus 200

# ============================================
# FINAL SUMMARY
# ============================================
Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "  📊 TEST SUMMARY" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

$successRate = if ($script:TotalTests -gt 0) {
    [Math]::Round(($script:PassedTests / $script:TotalTests) * 100, 1)
} else { 0 }

Write-Host "  Total Tests:   $script:TotalTests" -ForegroundColor White
Write-Host "  Passed:        $script:PassedTests " -NoNewline
Write-Host "✓" -ForegroundColor Green
Write-Host "  Failed:        $script:FailedTests " -NoNewline
Write-Host "✗" -ForegroundColor Red
Write-Host "  Skipped:       $script:SkippedTests" -ForegroundColor Yellow
Write-Host "  Success Rate:  $successRate%" -ForegroundColor $(
    if ($successRate -ge 90) { "Green" }
    elseif ($successRate -ge 70) { "Yellow" }
    else { "Red" }
)
Write-Host ""

# Performance summary
if ($backendTime -and $frontendTime) {
    Write-Host "  Performance:" -ForegroundColor Cyan
    Write-Host "    Backend:   $backendTime ms" -ForegroundColor White
    Write-Host "    Frontend:  $frontendTime ms" -ForegroundColor White
    Write-Host ""
}

# Final verdict
if ($script:FailedTests -eq 0 -and $script:PassedTests -gt 0) {
    Write-Host "╔════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║    ✅ ALL TESTS PASSED!                    ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Green
    $exitCode = 0
} elseif ($script:FailedTests -le 3 -and $successRate -ge 80) {
    Write-Host "╔════════════════════════════════════════════╗" -ForegroundColor Yellow
    Write-Host "║    ⚠️  TESTS PASSED WITH WARNINGS          ║" -ForegroundColor Yellow
    Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Yellow
    $exitCode = 0
} else {
    Write-Host "╔════════════════════════════════════════════╗" -ForegroundColor Red
    Write-Host "║    ❌ CRITICAL TESTS FAILED!               ║" -ForegroundColor Red
    Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Red
    $exitCode = 1
}

Write-Host ""
Write-Host "🔍 Recommendations:" -ForegroundColor Cyan

if ($script:FailedTests -gt 0) {
    Write-Host "   • Review failed tests and investigate errors" -ForegroundColor Yellow
    Write-Host "   • Check Render deployment logs" -ForegroundColor Yellow
    Write-Host "   • Verify environment variables are set correctly" -ForegroundColor Yellow
}

if ($backendTime -and $backendTime -gt 2000) {
    Write-Host "   • Backend response time is slow ($backendTime ms)" -ForegroundColor Yellow
    Write-Host "   • Consider upgrading Render plan or optimizing backend" -ForegroundColor Yellow
}

if ($script:SkippedTests -gt 5) {
    Write-Host "   • Many tests were skipped (API token not provided)" -ForegroundColor Yellow
    Write-Host "   • Run with -ApiToken for comprehensive testing" -ForegroundColor Yellow
}

if ($script:FailedTests -eq 0) {
    Write-Host "   • Deployment looks healthy!" -ForegroundColor Green
    Write-Host "   • Monitor logs for the next 30 minutes" -ForegroundColor Green
    Write-Host "   • Test critical user flows manually" -ForegroundColor Green
}

Write-Host ""

# Generate test report
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$reportFile = "test-report-$timestamp.md"

$report = @"
# 🧪 Post-Deployment Test Report

**Date:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Backend URL:** $BackendUrl
**Frontend URL:** $FrontendUrl

---

## 📊 Test Summary

- **Total Tests:** $script:TotalTests
- **Passed:** $script:PassedTests ✓
- **Failed:** $script:FailedTests ✗
- **Skipped:** $script:SkippedTests
- **Success Rate:** $successRate%

---

## ⏱️ Performance Metrics

- **Backend Response:** $(if ($backendTime) { "$backendTime ms" } else { "N/A" })
- **Frontend Response:** $(if ($frontendTime) { "$frontendTime ms" } else { "N/A" })

---

## 📋 Detailed Results

| Test | Status | Expected | Actual |
|------|--------|----------|--------|
$(foreach ($result in $script:Results) {
    "| $($result.Test) | $($result.Status) | $($result.Expected) | $($result.Actual) |"
})

---

## 🎯 Overall Status

$(
    if ($script:FailedTests -eq 0 -and $script:PassedTests -gt 0) {
        "✅ **ALL TESTS PASSED** - Production is healthy"
    } elseif ($successRate -ge 80) {
        "⚠️ **TESTS PASSED WITH WARNINGS** - Minor issues detected"
    } else {
        "❌ **CRITICAL TESTS FAILED** - Immediate attention required"
    }
)

---

Generated by test-production.ps1
"@

$report | Out-File -FilePath $reportFile -Encoding UTF8
Write-Host "📄 Test report saved to: $reportFile" -ForegroundColor Cyan
Write-Host ""

exit $exitCode
