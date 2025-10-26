# PaiiD Deployment Guide

## Overview

This guide covers deployment of the PaiiD trading platform to production environments. PaiiD is deployed on **Render** for both frontend and backend services, with PostgreSQL and Redis for data persistence.

## Table of Contents

1. [Production Architecture](#production-architecture)
2. [Prerequisites](#prerequisites)
3. [Frontend Deployment (Render)](#frontend-deployment-render)
4. [Backend Deployment (Render)](#backend-deployment-render)
5. [Database Setup](#database-setup)
6. [Environment Variables](#environment-variables)
7. [CI/CD Pipeline](#cicd-pipeline)
8. [Post-Deployment Verification](#post-deployment-verification)
9. [Rollback Procedures](#rollback-procedures)
10. [Monitoring and Alerts](#monitoring-and-alerts)

---

## Production Architecture

### Deployed Services

```
┌─────────────────────────────────────────────────────────────┐
│                        Render Cloud                          │
│                                                               │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Frontend Service (Docker)                         │    │
│  │  https://paiid-frontend.onrender.com               │    │
│  │  • Next.js 14 standalone build                     │    │
│  │  • Auto-deploy from main branch                    │    │
│  │  • SSL/TLS automatic                               │    │
│  └────────────────────────────────────────────────────┘    │
│                                                               │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Backend Service (Python)                          │    │
│  │  https://paiid-backend.onrender.com                │    │
│  │  • FastAPI + Uvicorn                               │    │
│  │  • Auto-deploy from main branch                    │    │
│  │  • Health checks enabled                           │    │
│  └────────────────────────────────────────────────────┘    │
│                                                               │
│  ┌────────────────────────────────────────────────────┐    │
│  │  PostgreSQL Database (Managed)                     │    │
│  │  • Auto-backups daily                              │    │
│  │  • SSL connections                                 │    │
│  │  • Connection pooling                              │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘

External Services:
• Tradier API (Market Data)
• Alpaca API (Paper Trading)
• Anthropic API (AI Features)
• Sentry (Error Tracking)
```

### Current Deployment URLs

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | https://paiid-frontend.onrender.com | User interface |
| **Backend** | https://paiid-backend.onrender.com | API server |
| **Health Check** | https://paiid-backend.onrender.com/api/health | Service health |
| **API Docs** | https://paiid-backend.onrender.com/docs | Swagger UI |

---

## Prerequisites

### Required Accounts

1. **GitHub Account** - For repository access
2. **Render Account** - For hosting (sign up at https://render.com)
3. **Tradier Account** - For market data API
4. **Alpaca Account** - For paper trading API
5. **Anthropic Account** - For AI features (optional)
6. **Sentry Account** - For error tracking (optional)

### Required Secrets

Generate the following secrets before deployment:

```bash
# API Token (Backend authentication)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# JWT Secret Key (User authentication)
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Frontend Deployment (Render)

### Step 1: Create Render Service

1. **Log in to Render Dashboard**
   - Navigate to https://dashboard.render.com

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect GitHub repository
   - Select the PaiiD repository

3. **Configure Service**
   ```yaml
   Name: paiid-frontend
   Region: Oregon (US West) or closest to users
   Branch: main
   Root Directory: frontend
   Runtime: Docker
   ```

4. **Build Settings**
   ```yaml
   Build Command: (leave empty - Docker handles this)
   Start Command: (leave empty - Docker handles this)
   Dockerfile Path: ./Dockerfile
   ```

### Step 2: Configure Environment Variables

Add the following environment variables in Render dashboard:

| Variable | Value | Description |
|----------|-------|-------------|
| `NEXT_PUBLIC_BACKEND_API_BASE_URL` | `https://paiid-backend.onrender.com` | Backend API URL |
| `NEXT_PUBLIC_API_TOKEN` | `<your-api-token>` | Backend auth token |
| `NEXT_PUBLIC_ANTHROPIC_API_KEY` | `<your-anthropic-key>` | AI features (optional) |
| `NODE_ENV` | `production` | Environment mode |

### Step 3: Deploy

1. Click "Create Web Service"
2. Render will automatically:
   - Build Docker image
   - Deploy to production
   - Assign SSL certificate
   - Start health checks

**Build Time:** ~5-7 minutes

### Step 4: Verify Deployment

```bash
# Check if frontend is live
curl https://paiid-frontend.onrender.com

# Should return HTML content
```

### Frontend Dockerfile

The frontend uses this production Dockerfile:

```dockerfile
# frontend/Dockerfile
FROM node:20-alpine AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV production
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
ENV PORT 3000

CMD ["node", "server.js"]
```

---

## Backend Deployment (Render)

### Step 1: Create Render Service

1. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Select PaiiD repository
   - Choose Python runtime

2. **Configure Service**
   ```yaml
   Name: paiid-backend
   Region: Oregon (US West) or closest to users
   Branch: main
   Root Directory: backend
   Runtime: Python 3
   ```

3. **Build Settings**
   ```yaml
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   Python Version: 3.10
   ```

### Step 2: Configure Environment Variables

Add these environment variables in Render dashboard:

**Required Secrets:**
```yaml
API_TOKEN: <your-api-token>
JWT_SECRET_KEY: <your-jwt-secret>
DATABASE_URL: <provided-by-render-postgres>
TRADIER_API_KEY: <your-tradier-key>
TRADIER_ACCOUNT_ID: <your-tradier-account>
ALPACA_PAPER_API_KEY: <your-alpaca-key>
ALPACA_PAPER_SECRET_KEY: <your-alpaca-secret>
```

**Optional Services:**
```yaml
ANTHROPIC_API_KEY: <your-anthropic-key>
SENTRY_DSN: <your-sentry-dsn>
REDIS_URL: <redis-connection-string>
```

**Configuration:**
```yaml
ALLOW_ORIGIN: https://paiid-frontend.onrender.com
LIVE_TRADING: false
TESTING: false
LOG_LEVEL: INFO
SENTRY_ENVIRONMENT: production
```

### Step 3: Configure Health Checks

```yaml
Health Check Path: /api/health
Health Check Interval: 60 seconds
Health Check Timeout: 10 seconds
```

### Step 4: Deploy

1. Click "Create Web Service"
2. Render will:
   - Install Python dependencies
   - Start Uvicorn server
   - Run health checks
   - Assign SSL certificate

**Build Time:** ~3-5 minutes

### Step 5: Run Database Migrations

After first deployment, run migrations:

```bash
# Connect to Render shell
render shell -s paiid-backend

# Run migrations
alembic upgrade head
```

### Step 6: Verify Deployment

```bash
# Health check
curl https://paiid-backend.onrender.com/api/health

# Should return:
# {"status": "healthy", "timestamp": "...", "services": {...}}
```

---

## Database Setup

### PostgreSQL on Render

**Step 1: Create Database**

1. **Create PostgreSQL Instance**
   - In Render dashboard: "New +" → "PostgreSQL"
   - Choose plan (Starter or higher)
   - Set name: `paiid-database`
   - Select region (same as backend)

2. **Database Configuration**
   ```yaml
   PostgreSQL Version: 15
   Plan: Starter ($7/month) or Free
   Region: Oregon (US West)
   ```

**Step 2: Connect to Backend**

1. Copy the **Internal Database URL** from Render
2. Add to backend environment variables:
   ```yaml
   DATABASE_URL: postgresql://user:pass@host:5432/dbname
   ```

**Step 3: Initialize Database**

```bash
# Connect to backend shell
render shell -s paiid-backend

# Run migrations
alembic upgrade head

# Verify tables created
psql $DATABASE_URL -c "\dt"
```

### Database Backup Strategy

**Render Automatic Backups:**
- Daily backups (retained 7 days on Starter plan)
- Point-in-time recovery available on Pro plans

**Manual Backup:**
```bash
# Export database
pg_dump $DATABASE_URL > backup.sql

# Restore from backup
psql $DATABASE_URL < backup.sql
```

---

## Environment Variables

### Complete Environment Variable Reference

**Frontend (.env for Render):**

```bash
# Backend API
NEXT_PUBLIC_BACKEND_API_BASE_URL=https://paiid-backend.onrender.com

# Authentication
NEXT_PUBLIC_API_TOKEN=<generated-token>

# AI Features (optional)
NEXT_PUBLIC_ANTHROPIC_API_KEY=<anthropic-key>

# Environment
NODE_ENV=production
```

**Backend (.env for Render):**

```bash
# ==================== REQUIRED SECRETS ====================

# Backend Authentication
API_TOKEN=<generated-token>

# JWT Authentication
JWT_SECRET_KEY=<generated-secret>
JWT_ALGORITHM=HS256

# Database
DATABASE_URL=<render-postgres-url>

# Tradier API (Market Data)
TRADIER_API_KEY=<tradier-key>
TRADIER_ACCOUNT_ID=<tradier-account>
TRADIER_API_BASE_URL=https://api.tradier.com/v1

# Alpaca API (Paper Trading)
ALPACA_PAPER_API_KEY=<alpaca-key>
ALPACA_PAPER_SECRET_KEY=<alpaca-secret>

# ==================== OPTIONAL SERVICES ====================

# Anthropic AI
ANTHROPIC_API_KEY=<anthropic-key>

# Redis Cache
REDIS_URL=<redis-connection-string>

# Sentry Error Tracking
SENTRY_DSN=<sentry-dsn>
SENTRY_ENVIRONMENT=production

# ==================== CONFIGURATION ====================

# CORS
ALLOW_ORIGIN=https://paiid-frontend.onrender.com

# Trading Mode
LIVE_TRADING=false

# Testing
TESTING=false
USE_TEST_FIXTURES=false

# Logging
LOG_LEVEL=INFO

# Cache TTLs (seconds)
CACHE_TTL_QUOTE=5
CACHE_TTL_OPTIONS_CHAIN=60
CACHE_TTL_HISTORICAL_BARS=3600
CACHE_TTL_NEWS=300
```

### Secret Management Best Practices

**1. Never Commit Secrets:**
```bash
# .gitignore should include:
.env
.env.local
.env.production
*.pem
*.key
```

**2. Use Environment-Specific Secrets:**
- Development: Local `.env` files
- Staging: Render environment variables (staging service)
- Production: Render environment variables (production service)

**3. Rotate Secrets Regularly:**
- API tokens: Every 90 days
- JWT secrets: Every 6 months
- Database passwords: Every 6 months

---

## CI/CD Pipeline

### Automatic Deployments

Render automatically deploys when you push to the `main` branch:

```bash
# Make changes
git add .
git commit -m "feat: add new feature"

# Push to main
git push origin main

# Render automatically:
# 1. Detects push to main
# 2. Pulls latest code
# 3. Runs build
# 4. Deploys to production
# 5. Runs health checks
```

### GitHub Actions (Optional)

Create `.github/workflows/deploy.yml` for additional CI checks:

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'

      - name: Install frontend dependencies
        run: cd frontend && npm ci

      - name: Run frontend tests
        run: cd frontend && npm run test:ci

      - name: Build frontend
        run: cd frontend && npm run build

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install backend dependencies
        run: cd backend && pip install -r requirements.txt

      - name: Run backend tests
        run: cd backend && pytest -v

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Render Deploy
        run: echo "Render auto-deploys on push to main"
```

### Deployment Checklist

Before deploying to production:

- [ ] All tests passing locally
- [ ] Environment variables configured on Render
- [ ] Database migrations reviewed
- [ ] API keys valid and active
- [ ] Frontend build succeeds: `npm run build`
- [ ] Backend health check responds: `/api/health`
- [ ] CORS origins configured correctly
- [ ] Error tracking (Sentry) configured
- [ ] Backup strategy in place

---

## Post-Deployment Verification

### Automated Health Checks

**Backend Health Check:**
```bash
curl https://paiid-backend.onrender.com/api/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2025-10-26T12:00:00Z",
  "services": {
    "database": "connected",
    "redis": "connected",
    "tradier": "operational",
    "alpaca": "operational"
  }
}
```

**Frontend Smoke Test:**
```bash
# Check frontend loads
curl -I https://paiid-frontend.onrender.com

# Should return 200 OK
HTTP/2 200
content-type: text/html
```

### Manual Verification Steps

**1. User Authentication:**
- [ ] User can register
- [ ] User can log in
- [ ] JWT tokens issued correctly
- [ ] Protected routes require auth

**2. Market Data:**
- [ ] Real-time quotes loading
- [ ] Options chains displaying
- [ ] Historical charts rendering
- [ ] News feed updating

**3. Trading Functionality:**
- [ ] Order submission works
- [ ] Positions display correctly
- [ ] Account balance accurate
- [ ] P&L calculations correct

**4. AI Features:**
- [ ] AI recommendations generate
- [ ] Chat interface responds
- [ ] Strategy suggestions display

### Performance Checks

```bash
# Response time test
time curl https://paiid-backend.onrender.com/api/health

# Should complete in < 500ms
real    0m0.234s

# Frontend load time
curl -w "@curl-format.txt" -o /dev/null -s https://paiid-frontend.onrender.com

# Should complete in < 2s
```

### Error Monitoring

**Sentry Dashboard:**
1. Navigate to Sentry project
2. Check for new errors
3. Verify error rate < 1%
4. Review performance metrics

**Render Logs:**
```bash
# View backend logs
render logs -s paiid-backend --tail 100

# View frontend logs
render logs -s paiid-frontend --tail 100
```

---

## Rollback Procedures

### Quick Rollback on Render

**Method 1: Revert to Previous Deploy**

1. Navigate to Render dashboard
2. Select service (frontend or backend)
3. Go to "Deploys" tab
4. Find last successful deploy
5. Click "Redeploy" button

**Time to rollback:** ~5 minutes

**Method 2: Git Revert**

```bash
# Revert last commit
git revert HEAD

# Push to main
git push origin main

# Render auto-deploys reverted version
```

**Time to rollback:** ~5-10 minutes (includes build time)

### Emergency Rollback Checklist

- [ ] Identify problematic deployment
- [ ] Check error logs for root cause
- [ ] Notify team of rollback
- [ ] Execute rollback (Method 1 or 2)
- [ ] Verify rollback successful
- [ ] Test critical functionality
- [ ] Document incident
- [ ] Plan fix for next deployment

### Database Rollback

**Rollback Migration:**
```bash
# Connect to backend shell
render shell -s paiid-backend

# Rollback one migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision_id>

# Verify database state
alembic current
```

**Restore from Backup:**
```bash
# Download backup from Render
# Restore to database
psql $DATABASE_URL < backup.sql
```

---

## Monitoring and Alerts

### Render Built-in Monitoring

**Metrics Available:**
- Request count
- Response time (p50, p95, p99)
- Error rate
- Memory usage
- CPU usage

**Access Metrics:**
1. Render Dashboard → Select Service
2. Click "Metrics" tab
3. View real-time graphs

### Sentry Error Tracking

**Setup:**
```python
# backend/app/main.py
import sentry_sdk

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    environment="production",
    traces_sample_rate=0.1
)
```

**Alerts:**
- Configure alerts for error spikes
- Set up Slack/email notifications
- Define alert thresholds

### Custom Health Monitoring

**Uptime Monitoring:**
- Use UptimeRobot or Pingdom
- Monitor `/api/health` endpoint
- Alert on downtime > 1 minute

**Example UptimeRobot Setup:**
```yaml
Monitor Type: HTTP(S)
URL: https://paiid-backend.onrender.com/api/health
Interval: 5 minutes
Alert Contacts: email, Slack
```

### Log Aggregation

**Render Logs:**
```bash
# Real-time logs
render logs -s paiid-backend --tail

# Export logs
render logs -s paiid-backend --since "2025-10-26" > logs.txt
```

**Log Analysis:**
- Search for errors: `grep ERROR logs.txt`
- Count API calls: `grep "GET /api" logs.txt | wc -l`
- Analyze response times: `grep "ms" logs.txt`

---

## Scaling and Performance

### Horizontal Scaling

**Render Auto-Scaling (Pro Plans):**
```yaml
Min Instances: 1
Max Instances: 10
Auto-Scale: Enabled
```

**Manual Scaling:**
1. Render Dashboard → Service Settings
2. Increase instance count
3. Save changes

### Database Scaling

**Connection Pooling:**
```python
# backend/app/db/session.py
engine = create_engine(
    DATABASE_URL,
    pool_size=10,        # Connections per instance
    max_overflow=20      # Additional connections
)
```

**Read Replicas:**
- Upgrade to Pro plan for read replicas
- Separate read/write connections
- Reduce load on primary database

### Caching Strategy

**Redis Cache (Recommended):**
```bash
# Add Redis to Render
# Connect via REDIS_URL environment variable
```

**Cache TTLs:**
- Quotes: 5 seconds
- Options: 60 seconds
- Historical: 1 hour
- News: 5 minutes

---

## Troubleshooting Deployment Issues

### Common Deployment Errors

**1. Build Failure (Frontend):**
```bash
# Check build logs
render logs -s paiid-frontend --deployment <deploy-id>

# Common causes:
# - TypeScript errors
# - Missing dependencies
# - Environment variable issues

# Fix:
# - Run `npm run build` locally
# - Fix errors
# - Commit and push
```

**2. Backend Not Starting:**
```bash
# Check startup logs
render logs -s paiid-backend --tail 100

# Common causes:
# - Missing environment variables
# - Database connection failure
# - Port binding issues

# Fix:
# - Verify all required env vars set
# - Check DATABASE_URL format
# - Ensure PORT=$PORT in start command
```

**3. Health Check Failing:**
```bash
# Test health endpoint locally
curl https://paiid-backend.onrender.com/api/health

# If 500 error, check logs for root cause
# Common causes:
# - Database unreachable
# - Redis connection timeout
# - API key invalid

# Fix:
# - Verify external service credentials
# - Check network connectivity
# - Review health check implementation
```

### Getting Help

**Render Support:**
- Community: https://community.render.com
- Docs: https://render.com/docs
- Support tickets (paid plans)

**PaiiD Team:**
- GitHub Issues: Report deployment issues
- Documentation: Check other docs/ files

---

## Appendix: Deployment Scripts

### Frontend Deployment Script

```bash
#!/bin/bash
# scripts/deploy-frontend.sh

echo "🚀 Deploying Frontend to Render..."

# Build locally first
cd frontend
npm run build

if [ $? -eq 0 ]; then
  echo "✅ Local build successful"
  echo "📤 Pushing to GitHub (triggers Render deploy)..."

  git add .
  git commit -m "deploy: update frontend"
  git push origin main

  echo "✅ Frontend deployment triggered!"
  echo "🔗 Monitor: https://dashboard.render.com"
else
  echo "❌ Build failed. Fix errors before deploying."
  exit 1
fi
```

### Backend Deployment Script

```bash
#!/bin/bash
# scripts/deploy-backend.sh

echo "🚀 Deploying Backend to Render..."

# Run tests first
cd backend
pytest -v

if [ $? -eq 0 ]; then
  echo "✅ Tests passed"
  echo "📤 Pushing to GitHub (triggers Render deploy)..."

  git add .
  git commit -m "deploy: update backend"
  git push origin main

  echo "✅ Backend deployment triggered!"
  echo "🔗 Monitor: https://dashboard.render.com"
else
  echo "❌ Tests failed. Fix errors before deploying."
  exit 1
fi
```

---

**Document Version:** 1.0.0
**Last Updated:** October 26, 2025
**Maintainer:** PaiiD Development Team
