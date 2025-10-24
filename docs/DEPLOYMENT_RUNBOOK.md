# PaiiD Deployment Runbook

## Overview

This runbook provides comprehensive procedures for deploying the PaiiD application to production environments. It covers pre-deployment checks, deployment procedures, post-deployment verification, and troubleshooting.

## Pre-Deployment Checklist

### Environment Preparation

- [ ] **Backend Environment Variables**
  - [ ] `SENTRY_DSN` configured for error tracking
  - [ ] `REDIS_URL` configured for caching
  - [ ] `DATABASE_URL` configured for persistence
  - [ ] `TRADIER_API_KEY` configured for market data
  - [ ] `ALPACA_API_KEY` and `ALPACA_SECRET_KEY` configured for trading
  - [ ] `ANTHROPIC_API_KEY` configured for AI features
  - [ ] `API_TOKEN` configured for authentication
  - [ ] `LIVE_TRADING` set to `false` for paper trading
  - [ ] `SENTRY_ENVIRONMENT` set to `production`
  - [ ] `LOG_LEVEL` set to `INFO` or `WARNING`

- [ ] **Frontend Environment Variables**
  - [ ] `NEXT_PUBLIC_API_BASE_URL` pointing to backend
  - [ ] `API_TOKEN` matching backend configuration

- [ ] **Infrastructure**
  - [ ] Render services configured and accessible
  - [ ] Vercel project configured (if using Vercel)
  - [ ] Domain names configured and DNS propagated
  - [ ] SSL certificates valid and not expiring soon

### Code Quality Checks

- [ ] **Git Status**
  - [ ] All changes committed and pushed
  - [ ] No uncommitted changes in working directory
  - [ ] Current branch is `main` or approved release branch
  - [ ] No merge conflicts

- [ ] **Configuration Validation**
  - [ ] Render configuration files validated
  - [ ] Hold points validated (no locked files modified)
  - [ ] Environment variables validated

- [ ] **Testing**
  - [ ] Backend pre-launch validation passes
  - [ ] Frontend build succeeds
  - [ ] All unit tests pass
  - [ ] Integration tests pass
  - [ ] Playwright tests pass (if applicable)

### Security Checks

- [ ] **Secrets Management**
  - [ ] No secrets in code or configuration files
  - [ ] All secrets properly configured in environment variables
  - [ ] API keys have appropriate permissions and limits
  - [ ] Database credentials are secure

- [ ] **Access Control**
  - [ ] Authentication endpoints protected
  - [ ] Rate limiting configured
  - [ ] CORS settings appropriate for production
  - [ ] Admin endpoints secured

## Deployment Procedures

### Option 1: Automated Deployment (Recommended)

#### Bash Deployment (Linux/macOS)

```bash
# Set required environment variables
export RENDER_API_KEY="your-render-api-key"
export BACKEND_SERVICE_ID="your-backend-service-id"
export FRONTEND_SERVICE_ID="your-frontend-service-id"

# Run deployment with full verification
./deploy.sh --auto-approve

# Or with custom URLs
./deploy.sh \
  --backend-url "https://your-backend.onrender.com" \
  --frontend-url "https://your-frontend.onrender.com" \
  --auto-approve
```

#### PowerShell Deployment (Windows)

```powershell
# Run deployment with full verification
.\deploy.ps1

# Or skip specific services
.\deploy.ps1 -SkipRender
.\deploy.ps1 -SkipVercel
```

### Option 2: Manual Deployment

#### Backend Deployment (Render)

1. **Navigate to Render Dashboard**
   - Go to https://dashboard.render.com
   - Select your backend service

2. **Trigger Deployment**
   - Click "Manual Deploy"
   - Select "Deploy latest commit"
   - Monitor deployment progress

3. **Verify Environment Variables**
   - Check all required environment variables are set
   - Verify values are correct and not expired

4. **Monitor Logs**
   - Watch deployment logs for errors
   - Check startup logs for configuration issues
   - Verify all services are connecting properly

#### Frontend Deployment (Vercel)

1. **Navigate to Vercel Dashboard**
   - Go to https://vercel.com/dashboard
   - Select your project

2. **Trigger Deployment**
   - Click "Deploy" or push to connected branch
   - Monitor deployment progress

