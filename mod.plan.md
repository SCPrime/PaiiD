# MOD SQUAD Plan – Branding + Full Verification (PaiiD)

## Objective
Guarantee a production‑tight PaiiD platform with:
- Locked PaiiD logo/chat component rendered in the header on every page
- UI branding: replace user‑facing “AI”/“iPi” text with “PaiiD” + locked logo (no code identifier changes)
- End‑to‑end live data validation (quotes, bars, options, news, auth, orders/positions)
- Zero browser errors, strict CORS/auth/error‑mapping, and no legacy code conflicts
- Identical checks by all agents/subagents/extensions

## Branding Enforcement
- Header: `frontend/components/layout/AppHeader.tsx` mounts `CompletePaiiDLogo` globally via `pages/_app.tsx`
- UI text replacements (visible strings only):
  - “AI Recommendations” → “PaiiD Recommendations”
  - “Ask AI” / “AI Suggest” → “Ask PaiiD” / “PaiiD Suggest”
  - Onboarding: “AI‑assisted” → “PaiiD‑assisted”
- Inline logo component: `frontend/components/ui/PaiiDInline.tsx` with `aria-label="PaiiD"`
- Accessibility: screen readers announce “PaiiD” wherever the inline logo replaces text
- Do NOT edit locked file `frontend/components/CompletePaiiDLogo.tsx`

## Single Source of Truth (All agents/subagents/extensions must use the same checks)
- Config: `mod_squad.config.json` (required) – base_url, origin, timeouts, tags, thresholds, report_paths
- Standard commands (required):
  - `npm run mod:github` → `python scripts/auto_github_monitor.py --full-audit --output reports/github_mod.json`
  - `npm run mod:browser` → `python scripts/browser_mod.py --check-render --live-data --output reports/browser_mod.json`
  - `npm run mod:flows` → `python scripts/live_data_flows.py --comprehensive --output reports/live_flows.json`
  - `npm run mod:all` → runs the three above; non‑zero exit on any failure
- Pre‑commit quick gate (required): render + minimal flows; fail blocks commit
- CI gating (required): `.github/workflows/mod-squad.yml` runs `mod:all` on push/PR; merge blocked unless all pass
- Artifact schema (required): identical top‑level keys across reports: `{ status, errors, timings, p95_ms, details }`
- Enforcement (required): any agent/subagent/extension must call these commands; deviation fails with reason “nonstandard runner”

## Tools (added)
- Repo audit: `scripts/auto_github_monitor.py`
  - Flags: `--full-audit`, `--scan-conflicts`, `--scan-old-code`, `--endpoint-coverage`, `--env-audit`, `--output`
  - Finds deprecated patterns, missing CORS/auth, proxy mismatches, env drift
- Browser verification: `scripts/browser_mod.py` (wrapper for Playwright tags) [planned]
  - Flags: `--check-render`, `--live-data`, `--interactions-only`, `--output`
- Live flows: `scripts/live_data_flows.py` (enhanced) [present]
  - Flags: `--comprehensive`, `--output`

## CI Workflow (planned)
`.github/workflows/mod-squad.yml`
- Steps:
  1) Repo audit → `github_mod.json`
  2) Browser checks (render + live) → `browser_mod.json`
  3) Live flows (comprehensive) → `live_flows.json`
- Upload artifacts: `mod-squad-reports/`
- Block merges on failures

## Branding Checks (Hard Gates)
- Grep rules: fail CI if UI contains raw `\biPi\b` text or “AI” branding in visible strings
  - Allow back‑end identifiers, env names, comments, docs
- Header presence test:
  - Assert PaiiD header exists on `/login`, `/register`, `/dashboard`, and all wedges
- A11y:
  - Assert inline logo is accompanied by `aria-label="PaiiD"` or sr‑only text

## Browser MOD Scenarios (Playwright tags)
- @render: `/login`, `/register`, `/dashboard`, each wedge → no console errors, header present
- @live: proxy origin preflight + health; quotes/bars/options/news → 200 OK; P95 ≤ 2s
- @interactions: 
  - Login with Remember Me → JWT cookie 30 days
  - Radial wedges navigate without errors
  - Execute trade (paper) → confirmation
  - PaiiD recommendations query flow → 3 cards, accept → prefilled trade
  - News impact cards show color outlines and actions

