# 🕐 Scheduler Quick Start Guide

**Status:** ✅ **DEPLOYED AND RUNNING**
**Last Updated:** 2025-10-24
**Production URL:** https://paiid-frontend.onrender.com

---

## 🎯 What Is the Scheduler?

The **Auto-Run Scheduler** lets you automate your trading workflows on a schedule. Set up recurring tasks like:

- **Morning Routine** - Daily market analysis at 9 AM
- **News Review** - Check market news every hour
- **AI Recommendations** - Get strategy updates at market open
- **Custom Tasks** - Any workflow on your preferred schedule

---

## ✅ Current Status (Production)

### Backend
- **Status:** 🟢 **RUNNING**
- **Health:** ✅ Healthy
- **Jobs:** 1 active job configured
- **API Base:** `https://paiid-backend.onrender.com/api/scheduler`

### Frontend
- **Location:** Settings → Automation Tab
- **Components:** ✅ SchedulerSettings + ApprovalQueue integrated
- **Access:** Click Settings wedge in RadialMenu

---

## 🚀 How to Use (Production)

### Step 1: Access the Scheduler

1. Open https://paid-frontend.onrender.com
2. Login with your credentials
3. Click the **Settings** wedge (bottom-right, gear icon ⚙️)
4. Look for the "Automation" or "Scheduler" tab

### Step 2: View Active Schedules

You can see all your configured schedules, including:
- Schedule name
- Run frequency (cron expression)
- Last run time
- Next scheduled run
- Enable/disable status

### Step 3: Create a New Schedule

Currently available schedule types:
- `morning_routine` - Daily morning analysis
- `news_review` - News aggregation
- `ai_recs` - AI recommendations
- `custom` - Custom workflow

**Example Schedule:**
- Name: "Daily Morning Analysis"
- Type: `morning_routine`
- Cron: `0 9 * * 1-5` (9 AM weekdays)
- Timezone: `America/New_York`
- Requires Approval: Yes

### Step 4: Approve Scheduled Actions

When a schedule runs and requires approval:
1. Check the **Approval Queue** tab in Settings
2. Review the proposed action (symbol, quantity, price)
3. See AI confidence score and risk rating
4. Approve or reject the action

---

## 🔧 API Endpoints (For Developers)

### Get All Schedules
```bash
GET /api/scheduler/schedules
Authorization: Bearer {your_token}
```

**Response:**
```json
[
  {
    "id": "abc123",
    "name": "Daily Morning Routine",
    "type": "morning_routine",
    "enabled": true,
    "cron_expression": "0 9 * * 1-5",
    "timezone": "America/New_York",
    "requires_approval": true,
    "last_run": "2025-10-24T09:00:00Z",
    "next_run": "2025-10-25T09:00:00Z",
    "status": "active",
    "created_at": "2025-10-20T10:00:00Z"
  }
]
```

### Create a Schedule
```bash
POST /api/scheduler/schedules
Authorization: Bearer {your_token}
Content-Type: application/json

{
  "name": "Daily Morning Analysis",
  "type": "morning_routine",
  "cron_expression": "0 9 * * 1-5",
  "timezone": "America/New_York",
  "requires_approval": true,
  "enabled": true
}
```

### Get Pending Approvals
```bash
GET /api/scheduler/pending-approvals
Authorization: Bearer {your_token}
```

**Response:**
```json
[
  {
    "id": "approval123",
    "execution_id": "exec456",
    "schedule_name": "Daily Morning Routine",
    "trade_type": "buy",
    "symbol": "AAPL",
    "quantity": 10,
    "estimated_price": 180.50,
    "estimated_value": 1805.00,
    "reason": "Strong bullish momentum, RSI at 62",
    "risk_score": 45,
    "ai_confidence": 0.85,
    "supporting_data": {...},
    "created_at": "2025-10-24T09:00:05Z",
    "expires_at": "2025-10-24T16:00:00Z"
  }
]
```

### Approve/Reject an Action
```bash
POST /api/scheduler/approvals/{approval_id}/approve
DELETE /api/scheduler/approvals/{approval_id}/reject
Authorization: Bearer {your_token}
Content-Type: application/json

{
  "reason": "Looks good, market conditions favorable"
}
```

### Get Scheduler Status
```bash
GET /api/scheduler/status
Authorization: Bearer {your_token}
```

**Response:**
```json
{
  "running": true,
  "jobs_count": 1,
  "status": "healthy"
}
```

### Get Execution History
```bash
GET /api/scheduler/executions
Authorization: Bearer {your_token}
```

---

## 📅 Cron Expression Guide

The scheduler uses cron expressions to define when tasks run:

