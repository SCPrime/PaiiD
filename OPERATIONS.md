# PaiiD Operations Card

**Production Environment** | Last updated: 2025-10-24

---

## 🌐 Live URLs (Render Only)

| Service            | URL                                           | Purpose           |
| ------------------ | --------------------------------------------- | ----------------- |
| **Frontend**       | https://paiid-frontend.onrender.com           | Main UI (Next.js) |
| **Backend**        | https://paiid-backend.onrender.com            | FastAPI service   |
| **Backend Health** | https://paiid-backend.onrender.com/api/health | Health check      |

---

## 🚦 Health Checks (30 seconds)

### Quick browser checks
1. **Backend Health**: https://paiid-backend.onrender.com/api/health
   ✅ Expect: `{"status":"ok", "time":"..."}`

2. **Frontend Root**: https://paiid-frontend.onrender.com/
   ✅ Expect: PaiiD Dashboard UI

### Automated smoke test (PowerShell)
```powershell
cd C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD
.\test-deployment.ps1
```

**Expected output**: All tests passing
- Backend health ✅
- Frontend root ✅

---

## 🧯 Emergency Controls

### Kill-Switch (Halt All Live Trading)

**Enable kill-switch** (blocks all live orders):
```bash
curl -X POST "https://paiid-backend.onrender.com/api/admin/kill" \
  -H "content-type: application/json" -d "true"
```

**Disable kill-switch** (resume trading):
```bash
curl -X POST "https://paiid-backend.onrender.com/api/admin/kill" \
  -H "content-type: application/json" -d "false"
```

**Verify status**:
```bash
curl "https://paiid-backend.onrender.com/api/settings"
# Look for: "tradingHalted": true/false
```

### Safety Net
- **LIVE_TRADING=false** (Render env var): All executes become dry-runs regardless of request
- **Kill-switch=true**: Blocks live executes even if LIVE_TRADING=true
- **Both layers must be green** for live orders to execute

---

## 🔄 Deploy & Update

### Backend (Render)
**Auto-deploy**: Push to `main` → Render builds automatically

**Manual redeploy**:
Render → your service → Manual Deploy → Deploy latest commit

**Check logs**:
Render → Logs → look for "Application startup complete"

### Frontend (Render)
**Auto-deploy**: Push to `main` → Render builds automatically

**Manual redeploy**:
Render → your service → Manual Deploy → Deploy latest commit

**Check logs**:
Render → Logs → look for "Build complete"

---

## 🧪 Test Execution Flow (Dry-Run)

### Single dry-run order
```bash
curl -X POST "https://paiid-backend.onrender.com/api/trading/execute" \
  -H "content-type: application/json" \
  -H "authorization: Bearer YOUR_TOKEN" \
  -d '{
    "dryRun": true,
    "requestId": "test-'$(date +%s)'",
    "orders": [
      {"symbol": "SPY", "side": "buy", "qty": 1, "type": "market"}
    ]
  }'
```

**Expected**: `{"accepted": true, "dryRun": true, "orders": [...]}`

---

## 🔐 Security Checklist

- ✅ **JWT Authentication**: All endpoints require valid JWT tokens
- ✅ **CORS configured**: Backend accepts only from frontend domain
- ✅ **Rate limiting**: 60 req/min per IP
- ✅ **Kill-switch**: Independent safety layer
- ✅ **Environment variables**: All secrets in Render dashboard only

### Environment Variables (DO NOT COMMIT)

**Render Backend**:
```
API_TOKEN=<secret-token>
LIVE_TRADING=false
ALPACA_PAPER_API_KEY=<key>
ALPACA_PAPER_SECRET_KEY=<secret>
ANTHROPIC_API_KEY=<key>
TRADIER_API_KEY=<key>
TRADIER_ACCOUNT_ID=<account>
DATABASE_URL=<postgres-url>
REDIS_URL=<redis-url>
```

**Render Frontend**:
```
NEXT_PUBLIC_API_BASE_URL=https://paiid-backend.onrender.com
API_TOKEN=<same-as-backend>
```

---

## 🔧 Common Tasks

### View current settings
```bash
curl "https://paiid-backend.onrender.com/api/settings" \
  -H "authorization: Bearer YOUR_TOKEN"
```

### View positions
```bash
curl "https://paiid-backend.onrender.com/api/positions" \
  -H "authorization: Bearer YOUR_TOKEN"
```

### Check build status
- **Render Dashboard**: https://dashboard.render.com → Services → Events

---

## 📊 Monitoring Checklist

### Daily (automated)
- [ ] Run smoke test: `.\test-deployment.ps1`
- [ ] Check Render deployment status: all services "Live"

### Before going live
- [ ] Verify kill-switch works (enable → test live execute → expect 423)
- [ ] Verify LIVE_TRADING is correct (false for safety)
- [ ] Confirm backend health endpoint returns OK
- [ ] Check Redis connection (if enabled): `"redis": {"connected": true}`

### During live trading window
- [ ] Kill-switch disabled (trading allowed)
- [ ] LIVE_TRADING=true on Render
- [ ] Monitor Render logs for errors
- [ ] Keep smoke tests ready to verify health

### After trading window
- [ ] Enable kill-switch (safety)
- [ ] Set LIVE_TRADING=false on Render
- [ ] Review logs for any failed orders

---

## 🚨 Troubleshooting

| Symptom                | Check          | Fix                                 |
| ---------------------- | -------------- | ----------------------------------- |
| Backend won't start    | Render logs    | Check environment variables         |
| Frontend 404           | Build logs     | Verify build completed successfully |
| Backend returns 403    | CORS / Origin  | Check ALLOW_ORIGIN env var          |
| TypeScript build fails | Dependencies   | Ensure TS is in `dependencies`      |
| API returns 401        | Authentication | Verify JWT token is valid           |

### Get help fast
1. **Build logs**: Render → Service → Logs
2. **Runtime logs**: Render → Service → Logs (live tail)
3. **Test locally**: `cd backend && uvicorn app.main:app --reload`

---

## 📞 Key Contacts

| Role        | Contact      | Responsibility             |
| ----------- | ------------ | -------------------------- |
| DevOps      | Dr. SC Prime | Deployment, infrastructure |
| Trading Ops | TBD          | Live execution approval    |
| Security    | TBD          | Token rotation, audits     |

---

## 🔄 Everyday Workflow

1. **Make changes** in Cursor/VS Code
2. **Commit & push** to `main`:
   ```bash
   git add .
   git commit -m "your message"
   git push origin main
   ```
3. **Wait for auto-deploy**: Render (~3-5 min for both services)
4. **Verify**: Run `.\test-deployment.ps1`

---

## 🎯 Production Readiness

| Component          | Status | Notes                                          |
| ------------------ | ------ | ---------------------------------------------- |
| Frontend build     | ✅      | Next.js 14, TypeScript                         |
| Backend API        | ✅      | FastAPI, JWT auth, kill-switch                 |
| Health checks      | ✅      | Automated smoke tests                          |
| Kill-switch        | ✅      | Tested, operational                            |
| CORS security      | ✅      | Configured for Render frontend                 |
| Secrets management | ✅      | Server-side only, no leaks                     |
| Monitoring         | ⚠️      | Manual smoke tests (automate via cron/Actions) |
| JWT Migration      | ✅      | All endpoints standardized                     |

---

**Last Updated**: 2025-10-24 (Vercel decommissioned - Render only)  
**Maintained By**: Dr. SC Prime  
**Repo**: https://github.com/SCPrime/PaiiD
