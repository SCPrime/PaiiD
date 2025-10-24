# 🚀 PaiiD Deployment Automation Scripts

Complete PowerShell-based deployment automation for Render.com production deployments.

## 📋 Overview

This suite provides enterprise-grade deployment automation with:
- Automated deployments via Render API
- Comprehensive health checks and smoke tests
- Automated rollback capabilities
- Detailed deployment reporting
- Pre-deployment validation

## 🗂️ Scripts

### 1. `deploy-production.ps1` - Main Deployment Script

**Purpose:** Complete automated production deployment to Render

**Features:**
- ✅ Pre-deployment validation (git status, tests, config files)
- ✅ Automated version tagging
- ✅ Render API deployment triggering
- ✅ Health checks with retry logic
- ✅ Smoke tests for critical endpoints
- ✅ Comprehensive deployment report generation

**Usage:**

```powershell
# Basic deployment (manual steps)
.\deploy-production.ps1

# Fully automated deployment with Render API
$env:RENDER_API_KEY = "rnd-xxxxxxxxxxxx"
.\deploy-production.ps1 -BackendServiceId "srv-xxxx" -FrontendServiceId "srv-yyyy"

# Skip tests for quick deployment
.\deploy-production.ps1 -SkipTests

# Auto-approve all prompts (CI/CD mode)
.\deploy-production.ps1 -AutoApprove

# Custom URLs
.\deploy-production.ps1 -BackendUrl "https://custom-backend.onrender.com" -FrontendUrl "https://custom-frontend.onrender.com"
```

