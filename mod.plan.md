# MOD SQUAD Plan – Branding + Full Verification (PaiiD)

## Objective
Guarantee a production‑tight PaiiD platform with:
- Locked PaiiD logo/chat component rendered in the header on every page
- UI branding: replace user‑facing “AI”/“iPi” text with “PaiiD” + locked logo (no code identifier changes)
- End‑to‑end live data validation (quotes, bars, options, news, auth, orders/positions)
- Zero browser errors, strict CORS/auth/error‑mapping, and no legacy code conflicts
- Identical checks by all agents/subagents/extensions

## Branding Enforcement
- Header: `frontend/components/layout/AppHeader.tsx` mounts `CompletePaiiDLogo` globally via `pages/_app.tsx`
- UI text replacements (visible strings only):
  - “AI Recommendations” → “PaiiD Recommendations”
  - “Ask AI” / “AI Suggest” → “Ask PaiiD” / “PaiiD Suggest”
  - Onboarding: “AI‑assisted” → “PaiiD‑assisted”
- Inline logo component: `frontend/components/ui/PaiiDInline.tsx` with `aria-label="PaiiD"`
- Accessibility: screen readers announce “PaiiD” wherever the inline logo replaces text
- Do NOT edit locked file `frontend/components/CompletePaiiDLogo.tsx`

## Single Source of Truth (All agents/subagents/extensions must use the same checks)
- Config: `mod_squad.config.json` (required) – base_url, origin, timeouts, tags, thresholds, report_paths
- Standard commands (required):
  - `npm run mod:github` → `python scripts/auto_github_monitor.py --full-audit --output reports/github_mod.json`
  - `npm run mod:browser` → `python scripts/browser_mod.py --check-render --live-data --output reports/browser_mod.json`
  - `npm run mod:flows` → `python scripts/live_data_flows.py --comprehensive --output reports/live_flows.json`
  - `npm run mod:all` → runs the three above; non‑zero exit on any failure
- Pre‑commit quick gate (required): render + minimal flows; fail blocks commit
- CI gating (required): `.github/workflows/mod-squad.yml` runs `mod:all` on push/PR; merge blocked unless all pass
- Artifact schema (required): identical top‑level keys across reports: `{ status, errors, timings, p95_ms, details }`
- Enforcement (required): any agent/subagent/extension must call these commands; deviation fails with reason “nonstandard runner”

## Tools (added)
- Repo audit: `scripts/auto_github_monitor.py`
  - Flags: `--full-audit`, `--scan-conflicts`, `--scan-old-code`, `--endpoint-coverage`, `--env-audit`, `--output`
  - Finds deprecated patterns, missing CORS/auth, proxy mismatches, env drift
- Browser verification: `scripts/browser_mod.py` (wrapper for Playwright tags) [planned]
  - Flags: `--check-render`, `--live-data`, `--interactions-only`, `--output`
- Live flows: `scripts/live_data_flows.py` (enhanced) [present]
  - Flags: `--comprehensive`, `--output`

## CI Workflow (planned)
`.github/workflows/mod-squad.yml`
- Steps:
  1) Repo audit → `github_mod.json`
  2) Browser checks (render + live) → `browser_mod.json`
  3) Live flows (comprehensive) → `live_flows.json`
- Upload artifacts: `mod-squad-reports/`
- Block merges on failures

## Branding Checks (Hard Gates)
- Grep rules: fail CI if UI contains raw `\biPi\b` text or “AI” branding in visible strings
  - Allow back‑end identifiers, env names, comments, docs
- Header presence test:
  - Assert PaiiD header exists on `/login`, `/register`, `/dashboard`, and all wedges
- A11y:
  - Assert inline logo is accompanied by `aria-label="PaiiD"` or sr‑only text

## Browser MOD Scenarios (Playwright tags)
- @render: `/login`, `/register`, `/dashboard`, each wedge → no console errors, header present
- @live: proxy origin preflight + health; quotes/bars/options/news → 200 OK; P95 ≤ 2s
- @interactions: 
  - Login with Remember Me → JWT cookie 30 days
  - Radial wedges navigate without errors
  - Execute trade (paper) → confirmation
  - PaiiD recommendations query flow → 3 cards, accept → prefilled trade
  - News impact cards show color outlines and actions

## Live Data Flows (scripts/live_data_flows.py)
- `/api/proxy/api/market/quote/SPY` → 200 (stale fallback acceptable)
- `/api/proxy/api/market/bars/SPY?timeframe=daily&limit=5` → 200
- `/api/proxy/api/options/expirations/SPY` → 200
- `/api/proxy/api/health/readiness` → 200 healthy or structured 503 (not 500)
- Optional: `/api/proxy/api/news/market` → 200

## Performance & Reliability
- Response times: P95 ≤ 2s on critical paths (Playwright timings + flows)
- Error mapping: 401/403/429 → 503; 5xx upstream → 502; missing quote → historical fallback 200
- CORS: env‑driven allowlist; preflights pass for production origin

## Security & Safety
- No secrets in code/logs (scan by repo audit)
- All user endpoints require JWT; service endpoints use API token via proxy
- Strict CORS (no wildcard)
- Locked files untouched (logo)

## Acceptance Criteria
- PaiiD header (locked logo/chat) renders on every page
- All visible UI “AI”/“iPi” strings show “PaiiD” + logo; a11y text says “PaiiD”
- All MOD SQUAD reports PASS; artifacts uploaded (no console errors)
- End‑to‑end live flows PASS; P95 ≤ 2s; correct error mapping
- No legacy code conflicts; env and proxy allowlist consistent with backend

## Commands
- Repo audit:
```
python scripts/auto_github_monitor.py --full-audit --output reports/github_mod.json
```
- Browser checks:
```
python scripts/browser_mod.py --check-render --live-data --output reports/browser_mod.json
```
- Live flows:
```
python scripts/live_data_flows.py --comprehensive --output reports/live_flows.json
```

## Notes
- Branding is UI‑only; backend identifiers or env vars with "ai" remain untouched.
- Any failure halts deployment and triggers remediation before re‑run.

