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

import { useEffect, useState, useCallback, useRef } from 'react';

export interface PriceData {
  price: number;
  timestamp: string;
  type: 'trade' | 'quote';
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
 * console.log(`AAPL: $${aaplPrice.toFixed(2)}`);
 */
export function useMarketStream(
  symbols: string[],
  options: UseMarketStreamOptions = {}
): MarketStreamState & { reconnect: () => void } {
  const {
    autoReconnect = true,
    maxReconnectAttempts = 5,
    heartbeatTimeout = 45,  // 45 seconds default (3x heartbeat interval)
    debug = false
  } = options;

  const [state, setState] = useState<MarketStreamState>({
    prices: {},
    connected: false,
    connecting: false,
    error: null,
    lastUpdate: null,
    lastHeartbeat: null
  });

  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const heartbeatCheckIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const log = useCallback((...args: any[]) => {
    if (debug) {
      console.log('[useMarketStream]', ...args);
    }
  }, [debug]);

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
      log('No symbols to subscribe to');
      return;
    }

    setState(prev => ({ ...prev, connecting: true, error: null }));
    log('Connecting to price stream:', symbols);

    try {
      // Build SSE URL
      const symbolsParam = symbols.join(',');
      const url = `/api/proxy/api/stream/prices?symbols=${symbolsParam}`;

      // Create EventSource
      const eventSource = new EventSource(url);
      eventSourceRef.current = eventSource;

      // Handle connection open
      eventSource.onopen = () => {
        log('✅ Connected to price stream');
        const now = new Date();
        setState(prev => ({
          ...prev,
          connected: true,
          connecting: false,
          error: null,
          lastHeartbeat: now  // Initialize heartbeat timestamp on connect
        }));
        reconnectAttemptsRef.current = 0;  // Reset reconnect counter on success

        // Start heartbeat timeout checker
        heartbeatCheckIntervalRef.current = setInterval(() => {
          setState(currentState => {
            if (!currentState.lastHeartbeat || !currentState.connected) {
              return currentState;
            }

            const timeSinceHeartbeat = (Date.now() - currentState.lastHeartbeat.getTime()) / 1000;

            if (timeSinceHeartbeat > heartbeatTimeout) {
              log(`⚠️ Heartbeat timeout (${timeSinceHeartbeat.toFixed(0)}s since last heartbeat)`);

              // Trigger reconnect
              if (eventSourceRef.current) {
                eventSourceRef.current.close();
                eventSourceRef.current = null;
              }

              if (autoReconnect && reconnectAttemptsRef.current < maxReconnectAttempts) {
                reconnectAttemptsRef.current++;
                log(`🔄 Reconnecting due to heartbeat timeout (attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts})`);
                connect();
              }

              return {
                ...currentState,
                connected: false,
                error: 'Heartbeat timeout - reconnecting...'
              };
            }

            return currentState;
          });
        }, 10000);  // Check every 10 seconds
      };

      // Handle price updates
      eventSource.addEventListener('price_update', (event) => {
        try {
          const newPrices = JSON.parse(event.data) as Record<string, PriceData>;
          log('📈 Price update:', Object.keys(newPrices).length, 'symbols');

          setState(prev => ({
            ...prev,
            prices: { ...prev.prices, ...newPrices },
            lastUpdate: new Date()
          }));
        } catch (error) {
          console.error('[useMarketStream] Error parsing price update:', error);
        }
      });

      // Handle heartbeat (keep-alive and timeout detection)
      eventSource.addEventListener('heartbeat', (_event) => {
        const now = new Date();
        log('💓 Heartbeat received');
        setState(prev => ({
          ...prev,
          lastHeartbeat: now
        }));
      });

      // Handle errors
      eventSource.addEventListener('error', (event) => {
        try {
          const errorData = JSON.parse((event as MessageEvent).data);
          console.error('[useMarketStream] Server error:', errorData.error);
          setState(prev => ({
            ...prev,
            error: errorData.error,
            connected: false
          }));
        } catch {
          // Not a formatted error event, just log it
          log('Error event (likely connection issue)');
        }
      });

      // Handle connection errors/close
      eventSource.onerror = (_error) => {
        log('❌ Connection error or closed');

        setState(prev => ({
          ...prev,
          connected: false,
          connecting: false,
          error: 'Connection lost'
        }));

        // Close the connection
        eventSource.close();
        eventSourceRef.current = null;

        // Attempt reconnect if enabled
        if (autoReconnect && reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++;
          const backoffTime = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000);  // Max 30s

          log(`⏳ Reconnecting in ${backoffTime/1000}s (attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts})`);

          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, backoffTime);
        } else if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
          setState(prev => ({
            ...prev,
            error: 'Max reconnect attempts reached. Please refresh the page.'
          }));
        }
      };

    } catch (error: any) {
      console.error('[useMarketStream] Connection error:', error);
      setState(prev => ({
        ...prev,
        connected: false,
        connecting: false,
        error: error.message || 'Failed to connect'
      }));
    }
  }, [symbols, autoReconnect, maxReconnectAttempts, log]);

  // Manual reconnect method
  const reconnect = useCallback(() => {
    log('🔄 Manual reconnect triggered');
    reconnectAttemptsRef.current = 0;  // Reset counter on manual reconnect
    connect();
  }, [connect, log]);

  // Connect on mount or when symbols change
  useEffect(() => {
    if (symbols.length > 0) {
      connect();
    }

    // Cleanup on unmount
    return () => {
      log('🧹 Cleaning up market stream');
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
  }, [symbols.join(','), connect, log]);  // Re-connect when symbols change

  return {
    ...state,
    reconnect
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
 * console.log(`AAPL: $${(price ?? 0).toFixed(2)}`);
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
    error
  };
}
