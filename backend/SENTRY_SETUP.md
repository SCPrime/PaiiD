# Sentry Error Tracking Setup Guide

## Overview

Sentry provides production error monitoring, performance tracking, and debugging context. The backend is configured to work with or without Sentry (graceful fallback).

## Setup Steps

### 1. Create Sentry Account (Free Tier)

1. Go to https://sentry.io/signup/
2. Create account (free for 5,000 errors/month + 10,000 performance units)
3. Choose **"Create Project"**

### 2. Configure Sentry Project

1. **Platform**: Select **Python**
2. **Alert Frequency**: Choose **"On every new issue"** (or customize)
3. **Project Name**: `paiid-backend`
4. **Team**: Default team (or create new)
5. Click **"Create Project"**

### 3. Get DSN (Data Source Name)

1. After project creation, you'll see the DSN immediately
2. Format: `https://[key]@o[org-id].ingest.sentry.io/[project-id]`
3. Or find it later: **Settings** → **Projects** → **paiid-backend** → **Client Keys (DSN)**

### 4. Add SENTRY_DSN to Environment

**Local Development** (`backend/.env`):
```bash
# ========================================
# SENTRY ERROR TRACKING (Phase 2.5)
# ========================================
SENTRY_DSN=https://your_key@o1234567.ingest.sentry.io/9876543
```

**Production (Render)**:
1. Go to Render Dashboard → Backend Service
2. **Environment** → **Add Environment Variable**
3. Key: `SENTRY_DSN`
4. Value: Your DSN from Sentry
5. **Save Changes** (triggers redeploy)

### 5. Restart Backend

```bash
# Local
cd backend
python -m uvicorn app.main:app --reload --port 8001
```

Expected startup log:
```
[OK] Sentry error tracking initialized
```

If SENTRY_DSN not set:
```
[WARNING] SENTRY_DSN not configured - error tracking disabled
```

## Verification

### Test Sentry Integration

1. **Trigger test error**:
   ```bash
   curl http://localhost:8001/api/health/sentry-test
   ```

   - If `SENTRY_DSN` is **missing**, the endpoint returns **503** with:
     ```json
     {
       "detail": "Sentry DSN is not configured. Set SENTRY_DSN before running the test."
     }
     ```

   - When `SENTRY_DSN` is configured, the endpoint raises a controlled error captured by Sentry and FastAPI returns **500** with:
     ```json
     {
       "detail": "This is a test error to verify Sentry integration is working"
     }
     ```

2. **Check Sentry Dashboard**:
   - Go to https://sentry.io/organizations/your-org/issues/
   - You should see a new error: **"HTTPException: This is a test error..."**
   - Click on it to see full context

3. **Verify Error Details**:
   - **Request context**: Method, URL, query params
   - **Environment**: development or production
   - **Breadcrumbs**: Request → Response flow
   - **Stack trace**: Full Python traceback

### Trigger Real Error (Optional)

```bash
# This will cause a real error (invalid symbol)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8001/api/market/quote/INVALID_SYMBOL_12345
```

Check Sentry for the captured error with full context.

## Sentry Dashboard Features

### Issues Tab

**What it shows**: All errors grouped by type

**Key metrics**:
- Error frequency
- Affected users (if user context added)
- First/Last seen timestamps
- Environment (production vs development)

**Actions**:
- **Resolve**: Mark error as fixed
- **Ignore**: Suppress known/acceptable errors
- **Assign**: Assign to team member
- **Merge**: Combine duplicate issues

### Performance Tab

**What it shows**: Endpoint performance metrics

**Key metrics**:
- Transactions per minute (TPM)
- P50/P75/P95/P99 latencies
- Slow endpoints
- Apdex score (user satisfaction)

**Filter by**:
- Endpoint (e.g., `/api/positions`)
- Environment
- Time range

### Releases Tab

**What it shows**: Error rates per deployment

**Setup**:
```python
# Already configured in main.py
release=f"paiid-backend@1.0.0"
```

Update version in `main.py` for each release to track regressions.

## Custom Context Functions

The middleware provides helper functions for adding custom context:

### Trading Events

```python
from app.middleware.sentry import capture_trading_event

# In your trading code
capture_trading_event(
    event_type="order_placed",
    symbol="AAPL",
    side="buy",
    quantity=10,
    order_type="market"
)
```

### Market Data Fetches

```python
from app.middleware.sentry import capture_market_data_fetch

# In market data routes
capture_market_data_fetch(
    source="tradier",
    endpoint="/markets/quotes",
    success=True,
    duration_ms=245.3
)
```

### Cache Operations

```python
from app.middleware.sentry import capture_cache_operation

# In cache service
capture_cache_operation(
    operation="get",
    key="market:indices",
    hit=True
)
```

These breadcrumbs appear in error reports, showing the sequence of events leading to an error.

## Alerts Configuration

### Set Up Alerts

