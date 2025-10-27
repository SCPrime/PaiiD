# Render Environment Variables Checklist - Frontend

**Last Updated:** 2025-10-27
**Service:** paiid-frontend (Next.js Docker Deployment)
**Region:** Oregon (us-west)
**Plan:** Free Tier

---

## Critical Requirements

### Environment Variables Configuration

All environment variables must be set in the **Render Dashboard** under:
`Service Settings → Environment Variables`

---

## Required Environment Variables

### 1. NEXT_PUBLIC_API_TOKEN
**Purpose:** Authentication token for frontend-backend communication
**Where to Set:** Render Dashboard (Environment Variables)
**Type:** Secret (sensitive)
**Format:** Alphanumeric string (48+ characters)

**Production Value:**
```
NEXT_PUBLIC_API_TOKEN=***[MUST MATCH BACKEND API_TOKEN]***
```

**Current Local Value (from .env.local):**
```
tuGlKvrYEoiJcv7r7oIy7zXM9pqVnaxN_74obFz6lVo
```

**Verification Steps:**
1. ✅ Value is set in Render dashboard
2. ✅ Value matches backend `API_TOKEN` EXACTLY
3. ✅ Test with: `curl -H "Authorization: Bearer <token>" https://paiid-backend.onrender.com/api/health`
4. ✅ Response should be: `{"status":"ok","time":"..."}`

**Critical Note:** This token MUST match the backend's `API_TOKEN` or all API requests will fail with 401/403 errors.

---

### 2. NEXT_PUBLIC_BACKEND_API_BASE_URL
**Purpose:** Base URL for backend API endpoints
**Where to Set:** render.yaml (hardcoded) OR Render Dashboard
**Type:** Public (not sensitive)
**Format:** HTTPS URL

**Production Value:**
```
NEXT_PUBLIC_BACKEND_API_BASE_URL=https://paiid-backend.onrender.com
```

**Verification Steps:**
1. ✅ Value is set to `https://paiid-backend.onrender.com` (no trailing slash)
2. ✅ Backend health check responds: `curl https://paiid-backend.onrender.com/api/health`
3. ✅ Expected response: `{"status":"ok","time":"2025-..."}`
4. ✅ No CORS errors in browser console when frontend calls backend

**Critical Note:** This is already set in render.yaml line 16. DO NOT override unless backend URL changes.

---

### 3. NEXT_PUBLIC_ANTHROPIC_API_KEY
**Purpose:** Claude AI API key for conversational onboarding and strategy building
**Where to Set:** Render Dashboard (Environment Variables)
**Type:** Secret (highly sensitive - NEVER commit to git)
**Format:** `sk-ant-api03-...` (starts with sk-ant-)

**Production Value:**
```
NEXT_PUBLIC_ANTHROPIC_API_KEY=sk-ant-api03-***[YOUR_KEY_HERE]***
```

**Current Local Value (from .env.local):**
```
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
```

**Verification Steps:**
1. ✅ Value is set in Render dashboard
2. ✅ Key starts with `sk-ant-api03-`
3. ✅ Test AI chat in frontend after deployment
4. ✅ No "API key not configured" errors in browser console
5. ✅ UserSetupAI component loads successfully

**Critical Note:** Without this key, AI features (onboarding, strategy builder, recommendations) will fail.

---

## Docker Build Arguments

These are passed during Docker build (Stage 1) and runtime (Stage 2):

### Build-Time Arguments (from Dockerfile lines 19-26)
```dockerfile
ARG NEXT_PUBLIC_API_TOKEN
ARG NEXT_PUBLIC_BACKEND_API_BASE_URL
ARG NEXT_PUBLIC_ANTHROPIC_API_KEY
```

### Runtime Arguments (from Dockerfile lines 61-72)
```dockerfile
ARG API_TOKEN
ARG NEXT_PUBLIC_API_TOKEN
ARG NEXT_PUBLIC_BACKEND_API_BASE_URL
ARG NEXT_PUBLIC_ANTHROPIC_API_KEY
```

**Render Behavior:** Render automatically passes environment variables as build args and runtime env vars.

---

## Hardcoded Environment Variables (render.yaml)

These are set automatically by render.yaml and should NOT be changed:

### NODE_ENV
```yaml
- key: NODE_ENV
  value: production
```
**Purpose:** Enables production optimizations in Next.js

### PORT
```yaml
- key: PORT
  value: "3000"
```
**Purpose:** Port for Next.js server (matches Dockerfile EXPOSE 3000)

---

## API Proxy Configuration

The API proxy (`pages/api/proxy/[...path].ts`) uses these environment variables:

### Server-Side API Token Loading (lines 5-9)
```typescript
const BACKEND =
  process.env.BACKEND_API_BASE_URL ||
  process.env.NEXT_PUBLIC_BACKEND_API_BASE_URL ||
  "https://paiid-backend.onrender.com";

const API_TOKEN = process.env.API_TOKEN || process.env.NEXT_PUBLIC_API_TOKEN || "";
```

**Important:** The proxy checks BOTH `API_TOKEN` and `NEXT_PUBLIC_API_TOKEN`. Set BOTH in Render dashboard:
- `API_TOKEN=<your-token>` (for server-side API routes)
- `NEXT_PUBLIC_API_TOKEN=<your-token>` (for client-side code)

**Both should have the SAME value!**

---

## CORS Configuration

