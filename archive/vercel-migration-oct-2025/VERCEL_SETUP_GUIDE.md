# ⚡ Vercel Dashboard Setup Guide

**Platform**: Vercel (Frontend Hosting)
**Service**: PaiiD Frontend
**URL**: https://frontend-scprimes-projects.vercel.app

---

## 📍 Step 1: Access Vercel Dashboard

1. Go to: https://vercel.com/scprimes-projects/frontend
2. Log in with your account
3. Click on the "frontend" project

---

## 🔧 Step 2: Navigate to Environment Variables

1. Click the **"Settings"** tab at the top
2. Click **"Environment Variables"** in the left sidebar
3. You'll see existing variables or an empty list

---

## 🔐 Step 3: Add These Variables

Click "Add New" for each variable below.

### Required Variables (5 total)

| Variable Name | Value | Environments |
|---------------|-------|--------------|
| `NEXT_PUBLIC_BACKEND_API_BASE_URL` | `https://ai-trader-86a1.onrender.com` | ✓ Production, ✓ Preview, ✓ Development |
| `NEXT_PUBLIC_API_TOKEN` | `tuGlKvrYEoiJcv7r7oIy7zXM9pqVnaxN_74obFz6lVo` | ✓ Production, ✓ Preview, ✓ Development |
| `NEXT_PUBLIC_ANTHROPIC_API_KEY` | `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` | ✓ Production, ✓ Preview, ✓ Development |
| `NEXT_PUBLIC_APP_NAME` | `PaiiD` | ✓ Production, ✓ Preview, ✓ Development |
| `NEXT_PUBLIC_TELEMETRY_ENABLED` | `false` | ✓ Production, ✓ Preview, ✓ Development |

**Important**: Check ALL THREE environment boxes for each variable:
- ✓ Production
- ✓ Preview
- ✓ Development

---

## ⚙️ Step 4: Save and Redeploy

### Option A: Trigger Automatic Redeploy
1. After adding all 5 variables, click "Save"
2. Vercel will prompt: "Redeploy to apply changes?"
3. Click **"Redeploy"** → Select "Production" → Click "Redeploy"

### Option B: Manual Redeploy
1. Go to "Deployments" tab
2. Find the latest deployment
3. Click "⋯" (three dots) → "Redeploy"
4. Select "Use existing Build Cache" → Click "Redeploy"

### Option C: Git Push (Easiest)
```bash
# Make any small change or empty commit
git commit --allow-empty -m "chore: trigger vercel redeploy with new env vars"
git push origin main
```

---

## 🔍 Step 5: Verify Deployment

### Watch Deployment Progress

1. Go to "Deployments" tab
2. Click on the active deployment (yellow "Building" badge)
3. Watch build logs for:
   ```
   ▲ Next.js 14.2.33
   Linting and checking validity of types ...
   Creating an optimized production build ...
   ✓ Compiled successfully
   ```

### Test Frontend

Open in browser:
```
https://frontend-scprimes-projects.vercel.app
```

**You should see:**
- PaiiD radial menu interface
- User onboarding (if first visit)
- No 401 errors (SSO is disabled)
- No console errors related to env variables

### Test API Connection

Open browser console (F12) and check:
```javascript
// Should see successful API calls
console.log("Backend URL:", process.env.NEXT_PUBLIC_BACKEND_API_BASE_URL)
```

---

## ✅ Verification Checklist

- [ ] All 5 environment variables added
- [ ] All variables have Production + Preview + Development checked
- [ ] Deployment triggered (auto or manual)
- [ ] Build completed successfully
- [ ] Frontend accessible at production URL
- [ ] No 401/403 errors
- [ ] No env variable undefined errors in console
- [ ] API calls reach backend successfully

---

## 🐛 Troubleshooting

### Issue: "Build failed - Type errors"
**Solution**:
- Check "Deployments" → "Build Logs"
- Look for TypeScript errors
- Verify all imports resolve correctly

### Issue: "401 Unauthorized"
**Solution**:
- Vercel SSO may have re-enabled
- Go to Settings → Deployment Protection
- Disable "Vercel Authentication"

### Issue: "Environment variable undefined in console"
**Solution**:
- Verify variable names start with `NEXT_PUBLIC_`
- Check spelling matches exactly
- Re-deploy after adding missing variables

### Issue: "CORS error" or "Failed to fetch"
**Solution**:
- Verify `NEXT_PUBLIC_BACKEND_API_BASE_URL` is correct
- Check Render backend `ALLOW_ORIGIN` matches Vercel URL
- Verify backend is running (not spun down)

### Issue: "Preview deployments not working"
**Solution**:
- Each preview deployment gets a unique URL
- Render CORS may need wildcard: `https://*.vercel.app`
- Or add each preview URL to backend CORS list

---

## 📝 Notes

### Preview vs Production

- **Production**: https://frontend-scprimes-projects.vercel.app
- **Preview**: https://frontend-[hash]-scprimes-projects.vercel.app
- Both use same environment variables

### Environment Variable Naming

Variables **MUST** start with `NEXT_PUBLIC_` to be accessible in browser:
- ✅ `NEXT_PUBLIC_BACKEND_API_BASE_URL` - Accessible
- ❌ `BACKEND_API_BASE_URL` - Not accessible (server-only)

### Automatic Deployments

Vercel auto-deploys when you push to GitHub:
- Push to `main` → Production deployment
- Push to other branch → Preview deployment
- Pull request → Preview deployment

---

## 🔐 Security Notes

1. **Public Variables**: `NEXT_PUBLIC_*` variables are visible in browser
   - Don't put server-only secrets here
   - API_TOKEN is OK (backend verifies it)
   - Anthropic key should ideally be backend-only (but works here for direct calls)

2. **Key Rotation**: When rotating keys:
   - Update in Vercel dashboard
   - Trigger redeploy
   - Old deployment still uses old keys until rebuilt

---

## 🔗 Quick Links

- **Project Dashboard**: https://vercel.com/scprimes-projects/frontend
- **Settings**: https://vercel.com/scprimes-projects/frontend/settings
- **Environment Variables**: https://vercel.com/scprimes-projects/frontend/settings/environment-variables
- **Deployments**: https://vercel.com/scprimes-projects/frontend/deployments
- **Frontend URL**: https://frontend-scprimes-projects.vercel.app

---

## 🎉 Success!

If all checks pass:
- ✅ Frontend is deployed and accessible
- ✅ Environment variables are set
- ✅ Backend connection works
- ✅ No errors in console

**Next Step**: Test the full application (see API_TEST_CHECKLIST.md)