## Live Data Flows (scripts/live_data_flows.py)
- `/api/proxy/api/market/quote/SPY` → 200 (stale fallback acceptable)
- `/api/proxy/api/market/bars/SPY?timeframe=daily&limit=5` → 200
- `/api/proxy/api/options/expirations/SPY` → 200
- `/api/proxy/api/health/readiness` → 200 healthy or structured 503 (not 500)
- Optional: `/api/proxy/api/news/market` → 200

## Performance & Reliability
- Response times: P95 ≤ 2s on critical paths (Playwright timings + flows)
- Error mapping: 401/403/429 → 503; 5xx upstream → 502; missing quote → historical fallback 200
- CORS: env‑driven allowlist; preflights pass for production origin

## Security & Safety
- No secrets in code/logs (scan by repo audit)
- All user endpoints require JWT; service endpoints use API token via proxy
- Strict CORS (no wildcard)
- Locked files untouched (logo)

## Port & URL Consistency (CRITICAL - Added Oct 30, 2025)
**Rule:** All references to the same service MUST use the same port across all config files.

**MOD SQUAD Enforcement:**
- Repo audit scans ALL JSON configs for port references (localhost:PORT, "port": PORT, HttpPort: PORT)
- Flags inconsistencies as HIGH severity errors
- Blocks commits if same service referenced with different ports
- Flags dangerous ports (80, 443) that require admin on Windows

**Examples of what gets caught:**
- ❌ Dashboard in services: `localhost:8000` but browser_tests scenario: `localhost:80` → INCONSISTENT!
- ❌ Port 80 or 443 anywhere → HIGH severity (use 8000, 8443 instead)
- ❌ LiteLLM in one file: `:4000`, in another: `:4001` → INCONSISTENT!

**Validation:**
```bash
python scripts/repo_audit.py --output reports/audit.json
# Will fail with exit code 1 if any port inconsistencies found
```

**This check is MANDATORY for all projects to prevent deployment failures.**

## Acceptance Criteria
- PaiiD header (locked logo/chat) renders on every page
- All visible UI “AI”/“iPi” strings show “PaiiD” + logo; a11y text says “PaiiD”
- All MOD SQUAD reports PASS; artifacts uploaded (no console errors)
- End‑to‑end live flows PASS; P95 ≤ 2s; correct error mapping
- No legacy code conflicts; env and proxy allowlist consistent with backend

## Commands
- Repo audit:
```
python scripts/auto_github_monitor.py --full-audit --output reports/github_mod.json
```
- Browser checks:
```
python scripts/browser_mod.py --check-render --live-data --output reports/browser_mod.json
```
- Live flows:
```
python scripts/live_data_flows.py --comprehensive --output reports/live_flows.json
```

## Notes
- Branding is UI‑only; backend identifiers or env vars with "ai" remain untouched.
- Any failure halts deployment and triggers remediation before re‑run.

---

## 📊 UNIVERSAL MOD SQUAD EXECUTION TRACKER

**Standard Operating Procedure for ALL Projects**

This tracking matrix must be used for every project (PaiiD, WolfPackAI, future projects) to ensure consistent execution, agent accountability, and real-time progress visibility.

### Master Execution Matrix

