# MOD SQUAD Operator Runbook

## Daily Activation (≈2 minutes)

1. Launch Cursor and verify the target repo is open.
2. Initiate a chat with the model best matched to the task:
   - Delivery & implementation → `deepseek-coder:latest`
   - Architecture & verification → `deepseek-r1-0528`
   - Research & market synthesis → `deepseek-v3.1`
   - Executive briefing → `gpt-5-pro`
   - Release notes & summaries → `claude-4.5-haiku`
3. State the engagement type (feature, bug fix, refactor, optimization, documentation) and instruct, “Follow MOD SQUAD workflow.”
4. Declare the active market module (e.g., “Stock options live” or “DEX meme coin paper”) so the orchestrator loads the right strategy pack.
5. Confirm reviewer mesh armed by asking “Reviewer mesh status?” — expect `R1–R4: standing by`.

## Local Infrastructure Prep (Postgres + Redis)

1. Run `docker compose -f infrastructure/docker-compose.dev.yml up -d` before starting the backend.
2. Wait for containers to report `healthy`; verify with `docker compose -f infrastructure/docker-compose.dev.yml ps`.
3. Confirm `.env` includes:
   - `DATABASE_URL=postgresql://paiid:paiid@localhost:5433/paiid`
   - `REDIS_URL=redis://localhost:6380/0`
4. Shutdown with `docker compose -f infrastructure/docker-compose.dev.yml down` after maintenance windows if desired.

## Operator Responsibilities During Execution

- Approve or decline guardrail prompts (budget usage, waivers, sensitive data flags).
- Escalate urgent fixes with the command “Invoke emergency_patch override,” which routes work through `gpt-5-codex-high`.
- Request compliance or governance reviews via “Escalate to gpt-5-pro.”
- Review reviewer outputs (`review_aggregator.jsonl`, `quality_inspector.jsonl`) and acknowledge discrepancies before ship.

## End-of-Day Checklist

1. In the integrated terminal run `pnpm modsquad:status` to confirm the maintenance crew completed its cycle.
2. If status reports `paused` or `stopped`, execute `pnpm modsquad:resume`.
3. Inspect the latest maintenance artifacts at `modsquad/logs/run-history/*.jsonl` (metrics, guardrail scheduler, component diff reports).
4. Cross-check reviewer outputs (`review_aggregator.jsonl`, `quality_inspector.jsonl`) and clear outstanding alerts.
5. Review `data/executions/history.jsonl` for the consolidated strategy execution summary (collateral, DEX allocation, status counts).

## Incident Protocol

1. Query any active model with “Conductor status report.”
2. If budget exhaustion is reported, adjust `daily_usd` / `monthly_usd` in `modsquad/config/modsquad.yaml` or wait for the next window.
3. For failed quality gates (lint/tests/security/API health), request “Provide guardrail diagnostic package” and escalate to leadership.

## Environment Expectations

- Maintain valid `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` values in the application `.env` file.
- Keep Ollama services running so DeepSeek agents remain available in Cursor.
- Approve OS prompts for Python, Ollama, or security updates that maintain runtime integrity.
- Ensure broker keys and RPC endpoints for each market module (stocks/options, DEX) remain current before switching modules.
- Verify DEX env vars before meme coin runs: `DEX_RPC_URL`, `DEX_WALLET_ADDRESS`, optional `DEX_ROUTER_CONTRACT`, `DEX_CHAIN_ID`, `DEX_SLIPPAGE_BPS`.
- Ensure `npm install` has been run in `frontend/` so Playwright regression command (`npm run playwright:test:ci`) can execute.
- Rotate secrets flagged by the `secrets_watchdog` (see `modsquad/logs/run-history/secrets_watchdog.jsonl`).
- Monitor `maintenance_notifier.jsonl` and `metrics.jsonl` for automated alerts; hook them into Slack/Teams when webhooks are ready.
- Review `strategy_verifier` artifacts after module updates to confirm smoke backtests passed.
- Track reviewer cadence: expect R1–R4 summaries every 12h; escalate to Ops Relay if missing.
- For persona runs, consult `persona_simulator` artifacts to ensure UX regressions are logged.
- Use `scripts/modsquad/after-maintenance.ps1` (Windows) or `scripts/modsquad/after-maintenance.sh` (macOS/Linux) immediately after each maintenance window so all extensions run in sequence.
