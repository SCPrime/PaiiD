# MOD SQUAD Universal Protocol v2.0
**Status:** 🔒 PERMANENT M.O. FOR ALL PROJECTS  
**Applies To:** All Cursor workspaces, all repositories  
**Last Updated:** October 30, 2025

---

## Core Principles

1. **Multi-Agent Parallel Execution:** Default to 4-6 specialized agents working simultaneously on non-overlapping file paths
2. **Zero-Defect Deployment:** <0.5% defect escape rate via layered guardrails
3. **Minimal Human Intervention:** Dr. SC Prime approves outcomes, not implementation
4. **Economies of Scale:** Achieve 50-65% wall-clock time reduction through parallelization
5. **Continuous Integration:** 2-hour checkpoint cycles prevent integration drift

---

## Agent Orchestra Composition

### Tier 0 – Oversight

| Unit              | Role                                         | Notes                             |
| ----------------- | -------------------------------------------- | --------------------------------- |
| Meta-Orchestrator | Supreme control, risk governor (<0.5%)       | Non-authoring, immutable          |
| Ops Relay         | Aggregate telemetry, dashboards, ETA rollups | Feeds Dr. SC Prime + leadership   |
| Risk Sentinel     | SLA / guardrail breach monitor               | Escalates immediately on failures |

### Tier 1 – Primary Streams

| Agent      | Domain               | Core Scope                                 |
| ---------- | -------------------- | ------------------------------------------ |
| `Agent 1A` | Frontend Core        | UI backlog orchestration                   |
| `Agent 2A` | Security Ops         | Guardrails, secrets, penetration prep      |
| `Agent 3A` | Test Infrastructure  | Playwright, visual + regression pipelines  |
| `Agent 4A` | DevOps & CI          | Port policy, pipeline health, budgets      |
| `Agent 5A` | Release Prep         | Integration checkpoint → production runway |
| `Agent 6A` | Data & Observability | Live flow latency, execution analytics     |
| `Agent 7A` | Docs & Knowledge     | Runbooks, DNA guidelines, change logs      |
| `Agent 8A` | Customer Simulation  | Persona journeys, UX regressions           |

### Tier 2 – Sub-Agent Mesh (examples)

- **Frontend (1B–1L):** guardrail automation, glassmorphic refactors, archive audits, ticket routing, accessibility sweeps.
- **Security (2B–2H):** secrets sentinel, SBOM remediation, IAM diff reviews, SAST triage, threat intel listener.
- **Testing (3B–3K):** Playwright harness builder, visual baseline curator, mobile matrix, smoke auto-writer, accessibility narrators.
- **DevOps (4B–4G):** port compliance bot, pipeline guardian, infra drift detector, rollback rehearsal scripting, artifact verification.
- **Release & QA (R1–R4):** reviewer cluster for DNA compliance, security report validation, test evidence vetting, documentation audits (see Phase 6).

### Tier 3 – Extensions & Services

- Scheduled automation: `guardrail_scheduler`, `accessibility_scheduler`, `persona_simulator`, `data_latency_tracker` (UTC-aligned cadences).
- Compliance insights: `component_diff_reporter`, `security_patch_advisor`, `dependency_tracker` enriched with per-package work items.
- Knowledge & sync: `docs_sync`, `metrics_streamer`, `maintenance_notifier` keeping stakeholders informed.
- Review utilities: `review_aggregator`, `quality_inspector` collating findings for Ops Relay and Risk Sentinel.

### Scaling Rules (Updated)
- **Micro scope (<10 files):** 3 agents (1 primary + 2 focused subs) to maintain separation of duties.
- **Standard scope (10–50 files):** 6–8 agents across at least two tiers.
- **Large / critical scope (50+ files or prod readiness):** Full web (Tier 0–2) + reviewer mesh.
- **Emergency posture:** Risk Sentinel invokes override; Reviewer tier must sign-off before ship.

---

## File Ownership & Conflict Prevention

### Pre-Execution Phase
1. Orchestrator analyzes repository structure
2. Generates file ownership matrix (agent → exclusive paths)
3. Creates dependency graph (e.g., UI dashboard → backend API)
4. Publishes to `modsquad/logs/file-ownership.json`

