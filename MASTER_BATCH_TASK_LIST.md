# Master BATCH Task List — Unified Execution Plan (October 23, 2025)

## 📌 Scope & Context
- This plan consolidates every workstream touched during the last 48 hours of FastAPI 500 recovery and `verify_config.py` ("V.PY") validation efforts, spanning backend fixes, frontend proxy alignment, automated testing, monitoring, and launch readiness updates. Evidence of the 500 failure and remediation history is documented in `BUG_REPORT_OPTIONS_500.md` and `KNOWN_ISSUES.md`, while the options platform has now been confirmed operational end-to-end.【F:BUG_REPORT_OPTIONS_500.md†L1-L90】【F:KNOWN_ISSUES.md†L3-L53】【F:OPTIONS_TRADING_COMPLETE.md†L1-L190】
- Additional dependencies (e.g., `psutil` for health monitoring) and configuration safeguards (`verify_config.py`) must be incorporated before declaring the PaiiD launch-ready state. Refer to `backend/requirements.txt` and `backend/verify_config.py` for the updated tooling expectations.【F:backend/requirements.txt†L1-L47】【F:backend/verify_config.py†L1-L116】
- Outstanding MVP and launch blockers recorded in `TODO.md` and `PAIID_APP_STATE.md` are explicitly included so the resulting workflow finishes with all documentation synchronized.【F:TODO.md†L1-L114】【F:PAIID_APP_STATE.md†L1-L24】

---

## ✅ Master Batch Sequence (Version 3 — Unified Workflow)
Each batch is ordered for execution. Complete a batch before advancing to the next so environment state and evidence capture stay synchronized. Status markers (`[ ]` pending, `[~]` in progress, `[x]` done) should be updated at the batch level and for each task.

### 🟡 Batch 0 — Preflight Sync & Safety Net
- **[ ] Refresh workspace dependencies**
  - Pull the latest `work` branch, remove stale virtualenv/node modules, and reinstall backend requirements to ensure `psutil` and monitoring dependencies are available.【F:backend/requirements.txt†L1-L47】
- **[ ] Validate secret files are present**
  - Confirm `.env` / `.env.local` align with the configuration checklist prior to starting the services.【F:API_CONFIGURATION_COMPLETE.md†L8-L129】

### 🔴 Batch 1 — Environment Reset & Port Hygiene
- **[ ] Kill residual Uvicorn processes**
  - Use Task Manager/`Get-Process`/`lsof` to terminate listeners on ports 8001-8002 (duplicate listeners were the confirmed root cause for the intermittent 500s).【F:CLEANUP_AUDIT_REPORT.md†L170-L214】
- **[ ] Log the cleanup**
  - Record PID, timestamp, and operator in the ops journal to preserve traceability for the audit trail.

### 🟠 Batch 2 — Configuration Assurance
- **[ ] Run `verify_config.py`**
  - From `backend/`, execute `python verify_config.py`; remediate any `[FAIL]` entries before proceeding.【F:backend/verify_config.py†L34-L111】
- **[ ] Archive verification output**
  - Mask sensitive fields and attach the results to the day’s deployment notes (`PRODUCTION_DEPLOYMENT_GUIDE.md` or launch tracker).

### 🟢 Batch 3 — Backend Launch & Live Validation
- **[ ] Start FastAPI cleanly**
  - Launch with `uvicorn app.main:app --reload --port 8001`, ensuring only a single PID binds to the port and capturing PID + timestamp in the log.【F:API_CONFIGURATION_COMPLETE.md†L61-L108】【F:CLEANUP_AUDIT_REPORT.md†L186-L214】
- **[ ] Tail startup logs**
  - Confirm router registration and absence of immediate stack traces while services warm up.
- **[ ] Smoke-test options endpoints**
  - Run curl checks for expirations, chain, and Greeks; confirm the 500 regression is gone and Greeks/IV/open-interest data are populated.【F:OPTIONS_TRADING_COMPLETE.md†L11-L189】
- **[ ] Archive API responses**
  - Store raw outputs for SPY + OPTT in `TEST_RESULTS.md` so evidence persists with the launch package.【F:TEST_RESULTS.md†L1-L58】

### 🔵 Batch 4 — Frontend Proxy & UX Confirmation
- **[ ] Reconfirm proxy routes**
  - Verify Vite proxy/`ALLOW_GET` entries include `/api/options/chain` and `/api/options/expirations` to match the backend routes.【F:OPTIONS_TRADING_COMPLETE.md†L35-L198】
- **[ ] Manual UI walkthrough**
  - Exercise the Options Trading wedge, checking dropdowns, filters, and Greeks rendering on desktop and mobile breakpoints; log observations for follow-up tickets.

### 🟣 Batch 5 — Automated Test Battery
- **[ ] Backend targeted pytest**
  - Run `pytest backend/tests/test_api_endpoints.py::TestOptions` (and adjacent suites if time) to validate service-level contracts.