**Parameters:**
- `-BackendServiceId` - Render service ID for backend (get from dashboard)
- `-FrontendServiceId` - Render service ID for frontend
- `-BackendUrl` - Backend URL for health checks (default: https://paiid-backend.onrender.com)
- `-FrontendUrl` - Frontend URL for health checks (default: https://paiid-frontend.onrender.com)
- `-SkipTests` - Skip pre-deployment tests
- `-SkipHealthChecks` - Skip post-deployment health checks
- `-AutoApprove` - Auto-approve all prompts (for CI/CD)

**Output:**
- Creates `deployment-report-YYYYMMDD-HHMMSS.md` with full deployment details
- Exit code 0 on success, 1 on failure

---

### 2. `rollback-production.ps1` - Rollback Script

**Purpose:** Rollback production to a previous version tag

**Features:**
- ✅ Automated git checkout to previous tag
- ✅ Render API redeployment
- ✅ Post-rollback health verification
- ✅ Rollback incident reporting

**Usage:**

```powershell
# Basic rollback
.\rollback-production.ps1 -CurrentTag "v1.0.3" -PreviousTag "v1.0.2"

# With Render API
$env:RENDER_API_KEY = "rnd-xxxxxxxxxxxx"
.\rollback-production.ps1 -CurrentTag "v1.0.3" -PreviousTag "v1.0.2" `
    -BackendServiceId "srv-xxxx" -FrontendServiceId "srv-yyyy"

# Force rollback (skip confirmation)
.\rollback-production.ps1 -CurrentTag "v1.0.3" -PreviousTag "v1.0.2" -Force
```

**Parameters:**
- `-CurrentTag` - **Required** - Current problematic version tag
- `-PreviousTag` - **Required** - Target rollback version tag
- `-BackendServiceId` - Render service ID for backend
- `-FrontendServiceId` - Render service ID for frontend
- `-BackendUrl` - Backend URL for health checks
- `-FrontendUrl` - Frontend URL for health checks
- `-Force` - Skip confirmation prompt

**Output:**
- Creates `rollback-report-YYYYMMDD-HHMMSS.md` with rollback details
- Returns to main branch after rollback
- Exit code 0 on success, 1 on failure

---

### 3. `test-production.ps1` - Post-Deployment Test Suite

**Purpose:** Comprehensive production testing after deployment

**Features:**
- ✅ Infrastructure health checks
- ✅ API authentication tests
- ✅ Market data endpoint tests
- ✅ Options trading flow tests
- ✅ AI & recommendation tests
- ✅ Paper trading tests
- ✅ Frontend asset tests
- ✅ CORS and security header verification
- ✅ Performance benchmarking
- ✅ Critical user flow validation

**Usage:**

```powershell
# Basic smoke tests (public endpoints only)
.\test-production.ps1

# Comprehensive tests with authentication
.\test-production.ps1 -ApiToken "your-api-token-here"

# Custom URLs
.\test-production.ps1 -BackendUrl "https://staging-backend.onrender.com"

# Detailed output mode
.\test-production.ps1 -Detailed
```

**Parameters:**
- `-BackendUrl` - Backend URL to test (default: https://paiid-backend.onrender.com)
- `-FrontendUrl` - Frontend URL to test (default: https://paiid-frontend.onrender.com)
- `-ApiToken` - API token for authenticated endpoint tests
- `-Detailed` - Show detailed response data

**Output:**
- Real-time test results with color-coded pass/fail
- Performance metrics (response times)
- Creates `test-report-YYYYMMDD-HHMMSS.md` with detailed results
- Exit code 0 if success rate ≥80%, 1 otherwise

**Test Categories:**
1. Infrastructure Health (3 tests)
2. API Authentication (2 tests)
3. Market Data Endpoints (3 tests)
4. Options Trading Endpoints (3 tests)
5. AI & Recommendations (2 tests)
6. Paper Trading (2 tests)
7. Frontend Assets & Pages (2 tests)
8. CORS & Security Headers (1 test)
9. Performance Metrics (2 tests)
10. Critical User Flows (2 tests)

---

## 🔧 Setup

### Prerequisites

1. **PowerShell 5.1+** (comes with Windows)
2. **Git** installed and configured
3. **GitHub CLI** (optional, recommended): https://cli.github.com/
4. **Render API Key** (for automated deployments):
   - Go to https://dashboard.render.com/u/settings#api-keys
   - Generate new API key
   - Set environment variable: `$env:RENDER_API_KEY = "rnd-xxxxxxxxxxxx"`

### Get Render Service IDs

1. Go to https://dashboard.render.com
2. Click on your backend service
3. Copy the service ID from the URL: `https://dashboard.render.com/web/srv-XXXXXXXXXXXXX`
4. Repeat for frontend service

### Environment Variables

```powershell
# Required for automated deployments
$env:RENDER_API_KEY = "rnd-xxxxxxxxxxxx"

# Optional - for CI/CD pipelines
$env:BACKEND_SERVICE_ID = "srv-backend-id"
$env:FRONTEND_SERVICE_ID = "srv-frontend-id"
$env:API_TOKEN = "your-api-token"
```

---

## 📖 Typical Workflows

### Full Production Deployment

```powershell
# 1. Set Render API key
$env:RENDER_API_KEY = "rnd-xxxxxxxxxxxx"

# 2. Run deployment
.\deploy-production.ps1 -BackendServiceId "srv-xxx" -FrontendServiceId "srv-yyy"

# 3. Wait for completion (script handles this)

# 4. Run post-deployment tests
.\test-production.ps1 -ApiToken "your-token"

# 5. Review deployment report
Get-Content deployment-report-*.md | Select-Object -Last 1
```

### Emergency Rollback

```powershell
# 1. Identify versions
git tag -l  # See available tags

# 2. Execute rollback
.\rollback-production.ps1 -CurrentTag "v1.0.5" -PreviousTag "v1.0.4"

# 3. Verify rollback
.\test-production.ps1

# 4. Review rollback report
Get-Content rollback-report-*.md | Select-Object -Last 1
```

### CI/CD Pipeline Integration

```powershell
# Automated deployment with zero interaction
$env:RENDER_API_KEY = $env:RENDER_API_KEY_SECRET

.\deploy-production.ps1 `
    -BackendServiceId $env:BACKEND_SERVICE_ID `
    -FrontendServiceId $env:FRONTEND_SERVICE_ID `
    -AutoApprove `
    -SkipTests

if ($LASTEXITCODE -eq 0) {
    .\test-production.ps1 -ApiToken $env:API_TOKEN
}
```

---

## 📊 Reports Generated

### Deployment Report (`deployment-report-*.md`)

Contains:
- Deployment metadata (date, version, deployed by)
- Git information (commit, tag, changes since last deploy)
- Health status of services
- Smoke test results
- Post-deployment tasks checklist
- Rollback procedure

### Rollback Report (`rollback-report-*.md`)

Contains:
- Rollback metadata (versions, timestamp, initiator)
- Reason for rollback
- Post-rollback health status
- Root cause analysis template
- Timeline of events
- Prevention measures template

### Test Report (`test-report-*.md`)

Contains:
- Test summary (total/passed/failed/skipped)
- Performance metrics
- Detailed test results table
- Overall status assessment

---

## 🔒 Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** for sensitive data
3. **Rotate API tokens** regularly
4. **Limit API key permissions** to deployment only
5. **Review deployment reports** before sharing
6. **Store rollback procedures** in secure location

---

## 🚨 Troubleshooting

### "RENDER_API_KEY not set"

```powershell
# Set the API key
$env:RENDER_API_KEY = "rnd-xxxxxxxxxxxx"

# Or use manual deployment mode
.\deploy-production.ps1  # Follow manual steps
```

### "Service ID not found"

```powershell
# Get service ID from Render dashboard URL
# Example: https://dashboard.render.com/web/srv-ct5abc123xyz
# Service ID: srv-ct5abc123xyz
```

### "Health checks failing"

```powershell
# Check Render deployment logs
# 1. Go to https://dashboard.render.com
# 2. Select service → "Logs" tab
# 3. Look for errors during deployment

# Verify environment variables are set in Render
# Dashboard → Service → "Environment" tab
```

### "Tests timing out"

```powershell
# Render free tier can be slow after inactivity
# Wait 2-3 minutes for services to wake up

# Run tests with longer timeout
.\test-production.ps1  # Already has 15s timeout per test
```

---

## 🎯 Best Practices

1. **Always tag deployments** - Use semantic versioning (v1.0.0)
2. **Run tests before deploying** - Use `-SkipTests` only when necessary
3. **Monitor after deployment** - Watch logs for 15-30 minutes
4. **Keep deployment reports** - Archive for compliance/auditing
5. **Test rollback procedures** - Practice rollbacks in staging first
6. **Document incidents** - Fill out rollback report templates
7. **Automate in CI/CD** - Use GitHub Actions or similar

---

## 📚 Additional Resources

- **Render Documentation:** https://render.com/docs
- **Render API Docs:** https://api-docs.render.com
- **GitHub CLI:** https://cli.github.com/manual
- **PowerShell Docs:** https://docs.microsoft.com/powershell

---

## 🤝 Contributing

Improvements to these scripts are welcome! Please:
1. Test thoroughly before committing
2. Update this README with any new features
3. Maintain backward compatibility
4. Add error handling for edge cases

---

## 📝 Version History

- **Batch 6** (2025-10-23) - Complete automation suite with Render API integration
- **Batch 5D** (2025-10-23) - Initial deployment preparation script

---

**Generated by:** Claude Code (Batch 6 Deployment Automation)
**Last Updated:** 2025-10-23
