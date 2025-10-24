# AI-Trader Cloud Deployment Script
# Deploys backend to Render and frontend to Vercel

param(
    [switch]$SkipRender,
    [switch]$SkipVercel,
    [switch]$SkipChecks
)

$ErrorActionPreference = "Stop"

Write-Host "`n🚀 AI-Trader Cloud Deployment" -ForegroundColor Cyan
Write-Host "==============================`n" -ForegroundColor Cyan

# Load environment variables
if (-not (Test-Path ".env")) {
    Write-Host "❌ .env file not found!" -ForegroundColor Red
    exit 1
}

$envVars = @{}
Get-Content ".env" | ForEach-Object {
    if ($_ -match '^([^#][^=]+)=(.*)$') {
        $envVars[$matches[1].Trim()] = $matches[2].Trim()
    }
}

$BACKEND_URL = $envVars["NEXT_PUBLIC_API_BASE_URL"]
$API_TOKEN = $envVars["API_TOKEN"]
$ALPACA_KEY = $envVars["ALPACA_PAPER_API_KEY"]
$ALPACA_SECRET = $envVars["ALPACA_PAPER_SECRET_KEY"]
$ANTHROPIC_KEY = $envVars["ANTHROPIC_API_KEY"]
$VERCEL_URL = $envVars["ALLOW_ORIGIN"]

if (-not $SkipChecks) {
    Write-Host "✓ Pre-flight checks..." -ForegroundColor Yellow

    # Pre-flight: Check for port conflicts
    Write-Host "🔍 Checking for port conflicts..." -ForegroundColor Yellow
    $PORT = $env:PORT ?? "8001"
    $PortInUse = Get-NetTCPConnection -LocalPort $PORT -ErrorAction SilentlyContinue
    if ($PortInUse) {
        Write-Host "⚠️  Port $PORT is in use" -ForegroundColor Yellow
        Write-Host "   Zombie processes detected. Run cleanup:" -ForegroundColor Gray
        Write-Host "   bash backend/scripts/cleanup.sh $PORT" -ForegroundColor Cyan
        $continue = Read-Host "Continue anyway? (y/N)"
        if ($continue -ne "y") { exit 0 }
    }

    # Pre-flight: Validate Render configurations
    Write-Host "🔍 Validating Render configurations..." -ForegroundColor Yellow
    $validationErrors = @()
    $result = python infra/render/validate.py backend/render.yaml infra/render/backend.json
    if ($LASTEXITCODE -ne 0) {
        $validationErrors += "Backend config drift detected"
    }
    $result = python infra/render/validate.py render.yaml
    if ($LASTEXITCODE -ne 0) {
        $validationErrors += "Root config validation failed"
    }
    if ($validationErrors.Count -gt 0) {
        Write-Host "❌ Configuration validation failed:" -ForegroundColor Red
        $validationErrors | ForEach-Object { Write-Host "   • $_" -ForegroundColor Red }
        exit 1
    }
    Write-Host "✅ Render configurations validated" -ForegroundColor Green

    # Pre-flight: Check git hold points
    Write-Host "🔍 Validating git hold points..." -ForegroundColor Yellow
    $result = python scripts/check_hold_points.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Hold point validation failed" -ForegroundColor Red
        Write-Host "   Locked files may have been modified" -ForegroundColor Yellow
        Write-Host "   Review .cursorrules and get approval" -ForegroundColor Gray
        exit 1
    }
    Write-Host "✅ Hold point validation passed" -ForegroundColor Green

    # Check git status
    $gitStatus = git status --porcelain
    if ($gitStatus -and ($gitStatus | Measure-Object).Count -gt 0) {
        Write-Host "⚠️  Uncommitted changes detected:" -ForegroundColor Yellow
        git status -sb
        $continue = Read-Host "`nContinue anyway? (y/N)"
        if ($continue -ne "y") { exit 0 }
    }

    # Check branch
    $branch = git branch --show-current
    Write-Host "  Branch: $branch" -ForegroundColor Gray

    # Check CLI tools
    $cliChecks = @(
        @{Name="gh"; Command="gh --version"},
        @{Name="vercel"; Command="vercel --version"}
    )

    foreach ($check in $cliChecks) {
        try {
            $null = Invoke-Expression $check.Command 2>&1
            Write-Host "  ✓ $($check.Name) CLI found" -ForegroundColor Green
        } catch {
            Write-Host "  ❌ $($check.Name) CLI not found" -ForegroundColor Red
            Write-Host "     Install: npm i -g $($check.Name)" -ForegroundColor Gray
            exit 1
        }
    }

    # Test backend pre-launch validation
    Write-Host "🔍 Testing backend pre-launch validation..." -ForegroundColor Yellow
    Push-Location backend
    try {
        python -m app.core.prelaunch --check-only
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ Backend pre-launch validation passed" -ForegroundColor Green
        } else {
            Write-Host "  ❌ Backend pre-launch validation failed" -ForegroundColor Red
            Pop-Location
            exit 1
        }
    } finally {
        Pop-Location
    }

    # Test frontend build
    Write-Host "🔍 Testing frontend build..." -ForegroundColor Yellow
    Push-Location frontend
    try {
        npm run build
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ Frontend build successful" -ForegroundColor Green
        } else {
            Write-Host "  ❌ Frontend build failed" -ForegroundColor Red
            Pop-Location
            exit 1
        }
    } finally {
        Pop-Location
    }
}

