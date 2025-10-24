# Master Batch Task List

**Scope:** Consolidated schedule for Batches 1–4 plus residual backlog.  
**Updated:** 2025-10-22  
**Source of Truth:** `TODO.md` (Phase gating) & `PHASE_1-6_FIXES.md` (status narrative).

---

## 🔢 Batch Ledger

| Batch | Target Window | Objectives | Key Deliverables | Status |
|-------|---------------|------------|------------------|--------|
| 1 | Oct 18–19 | Rebaseline MVP stability | ✅ SSE production verification<br>✅ Render smoke test confirmation | Complete |
| 2 | Oct 20 | Harden telemetry & logging | ✅ Sentry SDK wiring<br>⚠️ DSN secret pending Render update | Complete (Follow-up) |
| 3 | Oct 21 | Options trading scaffolding | ⚠️ `/api/expirations/{symbol}` 500 bug report filed<br>✅ Radial menu integration smoke test | In Progress (bug fix) |
| 4 | Oct 22 | Mobile readiness audit | ⚠️ Physical device validation blocked<br>✅ Mobile export script review | Blocked (await hardware) |

---

## 📆 Forward-Looking Backlog

### Immediate (Aligned to `TODO.md` In-Progress)
1. **Physical Device Testing**  
   - Tasks: `Test chart export on mobile`, `Mobile device testing (iPhone + Android)`  
   - Owner: Hardware QA support  
   - Dependency: Device access  
   - Related Batch: 4  
2. **Options Endpoint Remediation**  
   - Task: Resolve 500 error on `/api/expirations/{symbol}`  
   - Owner: Backend engineer  
   - Dependency: Debug session (pdb)  
   - Related Batch: 3  

### Near-Term (Next in Queue from `TODO.md`)
- **Phase 1 Buildout:** Options chain data hydration, Greeks calculations, trade execution flow, RadialMenu wiring.  
- **Phase 2 Prep:** Strategy backtesting enhancements & ML hook-in (blocked until Phase 1 done).  
- **Scheduler UI Integration:** Can proceed in parallel; ensure it does not distract from MVP closure.

### Deferred (Post Phase 0–4)
- Roadmap initiatives listed under `TODO.md` → `ROADMAP.md` (80-day plan). Maintain as read-only until MVP + Phase 1 complete.

---

## 🧠 GENIUS ACCELLERATOR Sequence Application
Every batch update now carries a GENIUS ACCELLERATOR tag:

| Sequence Step | Description | Current Focus |
|---------------|-------------|----------------|
| **G**ather | Collect monitoring + QA data | Bug reproduction logs, Render dashboard exports |
| **E**valuate | Determine priority vs. roadmap | MVP blockers outrank Phase 1+ work |
| **N**ormalize | Sync backlog with `TODO.md` | Updated in this master list & phase fixes doc |
| **I**mplement | Execute scoped fixes | Batch 3 debugging session (pending) |
| **U**pdate | Communicate status | See Slack/Notion templates in `COMMUNICATION_UPDATES_2025-10-22.md` |
| **S**tandardize | Codify QA + monitoring handoffs | References embedded in bug report SOP cross-links |

---

## 🔁 Review Rhythm
- **Daily:** Reconcile Batch board vs. `TODO.md` before stand-up.  
- **Weekly:** Confirm DSN secret + device access progress.  
- **Phase Gate:** Do not advance to Phase 1 development until Batch 3 & 4 blockers are cleared.

