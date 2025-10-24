# Cursor Migration Guide - Claude Code Review Checks

**Purpose**: Migrate GitHub Claude Code Action checks to local Cursor workflows to reduce costs and increase speed.

**Status**: 🚧 Migration In Progress
**Target**: Replace 70%+ of GitHub checks with Cursor by end of next sprint

---

## 🎯 Migration Strategy

### Phase 1: Immediate (Weeks 1-2)
- ✅ Configure GitHub Claude to run ONLY on critical files
- ✅ Focus GitHub reviews on stability issues only
- 🔄 Document all checks in this guide
- 🔄 Create `.cursorrules-checks` for Cursor to reference

### Phase 2: Transition (Weeks 3-4)
- 📋 Implement 50% of checks in Cursor
- 📋 Add pre-commit hooks for critical checks
- 📋 Monitor which GitHub checks are still valuable
- 📋 Track cost savings

### Phase 3: Complete Migration (Weeks 5-6)
- 📋 Move remaining checks to Cursor
- 📋 Disable GitHub Claude (or keep for final sanity check only)
- 📋 Document cost savings achieved

---

## 🔍 What GitHub Claude Currently Checks

### Critical Blockers (App Won't Work)

| Check                             | Description                                  | Cursor Alternative                        | Status         |
| --------------------------------- | -------------------------------------------- | ----------------------------------------- | -------------- |
| **API Endpoint Errors**           | 500 errors, missing error handling in routes | Manual review during coding               | 📋 To Do        |
| **Auth/Security Vulnerabilities** | SQL injection, exposed secrets, weak auth    | Can add to `.cursorrules-checks`          | 📋 To Do        |
| **Database Connection Failures**  | Missing DB session handling                  | Can add to `.cursorrules-checks`          | 📋 To Do        |
| **Missing Imports**               | Dependencies that break builds               | Caught by TypeScript/Python LSP in Cursor | ✅ Already Done |
| **Syntax Errors**                 | Code that won't compile                      | Caught by linters in Cursor               | ✅ Already Done |

### Stability Issues (App Might Crash)

| Check                        | Description                                     | Cursor Alternative                                | Status  |
| ---------------------------- | ----------------------------------------------- | ------------------------------------------------- | ------- |
| **Unhandled API Exceptions** | Missing try/except for Tradier/Alpaca/Anthropic | Can add to `.cursorrules-checks`                  | 📋 To Do |
| **Float in Financial Calc**  | Using `float` instead of `Decimal`              | Can add to `.cursorrules-checks`                  | 📋 To Do |
| **Missing CORS Headers**     | Security headers not configured                 | Manual review                                     | 📋 To Do |
| **Race Conditions**          | Async code issues                               | Manual review during coding                       | 📋 To Do |
| **Options Endpoint Pattern** | Similar routing issues to known bug             | Can add pattern matching to `.cursorrules-checks` | 📋 To Do |

---

## 💰 Cost Comparison

### GitHub Claude (Current)

**Before Optimization**:
- Runs on: Every PR to any branch
- Average cost per run: ~$0.15-0.30 (depending on diff size)
- Estimated monthly runs: ~40-60 PRs
- **Monthly cost**: ~$6-18

**After Optimization** (Current State):
- Runs on: PRs to `main` branch + critical files only
- Reduced frequency: ~80% fewer runs
- Average cost per run: ~$0.10-0.20 (reduced max_tokens)
- Estimated monthly runs: ~8-12 PRs
- **Monthly cost**: ~$1-3 💰 **70-85% savings**

### Cursor (Local - Target State)

**Cost**:
- No API costs (local execution)
- One-time setup: 1-2 hours
- Maintenance: ~30 min/month to update rules
- **Monthly cost**: $0 🎉 **100% savings**

**Benefits**:
- ✅ Instant feedback (no waiting for GitHub Actions)
- ✅ Catch issues BEFORE committing
- ✅ No monthly API bills
- ✅ Works offline
- ✅ Can customize checks per file/context

---

## 🛠️ How to Replicate Checks in Cursor

### 1. Financial Precision Check (Decimal vs Float)

**GitHub Check**: Flags `float` usage in financial calculations

**Cursor Implementation**:
```bash
# Add to pre-commit hook or run manually:
cd backend
grep -r "float.*price\|float.*quantity\|float.*balance" app/routers/ app/services/
```

**Better**: Use `.cursorrules-checks` - Cursor will automatically flag these patterns

### 2. API Error Handling Check

**GitHub Check**: Flags missing try/except around external API calls

**Cursor Implementation**:
1. When editing routers/services, manually verify:
   - Every `tradier_client.*` call is wrapped in try/except
   - Every `alpaca.*` call is wrapped in try/except
   - Every `anthropic.*` call is wrapped in try/except

