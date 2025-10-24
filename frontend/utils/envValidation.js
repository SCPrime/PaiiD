const path = require("path");
const fs = require("fs");

const RECOGNIZED_ENVS = new Set([
  "local",
  "development",
  "dev",
  "test",
  "staging",
  "preview",
  "production",
]);

const LOCAL_ENVS = new Set(["local", "development", "dev", "test"]);

function maskSecret(value, { prefix = 4, suffix = 2 } = {}) {
  if (!value) {
    return "[NOT SET]";
  }

  const normalized = String(value).trim();
  if (normalized.length <= prefix + suffix) {
    return "*".repeat(normalized.length);
  }

  return `${normalized.slice(0, prefix)}…${normalized.slice(-suffix)}`;
}

function resolveAppEnv() {
  const raw =
    process.env.NEXT_PUBLIC_APP_ENV ||
    process.env.APP_ENV ||
    process.env.NODE_ENV ||
    "development";
  const normalized = raw.trim().toLowerCase();
  return { raw, normalized };
}

function getEnvironmentLabel(normalized) {
  const mapping = {
    dev: "development",
    development: "development",
    local: "local",
    test: "test",
    staging: "staging",
    preview: "preview",
    production: "production",
  };

  return mapping[normalized] || normalized || "local";
}

function resolveCommitSha() {
  return (
    process.env.NEXT_PUBLIC_VERCEL_GIT_COMMIT_SHA ||
    process.env.VERCEL_GIT_COMMIT_SHA ||
    process.env.RENDER_GIT_COMMIT ||
    process.env.GIT_COMMIT ||
    null
  );
}

function resolveReleaseVersion() {
  return (
    process.env.NEXT_PUBLIC_RELEASE_VERSION ||
    process.env.RELEASE_VERSION ||
    null
  );
}

function resolveEnvFile() {
  const candidate = process.env.FRONTEND_ENV_PATH || path.join(process.cwd(), ".env.local");
  return {
    path: candidate,
    exists: fs.existsSync(candidate),
  };
}

function runFrontendValidations() {
  const { raw, normalized } = resolveAppEnv();
  const metadata = {
    rawEnv: raw,
    normalizedEnv: normalized,
    environmentLabel: getEnvironmentLabel(normalized),
    commit: resolveCommitSha(),
    release: resolveReleaseVersion(),
    envFile: resolveEnvFile(),
    isRecognized: RECOGNIZED_ENVS.has(normalized),
    isLocal: LOCAL_ENVS.has(normalized),
  };

  const checks = [];

  function addCheck(name, condition, successDetail, failureDetail, remediation, severity = "error") {
    checks.push({
      name,
      passed: Boolean(condition),
      detail: condition ? successDetail : failureDetail,
      remediation,
      severity,
    });
  }

  addCheck(
    "environment-profile",
    metadata.isRecognized,
    `Environment profile '${metadata.environmentLabel}' recognized`,
    `Unknown NEXT_PUBLIC_APP_ENV/APP_ENV profile: ${raw || "<empty>"}`,
    "Set NEXT_PUBLIC_APP_ENV (or APP_ENV) to local, development, test, staging, preview, or production.",
  );

  const sentryDsn = process.env.NEXT_PUBLIC_SENTRY_DSN || process.env.SENTRY_DSN;
  addCheck(
    "sentry-dsn",
    metadata.isLocal || Boolean(sentryDsn),
    sentryDsn ? `Sentry DSN configured (${maskSecret(sentryDsn)})` : "Sentry disabled for local/test environments",
    "NEXT_PUBLIC_SENTRY_DSN must be configured for staging/preview/production builds",
    "Add NEXT_PUBLIC_SENTRY_DSN to the deployment environment or downgrade to a local profile.",
  );

  const apiToken = process.env.API_TOKEN || process.env.NEXT_PUBLIC_API_TOKEN;
  addCheck(
    "api-token",
    metadata.isLocal || Boolean(apiToken),
    apiToken ? `API token configured (${maskSecret(apiToken)})` : "API token skipped in local/test",
    "API token missing for frontend proxy requests",
    "Set API_TOKEN (server) or NEXT_PUBLIC_API_TOKEN (client) for the frontend deployment.",
  );

  const backendBaseUrl = process.env.NEXT_PUBLIC_BACKEND_API_BASE_URL || process.env.BACKEND_API_BASE_URL;
  addCheck(
    "backend-base-url",
    Boolean(backendBaseUrl),
    `Backend API base set to ${backendBaseUrl}`,
    "NEXT_PUBLIC_BACKEND_API_BASE_URL missing",
    "Provide NEXT_PUBLIC_BACKEND_API_BASE_URL so the frontend knows where to send API requests.",
  );

  addCheck(
    "git-commit",
    Boolean(metadata.commit),
    `Commit metadata detected (${metadata.commit || "unknown"})`,
    "Git commit metadata missing",
    "Expose NEXT_PUBLIC_VERCEL_GIT_COMMIT_SHA (or VERCEL_GIT_COMMIT_SHA) for traceability.",
    "warning",
  );

  return {
    metadata,
    checks,
    get hasErrors() {
      return checks.some((check) => !check.passed && check.severity === "error");
    },
    get hasWarnings() {
      return checks.some((check) => !check.passed && check.severity === "warning");
    },
  };
}

function logFrontendStartup(report, { application = "paiid-frontend", runtime = "build", logger = console } = {}) {
  const lines = [];
  const envFileLabel = `${report.metadata.envFile.path} (${report.metadata.envFile.exists ? "exists" : "missing"})`;

  lines.push(`\n===== ${application.toUpperCase()} STARTUP (${runtime}) =====`);
  lines.push(`Environment profile: ${report.metadata.environmentLabel} (${report.metadata.rawEnv})`);
  lines.push(`Git commit: ${report.metadata.commit || "unknown"}`);
  lines.push(`Release version: ${report.metadata.release || "unreleased"}`);
  lines.push(`Sentry: ${process.env.NEXT_PUBLIC_SENTRY_DSN ? "ENABLED" : "disabled"}`);
  const apiToken = process.env.API_TOKEN || process.env.NEXT_PUBLIC_API_TOKEN;
  lines.push(`API token: ${maskSecret(apiToken)}`);
  const backendBaseUrl = process.env.NEXT_PUBLIC_BACKEND_API_BASE_URL || process.env.BACKEND_API_BASE_URL || "<not set>";
  lines.push(`Backend API base: ${backendBaseUrl}`);
  lines.push(`Env file: ${envFileLabel}`);

  lines.push("===== PRELAUNCH VALIDATION =====");
  for (const record of report.checks) {
    const status = record.passed ? "PASS" : record.severity === "warning" ? "WARN" : "FAIL";
    lines.push(`[${status}] ${record.name}: ${record.detail}`);
    if (!record.passed) {
      lines.push(`        Remediation: ${record.remediation}`);
    }
  }

  if (report.hasErrors) {
    lines.push("❌ Frontend validation failed - fix the configuration before deploying.");
  } else if (report.hasWarnings) {
    lines.push("⚠️  Frontend validation completed with warnings.");
  } else {
    lines.push("✅ All frontend validations passed.");
  }

  lines.push("================================\n");

  for (const line of lines) {
    if (logger && typeof logger.log === "function") {
      logger.log(line);
    } else {
      console.log(line);
    }
  }
}

module.exports = {
  maskSecret,
  runFrontendValidations,
  logFrontendStartup,
};
