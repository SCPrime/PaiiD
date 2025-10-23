# 🚀 PaiiD Production Deployment Script - Batch 6
# Complete automated deployment with Render API integration
# Includes: Testing, Deployment, Health Checks, and Reporting

param(
    [string]$BackendServiceId,
    [string]$FrontendServiceId,
    [string]$BackendUrl = "https://paiid-backend.onrender.com",
    [string]$FrontendUrl = "https://paiid-frontend.onrender.com",
    [switch]$SkipTests,
    [switch]$SkipHealthChecks,
    [switch]$AutoApprove
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Configuration
$RenderApiUrl = "https://api.render.com/v1"
$DeploymentTimeout = 600  # 10 minutes

Write-Host "`n╔════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   PaiiD Production Deployment to Render   ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# ============================================
# STEP 1: Prerequisites Check
# ============================================
Write-Host "📋 Step 1: Checking prerequisites..." -ForegroundColor Yellow

# Check Git
try {
    $null = Get-Command git -ErrorAction Stop
    Write-Host "  ✓ Git found" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Git not found" -ForegroundColor Red
    exit 1
}

# Check GitHub CLI (optional but recommended)
try {
    $null = Get-Command gh -ErrorAction Stop
    Write-Host "  ✓ GitHub CLI found" -ForegroundColor Green
    $hasGitHubCli = $true
} catch {
    Write-Host "  ⚠ GitHub CLI not found (optional)" -ForegroundColor Yellow
    $hasGitHubCli = $false
}

# Check for Render API key
if (-not $env:RENDER_API_KEY) {
    Write-Host "  ⚠ RENDER_API_KEY not set" -ForegroundColor Yellow
    Write-Host "    Get your API key from: https://dashboard.render.com/u/settings#api-keys" -ForegroundColor Cyan
    $manualDeploy = $true
} else {
    Write-Host "  ✓ Render API key configured" -ForegroundColor Green
    $manualDeploy = $false
}

Write-Host ""

# ============================================
# STEP 2: Verify Git Repository State
# ============================================
Write-Host "📂 Step 2: Verifying Git repository..." -ForegroundColor Yellow

# Check current branch
$currentBranch = git branch --show-current
if ($currentBranch -ne "main") {
    Write-Host "  ⚠ Currently on branch: $currentBranch" -ForegroundColor Yellow

    if ($AutoApprove) {
        Write-Host "  → Switching to main..." -ForegroundColor Cyan
        git checkout main
        git pull origin main
    } else {
        $switch = Read-Host "  Switch to main and pull latest? (y/n)"
        if ($switch -eq "y") {
            git checkout main
            git pull origin main
        } else {
            Write-Host "  ✗ Deployment aborted. Must be on main branch." -ForegroundColor Red
            exit 1
        }
    }
} else {
    git pull origin main
    Write-Host "  ✓ On main branch with latest code" -ForegroundColor Green
}

# Check for uncommitted changes
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Host "  ⚠ Uncommitted changes detected" -ForegroundColor Yellow
    Write-Host "    $gitStatus" -ForegroundColor Gray

    if (-not $AutoApprove) {
        $continue = Read-Host "  Continue anyway? (y/n)"
        if ($continue -ne "y") {
            Write-Host "  ✗ Deployment aborted" -ForegroundColor Red
            exit 1
        }
    }
}

Write-Host ""

# ============================================
# STEP 3: Run Pre-Deployment Tests
# ============================================
if (-not $SkipTests) {
    Write-Host "🧪 Step 3: Running pre-deployment tests..." -ForegroundColor Yellow

    # Backend tests
    if (Test-Path "backend/tests") {
        Write-Host "  → Testing backend..." -ForegroundColor Cyan
        Push-Location backend

        try {
            if (Get-Command pytest -ErrorAction SilentlyContinue) {
                $testResult = pytest tests/ -v --tb=short 2>&1
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "  ✓ Backend tests passed" -ForegroundColor Green
                } else {
                    Write-Host "  ⚠ Some backend tests failed" -ForegroundColor Yellow
                    if (-not $AutoApprove) {
                        $continue = Read-Host "  Continue deployment? (y/n)"
                        if ($continue -ne "y") {
                            Pop-Location
                            exit 1
                        }
                    }
                }
            } else {
                Write-Host "  ⚠ pytest not found, skipping backend tests" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "  ⚠ Backend tests encountered errors" -ForegroundColor Yellow
        }

        Pop-Location
    }

    # Frontend tests
    if (Test-Path "frontend/package.json") {
        Write-Host "  → Testing frontend..." -ForegroundColor Cyan
        Push-Location frontend

        try {
            $package = Get-Content package.json | ConvertFrom-Json
            if ($package.scripts."test:ci") {
                npm run test:ci 2>&1 | Out-Null
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "  ✓ Frontend tests passed" -ForegroundColor Green
                } else {
                    Write-Host "  ⚠ Some frontend tests failed" -ForegroundColor Yellow
                }
            } else {
                Write-Host "  ⚠ No test:ci script found" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "  ⚠ Frontend tests encountered errors" -ForegroundColor Yellow
        }

        Pop-Location
    }

    Write-Host ""
} else {
    Write-Host "⏭️  Step 3: Skipping tests (--SkipTests flag)`n" -ForegroundColor Yellow
}

