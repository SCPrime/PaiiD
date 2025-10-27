# PRE-COMMIT HOOKS - QUICK REFERENCE

**Status:** ✅ Configured and Ready
**Last Updated:** October 27, 2025
**Agent:** 5B - Pre-commit Hooks Specialist

---

## INSTALLATION

```bash
# Install all hooks (frontend + backend)
bash install-pre-commit.sh all

# Install frontend only
bash install-pre-commit.sh frontend

# Install backend only
bash install-pre-commit.sh backend
# OR
cd backend && bash install-hooks.sh
```

---

## MANUAL VALIDATION

### Frontend
```bash
cd frontend
npm run lint:fix          # Fix ESLint issues
npm run format           # Format with Prettier
npm run type-check       # Check TypeScript (warning only)
npx lint-staged          # Run on staged files
```

### Backend
```bash
cd backend
pre-commit run --all-files    # Run all hooks (slow)
pre-commit run --files app/main.py  # Run on specific files
black .                       # Format with Black
ruff check --fix .           # Lint with Ruff
```

---

## BYPASS MECHANISM

### For Orchestrator/CI (Recommended)
```bash
# Method 1: Environment variable
SKIP_HOOKS=1 git commit -m "orchestrator: automated commit"

# Method 2: Git flag
git commit --no-verify -m "orchestrator: automated commit"
```

### For Developers (Emergency Only)
```bash
# Skip validation (use sparingly!)
git commit --no-verify -m "emergency fix"
```

---

## HOOK BEHAVIOR

| Scenario | Frontend | Backend | Type-check |
|----------|----------|---------|------------|
| Frontend files changed | ✅ Runs | ⏭️ Skips | ⚠️ Warns |
| Backend files changed | ⏭️ Skips | ✅ Runs | N/A |
| Both changed | ✅ Runs | ✅ Runs | ⚠️ Warns |
| Docs only (*.md) | ⏭️ Skips | ⏭️ Skips | ⏭️ Skips |
| SKIP_HOOKS=1 | ⏭️ Skips All | ⏭️ Skips All | ⏭️ Skips All |
| CI=true | ⏭️ Skips All | ⏭️ Skips All | ⏭️ Skips All |

---

## WHAT GETS VALIDATED

### Frontend (Husky + lint-staged)
- **ESLint:** Linting on `*.{ts,tsx,js,jsx}` (auto-fix)
- **Prettier:** Formatting on `*.{ts,tsx,js,jsx,json,md,css}` (auto-fix)
- **TypeScript:** Type checking (warning only, doesn't block)

### Backend (pre-commit framework)
- **Black:** Python formatting (100 char lines, auto-fix)
- **Ruff:** Python linting (auto-fix common issues)
- **Syntax:** Python compilation check
- **Imports:** Package structure validation
- **Security:** Debugger/secret detection
- **File Quality:** Trailing whitespace, EOF, YAML/JSON/TOML validation

### Protected Files (Always Checked)
- **LOCKED FINAL:** Reference files that cannot be modified
- **Patterns:** "LOCKED FINAL", "Locked.tsx", "CompletePaiiDLogo", etc.
- **Action:** Commit blocked with detailed error message

---

## TROUBLESHOOTING

### "pre-commit: command not found"
```bash
cd backend
pip install pre-commit
pre-commit install
```

### "husky - pre-commit script failed"
```bash
# Check what's failing
bash .husky/pre-commit

# Bypass if needed
git commit --no-verify -m "message"
```

### "Black is not installed"
```bash
cd backend
pip install -r requirements.txt
```

### "TypeScript errors blocking commit"
**TypeScript errors are now WARNING ONLY** - they don't block commits.
If still blocked, run:
```bash
cd frontend
npm run type-check  # See errors
# Commit proceeds regardless
```

---

## FILES

| File | Purpose |
|------|---------|
| `.husky/pre-commit` | Root-level hook coordinator (modified) |
| `backend/.pre-commit-config.yaml` | Backend hook configuration (new) |
| `backend/install-hooks.sh` | Backend installation script (new) |
| `install-pre-commit.sh` | Root installation script (new) |
| `frontend/.lintstagedrc.json` | Frontend hook config (existing) |
| `pre-commit-hook.sh` | Python validation script (existing) |

---

## DETAILED DOCUMENTATION

See **AGENT_5B_PRECOMMIT_HOOKS.md** for:
- Complete configuration details
- Hook execution flow
- Performance metrics
- Security considerations
- Integration with CI/CD
- Troubleshooting guide

---

**Quick Help:**
- Installation: `bash install-pre-commit.sh all`
- Bypass: `SKIP_HOOKS=1 git commit -m "message"`
- Manual run: `bash .husky/pre-commit`
- Full docs: `AGENT_5B_PRECOMMIT_HOOKS.md`