| Phase       | Task                         | Agent             | Sub-Agent            | Extension/Tool     | Status     | Progress | Start    | End      | Duration | Output/Deliverable    |
| ----------- | ---------------------------- | ----------------- | -------------------- | ------------------ | ---------- | -------- | -------- | -------- | -------- | --------------------- |
| **PHASE 1** | **Discovery & Assessment**   |                   |                      |                    | **Status** | **%**    | **Time** | **Time** | **Min**  | **Files**             |
| 1.1         | Read architecture files      | Dr. Cursor Claude | File Reader          | `read_file`        | ⏳          | 0%       | --       | --       | --       | Architecture map      |
| 1.2         | Extract configurations       | Dr. Cursor Claude | File Reader          | `read_file`        | ⏳          | 0%       | --       | --       | --       | Config inventory      |
| 1.3         | Identify health endpoints    | Dr. Cursor Claude | Code Analyzer        | `codebase_search`  | ⏳          | 0%       | --       | --       | --       | Endpoint list         |
| 1.4         | Document auth patterns       | Dr. Cursor Claude | File Reader          | `read_file`        | ⏳          | 0%       | --       | --       | --       | Auth documentation    |
| 1.5         | Review automation            | Dr. Cursor Claude | File Reader          | `read_file`        | ⏳          | 0%       | --       | --       | --       | CI/CD analysis        |
| 1.6         | Create mod-squad folder      | Dr. Cursor Claude | PowerShell Agent     | `run_terminal_cmd` | ⏳          | 0%       | --       | --       | --       | `docs/mod-squad/`     |
| 1.7         | Write ASSESSMENT.md          | Dr. Cursor Claude | File Writer          | `write`            | ⏳          | 0%       | --       | --       | --       | Assessment doc        |
| 1.8         | Write PROGRESS.md            | Dr. Cursor Claude | File Writer          | `write`            | ⏳          | 0%       | --       | --       | --       | Progress tracker      |
| **PHASE 2** | **MOD SQUAD Implementation** |                   |                      |                    | **Status** | **%**    | **Time** | **Time** | **Min**  | **Files**             |
| 2.1         | Create scripts/ directory    | Dr. Cursor Claude | PowerShell Agent     | `run_terminal_cmd` | ⏳          | 0%       | --       | --       | --       | `scripts/`            |
| 2.2         | Create reports/ directory    | Dr. Cursor Claude | PowerShell Agent     | `run_terminal_cmd` | ⏳          | 0%       | --       | --       | --       | `reports/`            |
| 2.3         | Write mod_squad.config.json  | Dr. Cursor Claude | File Writer          | `write`            | ⏳          | 0%       | --       | --       | --       | Config file           |
| 2.4         | Write health check script    | Dr. Cursor Claude | Python Developer     | `write`            | ⏳          | 0%       | --       | --       | --       | Health checker        |
| 2.5         | Write browser test script    | Dr. Cursor Claude | Python Developer     | `write`            | ⏳          | 0%       | --       | --       | --       | Browser tests         |
| 2.6         | Write repo audit script      | Dr. Cursor Claude | Python Developer     | `write`            | ⏳          | 0%       | --       | --       | --       | Repo scanner          |
| 2.7         | Create package.json          | Dr. Cursor Claude | File Writer          | `write`            | ⏳          | 0%       | --       | --       | --       | npm commands          |
| 2.8         | Create requirements.txt      | Dr. Cursor Claude | File Writer          | `write`            | ⏳          | 0%       | --       | --       | --       | Python deps           |
| 2.9         | Write CI workflow            | Dr. Cursor Claude | File Writer          | `write`            | ⏳          | 0%       | --       | --       | --       | GitHub Actions        |
| 2.10        | Configure pre-commit hook    | Dr. Cursor Claude | File Writer          | `write`            | ⏳          | 0%       | --       | --       | --       | Git hook              |
| 2.11        | Test mod:all command         | Dr. Cursor Claude | PowerShell Agent     | `run_terminal_cmd` | ⏳          | 0%       | --       | --       | --       | Validation            |
| **PHASE 3** | **Bootstrap Script**         |                   |                      |                    | **Status** | **%**    | **Time** | **Time** | **Min**  | **Files**             |
| 3.1         | Write bootstrap script       | Dr. Cursor Claude | PowerShell Developer | `write`            | ⏳          | 0%       | --       | --       | --       | `bootstrap.ps1`       |
| 3.2         | Write QUICKSTART.md          | Dr. Cursor Claude | File Writer          | `write`            | ⏳          | 0%       | --       | --       | --       | User guide            |
| 3.3         | Test fresh environment       | Dr. Cursor Claude | PowerShell Agent     | `run_terminal_cmd` | ⏳          | 0%       | --       | --       | --       | E2E validation        |
| **PHASE 4** | **Universal Template**       |                   |                      |                    | **Status** | **%**    | **Time** | **Time** | **Min**  | **Files**             |
| 4.1         | Create template structure    | Dr. Cursor Claude | File System Agent    | `write`            | ⏳          | 0%       | --       | --       | --       | Template folder       |
| 4.2         | Write generic health script  | Dr. Cursor Claude | Python Developer     | `write`            | ⏳          | 0%       | --       | --       | --       | Template script       |
| 4.3         | Write generic browser script | Dr. Cursor Claude | Python Developer     | `write`            | ⏳          | 0%       | --       | --       | --       | Template script       |
| 4.4         | Write generic audit script   | Dr. Cursor Claude | Python Developer     | `write`            | ⏳          | 0%       | --       | --       | --       | Template script       |
| 4.5         | Write application wizard     | Dr. Cursor Claude | PowerShell Developer | `write`            | ⏳          | 0%       | --       | --       | --       | `apply_mod_squad.ps1` |
| 4.6         | Write TEMPLATE_GUIDE.md      | Dr. Cursor Claude | File Writer          | `write`            | ⏳          | 0%       | --       | --       | --       | Application docs      |
| 4.7         | Write config template        | Dr. Cursor Claude | File Writer          | `write`            | ⏳          | 0%       | --       | --       | --       | Template config       |

