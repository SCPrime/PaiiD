# Security Policy

## 🔐 API Key Management

**CRITICAL**: This project uses sensitive API keys for trading and AI services. **NEVER commit API keys to version control.**

### Required API Keys

1. **Anthropic Claude API** - AI chat and recommendations
   - Get key at: https://console.anthropic.com/settings/keys
   - Environment variable: `ANTHROPIC_API_KEY`

2. **Alpaca Trading API** - Paper trading (or live if configured)
   - Get key at: https://app.alpaca.markets/
   - Environment variables: `APCA_API_KEY_ID`, `APCA_API_SECRET_KEY`

3. **Tradier API** (alternative broker)
   - Get key at: https://www.tradier.com/
   - Environment variables: `TRADIER_API_KEY`, `TRADIER_ACCOUNT_ID`

4. **News APIs** (optional)
   - Alpha Vantage: https://www.alphavantage.co/
   - Polygon: https://polygon.io/
   - Finnhub: https://finnhub.io/

### 🚨 Immediate Actions if Keys are Exposed

If you accidentally commit API keys to Git:

1. **Rotate ALL exposed keys immediately**:
   - Anthropic: Revoke old key, generate new at console.anthropic.com
   - Alpaca: Reset keys in your account dashboard
   - Tradier: Generate new API key

2. **Update environment variables**:
   - Vercel dashboard (for frontend)
   - Render dashboard (for backend)
   - Local `.env` files (NOT committed)

3. **Clean Git history** (if repo is public):
   ```bash
   git filter-branch --force --index-filter \
   "git rm --cached --ignore-unmatch backend/.env backend/render.yaml" \
   --prune-empty --tag-name-filter cat -- --all
   ```

4. **Force push** (⚠️ WARNING - coordinate with team):
   ```bash
   git push origin --force --all
   ```

---

## 🏗️ Environment Configuration

### Frontend (Vercel)

Set these in **Vercel Dashboard** → Project → Settings → Environment Variables:

```env
NEXT_PUBLIC_BACKEND_API_BASE_URL=https://ai-trader-86a1.onrender.com
NEXT_PUBLIC_API_TOKEN=<your-render-api-token>
NEXT_PUBLIC_APP_NAME=PaiiD
```

### Backend (Render)

Set these in **Render Dashboard** → Web Service → Environment:

```env
# API Security
API_TOKEN=<generate-secure-token>

# Trading Broker (choose ONE)
# Option A: Alpaca
APCA_API_KEY_ID=<your-alpaca-key>
APCA_API_SECRET_KEY=<your-alpaca-secret>
APCA_API_BASE_URL=https://paper-api.alpaca.markets

# Option B: Tradier
TRADIER_API_KEY=<your-tradier-key>
TRADIER_ACCOUNT_ID=<your-account-id>
TRADIER_USE_SANDBOX=true  # Set false for live trading

# AI Configuration
ANTHROPIC_API_KEY=<your-claude-api-key>

# CORS
ALLOW_ORIGIN=https://frontend-scprimes-projects.vercel.app

# Trading Mode
LIVE_TRADING=false  # Set true ONLY for real money
TRADING_MODE=paper  # paper or live
```

### Local Development

Create these files (they are `.gitignore`d):

**Frontend** `.env.local`:
```env
NEXT_PUBLIC_BACKEND_API_BASE_URL=http://127.0.0.1:8001
NEXT_PUBLIC_API_TOKEN=rnd_local_dev_token
NEXT_PUBLIC_TELEMETRY_ENABLED=false
```

**Backend** `.env`:
```env
# Copy template from .env.example
# Fill in your development API keys
API_TOKEN=rnd_local_dev_token
ALLOW_ORIGIN=http://localhost:3000
# ... add other keys
```

---

## 🔒 Security Best Practices

### DO ✅

- Store ALL secrets in environment variables
- Use `.env.local` for local development (gitignored)
- Set secrets via platform dashboards (Vercel/Render)
- Use Alpaca **paper trading** for development
- Review `.gitignore` before commits
- Use `git status` to check for `.env` files before committing
- Rotate keys periodically (every 90 days)

### DON'T ❌

- Commit `.env` files to Git
- Hardcode API keys in source code
- Share API keys via Slack/email/messaging
- Use production keys in development
- Enable live trading without thorough testing
- Commit `render.yaml` with actual key values

---

## 🚨 Reporting Security Issues

If you discover a security vulnerability:

1. **DO NOT** open a public GitHub issue
2. Email: [your-security-email@domain.com]
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

---

## 📜 Git Configuration

### Required `.gitignore` Patterns

**Backend** (Python):
```gitignore
.env
.env.*
__pycache__/
*.pyc
venv/
```

**Frontend** (Next.js):
```gitignore
.env
.env.local
.env.*
node_modules/
.next/
```

### Pre-Commit Hook (Optional)

Install `pre-commit` to automatically check for secrets:

```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml <<EOF
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: detect-private-key
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
EOF

# Install hooks
pre-commit install
```

---

## 🔍 Auditing Checklist

Before deploying:

- [ ] All `.env` files in `.gitignore`
- [ ] No API keys in source code (search for `sk-`, `pk_`, etc.)
- [ ] No API keys in `render.yaml` (use `sync: false`)
- [ ] No API keys in `vercel.json`
- [ ] Environment variables set in platform dashboards
- [ ] Paper trading mode enabled (for non-production)
- [ ] CORS configured correctly
- [ ] API token authentication working

---

## 📚 References

- [Vercel Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)
- [Render Environment Variables](https://render.com/docs/environment-variables)
- [Git Secrets](https://github.com/awslabs/git-secrets)
- [OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)

---

**Last Updated**: October 11, 2025
**Maintainer**: Dr. SC Prime