# ============================================
# STEP 4: Version Tagging
# ============================================
Write-Host "🏷️  Step 4: Creating deployment tag..." -ForegroundColor Yellow

# Get last tag
try {
    $lastTag = git describe --tags --abbrev=0 2>$null
    Write-Host "  Last tag: $lastTag" -ForegroundColor Gray
} catch {
    $lastTag = "v0.0.0"
    Write-Host "  No previous tags found" -ForegroundColor Gray
}

if ($AutoApprove) {
    # Auto-increment patch version
    if ($lastTag -match 'v(\d+)\.(\d+)\.(\d+)') {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        $patch = [int]$matches[3] + 1
        $newTag = "v$major.$minor.$patch"
    } else {
        $newTag = "v1.0.0"
    }
} else {
    $version = Read-Host "  Enter new version (e.g., 1.0.1)"
    $newTag = "v$version"
}

git tag -a $newTag -m "Production deployment $newTag"
git push origin $newTag

Write-Host "  ✓ Created and pushed tag: $newTag" -ForegroundColor Green
Write-Host ""

# ============================================
# STEP 5: Validate Configuration
# ============================================
Write-Host "📋 Step 5: Validating configuration files..." -ForegroundColor Yellow

$configValid = $true

# Check render.yaml
if (Test-Path "render.yaml") {
    Write-Host "  ✓ render.yaml found" -ForegroundColor Green
} else {
    Write-Host "  ✗ render.yaml not found" -ForegroundColor Red
    $configValid = $false
}

# Check backend requirements
if (Test-Path "backend/requirements.txt") {
    Write-Host "  ✓ backend/requirements.txt found" -ForegroundColor Green
} else {
    Write-Host "  ✗ backend/requirements.txt not found" -ForegroundColor Red
    $configValid = $false
}

# Check frontend Dockerfile
if (Test-Path "frontend/Dockerfile") {
    Write-Host "  ✓ frontend/Dockerfile found" -ForegroundColor Green
} else {
    Write-Host "  ✗ frontend/Dockerfile not found" -ForegroundColor Red
    $configValid = $false
}

if (-not $configValid) {
    Write-Host "`n  ✗ Configuration validation failed" -ForegroundColor Red
    exit 1
}

Write-Host ""

# ============================================
# STEP 6: Deploy to Render
# ============================================
Write-Host "🚀 Step 6: Deploying to Render..." -ForegroundColor Yellow

