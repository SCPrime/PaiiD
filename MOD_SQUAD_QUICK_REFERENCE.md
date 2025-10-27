# MOD SQUAD Quick Reference Card
**Print this and keep it handy!**

---

## 🔍 GITHUB MOD

### Quick Health Check
```bash
python scripts/auto_github_monitor.py
```

### API Endpoint
```bash
curl https://paiid-backend.onrender.com/api/monitor/health
```

### Dashboard
```
https://paiid-frontend.onrender.com/monitor
```

**What it tracks:**
- ✅ Commits, pushes, deployments
- ✅ Issues opened/closed
- ✅ PRs opened/merged
- ✅ Build failures
- ✅ Test failures

---

## 🌐 BROWSER MOD

### Quick Render Check (30 sec)
```bash
# Production
python scripts/browser_mod.py --check-render

# Localhost
python scripts/browser_mod.py --dev --check-render
```

### Full Audit (5 min)
```bash
# Production
python scripts/browser_mod.py --full-audit

# Localhost
python scripts/browser_mod.py --dev --full-audit
```

### PowerShell (Windows)
```powershell
# Quick check
.\scripts\browser_mod.ps1 -QuickCheck

# Full audit
.\scripts\browser_mod.ps1 -FullAudit

# Localhost
.\scripts\browser_mod.ps1 -Dev -FullAudit
```

**What it checks:**
- ✅ Page renders successfully
- ✅ Console errors
- ✅ Network failures
- ✅ All 10 workflows accessible
- ✅ Performance (load time, FCP)
- ✅ Accessibility
- ✅ Responsive design

---

## MOD SQUAD Checkpoints

### ✅ BEFORE Code Changes
```bash
python scripts/auto_github_monitor.py
```

### ✅ BEFORE Commit
```bash
python scripts/browser_mod.py --dev --check-render
```

### ✅ AFTER Commit
```bash
python scripts/auto_github_monitor.py
```

### ✅ AFTER Deployment
```bash
python scripts/browser_mod.py --full-audit
```

---

## Exit Codes

**0** = Success (no critical issues)
**1** = Failure (critical issues found)

---

## Reports Location

**GITHUB MOD:**
- `monitor-data.json`
- Dashboard: `/monitor` page

**BROWSER MOD:**
- `browser-mod-report-YYYYMMDD-HHMMSS.json`
- `screenshots/` directory

---

## Issue Severity

**CRITICAL** = Blocks deployment (HTTP errors, render failure)
**HIGH** = Major UX issue (console errors, broken workflows)
**MEDIUM** = Minor UX issue (responsive, performance)
**LOW** = Nice-to-have (accessibility, warnings)

---

## Emergency Commands

### Check if site is up
```bash
curl -I https://paiid-frontend.onrender.com
```

### Check backend health
```bash
curl https://paiid-backend.onrender.com/api/health
```

### Quick browser test
```bash
python scripts/browser_mod.py --check-render
```

---

## Support

**Documentation:**
- Full guide: `MOD_SQUAD_MONITORING.md`
- GITHUB MOD: `MONITOR_COMPLETE_GUIDE.md`
- BROWSER MOD: `scripts/browser_mod.py --help`

**Troubleshooting:**
1. Check dependencies installed
2. Verify Python 3.8+
3. Check network connectivity
4. Review error messages

---

**Last Updated:** 2025-10-27
**Version:** 1.0
**Status:** Production-Ready ✅
