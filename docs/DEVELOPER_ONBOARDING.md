# PaiiD Developer Onboarding Guide
**Target Time:** 30 minutes to fully operational
**Difficulty:** Intermediate
**Last Updated:** 2025-10-27

---

## Prerequisites

### Required Software
- **Node.js**: v18.x or v20.x ([Download](https://nodejs.org/))
- **Python**: 3.11 or 3.12 ([Download](https://www.python.org/downloads/))
- **Git**: Latest version ([Download](https://git-scm.com/downloads))

### Optional (Recommended)
- **PostgreSQL**: 15.x (for local database)
- **Redis**: 7.x (for caching)
- **VS Code**: With TypeScript and Python extensions

### API Keys Required
1. **Tradier API** (market data): https://tradier.com/products/market-data-api
2. **Alpaca Paper Trading** (orders): https://alpaca.markets/
3. **Anthropic Claude** (AI features): https://console.anthropic.com/

---

## Quick Start (30 Minutes)

### Step 1: Clone Repository (2 minutes)

```bash
# Clone the repository
git clone https://github.com/SCPrime/PaiiD.git
cd PaiiD

# Check you're on main branch
git branch
# Should show: * main
```

---

### Step 2: Backend Setup (10 minutes)

```bash
# Navigate to backend
cd backend

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env  # Mac/Linux
copy .env.example .env  # Windows
```

**Edit `backend/.env`** with your API keys:
```env
# Required
API_TOKEN=rnd_bDRqi1TvLvd3rC78yvUSgDraH2Kl
TRADIER_API_KEY=your_tradier_key_here
TRADIER_ACCOUNT_ID=your_tradier_account_id
TRADIER_API_BASE_URL=https://api.tradier.com/v1
ALPACA_PAPER_API_KEY=your_alpaca_key_here
ALPACA_PAPER_SECRET_KEY=your_alpaca_secret_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Optional (defaults work for development)
DATABASE_URL=sqlite:///./paiid.db
REDIS_URL=redis://localhost:6379/0
ALLOW_ORIGIN=http://localhost:3000
```

**Start backend server:**
```bash
# Make sure you're in backend/ directory
python -m uvicorn app.main:app --reload --port 8001

# Expected output:
# INFO:     Uvicorn running on http://127.0.0.1:8001
# INFO:     Application startup complete.
```

**Verify backend is running:**
```bash
# In a new terminal:
curl http://127.0.0.1:8001/api/health
# Expected: {"status":"healthy"}
```

---

### Step 3: Frontend Setup (10 minutes)

```bash
# Open new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Create .env.local file
cp .env.example .env.local  # Mac/Linux
copy .env.example .env.local  # Windows
```

**Edit `frontend/.env.local`:**
```env
NEXT_PUBLIC_API_TOKEN=rnd_bDRqi1TvLvd3rC78yvUSgDraH2Kl
NEXT_PUBLIC_BACKEND_API_BASE_URL=http://127.0.0.1:8001
NEXT_PUBLIC_ANTHROPIC_API_KEY=your_anthropic_key_here
```

**Start frontend server:**
```bash
# Make sure you're in frontend/ directory
npm run dev

# Expected output:
# ready - started server on 0.0.0.0:3000, url: http://localhost:3000
# event - compiled client and server successfully
```

**Access the application:**
Open browser to: http://localhost:3000

---

### Step 4: Verify Everything Works (5 minutes)

**Backend Health Check:**
```bash
curl http://127.0.0.1:8001/api/health/detailed \
  -H "Authorization: Bearer rnd_bDRqi1TvLvd3rC78yvUSgDraH2Kl"
```

**Frontend Check:**
1. Navigate to http://localhost:3000
2. You should see the radial menu with 10 workflow segments
3. Click "Morning Routine" - should load AI interface
4. Check browser console for errors (F12)

**Common Success Indicators:**
- ✅ Backend: Server running on port 8001
- ✅ Frontend: App running on port 3000
- ✅ No CORS errors in browser console
- ✅ Radial menu renders correctly
- ✅ API calls return data (check Network tab)

---

## Environment Variables Reference

### Backend (.env)

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `API_TOKEN` | Yes | Backend API authentication token | `rnd_bDRqi...` |
| `TRADIER_API_KEY` | Yes | Tradier market data API key | `abc123...` |
| `TRADIER_ACCOUNT_ID` | Yes | Tradier account number | `VA12345678` |
| `TRADIER_API_BASE_URL` | Yes | Tradier API base URL | `https://api.tradier.com/v1` |
| `ALPACA_PAPER_API_KEY` | Yes | Alpaca paper trading key | `PK...` |
| `ALPACA_PAPER_SECRET_KEY` | Yes | Alpaca paper trading secret | `abc...` |
| `ANTHROPIC_API_KEY` | Yes | Claude AI API key | `sk-ant-...` |
| `DATABASE_URL` | No | Database connection string | `sqlite:///./paiid.db` |
| `REDIS_URL` | No | Redis connection string | `redis://localhost:6379/0` |
| `ALLOW_ORIGIN` | No | CORS allowed origin | `http://localhost:3000` |

### Frontend (.env.local)

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_API_TOKEN` | Yes | Must match backend API_TOKEN |
| `NEXT_PUBLIC_BACKEND_API_BASE_URL` | Yes | Backend URL (dev: http://127.0.0.1:8001) |
| `NEXT_PUBLIC_ANTHROPIC_API_KEY` | Yes | For client-side AI features |

---

## Development Workflow

### Running Tests

**Backend Tests:**
```bash
cd backend
python -m pytest tests/ -v

# With coverage:
python -m pytest tests/ --cov=app --cov-report=html

# Specific test file:
python -m pytest tests/test_health.py -v

# Current status: 67% pass rate (baseline)
```

**Frontend Tests:**
```bash
cd frontend
npm run test

# Watch mode (development):
npm run test

# CI mode (with coverage):
npm run test:ci
```

### Code Style & Linting

**Backend:**
```bash
cd backend

# Black (code formatter):
black app/ tests/

# Ruff (linter):
ruff check app/ tests/

# Type checking:
mypy app/
```

**Frontend:**
```bash
cd frontend

# TypeScript check:
npx tsc --noEmit

# ESLint:
npm run lint

# Prettier:
npx prettier --write .
```

### Pre-commit Hooks

The project uses Husky for pre-commit hooks:

```bash
# Install hooks (first time only):
npm install  # In root directory

# Hooks automatically run on:
# - git commit (runs linters, type checks)
# - git push (runs tests)

# Bypass hooks (use sparingly):
SKIP_HOOKS=1 git commit -m "message"
```

### Building for Production

**Frontend:**
```bash
cd frontend
npm run build

# Test production build locally:
npm start
```

**Backend:**
```bash
cd backend
# No build step - Python runs directly
# Ensure all dependencies in requirements.txt
```

---

## Common Troubleshooting

### Issue 1: Port Already in Use

**Symptoms:**
```
Error: listen EADDRINUSE: address already in use :::3000
```

**Solution:**
```bash
# Find process using port 3000:
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -ti:3000 | xargs kill -9

# Or use different port:
PORT=3001 npm run dev
```

### Issue 2: Module Not Found

**Symptoms:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```bash
# Ensure virtual environment is activated:
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# Reinstall dependencies:
pip install -r requirements.txt
```

### Issue 3: CORS Errors

**Symptoms:**
```
Access to XMLHttpRequest at 'http://127.0.0.1:8001/api/...' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Solution:**
1. Check backend `.env` has: `ALLOW_ORIGIN=http://localhost:3000`
2. Restart backend server
3. Clear browser cache (Ctrl+Shift+Delete)

### Issue 4: API Authentication Failures

**Symptoms:**
```
{"detail": "Not authenticated"}
```

**Solution:**
1. Verify `API_TOKEN` matches in both `.env` and `.env.local`
2. Check request headers include: `Authorization: Bearer <token>`
3. Ensure frontend proxy is working (`/api/proxy/api/*`)

### Issue 5: Database Migration Errors

**Symptoms:**
```
alembic.util.exc.CommandError: Can't locate revision identified by '...'
```

**Solution:**
```bash
cd backend

# Reset database (DEVELOPMENT ONLY):
rm paiid.db

# Run migrations:
alembic upgrade head

# Create new migration:
alembic revision --autogenerate -m "description"
```

### Issue 6: TypeScript Errors in IDE

**Symptoms:**
VS Code shows hundreds of red squiggly lines

**Solution:**
```bash
cd frontend

# Reload TypeScript server in VS Code:
# Ctrl+Shift+P -> "TypeScript: Restart TS Server"

# Rebuild TypeScript cache:
rm -rf .next
rm -rf node_modules/.cache
npm run build
```

### Issue 7: Backend Won't Start

**Symptoms:**
```
ImportError: cannot import name 'app' from 'app.main'
```

**Solution:**
1. Check you're in `backend/` directory
2. Virtual environment is activated
3. Try: `python -m uvicorn app.main:app --reload --port 8001`
4. Check `backend/app/main.py` exists

### Issue 8: Frontend Build Fails

**Symptoms:**
```
Type error: ... (TypeScript compilation errors)
```

**Solution:**
```bash
# Current status: 94 TypeScript errors (non-blocking)
# These are documented in docs/TECHNICAL_DEBT.md
# Production build still succeeds despite warnings

# To see errors:
npx tsc --noEmit

# Build anyway (production):
npm run build  # Succeeds with warnings
```

### Issue 9: Redis Connection Failed

**Symptoms:**
```
Error connecting to Redis: Connection refused
```

**Solution:**
```bash
# Redis is optional for development
# Application works without it (uses in-memory cache)

# To install Redis:
# Windows: Use WSL or download from https://github.com/microsoftarchive/redis/releases
# Mac: brew install redis && brew services start redis
# Linux: sudo apt-get install redis-server && sudo service redis-server start
```

### Issue 10: API Keys Not Working

**Symptoms:**
```
Tradier API: 401 Unauthorized
Alpaca API: Invalid API key
```

**Solution:**
1. **Tradier**: Verify key at https://developer.tradier.com/user/settings
2. **Alpaca**: Check paper trading keys at https://app.alpaca.markets/paper/dashboard/overview
3. **Anthropic**: Verify API key at https://console.anthropic.com/settings/keys
4. Ensure no extra spaces in `.env` file
5. Restart backend after changing `.env`

---

## Project Structure

```
PaiiD/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py         # FastAPI app entry point
│   │   ├── routers/        # API endpoints
│   │   ├── services/       # Business logic
│   │   ├── models/         # Database models
│   │   └── core/           # Config, auth, middleware
│   ├── tests/              # Backend tests
│   ├── requirements.txt    # Python dependencies
│   └── .env                # Backend config (not committed)
│
├── frontend/               # Next.js frontend
│   ├── pages/              # Next.js pages (NOT app/ - uses Pages Router)
│   │   ├── index.tsx       # Main dashboard
│   │   ├── _app.tsx        # App wrapper
│   │   └── api/            # API routes (proxy)
│   ├── components/         # React components
│   │   ├── RadialMenu.tsx  # Main navigation
│   │   ├── MorningRoutineAI.tsx
│   │   ├── ActivePositions.tsx
│   │   └── ...             # 10 workflow components
│   ├── lib/                # Utilities
│   ├── public/             # Static assets
│   ├── package.json        # Node dependencies
│   └── .env.local          # Frontend config (not committed)
│
├── docs/                   # Documentation
│   ├── API_QUICK_REFERENCE.md
│   ├── DEVELOPER_ONBOARDING.md (THIS FILE)
│   └── TECHNICAL_DEBT.md
│
└── .github/workflows/      # CI/CD
    ├── backend-tests.yml
    ├── frontend-build.yml
    └── deploy-validation.yml
```

---

## Git Workflow

### Branch Strategy
```bash
# Main branch (protected):
main  # Production-ready code

# Feature branches:
git checkout -b feature/your-feature-name
# Work on feature, commit changes
git push origin feature/your-feature-name
# Create pull request on GitHub
```

### Commit Messages
Follow conventional commits format:
```bash
# Format:
<type>(<scope>): <description>

# Types:
feat:     # New feature
fix:      # Bug fix
docs:     # Documentation
style:    # Formatting, no code change
refactor: # Code restructuring
test:     # Adding tests
chore:    # Maintenance

# Examples:
git commit -m "feat(trading): add options chain display"
git commit -m "fix(auth): resolve JWT token expiration"
git commit -m "docs: update API reference"
```

---

## IDE Setup (VS Code Recommended)

### Recommended Extensions
1. **Python** (ms-python.python)
2. **Pylance** (ms-python.vscode-pylance)
3. **TypeScript and JavaScript Language Features** (built-in)
4. **ESLint** (dbaeumer.vscode-eslint)
5. **Prettier** (esbenp.prettier-vscode)
6. **GitLens** (eamodio.gitlens)

### VS Code Settings
Create `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/backend/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[python]": {
    "editor.defaultFormatter": "ms-python.python"
  }
}
```

---

## Next Steps

1. ✅ Complete this onboarding (you're here!)
2. ☐ Read `docs/API_QUICK_REFERENCE.md` for API details
3. ☐ Review `CLAUDE.md` for architecture overview
4. ☐ Run backend and frontend locally
5. ☐ Make a small change and test
6. ☐ Run tests to verify setup
7. ☐ Read `docs/TECHNICAL_DEBT.md` for known issues
8. ☐ Join team communication channels
9. ☐ Pick your first task from backlog

---

## Getting Help

- **Documentation**: Check `/docs` directory first
- **API Reference**: `docs/API_QUICK_REFERENCE.md`
- **Technical Debt**: `docs/TECHNICAL_DEBT.md`
- **Issues**: https://github.com/SCPrime/PaiiD/issues
- **Swagger UI**: http://127.0.0.1:8001/docs (when backend running)

**Welcome to the PaiiD development team!** 🚀
