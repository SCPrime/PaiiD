# Observability Runbook

This runbook documents the steps required to enable, monitor, and verify the
backend observability stack for PaiiD. It covers Sentry for error tracking,
Datadog for distributed tracing and log aggregation, and New Relic for APM and
alert orchestration.

## 1. Configuration Summary

Set the following environment variables for the backend service:

| Variable | Purpose |
| --- | --- |
| `SENTRY_DSN` | Project DSN for Sentry error ingestion. |
| `SENTRY_ENVIRONMENT` | Optional override of the deployment environment label. Defaults to `APP_ENV`. |
| `SENTRY_TRACES_SAMPLE_RATE` | Floating-point sampling rate for performance traces (default `0.1`). |
| `SENTRY_PROFILES_SAMPLE_RATE` | Floating-point sampling rate for profiling (default `0.1`). |
| `DATADOG_TRACE_ENABLED` | Set to `true` to enable Datadog agent auto-instrumentation. |
| `DATADOG_SERVICE_NAME` | Overrides the Datadog service name (`paiid-backend` by default). |
| `DATADOG_ENVIRONMENT` | Logical Datadog environment (defaults to `APP_ENV`). |
| `DATADOG_TRACE_AGENT_URL` | Optional custom trace-agent endpoint such as `http://datadog-agent:8126`. |
| `NEW_RELIC_ENABLED` | Set to `true` to wrap the ASGI application with the New Relic agent. |
| `NEW_RELIC_APP_NAME` | Display name for the New Relic application. |
| `NEW_RELIC_ENVIRONMENT` | Target environment section in the New Relic config. |
| `NEW_RELIC_CONFIG_FILE` | Absolute path to a `newrelic.ini` configuration file. |
| `OBSERVABILITY_VERIFY_ON_STARTUP` | Set to `true` to emit synthetic verification signals during startup. |

> **Sensitive data**: Configure `NEW_RELIC_LICENSE_KEY`, `DD_API_KEY`, and other
> secrets through your deployment platform’s secret manager. They are consumed
> by the respective agents via environment variables and must not be committed
> to the repository.

## 2. Deployment Checklist

1. Install the updated backend dependencies (`sentry-sdk`, `ddtrace`,
   `newrelic`, `python-json-logger`).
2. Provide the environment variables listed above. When using Docker, pass the
   variables through `docker-compose` or the hosting provider UI.
3. For New Relic, provision a `newrelic.ini` file (or use the default one
   generated from your account) and set `NEW_RELIC_CONFIG_FILE` to its path.
4. Restart the backend service so that the observability initialization runs on
   startup.

## 3. Alert Policies

### Sentry

* Configure issue alerts for the `paiid-backend` project targeting the
  `SENTRY_ENVIRONMENT` values (`production`, `staging`, etc.).
* Recommended alerts:
  * **High-severity error**: Trigger when more than 5 errors occur within 1
    minute for the same issue in production.
  * **New issue regression**: Trigger on issues that regress after being
    resolved.

### Datadog

* Use the `paiid-backend` service within Datadog APM.
* Suggested monitors:
  * **APM error rate**: Alert when `service:paiid-backend` error rate exceeds
    5% for 5 minutes.
  * **Log-based alert**: Filter by `event:observability_verification_exception`
    to confirm verification events arrive.
* Link monitors to on-call escalation policies so synthetic verification
  signals do not page by marking them with the tag `verification:true`.

### New Relic

* Create an alert policy for the New Relic application configured via
  `NEW_RELIC_APP_NAME`.
* Recommended conditions:
  * **Error percentage** over 5% for 5 minutes.
  * **Apdex score** below 0.85 for more than 10 minutes.
* Route alerts to the same escalation path as Sentry/Datadog to maintain a
  unified incident workflow.

## 4. Verification Procedures

### Automated Startup Verification

1. Temporarily set `OBSERVABILITY_VERIFY_ON_STARTUP=true` and redeploy or start
   the backend locally.
2. Confirm that the application logs include the event
   `observability_verification_exception` in JSON format.
3. Check Sentry for a new event titled “Observability verification exception”.
4. In Datadog Logs, search for `event:observability_verification_datadog`. If a
   trace is active, confirm that the trace span contains the tag
   `observability.verification:true`.
5. In New Relic, locate the custom event `ObservabilityVerification` and ensure
   it reports the expected environment.
6. Disable the flag after verification to prevent repeated synthetic errors.

### Manual API Smoke Test

1. Trigger an intentional error via the API (for example, submit a malformed
   request to `/api/orders`).
2. Confirm the HTTP response returns a non-2xx status code.
3. Verify that:
   * Sentry captures the exception with request metadata (Authorization headers
     are automatically redacted).
   * Datadog surfaces the error in APM traces and logs.
   * New Relic records the error and raises the configured alert if the
     threshold is breached.

### Post-Incident Runback

After any incident involving elevated error rates:

1. Review Sentry issue details and assign owners.
2. Inspect correlated Datadog traces/logs using the trace ID embedded in the
   JSON logs.
3. Examine New Relic transactions for performance regressions.
4. Document remediation steps in the incident tracker and link back to the
   observability data points used.

## 5. Maintenance

* Rotate API keys and license keys quarterly.
* Keep the observability dependencies up to date to receive security fixes and
  instrumentation improvements.
* Update alert thresholds whenever the service baseline changes (for example,
  during major releases).

