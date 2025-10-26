/**
 * WebSocket Hook for Real-Time Market Data and Portfolio Updates
 *
 * Provides a React hook for managing WebSocket connections with automatic
 * reconnection, subscription management, and typed message handling.
 *
 * @module useWebSocket
 * @example
 * const {
 *   isConnected,
 *   marketData,
 *   subscribe,
 *   disconnect
 * } = useWebSocket({
 *   url: 'ws://localhost:8001/ws',
 *   userId: 'user123',
 *   autoConnect: true
 * });
 *
 * // Subscribe to market data
 * useEffect(() => {
 *   if (isConnected) {
 *     subscribe(['AAPL', 'MSFT', 'GOOGL']);
 *   }
 * }, [isConnected]);
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { logger } from "../lib/logger";

/**
 * WebSocket message structure
 * @interface WebSocketMessage
 * @property {string} type - Message type (market_data, portfolio_update, etc.)
 * @property {unknown} [data] - Message payload
 * @property {string} [symbol] - Stock symbol for market data messages
 * @property {string} timestamp - ISO timestamp of message
 */
export interface WebSocketMessage {
  type: string;
  data?: unknown;
  symbol?: string;
  timestamp: string;
}

/**
 * Real-time market data for a symbol
 * @interface MarketData
 * @property {string} symbol - Stock ticker symbol
 * @property {number} price - Current price
 * @property {number} change - Price change from previous close
 * @property {number} change_percent - Percentage change from previous close
 * @property {number} volume - Trading volume
 * @property {number} high - Day's high price
 * @property {number} low - Day's low price
 * @property {number} open - Opening price
 * @property {number} previous_close - Previous day's closing price
 * @property {string} timestamp - ISO timestamp of quote
 * @property {string} source - Data source (tradier, alpaca, etc.)
 */
export interface MarketData {
  symbol: string;
  price: number;
  change: number;
  change_percent: number;
  volume: number;
  high: number;
  low: number;
  open: number;
  previous_close: number;
  timestamp: string;
  source: string;
}

export interface PortfolioUpdate {
  total_value: number;
  total_change: number;
  total_change_percent: number;
  positions: Array<{
    symbol: string;
    quantity: number;
    current_price: number;
    market_value: number;
    unrealized_pnl: number;
    unrealized_pnl_percent: number;
  }>;
}

export interface PositionUpdate {
  symbol: string;
  quantity: number;
  current_price: number;
  market_value: number;
  unrealized_pnl: number;
  unrealized_pnl_percent: number;
  timestamp: string;
}

export interface TradingAlert {
  type: "price_alert" | "volume_alert" | "news_alert" | "system_alert";
  symbol?: string;
  message: string;
  severity: "info" | "warning" | "error" | "success";
  timestamp: string;
}

/**
 * Connection status types for WebSocket
 */
export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error' | 'reconnecting';

/**
 * Configuration options for WebSocket hook
 * @interface UseWebSocketOptions
 * @property {string} url - WebSocket server URL
 * @property {string} userId - User ID for authentication
 * @property {boolean} [autoConnect=true] - Auto-connect on mount
 * @property {number} [reconnectInterval=5000] - Milliseconds between reconnect attempts
 * @property {number} [maxReconnectAttempts=5] - Maximum reconnection attempts
 */
