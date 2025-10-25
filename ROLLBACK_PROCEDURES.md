# Rollback Procedures
**Project**: PaiiD  
**Date**: October 24, 2025  
**Purpose**: Emergency rollback procedures for production deployments

---

## Quick Reference

**When to Rollback**:
- Critical bugs affecting >50% of users
- Security vulnerability discovered
- Database corruption
- Complete service outage >10 minutes
- Data loss or integrity issues

**Decision Maker**: Engineering Lead or On-Call Engineer

**Maximum Time to Rollback**: 5 minutes

---

## Rollback Methods

### Method 1: Git Revert (Fastest)

```bash
# 1. Identify the problematic commit
git log --oneline -10

# 2. Revert to last known good commit
git revert <commit-hash> --no-edit

# 3. Push to trigger re-deployment
git push origin main

# 4. Monitor deployment
watch -n 2 'curl https://api.paiid.com/health'
```

**Time**: ~2-3 minutes  
**Use When**: Code changes are the issue

---

### Method 2: GitHub Deployment Rollback

```bash
# 1. Go to GitHub Actions
https://github.com/YourOrg/PaiiD/actions

# 2. Find last successful deployment
# Click "Re-run all jobs"

# 3. Monitor progress
# Deployment typically takes 5-8 minutes
```

**Time**: ~5-8 minutes  
**Use When**: Current deployment failed

---

### Method 3: Database Rollback

```bash
# 1. Stop application servers
./scripts/stop-production.sh

# 2. Restore database from backup
psql -U postgres -d paiid_prod < backups/paiid_backup_YYYYMMDD_HHMMSS.sql

# 3. Verify restore
psql -U postgres -d paiid_prod -c "SELECT COUNT(*) FROM users;"

# 4. Restart application
./scripts/start-production.sh

# 5. Run health check
curl https://api.paiid.com/health
```

**Time**: ~10-15 minutes (depends on database size)  
**Use When**: Database migration failed or data corruption

---

### Method 4: Full System Rollback

```bash
# 1. Activate maintenance mode
./scripts/maintenance-mode.sh enable

# 2. Rollback frontend
cd frontend
git checkout tags/v1.0.0  # Last stable version
npm run build
./scripts/deploy-frontend.sh

# 3. Rollback backend
cd backend
git checkout tags/v1.0.0  # Last stable version
./scripts/deploy-backend.sh

# 4. Rollback database (if needed)
psql -U postgres -d paiid_prod < backups/paiid_backup_stable.sql

# 5. Disable maintenance mode
./scripts/maintenance-mode.sh disable

# 6. Verify all services
./scripts/health-check-all.sh
```

**Time**: ~15-20 minutes  
**Use When**: Multiple systems affected

---

## Step-by-Step Rollback Guide

### Pre-Rollback Checklist

1. **Verify the issue**
   - [ ] Confirm issue is widespread (not isolated)
   - [ ] Check error logs
   - [ ] Review monitoring dashboards
   - [ ] Document exact symptoms

