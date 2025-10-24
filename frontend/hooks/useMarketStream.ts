/**
 * useMarketStream Hook
 *
 * React hook for real-time market data streaming via Server-Sent Events (SSE).
 *
 * Features:
 * - Subscribes to price updates for specified symbols
 * - Auto-reconnects on disconnect
 * - Provides connection status
 * - Returns latest prices for all subscribed symbols
 *
 * Phase 2.A - Real-Time Data Implementation
 */

import { useEffect, useState, useCallback, useRef } from "react";
import { recordStreamEvent, StreamLogLevel } from "../utils/streamMonitoring";

export interface PriceData {
  price: number;
  timestamp: string;
  type: "trade" | "quote";
  bid?: number;
  ask?: number;
  size?: number;
}

export interface MarketStreamState {
  prices: Record<string, PriceData>;
  connected: boolean;
  connecting: boolean;
  error: string | null;
  lastUpdate: Date | null;
  lastHeartbeat: Date | null;
}

export interface UseMarketStreamOptions {
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
 * Hook for streaming real-time market prices via SSE
 *
 * @param symbols Array of stock symbols to subscribe to (e.g., ['AAPL', 'MSFT'])
 * @param options Configuration options
 * @returns Object with prices, connection status, and control methods
 *
 * @example
 * const { prices, connected, error } = useMarketStream(['AAPL', 'MSFT', 'TSLA']);
 *
 * // Use prices in component
 * const aaplPrice = prices['AAPL']?.price ?? 0;
 * console.info(`AAPL: $${aaplPrice.toFixed(2)}`);
 */
export function useMarketStream(
  symbols: string[],
  options: UseMarketStreamOptions = {}
): MarketStreamState & { reconnect: () => void } {
  const {
    autoReconnect = true,
    maxReconnectAttempts = 5,
    heartbeatTimeout = 45, // 45 seconds default (3x heartbeat interval)
    debug = false,
  } = options;

  const symbolKey = symbols.join(",");

  const [state, setState] = useState<MarketStreamState>({
    prices: {},
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
        stream: "market-prices",
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

    // Don't connect if no symbols
    if (symbols.length === 0) {
      emitStreamEvent("no_symbols", "No symbols to subscribe to", "info", {
        symbols,
      });
      return;
    }

    setState((prev) => ({ ...prev, connecting: true, error: null }));
    emitStreamEvent("connect_start", "Connecting to price stream", "info", { symbols });

    try {
      // Build SSE URL
      const symbolsParam = symbols.join(",");
      const url = `/api/proxy/api/stream/prices?symbols=${symbolsParam}`;

      // Create EventSource
      const eventSource = new EventSource(url);
      eventSourceRef.current = eventSource;

      // Handle connection open
      eventSource.onopen = () => {
        emitStreamEvent("connected", "Connected to price stream", "info", {
          reconnectAttempts: reconnectAttemptsRef.current,
          symbols,
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
              emitStreamEvent("heartbeat_timeout", "Heartbeat timeout detected", "warning", {
                secondsSinceLastHeartbeat: timeSinceHeartbeat,
                timeoutThreshold: heartbeatTimeout,
                symbols,
              });

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
                    symbols,
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

      // Handle price updates
      eventSource.addEventListener("price_update", (event) => {
        try {
          const newPrices = JSON.parse(event.data) as Record<string, PriceData>;
          updateCountRef.current += 1;

          if (updateCountRef.current === 1 || updateCountRef.current % 10 === 0) {
            emitStreamEvent("price_update", "Received streamed price payload", "info", {
              symbols: Object.keys(newPrices),
              updateSequence: updateCountRef.current,
            });
          }

          setState((prev) => ({
            ...prev,
            prices: { ...prev.prices, ...newPrices },
            lastUpdate: new Date(),
          }));
        } catch (error) {
          emitStreamEvent("parse_error", "Error parsing price update", "error", {
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
            symbols,
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
          emitStreamEvent("server_error", "Market stream returned error", "error", {
            error: errorData.error,
            symbols,
          });
          setState((prev) => ({
            ...prev,
            error: errorData.error,
            connected: false,
          }));
        } catch {
          // Not a formatted error event, just log it
          emitStreamEvent("generic_error", "Received unformatted error event", "warning", {
            symbols,
          });
        }
      });

      // Handle connection errors/close
      eventSource.onerror = (_error) => {
        emitStreamEvent("connection_error", "Connection error or closed", "warning", {
          symbols,
        });

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
            symbols,
          });

          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, backoffTime);
        } else if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
          emitStreamEvent("reconnect_limit", "Max reconnect attempts reached", "error", {
            maxReconnectAttempts,
            symbols,
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
        symbols,
      });
      setState((prev) => ({
        ...prev,
        connected: false,
        connecting: false,
        error: error.message || "Failed to connect",
      }));
    }
  }, [symbols, autoReconnect, emitStreamEvent, heartbeatTimeout, maxReconnectAttempts]);

  // Manual reconnect method
  const reconnect = useCallback(() => {
    emitStreamEvent("manual_reconnect", "Manual reconnect triggered", "info", {
      symbols,
    });
    reconnectAttemptsRef.current = 0; // Reset counter on manual reconnect
    connect();
  }, [connect, emitStreamEvent, symbols]);

  // Connect on mount or when symbols change
  useEffect(() => {
    if (symbols.length > 0) {
      connect();
    }

    // Cleanup on unmount
    return () => {
      emitStreamEvent("cleanup", "Cleaning up market stream", "info", {
        symbols,
      });
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
  }, [symbolKey, connect, emitStreamEvent]); // Re-connect when symbols change

  return {
    ...state,
    reconnect,
  };
}

/**
 * Hook for getting a single symbol's price
 *
 * @param symbol Single stock symbol
 * @returns Price data for that symbol
 *
 * @example
 * const { price, connected } = useSymbolPrice('AAPL');
 * console.info(`AAPL: $${(price ?? 0).toFixed(2)}`);
 */
export function useSymbolPrice(symbol: string) {
  const { prices, connected, connecting, error } = useMarketStream([symbol]);
  const priceData = prices[symbol];

  return {
    price: priceData?.price ?? null,
    bid: priceData?.bid ?? null,
    ask: priceData?.ask ?? null,
    timestamp: priceData?.timestamp ?? null,
    type: priceData?.type ?? null,
    connected,
    connecting,
    error,
  };
}
