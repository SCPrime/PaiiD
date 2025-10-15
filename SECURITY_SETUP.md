# PaiiD - Security Configuration Guide

**Document Version:** 1.0
**Last Updated:** October 15, 2025
**Status:** Critical - Follow these steps immediately after code deployment

---

## 🚨 CRITICAL: API Tokens Removed from Repository

**Security Fix Applied:** All hardcoded API tokens have been removed from the repository for security.
**Action Required:** You MUST configure these tokens in your deployment environments.

---

## 📋 REQUIRED CONFIGURATIONS

### 1. Vercel (Frontend Deployment)

**Location:** Vercel Dashboard → Project Settings → Environment Variables

Add the following environment variables:

```
Variable Name: NEXT_PUBLIC_API_TOKEN
Value: rnd_bDRqi1TvLvd3rC78yvUSgDraH2Kl
Environments: Production, Preview, Development
```

**Steps:**
1. Go to https://vercel.com/dashboard
2. Select your project: `frontend-scprimes-projects`
3. Click "Settings" → "Environment Variables"
4. Add `NEXT_PUBLIC_API_TOKEN` with the value above
5. Select all environments (Production, Preview, Development)
6. Click "Save"
7. Redeploy your application (Settings → Deployments → Redeploy)

---

### 2. GitHub Actions (CI/CD Pipeline)

**Location:** GitHub Repository → Settings → Secrets and variables → Actions

Add the following secret:

```
Secret Name: API_TOKEN
Value: tuGlKvrYEoiJcv7r7oIy7zXM9pqVnaxN_74obFz6lVo
```

**Steps:**
1. Go to https://github.com/scprimes/ai-Trader (replace with your org/repo)
2. Click "Settings" → "Secrets and variables" → "Actions"
3. Click "New repository secret"
4. Name: `API_TOKEN`
5. Value: (paste the token above)
6. Click "Add secret"

**Note:** The CI workflow at `.github/workflows/ci.yml` is already configured to use `${{ secrets.API_TOKEN }}`.

---

### 3. Render (Backend Deployment)

**Location:** Render Dashboard → Service → Environment

The backend requires the following environment variables (these should already be set):

```
API_TOKEN=rnd_bDRqi1TvLvd3rC78yvUSgDraH2Kl
TRADIER_API_KEY=<your-tradier-api-key>
TRADIER_ACCOUNT_ID=<your-tradier-account-id>
ALPACA_PAPER_API_KEY=<your-alpaca-paper-key>
ALPACA_PAPER_SECRET_KEY=<your-alpaca-paper-secret>
ANTHROPIC_API_KEY=<your-anthropic-api-key>
```

**Steps to Verify/Update:**
1. Go to https://dashboard.render.com
2. Select your service: `paiid-backend`
3. Click "Environment" tab
4. Verify `API_TOKEN` is set
5. Click "Save Changes" if updated
6. Service will auto-redeploy

---

## 🔐 SECURITY BEST PRACTICES

### Token Rotation Schedule

**Recommended:** Rotate API tokens every 90 days for security.

**How to Rotate:**
1. Generate new token (use a secure random generator)
2. Update in Vercel, GitHub Secrets, and Render
3. Deploy changes
4. Test all endpoints
5. Revoke old token after 24 hours

### Token Generation

Use a cryptographically secure random generator:

