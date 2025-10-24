# 🚀 DEPLOYMENT EXECUTION GUIDE

**Your System:** Windows with PowerShell Core 7.5.3 ✅

---

## ✅ PREREQUISITES MET

You already have everything you need:
- ✅ PowerShell Core 7.5.3 installed
- ✅ All deployment scripts present:
  - `deploy-production.ps1`
  - `rollback-production.ps1`
  - `test-production.ps1`
- ✅ Git configured
- ✅ Repository at: `C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD`

---

## 🎯 OPTION 1: DRY RUN (Test Without Deploying)

Before deploying to production, test the scripts work correctly:

```powershell
# Navigate to project directory
cd C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD

# Run test suite against CURRENT production
pwsh -File test-production.ps1

# Expected output:
# - Tests run against https://paiid-backend.onrender.com
# - Shows which endpoints are working
# - Generates test-report-YYYYMMDD-HHMMSS.md
```

**This is SAFE** - it only reads from production, doesn't make changes.

---

## 🚀 OPTION 2: FULL PRODUCTION DEPLOYMENT

### Step 1: Set Up Render API Key (One-Time Setup)

```powershell
# Get API key from: https://dashboard.render.com/u/settings#api-keys
# Then set environment variable:
$env:RENDER_API_KEY = "rnd-xxxxxxxxxxxx"  # Replace with your actual key
```

### Step 2: Get Service IDs (One-Time Setup)

1. Go to https://dashboard.render.com
2. Click your **backend service**
3. Copy the ID from URL: `https://dashboard.render.com/web/srv-XXXXXXXXXXXXX`
4. Repeat for **frontend service**

```powershell
# Set service IDs
$BackendServiceId = "srv-backend-id-here"
$FrontendServiceId = "srv-frontend-id-here"
```

### Step 3: Run Deployment

```powershell
# Full automated deployment with all checks
pwsh -File deploy-production.ps1 `
  -BackendServiceId $BackendServiceId `
  -FrontendServiceId $FrontendServiceId
```

