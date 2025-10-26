# 🛠️ PaiiD Developer Setup Guide

Complete guide to development tools, code quality standards, and workflows for the PaiiD trading platform.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Development Tools](#development-tools)
- [IDE Configuration](#ide-configuration)
- [Pre-commit Hooks](#pre-commit-hooks)
- [Testing](#testing)
- [Code Quality Standards](#code-quality-standards)
- [Environment Variables](#environment-variables)
- [Zombie Process Prevention](#zombie-process-prevention)
- [Project Structure](#project-structure)
- [Common Issues](#common-issues)
- [Contributing](#contributing)

---

## Prerequisites

### Required Software

- **Node.js** 18+ and npm 9+
- **Python** 3.11+
- **Git** 2.40+
- **VS Code** (recommended) or any editor with EditorConfig support

### API Keys Required

- Tradier API key (live trading account for real-time market data)
- Alpaca Paper Trading API key (for paper trade execution)
- Anthropic API key (for AI features)

---

## Quick Start

### 1. Clone and Install

```bash
# Clone repository
git clone https://github.com/your-org/ai-Trader.git
cd ai-Trader

# Install frontend dependencies
cd frontend
npm install

# Install backend dependencies
cd ../backend
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create `.env.local` in `frontend/`:
```env
NEXT_PUBLIC_API_TOKEN=rnd_bDRqi1TvLvd3rC78yvUSgDraH2Kl
NEXT_PUBLIC_BACKEND_API_BASE_URL=http://127.0.0.1:8001
NEXT_PUBLIC_ANTHROPIC_API_KEY=<your-anthropic-key>
```

Create `.env` in `backend/`:
```env
API_TOKEN=rnd_bDRqi1TvLvd3rC78yvUSgDraH2Kl
TRADIER_API_KEY=<your-tradier-key>
TRADIER_ACCOUNT_ID=<your-tradier-account>
ALPACA_PAPER_API_KEY=<your-alpaca-key>
ALPACA_PAPER_SECRET_KEY=<your-alpaca-secret>
ALLOW_ORIGIN=http://localhost:3000
```

### 3. Run Development Servers

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8001
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Visit http://localhost:3000 to see the application.

---

## Development Tools

### Frontend Tools

#### ESLint
**Purpose:** JavaScript/TypeScript linting for code quality and consistency

**Config:** `frontend/.eslintrc.json`

**Usage:**
```bash
cd frontend
npm run lint           # Check for errors
npm run lint:fix       # Auto-fix issues
```

**Plugins enabled:**
- `@typescript-eslint` - TypeScript-specific rules
- `eslint-plugin-react` - React best practices
- `eslint-plugin-react-hooks` - React Hooks rules
- `eslint-plugin-prettier` - Prettier integration

#### Prettier
**Purpose:** Opinionated code formatter for consistent style

**Config:** `frontend/.prettierrc.json`

**Usage:**
```bash
cd frontend
npm run format         # Format all files
npm run format:check   # Check formatting without changes
```

**Configuration:**
- 100 character line width
- 2-space indentation
- Semicolons required
- Double quotes for strings
- ES5 trailing commas

#### TypeScript Strict Mode
**Purpose:** Enhanced type safety and compile-time error detection

**Config:** `frontend/tsconfig.json`

**Strict options enabled:**
- `strict: true` - All strict type-checking options
- `noUnusedLocals: true` - Error on unused local variables
- `noUnusedParameters: true` - Error on unused function parameters
- `noFallthroughCasesInSwitch: true` - Error on switch fallthrough
- `forceConsistentCasingInFileNames: true` - Case-sensitive imports

#### Husky + lint-staged
**Purpose:** Git hooks automation for pre-commit quality checks

**Config:**
- `frontend/.lintstagedrc.json` - Files to lint
- `.husky/pre-commit` - Pre-commit hook script
- `.husky/commit-msg` - Commit message validation

**Behavior:**
When you run `git commit`, Husky automatically:
1. Runs ESLint on staged `.ts`, `.tsx`, `.js`, `.jsx` files
2. Runs Prettier on staged files
3. Validates commit message format
4. Blocks commit if any checks fail

**Manual trigger:**
```bash
cd frontend
npx lint-staged
```

#### commitlint
**Purpose:** Enforce conventional commit message format

**Config:** `frontend/commitlint.config.js`

**Required format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Valid types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation changes
- `style` - Code style changes (formatting, no logic change)
- `refactor` - Code refactoring (no feature/bug change)
- `perf` - Performance improvements
- `test` - Test additions or fixes
- `build` - Build system changes
- `ci` - CI/CD changes
- `chore` - Maintenance tasks

**Examples:**
```bash
git commit -m "feat(trading): add stop-loss order support"
git commit -m "fix(api): resolve 401 auth errors on /positions"
git commit -m "docs: update DEVELOPER_SETUP.md with testing guide"
```

### Backend Tools

#### black
**Purpose:** Uncompromising Python code formatter (PEP 8 compliant)

**Config:** `backend/pyproject.toml` under `[tool.black]`

**Usage:**
```bash
cd backend
python -m black .              # Format all files
python -m black --check .      # Check without changes
python -m black --diff .       # Show diffs
```

**Configuration:**
- 100 character line length (matches pylint)
- Target Python 3.11

#### isort
**Purpose:** Python import statement organizer

**Config:** `backend/pyproject.toml` under `[tool.isort]`

**Usage:**
```bash
cd backend
python -m isort .              # Sort all imports
python -m isort --check .      # Check without changes
python -m isort --diff .       # Show diffs
```

**Configuration:**
- Uses "black" profile for compatibility
- 100 character line length
- Recognizes `app` as first-party package

#### mypy
**Purpose:** Static type checker for Python

**Config:** `backend/pyproject.toml` under `[tool.mypy]`

**Usage:**
```bash
cd backend
mypy app/                      # Type check all app code
mypy app/routers/              # Check specific directory
```

**Configuration:**
- Python 3.11 target
- Warns on `Any` return types
- Ignores missing library stubs (set `ignore_missing_imports = true`)

**Note:** Currently set to `continue-on-error` in CI (warnings don't fail builds)

#### pylint
**Purpose:** Python code linter for quality and best practices

**Config:** `backend/pyproject.toml` under `[tool.pylint]`

**Usage:**
```bash
cd backend
pylint app/ --max-line-length=100     # Lint all app code
pylint app/routers/portfolio.py       # Lint specific file
```

**Configuration:**
- 100 character line length (matches black)
- Follows PEP 8 standards

**Note:** Currently set to `continue-on-error` in CI (warnings don't fail builds)

#### bandit
**Purpose:** Security vulnerability scanner for Python

**Config:** `backend/.bandit`

**Usage:**
```bash
cd backend
bandit -r app/ -c .bandit      # Scan all app code
```

**Configuration:**
- Excludes `/tests`, `/venv`, `/migrations`
- Skips B101 (assert_used) and B601 (paramiko_calls)

**Checked vulnerabilities:**
- Hardcoded passwords
- SQL injection risks
- Shell injection risks
- Insecure random number generation
- Unsafe YAML loading
- And 30+ other security issues

#### pytest
**Purpose:** Python testing framework

**Usage:**
```bash
cd backend
pytest                         # Run all tests
pytest tests/test_market.py   # Run specific test file
pytest -v                      # Verbose output
pytest --cov=app              # With coverage report
```

**Test files:**
- `tests/test_orders.py` - Order execution tests
- `tests/test_market.py` - Market data endpoint tests
- `tests/test_database.py` - Database model tests
- `tests/conftest.py` - Shared test fixtures

---

## IDE Configuration

### VS Code (Recommended)

Install these extensions:

1. **ESLint** (`dbaeumer.vscode-eslint`)
   - Auto-fixes on save
   - Shows linting errors inline

2. **Prettier** (`esbenp.prettier-vscode`)
   - Format on save
   - Integrates with ESLint

3. **Python** (`ms-python.python`)
   - IntelliSense and debugging
   - Integrated linting

4. **Pylance** (`ms-python.vscode-pylance`)
   - Fast type checking
   - Auto-imports

5. **EditorConfig** (`editorconfig.editorconfig`)
   - Respects `.editorconfig` settings

**Recommended settings.json:**
```json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "eslint.workingDirectories": ["frontend"],
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.linting.mypyEnabled": true,
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "ms-python.black-formatter"
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

### EditorConfig

The `.editorconfig` file at project root ensures consistent coding styles across all editors:

```ini
[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = space
indent_size = 2

[*.{py,pyi}]
indent_size = 4
```

All modern editors support EditorConfig (VS Code, IntelliJ, Sublime, Atom, etc.)

---

## Pre-commit Hooks

### What Happens on Commit

When you run `git commit`, Husky triggers the following checks:

**1. Pre-commit Hook** (`.husky/pre-commit`):
```bash
cd frontend && npx lint-staged
```

This runs ESLint and Prettier on **only the files you're committing** (fast!):
- `*.{ts,tsx,js,jsx}` → ESLint with auto-fix + Prettier
- `*.{json,md,css}` → Prettier only

**2. Commit Message Hook** (`.husky/commit-msg`):
```bash
cd frontend && npx commitlint --edit $1
```

This validates your commit message follows conventional commit format.

### Example Workflow

```bash
# 1. Make changes to files
vim frontend/components/RadialMenu.tsx

# 2. Stage changes
git add frontend/components/RadialMenu.tsx

# 3. Commit with conventional format
git commit -m "feat(ui): add live market data to radial center"

# What happens automatically:
# ✅ ESLint checks RadialMenu.tsx
# ✅ Prettier formats RadialMenu.tsx
# ✅ commitlint validates message format
# ✅ Commit succeeds if all checks pass
```

### Bypassing Hooks (Emergency Only)

```bash
git commit --no-verify -m "emergency fix"
```

**⚠️ Use sparingly!** CI will still catch quality issues.

---

## Testing

### Frontend Tests

**Framework:** Jest + React Testing Library

**Run tests:**
```bash
cd frontend
npm run test          # Watch mode for development
npm run test:ci       # CI mode with coverage
```

**Test files:** `__tests__/` or `*.test.tsx`

**Coverage report:** Generated in `frontend/coverage/`

### Backend Tests

**Framework:** pytest + FastAPI TestClient

**Run tests:**
```bash
cd backend
pytest                # All tests
pytest -v             # Verbose output
pytest --cov=app      # With coverage
```

**Test files:**
- `tests/test_orders.py` - Trading order execution
- `tests/test_market.py` - Market data API integration
- `tests/test_database.py` - SQLAlchemy models
- `tests/conftest.py` - Shared fixtures

**Test database:** Uses SQLite in-memory (no real DB needed)

---

## Code Quality Standards

### Frontend Standards

✅ **TypeScript Strict Mode** - All type errors must be resolved
✅ **ESLint Max Warnings = 0** - No warnings allowed in committed code
✅ **Prettier Formatting** - All code must pass `npm run format:check`
✅ **Conventional Commits** - All commit messages must follow format
✅ **Test Coverage** - New features require tests (aim for 80%+)

### Backend Standards

✅ **Black Formatting** - All Python code formatted with black (100 char lines)
✅ **isort Import Sorting** - All imports organized with isort
✅ **Pylint Score** - Aim for 9.0+ pylint score (currently informational)
✅ **Type Hints** - All new functions should have type hints (checked by mypy)
✅ **Bandit Security** - No security vulnerabilities allowed
✅ **Test Coverage** - New endpoints require tests (aim for 80%+)

### CI/CD Quality Gates

GitHub Actions runs these checks on every PR:

**Frontend:**
1. `npm run build` - TypeScript compilation
2. `npm run lint` - ESLint with zero warnings
3. `npm run format:check` - Prettier formatting
4. `npm run test:ci` - Jest tests with coverage

**Backend:**
1. `black --check` - Code formatting
2. `isort --check` - Import sorting
3. `mypy app/` - Type checking (informational)
4. `pylint app/` - Linting (informational)
5. `bandit -r app/` - Security scanning
6. `pytest -v` - All tests pass

**All checks must pass before merging to main.**

---

## Environment Variables

### Frontend (.env.local)

```env
# Backend API Configuration
NEXT_PUBLIC_API_TOKEN=rnd_bDRqi1TvLvd3rC78yvUSgDraH2Kl
NEXT_PUBLIC_BACKEND_API_BASE_URL=http://127.0.0.1:8001

# AI Features
NEXT_PUBLIC_ANTHROPIC_API_KEY=<your-anthropic-api-key>
```

### Backend (.env)

```env
# API Security
API_TOKEN=rnd_bDRqi1TvLvd3rC78yvUSgDraH2Kl

# Tradier API (Real-time Market Data)
TRADIER_API_KEY=<your-tradier-api-key>
TRADIER_ACCOUNT_ID=<your-tradier-account-id>
TRADIER_API_BASE_URL=https://api.tradier.com/v1

# Alpaca Paper Trading (Order Execution Only)
ALPACA_PAPER_API_KEY=<your-alpaca-key>
ALPACA_PAPER_SECRET_KEY=<your-alpaca-secret>

# CORS Configuration
ALLOW_ORIGIN=http://localhost:3000

# Optional: Redis Caching
REDIS_URL=redis://localhost:6379

# Optional: Error Tracking
SENTRY_DSN=<your-sentry-dsn>
```

**⚠️ NEVER commit .env files to git!** They're in `.gitignore`.

---

## Zombie Process Prevention

### Overview

Zombie processes are a common issue in development environments where processes appear to be running (showing in `netstat`) but are actually dead or unresponsive. This can cause port conflicts and prevent clean development restarts.

### Quick Reference

#### Start Development Environment
```powershell
# ✅ Recommended - includes automatic zombie cleanup
.\start-dev.ps1

# ✅ With force cleanup
.\start-dev.ps1 -KillExisting
```

#### Stop Development Environment
```powershell
# ✅ Graceful shutdown
.\scripts\stop-all.ps1

# ✅ Force cleanup
.\scripts\stop-dev.ps1 -Force
```

#### Emergency Zombie Cleanup
```powershell
# ✅ Kill zombie processes
.\scripts\zombie-killer.ps1 -Force

# ✅ Nuclear option (kill all Python)
.\scripts\emergency-cleanup.ps1 -Force -KillAllPython
```

### Common Zombie Process Issues

#### 1. Port 8001 Zombie Processes
**Symptoms:**
- Port 8001 shows as "LISTENING" but no process found
- `taskkill /PID <pid>` returns "process not found"
- Development fails to start on port 8001

**Solution:**
```powershell
# Use port 8002 instead (default in start-dev.ps1)
.\start-dev.ps1

# Or clean up port 8001
.\scripts\emergency-cleanup.ps1 -Port 8001 -Force
```

#### 2. uvicorn Not Found
**Symptoms:**
- "uvicorn is not recognized as the name of a cmdlet"
- Backend fails to start

**Solution:**
```powershell
# Use full Python path
python -m uvicorn app.main:app --reload --port 8002

# Or use the managed startup script
.\start-dev.ps1
```

### Prevention Best Practices

#### 1. Always Use Managed Scripts
```powershell
# ✅ Correct
.\start-dev.ps1
.\scripts\stop-all.ps1

# ❌ Incorrect
Start-Process powershell -ArgumentList "uvicorn app.main:app"
taskkill /F /IM python.exe
```

#### 2. Proper Shutdown
```powershell
# ✅ Always stop processes gracefully
.\scripts\stop-all.ps1

# ❌ Don't force kill without cleanup
taskkill /F /IM python.exe
```

#### 3. Port Management
```powershell
# ✅ Check port availability first
netstat -ano | findstr :8001

# ✅ Use alternate ports if needed
$env:PORT=8002; .\start-dev.ps1
```

### Automated Detection

#### Scheduled Task (Optional)
```powershell
# Register weekly zombie detection (requires admin)
.\scripts\register-zombie-detection-task.ps1

# Manual detection
.\scripts\scheduled-zombie-detector.ps1
```

#### Log Files
- **Zombie Detection:** `backend/.logs/zombie-detection.log`
- **Process Manager:** `backend/.logs/process-manager.log`

### Emergency Recovery

#### Complete Reset
```powershell
# 1. Stop all processes
.\scripts\stop-all.ps1

# 2. Kill zombie processes
.\scripts\emergency-cleanup.ps1 -Force -KillAllPython

# 3. Clean up PID files
Remove-Item backend\.run\*.pid -Force -ErrorAction SilentlyContinue
Remove-Item frontend\.run\*.pid -Force -ErrorAction SilentlyContinue

# 4. Restart
.\start-dev.ps1 -KillExisting
```

### Troubleshooting

For detailed troubleshooting information, see [PROCESS_MANAGEMENT.md](docs/PROCESS_MANAGEMENT.md#troubleshooting-zombie-processes).

---

## Project Structure

```
ai-Trader/
├── frontend/                    # Next.js frontend
│   ├── components/              # React components
│   │   ├── RadialMenu.tsx       # Main D3.js radial navigation
│   │   ├── ActivePositions.tsx  # Portfolio positions view
│   │   ├── ExecuteTradeForm.tsx # Order entry form
│   │   └── ...
│   ├── pages/                   # Next.js pages (Pages Router)
│   │   ├── index.tsx            # Main dashboard
│   │   ├── _app.tsx             # App wrapper
│   │   └── api/
│   │       └── proxy/           # Backend API proxy
│   ├── lib/                     # Utility libraries
│   │   ├── alpaca.ts            # Alpaca API client
│   │   └── aiAdapter.ts         # Anthropic AI adapter
│   ├── styles/                  # Style configurations
│   │   └── paiid-theme.ts       # Theme colors/constants
│   ├── .eslintrc.json           # ESLint config
│   ├── .prettierrc.json         # Prettier config
│   ├── .lintstagedrc.json       # lint-staged config
│   ├── commitlint.config.js     # commitlint config
│   ├── tsconfig.json            # TypeScript config (strict mode)
│   ├── next.config.js           # Next.js config
│   └── package.json             # Dependencies + scripts
│
├── backend/                     # FastAPI backend
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── routers/             # API route handlers
│   │   │   ├── market.py        # Market data endpoints
│   │   │   ├── portfolio.py     # Portfolio/positions
│   │   │   ├── orders.py        # Trade execution
│   │   │   ├── ai.py            # AI recommendations
│   │   │   └── ...
│   │   ├── models/              # Database models
│   │   │   └── database.py      # SQLAlchemy models
│   │   ├── services/            # Business logic
│   │   │   ├── tradier.py       # Tradier API integration
│   │   │   └── cache.py         # Redis caching
│   │   ├── core/                # Core utilities
│   │   │   ├── config.py        # Settings/env vars
│   │   │   └── auth.py          # Authentication
│   │   └── middleware/          # Middleware layers
│   │       ├── rate_limit.py    # Rate limiting
│   │       └── validation.py    # Input validation
│   ├── tests/                   # Pytest tests
│   │   ├── conftest.py          # Test fixtures
│   │   ├── test_market.py       # Market data tests
│   │   ├── test_orders.py       # Order execution tests
│   │   └── test_database.py     # Database model tests
│   ├── pyproject.toml           # Python tool configs
│   ├── .bandit                  # Bandit security config
│   ├── requirements.txt         # Python dependencies
│   └── Dockerfile               # Docker image config
│
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI/CD pipeline
│
├── .husky/                      # Git hooks
│   ├── pre-commit               # Runs lint-staged
│   └── commit-msg               # Runs commitlint
│
├── .editorconfig                # Cross-editor config
├── CLAUDE.md                    # Claude Code project instructions
├── DEVELOPER_SETUP.md           # This file
├── README.md                    # Project overview
└── ...
```

---

## Common Issues

### Issue: Pre-commit hooks not running

**Solution:**
```bash
cd frontend
npm run prepare    # Reinstall Husky hooks
```

### Issue: ESLint errors on commit

**Solution:**
```bash
cd frontend
npm run lint:fix   # Auto-fix what's possible
npm run lint       # Check remaining issues
```

### Issue: Black/isort check failures in CI

**Solution:**
```bash
cd backend
python -m black .   # Format all files
python -m isort .   # Sort all imports
git add .
git commit -m "style: format code with black and isort"
```

### Issue: TypeScript strict mode errors

**Common fixes:**
- Replace `any` with proper types
- Add null checks: `value?.property`
- Add type assertions: `value as Type`
- Add function return types: `function foo(): ReturnType {}`

### Issue: Commit message rejected

**Error:** `⧗ input: fix bug` → fails commitlint

**Solution:** Use conventional format:
```bash
git commit -m "fix: resolve portfolio refresh bug"
```

### Issue: Tests failing locally

**Frontend:**
```bash
cd frontend
rm -rf node_modules .next
npm install
npm run test
```

**Backend:**
```bash
cd backend
rm -rf .pytest_cache
pytest -v
```

---

## Contributing

### Development Workflow

1. **Create feature branch:**
   ```bash
   git checkout -b feat/your-feature-name
   ```

2. **Make changes and test:**
   ```bash
   # Frontend
   cd frontend
   npm run dev
   npm run test
   npm run lint:fix

   # Backend
   cd backend
   python -m uvicorn app.main:app --reload
   pytest -v
   python -m black .
   python -m isort .
   ```

3. **Commit with conventional format:**
   ```bash
   git add .
   git commit -m "feat(trading): add stop-loss order support"
   ```

4. **Push and create PR:**
   ```bash
   git push origin feat/your-feature-name
   # Create PR on GitHub
   ```

5. **Wait for CI checks:**
   - All ESLint/Prettier checks pass
   - All pytest tests pass
   - All black/isort checks pass
   - Bandit security scan passes

6. **Address review feedback and merge**

### Code Review Checklist

**For reviewers:**
- ✅ Code follows TypeScript/Python style guides
- ✅ All tests pass locally and in CI
- ✅ New features have corresponding tests
- ✅ No security vulnerabilities (bandit)
- ✅ Commit messages follow conventional format
- ✅ No hardcoded secrets or credentials
- ✅ Documentation updated if needed

---

## References

- **ESLint Rules:** https://eslint.org/docs/rules/
- **Prettier Options:** https://prettier.io/docs/en/options.html
- **Conventional Commits:** https://www.conventionalcommits.org/
- **Black Formatter:** https://black.readthedocs.io/
- **pytest Documentation:** https://docs.pytest.org/
- **FastAPI Testing:** https://fastapi.tiangolo.com/tutorial/testing/
- **Next.js Documentation:** https://nextjs.org/docs

---

## Getting Help

**Issues with tools or setup?**
1. Check this guide first
2. Search GitHub issues for similar problems
3. Ask in team chat or create a new GitHub issue

**Questions about PaiiD architecture?**
1. Read `CLAUDE.md` for project overview
2. Check `README.md` for deployment info
3. Review `DATA_SOURCES.md` for data flow

**Want to contribute?**
1. Read this entire guide
2. Set up your local environment
3. Pick an issue from GitHub or propose a feature
4. Follow the contributing workflow above

---

**Happy coding! Let's make PaiiD Oscar-worthy in every category! 🏆**