### Allowed Origins (lines 107-118)
```typescript
const ALLOWED_ORIGINS = new Set<string>([
  "http://localhost:3000",
  "http://localhost:3003",
  "http://localhost:3004",
  "http://localhost:3005",
  "http://localhost:3006",
  "http://localhost:3007",
  "http://localhost:3008",
  "http://localhost:3009",
  "http://localhost:3010",
  "https://paiid-frontend.onrender.com", // ✅ PRODUCTION URL
]);
```

**Verification Steps:**
1. ✅ `https://paiid-frontend.onrender.com` is in ALLOWED_ORIGINS (line 117)
2. ✅ Backend CORS middleware allows this origin (see backend/app/main.py line 661)
3. ✅ No CORS errors in browser console
4. ✅ API requests return data (not 403 Forbidden)

---

## Environment Variable Validation Checklist

### Pre-Deployment Checks
- [ ] `NEXT_PUBLIC_API_TOKEN` is set in Render dashboard
- [ ] `API_TOKEN` is set in Render dashboard (same value as above)
- [ ] `NEXT_PUBLIC_API_TOKEN` matches backend `API_TOKEN` exactly
- [ ] `NEXT_PUBLIC_BACKEND_API_BASE_URL` is `https://paiid-backend.onrender.com`
- [ ] `NEXT_PUBLIC_ANTHROPIC_API_KEY` is set in Render dashboard
- [ ] `NODE_ENV` is set to `production` (auto-set by render.yaml)
- [ ] `PORT` is set to `3000` (auto-set by render.yaml)

### Post-Deployment Checks
- [ ] Frontend loads at https://paiid-frontend.onrender.com
- [ ] Health check responds: https://paiid-frontend.onrender.com/
- [ ] API proxy works: Open browser console, check for API calls to `/api/proxy/*`
- [ ] No "API key not configured" errors in console
- [ ] No CORS errors in console
- [ ] Backend health check responds: https://paiid-backend.onrender.com/api/health
- [ ] AI chat interface loads (tests Anthropic API key)
- [ ] Market data loads in RadialMenu center logo (tests backend connectivity)

---

## Common Issues & Solutions

### Issue 1: "API key not configured" in console
**Cause:** `NEXT_PUBLIC_ANTHROPIC_API_KEY` not set or invalid
**Solution:**
1. Check Render dashboard → Environment Variables
2. Verify key starts with `sk-ant-api03-`
3. Redeploy to reload environment variables

### Issue 2: All API requests fail with 401 Unauthorized
**Cause:** `NEXT_PUBLIC_API_TOKEN` doesn't match backend `API_TOKEN`
**Solution:**
1. Compare frontend and backend API tokens in Render dashboards
2. Ensure both are EXACTLY the same (case-sensitive)
3. Redeploy both services

### Issue 3: CORS errors in browser console
**Cause:** Frontend origin not in ALLOWED_ORIGINS or backend CORS config
**Solution:**
1. Verify `https://paiid-frontend.onrender.com` is in proxy allowed origins (line 117)
2. Verify backend CORS middleware includes this URL (backend/app/main.py line 661)
3. Redeploy if code changes needed

### Issue 4: API requests timeout or fail with 502
**Cause:** Backend is not running or URL is incorrect
**Solution:**
1. Check backend status: https://paiid-backend.onrender.com/api/health
2. Verify `NEXT_PUBLIC_BACKEND_API_BASE_URL` is correct
3. Check backend logs in Render dashboard

---

## Security Notes

### What to NEVER Commit to Git
- ❌ API tokens (NEXT_PUBLIC_API_TOKEN, API_TOKEN)
- ❌ Anthropic API keys (NEXT_PUBLIC_ANTHROPIC_API_KEY)
- ❌ Any secrets from .env.local

### What is Safe to Commit
- ✅ render.yaml (contains no secrets, only references)
- ✅ Dockerfile (contains no secrets, only ARG declarations)
- ✅ Backend URL (public information)

### API Token Rotation
If you need to rotate the API token:
1. Generate new token (48+ character random string)
2. Update in backend Render dashboard (`API_TOKEN`)
3. Update in frontend Render dashboard (`NEXT_PUBLIC_API_TOKEN` and `API_TOKEN`)
4. Redeploy both services
5. Test end-to-end connectivity

---

## Quick Reference

| Variable | Frontend Render | Backend Render | Must Match? |
|----------|----------------|----------------|-------------|
| `API_TOKEN` | ✅ Set | ✅ Set | ✅ YES |
| `NEXT_PUBLIC_API_TOKEN` | ✅ Set | ❌ N/A | ✅ Must match backend `API_TOKEN` |
| `NEXT_PUBLIC_BACKEND_API_BASE_URL` | ✅ Set | ❌ N/A | ❌ No |
| `NEXT_PUBLIC_ANTHROPIC_API_KEY` | ✅ Set | ❌ N/A | ❌ No |
| `NODE_ENV` | ✅ Auto | ✅ Auto | ❌ No |

---

## Contact & Support

**Documentation:**
- Main: `README.md`
- Deployment: `docs/DEPLOYMENT.md`
- Troubleshooting: `docs/TROUBLESHOOTING.md`

**Backend Health Check:**
```bash
curl https://paiid-backend.onrender.com/api/health
```

**Test API Token:**
```bash
curl -H "Authorization: Bearer <your-token>" \
  https://paiid-backend.onrender.com/api/health
```

**Expected Response:**
```json
{"status":"ok","time":"2025-10-27T..."}
```