# Push to GitHub
Write-Host "`n📤 Pushing to GitHub..." -ForegroundColor Cyan
git push origin $(git branch --show-current)
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Git push failed" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Pushed to GitHub" -ForegroundColor Green

# Deploy to Render (Backend)
if (-not $SkipRender) {
    Write-Host "`n🔧 Deploying Backend to Render..." -ForegroundColor Cyan
    Write-Host "   URL: $BACKEND_URL" -ForegroundColor Gray

    Write-Host "`n   Required Environment Variables on Render:" -ForegroundColor Yellow
    Write-Host "   ├─ ALPACA_PAPER_API_KEY=$ALPACA_KEY" -ForegroundColor Gray
    Write-Host "   ├─ ALPACA_PAPER_SECRET_KEY=***" -ForegroundColor Gray
    Write-Host "   ├─ APCA_API_KEY_ID=$ALPACA_KEY" -ForegroundColor Gray
    Write-Host "   ├─ APCA_API_SECRET_KEY=***" -ForegroundColor Gray
    Write-Host "   ├─ APCA_API_BASE_URL=https://paper-api.alpaca.markets" -ForegroundColor Gray
    Write-Host "   ├─ ANTHROPIC_API_KEY=***" -ForegroundColor Gray
    Write-Host "   ├─ API_TOKEN=$API_TOKEN" -ForegroundColor Gray
    Write-Host "   ├─ LIVE_TRADING=false" -ForegroundColor Gray
    Write-Host "   └─ ALLOW_ORIGIN=$VERCEL_URL" -ForegroundColor Gray

    Write-Host "`n   Manual Steps:" -ForegroundColor Yellow
    Write-Host "   1. Go to: https://dashboard.render.com" -ForegroundColor White
    Write-Host "   2. Select your backend service" -ForegroundColor White
    Write-Host "   3. Click 'Manual Deploy' → 'Deploy latest commit'" -ForegroundColor White
    Write-Host "   4. Verify environment variables match above" -ForegroundColor White

    $renderDone = Read-Host "`n   Press Enter when Render deployment is complete..."
}

# Deploy to Vercel (Frontend)
if (-not $SkipVercel) {
    Write-Host "`n🎨 Deploying Frontend to Vercel..." -ForegroundColor Cyan
    Write-Host "   URL: $VERCEL_URL" -ForegroundColor Gray

    Write-Host "`n   Vercel Configuration:" -ForegroundColor Yellow
    Write-Host "   ├─ Production Branch: $(git branch --show-current)" -ForegroundColor Gray
    Write-Host "   ├─ Root Directory: frontend/" -ForegroundColor Gray
    Write-Host "   ├─ Framework: Next.js" -ForegroundColor Gray
    Write-Host "   └─ Build Command: (auto-detected)" -ForegroundColor Gray

    Write-Host "`n   Environment Variables:" -ForegroundColor Yellow
    Write-Host "   ├─ BACKEND_API_BASE_URL=$BACKEND_URL" -ForegroundColor Gray
    Write-Host "   └─ API_TOKEN=$API_TOKEN" -ForegroundColor Gray

    # Check if vercel.json exists in frontend
    if (Test-Path "frontend/vercel.json") {
        Write-Host "`n   ✓ frontend/vercel.json found" -ForegroundColor Green
    }

    Push-Location frontend
    try {
        Write-Host "`n   Deploying to production..." -ForegroundColor Yellow
        vercel --prod --yes
        if ($LASTEXITCODE -ne 0) {
            Write-Host "   ❌ Vercel deployment failed" -ForegroundColor Red
            Pop-Location
            exit 1
        }
        Write-Host "   ✓ Deployed to Vercel" -ForegroundColor Green
    } finally {
        Pop-Location
    }
}

# Smoke tests
Write-Host "`n🧪 Running Smoke Tests..." -ForegroundColor Cyan

$tests = @(
    @{
        Name = "Backend Health"
        URL = "$BACKEND_URL/api/health"
        Expected = "healthy"
    },
    @{
        Name = "Frontend Proxy Health"
        URL = "$($VERCEL_URL.TrimEnd('/'))/api/proxy/api/health"
        Expected = "healthy"
    },
    @{
        Name = "Backend Settings"
        URL = "$BACKEND_URL/api/settings"
        Expected = "trading_mode"
    },
    @{
        Name = "Frontend Proxy Settings"
        URL = "$($VERCEL_URL.TrimEnd('/'))/api/proxy/api/settings"
        Expected = "trading_mode"
    }
)

