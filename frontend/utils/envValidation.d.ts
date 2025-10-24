export type SeverityLevel = "error" | "warning";

export interface ValidationRecord {
  name: string;
  passed: boolean;
  detail: string;
  remediation: string;
  severity: SeverityLevel;
}

export interface EnvFileMetadata {
  path: string;
  exists: boolean;
}

export interface FrontendValidationMetadata {
  rawEnv: string;
  normalizedEnv: string;
  environmentLabel: string;
  commit: string | null;
  release: string | null;
  envFile: EnvFileMetadata;
  isRecognized: boolean;
  isLocal: boolean;
}

export interface FrontendValidationReport {
  metadata: FrontendValidationMetadata;
  checks: ValidationRecord[];
  readonly hasErrors: boolean;
  readonly hasWarnings: boolean;
}

export interface LogOptions {
  application?: string;
  runtime?: string;
  logger?: Console;
}

export declare function maskSecret(value: string | undefined | null, options?: { prefix?: number; suffix?: number }): string;
export declare function runFrontendValidations(): FrontendValidationReport;
export declare function logFrontendStartup(report: FrontendValidationReport, options?: LogOptions): void;
