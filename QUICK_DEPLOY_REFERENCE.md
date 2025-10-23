# ⚡ Quick Deploy Reference Card

Fast reference for PaiiD deployment automation scripts.

---

## 🚀 DEPLOY TO PRODUCTION

```powershell
# 1. Set API key (one-time setup)
$env:RENDER_API_KEY = "rnd-xxxxxxxxxxxx"

# 2. Deploy
.\deploy-production.ps1 `
    -BackendServiceId "srv-backend-id" `
    -FrontendServiceId "srv-frontend-id"

# 3. Test
.\test-production.ps1 -ApiToken "your-token"
```

**Time:** ~10 minutes

---

## 🔄 ROLLBACK

```powershell
# Emergency rollback
.\rollback-production.ps1 `
    -CurrentTag "v1.0.5" `
    -PreviousTag "v1.0.4"

# Type "ROLLBACK" to confirm
```

**Time:** ~5 minutes

---

## 🧪 TEST PRODUCTION

```powershell
# Quick smoke test
.\test-production.ps1

# Full test with auth
.\test-production.ps1 -ApiToken "your-token" -Detailed
```

**Time:** ~1 minute

---

## 🔧 COMMON FLAGS

### Deploy
- `-AutoApprove` - Skip all prompts (CI/CD)
- `-SkipTests` - Skip pre-deployment tests
- `-SkipHealthChecks` - Skip health verification

### Rollback
- `-Force` - Skip confirmation prompt

### Test
- `-Detailed` - Show response data

---

## 📍 GET SERVICE IDs

1. Go to https://dashboard.render.com
2. Click backend service
3. Copy ID from URL: `srv-XXXXXXXXXXXXX`
4. Repeat for frontend

---

## 🔑 GET RENDER API KEY

1. Go to https://dashboard.render.com/u/settings#api-keys
2. Generate new API key
3. Copy and save securely

```powershell
# Set permanently (Windows)
[System.Environment]::SetEnvironmentVariable('RENDER_API_KEY', 'rnd-xxx', 'User')

# Set for session
$env:RENDER_API_KEY = "rnd-xxxxxxxxxxxx"
```

---

## 📊 REPORTS GENERATED

- `deployment-report-YYYYMMDD-HHMMSS.md` - After deploy
- `rollback-report-YYYYMMDD-HHMMSS.md` - After rollback
- `test-report-YYYYMMDD-HHMMSS.md` - After tests

---

## ❌ TROUBLESHOOTING

### "RENDER_API_KEY not set"
```powershell
$env:RENDER_API_KEY = "rnd-xxxxxxxxxxxx"
```

### "Service not found"
Check service ID in Render dashboard URL

### "Health checks failing"
Wait 2-3 minutes for Render to wake up (free tier)

### "Tests timing out"
```powershell
# Health check already has 15s timeout with 5 retries
# If still failing, check Render logs
```

---

## 🎯 CI/CD PIPELINE

```powershell
# GitHub Actions / CI/CD
$env:RENDER_API_KEY = ${{ secrets.RENDER_API_KEY }}

.\deploy-production.ps1 `
    -BackendServiceId ${{ secrets.BACKEND_SERVICE_ID }} `
    -FrontendServiceId ${{ secrets.FRONTEND_SERVICE_ID }} `
    -AutoApprove

if ($LASTEXITCODE -eq 0) {
    .\test-production.ps1 -ApiToken ${{ secrets.API_TOKEN }}
}
```

---

## 📚 FULL DOCS

See `DEPLOYMENT_SCRIPTS_README.md` for complete documentation.

---

**Quick tips:**
- Always tag deployments with semantic versioning
- Monitor logs for 15-30 minutes after deploy
- Test rollback procedure in staging first
- Keep deployment reports for compliance

**Production URLs:**
- Backend: https://paiid-backend.onrender.com
- Frontend: https://paiid-frontend.onrender.com