### Agent & Extension Deployment Matrix

| Agent/Sub-Agent/Extension      | Type              | Status | Phase 1  | Phase 2   | Phase 3  | Phase 4   | Total Invocations |
| ------------------------------ | ----------------- | ------ | -------- | --------- | -------- | --------- | ----------------- |
| **Dr. Cursor Claude**          | Primary AI Agent  | ⏳      | 8 tasks  | 11 tasks  | 3 tasks  | 7 tasks   | **29 tasks**      |
| ├─ **File Reader Sub-Agent**   | Read operations   | ⏳      | 5 reads  | 0         | 0        | 0         | **5 reads**       |
| ├─ **File Writer Sub-Agent**   | Write operations  | ⏳      | 2 writes | 7 writes  | 2 writes | 7 writes  | **18 writes**     |
| ├─ **Python Developer**        | Script creation   | ⏳      | 0        | 3 scripts | 0        | 3 scripts | **6 scripts**     |
| ├─ **PowerShell Developer**    | Script creation   | ⏳      | 0        | 0         | 1 script | 1 script  | **2 scripts**     |
| ├─ **PowerShell Agent**        | Command execution | ⏳      | 1 cmd    | 3 cmds    | 1 cmd    | 0         | **5 commands**    |
| └─ **Directory Scanner**       | List operations   | ⏳      | 2 lists  | 0         | 0        | 0         | **2 lists**       |
| **read_file Extension**        | File I/O          | ⏳      | 5 calls  | 0         | 0        | 0         | **5 calls**       |
| **write Extension**            | File I/O          | ⏳      | 2 calls  | 7 calls   | 2 calls  | 7 calls   | **18 calls**      |
| **run_terminal_cmd Extension** | Shell execution   | ⏳      | 1 call   | 3 calls   | 1 call   | 0         | **5 calls**       |
| **list_dir Extension**         | Directory ops     | ⏳      | 2 calls  | 0         | 0        | 0         | **2 calls**       |
| **codebase_search Extension**  | Code analysis     | ⏳      | 1 call   | 0         | 0        | 0         | **1 call**        |
| **Git Extension**              | Version control   | ⏳      | 0        | 0         | 1 call   | 0         | **1 call**        |
| **Python Runtime**             | Script testing    | ⏳      | 0        | 1 test    | 1 test   | 1 test    | **3 tests**       |
| **npm Runtime**                | Package mgmt      | ⏳      | 0        | 1 test    | 0        | 0         | **1 test**        |
| **Playwright Engine**          | Browser testing   | ⏳      | 0        | 1 test    | 0        | 0         | **1 test**        |

### Status Legend
- ⏳ **PENDING** - Not started
- 🟡 **IN PROGRESS** - Currently executing
- ✅ **COMPLETE** - Successfully finished
- 🔴 **FAILED** - Error occurred
- ⏭️ **SKIPPED** - Intentionally bypassed

### Usage Instructions

1. **Start of Project:** Copy this table to project-specific `docs/mod-squad/PROGRESS.md`
2. **During Execution:** Update status, times, and progress in real-time
3. **Agent Accountability:** Each agent/sub-agent must log their activity
4. **Extension Tracking:** Count every tool invocation for metrics
5. **End of Phase:** Verify all tasks marked ✅ before proceeding
6. **Post-Execution:** Archive final table in `docs/mod-squad/EXECUTION_REPORT.md`

### Required Metrics
- **Overall Progress:** Sum of completed tasks / total tasks
- **Phase Progress:** Per-phase completion percentage
- **Agent Efficiency:** Actual time vs estimated time
- **Extension Usage:** Tool invocation counts
- **Blocker Tracking:** Any status that remains 🟡 > 15 minutes

**This tracker is MANDATORY for all MOD SQUAD operations across all Dr. SC Prime projects.**

