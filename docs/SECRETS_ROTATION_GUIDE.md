# API Key Rotation Guide

**Version:** 1.0
**Last Updated:** October 27, 2025
**Owner:** Security Team / DevOps

---

## Table of Contents

1. [Overview](#overview)
2. [Rotation Schedule](#rotation-schedule)
3. [Pre-Rotation Checklist](#pre-rotation-checklist)
4. [API Key Rotation Procedures](#api-key-rotation-procedures)
   - [Tradier API Key](#tradier-api-key-rotation)
   - [Alpaca API Key](#alpaca-api-key-rotation)
   - [Anthropic API Key](#anthropic-api-key-rotation)
   - [GitHub Webhook Secret](#github-webhook-secret-rotation)
   - [JWT Secret Key](#jwt-secret-key-rotation)
   - [API_TOKEN](#api_token-rotation)
   - [Database Password](#database-password-rotation)
5. [Emergency Rotation Procedure](#emergency-rotation-procedure)
6. [Post-Rotation Validation](#post-rotation-validation)
7. [Rollback Procedures](#rollback-procedures)
8. [Incident Documentation](#incident-documentation)

---

## Overview

This guide provides step-by-step procedures for rotating all API keys and secrets used in the PaiiD application. Regular rotation is a critical security practice that:

- Limits the impact of compromised credentials
- Reduces the window of opportunity for attackers
- Maintains compliance with security best practices
- Ensures secrets are properly managed across environments

**IMPORTANT PRINCIPLES:**

1. **Always rotate in maintenance windows** - Especially for JWT secrets that invalidate sessions
2. **Test in development first** - Validate new keys work before updating production
3. **Keep old keys active briefly** - Allows for quick rollback if issues occur
4. **Document everything** - Record when, why, and who rotated secrets
5. **Validate immediately** - Test services after rotation to catch issues early

---

## Rotation Schedule

### Standard Rotation Intervals

| Secret | Rotation Frequency | Impact Level | Requires Maintenance Window |
|--------|-------------------|--------------|----------------------------|
| API_TOKEN | 90 days | Medium | No (seamless) |
| JWT_SECRET_KEY | 90 days | High | Yes (invalidates sessions) |
| Database Password | 90 days | Critical | Yes (service restart) |
| TRADIER_API_KEY | 180 days | Medium | No |
| ALPACA_PAPER_API_KEY | 180 days | Low | No |
| ALPACA_PAPER_SECRET_KEY | 180 days | Low | No |
| ANTHROPIC_API_KEY | 180 days | Low | No |
| GITHUB_WEBHOOK_SECRET | 180 days | Low | No |

### Next Rotation Dates

Track rotation dates in a secure location (e.g., password manager, internal docs):

```
Last Rotation: [Date]
Next Scheduled: [Date + interval]
Rotated By: [Name]
```

---

## Pre-Rotation Checklist

Before rotating any secret, complete this checklist:

- [ ] **Review recent logs** - Check for unusual activity or failed auth attempts
- [ ] **Backup configuration** - Save current .env files (encrypted, offline)
- [ ] **Schedule maintenance window** (if required) - Notify stakeholders
- [ ] **Test in development** - Validate rotation procedure in dev environment
- [ ] **Prepare rollback plan** - Document how to restore old secrets quickly
- [ ] **Communication ready** - Prepare notifications for users (if applicable)
- [ ] **Monitoring enabled** - Ensure alerts are active for auth failures
- [ ] **On-call available** - Have technical support ready during rotation

---

## API Key Rotation Procedures

---

### Tradier API Key Rotation

**Purpose:** Market data access (quotes, historical data, options chains)
**Impact:** Medium - Market data will fail if invalid
**Downtime:** None (if done correctly)
**Rotation Frequency:** 180 days

#### Steps:

1. **Generate New Key in Tradier Dashboard**

   ```bash
   # Navigate to Tradier Developer Portal
   https://developer.tradier.com/user/sign_in

   # Log in to your account
   # Navigate to: Settings > API Access
   # Click "Create New Application" or "Regenerate Key"

   # Save new API key securely:
   NEW_TRADIER_KEY="<your-new-key>"
   ```

2. **Test New Key Locally**

   ```bash
   # Update local environment file
   cd C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD\backend

   # Backup current .env
   cp .env .env.backup

   # Update TRADIER_API_KEY in .env
   # TRADIER_API_KEY=<new-key>

   # Test the key
   python -m uvicorn app.main:app --reload

   # In another terminal, test market data endpoint
   curl -H "Authorization: Bearer <API_TOKEN>" \
        http://127.0.0.1:8001/api/market/quote/SPY

   # Expected: Valid market data response (not 401 or 403)
   ```

3. **Verify All Tradier Features**

   ```bash
   # Test multiple endpoints to ensure key works

   # 1. Real-time quote
   curl -H "Authorization: Bearer <API_TOKEN>" \
        http://127.0.0.1:8001/api/market/quote/AAPL

   # 2. Historical data
   curl -H "Authorization: Bearer <API_TOKEN>" \
        http://127.0.0.1:8001/api/market/history/AAPL?interval=daily

   # 3. Options chain (if applicable)
   curl -H "Authorization: Bearer <API_TOKEN>" \
        http://127.0.0.1:8001/api/market/options/SPY

   # All should return 200 OK with valid data
   ```

4. **Update Production (Render)**

   ```bash
   # Navigate to Render dashboard
   https://dashboard.render.com

   # Select: paiid-backend > Environment
   # Click "Edit" on TRADIER_API_KEY
   # Paste new key value
   # Click "Save Changes"

   # Render will automatically restart the backend service
   # Monitor deployment logs for errors
   ```

5. **Validate Production**

   ```bash
   # Test production endpoint
   curl -H "Authorization: Bearer <PROD_API_TOKEN>" \
        https://paiid-backend.onrender.com/api/health/detailed

   # Expected: "tradier_status": "ok"

   # Test live market data
   curl -H "Authorization: Bearer <PROD_API_TOKEN>" \
        https://paiid-backend.onrender.com/api/market/quote/SPY

   # Expected: Valid market data
   ```

6. **Revoke Old Key**

   ```bash
   # ONLY after confirming new key works in production
   # Navigate to Tradier dashboard
   # Settings > API Access
   # Delete or disable old application/key
   ```

#### Rollback Procedure:

If new key fails:

```bash
# Render Dashboard: Edit TRADIER_API_KEY back to old value
# Or restore from .env.backup locally
cp .env.backup .env
python -m uvicorn app.main:app --reload
```

---

### Alpaca API Key Rotation

**Purpose:** Paper trading execution (orders, positions, account data)
**Impact:** Low - Only affects paper trading
**Downtime:** None
**Rotation Frequency:** 180 days

**NOTE:** Both API_KEY and SECRET_KEY must be rotated together.

#### Steps:

1. **Generate New Keys in Alpaca Dashboard**

   ```bash
   # Navigate to Alpaca Paper Trading Dashboard
   https://app.alpaca.markets/paper/dashboard/overview

   # Log in to your account
   # Navigate to: Your Apps > Paper Trading Keys
   # Click "Regenerate Keys" or "Create New Keys"

   # Save BOTH keys securely:
   NEW_ALPACA_API_KEY="<your-new-api-key>"
   NEW_ALPACA_SECRET_KEY="<your-new-secret-key>"
   ```

2. **Test New Keys Locally**

   ```bash
   # Update local environment file
   cd C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD\backend

   # Backup current .env
   cp .env .env.backup

   # Update both keys in .env
   # ALPACA_PAPER_API_KEY=<new-api-key>
   # ALPACA_PAPER_SECRET_KEY=<new-secret-key>

   # Restart backend
   python -m uvicorn app.main:app --reload

   # Test account endpoint
   curl -H "Authorization: Bearer <API_TOKEN>" \
        http://127.0.0.1:8001/api/account

   # Expected: Account balance and status
   ```

3. **Test Paper Trading**

   ```bash
   # Submit a small test order
   curl -X POST -H "Authorization: Bearer <API_TOKEN>" \
        -H "Content-Type: application/json" \
        -d '{"symbol":"SPY","qty":1,"side":"buy","type":"market"}' \
        http://127.0.0.1:8001/api/orders

   # Expected: Order confirmation (filled or pending)

   # Check positions
   curl -H "Authorization: Bearer <API_TOKEN>" \
        http://127.0.0.1:8001/api/positions

   # Expected: Position list (should include SPY if filled)

   # Cancel/close test position
   curl -X DELETE -H "Authorization: Bearer <API_TOKEN>" \
        http://127.0.0.1:8001/api/positions/SPY
   ```

4. **Update Production (Render)**

   ```bash
   # Navigate to Render dashboard
   https://dashboard.render.com

   # Select: paiid-backend > Environment
   # Update BOTH keys:
   #   1. ALPACA_PAPER_API_KEY=<new-api-key>
   #   2. ALPACA_PAPER_SECRET_KEY=<new-secret-key>
   # Click "Save Changes"

   # Monitor deployment logs
   ```

5. **Validate Production**

   ```bash
   # Test production account endpoint
   curl -H "Authorization: Bearer <PROD_API_TOKEN>" \
        https://paiid-backend.onrender.com/api/account

   # Expected: Account data

   # Test production positions
   curl -H "Authorization: Bearer <PROD_API_TOKEN>" \
        https://paiid-backend.onrender.com/api/positions

   # Expected: Position list
   ```

6. **Revoke Old Keys**

   ```bash
   # ONLY after confirming new keys work in production
   # Navigate to Alpaca dashboard
   # Your Apps > Paper Trading Keys
   # Delete old key pair
   ```

#### Rollback Procedure:

```bash
# Render Dashboard: Restore both old keys
# Or restore from .env.backup locally
cp .env.backup .env
python -m uvicorn app.main:app --reload
```

---

### Anthropic API Key Rotation

**Purpose:** AI-powered features (chat, recommendations, strategy builder)
**Impact:** Low - Only affects AI features
**Downtime:** None
**Rotation Frequency:** 180 days

**NOTE:** Must rotate in BOTH backend (server-side AI) and frontend (client-side AI).

#### Steps:

1. **Generate New Key in Anthropic Console**

   ```bash
   # Navigate to Anthropic Console
   https://console.anthropic.com/settings/keys

   # Log in to your account
   # Click "Create Key"
   # Name: "PaiiD Production - Oct 2025"
   # Copy the key (only shown once!)

   NEW_ANTHROPIC_KEY="sk-ant-api03-..."
   ```

2. **Test New Key Locally (Backend)**

   ```bash
   # Update backend/.env
   cd C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD\backend
   cp .env .env.backup

   # Update ANTHROPIC_API_KEY in .env
   # Restart backend
   python -m uvicorn app.main:app --reload

   # Test AI recommendations endpoint
   curl -H "Authorization: Bearer <API_TOKEN>" \
        http://127.0.0.1:8001/api/ai/recommendations

   # Expected: AI-generated trade recommendations
   ```

3. **Test New Key Locally (Frontend)**

   ```bash
   # Update frontend/.env.local
   cd C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD\frontend
   cp .env.local .env.local.backup

   # Update NEXT_PUBLIC_ANTHROPIC_API_KEY in .env.local
   # Restart frontend
   npm run dev

   # Open browser: http://localhost:3000
   # Test AI Chat Interface (any workflow with AI)
   # Expected: AI responses work correctly
   ```

4. **Update Production Backend (Render)**

   ```bash
   # Render dashboard
   # paiid-backend > Environment
   # Update: ANTHROPIC_API_KEY=<new-key>
   # Save changes (auto-restart)
   ```

5. **Update Production Frontend (Render)**

   ```bash
   # Render dashboard
   # paiid-frontend > Environment
   # Update: NEXT_PUBLIC_ANTHROPIC_API_KEY=<new-key>
   # Save changes (triggers rebuild and redeploy)
   ```

6. **Validate Production**

   ```bash
   # Test backend AI endpoint
   curl -H "Authorization: Bearer <PROD_API_TOKEN>" \
        https://paiid-backend.onrender.com/api/ai/recommendations

   # Expected: AI recommendations

   # Test frontend:
   # Open https://paiid-frontend.onrender.com
   # Navigate to AI Chat or Strategy Builder
   # Send test message
   # Expected: AI responds
   ```

7. **Delete Old Key**

   ```bash
   # Navigate to Anthropic Console
   # Settings > Keys
   # Find old key and click "Delete"
   ```

#### Rollback Procedure:

```bash
# Render: Restore old key in both backend and frontend
# Local: Restore from backup
cp .env.backup .env
cp .env.local.backup .env.local
```

---

### GitHub Webhook Secret Rotation

**Purpose:** Validates GitHub webhook signatures (repo monitoring)
**Impact:** Low - Only affects webhook validation
**Downtime:** None
**Rotation Frequency:** 180 days

#### Steps:

1. **Generate New Secret**

   ```bash
   # Generate cryptographically secure secret
   python -c "import secrets; print(secrets.token_hex(32))"

   # Save output
   NEW_WEBHOOK_SECRET="<generated-hex-string>"
   ```

2. **Update Backend Environment**

   ```bash
   # Local .env
   cd C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD\backend
   cp .env .env.backup

   # Update GITHUB_WEBHOOK_SECRET in .env
   python -m uvicorn app.main:app --reload
   ```

3. **Update GitHub Webhook Configuration**

   ```bash
   # Navigate to GitHub repository settings
   https://github.com/<your-org>/PaiiD/settings/hooks

   # Click on existing webhook (if any)
   # Update "Secret" field with NEW_WEBHOOK_SECRET
   # Click "Update webhook"
   ```

4. **Test Webhook Delivery**

   ```bash
   # In GitHub webhook settings, click "Recent Deliveries"
   # Click "Redeliver" on latest delivery
   # Expected: 200 OK response from backend
   ```

5. **Update Production (Render)**

   ```bash
   # Render dashboard
   # paiid-backend > Environment
   # Update: GITHUB_WEBHOOK_SECRET=<new-secret>
   # Save changes
   ```

6. **Validate Production Webhook**

   ```bash
   # Trigger a test event (e.g., push to branch)
   # Check GitHub webhook delivery status
   # Expected: 200 OK from production backend
   ```

#### Rollback Procedure:

```bash
# Update GitHub webhook secret back to old value
# Render: Restore old secret
```

---

### JWT Secret Key Rotation

**Purpose:** Signs and validates JWT authentication tokens
**Impact:** HIGH - Invalidates all active user sessions
**Downtime:** None, but users must re-login
**Rotation Frequency:** 90 days

**⚠️ WARNING:** This rotation logs out ALL users. Schedule during maintenance window and notify users.

#### Steps:

1. **Schedule Maintenance Window**

   ```bash
   # Recommended: Off-peak hours (e.g., 2 AM local time)
   # Notify users 24-48 hours in advance
   # Example notification:

   "Scheduled maintenance on [DATE] at [TIME].
   All users will be logged out and need to re-authenticate.
   Expected duration: 5 minutes.
   No data will be lost."
   ```

2. **Generate New Secret**

   ```bash
   # Generate strong secret
   python -c "import secrets; print(secrets.token_urlsafe(32))"

   # Save output securely
   NEW_JWT_SECRET="<generated-secret>"
   ```

3. **Test in Development**

   ```bash
   # Update backend/.env
   cd C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD\backend
   cp .env .env.backup

   # Update JWT_SECRET_KEY in .env
   python -m uvicorn app.main:app --reload

   # Test authentication flow
   # 1. Register new user
   curl -X POST -H "Content-Type: application/json" \
        -d '{"username":"testuser","password":"testpass123"}' \
        http://127.0.0.1:8001/api/auth/register

   # 2. Login (get JWT token)
   curl -X POST -H "Content-Type: application/json" \
        -d '{"username":"testuser","password":"testpass123"}' \
        http://127.0.0.1:8001/api/auth/login

   # Expected: JWT token returned

   # 3. Use token to access protected endpoint
   curl -H "Authorization: Bearer <jwt-token>" \
        http://127.0.0.1:8001/api/account

   # Expected: Valid response
   ```

4. **Update Production (During Maintenance Window)**

   ```bash
   # At scheduled time:
   # Render dashboard
   # paiid-backend > Environment
   # Update: JWT_SECRET_KEY=<new-secret>
   # Save changes (triggers restart)

   # Monitor logs for startup errors
   ```

5. **Validate Production**

   ```bash
   # Test authentication flow in production
   # 1. Try to access protected endpoint with old token
   curl -H "Authorization: Bearer <old-jwt-token>" \
        https://paiid-backend.onrender.com/api/account

   # Expected: 401 Unauthorized (old tokens invalid)

   # 2. Login with valid credentials
   # 3. Use new token to access endpoint
   # Expected: 200 OK
   ```

6. **Post-Rotation Communication**

   ```bash
   # Send follow-up notification:

   "Maintenance complete. If you're seeing authentication errors,
   please refresh your browser and log in again. Thank you!"
   ```

#### Rollback Procedure:

**⚠️ IMPORTANT:** Rollback also invalidates all tokens issued with new secret.

```bash
# Render: Restore old JWT_SECRET_KEY
# Notify users that sessions from last [X] minutes are invalid
# Users who logged in during new secret window must re-login
```

---

### API_TOKEN Rotation

**Purpose:** Authenticates frontend-to-backend API requests
**Impact:** Medium - Frontend can't access backend if mismatched
**Downtime:** Brief (during frontend rebuild)
**Rotation Frequency:** 90 days

#### Steps:

1. **Generate New Token**

   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"

   NEW_API_TOKEN="<generated-token>"
   ```

2. **Update Backend First**

   ```bash
   # Local backend/.env
   cd C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD\backend
   cp .env .env.backup

   # Update API_TOKEN in .env
   python -m uvicorn app.main:app --reload
   ```

3. **Update Frontend**

   ```bash
   # Local frontend/.env.local
   cd C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD\frontend
   cp .env.local .env.local.backup

   # Update NEXT_PUBLIC_API_TOKEN in .env.local
   # MUST match backend API_TOKEN exactly
   npm run dev

   # Test in browser: http://localhost:3000
   # Expected: Dashboard loads, data displays correctly
   ```

4. **Update Production Backend (Render)**

   ```bash
   # Render dashboard
   # paiid-backend > Environment
   # Update: API_TOKEN=<new-token>
   # Save changes
   ```

5. **Update Production Frontend (Render)**

   ```bash
   # Render dashboard
   # paiid-frontend > Environment
   # Update: NEXT_PUBLIC_API_TOKEN=<new-token>
   # Save changes (triggers rebuild - 2-5 min)

   # Monitor build logs for errors
   ```

6. **Validate Production**

   ```bash
   # Test health endpoint
   curl -H "Authorization: Bearer <new-token>" \
        https://paiid-backend.onrender.com/api/health

   # Expected: 200 OK

   # Open frontend in browser
   # https://paiid-frontend.onrender.com
   # Expected: Dashboard loads, all data displays
   ```

#### Rollback Procedure:

```bash
# Render: Restore old API_TOKEN in BOTH backend and frontend
# Ensure they match exactly
```

---

### Database Password Rotation

**Purpose:** Secures PostgreSQL database access
**Impact:** CRITICAL - Backend cannot function without database
**Downtime:** Yes (brief service restart)
**Rotation Frequency:** 90 days

**⚠️ WARNING:** Schedule during maintenance window. Requires service restart.

#### Steps:

1. **Connect to Database**

   ```bash
   # Get current DATABASE_URL from .env
   cd C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD\backend
   cat .env | grep DATABASE_URL

   # Connect via psql (if available locally)
   psql <database-url>

   # Or use Render dashboard database shell
   ```

2. **Generate New Password**

   ```bash
   # Generate strong password
   python -c "import secrets; import string; chars = string.ascii_letters + string.digits + '!@#$%^&*'; print(''.join(secrets.choice(chars) for _ in range(32)))"

   NEW_DB_PASSWORD="<generated-password>"
   ```

3. **Update Database User Password**

   ```sql
   -- In psql or database shell
   ALTER USER <your-db-user> WITH PASSWORD '<new-password>';

   -- Verify change
   \du

   -- Expected: Password last changed timestamp updated
   ```

4. **Update DATABASE_URL**

   ```bash
   # Format: postgresql://username:password@host:port/database

   # Old: postgresql://user:old_password@host:5432/paiid
   # New: postgresql://user:NEW_PASSWORD@host:5432/paiid

   # Update local .env
   cd C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD\backend
   cp .env .env.backup

   # Edit DATABASE_URL with new password
   ```

5. **Test Connection Locally**

   ```bash
   # Restart backend
   python -m uvicorn app.main:app --reload

   # Check logs for database connection errors
   # Expected: "Database connection successful"

   # Test endpoint that queries database
   curl -H "Authorization: Bearer <API_TOKEN>" \
        http://127.0.0.1:8001/api/positions

   # Expected: Data returned (not connection error)
   ```

6. **Update Production (Render)**

   ```bash
   # Render dashboard
   # paiid-backend > Environment
   # Update: DATABASE_URL=postgresql://user:NEW_PASSWORD@host:5432/paiid
   # Save changes (triggers restart)

   # Monitor deployment logs carefully
   # Look for: "Database connection successful"
   ```

7. **Validate Production**

   ```bash
   # Test health endpoint with database check
   curl -H "Authorization: Bearer <PROD_API_TOKEN>" \
        https://paiid-backend.onrender.com/api/health/detailed

   # Expected: "database_status": "ok"

   # Test data endpoint
   curl -H "Authorization: Bearer <PROD_API_TOKEN>" \
        https://paiid-backend.onrender.com/api/positions

   # Expected: Position data
   ```

#### Rollback Procedure:

**⚠️ CRITICAL:** Keep old password active briefly to allow rollback.

```bash
# If new password fails:
# 1. Connect to database
# 2. Restore old password: ALTER USER <user> WITH PASSWORD '<old-password>';
# 3. Render: Restore old DATABASE_URL
# 4. Verify connection works
```

---

## Emergency Rotation Procedure

Use this procedure when immediate rotation is required (e.g., secret exposed in logs, employee departure, suspected breach).

### Emergency Checklist:

- [ ] **Identify scope** - Which secret(s) were compromised?
- [ ] **Revoke immediately** - Disable old secret in provider dashboard
- [ ] **Generate new secret** - Use cryptographically secure method
- [ ] **Update all environments** - Dev, staging, production
- [ ] **Validate services** - Test all affected functionality
- [ ] **Review logs** - Check for unauthorized access using old secret
- [ ] **Document incident** - Record what happened, when, and actions taken
- [ ] **Post-mortem** - Identify how secret was exposed, prevent recurrence

### Quick Rotation Commands:

```bash
# Generate new secrets quickly
python -c "import secrets; print('API_TOKEN:', secrets.token_urlsafe(32))"
python -c "import secrets; print('JWT_SECRET:', secrets.token_urlsafe(32))"
python -c "import secrets; print('WEBHOOK_SECRET:', secrets.token_hex(32))"
```

### Emergency Update Script:

```bash
#!/bin/bash
# emergency_rotation.sh - Update multiple secrets at once

# Usage: ./emergency_rotation.sh <secret-name> <new-value>

SECRET_NAME=$1
NEW_VALUE=$2

echo "🚨 EMERGENCY ROTATION: $SECRET_NAME"

# Update local .env
cd backend
cp .env .env.emergency-backup-$(date +%Y%m%d-%H%M%S)
sed -i "s|^$SECRET_NAME=.*|$SECRET_NAME=$NEW_VALUE|" .env

echo "✅ Updated backend/.env"

# For frontend secrets (NEXT_PUBLIC_*)
if [[ $SECRET_NAME == NEXT_PUBLIC_* ]]; then
  cd ../frontend
  cp .env.local .env.local.emergency-backup-$(date +%Y%m%d-%H%M%S)
  sed -i "s|^$SECRET_NAME=.*|$SECRET_NAME=$NEW_VALUE|" .env.local
  echo "✅ Updated frontend/.env.local"
fi

echo ""
echo "Next steps:"
echo "1. Update Render environment variables"
echo "2. Restart services"
echo "3. Validate functionality"
echo "4. Revoke old secret in provider dashboard"
```

---

## Post-Rotation Validation

After ANY secret rotation, complete this validation checklist:

### Backend Validation:

```bash
# 1. Health check
curl -H "Authorization: Bearer <API_TOKEN>" \
     https://paiid-backend.onrender.com/api/health/detailed

# Expected: All services "ok"

# 2. Market data (Tradier)
curl -H "Authorization: Bearer <API_TOKEN>" \
     https://paiid-backend.onrender.com/api/market/quote/SPY

# Expected: Valid market data

# 3. Account data (Alpaca)
curl -H "Authorization: Bearer <API_TOKEN>" \
     https://paiid-backend.onrender.com/api/account

# Expected: Account balance

# 4. AI recommendations (Anthropic)
curl -H "Authorization: Bearer <API_TOKEN>" \
     https://paiid-backend.onrender.com/api/ai/recommendations

# Expected: AI-generated recommendations

# 5. Database query
curl -H "Authorization: Bearer <API_TOKEN>" \
     https://paiid-backend.onrender.com/api/positions

# Expected: Position data
```

### Frontend Validation:

```bash
# Open in browser: https://paiid-frontend.onrender.com

# Test:
# 1. Dashboard loads without errors
# 2. Market data displays (SPY, QQQ in center logo)
# 3. Active Positions workflow shows data
# 4. AI Chat responds to messages
# 5. Execute Trade form submits successfully (paper trade)
# 6. Settings page loads user preferences
```

### Log Review:

```bash
# Check backend logs for errors
# Render dashboard > paiid-backend > Logs

# Look for:
# ❌ Authentication failures
# ❌ API connection errors
# ❌ Database connection errors
# ✅ Successful API calls
# ✅ "Health check: OK"
```

---

## Rollback Procedures

If rotation causes issues, use these procedures to quickly restore service.

### General Rollback Steps:

1. **Identify the problem** - What's broken? Which secret?
2. **Check backups** - Locate .env.backup files
3. **Restore old secret** - Update environment variables
4. **Restart services** - Render auto-restarts on env var change
5. **Validate** - Confirm service restored
6. **Investigate** - Why did new secret fail?
7. **Retry rotation** - Fix issue and rotate again

### Render Quick Rollback:

```bash
# Render dashboard keeps history of environment variable changes
# paiid-backend (or frontend) > Environment > Activity
# Click "View History"
# Click "Restore" on previous version
# Service automatically restarts with old values
```

### Local Rollback:

```bash
# Backend
cd C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD\backend
cp .env.backup .env
python -m uvicorn app.main:app --reload

# Frontend
cd C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD\frontend
cp .env.local.backup .env.local
npm run dev
```

### Database Rollback:

```sql
-- Connect to database
psql <database-url>

-- Restore old password
ALTER USER <your-db-user> WITH PASSWORD '<old-password>';

-- Update DATABASE_URL with old password
-- Restart backend
```

---

## Incident Documentation

After emergency rotation or if secrets were compromised, document the incident:

### Incident Report Template:

```markdown
# Security Incident Report - Secret Exposure

**Incident ID:** SEC-<YYYYMMDD>-<NN>
**Date:** <Date and time>
**Reporter:** <Name>
**Severity:** Critical / High / Medium / Low

## Summary
Brief description of what happened.

## Affected Secrets
- [ ] API_TOKEN
- [ ] JWT_SECRET_KEY
- [ ] TRADIER_API_KEY
- [ ] ALPACA_PAPER_API_KEY
- [ ] ANTHROPIC_API_KEY
- [ ] DATABASE_URL
- [ ] Other: _________

## Timeline
- **YYYY-MM-DD HH:MM** - Secret potentially exposed
- **YYYY-MM-DD HH:MM** - Exposure discovered
- **YYYY-MM-DD HH:MM** - Old secret revoked
- **YYYY-MM-DD HH:MM** - New secret generated and deployed
- **YYYY-MM-DD HH:MM** - Services validated

## Root Cause
How was the secret exposed?
- [ ] Committed to version control
- [ ] Exposed in logs
- [ ] Shared via insecure channel
- [ ] Employee departure
- [ ] Third-party breach
- [ ] Other: _________

## Actions Taken
1. Revoked old secret
2. Generated new secret
3. Updated all environments (dev, staging, prod)
4. Validated all services
5. Reviewed logs for unauthorized access
6. Notified stakeholders (if required)

## Evidence of Compromise
- [ ] No evidence of unauthorized access
- [ ] Suspicious activity detected (describe below)
- [ ] Unknown

Details: _________

## Preventive Measures
What will prevent this from happening again?
1.
2.
3.

## Follow-Up Actions
- [ ] Implement additional monitoring
- [ ] Update documentation
- [ ] Team training/awareness
- [ ] Process improvements

## Reviewed By
- Name: _________
- Title: _________
- Date: _________
```

### Where to Store Incident Reports:

- **Internal wiki/docs** (NOT in public repository)
- **Secure password manager notes**
- **Compliance/audit system** (if required)

---

## Additional Resources

- **Main Secrets Guide:** `docs/SECRETS.md`
- **Environment Setup:** `backend/.env.example`, `frontend/.env.local.example`
- **Secrets Validation Script:** `backend/scripts/validate_secrets.py`
- **Pre-commit Secrets Scanning:** `.secrets.baseline`

### Support Contacts:

- **Security Issues:** [Repository owner]
- **Render Support:** https://render.com/docs
- **Tradier API Support:** https://developer.tradier.com/support
- **Alpaca API Support:** https://alpaca.markets/support
- **Anthropic Support:** https://console.anthropic.com/support

---

**Last Review:** October 27, 2025
**Next Review:** January 27, 2026 (90 days)
**Document Owner:** Security Team
