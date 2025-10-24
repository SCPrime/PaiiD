# SSE Regression QA Checklist

## QA Lead Ownership

- **Primary QA Lead:** Streaming QA Lead (Ops Quality Team)
- **Backup:** Platform Observability On-call
- **Escalation Path:** Engineering Manager → Incident Response Captain

## Pre-test Setup

- [ ] Launch the app via `npm run dev` (frontend) with backend proxies reachable or stubbed.
- [ ] Verify Playwright browsers are installed locally (`npx playwright install`) so automated flows don't skip.
- [ ] Open `/__qa__/streaming-harness` to access the dedicated SSE validation surface.
- [ ] Attach browser devtools console and network tab for live telemetry verification.
- [ ] Register event listener in console: `window.addEventListener("paiid:stream-event", console.log)`.

## Baseline Streaming Verification

- [ ] Confirm **Positions Stream** transitions to `CONNECTED` within 5s and displays seed symbols.
- [ ] Confirm **Market Prices Stream** transitions to `CONNECTED` within 5s and lists tracked tickers.
- [ ] Trigger mock position payload (Playwright harness or manual `window.__mockSSEInstances`) and validate UI updates counts + summary.
- [ ] Trigger mock price payload and verify symbol list + JSON payload update.
- [ ] Observe at least one `stream=positions` and `stream=market-prices` event emitted via `paiid:stream-event`.
- [ ] Ensure telemetry POST `/api/proxy/telemetry` fires (when backend available) or buffered events accumulate without errors.

## Heartbeat & Timeout Scenarios

- [ ] Simulate missing heartbeat for >5s and verify warning banner / log event `heartbeat_timeout` is captured.
- [ ] Confirm reconnect attempt occurs with exponential backoff and `reconnect_scheduled` is emitted to telemetry.
- [ ] Validate `lastHeartbeat` timestamp updates once heartbeat resumes.

## Failure & Recovery Regression

- [ ] Force server error payload and observe `server_error` log plus UI error banner (Positions & Market streams).
- [ ] Force abrupt `EventSource` failure; confirm reconnect cycle instantiates a new connection and surfaces `connection_exception`.
- [ ] Verify `Max reconnect attempts reached` copy appears after exhausting retry budget (set `maxReconnectAttempts=1` via harness button or devtools override).
- [ ] Confirm manual `Force Reconnect` button resets attempt counter and connection status.

## Observability Hooks

- [ ] Validate Sentry receives breadcrumb/message when DSN configured (check Network or Sentry dashboard).
- [ ] Export telemetry buffer (`localStorage` → telemetry export) and attach to QA report.
- [ ] Capture console log snapshot showing `streamMonitoring` events for archive.

## Reporting

- [ ] File QA sign-off in tracker with references to Playwright run `streaming-resilience.spec.ts` and manual checklist completion.
- [ ] Record baseline timings (time to CONNECTED, reconnect duration) for trend analysis.
- [ ] Escalate anomalies immediately with captured telemetry payload and reproduction steps.
