#!/bin/bash
# EXECUTE-BATCH-7.sh - Setup production monitoring

echo "📊 BATCH 7: PRODUCTION MONITORING SETUP"
echo "======================================="

# Install dependencies
pip install psutil  # For health_monitor.py

# Create monitoring directory
mkdir -p monitoring/logs
mkdir -p backups

# Make scripts executable
chmod +x backup-database.sh
chmod +x monitor-production.sh

# Setup cron jobs
echo "Setting up automated tasks..."

# Add to crontab
(crontab -l 2>/dev/null; echo "0 2 * * * $(pwd)/backup-database.sh >> monitoring/logs/backup.log 2>&1") | crontab -
(crontab -l 2>/dev/null; echo "*/5 * * * * $(pwd)/monitor-production.sh >> monitoring/logs/monitor.log 2>&1") | crontab -

echo "✅ Cron jobs configured:"
echo "   - Daily backup at 2 AM"
echo "   - Monitoring every 5 minutes"

# Commit monitoring code
git add backend/app/services/health_monitor.py
git add backend/app/services/alerts.py
git add backend/app/routers/health.py
git add backend/app/middleware/metrics.py
git add frontend/components/admin/PerformanceDashboard.tsx
git add backup-database.sh
git add monitor-production.sh

git commit -m "feat: add production monitoring and alerting

- Health monitoring service with system metrics
- Enhanced health endpoints
- Request tracking middleware
- Automated database backups
- Alert system with Slack integration
- Performance dashboard UI
- Continuous monitoring script"

git push origin main

echo ""
echo "✅ BATCH 7 COMPLETE!"
echo ""
echo "📊 Monitoring Features:"
echo "   - Health metrics at /api/health/detailed"
echo "   - Performance dashboard in admin UI"
echo "   - Automated backups daily"
echo "   - Continuous monitoring every 5 min"
echo "   - Slack alerts for critical issues"
echo ""
