import { useCallback, useEffect, useRef, useState } from "react";
import { logger } from "../lib/logger";

export interface WebSocketMessage {
  type: string;
  data?: unknown;
  symbol?: string;
  timestamp: string;
}

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

interface UseWebSocketOptions {
  url: string;
  userId: string;
  autoConnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

interface UseWebSocketReturn {
  isConnected: boolean;
  isConnecting: boolean;
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

export const useWebSocket = ({
  url,
  userId,
  autoConnect = true,
  reconnectInterval = 5000,
  maxReconnectAttempts = 5,
}: UseWebSocketOptions): UseWebSocketReturn => {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [marketData, setMarketData] = useState<Map<string, MarketData>>(new Map());
  const [portfolioUpdate, setPortfolioUpdate] = useState<PortfolioUpdate | null>(null);
  const [positionUpdates, setPositionUpdates] = useState<Map<string, PositionUpdate>>(new Map());
  const [tradingAlerts, setTradingAlerts] = useState<TradingAlert[]>([]);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const subscribedSymbolsRef = useRef<Set<string>>(new Set());

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setIsConnecting(true);
    setError(null);

    try {
      const ws = new WebSocket(`${url}?user_id=${userId}`);
      wsRef.current = ws;

      ws.onopen = () => {
        logger.info("WebSocket connected");
        setIsConnected(true);
        setIsConnecting(false);
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
        setIsConnected(false);
        setIsConnecting(false);

        // Attempt to reconnect if not a manual disconnect
        if (event.code !== 1000 && reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++;
          logger.info(
            `Attempting to reconnect (${reconnectAttemptsRef.current}/${maxReconnectAttempts})...`
          );

          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectInterval);
        } else if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
          setError("Failed to reconnect after maximum attempts");
        }
      };

      ws.onerror = (err) => {
        logger.error("WebSocket error", err);
        setError("WebSocket connection error");
        setIsConnecting(false);
      };
    } catch (err) {
      logger.error("Error creating WebSocket", err);
      setError("Failed to create WebSocket connection");
      setIsConnecting(false);
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

    setIsConnected(false);
    setIsConnecting(false);
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
        logger.info("Subscription confirmed for symbols", { symbols: (message.data as { symbols?: string[] })?.symbols });
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

  const sendMessage = useCallback((message: any) => {
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
    isConnected,
    isConnecting,
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
