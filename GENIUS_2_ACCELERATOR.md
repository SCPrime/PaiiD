# GENIUS 2 ACCELLERATOR

## Purpose
GENIUS 2 ACCELLERATOR organizes the most urgent PaiiD engineering work into sequenced batches so the team can finish Phase 0, harden production services, and unlock Phase 1 delivery without reintroducing legacy issues. The plan connects each batch to concrete production outcomes, ensuring defunct code is removed only when replacements are ready and that critical verification steps are captured alongside the implementation guidance.

## Contents
1. Purpose and guiding principles
2. Batched workflow overview (Batches A–D)
3. Before & after impact summary
4. Follow-up actions for branch management and PR hygiene
5. Updated delivery timeline

## Batched Workflow Overview
### Batch A – MVP Validation & Production Hardening
* Validate MVP behaviour on physical mobile devices and record findings in the shared QA log.
* Standardize FastAPI error handling across core routers (`positions`, `proposals`, `telemetry`, `users`, `scheduler`).
* Replace the stubbed `greeks.py` import with the production `options_greeks.py` implementation in `position_tracker`.
* Remove dormant Alpaca fallbacks while tightening `tradier_client.py` and `position_tracker.py` around live Tradier calls.
* Centralize orders router credentials in the settings module and enforce non-default `JWT_SECRET_KEY` validation.
* Connect `MarketScanner.tsx` and `Backtesting.tsx` to real backend APIs, adding loading and error states aligned with the design system.

### Batch B – API Contract & Security Alignment
* Expand the proxy route validator to accept templated parameters while preserving the allow-list model.
* Migrate every FastAPI router to the canonical JWT `get_current_user` dependency in place of legacy bearer checks.
* Add integration tests that exercise secured endpoints with JWT tokens.
* Smoke-test proxy calls from the frontend (quotes, options chain, news, AI analysis) to confirm successful responses.

### Batch C – Phase 1 Options Trading Enablement
* Extend the Tradier (or Alpaca, if required) service to deliver options chain and Greeks data suitable for trading flows.
* Introduce option order placement endpoints with full validation and logging.
* Integrate backend capabilities into the frontend radial-menu flows, including UI wedges, forms, and success/error feedback.
* Validate sandbox paper-trading execution end-to-end and document outcomes in `LAUNCH_READINESS.md`.

### Batch D – Scheduler UX & Parallel Enhancements
* Surface scheduler navigation within the radial menu with responsive states consistent with existing wedges.
* Build out the scheduler approval workflow UI to expose create/edit/cancel interactions with validation.
* Implement automated tests that cover the frontend-to-backend scheduler round trip.
* Update `SCHEDULER_DEPLOYMENT_GUIDE.md` and log production verification steps in `TEST_RESULTS.md`.

## Before & After Impact
*Before:* Inconsistent authentication, dormant integrations, mock data dependencies, and incomplete mobile checks create reliability gaps and hide finished capabilities such as the scheduler.

*After:* Once the batches land, the platform achieves end-to-end JWT enforcement, resilient error handling, production data sources, verified mobile behaviour, and exposed scheduler and options trading workflows—accelerating the roadmap while reducing regression risk.

## Follow-up Actions
* Review local branches for completed Phase 0 subtasks (SSE verification, Sentry DSN setup, recommendation history tracking) that still require PRs. Create topic branches, execute relevant test suites, and publish PRs with summarized validation steps.
* Maintain one branch per batch to keep reviews focused and to ensure sequential delivery of the GENIUS 2 ACCELLERATOR milestones.

## Timeline Update
* **Remaining MVP closure (Batch A focus):** ~1.5 engineering days with mobile validation as the critical path.
* **API/security alignment (Batch B):** ~1 day immediately after Batch A to remove integration blockers.
* **Options trading foundation (Batch C):** 2–3 days depending on Tradier/Alpaca integration needs and UI wiring.
* **Scheduler UX uplift (Batch D):** 1–1.5 days, can begin in parallel once Batch A is underway.
* **Overall delivery window:** Approximately 5–6 working days to complete GENIUS 2 ACCELLERATOR with contingency for device access and sandbox verification.