3. **Verify Environment Variables**
   - Check all required environment variables are set
   - Verify API endpoints are correct

## Post-Deployment Verification

### Automated Verification

Run the comprehensive verification script:

```bash
# Bash
./scripts/verify-deployment.sh \
  --backend-url "https://your-backend.onrender.com" \
  --frontend-url "https://your-frontend.onrender.com" \
  --verbose

# PowerShell
.\scripts\verify-deployment.ps1 \
  -BackendUrl "https://your-backend.onrender.com" \
  -FrontendUrl "https://your-frontend.onrender.com" \
  -Verbose
```

### Manual Verification

#### Backend Health Checks

1. **Basic Health**
   ```bash
   curl https://your-backend.onrender.com/api/health
   ```
   Expected: `{"status": "healthy"}`

2. **Detailed Health**
   ```bash
   curl https://your-backend.onrender.com/api/health/detailed
   ```
   Expected: Detailed health information

3. **Configuration**
   ```bash
   curl https://your-backend.onrender.com/api/settings/config
   ```
   Expected: Configuration without secrets

#### Frontend Health Checks

1. **Homepage**
   ```bash
   curl https://your-frontend.onrender.com
   ```
   Expected: HTML page with PaiiD content

2. **Static Assets**
   ```bash
   curl https://your-frontend.onrender.com/_next/static
   ```
   Expected: Static file directory

#### API Integration Tests

1. **Market Data**
   ```bash
   curl https://your-backend.onrender.com/api/market/conditions
   ```
   Expected: Market conditions data

2. **Settings**
   ```bash
   curl https://your-backend.onrender.com/api/settings
   ```
   Expected: Trading settings

3. **Authentication**
   ```bash
   curl -H "Authorization: Bearer your-api-token" \
        https://your-backend.onrender.com/api/positions
   ```
   Expected: Positions data (if authenticated)

### Performance Verification

1. **Response Times**
   - Backend health: < 2 seconds
   - API endpoints: < 5 seconds
   - Frontend load: < 3 seconds

2. **Error Rates**
   - Health endpoints: 0% errors
   - API endpoints: < 1% errors
   - Frontend: < 0.1% errors

## Common Deployment Issues

### Issue: Backend Startup Failures

**Symptoms:**
- Backend service shows "Failed" status
- Health endpoint returns 503
- Logs show startup errors

**Troubleshooting:**
1. Check environment variables are set correctly
2. Verify external service connectivity (Redis, Database)
3. Check for port conflicts
4. Review startup logs for specific errors

**Resolution:**
```bash
# Check environment variables
curl -H "Authorization: Bearer $RENDER_API_KEY" \
     https://api.render.com/v1/services/$SERVICE_ID/env-vars

# Check service logs
curl -H "Authorization: Bearer $RENDER_API_KEY" \
     https://api.render.com/v1/services/$SERVICE_ID/logs
```

### Issue: Frontend Build Failures

**Symptoms:**
- Frontend deployment fails during build
- Build logs show compilation errors
- Static assets not loading

**Troubleshooting:**
1. Check for TypeScript errors
2. Verify all dependencies are installed
3. Check for missing environment variables
4. Review build logs for specific errors

**Resolution:**
```bash
# Test build locally
cd frontend
npm install
npm run build

# Check for TypeScript errors
npm run type-check
```

### Issue: API Connectivity Problems

**Symptoms:**
- Frontend cannot connect to backend
- CORS errors in browser console
- API endpoints return 404

**Troubleshooting:**
1. Verify backend URL is correct
2. Check CORS configuration
3. Verify API routes are registered
4. Check for proxy configuration issues

**Resolution:**
```bash
# Test API connectivity
curl -v https://your-backend.onrender.com/api/health

# Check CORS headers
curl -H "Origin: https://your-frontend.onrender.com" \
     -v https://your-backend.onrender.com/api/health
```

### Issue: Environment Variable Problems

**Symptoms:**
- Backend shows configuration errors
- API keys not working
- Database connection failures

**Troubleshooting:**
1. Verify all required environment variables are set
2. Check for typos in variable names
3. Verify values are correct and not expired
4. Check for missing quotes or special characters

