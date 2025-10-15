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

import { useEffect, useState, useCallback, useRef } from 'react';

export interface Position {
  symbol: string;
  qty: number;
  avgEntryPrice: number;
  currentPrice: number;
  marketValue: number;
  unrealizedPL: number;
  unrealizedPLPercent: number;
  side: 'long' | 'short';
  dayChange: number;
  dayChangePercent: number;
}

export interface PositionStreamState {
  positions: Position[];
  connected: boolean;
  connecting: boolean;
  error: string | null;
  lastUpdate: Date | null;
}

export interface UsePositionUpdatesOptions {
  /** Auto-reconnect on disconnect (default: true) */
  autoReconnect?: boolean;
  /** Max reconnect attempts (default: 5) */
  maxReconnectAttempts?: number;
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
 * console.log(`Total P&L: $${totalPL.toFixed(2)}`);
 */
export function usePositionUpdates(
  options: UsePositionUpdatesOptions = {}
): PositionStreamState & { reconnect: () => void } {
  const {
    autoReconnect = true,
    maxReconnectAttempts = 5,
    debug = false
  } = options;

  const [state, setState] = useState<PositionStreamState>({
    positions: [],
    connected: false,
    connecting: false,
    error: null,
    lastUpdate: null
  });

  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const log = useCallback((...args: any[]) => {
    if (debug) {
      console.log('[usePositionUpdates]', ...args);
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

    setState(prev => ({ ...prev, connecting: true, error: null }));
    log('Connecting to position stream');

    try {
      // Build SSE URL
      const url = `/api/proxy/api/stream/positions`;

      // Create EventSource
      const eventSource = new EventSource(url);
      eventSourceRef.current = eventSource;

      // Handle connection open
      eventSource.onopen = () => {
        log('✅ Connected to position stream');
        setState(prev => ({
          ...prev,
          connected: true,
          connecting: false,
          error: null
        }));
        reconnectAttemptsRef.current = 0;  // Reset reconnect counter on success
      };

      // Handle position updates
      eventSource.addEventListener('position_update', (event) => {
        try {
          const newPositions = JSON.parse(event.data) as Position[];
          log('📊 Position update:', newPositions.length, 'positions');

          setState(prev => ({
            ...prev,
            positions: newPositions,
            lastUpdate: new Date()
          }));
        } catch (error) {
          console.error('[usePositionUpdates] Error parsing position update:', error);
        }
      });

      // Handle heartbeat (keep-alive)
      eventSource.addEventListener('heartbeat', (event) => {
        log('💓 Heartbeat received');
      });

      // Handle errors
      eventSource.addEventListener('error', (event) => {
        try {
          const errorData = JSON.parse((event as MessageEvent).data);
          console.error('[usePositionUpdates] Server error:', errorData.error);
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
      eventSource.onerror = (error) => {
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
      console.error('[usePositionUpdates] Connection error:', error);
      setState(prev => ({
        ...prev,
        connected: false,
        connecting: false,
        error: error.message || 'Failed to connect'
      }));
    }
  }, [autoReconnect, maxReconnectAttempts, log]);

  // Manual reconnect method
  const reconnect = useCallback(() => {
    log('🔄 Manual reconnect triggered');
    reconnectAttemptsRef.current = 0;  // Reset counter on manual reconnect
    connect();
  }, [connect, log]);

  // Connect on mount
  useEffect(() => {
    connect();

    // Cleanup on unmount
    return () => {
      log('🧹 Cleaning up position stream');
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
    };
  }, [connect, log]);

  return {
    ...state,
    reconnect
  };
}