2. **Notify stakeholders**
   - [ ] Alert engineering team (Slack #incidents)
   - [ ] Notify product/business teams
   - [ ] Update status page (if public)

3. **Prepare rollback**
   - [ ] Identify last known good version
   - [ ] Verify backups are available
   - [ ] Have rollback commands ready

### During Rollback

1. **Execute rollback** (choose method above)
   
2. **Monitor progress**
   ```bash
   # Watch application logs
   tail -f /var/log/paiid/application.log
   
   # Monitor error rates
   # Check Sentry/monitoring dashboard
   
   # Test critical endpoints
   curl https://api.paiid.com/api/auth/login
   curl https://api.paiid.com/api/portfolio/test
   ```

3. **Verify recovery**
   - [ ] Health checks passing
   - [ ] Error rates normalized
   - [ ] Key features functional
   - [ ] User reports resolved

### Post-Rollback

1. **Confirm stability**
   - Monitor for 30 minutes
   - Verify no new errors
   - Check user feedback

2. **Document incident**
   - Create incident report
   - Timeline of events
   - Root cause (if known)
   - Actions taken

3. **Plan forward**
   - Schedule post-mortem meeting
   - Create fix strategy
   - Plan re-deployment

---

## Rollback Decision Tree

```
Critical Issue Detected
        |
        ▼
Is it affecting >50% of users?
        |
   YES  |  NO
        |   └──> Monitor closely, prepare rollback
        ▼
Is it a security issue?
        |
   YES  |  NO
        |   └──> Can it be hotfixed in <10 min?
        |            |
        |       YES  |  NO
        |            |   └──> ROLLBACK
        ▼            ▼
    ROLLBACK    Deploy hotfix
```

---

## Automated Rollback Scripts

### Script 1: Quick Rollback
```bash
#!/bin/bash
# scripts/quick-rollback.sh

echo "🔄 Starting emergency rollback..."

# Revert to last commit
git revert HEAD --no-edit
git push origin main

echo "✅ Rollback initiated - monitoring deployment..."
watch -n 5 'curl -s https://api.paiid.com/health | jq'
```

### Script 2: Database Rollback
```bash
#!/bin/bash
# scripts/rollback-database.sh

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: ./rollback-database.sh <backup_file>"
    exit 1
fi

echo "⚠️  WARNING: This will restore database from backup"
echo "Backup file: $BACKUP_FILE"
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Rollback cancelled"
    exit 0
fi

echo "🛑 Stopping application..."
./scripts/stop-production.sh

echo "📥 Restoring database..."
psql -U postgres -d paiid_prod < "$BACKUP_FILE"

echo "🚀 Starting application..."
./scripts/start-production.sh

echo "✅ Database rollback complete"
```

---

## Communication Templates

### Slack Incident Alert
```
🚨 INCIDENT ALERT 🚨

**Issue**: [Brief description]
**Severity**: [Critical/High/Medium]
**Impact**: [% of users affected]
**Status**: Rollback in progress
**ETA**: [Time estimate]

**Actions**:
- [ ] Rollback initiated
- [ ] Monitoring progress
- [ ] Will update in 5 minutes

cc: @engineering @oncall
```

### Status Page Update
```
We're experiencing issues with [feature/service].

Our team is working on a fix and we expect to have
normal service restored within [time estimate].

We apologize for any inconvenience.

Status: [Investigating / Fixing / Monitoring]
Updated: [Timestamp]
```

### Post-Resolution Update
```
✅ RESOLVED

The issue has been resolved. All systems are now
operating normally.

We rolled back to a previous stable version and
verified all services are functioning correctly.

A full incident report will be published within
24 hours.

Thank you for your patience.
```

---

## Testing Rollback Procedures

### Quarterly Rollback Drill

1. **Schedule drill** (e.g., third Thursday of quarter)
2. **Notify team** (but not users)
3. **Execute rollback** in staging environment
4. **Time the process**
5. **Document lessons learned**
6. **Update procedures** if needed

### Staging Environment Testing

```bash
# Test rollback in staging before production
export ENVIRONMENT=staging

# 1. Deploy new version to staging
./scripts/deploy-staging.sh

# 2. Simulate issue
./scripts/simulate-error.sh

# 3. Execute rollback
./scripts/quick-rollback.sh

# 4. Verify recovery
./scripts/health-check-all.sh

# 5. Document results
echo "Rollback test completed at $(date)" >> rollback-tests.log
```

---

## Backup Strategy

### Automated Backups

- **Frequency**: Every 6 hours
- **Retention**: 7 days rolling
- **Location**: AWS S3 / Google Cloud Storage
- **Encryption**: AES-256

### Manual Backups

Create manual backup before major deployments:

```bash
# Create backup
pg_dump -U postgres paiid_prod > backups/pre-deploy-$(date +%Y%m%d_%H%M%S).sql

# Verify backup
ls -lh backups/ | tail -1

# Upload to cloud storage
aws s3 cp backups/pre-deploy-*.sql s3://paiid-backups/manual/
```

---

## Contact Information

### On-Call Rotation
- **Primary**: [Name] - [Phone] - [Email]
- **Secondary**: [Name] - [Phone] - [Email]
- **Escalation**: [Engineering Lead] - [Phone]

### External Contacts
- **Hosting Provider**: [Support contact]
- **Database Provider**: [Support contact]
- **CDN Provider**: [Support contact]

---

## Post-Incident Review Template

```markdown
# Incident Report: [Date]

## Summary
[Brief description of what happened]

## Timeline
- [HH:MM] - Issue first detected
- [HH:MM] - Rollback initiated
- [HH:MM] - Service restored
- [HH:MM] - Confirmed stable

## Root Cause
[What caused the issue]

## Impact
- Users affected: [Number/Percentage]
- Downtime: [Duration]
- Data loss: [Yes/No - Details]

## Resolution
[What was done to fix it]

## Prevention
[How to prevent this in the future]

## Action Items
- [ ] [Action 1] - Owner: [Name] - Due: [Date]
- [ ] [Action 2] - Owner: [Name] - Due: [Date]

## Lessons Learned
[Key takeaways]
```

---

## Status

**Documentation**: ✅ COMPLETE  
**Scripts Created**: 📋 PENDING  
**Tested**: ⚠️ NOT YET  
**Team Training**: 📋 PENDING

---

**Last Updated**: October 24, 2025  
**Next Review**: Quarterly (or after any incident)  
**Owner**: DevOps Team