2. Pattern to search for:
```python
# Search for unhandled API calls
grep -r "tradier_client\.\|alpaca\.\|anthropic\." backend/app/ | grep -v "try:"
```

### 3. SQL Injection Check

**GitHub Check**: Flags non-parameterized SQL queries

**Cursor Implementation**:
1. Search for f-strings in database queries:
```bash
grep -r "f\".*SELECT\|f\".*INSERT\|f\".*UPDATE\|f\".*DELETE" backend/app/
```

2. `.cursorrules-checks` will flag this pattern automatically

### 4. Options Endpoint Pattern Check

**GitHub Check**: Detects routing issues similar to known Options endpoint bug

**Cursor Implementation**:
1. When creating new endpoints, verify:
   - Route is registered in router with correct prefix
   - Route path doesn't conflict with existing routes
   - Path parameters are properly typed
   - Endpoint handler is async if calling async services

2. Test locally BEFORE pushing:
```bash
curl http://localhost:8001/api/your-endpoint
# Should NOT return 500 or 404
```

---

## 📝 Pre-Commit Checklist (Manual for Now)

Before committing changes to critical files, verify:

### Backend Changes (`app/routers/`, `app/services/`)
- [ ] All external API calls wrapped in try/except
- [ ] Using `Decimal` for financial calculations (not `float`)
- [ ] Database queries are parameterized (no f-strings in SQL)
- [ ] New endpoints tested locally (curl/browser)
- [ ] Auth required on protected endpoints

### Frontend Changes (`pages/api/proxy/`)
- [ ] API calls go through proxy (not direct to backend)
- [ ] Error states handled in UI
- [ ] Loading states shown during API calls
- [ ] TypeScript types defined (no `any`)

### Security Changes (`core/security.py`, `core/auth.py`)
- [ ] No secrets/keys hardcoded
- [ ] CORS settings correct
- [ ] Rate limiting in place
- [ ] Input validation on all endpoints

---

## 📊 Success Metrics

### Week 1-2 (Setup Phase)
- ✅ GitHub Claude running 80% less frequently
- ✅ Only critical files trigger reviews
- ✅ Cost reduced from ~$6-18/mo to ~$1-3/mo

### Week 3-4 (Transition Phase)
- 🎯 Target: 50% of issues caught in Cursor before commit
- 🎯 Target: GitHub Claude finds <2 issues per PR
- 🎯 Target: Time to PR approval reduced by 30%

### Week 5-6 (Complete Migration)
- 🎯 Target: 90% of issues caught locally in Cursor
- 🎯 Target: GitHub Claude disabled or runs once/week only
- 🎯 Target: API costs near $0/month

---

## 🔄 Repeated Issues Tracker

Track issues that GitHub Claude catches repeatedly - these are prime candidates for Cursor automation:

| Issue                               | Times Caught | Cursor Check Available? | Priority |
| ----------------------------------- | ------------ | ----------------------- | -------- |
| Missing try/except on Tradier calls | 0            | ⏳ Pending               | High     |
| Float instead of Decimal            | 0            | ⏳ Pending               | High     |
| SQL injection risk                  | 0            | ⏳ Pending               | Critical |
| Missing error handling              | 0            | ⏳ Pending               | High     |
| TypeScript `any` usage              | 0            | ✅ ESLint catches this   | Low      |

*Update this table as GitHub reviews happen - when an issue is caught 3+ times, immediately add it to `.cursorrules-checks`*

---

## 🎓 Learning from GitHub Claude

Each time GitHub Claude reviews a PR:

1. **Read the review** - What did it catch?
2. **Ask yourself** - Could I have caught this in Cursor?
3. **Update .cursorrules-checks** - Add pattern if repeated
4. **Document here** - Add to checklist if manual process needed

---

## 🚀 Next Steps

1. ✅ **This week**: Monitor GitHub Claude reviews, document what it catches
2. 📋 **Next week**: Implement top 3 most common checks in `.cursorrules-checks`
3. 📋 **Week 3**: Add pre-commit hooks for critical checks
4. 📋 **Week 4**: Review cost savings, adjust strategy
5. 📋 **Week 5-6**: Finalize migration, disable/minimize GitHub Claude

---

## 📞 When to Still Use GitHub Claude

Even after migration, keep GitHub Claude for:
- ✅ Final sanity check before merging to `main` (once/day max)
- ✅ Complex architectural changes that need deep analysis
- ✅ Security audit of auth/payment code
- ✅ When you're uncertain about a risky change

Run it **manually** via `workflow_dispatch` instead of automatically on every PR.

---

**Last Updated**: 2025-10-24
**Next Review**: Check progress in 1 week