1. **Project Settings** → **Alerts** → **Create Alert Rule**
2. **Alert Conditions**:
   - **When**: An event is seen
   - **If**: None (all errors)
   - **Then**: Send a notification

3. **Actions**:
   - **Email**: Your email (default fallback)
   - **Slack** (optional): Connect Slack workspace
   - **Webhook** (optional): For custom integrations (see routing matrix below)

## Alert Routing & Escalation

| Severity | Trigger | Primary Channel | Secondary Channel | Escalation Window |
|----------|---------|-----------------|-------------------|-------------------|
| Critical | `level:error` or `level:fatal` in production | Slack `#paiid-alerts` | On-call SMS via PagerDuty | 15 minutes |
| High | >10 errors in 5 minutes OR transaction.duration > 2s | Email `trading-ops@paiid.ai` | Slack `#paiid-alerts` | 60 minutes |
| Medium | Performance regression (Apdex < 0.8) | Email digest (daily) | - | Review in weekly ops sync |

### Escalation Flow

1. **Alert fires** → Sentry notifies the primary channel above.
2. **On-call acknowledgement**:
   - Critical: On-call engineer acknowledges in PagerDuty within 15 minutes.
   - High: Trading Ops acknowledges via Slack thread within 1 hour.
3. **Triage owner** documents root cause in the incident tracker.
4. **If no acknowledgement** within the escalation window, Sentry routes to the secondary channel and the engineering manager is pinged via email.
5. **Resolution**: Once fixed, mark the issue as resolved in Sentry and post-mortem summary in `#paiid-alerts`.

> **Tip:** Add multiple email recipients in Sentry alert actions to mirror the table above if Slack or PagerDuty are unavailable.

### Recommended Alert Rules

1. **Critical Errors**: Alert immediately
   - Condition: `level:error` OR `level:fatal`
   - Action: Email + Slack

2. **High Error Rate**: Alert on spikes
   - Condition: `>10 errors in 5 minutes`
   - Action: Email

3. **Slow Endpoints**: Alert on performance degradation
   - Condition: `transaction.duration:>2s`
   - Action: Email

## Privacy & Security

### PII Redaction

The backend automatically redacts sensitive data:

```python
# Authorization headers are redacted
before_send=lambda event, hint: event if not event.get("request", {}).get("headers", {}).get("Authorization") else {**event, "request": {**event.get("request", {}), "headers": {**event.get("request", {}).get("headers", {}), "Authorization": "[REDACTED]"}}}
```

### Disable PII Sending

```python
# Already configured in main.py
send_default_pii=False
```

This prevents:
- User IDs
- Email addresses
- IP addresses (unless explicitly added)
- Request body data

### GDPR Compliance

Sentry is GDPR compliant. Configure data retention:

1. **Settings** → **Data Management** → **Server-Side Scrubbing**
2. Add sensitive field patterns to scrub
3. Set **Data Retention** period (default: 90 days)

## Performance Monitoring

### Transaction Sampling

```python
# Currently set to 10% (cost-efficient)
traces_sample_rate=0.1
```

**Adjust based on needs**:
- **Development**: 1.0 (100% - see everything)
- **Staging**: 0.5 (50% - good coverage)
- **Production**: 0.1 (10% - cost-effective)

### Profile Sampling

```python
# Currently set to 10%
profiles_sample_rate=0.1
```

Profiles show code-level performance (which functions are slow).

## Troubleshooting

### "Sentry DSN invalid"

**Cause**: Malformed DSN string

**Fix**:
1. Copy DSN directly from Sentry dashboard
2. Ensure no extra spaces or quotes
3. Format: `https://key@org.ingest.sentry.io/project`

### Errors not appearing in Sentry

**Possible causes**:
1. SENTRY_DSN not set → Check startup logs
2. Network blocked → Check firewall/proxy settings
3. Sampling rate too low → Increase `traces_sample_rate`
4. Error already happened before Sentry init → Restart backend

**Debug**:
```python
# Add to route to test
import sentry_sdk
sentry_sdk.capture_message("Test message", level="info")
```

### Too many events (quota exceeded)

**Cause**: Exceeded free tier limit (5,000 errors/month)

**Solutions**:
1. **Ignore** noisy errors (e.g., 404s)
2. **Rate limiting** in Sentry project settings
3. **Upgrade plan** (Team plan: $26/month for 50,000 errors)

### High costs from performance monitoring

**Cause**: Too many transactions sampled

**Fix**: Reduce sampling rate
```python
traces_sample_rate=0.05  # 5% instead of 10%
```

## Free Tier Limits

| Feature | Free Tier |
|---------|-----------|
| Errors | 5,000/month |
| Performance | 10,000 transactions/month |
| Attachments | 1GB/month |
| Data Retention | 30 days |
| Team Members | Unlimited |
| Projects | Unlimited |

## Next Phase

Once Sentry is working, proceed with:
- **Task 4**: Critical Backend Tests

---

**Questions?** Check Sentry docs: https://docs.sentry.io/platforms/python/guides/fastapi/