```bash
# Linux/Mac
openssl rand -base64 32

# Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"

# Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Never Commit Tokens

**Gitignore patterns** (already configured):
- `.env`
- `.env.local`
- `.env.*.local`

**If you accidentally commit a token:**
1. Revoke the token immediately
2. Remove from Git history using `git filter-branch` or BFG Repo-Cleaner
3. Generate and deploy new token
4. Force push to remote (if repository is private)

---

## 🔍 VERIFICATION CHECKLIST

After configuring tokens, verify everything works:

### Frontend Verification
- [ ] Visit https://frontend-scprimes-projects.vercel.app
- [ ] Check browser console for no "API_TOKEN not configured" errors
- [ ] Click "Active Positions" - should load data without errors
- [ ] Check Network tab - `/api/proxy/*` requests should return 200

### Backend Verification
```bash
# Health check
curl https://paiid-backend.onrender.com/api/health

# Authenticated request
curl -H "Authorization: Bearer rnd_bDRqi1TvLvd3rC78yvUSgDraH2Kl" \
  https://paiid-backend.onrender.com/api/positions
```

### CI/CD Verification
- [ ] Push a commit to `main` branch
- [ ] Check GitHub Actions: https://github.com/<org>/<repo>/actions
- [ ] Verify "Build frontend" step passes
- [ ] Check for no "API_TOKEN" related errors in logs

---

## 🚨 TROUBLESHOOTING

### Issue: "API_TOKEN not configured" in browser console

**Cause:** Vercel environment variable not set or not deployed
**Fix:**
1. Verify variable exists in Vercel dashboard
2. Redeploy: Vercel Dashboard → Deployments → ... → Redeploy
3. Clear browser cache and hard refresh (Ctrl+Shift+R)

### Issue: GitHub Actions build fails with "API_TOKEN" error

**Cause:** GitHub secret not configured
**Fix:**
1. Verify secret exists: GitHub → Settings → Secrets and variables → Actions
2. Check secret name is exactly `API_TOKEN` (case-sensitive)
3. Re-run failed workflow: GitHub Actions → Re-run jobs

### Issue: Backend returns 401 Unauthorized

**Cause:** Token mismatch between frontend and backend
**Fix:**
1. Verify frontend token in Vercel matches backend token in Render
2. Both should be: `rnd_bDRqi1TvLvd3rC78yvUSgDraH2Kl`
3. Redeploy both services if tokens were updated

### Issue: CORS errors after security update

**Cause:** Origin not in allowed list
**Fix:**
1. Check your deployment URL matches one in `ALLOWED_ORIGINS`
2. Update `frontend/pages/api/proxy/[...path].ts` if needed
3. Allowed origins are:
   - `http://localhost:3000` (development)
   - `https://frontend-scprimes-projects.vercel.app` (production)
   - `https://*-projects.vercel.app` (preview deployments)

---

## 📊 SECURITY MONITORING

### What to Monitor

1. **Failed Authentication Attempts**
   - Check backend logs for 401/403 errors
   - Set up alerts for spike in auth failures

2. **Unusual API Usage**
   - Monitor request volume per endpoint
   - Alert on sudden spikes

3. **Token Exposure**
   - Use GitHub secret scanning alerts
   - Monitor for accidental commits

### Sentry Integration (Recommended)

Configure Sentry DSN for production error tracking:

**Environment Variable:**
```
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

**Add to:**
- Render (backend): Environment tab
- Vercel (frontend): Environment Variables

**Code is already configured** - just add the DSN!

---

## 🔄 INCIDENT RESPONSE

### If Token is Compromised

**Immediate Actions (< 5 minutes):**
1. Generate new token
2. Update in Vercel, GitHub, Render
3. Deploy all services
4. Monitor for unauthorized access

**Post-Incident (< 24 hours):**
1. Review access logs for suspicious activity
2. Rotate all other secrets (Tradier, Alpaca, Anthropic)
3. Document incident
4. Update security procedures if needed

### Emergency Contacts

- **Platform Owner:** [Your contact info]
- **DevOps Lead:** [Contact info]
- **Security Team:** [Contact info]

---

## ✅ SIGN-OFF

Once all tokens are configured, verify this checklist:

- [ ] Vercel environment variable set (`NEXT_PUBLIC_API_TOKEN`)
- [ ] GitHub secret set (`API_TOKEN`)
- [ ] Render environment variables verified (all tokens)
- [ ] Frontend deployment successful
- [ ] Backend health check passes
- [ ] CI/CD pipeline passes
- [ ] All workflows tested and functional
- [ ] Monitoring configured (optional but recommended)
- [ ] Documentation updated

---

## 📚 ADDITIONAL RESOURCES

- **Vercel Docs:** https://vercel.com/docs/concepts/projects/environment-variables
- **GitHub Secrets:** https://docs.github.com/en/actions/security-guides/encrypted-secrets
- **Render Env Vars:** https://render.com/docs/environment-variables
- **Token Best Practices:** https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html

---

**Document Status:** ✅ Complete
**Review Date:** October 15, 2026 (annual review)
**Maintained By:** Development Team

---

_PaiiD - Securing your investment dashboard with industry best practices_ 🔐