# Run comprehensive verification if script exists
if (Test-Path "scripts/verify-deployment.ps1") {
    Write-Host "`n🔍 Running Comprehensive Verification..." -ForegroundColor Cyan
    try {
        & "scripts/verify-deployment.ps1" -BackendUrl $BACKEND_URL -FrontendUrl $VERCEL_URL
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Comprehensive verification passed" -ForegroundColor Green
        } else {
            Write-Host "⚠ Comprehensive verification had issues" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠ Comprehensive verification failed: $($_.Exception.Message)" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠ Verification script not found, skipping comprehensive verification" -ForegroundColor Yellow
}

$passed = 0
$failed = 0

foreach ($test in $tests) {
    Write-Host "`n  Testing: $($test.Name)" -ForegroundColor Yellow
    Write-Host "  $($test.URL)" -ForegroundColor Gray

    try {
        $response = Invoke-RestMethod -Uri $test.URL -Method GET -TimeoutSec 10
        $responseText = $response | ConvertTo-Json -Compress

        if ($responseText -match $test.Expected) {
            Write-Host "  ✓ PASS" -ForegroundColor Green
            $passed++
        } else {
            Write-Host "  ❌ FAIL (unexpected response)" -ForegroundColor Red
            Write-Host "     Expected: $($test.Expected)" -ForegroundColor Gray
            Write-Host "     Got: $responseText" -ForegroundColor Gray
            $failed++
        }
    } catch {
        Write-Host "  ❌ FAIL ($($_.Exception.Message))" -ForegroundColor Red
        $failed++
    }
}

# Summary
Write-Host "`n" + ("=" * 50) -ForegroundColor Cyan
Write-Host "📊 Deployment Summary" -ForegroundColor Cyan
Write-Host ("=" * 50) -ForegroundColor Cyan

Write-Host "`nBackend (Render):" -ForegroundColor Yellow
Write-Host "  $BACKEND_URL" -ForegroundColor White

Write-Host "`nFrontend (Vercel):" -ForegroundColor Yellow
Write-Host "  $VERCEL_URL" -ForegroundColor White

Write-Host "`nSmoke Tests:" -ForegroundColor Yellow
Write-Host "  Passed: $passed" -ForegroundColor Green
Write-Host "  Failed: $failed" -ForegroundColor $(if ($failed -gt 0) { "Red" } else { "Gray" })

if ($failed -eq 0) {
    Write-Host "`n✅ Deployment Complete!" -ForegroundColor Green
    Write-Host "`nNext Steps:" -ForegroundColor Cyan
    Write-Host "  1. Open $VERCEL_URL in your browser" -ForegroundColor White
    Write-Host "  2. Click Health / Settings / Positions / Execute (Dry)" -ForegroundColor White
    Write-Host "  3. Verify all buttons return JSON" -ForegroundColor White
    
    # Generate deployment report
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $reportFile = "deployment-report-$timestamp.md"
    
    $reportContent = @"
# 🚀 Deployment Report

**Date:** $(Get-Date)
**Deployed by:** $env:USERNAME
**Branch:** $(git branch --show-current)
**Commit:** $(git rev-parse HEAD)

## Services Deployed

- **Backend:** $BACKEND_URL
- **Frontend:** $VERCEL_URL

## Configuration

- Skip Render: $SkipRender
- Skip Vercel: $SkipVercel
- Skip Checks: $SkipChecks

## Health Status

- Backend: $(try { $null = Invoke-RestMethod -Uri "$BACKEND_URL/api/health" -Method GET -TimeoutSec 5; "✅ Healthy" } catch { "❌ Unhealthy" })
- Frontend: $(try { $null = Invoke-RestMethod -Uri $VERCEL_URL -Method GET -TimeoutSec 5; "✅ Healthy" } catch { "❌ Unhealthy" })

## Smoke Test Results

- Passed: $passed
- Failed: $failed

## Next Steps

1. Verify all endpoints are responding
2. Run full test suite
3. Monitor logs for any issues
4. Update documentation if needed

## Rollback Procedure

If issues are detected:

1. Run: `./rollback-production.sh --current-tag v1.0.X --previous-tag v1.0.Y`
2. Verify rollback deployment
3. Investigate root cause
4. Create incident report

---
*Generated by PaiiD deployment script*
"@
    
    $reportContent | Out-File -FilePath $reportFile -Encoding UTF8
    Write-Host "`n📄 Deployment report generated: $reportFile" -ForegroundColor Green
} else {
    Write-Host "`n⚠️  Deployment completed with errors" -ForegroundColor Yellow
    Write-Host "   Check the failed tests above and verify environment variables" -ForegroundColor Gray
    exit 1
}

Write-Host ""