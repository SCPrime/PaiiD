# Develop Efficient Task Workflow Plan

**Version:** 2025-10-22  
**Operating Model:** GENIUS ACCELLERATOR sequencing  
**Supporting Docs:** `PLAN_NEXT_STEPS.md`, `MASTER_BATCH_TASK_LIST.md`, `PHASE_1-6_FIXES.md`, `TODO.md`

---

## 1. Workflow Principles
- **Focus on Blockers First:** Physical device testing + options endpoint debug trump new feature work.  
- **Time-boxed Execution:** Treat each GENIUS stage as a discrete micro-sprint; avoid context switching mid-stage.  
- **Single Source Alignment:** Every update must reconcile with `TODO.md` to prevent drift.

---

## 2. GENIUS ACCELLERATOR Workflow Map
| Stage | Primary Owner | Inputs | Outputs | Tooling |
|-------|----------------|--------|---------|---------|
| **G**ather | Ops/QA | Render dashboards, Sentry (post-DSN), QA runbooks | Daily health snapshot | `DUAL_AI_MONITORING_WORKFLOW.md`, `instructions/13-monitoring-maintenance.md` |
| **E**valuate | Product/Tech Lead | Health snapshot, bug reports | Prioritized task list | `ANALYZE_PROJECT_COMPLETION.md` |
| **N**ormalize | Project Ops | Prioritized list | Updated `TODO.md`, `MASTER_BATCH_TASK_LIST.md` | Git + docs |
| **I**mplement | Engineering | Assigned tasks | Code changes, verified fixes | Local env, debugger, tests |
| **U**pdate | Comms Lead | Implementation notes | Slack + Notion posts | `COMMUNICATION_UPDATES_2025-10-22.md` |
| **S**tandardize | QA Lead | Fix validation, monitoring hooks | SOP updates, regression suites | `BUG_REPORT_OPTIONS_500.md`, `instructions/12-testing-framework.md` |

---

## 3. Weekly Rhythm
- **Monday:** GENIUS reset meeting (G→E stages) to capture new telemetry + reassess blockers.  
- **Tuesday–Thursday:** Focused implementation blocks (I stage) with daily updates (U stage).  
- **Friday:** Standardization review (S stage) ensuring QA + monitoring assets updated.

---

## 4. Toolchain & Automation Hooks
- **Monitoring:** Leverage Grafana/Render dashboards described in `instructions/13-monitoring-maintenance.md`; ensure alerts route to Slack.  
- **QA Automation:** Follow `instructions/12-testing-framework.md` for regression runs; expand Playwright coverage once options endpoint fixed.  
- **Documentation:** Refresh `PHASE_1-6_FIXES.md` and `MASTER_BATCH_TASK_LIST.md` after each batch cycle.  
- **Ticketing:** Mirror GENIUS stages in issue tracker tags (`Gather`, `Evaluate`, etc.) for quick filtering.

---

## 5. Success Metrics
- **MVP Closure:** Device testing signed off + endpoint fix merged.  
- **Signal Latency:** Monitoring alerts acknowledged within 15 minutes of trigger.  
- **Documentation Freshness:** Key planning docs updated within 12 hours of any status change.  
- **Cycle Time:** Each GENIUS loop <= 3 working days for high-priority issues.

