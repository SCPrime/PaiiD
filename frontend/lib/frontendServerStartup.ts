import type { FrontendValidationReport } from "../utils/envValidation";
import { logFrontendStartup, runFrontendValidations } from "../utils/envValidation";

let cachedReport: FrontendValidationReport | null = null;
let logged = false;

function getReport(): FrontendValidationReport {
  if (!cachedReport) {
    cachedReport = runFrontendValidations();
  }
  return cachedReport;
}

export function ensureServerEnvironment(): void {
  const report = getReport();
  if (report.hasErrors && !report.metadata.isLocal) {
    throw new Error(
      "Frontend prelaunch validation failed. Resolve the configuration errors logged above."
    );
  }
}

export function logServerStartup(): void {
  if (logged) {
    return;
  }
  const report = getReport();
  logFrontendStartup(report, { application: "paiid-frontend", runtime: "server" });
  logged = true;
}

export function getServerValidationReport(): FrontendValidationReport {
  return getReport();
}