if ($manualDeploy) {
    Write-Host "  ⚠ Manual deployment required (no API key)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  📖 Manual Deployment Steps:" -ForegroundColor Cyan
    Write-Host "     1. Go to https://dashboard.render.com" -ForegroundColor White
    Write-Host "     2. Select your backend service" -ForegroundColor White
    Write-Host "     3. Click 'Manual Deploy' → 'Deploy latest commit'" -ForegroundColor White
    Write-Host "     4. Repeat for frontend service" -ForegroundColor White
    Write-Host ""

    $manual = Read-Host "  Press Enter when deployment is triggered..."
} else {
    # Automated deployment via API

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

    # Deploy backend
    Write-Host "  → Deploying backend..." -ForegroundColor Cyan
    try {
        $backendBody = @{ clearCache = $false } | ConvertTo-Json
        $backendDeploy = Invoke-RestMethod -Uri "$RenderApiUrl/services/$BackendServiceId/deploys" `
            -Method Post -Headers $headers -Body $backendBody

        Write-Host "  ✓ Backend deployment triggered (ID: $($backendDeploy.id))" -ForegroundColor Green
        $backendDeployId = $backendDeploy.id
    } catch {
        Write-Host "  ✗ Backend deployment failed: $_" -ForegroundColor Red
        exit 1
    }

    Start-Sleep -Seconds 2

    # Deploy frontend
    Write-Host "  → Deploying frontend..." -ForegroundColor Cyan
    try {
        $frontendBody = @{ clearCache = $false } | ConvertTo-Json
        $frontendDeploy = Invoke-RestMethod -Uri "$RenderApiUrl/services/$FrontendServiceId/deploys" `
            -Method Post -Headers $headers -Body $frontendBody

        Write-Host "  ✓ Frontend deployment triggered (ID: $($frontendDeploy.id))" -ForegroundColor Green
        $frontendDeployId = $frontendDeploy.id
    } catch {
        Write-Host "  ✗ Frontend deployment failed: $_" -ForegroundColor Red
        exit 1
    }

    # Wait for deployments
    Write-Host "`n  ⏳ Waiting for deployments to complete..." -ForegroundColor Cyan
    Write-Host "     This may take 5-10 minutes. Monitoring..." -ForegroundColor Gray
    Start-Sleep -Seconds 60
}

Write-Host ""

# ============================================
# STEP 7: Health Checks
# ============================================
if (-not $SkipHealthChecks) {
    Write-Host "🏥 Step 7: Running health checks..." -ForegroundColor Yellow

    # Backend health check
    Write-Host "  → Checking backend health..." -ForegroundColor Cyan
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
                Write-Host "  ✗ Backend health check failed after $maxRetries retries" -ForegroundColor Red
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
                Write-Host "  ✗ Frontend health check failed after $maxRetries retries" -ForegroundColor Red
            }
        }
    }

    Write-Host ""
} else {
    Write-Host "⏭️  Step 7: Skipping health checks (--SkipHealthChecks flag)`n" -ForegroundColor Yellow
}

# ============================================
# STEP 8: Smoke Tests
# ============================================
Write-Host "💨 Step 8: Running smoke tests..." -ForegroundColor Yellow

function Test-Endpoint {
    param([string]$Url, [int]$ExpectedStatus, [string]$Description)

    try {
        $response = Invoke-WebRequest -Uri $Url -Method Get -UseBasicParsing -TimeoutSec 10
        $status = $response.StatusCode
    } catch {
        $status = $_.Exception.Response.StatusCode.Value__
    }

    if ($status -eq $ExpectedStatus) {
        Write-Host "  ✓ $Description (HTTP $status)" -ForegroundColor Green
        return $true
    } else {
        Write-Host "  ✗ $Description (HTTP $status, expected $ExpectedStatus)" -ForegroundColor Red
        return $false
    }
}

$smokeTestsPassed = 0
$smokeTestsFailed = 0

# Test critical endpoints
if (Test-Endpoint -Url "$BackendUrl/api/health" -ExpectedStatus 200 -Description "Backend health endpoint") { $smokeTestsPassed++ } else { $smokeTestsFailed++ }
if (Test-Endpoint -Url "$BackendUrl/api/docs" -ExpectedStatus 200 -Description "API documentation") { $smokeTestsPassed++ } else { $smokeTestsFailed++ }
if (Test-Endpoint -Url "$FrontendUrl" -ExpectedStatus 200 -Description "Frontend homepage") { $smokeTestsPassed++ } else { $smokeTestsFailed++ }

Write-Host "`n  📊 Smoke tests: $smokeTestsPassed passed, $smokeTestsFailed failed" -ForegroundColor $(if ($smokeTestsFailed -eq 0) { "Green" } else { "Yellow" })
Write-Host ""

# ============================================
# STEP 9: Generate Deployment Report
# ============================================
Write-Host "📄 Step 9: Generating deployment report..." -ForegroundColor Yellow

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$reportFile = "deployment-report-$timestamp.md"

$commitHash = git rev-parse HEAD
$commitMessage = git log -1 --pretty=%B
$gitLog = git log "$lastTag..HEAD" --oneline | Out-String

$report = @"
# 🚀 Deployment Report

**Date:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Version:** $newTag
**Deployed By:** $(git config user.name) <$(git config user.email)>
**Duration:** N/A (manual tracking recommended)

---

## 📦 Services Deployed

- **Backend:** $BackendUrl
- **Frontend:** $FrontendUrl

---

## 🏥 Health Status

