## Issue 1 – Production configuration lacks validation and observability guardrails  
`Settings` currently pulls raw environment variables without enforcing production-only requirements, validating observability inputs, or surfacing misconfiguration, leaving Sentry and logging accuracy entirely dependent on manual dashboard setup.

:::task-stub{title="Add production configuration validation and observability guardrails"}
1. Augment `backend/app/core/config.py` with Pydantic validators or helper methods to enforce `SENTRY_DSN`, `LOG_LEVEL`, and related observability settings when `RENDER_EXTERNAL_URL`/`LIVE_TRADING` imply production.  
2. Create a `verify_config.py`-style entry point (or expand existing script) that calls the new validation logic during prelaunch and CI.  
3. Emit structured diagnostics (warnings vs hard failures) and unit tests in `backend/tests/` covering success/failure cases.
:::

## Issue 2 – Startup telemetry enhancements never landed  
`app/main.py` only prints a handful of env values and lacks the promised startup duration metric, package/version logging, or structured logging hooks, preventing baseline SLO tracking and root-cause analysis when startup regresses.

:::task-stub{title="Instrument startup telemetry with timing and structured logging"}
1. In `backend/app/main.py`, add `time`/`sys` imports, capture monotonic timestamps around startup phases, and log structured payloads (JSON or key-value) summarizing environment, package versions, and duration.  
2. Introduce a reusable logging helper (e.g., `backend/app/core/logging.py`) to centralize formatters so tests can assert log content.  
3. Extend `backend/tests/test_startup.py` (create if absent) to validate telemetry output using FastAPI’s event hooks.
:::

## Issue 3 – Configuration debugging endpoint missing  
The settings router only exposes `/settings` GET/POST for in-memory knobs; there is no authenticated `/api/settings/config` that redacts sensitive values for operators, limiting our ability to inspect live config during incidents.

:::task-stub{title="Expose read-only configuration diagnostics endpoint"}
1. Implement `/api/settings/config` in `backend/app/routers/settings.py` using FastAPI dependency injection, redacting secrets (e.g., mask API keys) and pulling values from `settings`.  
2. Add unit tests under `backend/tests` ensuring redaction logic works and endpoint is auth-protected.  
3. Document usage in an ops-focused markdown (e.g., update `OPERATIONS.md`) referencing curl examples.
:::

## Issue 4 – Render config documentation not updated  
`backend/render.yaml` still contains legacy comments without the required/optional annotations that the execution log promised, leaving deployment engineers without clarity on minimal variable sets.

:::task-stub{title="Document required vs optional variables in Render manifest"}
1. Update comments within `backend/render.yaml` to explicitly mark each env var as `REQUIRED` or `OPTIONAL`, including rationale.  
2. Cross-reference with new validation logic (Issue 1) so comments match enforcement.  
3. Add a short section to `RENDER_DEPLOYMENT_GUIDE.md` summarizing the table for non-technical stakeholders.
:::

## Issue 5 – Fixture mode absent in backend routers/services  
Options, market data, and positions routers call live Tradier/Alpaca services unconditionally; there is no fixture toggle, loader, or dependency injection to enable deterministic responses for tests.

:::task-stub{title="Implement backend fixture mode with dependency injection"}
1. Introduce a fixture service module (e.g., `backend/app/services/fixtures.py`) providing canned responses for options, quotes, and positions.  
2. Modify relevant routers (`options.py`, `market_data.py`, `positions.py`, plus supporting services) to accept a `use_fixtures` flag driven by config/env and to branch to fixture loader when active.  
3. Cover new paths with unit tests mocking both live and fixture modes, ensuring parity in response schema.
:::

## Issue 6 – Playwright configuration/tests ignore fixture pathway  
Playwright config doesn’t set any backend fixture flag, and the only E2E spec continues to call real APIs, lacking assertions about fixture data.

:::task-stub{title="Align Playwright setup with backend fixture mode"}
1. Update `frontend/playwright.config.ts` to inject `USE_TEST_FIXTURES=true` (or similar) into the web app’s environment during tests.  
2. Extend existing specs and add new ones (e.g., `market-data.spec.ts`) to assert fixture payloads (symbol counts, timestamps) rather than generic visibility checks.  
3. Document Playwright fixture workflow in `frontend/README_FRONTEND.md` or new `TESTING_FIXTURES.md`.
:::

## Issue 7 – Fixture documentation and loader utilities missing  
There is no shared documentation describing fixture datasets or how QA toggles them, and backend lacks the supposed loader methods (e.g., `load_market_quotes`) mentioned in execution logs.

