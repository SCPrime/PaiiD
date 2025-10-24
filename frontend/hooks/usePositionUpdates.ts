/**
 * usePositionUpdates Hook
 *
 * React hook for real-time position updates via Server-Sent Events (SSE).
 *
 * Features:
 * - Subscribes to position updates from backend
 * - Auto-reconnects on disconnect
 * - Provides connection status
 * - Returns latest positions with P&L
 *
 * Phase 5.B.2 - Real-Time UI Updates
 */

import { useEffect, useState, useCallback, useRef } from "react";

/**
 * Quality Engineering ownership sourced from BUG_REPORT_OPTIONS_500.md.
 * Provides acceptance checklist items used by QA dashboards and lifecycle logs.
 */
export const POSITION_STREAM_QE = {
  owner: "Dr. Cursor Claude (Quality Engineering)",
  acceptanceChecklist: [
    "Verify /api/proxy/stream/positions opens SSE channel without 500 errors.",
    "Heartbeat events arrive within the configured heartbeatTimeout (<=45s).",
    "Auto-reconnect succeeds within maxReconnectAttempts when the stream drops.",
  ],
} as const;

export interface Position {
  symbol: string;
  qty: number;
  avgEntryPrice: number;
  currentPrice: number;
  marketValue: number;
  unrealizedPL: number;
  unrealizedPLPercent: number;
  side: "long" | "short";
  dayChange: number;
  dayChangePercent: number;
}

export interface PositionStreamState {
  positions: Position[];
  connected: boolean;
  connecting: boolean;
  error: string | null;
  lastUpdate: Date | null;
  lastHeartbeat: Date | null;
}

export interface UsePositionUpdatesOptions {
  /** Auto-reconnect on disconnect (default: true) */
  autoReconnect?: boolean;
  /** Max reconnect attempts (default: 5) */
  maxReconnectAttempts?: number;
  /** Heartbeat timeout in seconds (default: 45) - reconnect if no heartbeat received */
  heartbeatTimeout?: number;
  /** Enable debug logging (default: false) */
  debug?: boolean;
}

/**
 * Hook for streaming real-time position updates via SSE
 *
 * @param options Configuration options
 * @returns Object with positions, connection status, and control methods
 *
 * @example
 * const { positions, connected, error } = usePositionUpdates();
 *
 * // Use positions in component
 * const totalPL = positions.reduce((sum, p) => sum + p.unrealizedPL, 0);
 * console.info(`Total P&L: $${totalPL.toFixed(2)}`);
 */