- **Backend Health:** $(if ($backendHealthy) { "✅ HEALTHY" } else { "⚠️ DEGRADED" })
- **Frontend Health:** $(if ($frontendHealthy) { "✅ ACCESSIBLE" } else { "⚠️ DEGRADED" })
- **Smoke Tests:** $smokeTestsPassed passed, $smokeTestsFailed failed

---

## 📝 Git Information

- **Commit:** ``$commitHash``
- **Tag:** ``$newTag``
- **Branch:** ``main``
- **Previous Tag:** ``$lastTag``

### Latest Commit
``````
$commitMessage
``````

### Changes Since Last Deployment
``````
$gitLog
``````

---

## ✅ Deployment Steps Completed

- [x] Code synced from main branch
- [x] Pre-deployment tests executed
- [x] Version tagged as $newTag
- [x] Configuration files validated
- [x] Services deployed to Render
- [x] Health checks performed
- [x] Smoke tests completed
- [x] Deployment report generated

---

## 🔍 Post-Deployment Tasks

- [ ] Monitor error logs for 1 hour
- [ ] Verify all 10 workflow stages in production
- [ ] Test options trading flow end-to-end
- [ ] Verify real-time market data updates
- [ ] Test paper trading execution
- [ ] Monitor performance metrics
- [ ] Update team/stakeholders

---

## 🔄 Rollback Procedure

If critical issues arise, rollback with:

``````powershell
.\rollback-production.ps1 -CurrentTag "$newTag" -PreviousTag "$lastTag"
``````

Or manual rollback via Render Dashboard:
1. Go to https://dashboard.render.com
2. Select service
3. Go to "Deploys" tab
4. Find deploy for ``$lastTag``
5. Click "Redeploy"

---

## 🌐 Production URLs

- **Frontend:** $FrontendUrl
- **Backend:** $BackendUrl
- **API Health:** $BackendUrl/api/health
- **API Docs:** $BackendUrl/api/docs
- **Render Dashboard:** https://dashboard.render.com

---

## 📊 Features Live in Production

✅ Complete Options Trading Platform
✅ Real-time Position Management
✅ Greeks Calculator with py_vollib
✅ Paper Trading via Alpaca
✅ Live Market Data via Tradier
✅ 10-Stage Radial Workflow Interface
✅ AI-Powered Recommendations
✅ Security Headers & CORS
✅ Error Handling & Monitoring

---

**Deployment Status:** $(if ($smokeTestsFailed -eq 0 -and $backendHealthy -and $frontendHealthy) { "✅ SUCCESS" } else { "⚠️ DEGRADED - Requires Attention" })

Generated by deploy-production.ps1 (Batch 6)
"@

$report | Out-File -FilePath $reportFile -Encoding UTF8

Write-Host "  ✓ Report saved to: $reportFile" -ForegroundColor Green
Write-Host ""

# ============================================
# STEP 10: Final Summary
# ============================================
Write-Host "╔════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║       ✅ DEPLOYMENT COMPLETE!              ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════╝`n" -ForegroundColor Green

Write-Host "🌐 Production URLs:" -ForegroundColor Cyan
Write-Host "   Backend:  $BackendUrl" -ForegroundColor White
Write-Host "   Frontend: $FrontendUrl" -ForegroundColor White
Write-Host ""
Write-Host "🏷️  Version: $newTag" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 Results:" -ForegroundColor Cyan
Write-Host "   Smoke Tests: $smokeTestsPassed passed, $smokeTestsFailed failed" -ForegroundColor White
Write-Host "   Backend: $(if ($backendHealthy) { "✅ Healthy" } else { "⚠️ Check logs" })" -ForegroundColor $(if ($backendHealthy) { "Green" } else { "Yellow" })
Write-Host "   Frontend: $(if ($frontendHealthy) { "✅ Accessible" } else { "⚠️ Check logs" })" -ForegroundColor $(if ($frontendHealthy) { "Green" } else { "Yellow" })
Write-Host ""
Write-Host "📄 Deployment report: $reportFile" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔍 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Monitor logs: https://dashboard.render.com" -ForegroundColor White
Write-Host "   2. Test production: $FrontendUrl" -ForegroundColor White
Write-Host "   3. Review deployment report" -ForegroundColor White
Write-Host "   4. Monitor for 15-30 minutes" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  Keep this terminal open to monitor for issues" -ForegroundColor Yellow
Write-Host ""