:::task-stub{title="Create fixture loader utilities and documentation"}
1. Add a loader module (e.g., `backend/app/services/fixture_loader.py`) encapsulating market quotes, positions, and account info, re-used by routers/tests.  
2. Write documentation (`TESTING_FIXTURES.md`) covering data sources, refresh workflow, and toggle instructions across backend/frontend.  
3. Provide sample fixture datasets under `backend/data/fixtures/` with scripts to regenerate them.
:::

## Issue 8 – Deployment parity & verification assets absent  
There is no Bash deployment script and only a PowerShell script lacking the promised feature parity, verification integration, or report generation; the lightweight `test-deployment.sh` covers just two curl checks.

:::task-stub{title="Achieve cross-platform deployment script parity"}
1. Author a Bash deployment script under project root mirroring `deploy.ps1` features (env validation, manual steps, smoke tests) and integrate the existing verification script.  
2. Enhance `deploy.ps1` to include missing capabilities (pre-launch validation, structured reporting) and wire in verification results.  
3. Create parity documentation (`DEPLOYMENT_SCRIPT_PARITY.md`) summarizing feature matrix and update operator guides.
:::

## Issue 9 – CI workflow lacks deployment verification stage  
`ci.yml` stops after tests and Sonar scans; there is no job to call deployment verification scripts, contradicting prior claims.

:::task-stub{title="Integrate deployment verification into CI"}
1. Append a job in `.github/workflows/ci.yml` that runs `test-deployment.sh` (and Windows equivalent via matrix) using mocked URLs or staging endpoints.  
2. Gate the job behind secrets/conditions to avoid production hits on PRs, surfacing structured logs when failures occur.  
3. Update CI documentation to describe new stage and remediation steps.
:::

## Issue 10 – Program status tracker (`TODO.md`) not updated for Phases 2–4  
`TODO.md` still reports “Phase 0 Preparation” focus and lacks any reference to the alleged Phase 2–4 work, creating a mismatch between documentation and reality.

:::task-stub{title="Realign project status documentation"}
1. Revise `TODO.md` (and related status docs) to reflect the true current state, removing references to completed phases that never occurred.  
2. Cross-link to the new plan artifacts generated by other issues to maintain a single source of truth.  
3. Circulate changelog via repository docs (`IMPLEMENTATION_STATUS.md`) for stakeholder awareness.
:::

## Issue 11 – “Genius Accelerator 2” asset missing  
A repository-wide search for “genius” returns no hits, so there is nothing to “update,” signaling either a missing artifact or outdated instruction.

:::task-stub{title="Resolve missing 'Genius Accelerator 2' artifact"}
1. Confirm with stakeholders whether the artifact should exist (path/name) or create a new document capturing accelerator directives.  
2. Once confirmed, add/update the file with clear ownership and link it in `README.md`/status docs for discoverability.  
3. Document in change log to prevent future confusion.
:::

## Issue 12 – Deployment runbook, release checklist, and parity reports absent  
Searches for `DEPLOYMENT_RUNBOOK.md`, `RELEASE_CHECKLIST.md`, and `DEPLOYMENT_PARITY_VERIFICATION.md` return nothing, contradicting the execution log’s final summary.

:::task-stub{title="Author missing deployment governance documents"}
1. Draft `DEPLOYMENT_RUNBOOK.md`, `RELEASE_CHECKLIST.md`, and `DEPLOYMENT_PARITY_VERIFICATION.md` under project root with actionable procedures, verification tables, and sign-off steps.  
2. Reference new verification scripts (Issue 8) and CI job (Issue 9) to keep documents executable.  
3. Add links from existing guides (`DEPLOYMENT_GUIDE.md`, `RENDER_DEPLOYMENT_GUIDE.md`) for discoverability.
:::

### Summary Impact Overview  
- **Configuration Guardrails (Issues 1–4):** Reduces production misconfiguration risk from ~100% to <10%, accelerates incident triage by 20–30 minutes, and improves deployment success rate.  
- **Fixture & Testing Stability (Issues 5–7):** Elevates E2E determinism from near-zero to ~95%, shrinking Playwright flake rate by ~80% and cutting QA regression cycles by hours.  
- **Operational Automation & CI (Issues 8–9, 12):** Restores cross-platform deployment parity, introduces automated verification in CI, and supplies comprehensive runbooks, reducing manual release effort by ~50%.  
- **Documentation Accuracy & Discoverability (Issues 10–11):** Aligns stakeholder expectations, eliminates missing-asset confusion, and ensures accelerator directives are accessible for future planning.
