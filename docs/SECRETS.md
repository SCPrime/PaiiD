# Secret Management Guide

**Version:** 1.0
**Last Updated:** October 26, 2025
**Owner:** DevOps / Security Team

---

## Table of Contents

1. [Overview](#overview)
2. [Required Secrets](#required-secrets)
3. [Optional Secrets](#optional-secrets)
4. [Secret Generation](#secret-generation)
5. [Environment Setup](#environment-setup)
6. [Secret Rotation Policy](#secret-rotation-policy)
7. [Production Deployment](#production-deployment)
8. [Security Best Practices](#security-best-practices)
9. [Troubleshooting](#troubleshooting)

---

## Overview

PaiiD uses environment variables for all sensitive configuration including API keys, database credentials, and JWT signing secrets. This document describes:

- What secrets are required vs. optional
- How to generate cryptographically secure secrets
- Where secrets are stored in different environments
- How to rotate secrets safely
- Security best practices

**CRITICAL SECURITY RULES:**

1. **NEVER commit secrets to version control** - Use `.env` and `.env.local` files (gitignored)
2. **Use different secrets for dev/staging/prod** - Never reuse secrets across environments
3. **Rotate secrets regularly** - At minimum every 90 days, immediately if compromised
4. **Use secret managers in production** - Render environment variables, AWS Secrets Manager, etc.
5. **Audit secret access** - Monitor logs for unauthorized access attempts

---

## Required Secrets

These secrets **MUST** be configured for the application to function:

### Backend (backend/.env)

#### 1. API_TOKEN
- **Purpose:** Authenticates all backend API requests from frontend
- **Format:** URL-safe random string (32+ bytes)
- **Generate:** `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- **Example:** `rnd_bDRqi1TvLvd3rC78yvUSgDraH2Kl`
- **Security:** Must be at least 20 characters, shared between frontend and backend
- **Rotation:** Every 90 days or on suspected compromise

#### 2. TRADIER_API_KEY
- **Purpose:** Access Tradier API for market data (quotes, bars, options chains)
- **Where to Get:** https://developer.tradier.com
- **Format:** Alphanumeric string from Tradier
- **Security:** Read-only access recommended, enable IP whitelisting if available
- **Rotation:** Every 180 days or per Tradier's security policy

#### 3. TRADIER_ACCOUNT_ID
- **Purpose:** Identifies your Tradier account for API requests
- **Where to Get:** Tradier dashboard after account creation
- **Format:** Alphanumeric account identifier
- **Security:** Not secret but required for API calls

#### 4. ALPACA_PAPER_API_KEY
- **Purpose:** Authenticate with Alpaca paper trading API
- **Where to Get:** https://app.alpaca.markets/paper/dashboard/overview
- **Format:** Alphanumeric key from Alpaca
- **Security:** Paper trading only - DO NOT use live trading keys
- **Rotation:** Every 180 days

#### 5. ALPACA_PAPER_SECRET_KEY
- **Purpose:** Secret key for Alpaca paper trading API
- **Where to Get:** Alpaca paper trading dashboard (same place as API key)
- **Format:** Alphanumeric secret from Alpaca
- **Security:** NEVER expose in logs or error messages
- **Rotation:** Every 180 days, same schedule as API key

#### 6. DATABASE_URL
- **Purpose:** PostgreSQL database connection string
- **Format:** `postgresql://username:password@host:port/database`
- **Example (dev):** `postgresql://postgres:postgres@localhost:5432/paiid`
- **Example (prod):** `postgresql://user:SECURE_PASS@db.example.com:5432/paiid_prod`
- **Security:** Use strong passwords (20+ chars, mixed case, numbers, symbols)
- **Rotation:** Database password every 90 days

#### 7. JWT_SECRET_KEY
- **Purpose:** Signs and validates JWT tokens for multi-user authentication
- **Format:** URL-safe random string (32+ bytes)
- **Generate:** `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- **Security:** CRITICAL - compromise allows session hijacking
- **Rotation:** Every 90 days (WARNING: invalidates all active user sessions)
- **Note:** Auto-generated if not set (not recommended for production)

### Frontend (frontend/.env.local)

#### 1. NEXT_PUBLIC_API_TOKEN
- **Purpose:** Backend API authentication (must match backend API_TOKEN)
- **Value:** SAME as backend `API_TOKEN`
- **Security:** Exposed to browser but validated by backend

#### 2. NEXT_PUBLIC_BACKEND_API_BASE_URL
- **Purpose:** Backend API endpoint URL
- **Dev:** `http://127.0.0.1:8001`
- **Prod:** `https://paiid-backend.onrender.com`

#### 3. NEXT_PUBLIC_ANTHROPIC_API_KEY
- **Purpose:** Client-side AI features (onboarding, chat, strategy builder)
- **Where to Get:** https://console.anthropic.com/
- **Security:** Exposed to browser - use rate limits and monitoring
- **Rotation:** Every 180 days

---

## Optional Secrets

These secrets enhance functionality but are not strictly required:

### ANTHROPIC_API_KEY (Backend)
- **Purpose:** Server-side AI recommendations and analysis
- **Recommended:** Yes - enables AI-powered features
- **Where to Get:** https://console.anthropic.com/

### GITHUB_WEBHOOK_SECRET
- **Purpose:** Validates GitHub webhook signatures for repo monitoring
- **Required:** Only if using GitHub monitoring feature
- **Generate:** `python -c "import secrets; print(secrets.token_hex(32))"`

### REDIS_URL
- **Purpose:** Redis cache for improved performance
- **Format:** `redis://[[username]:[password]@]host:port[/database]`
- **Recommended:** Yes for production (reduces API calls by 60-80%)
- **Fallback:** Uses in-memory cache if not configured

### SENTRY_DSN
- **Purpose:** Error tracking and performance monitoring
- **Where to Get:** https://sentry.io/
- **Recommended:** Highly recommended for production
- **Security:** DSN is public (safe to expose)

---

## Secret Generation

### Generating Random Secrets

Use Python's `secrets` module for cryptographically secure random values:

```bash
# API_TOKEN and JWT_SECRET_KEY (32 bytes, URL-safe)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# GitHub webhook secret (32 bytes, hex)
python -c "import secrets; print(secrets.token_hex(32))"

# Custom length (64 bytes)
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

### Database Password

For strong database passwords:

```bash
# 32 character alphanumeric + symbols
python -c "import secrets; import string; chars = string.ascii_letters + string.digits + '!@#$%^&*'; print(''.join(secrets.choice(chars) for _ in range(32)))"
```

### Validation Requirements

The application validates secrets on startup:

- **API_TOKEN:** Minimum 20 characters, cannot be "change-me"
- **JWT_SECRET_KEY:** Minimum 32 characters, no placeholders like "dev-secret-key"
- **DATABASE_URL:** Must start with `postgresql://` or `sqlite://`

---

## Environment Setup

### Local Development

1. **Backend Setup:**
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env and fill in all required secrets
   ```

2. **Frontend Setup:**
   ```bash
   cd frontend
   cp .env.local.example .env.local
   # Edit .env.local and fill in required secrets
   # IMPORTANT: NEXT_PUBLIC_API_TOKEN must match backend API_TOKEN
   ```

3. **Verify Configuration:**
   ```bash
   # Backend will validate on startup
   cd backend
   python -m uvicorn app.main:app --reload
   # Check logs for "✅ All required secrets validated successfully"
   ```

### Strict Validation Mode

Enable strict secret validation to block startup if any secrets are missing:

```bash
# backend/.env
STRICT_SECRET_VALIDATION=true
```

This is automatically enabled in production (when deployed on Render).

---

## Secret Rotation Policy

### Standard Rotation Schedule

| Secret Type | Rotation Frequency | Reason |
|------------|-------------------|---------|
| API_TOKEN | Every 90 days | General security hygiene |
| JWT_SECRET_KEY | Every 90 days | Session security (invalidates sessions) |
| Database Password | Every 90 days | Database security |
| External API Keys | Every 180 days | Per provider recommendations |
| GITHUB_WEBHOOK_SECRET | Every 180 days | Webhook security |

### Emergency Rotation

Rotate immediately if:
- Secret appears in logs, error messages, or support tickets
- Employee with access leaves the company
- Suspected security breach or unauthorized access
- Service provider reports a breach
- Secret accidentally committed to version control

### Rotation Procedure

#### 1. API_TOKEN Rotation

```bash
# Generate new token
NEW_TOKEN=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# Update backend/.env
API_TOKEN=$NEW_TOKEN

# Update frontend/.env.local
NEXT_PUBLIC_API_TOKEN=$NEW_TOKEN

# Update Render environment variables (production)
# - Backend: Update API_TOKEN in Render dashboard
# - Frontend: Update NEXT_PUBLIC_API_TOKEN in Render dashboard

# Restart both services
```

#### 2. JWT_SECRET_KEY Rotation

**WARNING:** This invalidates all active user sessions!

```bash
# Schedule during maintenance window
# Generate new secret
NEW_JWT_SECRET=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# Update backend/.env
JWT_SECRET_KEY=$NEW_JWT_SECRET

# Update Render environment variable
# Restart backend (users will need to log in again)
```

#### 3. Database Password Rotation

```bash
# Connect to database
psql $DATABASE_URL

# Create new password
ALTER USER your_user WITH PASSWORD 'new_secure_password';

# Update DATABASE_URL in backend/.env
DATABASE_URL=postgresql://user:new_secure_password@host:port/database

# Update Render environment variable
# Restart backend
```

#### 4. External API Keys (Tradier, Alpaca, Anthropic)

1. Log into provider dashboard
2. Generate new API key
3. Update `.env` file
4. Update production environment variables
5. Restart services
6. Revoke old API key after verifying new one works

---

## Production Deployment

### Render Environment Variables

Secrets are stored as environment variables in Render (NOT in .env files):

1. **Backend Secrets (Render Dashboard):**
   - Go to: https://dashboard.render.com → paiid-backend → Environment
   - Add/update secrets:
     - `API_TOKEN`
     - `TRADIER_API_KEY`
     - `TRADIER_ACCOUNT_ID`
     - `ALPACA_PAPER_API_KEY`
     - `ALPACA_PAPER_SECRET_KEY`
     - `DATABASE_URL` (auto-populated by Render PostgreSQL addon)
     - `JWT_SECRET_KEY`
     - `ANTHROPIC_API_KEY` (optional)
     - `SENTRY_DSN` (optional)
     - `REDIS_URL` (optional, auto-populated by Render Redis addon)

2. **Frontend Secrets (Render Dashboard):**
   - Go to: https://dashboard.render.com → paiid-frontend → Environment
   - Add/update secrets:
     - `NEXT_PUBLIC_API_TOKEN` (must match backend API_TOKEN)
     - `NEXT_PUBLIC_BACKEND_API_BASE_URL=https://paiid-backend.onrender.com`
     - `NEXT_PUBLIC_ANTHROPIC_API_KEY`

3. **Auto-Restart:**
   - Render automatically restarts services when environment variables change
   - Monitor deployment logs for validation errors

### Secret Validation on Startup

Production deployments automatically enable strict secret validation:

```python
# Automatic in production (Render)
is_production = "render.com" in os.getenv("RENDER_EXTERNAL_URL", "")
if is_production:
    # Missing secrets will block startup
```

Check deployment logs for:
- `✅ All required secrets validated successfully` - Good!
- `🚨 SECRET VALIDATION FAILED!` - Fix missing secrets

---

## Security Best Practices

### 1. Never Commit Secrets

**Verify .gitignore:**
```bash
# These files should be gitignored:
backend/.env
frontend/.env.local
.env
*.env.production
```

**Check for accidental commits:**
```bash
# Search git history for secrets
git log --all --full-history --source -- backend/.env
git log -p | grep -i "api_token\|tradier\|alpaca"
```

**If secret was committed:**
1. Rotate the secret immediately
2. Use `git filter-branch` or BFG Repo-Cleaner to remove from history
3. Force push to remote (coordinate with team)
4. Update all deployments with new secret

### 2. Use Read-Only Keys Where Possible

- Tradier: Use read-only API key (no trading permissions)
- Database: Use limited permissions (no DROP TABLE in production)
- Alpaca: ALWAYS use paper trading keys (never live trading)

### 3. Enable 2FA on Provider Accounts

Enable two-factor authentication on:
- Tradier account
- Alpaca account
- Anthropic account
- Render dashboard
- GitHub repository
- Database hosting

### 4. Monitor Secret Usage

**Set up alerts for:**
- Failed authentication attempts (API_TOKEN, JWT)
- Unusual API usage patterns (rate limit hits)
- Database connection failures
- Secret rotation events

**Review logs regularly:**
```bash
# Check for auth failures
grep "401 UNAUTHORIZED" backend/logs/*.log

# Check for secret validation errors
grep "SECRET VALIDATION FAILED" backend/logs/*.log
```

### 5. Principle of Least Privilege

- Development: Use sandbox/test API keys with limited permissions
- Staging: Separate secrets from production
- Production: Full permissions but with monitoring and rate limits

### 6. Secret Storage

**DO:**
- ✅ Store in environment variables (Render, AWS Secrets Manager)
- ✅ Use `.env` files locally (gitignored)
- ✅ Encrypt backups containing secrets
- ✅ Use secret management tools (1Password, HashiCorp Vault)

**DON'T:**
- ❌ Hard-code secrets in source code
- ❌ Commit secrets to version control
- ❌ Share secrets via email or Slack
- ❌ Store secrets in plain text documentation
- ❌ Reuse secrets across environments

---

## Troubleshooting

### Secret Validation Failed on Startup

**Error:**
```
🚨 SECRET VALIDATION FAILED!
Missing or invalid secrets detected:
   ❌ API_TOKEN (REQUIRED)
   ❌ JWT_SECRET_KEY (REQUIRED)
```

**Solution:**
1. Check `backend/.env` exists: `ls -la backend/.env`
2. Verify all required secrets are set (non-empty)
3. Check for placeholder values like "your-key-here"
4. Generate missing secrets (see Secret Generation section)
5. Restart backend: `uvicorn app.main:app --reload`

### Frontend Can't Connect to Backend (401 Unauthorized)

**Cause:** API_TOKEN mismatch between frontend and backend

**Solution:**
```bash
# Check backend API_TOKEN
grep API_TOKEN backend/.env

# Check frontend API_TOKEN
grep NEXT_PUBLIC_API_TOKEN frontend/.env.local

# Ensure they match exactly (no extra spaces or quotes)
```

### JWT Tokens Invalid After Deployment

**Cause:** JWT_SECRET_KEY was rotated, invalidating all sessions

**Solution:**
- This is expected behavior - users must log in again
- Communicate planned rotations to users in advance
- Consider implementing a grace period (accept old + new secrets temporarily)

### Database Connection Failed

**Error:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution:**
1. Check DATABASE_URL format: `postgresql://user:password@host:port/database`
2. Verify credentials are correct
3. Check network access (firewall, IP whitelist)
4. Test connection manually: `psql $DATABASE_URL`

### Pydantic Validation Error

**Error:**
```
pydantic.ValidationError: API_TOKEN must be at least 20 characters long for security
```

**Solution:**
- Generate a longer secret: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- Minimum lengths enforced for security:
  - API_TOKEN: 20 chars
  - JWT_SECRET_KEY: 32 chars

---

## Quick Reference

### Environment File Locations

| File | Purpose | Gitignored |
|------|---------|------------|
| `backend/.env` | Backend secrets (local dev) | ✅ Yes |
| `frontend/.env.local` | Frontend secrets (local dev) | ✅ Yes |
| `backend/.env.example` | Backend template (no secrets) | ❌ No |
| `frontend/.env.local.example` | Frontend template (no secrets) | ❌ No |

### Secret Generation Quick Commands

```bash
# API_TOKEN / JWT_SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# GitHub Webhook Secret
python -c "import secrets; print(secrets.token_hex(32))"

# Database Password
python -c "import secrets; import string; chars = string.ascii_letters + string.digits + '!@#$%^&*'; print(''.join(secrets.choice(chars) for _ in range(32)))"
```

### Where to Get API Keys

| Service | URL | Free Tier |
|---------|-----|-----------|
| Tradier | https://developer.tradier.com | ✅ Yes (sandbox) |
| Alpaca | https://app.alpaca.markets/paper/dashboard/overview | ✅ Yes (paper trading) |
| Anthropic | https://console.anthropic.com/ | ❌ Pay-as-you-go |
| Sentry | https://sentry.io/ | ✅ Yes (limited) |
| Redis | https://redis.com/try-free/ | ✅ Yes (limited) |

### Support

**Security Issues:** Report to repository owner immediately
**Documentation:** See other docs in `/docs` folder
**Questions:** Open GitHub issue with label `security` (do NOT include secret values)

---

**Last Review:** October 26, 2025
**Next Review:** January 26, 2026 (90 days)
