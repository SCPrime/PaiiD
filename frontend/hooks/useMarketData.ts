import { useCallback, useEffect, useState } from "react";
import { throttle } from "lodash";
import { logger } from "../lib/logger";

export interface MarketDataState {
  dow: { value: number; change: number; symbol: string };
  nasdaq: { value: number; change: number; symbol: string };
  lastUpdate: number;
}

export interface MarketStatus {
  is_open: boolean;
  state: string;
  description: string;
}

export function useMarketData() {
  const [marketData, setMarketData] = useState<MarketDataState>({
    dow: { value: 0, change: 0, symbol: "DJI" },
    nasdaq: { value: 0, change: 0, symbol: "COMP" },
    lastUpdate: 0,
  });
  const [forceFieldConfidence, setForceFieldConfidence] = useState(0);
  const [isMarketDataLoading, setIsMarketDataLoading] = useState(true);
  const [sseConnected, setSseConnected] = useState(false);
  const [sseRetryCount, setSseRetryCount] = useState(0);
  const [marketStatus, setMarketStatus] = useState<MarketStatus | null>(null);

  // Throttled market data update - prevents animation interruptions
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const throttledSetMarketData = useCallback(
    throttle((newData: MarketDataState) => {
      setMarketData(newData);
      logger.info("[useMarketData] Market data updated (throttled)");
    }, 10000), // Update max once per 10 seconds
    []
  );

  // Real-time streaming: SSE for market data with auto-reconnection
  useEffect(() => {
    let eventSource: EventSource | null = null;
    let reconnectTimeout: NodeJS.Timeout | null = null;
    let isUnmounted = false;

    // Load cached market data on mount
    const loadCachedData = () => {
      try {
        const cached = localStorage.getItem("paiid-market-data");
        if (cached) {
          const parsed = JSON.parse(cached);
          // Only use cache if it's less than 24 hours old
          if (parsed.timestamp && Date.now() - parsed.timestamp < 24 * 60 * 60 * 1000) {
            logger.info("[useMarketData] Loading cached market data from localStorage");
            setMarketData(parsed.data);
            setIsMarketDataLoading(false);
          }
        }
      } catch (error) {
        logger.error("[useMarketData] Failed to load cached market data", error);
      }
    };

    // SSE connection with exponential backoff retry
    const connectSSE = (retryAttempt = 0) => {
      if (isUnmounted) return;

      const maxRetries = 10;
      const baseDelay = 2000; // 2 seconds

      if (retryAttempt >= maxRetries) {
        logger.error("[useMarketData] Max SSE retry attempts reached. Giving up.");
        setIsMarketDataLoading(false);
        return;
      }

      logger.info(
        `[useMarketData] Connecting to SSE stream (attempt ${retryAttempt + 1}/${maxRetries})...`
      );
      setSseRetryCount(retryAttempt);

      try {
        eventSource = new EventSource("/api/proxy/stream/market-indices");

        eventSource.addEventListener("indices_update", (e) => {
          const data = JSON.parse(e.data);
          logger.debug("[useMarketData] Received live market data", { data });

          const now = Date.now();
          const newData: MarketDataState = {
            dow: {
              value: data.dow?.last || 0,
              change: data.dow?.changePercent || 0,
              symbol: "DJI",
            },
            nasdaq: {
              value: data.nasdaq?.last || 0,
              change: data.nasdaq?.changePercent || 0,
              symbol: "COMP",
            },
            lastUpdate: now,
          };

          // Calculate Force Field Confidence (0-100%)
          // Based on: data freshness, market stability, and connection quality
          const dataFreshness = 100; // Fresh data just received
          const marketVolatility = Math.abs(newData.dow.change) + Math.abs(newData.nasdaq.change);
          const stabilityScore = Math.max(0, 100 - marketVolatility * 10); // Lower volatility = higher confidence
          const connectionScore = retryAttempt === 0 ? 100 : Math.max(0, 100 - retryAttempt * 10);

          const confidence = Math.round(
            dataFreshness * 0.4 + stabilityScore * 0.4 + connectionScore * 0.2
          );
          setForceFieldConfidence(Math.min(100, Math.max(0, confidence)));

          // Use throttled update to prevent logo animation interruptions
          throttledSetMarketData(newData);

          // Mark as connected and loading complete
          setSseConnected(true);
          setIsMarketDataLoading(false);
          setSseRetryCount(0); // Reset retry count on success

          // Cache the data in localStorage (immediate, not throttled)
          try {
            localStorage.setItem(
              "paiid-market-data",
              JSON.stringify({
                data: newData,
                timestamp: Date.now(),
              })
            );
          } catch (error) {
            logger.error("[useMarketData] Failed to cache market data", error);
          }
        });

        eventSource.addEventListener("heartbeat", (e) => {
          const data = JSON.parse(e.data);
          logger.debug("[useMarketData] SSE heartbeat received", { timestamp: data.timestamp });
        });

        eventSource.addEventListener("error", (e) => {
          logger.error("[useMarketData] SSE connection error", e);
          setSseConnected(false);

          if (eventSource) {
            eventSource.close();
            eventSource = null;
          }

          // Exponential backoff: 2s, 4s, 8s, 16s, 32s, 64s, 128s (max ~2min)
          const delay = Math.min(baseDelay * Math.pow(2, retryAttempt), 128000);
          logger.warn(
            `[useMarketData] SSE disconnected. Retrying in ${delay / 1000}s... (attempt ${retryAttempt + 1}/${maxRetries})`
          );

          reconnectTimeout = setTimeout(() => {
            connectSSE(retryAttempt + 1);
          }, delay);
        });

        eventSource.addEventListener("open", () => {
          logger.info("[useMarketData] SSE connection established");
          setSseConnected(true);
        });
      } catch (error) {
        logger.error("[useMarketData] Failed to create EventSource", error);
        setSseConnected(false);

        // Retry with exponential backoff
        const delay = Math.min(baseDelay * Math.pow(2, retryAttempt), 128000);
        reconnectTimeout = setTimeout(() => {
          connectSSE(retryAttempt + 1);
        }, delay);
      }
    };

    // Initialize
    loadCachedData();
    connectSSE(0);

    // Cleanup: close SSE connection on unmount
    return () => {
      isUnmounted = true;
      logger.info("[useMarketData] Closing SSE connection");

      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }

      if (eventSource) {
        eventSource.close();
      }
    };
  }, [throttledSetMarketData]);

  return {
    marketData,
    forceFieldConfidence,
    isMarketDataLoading,
    sseConnected,
    sseRetryCount,
    marketStatus,
    setMarketStatus,
  };
}