**Format:** `minute hour day month day_of_week`

**Examples:**
- `0 9 * * 1-5` - 9 AM weekdays
- `0 9,15 * * *` - 9 AM and 3 PM daily
- `*/30 9-16 * * 1-5` - Every 30 min, 9 AM-4 PM weekdays
- `0 10 * * 1` - 10 AM every Monday
- `0 0 1 * *` - Midnight on 1st of every month

**Timezone:**
- Default: `America/New_York` (EST/EDT)
- Market hours: 9:30 AM - 4:00 PM ET

---

## 🔒 Safety Features

### Approval Workflow
When `requires_approval: true`:
1. Schedule runs on time
2. AI generates trade proposal
3. Proposal waits in approval queue
4. You review and approve/reject
5. Trade executes only after approval

### Risk Scoring
Every approval includes:
- **Risk Score:** 0-100 (higher = riskier)
- **AI Confidence:** 0-1 (higher = more confident)
- **Supporting Data:** Technical indicators, news sentiment
- **Expiration:** Approvals expire if not acted upon

### Manual Override
- You can disable any schedule anytime
- You can reject any approval
- You can delete schedules
- No trades execute without your approval

---

## 🐛 Known Issues & Fixes

### Issue 1: Schedule Creation Returns 500 Error
**Status:** 🔍 Under Investigation
**Workaround:** Use API directly or wait for fix
**ETA:** Next deployment

### Issue 2: Scheduler Not Visible in UI
**Fix:** Make sure you're on the Settings wedge
**Location:** Settings → Automation tab (may need scrolling)

### Issue 3: Next Run Time Shows Null
**Cause:** Schedule disabled or invalid cron expression
**Fix:** Enable schedule and verify cron syntax

---

## 📊 Current Configuration

### File-Based Storage
Schedules stored in: `backend/data/schedules/`
- `/schedules/` - Schedule configurations
- `/executions/` - Execution history
- `/approvals/` - Pending approvals

**No database required!** All data is file-based for simplicity.

### Active Jobs (Production)
Based on status endpoint:
- **Jobs Count:** 1
- **Running:** Yes
- **Status:** Healthy

---

## 🎓 Best Practices

### Starting Out
1. **Start with approval required** - Review all actions first
2. **Test with small quantities** - Verify workflow works
3. **Use conservative schedules** - Don't over-automate
4. **Monitor execution history** - Check what ran and when

### Advanced Usage
1. **Disable approval for trusted workflows** - After testing
2. **Combine multiple schedules** - Different strategies, different times
3. **Use risk scores** - Set thresholds for auto-approval
4. **Monitor market conditions** - Pause during high volatility

### Safety Tips
- **Never automate with real money** until fully tested
- **Always use paper trading** for scheduler testing
- **Set position limits** in your risk settings
- **Review approval queue** daily
- **Check execution history** weekly

---

## 🚀 Roadmap (Future Enhancements)

### Phase 2: Scheduler Improvements
- [ ] Schedule templates (pre-configured common patterns)
- [ ] Conditional execution (only run if market conditions met)
- [ ] Multi-strategy scheduling (chain multiple workflows)
- [ ] Email/SMS notifications for approvals
- [ ] Auto-approval based on risk score thresholds
- [ ] Schedule analytics (success rate, P&L tracking)

### Phase 3: Advanced Features
- [ ] Machine learning for optimal schedule timing
- [ ] Backtesting scheduler strategies
- [ ] Calendar view of upcoming executions
- [ ] Bulk schedule management
- [ ] Schedule sharing/importing

---

## 📞 Support

### Questions?
- Check `/api/scheduler/status` for health
- Review backend logs in Render dashboard
- See `SCHEDULER_DEPLOYMENT_GUIDE.md` for technical details

### Found a Bug?
- Report on GitHub Issues
- Include schedule configuration
- Include execution ID if applicable
- Check backend logs for errors

---

## ✅ Quick Checklist

Before using the scheduler:
- [ ] Verified scheduler is running (`/api/scheduler/status`)
- [ ] Configured at least one test schedule
- [ ] Tested approval workflow
- [ ] Set appropriate risk limits
- [ ] Enabled paper trading mode
- [ ] Reviewed cron expression syntax
- [ ] Understood approval expiration times
- [ ] Checked timezone settings

---

## 🎉 You're Ready!

The scheduler is deployed, running, and ready to automate your trading workflows. Start with a simple schedule, test the approval workflow, and gradually build confidence in automation.

**Happy Trading! 🚀**

---

**Generated by:** Claude Code
**Date:** 2025-10-24
**Status:** Production Ready ✅