### During Execution
1. Agent checks ownership registry before editing any file
2. If file owned by another agent, requests handoff from orchestrator
3. Orchestrator approves/denies based on dependency graph
4. If denied, agent queues task for later or proposes alternative approach

### Conflict Detection
- Git pre-commit hook runs `stream_coordinator.py`
- Checks for overlapping file edits across branches
- Auto-merges if zero conflicts, alerts orchestrator if conflicts detected
- Orchestrator resolves conflicts or reassigns work

---

## Continuous Integration Checkpoints

### 2-Hour Integration Cycle

**Every 2 hours during parallel execution:**

1. **Pause & Sync:** All agents pause and push to feature branches
2. **Integration Test:** Orchestrator merges all branches to `integration/staging`
3. **Validation Suite:**
   - Backend: pytest full suite + API contract tests (Dredd)
   - Frontend: Playwright E2E + axe-core accessibility + Lighthouse performance
   - Integration: End-to-end smoke tests (login → trade → view history)
4. **Pass/Fail Decision:**
   - ✅ All green → agents resume work
   - ❌ Any red → failing agent pauses, orchestrator debugs, work reassigned
5. **Artifact Logging:** Results dumped to `modsquad/logs/integration-checkpoint-TIMESTAMP.json`

---

## Quality Guardrails (Layered Defense)

### Layer 1: Pre-Commit (Local)
- Design DNA validator (`design-dna-validator.py`)
- ESLint + Prettier (code style)
- TypeScript type check (no `any` types)
- Unit tests for modified files

### Layer 2: CI/CD (GitHub Actions)
- Full test suite (pytest + Playwright)
- Percy visual regression (frontend)
- axe-core accessibility scan (score ≥90%)
- Lighthouse performance (score ≥85%)
- Dredd API contract validation
- Bundle size check (max +10% increase)

### Layer 3: Integration Checkpoints (Every 2h)
- Cross-stream smoke tests
- Dependency graph validation
- Performance profiling (no regressions)
- Security scan (OWASP checks)

### Layer 4: Pre-Production (Staging)
- Full E2E test suite (all user flows)
- Load testing (100 concurrent users)
- Sentry error monitoring (zero critical errors for 24h)
- Percy baseline approval (Dr. SC Prime clicks "Ship It")

### Layer 5: Production (Live Monitoring)
- Sentry real-time error tracking
- LogRocket session replay (10% sample)
- Lighthouse CI on every deployment
- Automated rollback if error rate >10/hour

**Defect Escape Rate:** <0.5% (target achieved via 5-layer defense)

---

## Time Efficiency Economies (Permanent Features)

### Economy Suite (Auto-Enabled)
1. **Shared Dependency Cache:** `node_modules`, `venv` cached after first install
2. **Incremental Builds:** TypeScript `.tsbuildinfo`, Webpack cache persist across agents
3. **Parallel Test Execution:** pytest-xdist (8 workers), Playwright (4 workers)
4. **Hot Module Replacement:** Dev servers stay warm during agent handoffs
5. **Smart Install Detection:** Hash-based check before `npm install` / `pip install`

**Time Savings:** 3-4 hours per project (15-20% reduction)

---

## Agent Coordination Protocol

### Communication Flow
1. **Agent → Orchestrator:** "Requesting ownership of `frontend/components/ExecuteTradeForm.tsx`"
2. **Orchestrator → Registry:** Checks file locks and dependency graph
3. **Orchestrator → Agent:** "Approved, proceed" OR "Denied, file locked by `claude-4.5-sonnet`"
4. **Agent → Orchestrator:** "Task complete, releasing lock"

### Dependency Sync Protocol
1. Backend agent modifies `/api/strategies/run` endpoint (adds new field)
2. `dependency_tracker.py` detects API contract change
3. Orchestrator alerts UI agent: "Backend modified your dependency, sync required"
4. UI agent pauses, pulls latest API schema, updates frontend types, resumes

### Conflict Resolution
1. Two agents accidentally edit same file (rare, but possible)
2. `stream_coordinator.py` detects conflict during checkpoint
3. Orchestrator reviews both changes:
   - If compatible → auto-merge
   - If incompatible → higher-priority agent wins, lower-priority agent refactors
4. Conflict logged to `modsquad/logs/conflict-resolution.jsonl`

---

## Activation & Deployment

### Project Initialization (Auto-Run at Cursor Launch)

