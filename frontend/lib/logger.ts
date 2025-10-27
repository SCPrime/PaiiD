/**
 * Centralized logging utility for PaiiD
 *
 * Usage:
 *   import { logger } from '@/lib/logger';
 *   logger.info('User logged in', { userId: '123' });
 *   logger.error('API call failed', error);
 */

/* eslint-disable no-console */
// Console methods are intentionally used in this logging utility

const isDevelopment = process.env.NODE_ENV === "development";
const isTest = process.env.NODE_ENV === "test";

export interface LogData {
  [key: string]: unknown;
}

class Logger {
  private formatMessage(level: string, message: string, data?: LogData): string {
    const timestamp = new Date().toISOString();
    const dataStr = data ? ` ${JSON.stringify(data)}` : "";
    return `[${timestamp}] [${level}] ${message}${dataStr}`;
  }

  /**
   * Log informational messages (development only)
   */
  info(message: string, data?: LogData): void {
    if (isDevelopment && !isTest) {
      console.info(this.formatMessage("INFO", message, data));
    }
  }

  /**
   * Log warning messages (development only)
   */
  warn(message: string, data?: LogData): void {
    if (isDevelopment && !isTest) {
      console.warn(this.formatMessage("WARN", message, data));
    }
  }

  /**
   * Log error messages (always logged)
   */
  error(message: string, error?: Error | unknown, data?: LogData): void {
    const errorData =
      error instanceof Error
        ? { message: error.message, stack: error.stack, ...data }
        : { error, ...data };

    console.error(this.formatMessage("ERROR", message, errorData));
  }

  /**
   * Log debug messages (development only, verbose)
   */
  debug(message: string, data?: LogData): void {
    if (isDevelopment && !isTest) {
      console.debug(this.formatMessage("DEBUG", message, data));
    }
  }

  /**
   * Group related log messages
   */
  group(label: string): void {
    if (isDevelopment && !isTest) {
      console.group(label);
    }
  }

  groupEnd(): void {
    if (isDevelopment && !isTest) {
      console.groupEnd();
    }
  }

  /**
   * Time a function execution
   */
  time(label: string): void {
    if (isDevelopment && !isTest) {
      console.time(label);
    }
  }

  timeEnd(label: string): void {
    if (isDevelopment && !isTest) {
      console.timeEnd(label);
    }
  }
}

export const logger = new Logger();
export default logger;
