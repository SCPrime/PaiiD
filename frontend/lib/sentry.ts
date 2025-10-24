/**
 * Sentry Error Tracking Configuration
 *
 * Initializes Sentry for production error monitoring.
 *
 * Setup Instructions:
 * 1. Sign up at https://sentry.io (free tier available)
 * 2. Create a new Next.js project
 * 3. Copy your DSN
 * 4. Add to Vercel: NEXT_PUBLIC_SENTRY_DSN=your-dsn-here
 * 5. Redeploy
 */

import * as Sentry from "@sentry/nextjs";

let sentryInitialized = false;

const AUTH_HEADER_KEYS = new Set(["authorization", "Authorization"]);

function coerceSampleRate(values: Array<string | number | undefined>, fallback: number): number {
  for (const value of values) {
    if (value === undefined) {
      continue;
    }

    const numericValue = typeof value === "number" ? value : Number(value);
    if (Number.isFinite(numericValue) && numericValue >= 0 && numericValue <= 1) {
      return numericValue;
    }
  }

  return fallback;
}

function redactHeaders<T extends Record<string, unknown> | undefined>(headers: T): T {
  if (!headers) {
    return headers;
  }

  const sanitized = { ...headers } as Record<string, unknown>;
  for (const key of Object.keys(sanitized)) {
    if (AUTH_HEADER_KEYS.has(key) || key.toLowerCase() === "authorization") {
      sanitized[key] = "[REDACTED]";
    }
  }

  return sanitized as T;
}

function sanitizeEvent(event: Sentry.Event): Sentry.Event {
  if (event.request?.headers) {
    event.request.headers = redactHeaders(event.request.headers);
  }

  if ((event as Record<string, unknown>).type === "replay_event") {
    const contexts = event.contexts as Record<string, any> | undefined;
    const replayContext = contexts?.replay as Record<string, any> | undefined;
    if (replayContext?.request?.headers) {
      replayContext.request.headers = redactHeaders(replayContext.request.headers);
    }
  }

  if (event.breadcrumbs) {
    event.breadcrumbs = event.breadcrumbs.map((breadcrumb) => {
      if (breadcrumb.data?.url) {
        breadcrumb.data.url = breadcrumb.data.url.replace(/token=[^&]*/g, "token=REDACTED");
      }
      if (breadcrumb.data?.request?.headers) {
        breadcrumb.data.request.headers = redactHeaders(breadcrumb.data.request.headers);
      }
      return breadcrumb;
    });
  }

  return event;
}

export function initSentry(): void {
  if (sentryInitialized) {
    return;
  }

  const sentryDsn =
    process.env.NEXT_PUBLIC_SENTRY_DSN ||
    process.env.SENTRY_DSN ||
    process.env.NEXT_PUBLIC_RENDER_SENTRY_DSN ||
    process.env.RENDER_SENTRY_DSN;

  if (!sentryDsn) {
    console.info("[Sentry] DSN not configured - error tracking disabled");
    console.info("[Sentry] To enable: Add NEXT_PUBLIC_SENTRY_DSN to environment variables");
    return;
  }

  const isProduction = process.env.NODE_ENV === "production";
  const resolvedEnvironment =
    process.env.NEXT_PUBLIC_SENTRY_ENVIRONMENT ||
    process.env.SENTRY_ENVIRONMENT ||
    process.env.VERCEL_ENV ||
    (isProduction ? "production" : "development");

  const releaseSha =
    process.env.NEXT_PUBLIC_SENTRY_RELEASE ||
    process.env.SENTRY_RELEASE ||
    process.env.NEXT_PUBLIC_VERCEL_GIT_COMMIT_SHA ||
    process.env.VERCEL_GIT_COMMIT_SHA ||
    process.env.GIT_COMMIT_SHA;
  const release = `paiid-frontend@${releaseSha || "dev"}`;

  const tracesSampleRate = coerceSampleRate(
    [
      process.env.NEXT_PUBLIC_SENTRY_TRACES_SAMPLE_RATE,
      process.env.SENTRY_TRACES_SAMPLE_RATE,
    ],
    0.1,
  );

  const replaysSessionSampleRate = coerceSampleRate(
    [
      process.env.NEXT_PUBLIC_SENTRY_REPLAYS_SESSION_SAMPLE_RATE,
      process.env.SENTRY_REPLAYS_SESSION_SAMPLE_RATE,
    ],
    isProduction ? 0.1 : 0,
  );

  const replaysOnErrorSampleRate = coerceSampleRate(
    [
      process.env.NEXT_PUBLIC_SENTRY_REPLAYS_ERROR_SAMPLE_RATE,
      process.env.SENTRY_REPLAYS_ERROR_SAMPLE_RATE,
    ],
    1,
  );

  try {
    Sentry.init({
      dsn: sentryDsn,
      environment: resolvedEnvironment,
      tracesSampleRate,
      replaysSessionSampleRate,
      replaysOnErrorSampleRate,
      release,
      integrations: [
        new Sentry.BrowserTracing({}),
        new Sentry.Replay({
          maskAllText: true,
          maskAllInputs: true,
          blockAllMedia: true,
          networkCaptureBodies: false,
          networkRequestHeaders: false,
          networkResponseHeaders: false,
        }),
      ],
      beforeSend(event) {
        return sanitizeEvent(event);
      },
      ignoreErrors: [
        "top.GLOBALS",
        "canvas.contentDocument",
        "MyApp_RemoveAllHighlights",
        "atomicFindClose",
        "NetworkError",
        "Failed to fetch",
        "Hydration failed",
        "There was an error while hydrating",
      ],
      sendDefaultPii: false,
    });

    Sentry.addGlobalEventProcessor((event) => sanitizeEvent(event));

    sentryInitialized = true;
    console.info("[Sentry] ✅ Error tracking initialized");
  } catch (error) {
    console.error("[Sentry] ❌ Failed to initialize:", error);
  }
}

/**
 * Capture an exception manually
 */
export function captureException(error: Error, context?: Record<string, any>): void {
  if (!sentryInitialized) {
    console.error("[Sentry] Not initialized, logging error:", error);
    return;
  }

  Sentry.captureException(error, {
    contexts: context ? { custom: context } : undefined,
  });
}

/**
 * Capture a message (non-error event)
 */
export function captureMessage(
  message: string,
  level: "info" | "warning" | "error" = "info"
): void {
  if (!sentryInitialized) {
    console.info(`[Sentry] Not initialized, logging message [${level}]:`, message);
    return;
  }

  Sentry.captureMessage(message, level);
}

/**
 * Set user context (for tracking which user experienced an error)
 */
export function setUser(userId: string, role?: string): void {
  if (!sentryInitialized) {
    return;
  }

  Sentry.setUser({
    id: userId,
    role: role,
  });
}

/**
 * Add breadcrumb (for debugging context)
 */
export function addBreadcrumb(message: string, data?: Record<string, any>): void {
  if (!sentryInitialized) {
    return;
  }

  Sentry.addBreadcrumb({
    message,
    data,
    level: "info",
    timestamp: Date.now() / 1000,
  });
}

/**
 * Check if Sentry is initialized
 */
export function isSentryEnabled(): boolean {
  return sentryInitialized;
}

export default Sentry;
