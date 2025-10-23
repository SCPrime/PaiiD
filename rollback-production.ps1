# 🔄 PaiiD Production Rollback Script
# Rollback to previous deployment version

param(
    [Parameter(Mandatory=$true)]
    [string]$CurrentTag,

    [Parameter(Mandatory=$true)]
    [string]$PreviousTag,

    [string]$BackendServiceId,
    [string]$FrontendServiceId,
    [string]$BackendUrl = "https://paiid-backend.onrender.com",
    [string]$FrontendUrl = "https://paiid-frontend.onrender.com",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

Write-Host "`n╔════════════════════════════════════════════╗" -ForegroundColor Red
Write-Host "║      ⚠️  PRODUCTION ROLLBACK INITIATED      ║" -ForegroundColor Red
Write-Host "╚════════════════════════════════════════════╝`n" -ForegroundColor Red

Write-Host "Rolling back from $CurrentTag to $PreviousTag" -ForegroundColor Yellow
Write-Host ""

# ============================================
# STEP 1: Confirmation
# ============================================
if (-not $Force) {
    Write-Host "⚠️  This will rollback the production deployment!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Current version: $CurrentTag" -ForegroundColor Yellow
    Write-Host "Target version:  $PreviousTag" -ForegroundColor Green
    Write-Host ""

    $confirm = Read-Host "Are you sure you want to proceed? (type 'ROLLBACK' to confirm)"

    if ($confirm -ne "ROLLBACK") {
        Write-Host "`n✗ Rollback cancelled" -ForegroundColor Yellow
        exit 0
    }
}

Write-Host ""

# ============================================
# STEP 2: Verify Git Tag Exists
# ============================================
Write-Host "📋 Step 1: Verifying rollback target..." -ForegroundColor Yellow

try {
    $tagExists = git tag -l $PreviousTag
    if (-not $tagExists) {
        Write-Host "  ✗ Tag $PreviousTag does not exist" -ForegroundColor Red
        Write-Host "    Available tags:" -ForegroundColor Gray
        git tag -l | ForEach-Object { Write-Host "    - $_" -ForegroundColor Gray }
        exit 1
    }

    Write-Host "  ✓ Tag $PreviousTag found" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Error verifying tag: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# ============================================
# STEP 3: Checkout Previous Version
# ============================================
Write-Host "🔄 Step 2: Checking out previous version..." -ForegroundColor Yellow

try {
    # Stash any local changes
    $status = git status --porcelain
    if ($status) {
        Write-Host "  → Stashing local changes..." -ForegroundColor Cyan
        git stash push -m "Rollback stash - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    }

    # Checkout previous tag
    git checkout $PreviousTag

    Write-Host "  ✓ Checked out $PreviousTag" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Failed to checkout $PreviousTag : $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# ============================================
# STEP 4: Deploy via Render
# ============================================
Write-Host "🚀 Step 3: Triggering Render redeploy..." -ForegroundColor Yellow

if (-not $env:RENDER_API_KEY) {
    Write-Host "  ⚠ RENDER_API_KEY not set - manual rollback required" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  📖 Manual Rollback Steps:" -ForegroundColor Cyan
    Write-Host "     1. Go to https://dashboard.render.com" -ForegroundColor White
    Write-Host "     2. Select backend service → 'Deploys' tab" -ForegroundColor White
    Write-Host "     3. Find deploy for tag '$PreviousTag'" -ForegroundColor White
    Write-Host "     4. Click 'Redeploy'" -ForegroundColor White
    Write-Host "     5. Repeat for frontend service" -ForegroundColor White
    Write-Host ""

    $manual = Read-Host "  Press Enter when rollback is complete..."
} else {
    # Automated rollback via API
    $RenderApiUrl = "https://api.render.com/v1"

    # Get service IDs if not provided
    if (-not $BackendServiceId) {
        $BackendServiceId = Read-Host "  Enter Backend Service ID"
    }

    if (-not $FrontendServiceId) {
        $FrontendServiceId = Read-Host "  Enter Frontend Service ID"
    }

    $headers = @{
        "Authorization" = "Bearer $env:RENDER_API_KEY"
        "Content-Type" = "application/json"
    }

    # Rollback backend
    Write-Host "  → Rolling back backend..." -ForegroundColor Cyan
    try {
        $backendBody = @{
            clearCache = $true  # Clear cache on rollback
        } | ConvertTo-Json

        $backendDeploy = Invoke-RestMethod -Uri "$RenderApiUrl/services/$BackendServiceId/deploys" `
            -Method Post -Headers $headers -Body $backendBody

        Write-Host "  ✓ Backend rollback triggered (ID: $($backendDeploy.id))" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ Backend rollback failed: $_" -ForegroundColor Red
        exit 1
    }

    Start-Sleep -Seconds 2

    # Rollback frontend
    Write-Host "  → Rolling back frontend..." -ForegroundColor Cyan
    try {
        $frontendBody = @{
            clearCache = $true
        } | ConvertTo-Json

        $frontendDeploy = Invoke-RestMethod -Uri "$RenderApiUrl/services/$FrontendServiceId/deploys" `
            -Method Post -Headers $headers -Body $frontendBody

        Write-Host "  ✓ Frontend rollback triggered (ID: $($frontendDeploy.id))" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ Frontend rollback failed: $_" -ForegroundColor Red
        exit 1
    }

    Write-Host "`n  ⏳ Waiting for rollback to complete..." -ForegroundColor Cyan
    Write-Host "     This may take 5-10 minutes..." -ForegroundColor Gray
    Start-Sleep -Seconds 60
}

Write-Host ""

# ============================================
# STEP 5: Verify Rollback
# ============================================
Write-Host "🏥 Step 4: Verifying rollback..." -ForegroundColor Yellow

# Backend health check
Write-Host "  → Checking backend..." -ForegroundColor Cyan
$maxRetries = 5
$retryCount = 0
$backendHealthy = $false

while ($retryCount -lt $maxRetries -and -not $backendHealthy) {
    try {
        $response = Invoke-WebRequest -Uri "$BackendUrl/api/health" -Method Get -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✓ Backend is healthy (HTTP 200)" -ForegroundColor Green
            $backendHealthy = $true
        }
    } catch {
        $retryCount++
        if ($retryCount -lt $maxRetries) {
            Write-Host "    Retry $retryCount/$maxRetries..." -ForegroundColor Gray
            Start-Sleep -Seconds 15
        } else {
            Write-Host "  ✗ Backend health check failed" -ForegroundColor Red
        }
    }
}

# Frontend health check
Write-Host "  → Checking frontend..." -ForegroundColor Cyan
$retryCount = 0
$frontendHealthy = $false

while ($retryCount -lt $maxRetries -and -not $frontendHealthy) {
    try {
        $response = Invoke-WebRequest -Uri $FrontendUrl -Method Get -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✓ Frontend is accessible (HTTP 200)" -ForegroundColor Green
            $frontendHealthy = $true
        }
    } catch {
        $retryCount++
        if ($retryCount -lt $maxRetries) {
            Write-Host "    Retry $retryCount/$maxRetries..." -ForegroundColor Gray
            Start-Sleep -Seconds 15
        } else {
            Write-Host "  ✗ Frontend health check failed" -ForegroundColor Red
        }
    }
}

Write-Host ""

# ============================================
# STEP 6: Create Rollback Report
# ============================================
Write-Host "📄 Step 5: Generating rollback report..." -ForegroundColor Yellow

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$reportFile = "rollback-report-$timestamp.md"

$rollbackReason = Read-Host "  Enter reason for rollback (optional)"

$report = @"
# 🔄 Rollback Report

**Date:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Rolled Back By:** $(git config user.name) <$(git config user.email)>

---

## 📋 Rollback Details

- **From Version:** $CurrentTag
- **To Version:** $PreviousTag
- **Reason:** $rollbackReason

---

## 🏥 Health Status After Rollback

- **Backend:** $(if ($backendHealthy) { "✅ HEALTHY" } else { "❌ UNHEALTHY - INVESTIGATION REQUIRED" })
- **Frontend:** $(if ($frontendHealthy) { "✅ ACCESSIBLE" } else { "❌ INACCESSIBLE - INVESTIGATION REQUIRED" })

---

## 🌐 Production URLs

- **Backend:** $BackendUrl
- **Frontend:** $FrontendUrl

---

## 🔍 Post-Rollback Tasks

- [ ] Verify all critical features working
- [ ] Monitor error logs for 30 minutes
- [ ] Test options trading flow
- [ ] Test market data updates
- [ ] Investigate root cause of rollback
- [ ] Create incident report
- [ ] Fix issues before next deployment

---

## 🔬 Root Cause Analysis

*TODO: Document root cause of issues that led to rollback*

### Timeline
- **Deployment Time:** Unknown
- **Issue Detected:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
- **Rollback Initiated:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
- **Rollback Completed:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

### What Went Wrong
*TODO: Add details*

### Prevention Measures
*TODO: Add prevention steps*

---

**Rollback Status:** $(if ($backendHealthy -and $frontendHealthy) { "✅ SUCCESS" } else { "❌ FAILED - MANUAL INTERVENTION REQUIRED" })

Generated by rollback-production.ps1
"@

$report | Out-File -FilePath $reportFile -Encoding UTF8

Write-Host "  ✓ Report saved to: $reportFile" -ForegroundColor Green
Write-Host ""

# ============================================
# STEP 7: Return to Main Branch
# ============================================
Write-Host "🔙 Step 6: Returning to main branch..." -ForegroundColor Yellow

try {
    git checkout main
    git pull origin main

    # Pop stashed changes if any
    $stashList = git stash list
    if ($stashList -match "Rollback stash") {
        $restore = Read-Host "  Restore stashed changes? (y/n)"
        if ($restore -eq "y") {
            git stash pop
        }
    }

    Write-Host "  ✓ Returned to main branch" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ Could not return to main branch: $_" -ForegroundColor Yellow
}

Write-Host ""

# ============================================
# STEP 8: Summary
# ============================================
if ($backendHealthy -and $frontendHealthy) {
    Write-Host "╔════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║      ✅ ROLLBACK SUCCESSFUL!               ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════════╝`n" -ForegroundColor Green
} else {
    Write-Host "╔════════════════════════════════════════════╗" -ForegroundColor Red
    Write-Host "║  ❌ ROLLBACK COMPLETED WITH ISSUES!       ║" -ForegroundColor Red
    Write-Host "╚════════════════════════════════════════════╝`n" -ForegroundColor Red
}

Write-Host "📊 Summary:" -ForegroundColor Cyan
Write-Host "   From: $CurrentTag" -ForegroundColor White
Write-Host "   To:   $PreviousTag" -ForegroundColor White
Write-Host "   Backend:  $(if ($backendHealthy) { "✅ Healthy" } else { "❌ Unhealthy" })" -ForegroundColor $(if ($backendHealthy) { "Green" } else { "Red" })
Write-Host "   Frontend: $(if ($frontendHealthy) { "✅ Accessible" } else { "❌ Inaccessible" })" -ForegroundColor $(if ($frontendHealthy) { "Green" } else { "Red" })
Write-Host ""
Write-Host "📄 Rollback report: $reportFile" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔍 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Monitor production: $FrontendUrl" -ForegroundColor White
Write-Host "   2. Investigate root cause" -ForegroundColor White
Write-Host "   3. Create incident report" -ForegroundColor White
Write-Host "   4. Fix issues before next deployment" -ForegroundColor White
Write-Host ""