- **[ ] Playwright regression run**
  - Execute `npx playwright test` and re-run any flaky specs with trace viewer; success criteria come from the MCP automation checklist.【F:MCP_SETUP_COMPLETE.md†L36-L88】
- **[ ] Thunder Client/API client validation**
  - Trigger saved requests for expirations/chain via proxy and direct FastAPI endpoints to confirm manual coverage stays in sync.【F:MCP_SETUP_COMPLETE.md†L69-L88】

### 🟤 Batch 6 — Monitoring & Logging Hardening
- **[ ] Wire psutil/system metrics**
  - Add `psutil`-based health checks or port guard scripts so multi-PID listeners raise alerts automatically.【F:backend/requirements.txt†L1-L47】【F:DEPLOYMENT_VERIFICATION.md†L60-L104】
- **[ ] Schedule recurring hygiene checks**
  - Configure cron/task scheduler jobs to run port scans and notify the ops channel when conflicts appear.
- **[ ] Improve log retention**
  - Ensure backend logs rotate and remain accessible for failure correlation during future incident reviews.

### ⚫ Batch 7 — Documentation, Communication & Launch Gate
- **[ ] Update operational records**
  - Sync `TEST_RESULTS.md`, `LAUNCH_READINESS.md`, and `PAIID_APP_STATE.md` with the day’s findings and any blockers closed.【F:TEST_RESULTS.md†L1-L58】【F:PAIID_APP_STATE.md†L1-L24】
- **[ ] Close out incident narrative**
  - Reflect the resolution in `BUG_REPORT_OPTIONS_500.md` and `KNOWN_ISSUES.md`, leaving breadcrumbs for future audits.【F:BUG_REPORT_OPTIONS_500.md†L1-L117】【F:KNOWN_ISSUES.md†L3-L53】
- **[ ] Launch readiness checkpoint**
  - Reconcile remaining MVP blockers (mobile testing, chart export, etc.), assign owners/timelines, and record the sign-off decision in `PAIID_APP_STATE.md` and `LAUNCH_READINESS.md`.【F:TODO.md†L21-L69】【F:PAIID_APP_STATE.md†L1-L24】

---

## 🕰 Historical Master BATCH Task Lists (Reconstructed)
These references capture the two prior batches you started so progress can be tracked alongside the new unified sequence.

### Version 1 — Immediate Recovery Sequence (Oct 22, 2025)
1. **Kill zombie Uvicorn processes** before every test run.
2. **Start a fresh backend instance** on a clean port (8001/8002) once the system is clear.
3. **Run Playwright + API curl tests** to prove stability post-restart.

### Version 2 — Process Hardening Sequence (Oct 22, 2025)
1. Stabilize backend environment by clearing zombie Uvicorn processes before every run.
2. Launch the backend cleanly and lock the service to a predictable port.
3. Verify backend health with diagnostics before client traffic.
4. Run full end-to-end Playwright suite after backend validation.
5. Re-enable frontend proxy and ensure ALLOW_GET paths remain synchronized.
6. Implement continuous monitoring to prevent recurrence of multi-process conflicts.
7. Automate log rotation and retention for easier debugging.
8. Document the stabilized workflow and train the team.
9. Track completion and readiness for PaiiD launch.

---

## 🔍 Comparison Matrix
| Plan | Primary Focus | Benefits (+) | Limitations (−) | Launch Impact |
|------|---------------|--------------|-----------------|---------------|
| **Version 1** | Rapid recovery & validation | Fastest path to prove options endpoint stability after restarts. | No monitoring, limited documentation, no linkage to launch trackers. | Short-term stability only; recurring regressions likely. |
| **Version 2** | Process hardening & monitoring | Introduced monitoring/log rotation and proxy verification routines. | Still missing config verification, evidence capture, and MVP blocker alignment. | Better reliability but still disconnected from launch governance. |
| **Version 3 (Current)** | End-to-end execution (tech + ops) | Unifies cleanup, configuration checks, automated tests, monitoring, and documentation in one batched flow. | Requires disciplined execution time (~90–120 min) and cross-team coordination. | Positions PaiiD for launch readiness sign-off with auditable evidence. |

---

## 📒 Reporting & Ownership Notes
- Update status markers in this file at the end of each work session and commit with message `docs: update master batch checklist` for traceability.
- Mirror the completion states in `LAUNCH_READINESS.md` and `PAIID_APP_STATE.md` so leadership dashboards reflect the live state of the FastAPI fix and test coverage.【F:PAIID_APP_STATE.md†L1-L24】【F:TODO.md†L1-L114】
- Archive curl/Playwright artifacts in `TEST_RESULTS.md` after each batch run; they form the evidence pack for the PaiiD launch go/no-go review.【F:MCP_SETUP_COMPLETE.md†L48-L88】
