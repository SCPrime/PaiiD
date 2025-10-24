# Contributing to PaiiD

Thank you for contributing to **PaiiD (Personal Artificial Intelligence Investment Dashboard)**! This guide will help you get started with contributing code, documentation, and improvements to the platform.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Pull Request Process](#pull-request-process)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing Requirements](#testing-requirements)
- [Documentation](#documentation)
- [Community](#community)

---

## Code of Conduct

### Our Standards

- **Be respectful** - Treat all contributors with respect
- **Be constructive** - Provide helpful feedback in code reviews
- **Be collaborative** - Work together to solve problems
- **Be patient** - Remember that everyone is learning

### Unacceptable Behavior

- Harassment or discriminatory language
- Trolling or personal attacks
- Publishing private information without permission
- Any conduct that could be considered unprofessional

---

## Getting Started

### Quick Setup (Recommended)

Use our automated setup script for fastest onboarding:

```bash
./scripts/setup-dev-env.sh
```

This will automatically:
- ✅ Check all prerequisites
- ✅ Create virtual environments
- ✅ Install all dependencies (frontend + backend)
- ✅ Set up environment files from templates
- ✅ Configure internal PyPI mirror for security auditing
- ✅ Verify installation

**Time:** ~5 minutes ⚡

### Prerequisites

Before contributing, make sure you have:

1. **Git** installed and configured
2. **Node.js 20+** and npm 9+
3. **Python 3.11+** and pip
4. **VS Code** or another editor with EditorConfig support
5. **API keys** for development (Tradier, Alpaca, Anthropic)

### Manual Setup

If you prefer manual setup or the automated script fails:

1. **Fork the repository** on GitHub
2. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR-USERNAME/PaiiD.git
   cd PaiiD
   ```

3. **Add upstream remote:**
   ```bash
   git remote add upstream https://github.com/SCPrime/PaiiD.git
   ```

4. **Install dependencies:**
   ```bash
   # Frontend
   cd frontend
   npm ci

   # Backend
   cd ../backend
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Optional dev tools
   ```

5. **Set up environment variables:**
   ```bash
   # Backend
   cd backend
   cp .env.example .env
   # Edit .env and add your API keys

   # Frontend
   cd frontend
   echo "NEXT_PUBLIC_API_TOKEN=rnd_bDRqi1TvLvd3rC78yvUSgDraH2Kl" > .env.local
   echo "NEXT_PUBLIC_BACKEND_API_BASE_URL=http://127.0.0.1:8001" >> .env.local
   ```

6. **Verify setup:**
   ```bash
   # Frontend
   cd frontend
   npm run dev         # Should start on localhost:3000
   npm run test        # Tests should pass
   npm run lint        # No errors

   # Backend
   cd backend
   source venv/bin/activate
   python -m uvicorn app.main:app --reload --port 8001  # Should start on :8001
   pytest -v           # Tests should pass
   ```

---

## 🔒 Security Practices

### Dependency Security Audits

PaiiD uses an **internal PyPI mirror** for automated security scanning with `pip-audit`. All Python dependencies are continuously monitored for vulnerabilities.

#### Running Security Audits Locally

**Quick Audit (Recommended):**
```bash
cd backend/pypi-mirror
./scripts/quick-audit.sh
```

This automated script will:
1. Populate the internal mirror (if needed)
2. Start the mirror server
3. Install pip-audit from the mirror
4. Scan all backend dependencies
5. Generate a detailed security report
6. Display vulnerabilities with fix recommendations

**Output:**
```
🔒 PaiiD Security Audit
📦 Packages Audited: 85
⚠️  Vulnerabilities Found: 1
📄 Report: backend/security-audit-20251024-123456.txt
```

**Manual Audit:**
```bash
# 1. Start mirror server (in one terminal)
cd backend/pypi-mirror
python scripts/serve-mirror.py

# 2. In another terminal, configure and audit
source backend/pypi-mirror/activate-mirror.sh
pip install pip-audit
cd backend
pip-audit -r requirements.txt
```

#### CI/CD Automated Scanning

**Every commit automatically:**
- ✅ Runs `pip-audit` on all backend dependencies
- ✅ Posts PR comments if vulnerabilities found
- ✅ Uploads detailed audit reports (90-day retention)
- ✅ Blocks merge if critical vulnerabilities detected

**Viewing Audit Reports:**
1. Go to **Actions** tab on GitHub
2. Click on your workflow run
3. Download "pip-audit-report" artifact
4. Review JSON report for full vulnerability details

#### Handling Security Vulnerabilities

When vulnerabilities are found:

**1. Review the Report:**
```bash
cat backend/security-audit-*.txt
```

**2. Assess Impact:**
- Is it in a direct or indirect dependency?
- Does it affect functionality we actually use?
- What's the severity? (Critical, High, Medium, Low)
- Is there a fix available?

**3. Fix the Vulnerability:**

```bash
# Option A: Update the vulnerable package
cd backend
source venv/bin/activate
pip install --upgrade vulnerable-package
pip freeze | grep vulnerable-package >> requirements.txt

# Option B: Update all dependencies (careful!)
pip install --upgrade -r requirements.txt
pip freeze > requirements.txt

# Option C: Switch to alternative package (if no fix available)
pip uninstall vulnerable-package
pip install alternative-package
# Update imports in code
```

**4. Verify the Fix:**
```bash
cd backend/pypi-mirror
./scripts/quick-audit.sh --no-download
```

**5. Commit and Test:**
```bash
git add backend/requirements.txt
git commit -m "fix(security): update <package> to fix <CVE-ID>"

# Run full test suite
cd backend && pytest
cd frontend && npm test
```

**6. Document if Accepting Risk:**

If vulnerability has no fix or minimal impact:
```bash
# Create docs/security/CVE-XXXX-XXXXX.md
echo "## CVE-XXXX-XXXXX Assessment

**Package:** package-name v1.2.3
**Severity:** Medium
**Impact:** Timing attack on cryptographic operations

**Risk Assessment:** ACCEPTED
- Attack requires local access to measure timing
- Not exposed in our API usage
- Upstream has no planned fix
- Alternative packages have worse trade-offs

**Mitigation:**
- Rate limiting on authentication endpoints
- Network-level TLS protections
- Monitoring for unusual timing patterns

**Approved By:** @username
**Date:** 2025-10-24
" > docs/security/CVE-XXXX-XXXXX.md

git add docs/security/CVE-XXXX-XXXXX.md
git commit -m "docs(security): document accepted risk for CVE-XXXX-XXXXX"
```

#### Security Best Practices

**Never commit secrets:**
- ✅ Use `.env` files (in `.gitignore`)
- ✅ Use environment variables in CI/CD
- ✅ Use `.env.example` templates for documentation
- ❌ Never commit real API keys, passwords, or tokens

**Keep dependencies updated:**
```bash
# Check for outdated packages
cd backend && pip list --outdated

# Update specific package
pip install --upgrade package-name

# Run security audit after updates
cd pypi-mirror && ./scripts/quick-audit.sh
```

**Use the internal mirror:**
```bash
# In development
source backend/pypi-mirror/activate-mirror.sh
pip install <package>

# In CI/CD (automatically configured)
# See .github/workflows/ci.yml
```

---

## Development Workflow

### 1. Sync with Upstream

Always start by syncing with the latest upstream changes:

```bash
git checkout main
git pull upstream main
git push origin main
```

### 2. Create a Feature Branch

Use descriptive branch names with type prefixes:

```bash
git checkout -b feat/add-stop-loss-orders
git checkout -b fix/portfolio-refresh-bug
git checkout -b docs/update-api-documentation
```

**Branch name conventions:**
- `feat/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions or improvements
- `chore/` - Maintenance tasks

### 3. Make Your Changes

**Best practices:**
- Write clean, self-documenting code
- Follow existing code style and patterns
- Add comments for complex logic
- Keep changes focused (one feature/fix per PR)
- Write tests for new functionality
- Update documentation if needed

### 4. Test Your Changes

**Frontend:**
```bash
cd frontend
npm run dev              # Manual testing
npm run test             # Automated tests
npm run lint             # Check for linting errors
npm run format:check     # Check formatting
```

**Backend:**
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8001  # Manual testing
pytest -v                # Automated tests
python -m black .        # Format code
python -m isort .        # Sort imports
python -m mypy app/      # Type checking
python -m pylint app/    # Linting
```

### 5. Commit Your Changes

Follow [Conventional Commits](https://www.conventionalcommits.org/) format:

```bash
git add .
git commit -m "feat(trading): add stop-loss order support"
```

**Pre-commit hooks will automatically:**
- Run ESLint and Prettier on staged files
- Validate commit message format
- Block commit if checks fail

### 6. Push to Your Fork

```bash
git push origin feat/add-stop-loss-orders
```

### 7. Create a Pull Request

1. Go to your fork on GitHub
2. Click "Compare & pull request"
3. Fill out the PR template (see below)
4. Wait for CI checks to pass
5. Request reviews from maintainers

---

## Commit Message Guidelines

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type

Must be one of:
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation only
- `style` - Code style changes (formatting, no logic change)
- `refactor` - Code refactoring (no feature/bug change)
- `perf` - Performance improvements
- `test` - Test additions or fixes
- `build` - Build system changes
- `ci` - CI/CD configuration changes
- `chore` - Maintenance tasks (dependencies, etc.)
- `revert` - Revert a previous commit

### Scope

Optional. Indicates which part of the codebase:
- `trading` - Order execution, positions
- `market` - Market data, quotes
- `ai` - AI recommendations, chat
- `ui` - User interface components
- `api` - Backend API endpoints
- `db` - Database models/migrations
- `auth` - Authentication/authorization
- `docs` - Documentation

### Subject

- Use imperative, present tense: "add" not "added" or "adds"
- Don't capitalize first letter
- No period (.) at the end
- Maximum 72 characters

### Body

Optional. Explain what and why (not how):
- Wrap at 72 characters
- Separate from subject with blank line
- Use bullet points if needed

### Footer

Optional. Reference issues or breaking changes:
```
Closes #123
BREAKING CHANGE: API endpoint /api/positions renamed to /api/portfolio/positions
```

### Examples

**Good commits:**
```
feat(trading): add stop-loss order support

Implement stop-loss order type with configurable trigger price.
Updates OrderTemplate model and ExecuteTradeForm component.

Closes #456
```

```
fix(api): resolve 401 errors on /positions endpoint

The endpoint was missing Authorization header validation.
Added require_bearer dependency to fix authentication.

Fixes #789
```

```
docs: update DEVELOPER_SETUP.md with testing guide

Add comprehensive testing section covering Jest and pytest usage.
```

**Bad commits:**
```
fix bug                    ❌ (no scope, vague subject)
Added new feature          ❌ (past tense, not conventional)
WIP                        ❌ (not descriptive)
asdfasdf                   ❌ (not meaningful)
```

---

## Pull Request Process

### PR Template

When creating a PR, include:

```markdown
## Description
Brief description of what this PR does and why.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Documentation update

## Related Issues
Closes #123
Relates to #456

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
- [ ] Tests added for new functionality
- [ ] All existing tests pass
- [ ] Manual testing completed

## Screenshots (if UI changes)
[Add screenshots here]

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No console.log or debug statements
- [ ] All CI checks pass
```

### CI Requirements

All PRs must pass these CI checks:

**Frontend:**
- ✅ TypeScript compilation (`npm run build`)
- ✅ ESLint with zero warnings (`npm run lint`)
- ✅ Prettier formatting (`npm run format:check`)
- ✅ Jest tests (`npm run test:ci`)

**Backend:**
- ✅ Black formatting (`black --check .`)
- ✅ isort import sorting (`isort --check .`)
- ✅ mypy type checking (informational)
- ✅ pylint linting (informational)
- ✅ bandit security scan (`bandit -r app/`)
- ✅ pytest tests (`pytest -v`)

### Review Process

1. **Automated checks** - CI must pass before review
2. **Code review** - At least one maintainer approval required
3. **Address feedback** - Make requested changes and push updates
4. **Final approval** - Maintainer approves and merges

### After Merge

1. **Delete your branch** (GitHub will prompt)
2. **Sync your fork:**
   ```bash
   git checkout main
   git pull upstream main
   git push origin main
   ```
3. **Celebrate!** 🎉

---

## Code Style Guidelines

### Frontend (TypeScript/React)

**TypeScript:**
- Use `interface` for object shapes, `type` for unions
- Avoid `any` - use proper types or `unknown`
- Enable all strict compiler options
- Add return types to functions

**React:**
- Functional components with hooks only
- Use descriptive prop names
- Extract reusable logic into custom hooks
- Keep components focused (single responsibility)

**Styling:**
- Inline styles only (no CSS-in-JS libraries)
- Use glassmorphism dark theme colors
- Follow existing patterns in RadialMenu.tsx

**File organization:**
```typescript
// 1. Imports
import { useState, useEffect } from 'react';

// 2. Types/Interfaces
interface ComponentProps {
  title: string;
  onClose: () => void;
}

// 3. Component
export default function Component({ title, onClose }: ComponentProps) {
  // 4. Hooks
  const [state, setState] = useState<string>('');

  // 5. Effects
  useEffect(() => {
    // ...
  }, []);

  // 6. Event handlers
  const handleClick = () => {
    // ...
  };

  // 7. Render
  return <div>{title}</div>;
}
```

### Backend (Python/FastAPI)

**Python:**
- Follow PEP 8 style guide
- 100 character line length (enforced by black)
- Type hints for all functions
- Docstrings for public functions

**FastAPI:**
- Use Pydantic models for request/response validation
- Dependency injection for database sessions
- Proper HTTP status codes
- Comprehensive error handling

**File organization:**
```python
# 1. Standard library imports
import logging
from datetime import datetime
from typing import List, Optional

# 2. Third-party imports
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

# 3. Local imports
from ..core.auth import require_bearer
from ..db.session import get_db
from ..models.database import User

# 4. Module constants
logger = logging.getLogger(__name__)
CACHE_TTL = 300

# 5. Pydantic models
class UserResponse(BaseModel):
    id: int
    email: str

# 6. Router
router = APIRouter()

# 7. Endpoints
@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

### Documentation

**Code comments:**
- Explain **why**, not **what** (code should be self-documenting)
- Add comments for complex algorithms
- Use TODO comments for follow-up work: `# TODO: Add pagination support`

**Docstrings:**
```python
def execute_trade(symbol: str, quantity: int, side: str) -> dict:
    """
    Execute a paper trade via Alpaca API.

    Args:
        symbol: Stock ticker symbol (e.g., "AAPL")
        quantity: Number of shares to trade
        side: "buy" or "sell"

    Returns:
        dict: Alpaca order response with order_id and status

    Raises:
        HTTPException: If API call fails or validation errors occur
    """
    # Implementation...
```

---

## Testing Requirements

### Frontend Testing

**What to test:**
- Component rendering
- User interactions (clicks, form submissions)
- API call mocking
- Edge cases and error states

**Example test:**
```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import ExecuteTradeForm from '../components/ExecuteTradeForm';

test('submits trade with valid inputs', async () => {
  render(<ExecuteTradeForm />);

  fireEvent.change(screen.getByLabelText('Symbol'), { target: { value: 'AAPL' } });
  fireEvent.change(screen.getByLabelText('Quantity'), { target: { value: '10' } });
  fireEvent.click(screen.getByText('Submit'));

  expect(await screen.findByText('Order submitted')).toBeInTheDocument();
});
```

### Backend Testing

**What to test:**
- API endpoints (success and error cases)
- Database models and relationships
- Business logic in service layers
- Security and validation

**Example test:**
```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_positions_requires_auth():
    """Test /api/positions requires authentication"""
    response = client.get("/api/positions")
    assert response.status_code == 401

def test_get_positions_success():
    """Test /api/positions returns positions with valid auth"""
    headers = {"Authorization": "Bearer test-token-12345"}
    response = client.get("/api/positions", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

### Coverage Goals

- **New features:** 80%+ coverage required
- **Bug fixes:** Add regression tests
- **Refactoring:** Maintain or improve coverage

---

## Documentation

### What to Document

**Update these files when relevant:**
- `README.md` - Project overview, deployment URLs
- `CLAUDE.md` - Architecture, conventions, troubleshooting
- `DEVELOPER_SETUP.md` - Development tools, setup guide
- `CONTRIBUTING.md` - This file
- `DATA_SOURCES.md` - Data flow explanations
- Inline code comments - Complex logic

### Documentation Standards

- Use clear, concise language
- Include code examples
- Keep information up to date
- Link to external resources when helpful

---

## Community

### Getting Help

- **Questions?** Open a GitHub Discussion
- **Bugs?** Create a GitHub Issue with reproduction steps
- **Features?** Propose in GitHub Issues with use case

### Reporting Bugs

**Use this template:**
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g., Windows 11]
- Browser: [e.g., Chrome 120]
- Frontend version: [e.g., commit hash]
- Backend version: [e.g., commit hash]

**Additional context**
Any other relevant information.
```

### Suggesting Features

**Use this template:**
```markdown
**Feature Description**
Clear description of the proposed feature.

**Use Case**
Why is this feature needed? What problem does it solve?

**Proposed Solution**
How would you implement this feature?

**Alternatives Considered**
Other approaches you've considered.

**Additional Context**
Mockups, diagrams, or examples.
```

---

## Thank You!

Your contributions make PaiiD better for everyone. Whether it's code, documentation, bug reports, or feature suggestions - every contribution is valued.

**Let's make PaiiD Oscar-worthy in every category! 🏆**

Questions? Reach out in GitHub Discussions or create an issue.

Happy contributing! 🚀
