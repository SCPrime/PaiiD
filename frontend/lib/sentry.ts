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

import * as Sentry from '@sentry/nextjs';

let sentryInitialized = false;

export function initSentry(): void {
  // Only initialize once
  if (sentryInitialized) {
    return;
  }

  const SENTRY_DSN = process.env.NEXT_PUBLIC_SENTRY_DSN;

  // Skip initialization if no DSN configured
  if (!SENTRY_DSN) {
    console.info('[Sentry] DSN not configured - error tracking disabled');
    console.info('[Sentry] To enable: Add NEXT_PUBLIC_SENTRY_DSN to environment variables');
    return;
  }

  try {
    Sentry.init({
      dsn: SENTRY_DSN,

      // Environment detection
      environment: process.env.NODE_ENV === 'production' ? 'production' : 'development',

      // Performance Monitoring
      tracesSampleRate: 0.1, // 10% of transactions for performance monitoring

      // Session Replay (captures user interactions for debugging)
      replaysSessionSampleRate: 0.1, // 10% of sessions
      replaysOnErrorSampleRate: 1.0, // 100% of sessions with errors

      // Release tracking
      release: `paiid-frontend@${process.env.NEXT_PUBLIC_VERCEL_GIT_COMMIT_SHA || 'dev'}`,

      // Integrations
      integrations: [
        new Sentry.BrowserTracing({
          // Next.js handles routing automatically via @sentry/nextjs
          // No React Router instrumentation needed
        }),
        new Sentry.Replay({
          // Mask all text and user input by default for privacy
          maskAllText: true,
          blockAllMedia: true,
        }),
      ],

      // Filter out sensitive data
      beforeSend(event, _hint) {
        // Remove Authorization headers
        if (event.request?.headers) {
          delete event.request.headers.Authorization;
          delete event.request.headers.authorization;
        }

        // Remove API tokens from breadcrumbs
        if (event.breadcrumbs) {
          event.breadcrumbs = event.breadcrumbs.map(breadcrumb => {
            if (breadcrumb.data?.url) {
              breadcrumb.data.url = breadcrumb.data.url.replace(/token=[^&]*/g, 'token=REDACTED');
            }
            return breadcrumb;
          });
        }

        return event;
      },

      // Ignore known non-critical errors
      ignoreErrors: [
        // Browser extensions
        'top.GLOBALS',
        'canvas.contentDocument',
        'MyApp_RemoveAllHighlights',
        'atomicFindClose',
        // Network errors (handled gracefully)
        'NetworkError',
        'Failed to fetch',
        // React hydration warnings (cosmetic)
        'Hydration failed',
        'There was an error while hydrating',
      ],

      // Don't send PII (personally identifiable information)
      sendDefaultPii: false,
    });

    sentryInitialized = true;
    console.info('[Sentry] ✅ Error tracking initialized');
  } catch (error) {
    console.error('[Sentry] ❌ Failed to initialize:', error);
  }
}

/**
 * Capture an exception manually
 */
export function captureException(error: Error, context?: Record<string, any>): void {
  if (!sentryInitialized) {
    console.error('[Sentry] Not initialized, logging error:', error);
    return;
  }

  Sentry.captureException(error, {
    contexts: context ? { custom: context } : undefined,
  });
}

/**
 * Capture a message (non-error event)
 */
export function captureMessage(message: string, level: 'info' | 'warning' | 'error' = 'info'): void {
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
    level: 'info',
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
