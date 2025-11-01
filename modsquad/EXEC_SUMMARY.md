# MOD SQUAD Orchestra One-Sheet

## Mission Snapshot

- **Purpose:** Autonomous, policy-driven engineering force that keeps PaiiD-2mx production-ready across equities, commodities, and DEX meme-coin strategies.
- **Operating Mode:** 24/7 conductor-led orchestration with human-in-the-loop checkpoints defined in guardrails.

## Core Roles & Responsibilities

- **Conductor** (modsquad runtime)
  - Routes tickets to the best-fit model stack based on workflow stage and budget tier.
  - Balances speed vs. depth; escalates to `gpt-5-pro` for executive validation.
  - Enforces token/budget ceilings defined in `modsquad/config/modsquad.yaml`.

- **DeepSeek Unit**
  - `deepseek-coder:latest`: Primary builder for scaffolding, implementation, and regression tests.
  - `deepseek-r1-0528`: High-rigor reviewer for architecture, risk, and incident triage.
  - `deepseek-v3.1`: Narrative analyst delivering research briefs and context packs.

- **OpenAI Codex Successors**
  - `gpt-5-codex-high`: Burst-mode optimizer and emergency patch executor.
  - `gpt-5` & `gpt-5-pro`: Strategic reasoning, compliance sweeps, and executive storytelling.

- **Anthropic Crew**
  - `claude-4.5-sonnet`: Long-form documentation, UX copy, and design review.
  - `claude-4.5-haiku`: Rapid summaries, release notes, and maintenance briefs.

- **Maintenance Crew**
  - Runs the nine-phase maintenance loop (pause → backup → verify → clean → detect_errors → security → performance → report → resume) on the `maintenance_schedule` cadence.
  - Emits activity JSONL streams to `modsquad/logs/run-history` for auditing.

- **Guardrails**
  - Enforce safety (PII filters, harmful content blocks), budget ceilings, and rate limits.
  - Integrate quality gates (lint, test, API health, security, observability) before merges.
- **Market Modules**
  - Modular strategy packs for `stocks_options` (paper/live) and `dex_meme_coins` (paper) now register automatically.
  - Orchestrator selects modules per workflow instructions, enabling multi-market hot swaps.

## Active Workflows & Model Pairings

- **Feature Development:** `gpt-5-pro` brief → DeepSeek build → `deepseek-r1` review → `claude-4.5-sonnet` doc.
- **Bug Fix:** `deepseek-r1` reproduce → `deepseek-coder` patch/tests → `claude-4.5-haiku` incident wrap-up.
- **Refactor:** `deepseek-r1` architecture → `deepseek-coder` change set → `gpt-5-pro` risk audit.
- **Optimization:** `deepseek-r1` profile → `deepseek-coder` tuning → `gpt-5-codex-high` benchmark.
- **Documentation Refresh:** `deepseek-v3.1` audit → `claude-4.5-sonnet` rewrite → `gpt-5` proofread.

## Achievements to Date

- Unified PaiiD-2mx model catalog with Cursor-verified agents; no dormant endpoints.
- Hardwired routing, budgets, and maintenance guardrails into versioned YAML configs.
- Deployed operator-facing control surface (executive sheet + professional runbook) to keep leadership in command.
- Mirrored modular market architecture across PaiiD and PaiiD-2mx for synchronous upgrades.

## Escalation & Reporting

- Daily maintenance snapshots posted to `modsquad/logs/run-history`.
- Budget alerts at 80% threshold; Conductor auto-pauses when exceeded.
- Human override tokens required for guardrail waivers (`release_manager` or `security_officer`).
