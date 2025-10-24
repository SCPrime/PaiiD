import { useCallback, useEffect, useRef, useState } from "react";

export interface UseSSEOptions {
  events?: Record<string, (event: MessageEvent) => void>;
  enabled?: boolean;
  autoReconnect?: boolean;
  maxReconnectAttempts?: number;
  reconnectDelayMs?: number;
  reconnectBackoffMultiplier?: number;
  maxReconnectDelayMs?: number;
  heartbeatEvent?: string;
  withCredentials?: boolean;
  onOpen?: (eventSource: EventSource) => void;
  onClose?: () => void;
  onError?: (error: Event) => void;
  debug?: boolean;
}

export interface UseSSEResult {
  connected: boolean;
  connecting: boolean;
  error: string | null;
  lastEventId: string | null;
  lastEventAt: Date | null;
  lastHeartbeatAt: Date | null;
  reconnectAttempts: number;
  eventSource: EventSource | null;
  reconnect: () => void;
  disconnect: () => void;
}

const noop = () => undefined;

export function useSSE(url: string | null, options: UseSSEOptions = {}): UseSSEResult {
  const {
    events,
    enabled = true,
    autoReconnect = true,
    maxReconnectAttempts = 5,
    reconnectDelayMs = 2000,
    reconnectBackoffMultiplier = 2,
    maxReconnectDelayMs = 30000,
    heartbeatEvent,
    withCredentials = false,
    onOpen = noop,
    onClose = noop,
    onError = noop,
    debug = false,
  } = options;

  const [connected, setConnected] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastEventId, setLastEventId] = useState<string | null>(null);
  const [lastEventAt, setLastEventAt] = useState<Date | null>(null);
  const [lastHeartbeatAt, setLastHeartbeatAt] = useState<Date | null>(null);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);

  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const cleanupRef = useRef<(() => void) | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const isMountedRef = useRef(true);
  const heartbeatEventRef = useRef<string | undefined>(heartbeatEvent);
  const eventsRef = useRef<Record<string, (event: MessageEvent) => void> | undefined>(events);

  useEffect(() => {
    heartbeatEventRef.current = heartbeatEvent;
  }, [heartbeatEvent]);

  useEffect(() => {
    eventsRef.current = events;
  }, [events]);

  useEffect(() => {
    return () => {
      isMountedRef.current = false;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (cleanupRef.current) {
        cleanupRef.current();
      }
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
    };
  }, []);

  const log = useCallback(
    (...args: unknown[]) => {
      if (debug) {
        // eslint-disable-next-line no-console
        console.info("[useSSE]", ...args);
      }
    },
    [debug]
  );

  const clearReconnectTimeout = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
  }, []);

  const cleanupCurrentSource = useCallback(() => {
    if (cleanupRef.current) {
      cleanupRef.current();
      cleanupRef.current = null;
    }
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
  }, []);

  const disconnect = useCallback(() => {
    log("Disconnecting SSE stream");
    clearReconnectTimeout();
    cleanupCurrentSource();
    reconnectAttemptsRef.current = 0;
    if (isMountedRef.current) {
      setReconnectAttempts(0);
      setConnected(false);
      setConnecting(false);
      setError(null);
      setLastEventId(null);
      setLastEventAt(null);
      setLastHeartbeatAt(null);
      onClose();
    }
  }, [clearReconnectTimeout, cleanupCurrentSource, log, onClose]);

  const connectRef = useRef<() => void>(() => undefined);

  const scheduleReconnect = useCallback(() => {
    if (!autoReconnect) {
      log("Auto-reconnect disabled; not scheduling reconnect");
      return;
    }

    const nextAttempt = reconnectAttemptsRef.current + 1;
    if (maxReconnectAttempts >= 0 && nextAttempt > maxReconnectAttempts) {
      log("Max reconnect attempts reached");
      if (isMountedRef.current) {
        setError("Max reconnect attempts reached");
      }
      return;
    }

    reconnectAttemptsRef.current = nextAttempt;
    if (isMountedRef.current) {
      setReconnectAttempts(nextAttempt);
    }

    const delay = Math.min(
      reconnectDelayMs * Math.pow(reconnectBackoffMultiplier, nextAttempt - 1),
      maxReconnectDelayMs
    );

    log(`Scheduling reconnect attempt ${nextAttempt} in ${delay}ms`);
    clearReconnectTimeout();
    reconnectTimeoutRef.current = setTimeout(() => {
      if (!isMountedRef.current) {
        return;
      }
      connectRef.current();
    }, delay);
  }, [
    autoReconnect,
    clearReconnectTimeout,
    log,
    maxReconnectAttempts,
    maxReconnectDelayMs,
    reconnectBackoffMultiplier,
    reconnectDelayMs,
  ]);

  const connect = useCallback(() => {
    clearReconnectTimeout();

    if (!enabled) {
      log("SSE disabled; skipping connect");
      return;
    }
    if (!url) {
      log("No SSE url provided; skipping connect");
      return;
    }

    cleanupCurrentSource();
    setConnecting(true);
    setError(null);

    try {
      const eventSource = new EventSource(url, { withCredentials });
      eventSourceRef.current = eventSource;
      reconnectAttemptsRef.current = 0;
      if (isMountedRef.current) {
        setReconnectAttempts(0);
      }

      const handlers: Array<[string, (event: MessageEvent) => void]> = [];
      const registerHandler = (eventName: string, handler: (event: MessageEvent) => void) => {
        const wrapped = (event: MessageEvent) => {
          if (!isMountedRef.current) {
            return;
          }
          setLastEventId(event.lastEventId || null);
          const now = new Date();
          setLastEventAt(now);
          if (heartbeatEventRef.current && eventName === heartbeatEventRef.current) {
            setLastHeartbeatAt(now);
          }
          handler(event);
        };
        handlers.push([eventName, wrapped]);
        eventSource.addEventListener(eventName, wrapped as EventListener);
      };

      const currentEvents = eventsRef.current;
      if (currentEvents) {
        Object.entries(currentEvents).forEach(([eventName, handler]) => {
          registerHandler(eventName, handler);
        });
      }

      cleanupRef.current = () => {
        handlers.forEach(([eventName, handler]) => {
          eventSource.removeEventListener(eventName, handler as EventListener);
        });
        eventSource.onopen = null;
        eventSource.onerror = null;
      };

      eventSource.onopen = () => {
        log("SSE connection established");
        if (!isMountedRef.current) {
          return;
        }
        setConnected(true);
        setConnecting(false);
        setError(null);
        setLastEventAt(new Date());
        setLastHeartbeatAt(null);
        onOpen(eventSource);
      };

      eventSource.onerror = (event) => {
        log("SSE connection error", event);
        onError(event);
        cleanupCurrentSource();
        if (!isMountedRef.current) {
          return;
        }
        setConnected(false);
        setConnecting(false);
        setLastEventId(null);
        setLastHeartbeatAt(null);
        setError("Connection lost");
        scheduleReconnect();
      };
    } catch (err) {
      log("Failed to create EventSource", err);
      cleanupCurrentSource();
      if (!isMountedRef.current) {
        return;
      }
      setConnecting(false);
      setConnected(false);
      const message = err instanceof Error ? err.message : String(err);
      setError(message || "Failed to connect to stream");
      scheduleReconnect();
    }
  }, [
    cleanupCurrentSource,
    clearReconnectTimeout,
    enabled,
    log,
    onError,
    onOpen,
    scheduleReconnect,
    url,
    withCredentials,
  ]);

  connectRef.current = connect;

  useEffect(() => {
    if (!enabled || !url) {
      disconnect();
      return;
    }

    connect();

    return () => {
      disconnect();
    };
  }, [connect, disconnect, enabled, url]);

  const reconnect = useCallback(() => {
    log("Manual reconnect triggered");
    reconnectAttemptsRef.current = 0;
    if (isMountedRef.current) {
      setReconnectAttempts(0);
    }
    connect();
  }, [connect, log]);

  return {
    connected,
    connecting,
    error,
    lastEventId,
    lastEventAt,
    lastHeartbeatAt,
    reconnectAttempts,
    eventSource: eventSourceRef.current,
    reconnect,
    disconnect,
  };
}