interface UseWebSocketOptions {
  url: string;
  userId: string;
  autoConnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

/**
 * Return value from useWebSocket hook
 * @interface UseWebSocketReturn
 * @property {ConnectionStatus} status - Current connection status
 * @property {boolean} isConnected - WebSocket connection status
 * @property {boolean} isConnecting - Currently attempting to connect
 * @property {boolean} isReconnecting - Currently attempting to reconnect
 * @property {string | null} error - Error message if connection failed
 * @property {Map<string, MarketData>} marketData - Real-time market data by symbol
 * @property {PortfolioUpdate | null} portfolioUpdate - Latest portfolio update
 * @property {Map<string, PositionUpdate>} positionUpdates - Position updates by symbol
 * @property {TradingAlert[]} tradingAlerts - List of trading alerts (max 50)
 * @property {(symbols: string[]) => void} subscribe - Subscribe to symbol updates
 * @property {(symbols: string[]) => void} unsubscribe - Unsubscribe from symbol updates
 * @property {(message: WebSocketMessage) => void} sendMessage - Send custom message
 * @property {() => void} connect - Manually connect to WebSocket
 * @property {() => void} disconnect - Manually disconnect from WebSocket
 */
interface UseWebSocketReturn {
  status: ConnectionStatus;
  isConnected: boolean;
  isConnecting: boolean;
  isReconnecting: boolean;
  error: string | null;
  marketData: Map<string, MarketData>;
  portfolioUpdate: PortfolioUpdate | null;
  positionUpdates: Map<string, PositionUpdate>;
  tradingAlerts: TradingAlert[];
  subscribe: (symbols: string[]) => void;
  unsubscribe: (symbols: string[]) => void;
  sendMessage: (message: WebSocketMessage) => void;
  connect: () => void;
  disconnect: () => void;
}

/**
 * Custom React hook for managing WebSocket connections
 *
 * Handles connection lifecycle, automatic reconnection, message routing,
 * and subscription management for real-time market data and portfolio updates.
 *
 * @param {UseWebSocketOptions} options - WebSocket configuration
 * @returns {UseWebSocketReturn} WebSocket state and control functions
 *
 * @example
 * const {
 *   isConnected,
 *   marketData,
 *   portfolioUpdate,
 *   subscribe,
 *   unsubscribe
 * } = useWebSocket({
 *   url: 'ws://localhost:8001/ws',
 *   userId: 'user_123',
 *   autoConnect: true,
 *   reconnectInterval: 3000,
 *   maxReconnectAttempts: 10
 * });
 */
export const useWebSocket = ({
  url,
  userId,
  autoConnect = true,
  reconnectInterval = 5000,
  maxReconnectAttempts = 5,
}: UseWebSocketOptions): UseWebSocketReturn => {
  const [status, setStatus] = useState<ConnectionStatus>('disconnected');
  const [error, setError] = useState<string | null>(null);
  const [marketData, setMarketData] = useState<Map<string, MarketData>>(new Map());
  const [portfolioUpdate, setPortfolioUpdate] = useState<PortfolioUpdate | null>(null);
  const [positionUpdates, setPositionUpdates] = useState<Map<string, PositionUpdate>>(new Map());
  const [tradingAlerts, setTradingAlerts] = useState<TradingAlert[]>([]);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const subscribedSymbolsRef = useRef<Set<string>>(new Set());

  // Derived states for backwards compatibility
  const isConnected = status === 'connected';
  const isConnecting = status === 'connecting';
  const isReconnecting = status === 'reconnecting';

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setStatus('connecting');
    setError(null);

    try {
      const ws = new WebSocket(`${url}?user_id=${userId}`);
      wsRef.current = ws;

      ws.onopen = () => {
        logger.info("WebSocket connected");
        setStatus('connected');
        setError(null);
        reconnectAttemptsRef.current = 0;

        // Resubscribe to previously subscribed symbols
        if (subscribedSymbolsRef.current.size > 0) {
          ws.send(
            JSON.stringify({
              type: "subscribe",
              symbols: Array.from(subscribedSymbolsRef.current),
            })
          );
        }
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          handleMessage(message);
        } catch (err) {
          logger.error("Error parsing WebSocket message", err);
        }
      };

      ws.onclose = (event) => {
        logger.info("WebSocket disconnected", { code: event.code, reason: event.reason });
        setStatus('disconnected');

        // Attempt to reconnect if not a manual disconnect
        if (event.code !== 1000 && reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++;
          setStatus('reconnecting');
          setError('Connection lost. Attempting to reconnect...');
          logger.info(
            `Attempting to reconnect (${reconnectAttemptsRef.current}/${maxReconnectAttempts})...`
          );

          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectInterval);
        } else if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
          setStatus('error');
          setError('Unable to establish connection after multiple attempts. Please refresh the page.');
        }
      };

      ws.onerror = () => {
        logger.error("WebSocket error");
        setStatus('error');

        // User-friendly error messages based on online status
        const errorMessage = navigator.onLine
          ? 'Real-time connection failed. Retrying automatically...'
          : 'You appear to be offline. Connection will resume when online.';

        setError(errorMessage);
      };
    } catch (err) {
      logger.error("Error creating WebSocket", err);
      setStatus('error');
      setError('Failed to create real-time connection. Please try refreshing the page.');
    }
  }, [url, userId, reconnectInterval, maxReconnectAttempts]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close(1000, "Manual disconnect");
      wsRef.current = null;
    }

    setStatus('disconnected');
    setError(null);
    reconnectAttemptsRef.current = 0;
  }, []);

  const handleMessage = useCallback((message: WebSocketMessage) => {
    switch (message.type) {
      case "connection":
        logger.info("WebSocket connection established", { message });
        break;

      case "market_data":
        if (message.symbol && message.data) {
          setMarketData((prev) => {
            const newMap = new Map(prev);
            newMap.set(message.symbol!, message.data as MarketData);
            return newMap;
          });
        }
        break;

      case "portfolio_update":
        if (message.data) {
          setPortfolioUpdate(message.data as PortfolioUpdate);
        }
        break;

      case "position_update":
        if (message.data) {
          const positionData = message.data as PositionUpdate;
          setPositionUpdates((prev) => {
            const newMap = new Map(prev);
            newMap.set(positionData.symbol, positionData);
            return newMap;
          });
        }
        break;

      case "trading_alert":
        if (message.data) {
          setTradingAlerts((prev) => {
            const newAlert = message.data as TradingAlert;
            return [newAlert, ...prev].slice(0, 50); // Keep last 50 alerts
          });
        }
        break;

      case "subscription_confirmed":
        if (message.data && typeof message.data === 'object' && 'symbols' in message.data) {
          logger.info("Subscription confirmed for symbols", { symbols: (message.data as { symbols: string[] }).symbols });
        }
        break;

      case "pong":
        // Handle ping/pong for connection health
        break;

      default:
        logger.info("Unknown message type", { type: message.type });
    }
  }, []);

  const subscribe = useCallback((symbols: string[]) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      const newSymbols = symbols.filter((s) => !subscribedSymbolsRef.current.has(s));
      if (newSymbols.length > 0) {
        subscribedSymbolsRef.current = new Set([...Array.from(subscribedSymbolsRef.current), ...newSymbols]);
        wsRef.current.send(
          JSON.stringify({
            type: "subscribe",
            symbols: newSymbols,
          })
        );
      }
    }
  }, []);

  const unsubscribe = useCallback((symbols: string[]) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      symbols.forEach((symbol) => subscribedSymbolsRef.current.delete(symbol));
      wsRef.current.send(
        JSON.stringify({
          type: "unsubscribe",
          symbols,
        })
      );
    }
  }, []);

  const sendMessage = useCallback((message: WebSocketMessage) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  }, []);

  // Auto-connect on mount
  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, []);

  return {
    status,
    isConnected,
    isConnecting,
    isReconnecting,
    error,
    marketData,
    portfolioUpdate,
    positionUpdates,
    tradingAlerts,
    subscribe,
    unsubscribe,
    sendMessage,
    connect,
    disconnect,
  };
};
