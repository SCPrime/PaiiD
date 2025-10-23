# Master BATCH Task List — Unified Execution Plan (October 23, 2025)

## 📌 Scope & Context
- This plan consolidates every workstream touched during the last 48 hours of FastAPI 500 recovery and `verify_config.py` ("V.PY") validation efforts, spanning backend fixes, frontend proxy alignment, automated testing, monitoring, and launch readiness updates. Evidence of the 500 failure and remediation history is documented in `BUG_REPORT_OPTIONS_500.md` and `KNOWN_ISSUES.md`, while the options platform has now been confirmed operational end-to-end.【F:BUG_REPORT_OPTIONS_500.md†L1-L90】【F:KNOWN_ISSUES.md†L3-L53】【F:OPTIONS_TRADING_COMPLETE.md†L1-L190】
- Additional dependencies (e.g., `psutil` for health monitoring) and configuration safeguards (`verify_config.py`) must be incorporated before declaring the PaiiD launch-ready state. Refer to `backend/requirements.txt` and `backend/verify_config.py` for the updated tooling expectations.【F:backend/requirements.txt†L1-L47】【F:backend/verify_config.py†L1-L116】
- Outstanding MVP and launch blockers recorded in `TODO.md` and `PAIID_APP_STATE.md` are explicitly included so the resulting workflow finishes with all documentation synchronized.【F:TODO.md†L1-L114】【F:PAIID_APP_STATE.md†L1-L24】

---

## ✅ Master Batch Sequence (Version 3 — Unified Workflow)
Each stage is sequential and assumes the previous stage has been completed. Status markers (`[ ]` pending, `[~]` in progress, `[x]` done) should be updated as you execute.

1. **[ ] Workspace & Dependency Refresh**
   - Pull latest `work` branch, prune stale venv/node installs, and reinstall backend requirements to ensure `psutil` is available for monitoring hooks.【F:backend/requirements.txt†L1-L47】
   - Confirm `.env` and `.env.local` files exist per configuration checklist (see Stage 3 for verification).【F:API_CONFIGURATION_COMPLETE.md†L8-L129】

2. **[ ] Kill Residual Uvicorn Processes & Reset Ports**
   - Use Task Manager/`Get-Process`/`lsof` to terminate any listeners on ports 8001-8002 (zombie processes were the confirmed root cause for the intermittent 500s).【F:CLEANUP_AUDIT_REPORT.md†L170-L184】
   - Document the reset in an ops log entry (include PID list) before moving forward.

3. **[ ] Verify Configuration & Secrets**
   - From `backend/`, run `python verify_config.py` and resolve any `[FAIL]` entries before proceeding.【F:backend/verify_config.py†L34-L111】
   - Capture the masked output and store it in the day’s audit notes (`PRODUCTION_DEPLOYMENT_GUIDE.md` or launch tracker).

4. **[ ] Launch Backend Cleanly**
   - Start FastAPI on port 8001 using `uvicorn app.main:app --reload --port 8001`, ensuring only a single PID binds to the port (log PID + timestamp).【F:API_CONFIGURATION_COMPLETE.md†L61-L108】【F:CLEANUP_AUDIT_REPORT.md†L186-L214】
   - Tail logs to confirm the options router is registered and no immediate errors surface.

5. **[ ] Smoke-Test Critical Options Endpoints**
   - Run the canonical curl checks for expirations, chain, and Greeks to validate that the 500 regression is gone and data quality (Greeks, IV, open interest) matches expectations.【F:OPTIONS_TRADING_COMPLETE.md†L11-L189】
   - Archive raw responses for SPY + OPTT into `TEST_RESULTS.md` for traceability.

6. **[ ] Frontend Proxy & UI Verification**
   - Confirm proxy routes and ALLOW_GET lists still include the options endpoints, then open the Options Trading wedge to validate dropdowns, filters, and Greeks rendering.【F:OPTIONS_TRADING_COMPLETE.md†L35-L198】
   - Note any UI regressions (especially mobile/responsive quirks) for later UX passes.

7. **[ ] Automated Test Execution**
   - Backend: execute targeted pytest suite (`pytest backend/tests/test_api_endpoints.py::TestOptions` etc.) if time permits.
   - Frontend: run `npx playwright test` (headless) and rerun flaky specs with trace viewer as needed; Playwright coverage enumerated in `MCP_SETUP_COMPLETE.md` sets the required assertions.【F:MCP_SETUP_COMPLETE.md†L36-L88】
   - Thunder Client: fire the prepared requests (expirations/chain via proxy and direct) to double-check manual test coverage.【F:MCP_SETUP_COMPLETE.md†L69-L88】

8. **[ ] Monitoring & Logging Hardening**
   - Hook `psutil` metrics into the startup monitor or health endpoint (if not already) to prevent silent regressions, aligning with the zombie-process lessons learned.【F:backend/requirements.txt†L1-L47】【F:DEPLOYMENT_VERIFICATION.md†L60-L104】
   - Schedule recurring checks (cron/task scheduler) to alert on multi-PID port listeners.

9. **[ ] Documentation & Knowledge Capture**
   - Update `TEST_RESULTS.md`, `LAUNCH_READINESS.md`, and `PAIID_APP_STATE.md` with the day’s outcomes and any newly closed blockers.【F:TODO.md†L1-L114】【F:PAIID_APP_STATE.md†L1-L24】
   - Ensure `BUG_REPORT_OPTIONS_500.md` and `KNOWN_ISSUES.md` reflect the resolution, leaving breadcrumbs for future incident reviews.【F:BUG_REPORT_OPTIONS_500.md†L1-L117】【F:KNOWN_ISSUES.md†L3-L53】

10. **[ ] Launch Readiness Gate**
    - Reconcile remaining MVP blockers (mobile testing & chart export) and mark owners/timelines so the launch decision is data-backed.【F:TODO.md†L21-L69】
    - Capture final sign-off in `PAIID_APP_STATE.md` and `LAUNCH_READINESS.md`.

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
| Plan | Primary Focus | Strengths | Gaps Addressed by V3 | Launch Impact |
|------|---------------|-----------|----------------------|---------------|
| **Version 1** | Rapid recovery & validation | Fast to execute; ensured backend restarts weren’t hitting zombie PIDs. | Lacked monitoring, documentation updates, and linkage to launch trackers. | Short-term stability only. |
| **Version 2** | Process hardening & monitoring | Added monitoring/log rotation and proxy verification routines. | Still omitted config verification, explicit documentation closure, and MVP blocker tracking. | Improved reliability but didn’t tie directly to launch checklist. |
| **Version 3 (Current)** | End-to-end execution (tech + ops) | Integrates environment cleanup, config checks, automated tests, monitoring, and documentation updates in one run. | — | Positions PaiiD for launch readiness sign-off with traceable evidence. |

---

## 📒 Reporting & Ownership Notes
- Update status markers in this file at the end of each work session and commit with message `docs: update master batch checklist` for traceability.
- Mirror the completion states in `LAUNCH_READINESS.md` and `PAIID_APP_STATE.md` so leadership dashboards reflect the live state of the FastAPI fix and test coverage.【F:PAIID_APP_STATE.md†L1-L24】【F:TODO.md†L1-L114】
- Archive curl/Playwright artifacts in `TEST_RESULTS.md` after each batch run; they form the evidence pack for the PaiiD launch go/no-go review.【F:MCP_SETUP_COMPLETE.md†L48-L88】