**Resolution:**
```bash
# List all environment variables
curl -H "Authorization: Bearer $RENDER_API_KEY" \
     https://api.render.com/v1/services/$SERVICE_ID/env-vars

# Update environment variables
curl -X POST \
     -H "Authorization: Bearer $RENDER_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"key": "VARIABLE_NAME", "value": "VARIABLE_VALUE"}' \
     https://api.render.com/v1/services/$SERVICE_ID/env-vars
```

## Rollback Procedures

### Emergency Rollback

If critical issues are detected:

1. **Immediate Actions**
   - Stop all user traffic if possible
   - Document the issue and symptoms
   - Notify stakeholders

2. **Rollback Backend**
   ```bash
   # Rollback to previous deployment
   curl -X POST \
        -H "Authorization: Bearer $RENDER_API_KEY" \
        -H "Content-Type: application/json" \
        -d '{"commit": "previous-commit-hash"}' \
        https://api.render.com/v1/services/$BACKEND_SERVICE_ID/deploys
   ```

3. **Rollback Frontend**
   ```bash
   # Rollback to previous deployment
   curl -X POST \
        -H "Authorization: Bearer $VERCEL_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"gitRef": "previous-commit-hash"}' \
        https://api.vercel.com/v1/deployments
   ```

4. **Verification**
   - Run health checks on rolled back services
   - Verify functionality is restored
   - Monitor for any remaining issues

### Planned Rollback

For planned rollbacks:

1. **Preparation**
   - Identify the target commit/version
   - Verify the target version is stable
   - Prepare rollback plan

2. **Execution**
   - Follow the same rollback procedures as emergency
   - Monitor deployment progress
   - Verify all services are healthy

3. **Post-Rollback**
   - Run full verification suite
   - Document rollback reason and results
   - Plan investigation of original issue

## Monitoring and Alerting

### Key Metrics to Monitor

1. **Backend Metrics**
   - Response time (target: < 2s)
   - Error rate (target: < 1%)
   - CPU usage (target: < 80%)
   - Memory usage (target: < 80%)

2. **Frontend Metrics**
   - Page load time (target: < 3s)
   - Error rate (target: < 0.1%)
   - User experience metrics

3. **Business Metrics**
   - API request volume
   - User authentication success rate
   - Trading operation success rate

### Alerting Thresholds

- **Critical**: Service down, > 5% error rate
- **Warning**: > 2s response time, > 1% error rate
- **Info**: Deployment completed, configuration changes

## Emergency Contacts

### Development Team
- **Primary**: [Your Name] - [Phone] - [Email]
- **Secondary**: [Team Member] - [Phone] - [Email]

### Infrastructure Team
- **Render Support**: https://render.com/support
- **Vercel Support**: https://vercel.com/support

### Escalation Procedures

1. **Level 1**: Development team (0-15 minutes)
2. **Level 2**: Senior developer/architect (15-30 minutes)
3. **Level 3**: Engineering manager (30+ minutes)
4. **Level 4**: CTO/VP Engineering (1+ hours)

## Post-Deployment Tasks

### Immediate (0-1 hour)
- [ ] Verify all health checks pass
- [ ] Monitor error rates and response times
- [ ] Check logs for any issues
- [ ] Notify stakeholders of successful deployment

### Short-term (1-24 hours)
- [ ] Monitor user feedback and reports
- [ ] Check business metrics and KPIs
- [ ] Review performance metrics
- [ ] Update documentation if needed

### Long-term (1-7 days)
- [ ] Conduct post-deployment review
- [ ] Document lessons learned
- [ ] Update deployment procedures if needed
- [ ] Plan next deployment cycle

## Documentation Updates

After each deployment:

1. **Update Deployment Log**
   - Record deployment date and time
   - Document any issues encountered
   - Note configuration changes

2. **Update Runbook**
   - Add new troubleshooting procedures
   - Update contact information
   - Refine deployment procedures

3. **Update Architecture Documentation**
   - Document infrastructure changes
   - Update system diagrams
   - Record configuration changes

## Conclusion

This runbook provides comprehensive procedures for deploying and maintaining the PaiiD application. Regular updates and practice with these procedures will ensure smooth deployments and quick resolution of any issues.

For questions or updates to this runbook, contact the development team or create an issue in the project repository.
