# Debug Task: unified_auth Logic Issue

**Status**: 🔴 Active Issue
**Created**: 2025-10-25
**Priority**: Medium
**Assignee**: Follow-up debugging session

## Problem
After migrating all 17 backend routers to use `get_current_user_unified`, authenticated endpoints still return:
```json
{"detail":"Invalid token: Not enough segments"}
```

This error comes from JWT validation logic, suggesting the unified auth is incorrectly treating simple API tokens as JWTs.

## What's Working
- ✅ Backend starts successfully on port 8001
- ✅ All 17 router files correctly import `get_current_user_unified`
- ✅ Basic (unauthenticated) health check works: `GET /api/health`
- ✅ No import errors or syntax errors

## What's Failing
- ❌ Authenticated endpoints return JWT error: `GET /api/health/detailed`
- ❌ Simple API tokens not being recognized despite matching `settings.API_TOKEN`

## Test Case
```bash
# API Token from .env
API_TOKEN=tuGlKvrYEoiJcv7r7oIy7zXM9pqVnaxN_74obFz6lVo

# Test command
curl -H "Authorization: Bearer tuGlKvrYEoiJcv7r7oIy7zXM9pqVnaxN_74obFz6lVo" \
  http://127.0.0.1:8001/api/health/detailed

# Expected: {"status": "healthy", ...}
# Actual: {"detail": "Invalid token: Not enough segments"}
```

## Root Cause Hypothesis
The issue is likely in `backend/app/core/unified_auth.py` lines 98-129:

```python
def get_current_user_unified(
    authorization: str | None = Header(None), db: Session = Depends(get_db)
) -> User:
    auth_mode = get_auth_mode(authorization)  # Line 98

    # CASE 1: Simple API Token
    if auth_mode == AuthMode.API_TOKEN:  # Line 103
        # Should return user here...

    # CASE 2: JWT Authentication
    if auth_mode == AuthMode.JWT:  # Line 126
        # JWT validation happens here (causing the error)
```

**Hypothesis**: The `get_auth_mode()` function (line 54-77) might not be correctly detecting simple API tokens, causing all tokens to fall through to JWT validation.

## Files Involved
- `backend/app/core/unified_auth.py` (lines 54-129) - **PRIMARY SUSPECT**
- `backend/app/core/config.py` (settings.API_TOKEN loading)
- `backend/app/core/jwt.py` (JWT decode logic throwing the error)
- All 17 router files in `backend/app/routers/` (already correctly updated)

## Debugging Steps

### Step 1: Add Logging
Add debug logging to `unified_auth.py`:

```python
def get_auth_mode(authorization: str | None = Header(None)) -> str:
    logger.debug(f"🔍 get_auth_mode called with authorization: {authorization[:50] if authorization else None}...")

    if not authorization:
        logger.debug("  → AuthMode.MVP_FALLBACK (no auth header)")
        return AuthMode.MVP_FALLBACK

    if not authorization.startswith("Bearer "):
        logger.debug("  → AuthMode.MVP_FALLBACK (not Bearer)")
        return AuthMode.MVP_FALLBACK

    token = authorization.split(" ", 1)[1]
    logger.debug(f"  Extracted token: {token[:20]}...")
    logger.debug(f"  settings.API_TOKEN: {settings.API_TOKEN[:20]}...")

    # Check if it's the simple API token
    if token == settings.API_TOKEN:
        logger.debug("  → AuthMode.API_TOKEN (matched settings)")
        return AuthMode.API_TOKEN

    # Otherwise assume it's a JWT
    logger.debug("  → AuthMode.JWT (no match, assuming JWT)")
    return AuthMode.JWT
```

### Step 2: Use F5 Debugging
1. Open `backend/app/core/unified_auth.py` in VS Code
2. Set breakpoint on line 98: `auth_mode = get_auth_mode(authorization)`
3. Press `Ctrl+Shift+D` to open Debug panel
4. Select `🐍 Python: Backend (Uvicorn)` from dropdown
5. Press `F5` to start debugging
6. In another terminal, run the curl test command
7. When breakpoint hits:
   - Step into `get_auth_mode()` (F11)
   - Inspect `authorization` variable
   - Inspect `settings.API_TOKEN` variable
   - Check if token comparison succeeds
   - See which auth_mode is returned

### Step 3: Check Environment Variable Loading
```bash
# Verify .env is being loaded
cd backend
grep "^API_TOKEN=" .env

# Check Python can access it
python -c "from app.core.config import settings; print(f'API_TOKEN: {settings.API_TOKEN[:20]}...')"
```

### Step 4: Test Token Comparison
Add this temporary endpoint to test:

```python
@router.get("/debug/auth-mode")
async def debug_auth_mode(authorization: str | None = Header(None)):
    from app.core.config import settings

    if not authorization:
        return {"result": "No auth header"}

    if not authorization.startswith("Bearer "):
        return {"result": "Not Bearer token"}

    token = authorization.split(" ", 1)[1]

    return {
        "token_length": len(token),
        "expected_length": len(settings.API_TOKEN),
        "tokens_match": token == settings.API_TOKEN,
        "token_first_20": token[:20],
        "expected_first_20": settings.API_TOKEN[:20]
    }
```

## Recommended Fix Approach
1. ✅ Use VS Code F5 debugging to trace execution
2. ✅ Add `logger.debug()` statements to see auth flow
3. 🔍 Identify where token comparison fails
4. 🔧 Fix logic in `get_auth_mode()` or `get_current_user_unified()`
5. ✅ Test with curl command
6. ✅ Verify all 17 router endpoints work
7. ✅ Remove debug logging
8. ✅ Commit fix

## Related Files Created
- `.vscode/launch.json` - F5 debugging configurations
- `.vscode/F5_ACTIVATION_GUIDE.md` - Debugging guide
- `TEST_F5_NOW.md` - Quick F5 test procedure
- `test-f5-debug.html` - Interactive browser test
- `scripts/fix_backend_auth_universal.py` - Auth migration script

## Related Commit
Commit: `dabd626` - "feat: Migrate 17 backend routers to unified auth + F5 debugging"

## Success Criteria
- [ ] curl test command returns healthy status (not JWT error)
- [ ] All 17 authenticated endpoints accept simple API tokens
- [ ] JWT authentication still works for actual JWTs
- [ ] MVP fallback mode still works (no auth header)
- [ ] Unit tests added for `get_auth_mode()` function
- [ ] Debug logging removed or set to DEBUG level only

## Notes
- Backend successfully starts, so this is not a critical blocker
- All router files are correctly configured
- Issue is isolated to `unified_auth.py` logic only
- F5 debugging tools are ready to use for investigation

---

**Next Session**: Use F5 debugging to step through auth flow and identify exact failure point.
