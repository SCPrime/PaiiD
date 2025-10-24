# PaiiD Render Deployment Script
# Deploys to Render (Backend + Frontend)

param(
    [switch]$SkipRender,
    [switch]$SkipChecks,
    [switch]$Production
)

$ErrorActionPreference = "Stop"

Write-Host "`n🚀 PaiiD Render Deployment" -ForegroundColor Cyan
Write-Host "==============================`n" -ForegroundColor Cyan

# Production URLs (Render Only)
$BACKEND_URL = "https://paiid-backend.onrender.com"
$FRONTEND_URL = "https://paiid-frontend.onrender.com"

if (-not $SkipChecks) {
    Write-Host "✓ Pre-flight checks..." -ForegroundColor Yellow

    # Check git status
    $gitStatus = git status --porcelain
    if ($gitStatus) {
        Write-Host "⚠️  Uncommitted changes detected:" -ForegroundColor Yellow
        git status --short
        $continue = Read-Host "`nContinue deployment? (y/N)"
        if ($continue -ne "y") { 
            Write-Host "❌ Deployment cancelled" -ForegroundColor Red
            exit 0 
        }
    }

    # Check current branch
    $branch = git branch --show-current
    Write-Host "📌 Current branch: $branch" -ForegroundColor Cyan
    
    if ($Production -and $branch -ne "main") {
        Write-Host "⚠️  Production deployment should be from 'main' branch" -ForegroundColor Yellow
        $continue = Read-Host "Continue anyway? (y/N)"
        if ($continue -ne "y") { exit 0 }
    }

    Write-Host "✅ Pre-flight checks passed`n" -ForegroundColor Green
}

# Display deployment target
Write-Host "🎯 Deployment Target:" -ForegroundColor Cyan
Write-Host "   Backend:  $BACKEND_URL" -ForegroundColor White
Write-Host "   Frontend: $FRONTEND_URL" -ForegroundColor White
Write-Host ""

if (-not $SkipRender) {
    Write-Host "📦 Deploying to Render..." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "   Render will auto-deploy from GitHub when you push" -ForegroundColor Yellow
    Write-Host "   Run: git push origin main" -ForegroundColor Cyan
    Write-Host ""
    
    # Check if we need to push
    $aheadBehind = git rev-list --left-right --count origin/main...HEAD
    if ($aheadBehind -match "0\s+0") {
        Write-Host "✅ Already synced with origin/main" -ForegroundColor Green
    } else {
        Write-Host "📤 Pushing to GitHub..." -ForegroundColor Cyan
        git push origin main
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Pushed to GitHub - Render auto-deploy triggered" -ForegroundColor Green
        } else {
            Write-Host "❌ Push failed!" -ForegroundColor Red
            exit 1
        }
    }
    
    Write-Host ""
    Write-Host "⏳ Render is building and deploying..." -ForegroundColor Yellow
    Write-Host "   Monitor: https://dashboard.render.com" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "   Deployment typically takes 2-5 minutes" -ForegroundColor Gray
    Write-Host ""
    
    # Wait for deployment
    $wait = Read-Host "Wait for deployment to complete? (y/N)"
    if ($wait -eq "y") {
        Write-Host ""
        Write-Host "⏳ Waiting 30 seconds for deployment..." -ForegroundColor Yellow
        Start-Sleep -Seconds 30
    }
}

# Verification
Write-Host ""
Write-Host "🔍 Verifying Deployment..." -ForegroundColor Cyan
Write-Host ""

$tests = @(
    @{
        Name = "Backend Health"
        URL = "$BACKEND_URL/api/health"
        ExpectedStatus = 200
    },
    @{
        Name = "Frontend Health"
        URL = "$FRONTEND_URL"
        ExpectedStatus = 200
    }
)

$allPassed = $true
foreach ($test in $tests) {
    Write-Host "   Testing: $($test.Name)..." -ForegroundColor Gray
    try {
        $response = Invoke-WebRequest -Uri $test.URL -Method GET -TimeoutSec 10 -UseBasicParsing
        if ($response.StatusCode -eq $test.ExpectedStatus) {
            Write-Host "   ✅ $($test.Name) - OK" -ForegroundColor Green
        } else {
            Write-Host "   ❌ $($test.Name) - Unexpected status: $($response.StatusCode)" -ForegroundColor Red
            $allPassed = $false
        }
    } catch {
        Write-Host "   ❌ $($test.Name) - Failed: $($_.Exception.Message)" -ForegroundColor Red
        $allPassed = $false
    }
}

Write-Host ""
if ($allPassed) {
    Write-Host "✅ DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Some tests failed - check Render dashboard" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "=" -NoNewline; 1..50 | ForEach-Object { Write-Host "=" -NoNewline }; Write-Host ""
Write-Host "📊 DEPLOYMENT SUMMARY" -ForegroundColor Cyan
Write-Host "=" -NoNewline; 1..50 | ForEach-Object { Write-Host "=" -NoNewline }; Write-Host ""
Write-Host ""
Write-Host "Production URLs (Render):" -ForegroundColor Yellow
Write-Host "  Frontend: $FRONTEND_URL" -ForegroundColor White
Write-Host "  Backend:  $BACKEND_URL" -ForegroundColor White
Write-Host "  Backend Health: $BACKEND_URL/api/health" -ForegroundColor White
Write-Host "  Backend Docs: $BACKEND_URL/docs" -ForegroundColor White
Write-Host ""
Write-Host "Monitoring:" -ForegroundColor Yellow
Write-Host "  Render Dashboard: https://dashboard.render.com" -ForegroundColor White
Write-Host "  GitHub Repo: https://github.com/SCPrime/PaiiD" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Test in browser: $FRONTEND_URL" -ForegroundColor White
Write-Host "  2. Check logs in Render dashboard" -ForegroundColor White
Write-Host "  3. Monitor for errors in Sentry (if configured)" -ForegroundColor White
Write-Host ""
Write-Host "=" -NoNewline; 1..50 | ForEach-Object { Write-Host "=" -NoNewline }; Write-Host ""
Write-Host ""
Write-Host "🎉 Deployment complete!" -ForegroundColor Green
Write-Host ""
