# Strategic Batch Delivery Plan (October 2025 Refresh)

## Purpose
This plan re-evaluates the PaiiD repository after the October remediation work and restructures delivery into clearly bounded batches. Each batch groups tightly-related fixes and enhancements so that QA, release management, and AI reviewer automation (Claude) can execute with predictable velocity.

## Guiding Principles
1. **Stability First** – Resolve production-affecting defects and infrastructure gaps before unlocking new functionality.
2. **AI-Assisted Review** – Require Claude GitHub Actions to participate in every PR touching critical paths (backend routing, deployment automation, authentication) to accelerate root-cause detection.
3. **Tight Feedback Loops** – Keep each batch <= 3 deployable PRs with automated smoke coverage plus clearly-defined manual sign-off steps.
4. **Documentation Parity** – Update runbooks and status dashboards inside the repo as part of each batch to prevent knowledge drift.

## Batch 1 – Backend Reliability & Options Routing (Target: 2 PRs)
- **Goals**
  - Repair `/api/expirations/{symbol}` routing so FastAPI surfaces options expirations.
  - Harden backend router registration (import guards, middleware ordering tests).
- **Key Tasks**
  - Instrument FastAPI routing table and trace middleware (PR #1).
  - Implement regression tests in `backend/tests/test_options_endpoint.py` and ensure CI executes them (PR #2).
- **Readiness Gates**
  - CI: `pytest backend/tests/test_options_endpoint.py`.
  - Manual: Options expiration dropdown populates in `frontend/components/OptionsChain.tsx` via staging deployment.
  - Claude Review: Require "blocking" Claude check on both PRs.

## Batch 2 – Deployment & Observability Hardening (Target: 3 PRs)
- **Goals**
  - Finalize Render + Redis + Sentry verification.
  - Disable Vercel SSO and document the irreversible cut-over.
- **Key Tasks**
  - Infrastructure validation script updates in `monitor-production.sh` and `test-deployment.sh` (PR #3).
  - Dashboard updates in `DEPLOYMENT_STATUS.md` and `STATE_OF_AFFAIRS_REPORT.md` (PR #4).
  - Configure Sentry DSN secrets and update `backend/app/core/settings.py` (PR #5).
- **Readiness Gates**
  - CI: `./test-deployment.sh` (smoke) must pass.
  - Manual: Ops to capture screenshots of Sentry + Render dashboards.
  - Claude Review: Required for PRs #3 and #5.

## Batch 3 – Phase 5.A Workflow Enhancements (Target: 3 PRs)
- **Goals**
  - Deliver order templates, keyboard shortcuts, and TradingView widget integration.
  - Polish responsive layouts highlighted in `MOBILE_AUDIT_REPORT.md`.
- **Key Tasks**
  - Order template library in `frontend/components/orders/` (PR #6).
  - Shortcut manager in `frontend/utils/shortcuts.ts` with Jest coverage (PR #7).
  - TradingView widget embed + responsive refactor in `frontend/pages/index.tsx` (PR #8).
- **Readiness Gates**
  - CI: `npm run test:ci`.
  - Manual: Mobile Safari + Chrome DevTools responsive audit.
  - Claude Review: Required for PR #7 and #8.

## Batch 4 – AI Recommendation & Telemetry Uplift (Target: 2 PRs)
- **Goals**
  - Expand AI recommendation explanations with traceability hooks.
  - Log recommendation history for compliance.
- **Key Tasks**
  - Update `backend/app/routers/ai.py` to log structured recommendation payloads (PR #9).
  - Frontend timeline component in `frontend/components/AIRecommendations.tsx` (PR #10).
- **Readiness Gates**
  - CI: Backend unit tests + frontend snapshot tests.
  - Manual: Review new telemetry events in Redis/Sentry.
  - Claude Review: Required for both PRs.

## Batch Governance
- **Cadence** – Deliver sequentially; do not start Batch N+1 until Batch N passes smoke tests and documentation updates are merged.
- **Stakeholder Checkpoints** – Hold end-of-batch review using `PRODUCTION_DEPLOYMENT_GUIDE.md` checklist plus Claude-generated summary comment.
- **Metrics** – Track cycle time, escaped defects, and Claude reviewer findings for continuous improvement.

## Next Steps
1. Socialize this batch plan with engineering + ops leads.
2. Update `Genius Accelerator 2` roadmap to align milestones with batch sequencing.
3. Implement GitHub Claude integration (see updated `CLAUDE.md`).
