# PaiiD Deployment Guide

Complete deployment guide for production infrastructure.

## 🚀 Production Deployments

### Current Deployment Status

**Live Production URLs:**
- Frontend: https://paiid-frontend.onrender.com
- Backend: https://paiid-backend.onrender.com

**Platform:** Render.com (Free Tier)

---

## 📋 Prerequisites

### Required Accounts
1. **Render.com** - Application hosting
2. **GitHub** - Source code repository
3. **Stripe** (Optional) - Payment processing
4. **Redis Cloud** (Optional) - ML prediction caching
5. **PostgreSQL** (Optional) - Database for analytics

### Required Secrets

**Frontend Environment Variables:**
```env
NEXT_PUBLIC_API_TOKEN=rnd_bDRqi1TvLvd3rC78yvUSgDraH2Kl
NEXT_PUBLIC_BACKEND_API_BASE_URL=https://paiid-backend.onrender.com
NEXT_PUBLIC_ANTHROPIC_API_KEY=<your-claude-api-key>
```

**Backend Environment Variables:**
```env
API_TOKEN=rnd_bDRqi1TvLvd3rC78yvUSgDraH2Kl
TRADIER_API_KEY=<your-tradier-key>
TRADIER_ACCOUNT_ID=<your-tradier-account>
TRADIER_API_BASE_URL=https://api.tradier.com/v1
ALPACA_PAPER_API_KEY=<your-alpaca-key>
ALPACA_PAPER_SECRET_KEY=<your-alpaca-secret>
ALLOW_ORIGIN=https://paiid-frontend.onrender.com
STRIPE_SECRET_KEY=<your-stripe-secret> (Optional)
STRIPE_WEBHOOK_SECRET=<your-stripe-webhook-secret> (Optional)
REDIS_URL=<your-redis-url> (Optional)
DATABASE_URL=<your-postgres-url> (Optional)
```

---

## 🔧 Render.com Deployment

### Frontend Deployment

1. **Create New Web Service**
   - Connect GitHub repository
   - Root Directory: `frontend`
   - Environment: Docker
   - Build Command: Automatic (uses Dockerfile)
   - Start Command: `node server.js`

2. **Environment Variables**
   - Add all frontend env vars in Render dashboard
   - Enable "Auto-Deploy" for `main` branch

3. **Custom Domain (Optional)**
   - Add custom domain in Render settings
   - Update DNS records per Render instructions

### Backend Deployment

1. **Create New Web Service**
   - Connect GitHub repository
   - Root Directory: `backend`
   - Environment: Python 3.11
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

2. **Environment Variables**
   - Add all backend env vars in Render dashboard
   - Enable "Auto-Deploy" for `main` branch

3. **Health Checks**
   - Path: `/api/health`
   - Expected Status: 200 OK

---

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

The `.github/workflows/ci-cd.yml` file automates:

**On Pull Request:**
- ✅ Frontend tests & build
- ✅ Backend tests & linting
- ✅ Security scanning (Trivy)
- ✅ Lighthouse performance audit
- ✅ Preview deployment

**On Main Branch Push:**
- ✅ All PR checks
- ✅ Automated deployment to production
- ✅ Health checks post-deployment
- ✅ Deployment notifications

### Required GitHub Secrets

Add these to repository Settings > Secrets:

```
NEXT_PUBLIC_API_TOKEN
RENDER_FRONTEND_DEPLOY_HOOK
RENDER_BACKEND_DEPLOY_HOOK
```

---

## 📊 Monitoring & Observability

### Health Endpoints

**Frontend Health:**
```bash
curl https://paiid-frontend.onrender.com
# Should return 200 OK with HTML
```

**Backend Health:**
```bash
curl https://paiid-backend.onrender.com/api/health
# Response: {"status": "healthy", "environment": "production"}
```

### Performance Monitoring

**Recommended Tools:**
1. **Sentry** - Error tracking
2. **LogRocket** - Session replay
3. **Render Metrics** - Built-in monitoring
4. **Google Analytics** - User analytics

### Logging

**Backend Logs:**
- Access via Render dashboard
- Filter by severity level
- Real-time log streaming

**Frontend Logs:**
- Browser console (development)
- Sentry for production errors
- Server logs in Render dashboard

---

## 🔐 Security Best Practices

### Environment Variables
- Never commit `.env` files
- Use Render's environment variable management
- Rotate API keys regularly

### API Security
- CORS configured for specific origins
- Rate limiting enabled (SlowAPI)
- API token authentication
- HTTPS only in production

### Dependency Security
- Regular `npm audit` and `pip check`
- Dependabot alerts enabled
- Trivy security scanning in CI

---

## 🚨 Troubleshooting

### Common Issues

**Build Failures:**
```bash
# Frontend
cd frontend && npm run build

# Backend
cd backend && pip install -r requirements.txt
```

**CORS Errors:**
- Verify `ALLOW_ORIGIN` matches frontend URL
- Check Render environment variables

**API Connection Failed:**
- Verify `NEXT_PUBLIC_BACKEND_API_BASE_URL`
- Check backend health endpoint
- Review Render logs

**Deployment Stuck:**
- Check Render dashboard for errors
- Verify GitHub Actions workflow status
- Review build logs

---

## 📈 Scaling Considerations

### Current Limitations (Free Tier)
- 512 MB RAM per service
- Services spin down after 15 min inactivity
- 750 compute hours/month
- No horizontal scaling

### Upgrade Path
1. **Starter Plan ($7/month per service)**
   - Always-on instances
   - 1 GB RAM
   - Custom domains

2. **Standard Plan ($25/month per service)**
   - 2 GB RAM
   - Horizontal scaling
   - Priority support

3. **Pro Plan ($85/month per service)**
   - 8 GB RAM
   - Advanced scaling
   - Dedicated resources

---

## 🎯 Deployment Checklist

**Pre-Deployment:**
- [ ] All tests passing locally
- [ ] Environment variables configured
- [ ] Build succeeds locally
- [ ] API keys valid and active
- [ ] Database migrations ready (if applicable)

**Post-Deployment:**
- [ ] Health checks passing
- [ ] Frontend loading correctly
- [ ] Backend API responding
- [ ] Trading data flowing
- [ ] ML predictions working
- [ ] Subscription system functional
- [ ] Error tracking active

---

## 📞 Support

**Issues:**
- GitHub Issues: https://github.com/SCPrime/PaiiD/issues
- Email: support@paiid.app

**Resources:**
- Render Docs: https://render.com/docs
- Next.js Docs: https://nextjs.org/docs
- FastAPI Docs: https://fastapi.tiangolo.com

---

## 🏆 Production Readiness

**Achieved:**
- ✅ CI/CD pipeline
- ✅ Automated deployments
- ✅ Health monitoring
- ✅ Security scanning
- ✅ Error boundaries
- ✅ Rate limiting
- ✅ Model persistence
- ✅ Caching layer
- ✅ Subscription system
- ✅ PWA support

**Recommended Next Steps:**
1. Enable Sentry error tracking
2. Set up database backups
3. Configure monitoring alerts
4. Add custom domain
5. Enable CDN for static assets
6. Implement A/B testing
7. Set up staging environment

---

Generated with ❤️ by Claude Code
