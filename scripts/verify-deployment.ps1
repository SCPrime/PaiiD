# PaiiD Deployment Verification Script (PowerShell)
# Comprehensive verification of deployed services

param(
    [string]$BackendUrl = "https://paiid-backend.onrender.com",
    [string]$FrontendUrl = "https://paiid-frontend.onrender.com",
    [switch]$Verbose,
    [int]$Timeout = 10
)

$ErrorActionPreference = "Stop"

# Test result tracking
$script:TestsPassed = 0
$script:TestsFailed = 0
$script:FailedTests = @()

# Logging functions
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-Test {
    param([string]$Message)
    Write-Host "[TEST] $Message" -ForegroundColor Cyan
}

# Test function
function Test-Endpoint {
    param(
        [string]$TestName,
        [string]$Url,
        [string]$ExpectedContent = "",
        [string]$Description = ""
    )
    
    Write-Test $TestName
    if ($Verbose) {
        Write-Host "  URL: $Url" -ForegroundColor Gray
        Write-Host "  Expected: $ExpectedContent" -ForegroundColor Gray
        Write-Host "  Description: $Description" -ForegroundColor Gray
    }
    
    try {
        $startTime = Get-Date
        $response = Invoke-RestMethod -Uri $Url -Method GET -TimeoutSec $Timeout -ErrorAction Stop
        $endTime = Get-Date
        $responseTime = ($endTime - $startTime).TotalMilliseconds
        
        if ($ExpectedContent) {
            $responseText = $response | ConvertTo-Json -Compress
            if ($responseText -match $ExpectedContent) {
                Write-Success "✓ $TestName - PASS ($([math]::Round($responseTime))ms)"
                $script:TestsPassed++
                return $true
            } else {
                Write-Error "✗ $TestName - FAIL (content mismatch)"
                if ($Verbose) {
                    Write-Host "  Expected: $ExpectedContent" -ForegroundColor Gray
                    Write-Host "  Got: $responseText" -ForegroundColor Gray
                }
                $script:TestsFailed++
                $script:FailedTests += $TestName
                return $false
            }
        } else {
            Write-Success "✓ $TestName - PASS ($([math]::Round($responseTime))ms)"
            $script:TestsPassed++
            return $true
        }
    } catch {
        Write-Error "✗ $TestName - FAIL ($($_.Exception.Message))"
        $script:TestsFailed++
        $script:FailedTests += $TestName
        return $false
    }
}

# Health endpoint tests
function Test-HealthEndpoints {
    Write-Info "Testing health endpoints..."
    
    Test-Endpoint -TestName "Backend Health" `
        -Url "$BackendUrl/api/health" `
        -ExpectedContent "healthy" `
        -Description "Basic health check"
    
    Test-Endpoint -TestName "Backend Detailed Health" `
        -Url "$BackendUrl/api/health/detailed" `
        -ExpectedContent "status" `
        -Description "Detailed health information"
    
    Test-Endpoint -TestName "Backend Readiness" `
        -Url "$BackendUrl/api/health/readiness" `
        -ExpectedContent "ready" `
        -Description "Readiness check"
    
    Test-Endpoint -TestName "Backend Liveness" `
        -Url "$BackendUrl/api/health/liveness" `
        -ExpectedContent "alive" `
        -Description "Liveness check"
}

# API endpoint tests
function Test-ApiEndpoints {
    Write-Info "Testing API endpoints..."
    
    Test-Endpoint -TestName "Backend Settings" `
        -Url "$BackendUrl/api/settings" `
        -ExpectedContent "stop_loss" `
        -Description "Settings endpoint"
    
    Test-Endpoint -TestName "Backend Configuration" `
        -Url "$BackendUrl/api/settings/config" `
        -ExpectedContent "environment" `
        -Description "Configuration endpoint"
    
    Test-Endpoint -TestName "Backend Market Conditions" `
        -Url "$BackendUrl/api/market/conditions" `
        -ExpectedContent "conditions" `
        -Description "Market conditions endpoint"
    
    Test-Endpoint -TestName "Backend Market Indices" `
        -Url "$BackendUrl/api/market/indices" `
        -ExpectedContent "dow" `
        -Description "Market indices endpoint"
}

# Frontend tests
function Test-Frontend {
    Write-Info "Testing frontend..."
    
    Test-Endpoint -TestName "Frontend Health" `
        -Url $FrontendUrl `
        -ExpectedContent "PaiiD" `
        -Description "Frontend homepage"
    
    # Test if frontend is serving static files
    Test-Endpoint -TestName "Frontend Static Assets" `
        -Url "$FrontendUrl/_next/static" `
        -Description "Static assets directory"
}

# External service tests
function Test-ExternalServices {
    Write-Info "Testing external service connectivity..."
    
    # Test if backend can reach external services
    Test-Endpoint -TestName "Backend External Services" `
        -Url "$BackendUrl/api/health/detailed" `
        -ExpectedContent "external_services" `
        -Description "External service connectivity"
}

# Configuration tests
function Test-Configuration {
    Write-Info "Testing configuration..."
    
    # Test configuration endpoint for proper environment
    Test-Endpoint -TestName "Backend Environment" `
        -Url "$BackendUrl/api/settings/config" `
        -ExpectedContent "production" `
        -Description "Production environment configuration"
    
    # Test if Sentry is configured (if in production)
    Test-Endpoint -TestName "Backend Sentry Configuration" `
        -Url "$BackendUrl/api/settings/config" `
        -ExpectedContent "sentry_configured" `
        -Description "Sentry error tracking configuration"
}

# Performance tests
function Test-Performance {
    Write-Info "Testing performance..."
    
    # Test response times
    $startTime = Get-Date
    try {
        $null = Invoke-RestMethod -Uri "$BackendUrl/api/health" -Method GET -TimeoutSec $Timeout
        $endTime = Get-Date
        $responseTime = ($endTime - $startTime).TotalMilliseconds
        
        if ($responseTime -lt 5000) {
            Write-Success "✓ Performance - PASS ($([math]::Round($responseTime))ms)"
            $script:TestsPassed++
        } else {
            Write-Warning "⚠ Performance - SLOW ($([math]::Round($responseTime))ms)"
            $script:TestsPassed++
        }
    } catch {
        Write-Error "✗ Performance - FAIL (timeout)"
        $script:TestsFailed++
        $script:FailedTests += "Performance"
    }
}

# Main verification function
function Main {
    Write-Info "🔍 Starting PaiiD deployment verification..."
    Write-Info "Backend URL: $BackendUrl"
    Write-Info "Frontend URL: $FrontendUrl"
    Write-Info "Timeout: ${Timeout}s"
    Write-Host ""
    
    # Run all test suites
    Test-HealthEndpoints
    Test-ApiEndpoints
    Test-Frontend
    Test-ExternalServices
    Test-Configuration
    Test-Performance
    
    # Generate summary
    Write-Host ""
    Write-Info "📊 Verification Summary"
    Write-Host "================================"
    Write-Success "Passed: $script:TestsPassed"
    if ($script:TestsFailed -gt 0) {
        Write-Error "Failed: $script:TestsFailed"
        Write-Error "Failed tests: $($script:FailedTests -join ', ')"
    } else {
        Write-Success "Failed: $script:TestsFailed"
    }
    
    # Overall result
    if ($script:TestsFailed -eq 0) {
        Write-Success "🎉 All verification tests passed!"
        exit 0
    } else {
        Write-Error "❌ Some verification tests failed"
        exit 1
    }
}

# Run main function
Main