export function usePositionUpdates(
  options: UsePositionUpdatesOptions = {}
): PositionStreamState & { reconnect: () => void } {
  const {
    autoReconnect = true,
    maxReconnectAttempts = 5,
    heartbeatTimeout = 45, // 45 seconds default (3x heartbeat interval)
    debug = false,
  } = options;

  const [state, setState] = useState<PositionStreamState>({
    positions: [],
    connected: false,
    connecting: false,
    error: null,
    lastUpdate: null,
    lastHeartbeat: null,
  });

  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const heartbeatCheckIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const qeLifecycleMetaLoggedRef = useRef(false);

  const lifecycleLog = useCallback(
    (event: string, detail: Record<string, unknown> = {}) => {
      const payload: Record<string, unknown> = {
        event,
        detail,
        owner: POSITION_STREAM_QE.owner,
        timestamp: new Date().toISOString(),
      };

      if (!qeLifecycleMetaLoggedRef.current) {
        payload.acceptanceChecklist = POSITION_STREAM_QE.acceptanceChecklist;
        qeLifecycleMetaLoggedRef.current = true;
      }

      console.info("[usePositionUpdates:lifecycle]", payload);
    },
    []
  );

  const log = useCallback(
    (...args: any[]) => {
      if (debug) {
        console.info("[usePositionUpdates]", ...args);
      }
    },
    [debug]
  );

  const connect = useCallback(() => {
    // Clean up existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }

    // Clear any pending reconnect
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    // Clear heartbeat check interval
    if (heartbeatCheckIntervalRef.current) {
      clearInterval(heartbeatCheckIntervalRef.current);
      heartbeatCheckIntervalRef.current = null;
    }

    setState((prev) => ({ ...prev, connecting: true, error: null }));
    lifecycleLog("connect:start", {
      autoReconnect,
      maxReconnectAttempts,
    });
    log("Connecting to position stream");

    try {
      // Build SSE URL
      const url = `/api/proxy/stream/positions`;

      lifecycleLog("connect:url", { url });

      // Create EventSource
      const eventSource = new EventSource(url);
      eventSourceRef.current = eventSource;

      // Handle connection open
      eventSource.onopen = () => {
        lifecycleLog("connect:open", { readyState: eventSource.readyState });
        log("✅ Connected to position stream");
        const now = new Date();
        setState((prev) => ({
          ...prev,
          connected: true,
          connecting: false,
          error: null,
          lastHeartbeat: now, // Initialize heartbeat timestamp on connect
        }));
        reconnectAttemptsRef.current = 0; // Reset reconnect counter on success

        // Start heartbeat timeout checker
        heartbeatCheckIntervalRef.current = setInterval(() => {
          setState((currentState) => {
            if (!currentState.lastHeartbeat || !currentState.connected) {
              return currentState;
            }

            const timeSinceHeartbeat = (Date.now() - currentState.lastHeartbeat.getTime()) / 1000;

            if (timeSinceHeartbeat > heartbeatTimeout) {
              const timeoutSeconds = Number(timeSinceHeartbeat.toFixed(0));
              lifecycleLog("event:heartbeat-timeout", { seconds: timeoutSeconds });
              log(`⚠️ Heartbeat timeout (${timeoutSeconds}s since last heartbeat)`);

              // Trigger reconnect
              if (eventSourceRef.current) {
                eventSourceRef.current.close();
                eventSourceRef.current = null;
              }

              if (autoReconnect && reconnectAttemptsRef.current < maxReconnectAttempts) {
                reconnectAttemptsRef.current++;
                lifecycleLog("connect:retry", {
                  attempt: reconnectAttemptsRef.current,
                  maxReconnectAttempts,
                  reason: "heartbeat-timeout",
                });
                log(
                  `🔄 Reconnecting due to heartbeat timeout (attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts})`
                );
                connect();
              }

              return {
                ...currentState,
                connected: false,
                error: "Heartbeat timeout - reconnecting...",
              };
            }

            return currentState;
          });
        }, 10000); // Check every 10 seconds
      };

      // Handle position updates
      eventSource.addEventListener("position_update", (event) => {
        try {
          const newPositions = JSON.parse(event.data) as Position[];
          log("📊 Position update:", newPositions.length, "positions");
          
          setState((prev) => ({
            ...prev,
            positions: newPositions,
            lastUpdate: new Date(),
          }));
        } catch (error) {
          console.error("[usePositionUpdates] Error parsing position update:", error);
        }
      });

      // Handle heartbeat (keep-alive and timeout detection)
      eventSource.addEventListener("heartbeat", (_event) => {
        const now = new Date();
        log("💓 Heartbeat received");
        setState((prev) => ({
          ...prev,
          lastHeartbeat: now,
        }));
      });

      // Handle errors
      eventSource.addEventListener("error", (event) => {
        try {
          const errorData = JSON.parse((event as MessageEvent).data);
          lifecycleLog("event:error", { message: errorData.error });
          console.error("[usePositionUpdates] Server error:", errorData.error);
          setState((prev) => ({
            ...prev,
            error: errorData.error,
            connected: false,
          }));
        } catch {
          // Not a formatted error event, just log it
          lifecycleLog("event:error", { message: "unformatted error event" });
          log("Error event (likely connection issue)");
        }
      });

      // Handle connection errors/close
      eventSource.onerror = (_error) => {
        lifecycleLog("connect:error", {
          attempt: reconnectAttemptsRef.current,
          autoReconnect,
        });
        log("❌ Connection error or closed");

        setState((prev) => ({
          ...prev,
          connected: false,
          connecting: false,
          error: "Connection lost",
        }));

        // Close the connection
        eventSource.close();
        eventSourceRef.current = null;

        // Attempt reconnect if enabled
        if (autoReconnect && reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++;
          const backoffTime = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000); // Max 30s

          lifecycleLog("connect:retry-scheduled", {
            attempt: reconnectAttemptsRef.current,
            delaySeconds: backoffTime / 1000,
            maxReconnectAttempts,
          });
          log(`⏳ Reconnecting in ${backoffTime / 1000}s (attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts})`);

          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, backoffTime);
        } else if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
          lifecycleLog("connect:retry-exhausted", {
            attempt: reconnectAttemptsRef.current,
            maxReconnectAttempts,
          });
          setState((prev) => ({
            ...prev,
            error: "Max reconnect attempts reached. Please refresh the page.",
          }));
        }
      };
    } catch (error: any) {
      lifecycleLog("connect:exception", { message: error?.message ?? "unknown" });
      console.error("[usePositionUpdates] Connection error:", error);
      setState((prev) => ({
        ...prev,
        connected: false,
        connecting: false,
        error: error.message || "Failed to connect",
      }));
    }
  }, [autoReconnect, lifecycleLog, log, maxReconnectAttempts]);

  // Manual reconnect method
  const reconnect = useCallback(() => {
    lifecycleLog("connect:manual", {
      previousAttempts: reconnectAttemptsRef.current,
    });
    log("🔄 Manual reconnect triggered");
    reconnectAttemptsRef.current = 0; // Reset counter on manual reconnect
    connect();
  }, [connect, lifecycleLog, log]);

  // Connect on mount
  useEffect(() => {
    lifecycleLog("hook:mount", { debug });
    connect();

    // Cleanup on unmount
    return () => {
      lifecycleLog("hook:unmount", {
        hadActiveConnection: Boolean(eventSourceRef.current),
      });
      log("🧹 Cleaning up position stream");
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
      if (heartbeatCheckIntervalRef.current) {
        clearInterval(heartbeatCheckIntervalRef.current);
        heartbeatCheckIntervalRef.current = null;
      }
    };
  }, [connect, debug, lifecycleLog, log]);

  return {
    ...state,
    reconnect,
  };
}
