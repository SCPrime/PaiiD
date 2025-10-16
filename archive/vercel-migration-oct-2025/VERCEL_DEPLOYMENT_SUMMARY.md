# Vercel Deployment Summary

**Deployment Date:** Thu Oct 9 2025 23:39:11 GMT-0400 (Eastern Daylight Time)
**Project Name:** frontend
**Platform:** Vercel

## Deployment Details

**Production URL:** https://frontend-scprimes-projects.vercel.app
**Deployment URL:** https://frontend-3902d9g6z-scprimes-projects.vercel.app
**Additional Aliases:**
- https://frontend-three-rho-84.vercel.app
- https://frontend-scprime-scprimes-projects.vercel.app

**Framework:** Next.js 14.2.33
**Build Command:** npm run build
**Output Directory:** .next
**Node Version:** v20.18.0
**Region:** iad1 (US East)

## Environment Variables

```
NEXT_PUBLIC_BACKEND_URL=https://paiid-backend.onrender.com
```

## Deployment Status

- Build: ✅ Successful
- Tests: ✅ Passed
- TypeScript: ✅ No errors
- Deployment: ✅ Live (Ready)
- Build Time: ~2 seconds

## Build Output

**API Routes (Lambda Functions):**
- api/ai/recommendations (664.61KB)
- api/ai/suggest-strategy (664.61KB)
- api/market/historical (664.61KB)
- api/market/options-chain (664.61KB)
- api/pnl/calculate-theoretical (664.61KB)
- api/pnl/comparison/[positionId] (664.61KB)
- api/pnl/track-position (664.61KB)
- api/proposals (664.61KB)
- api/proposals/[id]/approve (664.61KB)
- api/proposals/[id]/reject (664.61KB)
- api/proposals/[id]/reprice (664.61KB)
- api/proxy/[...path] (664.61KB)
- api/strategies (664.61KB)
- api/strategies/[strategyId]/versions (664.61KB)

**Static Pages:**
- / (homepage)
- /404
- /test-radial

## Next Steps

1. ✅ Frontend deployed to Vercel
2. ⏳ Deploy backend to Render (Stage 15)
3. ⏳ Configure backend environment variables
4. ⏳ Test API connectivity
5. ⏳ Verify CORS configuration

## Rollback Information

Previous deployment: ai-trader (20+ deployments)
Frozen backup: ai-Trader-frozen-backup-20251009
Repository: https://github.com/SCPrime/PaiiD
Git commit: c318f6f (CORS update)

## Verification Commands

```bash
# Check deployment status
vercel ls frontend

# View deployment logs
vercel logs frontend-3902d9g6z-scprimes-projects.vercel.app

# Inspect deployment
vercel inspect frontend-3902d9g6z-scprimes-projects.vercel.app

# Redeploy if needed
cd frontend && vercel --prod
```

## CORS Configuration

Backend render.yaml updated to allow:
- ALLOW_ORIGIN: https://frontend-scprimes-projects.vercel.app

## Deployment ID

**ID:** dpl_3vfyX4hZSdwHdwnE2jpBtKAADG4j
**Target:** production
**Created:** Thu Oct 09 2025 23:39:11 GMT-0400
