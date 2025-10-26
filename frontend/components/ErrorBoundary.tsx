import { Component, ErrorInfo, ReactNode } from "react";
import { logger } from "../lib/logger";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  errorCount: number;
}

/**
 * Error Boundary Component
 *
 * Catches JavaScript errors anywhere in the child component tree,
 * logs those errors, and displays a fallback UI instead of crashing.
 *
 * Usage:
 * <ErrorBoundary>
 *   <YourComponent />
 * </ErrorBoundary>
 */
export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorCount: 0,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    // Update state so next render shows fallback UI
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Log error to console
    logger.error("[ErrorBoundary] Caught error", error);
    logger.error("[ErrorBoundary] Error info", errorInfo);

    // Update state with error details and increment error count
    this.setState((prev) => ({
      error,
      errorInfo,
      errorCount: prev.errorCount + 1,
    }));

    // Send to Sentry if available
    try {
      // Dynamic import to avoid errors if Sentry not configured
      import("../lib/sentry")
        .then(({ captureException, isSentryEnabled }) => {
          if (isSentryEnabled()) {
            captureException(error, {
              react: {
                componentStack: errorInfo.componentStack,
              },
            });
            // eslint-disable-next-line no-console
            logger.info("[ErrorBoundary] Error sent to Sentry");
          }
        })
        .catch(() => {
          // Sentry not available, skip
        });
    } catch (sentryError) {
      logger.warn("[ErrorBoundary] Failed to send to Sentry", sentryError instanceof Error ? sentryError : undefined);
    }

    // Call optional error handler prop
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  handleReset = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      // Keep errorCount to track recurring errors
    });
  };

  handleReload = (): void => {
    window.location.reload();
  };

  handleGoBack = (): void => {
    window.history.back();
  };

  render(): ReactNode {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default fallback UI
      return (
        <div
          style={{
            position: "fixed",
            inset: 0,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            background: "rgba(0, 0, 0, 0.7)",
            backdropFilter: "blur(10px)",
            padding: "24px",
            zIndex: 9999,
          }}
        >
          <div
            style={{
              maxWidth: "600px",
              background: "rgba(30, 41, 59, 0.95)",
              backdropFilter: "blur(20px)",
              border: "1px solid rgba(71, 85, 105, 0.5)",
              borderRadius: "16px",
              padding: "32px",
              textAlign: "center",
              boxShadow: "0 20px 60px rgba(0, 0, 0, 0.5)",
            }}
          >
            <div style={{ fontSize: "64px", marginBottom: "16px" }}>⚠️</div>

            <h1
              style={{
                color: "#ef4444",
                fontSize: "24px",
                marginBottom: "16px",
                fontWeight: "bold",
              }}
            >
              Something Went Wrong
            </h1>

            <p
              style={{
                color: "#cbd5e1",
                marginBottom: "24px",
                lineHeight: "1.6",
                fontSize: "15px",
              }}
            >
              We encountered an unexpected error while rendering this component.
              Don&apos;t worry - your data is safe. Try refreshing the page or going back.
            </p>

            {this.state.error && (
              <details
                style={{
                  textAlign: "left",
                  marginBottom: "24px",
                  padding: "16px",
                  background: "rgba(15, 23, 42, 0.5)",
                  borderRadius: "8px",
                  fontSize: "14px",
                  color: "#94a3b8",
                }}
              >
                <summary style={{ cursor: "pointer", marginBottom: "8px", fontWeight: "600" }}>
                  Technical Details (for developers)
                </summary>
                <pre
                  style={{
                    overflowX: "auto",
                    whiteSpace: "pre-wrap",
                    wordBreak: "break-word",
                    margin: 0,
                  }}
                >
                  {this.state.error.toString()}
                  {this.state.errorInfo?.componentStack}
                </pre>
              </details>
            )}

            <div style={{ display: "flex", gap: "12px", justifyContent: "center", flexWrap: "wrap" }}>
              <button
                onClick={this.handleReset}
                style={{
                  background: "#3b82f6",
                  color: "white",
                  padding: "12px 24px",
                  borderRadius: "8px",
                  border: "none",
                  cursor: "pointer",
                  fontWeight: "500",
                  fontSize: "14px",
                }}
              >
                Try Again
              </button>

              <button
                onClick={this.handleReload}
                style={{
                  background: "rgba(71, 85, 105, 0.5)",
                  color: "white",
                  padding: "12px 24px",
                  borderRadius: "8px",
                  border: "1px solid rgba(148, 163, 184, 0.3)",
                  cursor: "pointer",
                  fontWeight: "500",
                  fontSize: "14px",
                }}
              >
                Reload Page
              </button>

              <button
                onClick={this.handleGoBack}
                style={{
                  background: "transparent",
                  color: "#94a3b8",
                  padding: "12px 24px",
                  borderRadius: "8px",
                  border: "1px solid rgba(148, 163, 184, 0.3)",
                  cursor: "pointer",
                  fontWeight: "500",
                  fontSize: "14px",
                }}
              >
                Go Back
              </button>
            </div>

            {this.state.errorCount > 2 && (
              <div
                style={{
                  marginTop: "24px",
                  padding: "12px",
                  background: "rgba(234, 179, 8, 0.1)",
                  border: "1px solid rgba(234, 179, 8, 0.3)",
                  borderRadius: "8px",
                  color: "#eab308",
                  fontSize: "14px",
                }}
              >
                ⚠️ This error has occurred {this.state.errorCount} times.
                Consider contacting support if the issue persists.
              </div>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
