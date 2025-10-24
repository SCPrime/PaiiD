# PaiiD Deployment Instructions - Render Only

**Last Updated**: October 24, 2025  
**Platform**: Render (Backend + Frontend)

---

## Prerequisites

- GitHub repo: `SCPrime/PaiiD`
- Branch: `main`
- Render account with access to the repo
- Environment variables ready (see RENDER_SETUP_GUIDE.md)

---

## Step 1: Deploy Backend to Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **New +** → **Web Service**
3. Connect repository: `SCPrime/PaiiD`
4. Configure:
   - **Name**: `paiid-backend`
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: `backend/`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: Free (or paid for production)

5. **Environment Variables** (click "Advanced" or go to Environment tab):
   ```
   API_TOKEN=<generate-secure-token>
   LIVE_TRADING=false
   ALPACA_PAPER_API_KEY=<your-key>
   ALPACA_PAPER_SECRET_KEY=<your-secret>
   ANTHROPIC_API_KEY=<your-key>
   TRADIER_API_KEY=<your-key>
   TRADIER_ACCOUNT_ID=<your-account>
   DATABASE_URL=<postgres-url>
   REDIS_URL=<redis-url>
   ```

   **Important**:
   - Generate a strong `API_TOKEN` (use `openssl rand -hex 32`)
   - For production, use managed PostgreSQL and Redis services in Render

6. Click **Create Web Service**
7. Wait for deployment (5-10 minutes)
8. **Copy your Render URL**: `https://paiid-backend.onrender.com` (or similar)

### Verify Backend

```bash
curl -s https://paiid-backend.onrender.com/api/health | jq .
```

Expected response:
```json
{
  "status": "ok",
  "timestamp": "...",
  "redis": {...},
  "database": {...}
}
```

---

## Step 2: Deploy Frontend to Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **New +** → **Static Site** (or **Web Service** for server-side rendering)
3. Connect repository: `SCPrime/PaiiD`
4. Configure:
   - **Name**: `paiid-frontend`
   - **Region**: Choose same as backend
   - **Branch**: `main`
   - **Root Directory**: `frontend/`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `.next` (for static) or use start command for SSR

   **For Server-Side Rendering (recommended)**:
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm start`

5. **Environment Variables**:
   ```
   NEXT_PUBLIC_API_BASE_URL=https://paiid-backend.onrender.com
   API_TOKEN=<same-token-as-backend>
   ```

6. Click **Create Static Site** (or **Create Web Service**)
7. Wait for deployment (5-10 minutes)
8. **Copy your Render URL**: `https://paiid-frontend.onrender.com` (or similar)

---

## Step 3: Update Backend CORS

1. Go back to Render dashboard
2. Select your `paiid-backend` service
3. Go to **Environment** tab
4. Add or update `ALLOW_ORIGIN`:
   ```
   ALLOW_ORIGIN=https://paiid-frontend.onrender.com
   ```
5. Save (this will trigger a redeploy ~2-5 min)

---

## Step 4: Acceptance Testing

### Browser Testing

1. Open: `https://paiid-frontend.onrender.com`
2. Open DevTools → Network tab
3. Test authentication:
   - Sign up or log in
   - Verify JWT token in localStorage
4. Test API endpoints:
   - Dashboard loads
   - Positions display
   - Settings accessible
5. Verify in Network tab:
   - All requests go to `https://paiid-backend.onrender.com`
   - No CORS errors
   - No 404/500 errors
   - Response includes status codes

### Terminal Testing

Replace `<backend-url>` and `<your-token>` with your actual values:

```bash
# Test health endpoint
curl -s https://paiid-backend.onrender.com/api/health | jq .

# Test authenticated endpoint
curl -s https://paiid-backend.onrender.com/api/positions \
  -H "authorization: Bearer YOUR_JWT_TOKEN" | jq .
```

---

## Step 5: Configure Auto-Deploy

Both Render services are configured to auto-deploy on push to `main`:

1. Make code changes locally
2. Commit and push:
   ```bash
   git add .
   git commit -m "Your message"
   git push origin main
   ```
3. Render automatically deploys both services
4. Monitor progress in Render dashboard

---

## Architecture Summary

```
User Browser
    ↓
Render Frontend (Next.js)
    ↓ [JWT auth, API calls]
Render Backend (FastAPI)
    ↓
PostgreSQL (Database)
    ↓
Redis (Cache)
```

### Security Features Deployed

- ✅ JWT Authentication (all endpoints)
- ✅ Strict CORS to specific origins
- ✅ CSP + security headers
- ✅ Environment variables hidden (never exposed to browser)
- ✅ Kill-switch (emergency trading halt)
- ✅ Rate limiting (60 req/min per IP)
- ✅ Structured JSON logging
- ✅ Request ID tracing

---

## Troubleshooting

### Backend won't start
- Check Render logs: Dashboard → Service → Logs
- Verify `requirements.txt` exists in `backend/`
- Ensure `PORT` env var is not overridden
- Check all required environment variables are set

### Frontend build fails
- Check Render logs: Dashboard → Service → Logs
- Verify `package.json` exists in `frontend/`
- Ensure all dependencies are in `dependencies` (not just `devDependencies`)
- Check Node.js version compatibility

### CORS errors
- Verify `ALLOW_ORIGIN` on backend matches frontend URL exactly
- No trailing slashes
- Must be HTTPS
- Redeploy backend after changing CORS settings

### API returns 401
- Verify JWT token is valid
- Check token expiration
- Ensure `API_TOKEN` matches on both services
- Test with `/api/auth/login` endpoint first

---

## Cost Estimate

- **Render Free Tier**: $0/month (services sleep after 15min inactivity)
- **Render Starter**: $7/month per service (no sleep, always on)
- **PostgreSQL (managed)**: $7/month
- **Redis (managed)**: $10/month

**Free Total**: $0/month (with cold starts)  
**Production Total**: $31/month (always on, with databases)

---

## Next Steps

After successful deployment:

1. [ ] Test all acceptance criteria above
2. [ ] Monitor Render logs for any errors
3. [ ] Set up PostgreSQL managed service for production
4. [ ] Set up Redis managed service for production
5. [ ] Configure custom domain (optional)
6. [ ] Set up monitoring/alerts (Sentry, etc.)
7. [ ] Run security audit
8. [ ] Document production URLs in OPERATIONS.md

---

## Production Checklist

- [ ] Backend deployed and healthy
- [ ] Frontend deployed and accessible
- [ ] All environment variables configured
- [ ] CORS properly configured
- [ ] JWT authentication working
- [ ] PostgreSQL database connected
- [ ] Redis cache connected
- [ ] Auto-deploy configured
- [ ] Monitoring configured
- [ ] Backup strategy in place
- [ ] Security audit completed

---

**🎉 Deployment Complete!**

Your PaiiD application is now live on Render!

- Frontend: `https://paiid-frontend.onrender.com`
- Backend: `https://paiid-backend.onrender.com`

For daily operations, see `OPERATIONS.md`
