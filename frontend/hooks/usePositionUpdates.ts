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
import { recordStreamEvent, StreamLogLevel } from "../utils/streamMonitoring";

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

  const updateCountRef = useRef(0);
  const heartbeatCountRef = useRef(0);

  const emitStreamEvent = useCallback(
    (
      event: string,
      message: string,
      level: StreamLogLevel = "info",
      context: Record<string, unknown> = {}
    ) => {
      recordStreamEvent({
        stream: "positions",
        event,
        message,
        level,
        context,
        debug,
      });
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
    emitStreamEvent("connect_start", "Connecting to position stream", "info", {
      url: "/api/proxy/stream/positions",
    });

    try {
      // Build SSE URL
      const url = `/api/proxy/stream/positions`;

      // Create EventSource
      const eventSource = new EventSource(url);
      eventSourceRef.current = eventSource;

      // Handle connection open
      eventSource.onopen = () => {
        emitStreamEvent("connected", "Connected to position stream", "info", {
          reconnectAttempts: reconnectAttemptsRef.current,
        });
        updateCountRef.current = 0;
        heartbeatCountRef.current = 0;
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
              emitStreamEvent(
                "heartbeat_timeout",
                "Heartbeat timeout detected",
                "warning",
                {
                  secondsSinceLastHeartbeat: timeSinceHeartbeat,
                  timeoutThreshold: heartbeatTimeout,
                }
              );

              // Trigger reconnect
              if (eventSourceRef.current) {
                eventSourceRef.current.close();
                eventSourceRef.current = null;
              }

              if (autoReconnect && reconnectAttemptsRef.current < maxReconnectAttempts) {
                reconnectAttemptsRef.current++;
                emitStreamEvent(
                  "heartbeat_reconnect",
                  "Scheduling reconnect due to heartbeat timeout",
                  "warning",
                  {
                    attempt: reconnectAttemptsRef.current,
                    maxReconnectAttempts,
                  }
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
          updateCountRef.current += 1;

          if (updateCountRef.current === 1 || updateCountRef.current % 10 === 0) {
            emitStreamEvent(
              "position_update",
              "Received streamed position payload",
              "info",
              {
                positionsCount: newPositions.length,
                updateSequence: updateCountRef.current,
              }
            );
          }

          setState((prev) => ({
            ...prev,
            positions: newPositions,
            lastUpdate: new Date(),
          }));
        } catch (error) {
          emitStreamEvent("parse_error", "Error parsing position update", "error", {
            rawData: event.data,
            error: error instanceof Error ? error.message : String(error),
          });
        }
      });

      // Handle heartbeat (keep-alive and timeout detection)
      eventSource.addEventListener("heartbeat", (_event) => {
        const now = new Date();
        heartbeatCountRef.current += 1;

        if (heartbeatCountRef.current === 1 || heartbeatCountRef.current % 12 === 0) {
          emitStreamEvent("heartbeat", "Heartbeat received", "info", {
            heartbeatSequence: heartbeatCountRef.current,
          });
        }
        setState((prev) => ({
          ...prev,
          lastHeartbeat: now,
        }));
      });

      // Handle errors
      eventSource.addEventListener("error", (event) => {
        try {
          const errorData = JSON.parse((event as MessageEvent).data);
          emitStreamEvent("server_error", "Position stream returned error", "error", {
            error: errorData.error,
          });
          setState((prev) => ({
            ...prev,
            error: errorData.error,
            connected: false,
          }));
        } catch {
          // Not a formatted error event, just log it
          emitStreamEvent("generic_error", "Received unformatted error event", "warning");
        }
      });

      // Handle connection errors/close
      eventSource.onerror = (_error) => {
        emitStreamEvent("connection_error", "Connection error or closed", "warning");

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

          emitStreamEvent("reconnect_scheduled", "Scheduling reconnect attempt", "warning", {
            delayMs: backoffTime,
            attempt: reconnectAttemptsRef.current,
            maxReconnectAttempts,
          });

          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, backoffTime);
        } else if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
          emitStreamEvent("reconnect_limit", "Max reconnect attempts reached", "error", {
            maxReconnectAttempts,
          });
          setState((prev) => ({
            ...prev,
            error: "Max reconnect attempts reached. Please refresh the page.",
          }));
        }
      };
    } catch (error: any) {
      emitStreamEvent("connection_exception", "Connection exception thrown", "error", {
        error: error?.message || String(error),
      });
      setState((prev) => ({
        ...prev,
        connected: false,
        connecting: false,
        error: error.message || "Failed to connect",
      }));
    }
  }, [autoReconnect, emitStreamEvent, heartbeatTimeout, maxReconnectAttempts]);

  // Manual reconnect method
  const reconnect = useCallback(() => {
    emitStreamEvent("manual_reconnect", "Manual reconnect triggered", "info");
    reconnectAttemptsRef.current = 0; // Reset counter on manual reconnect
    connect();
  }, [connect, emitStreamEvent]);

  // Connect on mount
  useEffect(() => {
    connect();

    // Cleanup on unmount
    return () => {
      emitStreamEvent("cleanup", "Cleaning up position stream", "info");
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
  }, [connect, emitStreamEvent]);

  return {
    ...state,
    reconnect,
  };
}
