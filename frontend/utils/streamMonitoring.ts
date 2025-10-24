import { addBreadcrumb, captureMessage } from "../lib/sentry";
import { telemetry } from "../services/telemetry";

export type StreamLogLevel = "info" | "warning" | "error";

interface StreamLogEvent {
  stream: string;
  event: string;
  message: string;
  level?: StreamLogLevel;
  context?: Record<string, unknown>;
  debug?: boolean;
}

type TelemetryRole = "admin" | "beta" | "alpha" | "user" | "owner";

const VALID_ROLES: TelemetryRole[] = ["admin", "beta", "alpha", "user", "owner"];

function sanitize(value: unknown, depth = 0): unknown {
  if (depth > 3) {
    return "[depth-limit]";
  }

  if (value instanceof Error) {
    return {
      name: value.name,
      message: value.message,
      stack: value.stack,
    };
  }

  if (value instanceof Date) {
    return value.toISOString();
  }

  if (typeof value === "bigint") {
    return value.toString();
  }

  if (Array.isArray(value)) {
    return value.slice(0, 20).map((item) => sanitize(item, depth + 1));
  }

  if (value && typeof value === "object") {
    const entries = Object.entries(value as Record<string, unknown>).slice(0, 20);
    return entries.reduce<Record<string, unknown>>((acc, [key, val]) => {
      acc[key] = sanitize(val, depth + 1);
      return acc;
    }, {});
  }

  if (typeof value === "function") {
    return `[function ${value.name || "anonymous"}]`;
  }

  return value;
}

function getTelemetryIdentity(): { userId: string; userRole: TelemetryRole } {
  if (typeof window === "undefined") {
    return { userId: "system", userRole: "user" };
  }

  try {
    const storedId = window.localStorage?.getItem("userId");
    const storedRole = window.localStorage?.getItem("userRole");

    const userId = storedId && storedId.trim().length > 0 ? storedId : "anonymous";

    if (storedRole && (VALID_ROLES as readonly string[]).includes(storedRole)) {
      return { userId, userRole: storedRole as TelemetryRole };
    }

    return { userId, userRole: "user" };
  } catch (error) {
    console.warn("[StreamMonitoring] Failed to read telemetry identity", error);
    return { userId: "anonymous", userRole: "user" };
  }
}

export function recordStreamEvent({
  stream,
  event,
  message,
  level = "info",
  context = {},
  debug = false,
}: StreamLogEvent): void {
  const timestamp = new Date().toISOString();
  const sanitizedContext = sanitize(context);
  const payload = {
    stream,
    event,
    message,
    level,
    context: sanitizedContext,
    timestamp,
  };

  if (level === "error") {
    console.error(`[${stream}] ${message}`, sanitizedContext);
  } else if (level === "warning") {
    console.warn(`[${stream}] ${message}`, sanitizedContext);
  } else if (debug) {
    console.info(`[${stream}] ${message}`, sanitizedContext);
  }

  addBreadcrumb(`[${stream}] ${message}`, {
    event,
    level,
    timestamp,
    context: sanitizedContext,
  });

  if (level !== "info") {
    captureMessage(`[${stream}] ${message}`, level === "warning" ? "warning" : "error");
  }

  if (typeof window !== "undefined") {
    try {
      const { userId, userRole } = getTelemetryIdentity();

      telemetry.track({
        userId,
        userRole,
        component: `sse:${stream}`,
        action: `stream_${event}`,
        metadata: {
          ...payload,
        },
      });

      window.dispatchEvent(new CustomEvent("paiid:stream-event", { detail: payload }));
    } catch (error) {
      console.warn("[StreamMonitoring] Failed to forward stream event", error);
    }
  }
}

export default recordStreamEvent;