**When Dr. SC Prime opens any project in Cursor:**

1. MOD SQUAD scans repo for `modsquad/` directory
2. If present → loads protocol and spawns orchestrator
3. Orchestrator analyzes TODO.md, open issues, recent commits
4. Proposes task breakdown with agent assignments
5. Dr. SC Prime reviews and says "EXECUTE NOW" (or modifies plan)

### Ongoing Operations (Every 8 Hours)

**Automated Maintenance Windows (3x daily):**

- **Window 1 (12:00 AM UTC):** Code quality sweep, dependency updates, security scans
- **Window 2 (08:00 AM UTC):** Performance profiling, cache optimization, log cleanup
- **Window 3 (04:00 PM UTC):** Documentation sync, test coverage audit, backup verification

**Extensions Run:** All enabled extensions (notifier, metrics, secrets, verifier, browser_validator, contract_enforcer, infra_health)

---

## Universal File Structure (All Projects)

```
project-root/
├── modsquad/
│   ├── PROTOCOL.md (this file)
│   ├── config/
│   │   ├── modsquad.yaml (agent settings, budgets)
│   │   ├── maintenance_schedule.yaml (8h windows)
│   │   ├── quality_gates.yaml (lint, tests, security)
│   │   ├── model_routing.yaml (task → agent mapping)
│   │   ├── extensions.yaml (notifier, metrics, etc.)
│   │   └── browser_guardrails.yaml (Percy, Lighthouse, axe)
│   ├── extensions/
│   │   ├── maintenance_notifier.py
│   │   ├── metrics_streamer.py
│   │   ├── secrets_watchdog.py
│   │   ├── strategy_verifier.py
│   │   ├── browser_validator.py (NEW)
│   │   ├── contract_enforcer.py (NEW)
│   │   ├── infra_health.py (NEW)
│   │   ├── stream_coordinator.py (NEW)
│   │   ├── integration_validator.py (NEW)
│   │   └── dependency_tracker.py (NEW)
│   ├── logs/
│   │   └── run-history/ (JSONL logs per extension)
│   ├── OPERATOR_RUNBOOK.md
│   └── EXEC_SUMMARY.md
├── frontend/
│   └── DESIGN_DNA.md (brand guidelines, auto-validated)
├── scripts/
│   ├── design-dna-validator.py
│   └── modsquad/ (after-maintenance scripts)
└── .github/
    └── workflows/ (CI/CD with MOD SQUAD gates)
```

---

## Permanent Guardrails (Auto-Enforced)

### Brand Compliance
- `design-dna-validator.py` runs pre-commit
- Blocks unapproved colors, spacing, patterns
- Enforces glassmorphic aesthetic

### Performance
- Lighthouse CI blocks deployment if score <85
- Bundle analyzer alerts if any chunk >500KB
- API response time monitored (target <200ms)

### Accessibility
- axe-core blocks commit if score <90%
- Touch targets enforced at 40x40px minimum
- Keyboard navigation required for all interactive elements

### Security
- OWASP Top 10 scanned weekly
- Secrets rotation enforced (30-day max age)
- Rate limiting per user + global

### Testing
- pytest coverage threshold 80% (blocks if dropped)
- Playwright E2E tests must pass (blocks deployment)
- API contract tests (Dredd) prevent drift

---

## Success Metrics (Tracked Automatically)

### Velocity Metrics
- **Tasks completed per 8h window** (target: 6-8 tasks)
- **Wall-clock time vs. sequential estimate** (target: 50-65% reduction)
- **Agent utilization rate** (target: >80% active time)

### Quality Metrics
- **Defect escape rate** (target: <0.5%)
- **Test coverage** (target: ≥90%)
- **Accessibility score** (target: ≥95%)
- **Performance score** (target: ≥90%)

### User Satisfaction Metrics
- **Dr. SC Prime approval rate** (target: >95% first-try)
- **Rollback frequency** (target: <1 per 50 deployments)
- **Time to production** (target: <3 days from feature request)

---

## Version History

- **v1.0 (Oct 24, 2025):** Initial MOD SQUAD protocol (single-agent)
- **v2.0 (Oct 30, 2025):** Multi-agent parallel execution, browser guardrails, universal deployment (this version)

---

**This protocol is now PERMANENT and UNIVERSAL across all Dr. SC Prime's projects.**

