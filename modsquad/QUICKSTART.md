# META-ORCHESTRATOR QUICK START GUIDE
**For:** Dr. SC Prime and authorized operators
**Last Updated:** October 31, 2025

---

## INSTANT COMMANDS

### Resume Agent Oversight (After App Shutdown)
```bash
# Quick health check (3 core validations, ~15s)
python scripts/meta_orchestrator.py --mode quick

# Full validation suite (includes browser tests, ~2-5min)
python scripts/meta_orchestrator.py --mode full --risk-target 0.5

# Launch live monitoring dashboard
python scripts/meta_dashboard.py
```

### Check Current Status
```bash
# One-time status display
python scripts/meta_dashboard.py --once

# View latest execution report
cat reports/meta_orchestrator_*.txt | tail -1
```

### Run Individual Checks
```bash
# Repository audit
python scripts/auto_github_monitor.py --full-audit

# Live data flows
python scripts/live_data_flows.py --comprehensive

# Branding/accessibility
python scripts/branding_a11y_checks.py

# Wedge components
python scripts/wedge_flows.py
```

---

## COMMON SCENARIOS

### Scenario 1: App Just Shut Down, Need to Resume
**What to do:**
```bash
# 1. Quick health check first
python scripts/meta_orchestrator.py --mode quick

# 2. If all green, launch continuous monitoring
python scripts/meta_dashboard.py

# 3. Review status report
cat modsquad/META_ORCHESTRATOR_STATUS.md
```

**Expected output:**
```
[OK] RISK RATE: 0.00% (TARGET: <2.0%)
[OK] PRODUCTION READINESS: APPROVED
[OK] SUCCESS: All validations passed
```

### Scenario 2: Pre-Deployment Validation
**What to do:**
```bash
# Run full validation suite with strict target
python scripts/meta_orchestrator.py --mode full --risk-target 0.5

# If all pass, proceed with deployment
# If any fail, review errors in reports/meta_orchestrator_*.txt
```

### Scenario 3: Something Broke, Need to Investigate
**What to do:**
```bash
# 1. Check what's failing
python scripts/meta_orchestrator.py --mode quick

# 2. View detailed execution logs
cat modsquad/logs/execution_log_*.jsonl | tail -20

# 3. Run specific failing check manually for debugging
python scripts/live_data_flows.py --comprehensive
python scripts/browser_mod.py --check-render --live-data

# 4. Check recent validation reports
ls -lt reports/*.json | head -5
cat reports/live_flows*.json
```

### Scenario 4: Continuous Monitoring During Development
**What to do:**
```bash
# Terminal 1: Keep dashboard running
python scripts/meta_dashboard.py

# Terminal 2: Run validation after each change
python scripts/meta_orchestrator.py --mode quick

# Terminal 3: Normal development work
cd frontend && npm run dev
# or
cd backend && python -m uvicorn app.main:app --reload --port 8001
```

### Scenario 5: Scheduled Maintenance Check
**What to do:**
```bash
# Run comprehensive validation
python scripts/meta_orchestrator.py --mode full --risk-target 0.5 > maintenance_$(date +%Y%m%d).log

# Review any warnings or errors
grep -E '\[FAIL\]|\[WARN\]' maintenance_*.log

# Update status documentation
cat modsquad/META_ORCHESTRATOR_STATUS.md
```

---

## INTERPRETING RESULTS

### Risk Rate Thresholds
- **0.00% - 0.50%:** ✅ GREEN (production ready)
- **0.51% - 2.00%:** ⚠️ YELLOW (investigate, staging OK)
- **2.01% - 5.00%:** 🔶 ORANGE (deployment blocked, fix required)
- **> 5.00%:** 🚨 RED (critical issues, immediate action)

### Exit Codes
- **0:** Success, all validations passed
- **1:** Failures detected or risk rate exceeded target
- **130:** User interrupted (Ctrl+C)

### Log File Locations
```
modsquad/logs/execution_log_YYYYMMDD_HHMMSS.jsonl    # Detailed task logs
reports/meta_orchestrator_YYYYMMDD_HHMMSS.txt        # Validation reports
reports/github_mod.json                               # Repository audit
reports/live_flows.json                               # Data flow validation
reports/browser_mod.json                              # Browser test results
```

---

## DASHBOARD METRICS EXPLAINED

