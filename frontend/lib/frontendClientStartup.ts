let clientLogged = false;

function resolveClientMetadata() {
  const appEnv = (process.env.NEXT_PUBLIC_APP_ENV || process.env.NODE_ENV || "development").trim();
  const commit =
    process.env.NEXT_PUBLIC_VERCEL_GIT_COMMIT_SHA ||
    process.env.VERCEL_GIT_COMMIT_SHA ||
    "unknown";
  const release = process.env.NEXT_PUBLIC_RELEASE_VERSION || "unreleased";
  const telemetryEnabled = process.env.NEXT_PUBLIC_TELEMETRY_ENABLED !== "false";
  const sentryEnabled = Boolean(process.env.NEXT_PUBLIC_SENTRY_DSN);

  return { appEnv, commit, release, telemetryEnabled, sentryEnabled };
}

export function logClientStartup(): void {
  if (typeof window === "undefined" || clientLogged) {
    return;
  }

  const metadata = resolveClientMetadata();

  // eslint-disable-next-line no-console
  console.info("\n===== PAIID FRONTEND STARTUP (client) =====");
  // eslint-disable-next-line no-console
  console.info(`Environment profile: ${metadata.appEnv}`);
  // eslint-disable-next-line no-console
  console.info(`Git commit: ${metadata.commit}`);
  // eslint-disable-next-line no-console
  console.info(`Release version: ${metadata.release}`);
  // eslint-disable-next-line no-console
  console.info(`Telemetry enabled: ${metadata.telemetryEnabled ? "yes" : "no"}`);
  // eslint-disable-next-line no-console
  console.info(`Sentry: ${metadata.sentryEnabled ? "ENABLED" : "disabled"}`);
  // eslint-disable-next-line no-console
  console.info("===========================================\n");

  clientLogged = true;
}
