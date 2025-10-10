# Render Deployment Checklist

## Pre-Deployment

- [x] Backend code committed to GitHub (PaiiD repository)
- [x] render.yaml configuration file present
- [x] requirements.txt file present
- [x] Environment variables documented

## During Deployment

- [ ] Logged into Render dashboard
- [ ] Created new Web Service
- [ ] Connected to SCPrime/PaiiD repository
- [ ] Configured service name: paiid-backend
- [ ] Set root directory: backend
- [ ] Set build command: pip install -r requirements.txt
- [ ] Set start command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
- [ ] Added all required environment variables
- [ ] Verified ALLOW_ORIGIN matches Vercel URL
- [ ] Clicked "Create Web Service"

## Post-Deployment

- [ ] Service deployed successfully (Status: Live)
- [ ] Health check responds: /api/health
- [ ] Backend URL noted (e.g., https://paiid-backend.onrender.com)
- [ ] Updated frontend environment variable
- [ ] Tested frontend → backend connectivity

## Required Environment Variables

**Critical (Must Configure):**
1. API_TOKEN
2. TRADIER_API_KEY
3. TRADIER_ACCOUNT_ID
4. ANTHROPIC_API_KEY
5. ALLOW_ORIGIN=https://frontend-scprimes-projects.vercel.app

**Trading Configuration:**
6. TRADIER_USE_SANDBOX=false
7. TRADIER_API_BASE_URL=https://api.tradier.com/v1
8. TRADING_MODE=live
9. SUPERVISOR_MODE=suggest

**Optional (News APIs):**
- ALPHA_VANTAGE_API_KEY
- POLYGON_API_KEY
- FINNHUB_API_KEY

## URLs to Update

**After backend deploys, update these locations:**

1. **Vercel Environment Variable:**
   - Variable: `NEXT_PUBLIC_BACKEND_URL`
   - Value: `<your-render-url>`
   - Action: Redeploy frontend on Vercel

2. **Documentation Files:**
   - VERCEL_DEPLOYMENT_SUMMARY.md
   - DEPLOYMENT_CHECKLIST.md
   - Any other files referencing backend URL
