# Genius Accelerator 2 – Strategic Execution Refresh (October 2025)

## Objective
Align the Genius Accelerator initiative with the refreshed strategic batch plan so product, engineering, and AI operations move in lockstep through the remaining MVP milestones.

## Current Standing
- **Overall Completion:** ~70% of long-range roadmap; Phase 0 Preparation at 94% complete.
- **Critical Blockers:**
  - Options expiration endpoint regression preventing full options workflow.
  - Pending infrastructure chores (Render Redis verification, Sentry DSN configuration, Vercel SSO shutdown).
- **Quality Posture:** Post-incident guardrails (import tests, pre-commit hooks, CI gates) active; Claude reviewer integration pending.

## Updated Accelerator Tracks
### Track A – Reliability Surge (Batches 1 & 2)
- Execute Batch 1 backend fixes to restore options routing and add regression tests.
- Run Batch 2 infrastructure hardening to remove deployment blockers and finalize observability.
- **Milestone:** Declare production backend + deployment pipeline green, enabling options feature sign-off.

### Track B – Experience Elevation (Batch 3)
- Deliver workflow polish (order templates, shortcuts, TradingView widget) with responsive QA.
- Integrate learnings from `MOBILE_AUDIT_REPORT.md` and capture before/after metrics.
- **Milestone:** Phase 5.A Quick Wins marked complete with validated mobile experience.

### Track C – Intelligence Amplification (Batch 4)
- Expand AI recommendations with traceable telemetry and historical logging.
- Surface history timeline in UI for compliance and user trust.
- **Milestone:** Recommendation engine ready for Phase 1 launch review.

## Claude-as-Gatekeeper Rollout
- Install and enforce Claude GitHub reviewer automation per `CLAUDE.md`.
- Tag critical directories (`backend/app/routers`, `frontend/pages`, `frontend/components`) in CODEOWNERS to ensure Claude coverage.
- Monitor initial PRs for reviewer noise; iterate instructions in `CLAUDE_PROTOCOL.md` for clarity.

## Success Metrics
- **Cycle Time:** <3 days per batch PR from open to merge after Claude adoption.
- **Regression Rate:** 0 escaped defects from options routing and deployment scripts after Batch 2.
- **AI Review Impact:** ≥80% of Claude-raised issues resolved before human review.

## Action Timeline
| Week | Focus | Key Deliverables |
|------|-------|------------------|
| Week 1 | Batch 1 execution | FastAPI routing fix, options test coverage, Claude reviewer enabled |
| Week 2 | Batch 2 execution | Render/Sentry verification docs updated, Vercel SSO disabled |
| Week 3 | Batch 3 execution | Order templates, shortcut manager, TradingView widget, mobile QA report |
| Week 4 | Batch 4 execution | AI recommendation logging, timeline UI, telemetry validation |

## Next Actions
1. Kick off Batch 1 investigation pairing backend lead with Claude-assisted debugging.
2. Configure GitHub Claude reviewer workflow and branch protections (see `CLAUDE.md`).
3. Update deployment and QA leads on cadence using `STRATEGIC_BATCH_PLAN.md` as the canonical reference.
