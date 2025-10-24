# Render Backend Deployment Guide

## Step 1: Create New Web Service

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect to GitHub repository: **SCPrime/PaiiD**

## Step 2: Configure Service Settings

**Basic Settings:**
- **Name:** `paiid-backend`
- **Region:** `Oregon (US West)` (recommended)
- **Branch:** `main`
- **Root Directory:** `backend`
- **Runtime:** `Python 3`

**Build & Deploy:**
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Instance Type:**
- **Free tier** (sufficient for development/testing)

## Step 3: Configure Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**

Add these variables (get values from `backend/.env`):

```
API_TOKEN=<your-token>
TRADIER_API_KEY=<your-key>
TRADIER_ACCOUNT_ID=<your-account>
ANTHROPIC_API_KEY=<your-key>
ALLOW_ORIGIN=https://frontend-scprimes-projects.vercel.app
```

**Critical:** Ensure `ALLOW_ORIGIN` matches your Vercel URL exactly!

## Step 4: Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone repository
   - Install dependencies
   - Start the service
3. Wait 3-5 minutes for deployment to complete

## Step 5: Get Backend URL

Once deployed, Render will assign a URL like:
`https://paiid-backend.onrender.com`

Copy this URL - you'll need it for frontend configuration.

## Step 6: Verify Deployment

Test health endpoint:

```bash
curl https://paiid-backend.onrender.com/api/health
```

Expected response:
```json
{"status":"healthy"}
```

## Troubleshooting

**Build fails:**
- Check that requirements.txt exists in backend/ directory
- Verify Python version compatibility

**Service won't start:**
- Check logs in Render dashboard
- Verify all environment variables are set
- Ensure start command is correct

**CORS errors:**
- Verify ALLOW_ORIGIN exactly matches Vercel URL
- No trailing slash in URL
- Use https:// (not http://)

## Security Notes

✅ Service is deployed from private GitHub repository
✅ Environment variables are encrypted by Render
✅ Only your Vercel frontend can access the API (CORS)
⚠️ Free tier services sleep after 15 minutes of inactivity