### Execution Metrics
- **Total Tasks:** Number of validation checks executed
- **Completed:** Successfully finished tasks
- **In Progress:** Currently running tasks (should be 0 when idle)
- **Failed:** Tasks that encountered errors
- **Pending:** Queued tasks waiting to execute

### Error/Warning Counts
- **Errors:** Critical issues blocking production readiness
- **Warnings:** Non-critical issues requiring attention

### Risk Rate Calculation
```
Risk Rate = (Total Errors / Total Tasks) × 100%
```

Example:
- 3 tasks run, 0 errors → 0.00% risk rate ✅
- 10 tasks run, 1 error → 10.00% risk rate 🚨

---

## TROUBLESHOOTING

### Problem: Meta-orchestrator not found
**Solution:**
```bash
# Ensure you're in project root
cd C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD

# Verify script exists
ls scripts/meta_orchestrator.py

# Check Python environment
python --version  # Should be 3.9+
```

### Problem: Validation failures
**Solution:**
```bash
# 1. Check which validation failed
python scripts/meta_orchestrator.py --mode quick

# 2. Run failing check directly for details
python scripts/live_data_flows.py --comprehensive
python scripts/auto_github_monitor.py --full-audit

# 3. Review error messages in output
# 4. Fix underlying issue
# 5. Re-run validation
```

### Problem: Dashboard shows old data
**Solution:**
```bash
# Dashboard reads latest execution log
# Run a new validation to refresh:
python scripts/meta_orchestrator.py --mode quick

# Then view dashboard:
python scripts/meta_dashboard.py --once
```

### Problem: Services not responding
**Solution:**
```bash
# Check if backend is running
curl http://127.0.0.1:8001/api/health

# If not, start backend
cd backend
python -m uvicorn app.main:app --reload --port 8001

# Check if frontend is running
curl http://localhost:3000

# If not, start frontend
cd frontend
npm run dev
```

---

## MAINTENANCE SCHEDULE

### Daily (Every 24 hours)
```bash
# Morning health check
python scripts/meta_orchestrator.py --mode full --risk-target 0.5
```

### Weekly (Every Sunday)
```bash
# Comprehensive audit
python scripts/meta_orchestrator.py --mode full --risk-target 0.5
python scripts/design-dna-validator.py

# Review all logs
ls -lt modsquad/logs/ | head -10
```

### Pre-Deployment (Before every production push)
```bash
# Strict validation
python scripts/meta_orchestrator.py --mode full --risk-target 0.5

# Manual smoke test
# 1. Login to production
# 2. Execute a paper trade
# 3. View positions
# 4. Check P&L analytics
```

---

## CONTACT & ESCALATION

### Automated Monitoring
- Meta-Dashboard: Run `python scripts/meta_dashboard.py` (keep open)
- Logs: `modsquad/logs/execution_log_*.jsonl`
- Reports: `reports/meta_orchestrator_*.txt`

### Manual Review
- Status: `modsquad/META_ORCHESTRATOR_STATUS.md`
- Protocol: `modsquad/PROTOCOL.md`
- Runbook: `modsquad/OPERATOR_RUNBOOK.md`

### Emergency Rollback
```bash
# If production deployment fails
git revert HEAD
git push origin main

# Render will auto-deploy previous version
# Monitor rollback: https://dashboard.render.com
```

---

## QUICK REFERENCE CARD

```
┌──────────────────────────────────────────────────────────────┐
│              META-ORCHESTRATOR CHEAT SHEET                   │
├──────────────────────────────────────────────────────────────┤
│ Resume oversight:                                            │
│   python scripts/meta_orchestrator.py --mode quick           │
│                                                              │
│ Live monitoring:                                             │
│   python scripts/meta_dashboard.py                           │
│                                                              │
│ Full validation:                                             │
│   python scripts/meta_orchestrator.py --mode full            │
│                                                              │
│ One-time status:                                             │
│   python scripts/meta_dashboard.py --once                    │
│                                                              │
│ Check logs:                                                  │
│   cat modsquad/logs/execution_log_*.jsonl                    │
│                                                              │
│ View reports:                                                │
│   cat reports/meta_orchestrator_*.txt                        │
│                                                              │
│ Target risk rate: <0.5%                                      │
│ Production ready: 0.00% risk, all checks passing             │
└──────────────────────────────────────────────────────────────┘
```

---

**READY TO EXECUTE** ✅

Next command to run:
```bash
python scripts/meta_orchestrator.py --mode quick
```

Then launch dashboard:
```bash
python scripts/meta_dashboard.py
```
