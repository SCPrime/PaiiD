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

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { useSSE } from "./useSSE";

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
    heartbeatTimeout = 45,
    debug = false,
  } = options;

  const initialState = useRef<MarketStreamState>({
    prices: {},
    connected: false,
    connecting: false,
    error: null,
    lastUpdate: null,
    lastHeartbeat: null,
  });

  const [state, setState] = useState<MarketStreamState>(initialState.current);
  const [cacheBuster, setCacheBuster] = useState(() => Date.now());

  const normalizedSymbols = useMemo(() => {
    return Array.from(
      new Set(
        symbols.map((symbol) => symbol.trim().toUpperCase()).filter((symbol) => symbol.length > 0)
      )
    ).sort();
  }, [symbols]);

  const normalizedSymbolsKey = useMemo(() => normalizedSymbols.join(","), [normalizedSymbols]);

  useEffect(() => {
    setCacheBuster(Date.now());
  }, [normalizedSymbolsKey]);

  const streamUrl = useMemo(() => {
    if (normalizedSymbols.length === 0) {
      return null;
    }
    const params = new URLSearchParams({
      symbols: normalizedSymbols.join(","),
      t: String(cacheBuster),
    });
    return `/api/proxy/api/stream/prices?${params.toString()}`;
  }, [cacheBuster, normalizedSymbols]);

  const log = useCallback(
    (...args: unknown[]) => {
      if (debug) {
        // eslint-disable-next-line no-console
        console.info("[useMarketStream]", ...args);
      }
    },
    [debug]
  );

  const handlePriceUpdate = useCallback(
    (event: MessageEvent) => {
      try {
        const newPrices = JSON.parse(event.data) as Record<string, PriceData>;
        log("📈 Price update:", Object.keys(newPrices).length, "symbols");
        setState((prev) => ({
          ...prev,
          prices: { ...prev.prices, ...newPrices },
          lastUpdate: new Date(),
        }));
      } catch (error) {
        console.error("[useMarketStream] Error parsing price update:", error);
      }
    },
    [log]
  );

  const handleHeartbeat = useCallback(() => {
    const now = new Date();
    log("💓 Heartbeat received");
    setState((prev) => ({
      ...prev,
      lastHeartbeat: now,
    }));
  }, [log]);

  const handleServerError = useCallback(
    (event: MessageEvent) => {
      try {
        const payload = JSON.parse(event.data) as { error?: string };
        if (payload?.error) {
          console.error("[useMarketStream] Server error:", payload.error);
          setState((prev) => ({
            ...prev,
            error: payload.error ?? null,
            connected: false,
          }));
        }
      } catch (err) {
        log("Received non-JSON error event", err);
      }
    },
    [log]
  );

  const {
    connected,
    connecting,
    error: connectionError,
    lastHeartbeatAt,
    reconnect: sseReconnect,
  } = useSSE(streamUrl, {
    events: {
      price_update: handlePriceUpdate,
      heartbeat: handleHeartbeat,
      error: handleServerError,
    },
    heartbeatEvent: "heartbeat",
    autoReconnect,
    maxReconnectAttempts,
    debug,
  });

  useEffect(() => {
    if (!streamUrl) {
      setState(() => ({
        ...initialState.current,
        prices: {},
      }));
    }
  }, [streamUrl]);

  useEffect(() => {
    setState((prev) => {
      if (prev.connected === connected && prev.connecting === connecting) {
        return prev;
      }
      return {
        ...prev,
        connected,
        connecting,
      };
    });
  }, [connected, connecting]);

  useEffect(() => {
    if (connectionError) {
      setState((prev) => {
        if (prev.error === connectionError) {
          return prev;
        }
        return {
          ...prev,
          error: connectionError,
        };
      });
    } else if (connected) {
      setState((prev) => {
        if (prev.error === null) {
          return prev;
        }
        return {
          ...prev,
          error: null,
        };
      });
    }
  }, [connectionError, connected]);

  useEffect(() => {
    setState((prev) => {
      const prevTimestamp = prev.lastHeartbeat?.getTime() ?? null;
      const nextTimestamp = lastHeartbeatAt ? lastHeartbeatAt.getTime() : null;
      if (prevTimestamp === nextTimestamp) {
        return prev;
      }
      return {
        ...prev,
        lastHeartbeat: lastHeartbeatAt ?? null,
      };
    });
  }, [lastHeartbeatAt]);

  useEffect(() => {
    if (normalizedSymbols.length === 0) {
      setState((prev) => ({
        ...prev,
        prices: {},
      }));
      return;
    }

    setState((prev) => {
      const allowed = new Set(normalizedSymbols);
      const filteredEntries = Object.entries(prev.prices).filter(([symbol]) => allowed.has(symbol));
      if (filteredEntries.length === Object.keys(prev.prices).length) {
        return prev;
      }
      return {
        ...prev,
        prices: Object.fromEntries(filteredEntries),
      };
    });
  }, [normalizedSymbols]);

  useEffect(() => {
    if (heartbeatTimeout <= 0) {
      return;
    }

    const interval = setInterval(
      () => {
        let shouldReconnect = false;
        setState((prev) => {
          if (!prev.lastHeartbeat || !prev.connected) {
            return prev;
          }

          const secondsSinceHeartbeat = (Date.now() - prev.lastHeartbeat.getTime()) / 1000;
          if (secondsSinceHeartbeat <= heartbeatTimeout) {
            return prev;
          }

          log(`⚠️ Heartbeat timeout (${secondsSinceHeartbeat.toFixed(0)}s)`);
          shouldReconnect = true;
          return {
            ...prev,
            connected: false,
            error: "Heartbeat timeout - reconnecting...",
          };
        });

        if (shouldReconnect) {
          setCacheBuster(Date.now());
          sseReconnect();
        }
      },
      Math.min(Math.max(heartbeatTimeout * 500, 1000), 10000)
    );

    return () => {
      clearInterval(interval);
    };
  }, [heartbeatTimeout, log, sseReconnect]);

  const reconnect = useCallback(() => {
    log("🔄 Manual reconnect triggered");
    setCacheBuster(Date.now());
    sseReconnect();
  }, [log, sseReconnect]);

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
