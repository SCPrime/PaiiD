# Genius Accelerator 2 Initiative

## Overview
The Genius Accelerator 2 initiative captures the follow-up improvements required to finalize
our automated pull-request workflow around trade candidate insights. The objective is to
translate the "best candidates" surfaced by the Morning Routine AI scanner into actionable,
tracked changes within both backend and frontend repositories.

## Candidate Pull Request Blueprint
The Morning Routine AI surfaces trade candidates that must be reflected across the stack. To
keep the repositories synchronized, each candidate batch should generate a coordinated set
of pull requests:

1. **Backend (FastAPI services)**
   - Extend `backend/app/routers/market_data.py` to persist the candidate snapshot returned by
     `/market-data/scanner`.
   - Document the payload contract in `API_DOCUMENTATION.md` and align the pydantic models used
     in `backend/strategies/under4_multileg.py`.
   - Add regression coverage that validates the serialized candidate list during async scanner
     execution.

2. **Frontend (Next.js dashboard)**
   - Update the candidate preview cards within `frontend/components/MorningRoutineAI.tsx` to
     highlight the batch timestamp and the risk notes returned by the backend.
   - Expand `frontend/lib/marketData.ts` with a helper that formats the candidate universe for
     the UI widgets and scheduler prompts.
   - Refresh Storybook entries (if available) so design stakeholders can approve the candidate
     layout before merge.

3. **Infrastructure & Documentation**
   - Mirror the new contracts in `API_DOCUMENTATION.md` and add a quick validation checklist to
     `DEPLOYMENT_CHECKLIST.md`.
   - Ensure the Render environment variables include the toggles required for batch candidate
     exports.

## Repository Update Flow
1. Capture the latest candidate batch output from the production or staging scanner.
2. Open paired pull requests (backend + frontend) using the blueprint above, referencing the
   candidate batch ID in the PR titles.
3. Run the existing test matrix (`pytest`, `npm test`, and Playwright smoke suite) before
   requesting reviews.
4. Merge once automated checks pass, then trigger the deployment workflow described in
   `DEPLOYMENT_RUNBOOK.md`.

## Tracking
- Record merged candidate PRs in `PR_FAILURE_ANALYSIS_REPORT_72H.md` to keep the audit trail up
  to date.
- Link Jira or Linear tickets directly in the PR descriptions for full traceability.