**What happens:**
1. ✅ Checks you're on main branch
2. ✅ Pulls latest code
3. ✅ Runs pre-deployment tests
4. ✅ Creates version tag (you'll be prompted for version number)
5. ✅ Validates render.yaml
6. ✅ Triggers Render deployment via API
7. ✅ Waits for deployment to complete
8. ✅ Runs health checks with retries
9. ✅ Runs smoke tests
10. ✅ Generates deployment report

**Duration:** ~10-15 minutes

---

## 🧪 OPTION 3: MANUAL DEPLOYMENT + AUTOMATED TESTING

If you don't have Render API key, you can deploy manually and test automatically:

### Step 1: Deploy Manually

1. Go to https://dashboard.render.com
2. Select backend service → "Manual Deploy" → "Deploy latest commit"
3. Select frontend service → "Manual Deploy" → "Deploy latest commit"
4. Wait for deployments to complete (~5-10 minutes)

### Step 2: Run Automated Tests

```powershell
# Test the deployed services
pwsh -File test-production.ps1
```

### Step 3: Review Results

```powershell
# Open the generated report
Get-Content test-report-*.md | Select-Object -Last 1
```

---

## 🔄 EMERGENCY ROLLBACK

If something goes wrong after deployment:

```powershell
# Rollback to previous version
pwsh -File rollback-production.ps1 `
  -CurrentTag "v1.0.5" `
  -PreviousTag "v1.0.4"

# Type "ROLLBACK" when prompted to confirm
```

---

## 📊 HEALTH CHECK COMMANDS (Manual)

If you prefer manual verification:

```powershell
# Check backend health
curl https://paiid-backend.onrender.com/api/health

# Check frontend
curl https://paiid-frontend.onrender.com

# Check API docs
curl https://paiid-backend.onrender.com/api/docs
```

Expected responses: All should return **HTTP 200**

---

## 🐛 TROUBLESHOOTING

### Issue: "deploy-production.ps1 cannot be loaded"

**Solution:**
```powershell
# Unblock the script
Unblock-File deploy-production.ps1
Unblock-File test-production.ps1
Unblock-File rollback-production.ps1
```

### Issue: "Execution of scripts is disabled"

**Solution:**
```powershell
# Check current policy
Get-ExecutionPolicy

# If it's "Restricted", change to RemoteSigned
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: "RENDER_API_KEY not set"

**Solution:**
```powershell
# Set the API key
$env:RENDER_API_KEY = "rnd-xxxxxxxxxxxx"

# Or run script without API key (manual deployment mode)
pwsh -File deploy-production.ps1
# It will guide you through manual deployment steps
```

### Issue: "Tests failing with connection errors"

**Cause:** Render free tier services sleep after inactivity

**Solution:**
```powershell
# Wake up services first
curl https://paiid-backend.onrender.com/api/health
curl https://paiid-frontend.onrender.com

# Wait 2-3 minutes for services to fully wake up
Start-Sleep -Seconds 180

# Then run tests
pwsh -File test-production.ps1
```

---

## 📝 EXAMPLE: COMPLETE DEPLOYMENT SESSION

Here's a full example of deploying with API key:

```powershell
# 1. Navigate to project
cd C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD

# 2. Set API credentials (replace with your actual values)
$env:RENDER_API_KEY = "rnd-your-key-here"
$BackendServiceId = "srv-your-backend-id"
$FrontendServiceId = "srv-your-frontend-id"

# 3. Run deployment
pwsh -File deploy-production.ps1 `
  -BackendServiceId $BackendServiceId `
  -FrontendServiceId $FrontendServiceId

# You'll be prompted:
# - "Enter new version": Type 1.0.1 (or your version number)
# - Script will run all checks automatically

# 4. Wait for completion (10-15 minutes)

# 5. Review deployment report
Get-Content deployment-report-*.md | Select-Object -Last 1

# 6. Run post-deployment tests (optional)
pwsh -File test-production.ps1

# 7. Monitor production
# Keep terminal open for 15-30 minutes
# Watch for errors in Render dashboard: https://dashboard.render.com
```

---

## 🎯 RECOMMENDED FIRST RUN

Since you're running this for the first time, I recommend:

### Option A: Test Only (Safest)
```powershell
pwsh -File test-production.ps1
```
- ✅ No changes to production
- ✅ Shows what's working/broken
- ✅ Generates report

### Option B: Deploy Without Tests (Fastest)
```powershell
pwsh -File deploy-production.ps1 -SkipTests
```
- ⚠️ Skips pre-deployment tests
- ⚠️ Use only if you've already tested manually

### Option C: Full Deployment (Recommended)
```powershell
pwsh -File deploy-production.ps1 `
  -BackendServiceId "srv-xxx" `
  -FrontendServiceId "srv-yyy"
```
- ✅ Complete validation
- ✅ Automated deployment
- ✅ Full reporting

---

## 📚 AVAILABLE FLAGS

### deploy-production.ps1
```powershell
-BackendServiceId "srv-xxx"     # Render backend service ID
-FrontendServiceId "srv-yyy"    # Render frontend service ID
-BackendUrl "https://..."       # Override backend URL
-FrontendUrl "https://..."      # Override frontend URL
-SkipTests                      # Skip pre-deployment tests
-SkipHealthChecks               # Skip post-deployment health checks
-AutoApprove                    # Auto-approve all prompts (CI/CD mode)
```

### test-production.ps1
```powershell
-BackendUrl "https://..."       # Override backend URL
-FrontendUrl "https://..."      # Override frontend URL
-ApiToken "your-token"          # API token for authenticated tests
-Detailed                       # Show detailed response data
```

### rollback-production.ps1
```powershell
-CurrentTag "v1.0.5"           # Required: Current problematic version
-PreviousTag "v1.0.4"          # Required: Target rollback version
-BackendServiceId "srv-xxx"    # Render backend service ID
-FrontendServiceId "srv-yyy"   # Render frontend service ID
-Force                         # Skip confirmation prompt
```

---

## 🔒 SECURITY BEST PRACTICES

1. **Never commit API keys:**
   ```powershell
   # GOOD: Set in session only
   $env:RENDER_API_KEY = "rnd-xxx"

   # BAD: Don't add to scripts or commit
   ```

2. **Store keys securely:**
   ```powershell
   # Use Windows Credential Manager or 1Password
   # Or set permanently (but securely):
   [System.Environment]::SetEnvironmentVariable('RENDER_API_KEY', 'rnd-xxx', 'User')
   ```

3. **Review deployment reports:**
   - Never share reports publicly (they contain URLs, IDs)
   - Review before committing to version control
   - Redact sensitive information if sharing

---

## ✅ SUCCESS CHECKLIST

After deployment, verify:
- [ ] Backend health check returns 200 OK
- [ ] Frontend loads successfully
- [ ] Deployment report shows all tests passed
- [ ] No errors in Render logs
- [ ] All 10 workflows load correctly
- [ ] Market data updates in real-time
- [ ] Position tracking works
- [ ] Order execution functions (paper trading)

---

## 🆘 GETTING HELP

If you encounter issues:

1. **Check the deployment report:**
   ```powershell
   Get-Content deployment-report-*.md | Select-Object -Last 1
   ```

2. **Check Render logs:**
   - Go to https://dashboard.render.com
   - Select service → "Logs" tab
   - Look for errors during deployment

3. **Run diagnostics:**
   ```powershell
   # Test health endpoints
   curl https://paiid-backend.onrender.com/api/health

   # Check service status
   curl https://paiid-backend.onrender.com/api/docs
   ```

4. **Review audit reports:**
   - `COMPREHENSIVE_AUDIT_REPORT.md`
   - `QUICK_FIXES.md`
   - `ISSUE_TRACKER.md`

---

## 📞 NEXT STEPS

**Before deploying:**
1. Review `COMPREHENSIVE_AUDIT_REPORT.md`
2. Consider fixing 12 P0 critical issues first
3. Run `test-production.ps1` to see current status

**After deploying:**
1. Monitor logs for 30 minutes
2. Test all 10 workflow stages
3. Verify real-time data updates
4. Check error rates and response times

---

**Your system is ready! You can start with:**

```powershell
cd C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD
pwsh -File test-production.ps1
```

This will show you the current state of production without making any changes.
