import type { NextApiRequest, NextApiResponse } from "next";

// NOTE: API routes run server-side and use NON-PREFIXED env vars
// NEXT_PUBLIC_* is for client-side code only!
const BACKEND =
  process.env.BACKEND_API_BASE_URL ||
  process.env.NEXT_PUBLIC_BACKEND_API_BASE_URL ||
  "https://paiid-backend.onrender.com";
const API_TOKEN = process.env.API_TOKEN || process.env.NEXT_PUBLIC_API_TOKEN || "";

const isVerboseLogging = process.env.NODE_ENV !== "production";

const logVerbose = (...args: unknown[]) => {
  if (isVerboseLogging) {
    console.info(...args);
  }
};

if (!API_TOKEN) {
  console.error("[PROXY] ⚠️ API_TOKEN not configured in environment variables");
  console.error("[PROXY] ⚠️ Checked: process.env.API_TOKEN and process.env.NEXT_PUBLIC_API_TOKEN");
} else {
  logVerbose(`[PROXY] ✅ API_TOKEN loaded: ${API_TOKEN.substring(0, 10)}...`);
}

// Exact endpoints our UI uses (paths without /api prefix - added in URL construction)
const ALLOW_GET = new Set<string>([
  "health",
  "settings",
  "portfolio/positions",
  "ai/recommendations",
  "ai/signals",
  "ai/analyze-symbol",
  "market/historical",
  "screening/opportunities",
  "screening/strategies",
  "market/conditions",
  "market/indices",
  "market/sectors",
  "market/status", // Market hours detection
  // Live market data endpoints
  "market/quote",
  "market/quotes",
  "market/scanner/under4",
  "market/bars",
  // Options endpoints
  "options/greeks",
  "options/chain",
  // News endpoints
  "news/providers",
  "news/company",
  "news/market",
  "news/sentiment/market",
  "news/cache/stats",
  // Alpaca endpoints
  "account",
  "positions",
  "orders",
  "assets",
  "clock",
  "calendar",
  "watchlists",
  // Order templates
  "order-templates",
  // Claude AI endpoints
  "claude/chat",
  "claude/health",
  // Analytics endpoints
  "portfolio/summary",
  "portfolio/history",
  "analytics/performance",
  // Scheduler endpoints
  "scheduler/schedules",
  "scheduler/executions",
  // Backtesting endpoints
  "backtesting/run",
  "backtesting/quick-test",
  "backtesting/strategy-templates",
  // Strategy endpoints
  "strategies/templates",
  // SSE streaming endpoints
  "stream/market-indices",
  "stream/positions",
]);

const ALLOW_POST = new Set<string>([
  "trading/execute",
  "settings",
  "admin/kill",
  // Alpaca endpoints
  "orders",
  "watchlists",
  // Order templates
  "order-templates",
  // Claude AI endpoints (both full and simplified paths)
  "claude/chat",
  "claude/health",
  "chat",
  // Telemetry
  "telemetry",
  // News cache management
  "news/cache/clear",
  // Backtesting endpoints
  "backtesting/run",
  // Scheduler endpoints
  "scheduler/schedules",
  "scheduler/pause-all",
  "scheduler/resume-all",
]);

const ALLOW_DELETE = new Set<string>([
  // Alpaca endpoints
  "positions",
  "orders",
  "watchlists",
  // Order templates
  "order-templates",
  // Scheduler endpoints
  "scheduler/schedules",
]);

const ALLOW_PATCH = new Set<string>([
  // Scheduler endpoints
  "scheduler/schedules",
]);

// Allowed origins for CORS (production and development only)
const ALLOWED_ORIGINS = new Set<string>([
  "http://localhost:3000",
  "http://localhost:3003", // Alternative dev server port
  "http://localhost:3004", // Alternative dev server port
  "http://localhost:3005", // Alternative dev server port
  "http://localhost:3006", // Alternative dev server port
  "http://localhost:3007", // Alternative dev server port
  "http://localhost:3008", // Alternative dev server port
  "http://localhost:3009", // Alternative dev server port
  "http://localhost:3010", // Alternative dev server port
  "https://paiid-frontend.onrender.com",
]);

function isAllowedOrigin(req: NextApiRequest): boolean {
  const origin = (req.headers.origin || "").toLowerCase();
  const referer = (req.headers.referer || "").toLowerCase();
  const host = (req.headers.host || "").toLowerCase();

  // Check if origin is in allowed list
  if (origin && ALLOWED_ORIGINS.has(origin)) {
    logVerbose(`[PROXY] ✅ Origin allowed: ${origin}`);
    return true;
  }

  // Fallback: Check referer for same-origin requests
  if (!origin && referer) {
    try {
      const refererUrl = new URL(referer);
      const refererOrigin = `${refererUrl.protocol}//${refererUrl.host}`;
      if (ALLOWED_ORIGINS.has(refererOrigin)) {
        logVerbose(`[PROXY] ✅ Referer allowed: ${refererOrigin}`);
        return true;
      }
    } catch (e) {
      // Invalid referer URL
    }
  }

  console.warn(
    `[PROXY] ⚠️ Origin blocked: ${origin || "none"} (referer: ${referer || "none"}, host: ${host})`
  );
  return false;
}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  // Log EVERY request for debugging
  logVerbose(`\n[PROXY] ====== NEW REQUEST ======`);
  logVerbose(`[PROXY] Method: ${req.method}`);
  logVerbose(`[PROXY] URL: ${req.url}`);
  logVerbose(`[PROXY] Origin: ${req.headers.origin || "NONE"}`);

  // CORS preflight - Validate origin first
  if (req.method === "OPTIONS") {
    logVerbose(`[PROXY] Handling OPTIONS preflight`);
    const origin = req.headers.origin;

    // Only allow preflight from authorized origins
    if (origin && isAllowedOrigin(req)) {
      res.setHeader("access-control-allow-origin", origin);
      res.setHeader("access-control-allow-methods", "GET,POST,DELETE,PATCH,OPTIONS");
      res.setHeader("access-control-allow-headers", "content-type,x-request-id,authorization");
      res.setHeader("access-control-allow-credentials", "true");
      res.status(204).end();
      return;
    } else {
      // Block unauthorized preflight requests
      console.warn(`[PROXY] ⚠️ Blocked OPTIONS from: ${origin || "unknown"}`);
      res.status(403).json({ error: "Forbidden origin" });
      return;
    }
  }

  const originAllowed = isAllowedOrigin(req);
  logVerbose(`[PROXY] Origin check result: ${originAllowed ? "ALLOWED" : "BLOCKED"}`);

  if (!originAllowed) {
    console.error(`[PROXY] ⛔ REJECTING REQUEST WITH 403`);
    res
      .status(403)
      .json({ error: "Forbidden (origin)", origin: req.headers.origin || "none", url: req.url });
    return;
  }

  // Set CORS headers for all successful responses (only for allowed origins)
  const origin = req.headers.origin;
  if (origin) {
    res.setHeader("access-control-allow-origin", origin);
    res.setHeader("access-control-allow-credentials", "true");
  }

  logVerbose(`[PROXY] ✅ Origin check passed, proceeding with request`);

  const parts = (req.query.path as string[]) || [];
  let path = parts.join("/");

  // Handle legacy URLs with /api/ prefix (e.g., /api/proxy/api/health)
  // Strip leading "api/" if present
  if (path.startsWith("api/")) {
    path = path.substring(4);
  }

  // Check if path is allowed based on method
  if (req.method === "GET" && !ALLOW_GET.has(path)) {
    // Allow wildcard patterns for dynamic routes
    const isAllowedPattern = Array.from(ALLOW_GET).some(
      (allowed) => path.startsWith(allowed + "/") || path === allowed
    );
    if (!isAllowedPattern) {
      return res.status(405).json({ error: "Not allowed" });
    }
  }
  if (req.method === "POST" && !ALLOW_POST.has(path)) {
    const isAllowedPattern = Array.from(ALLOW_POST).some(
      (allowed) => path.startsWith(allowed + "/") || path === allowed
    );
    if (!isAllowedPattern) {
      return res.status(405).json({ error: "Not allowed" });
    }
  }
  if (req.method === "DELETE" && !ALLOW_DELETE.has(path)) {
    const isAllowedPattern = Array.from(ALLOW_DELETE).some(
      (allowed) => path.startsWith(allowed + "/") || path === allowed
    );
    if (!isAllowedPattern) {
      return res.status(405).json({ error: "Not allowed" });
    }
  }
  if (req.method === "PATCH" && !ALLOW_PATCH.has(path)) {
    const isAllowedPattern = Array.from(ALLOW_PATCH).some(
      (allowed) => path.startsWith(allowed + "/") || path === allowed
    );
    if (!isAllowedPattern) {
      return res.status(405).json({ error: "Not allowed" });
    }
  }

  // Preserve query parameters from original request
  const queryString = req.url?.split("?")[1] || "";
  const url = `${BACKEND}/api/${path}${queryString ? "?" + queryString : ""}`;

  const headers: Record<string, string> = {
    authorization: `Bearer ${API_TOKEN}`,
    "content-type": "application/json",
  };

  // propagate request id if client set one
  const rid = (req.headers["x-request-id"] as string) || "";
  if (rid) headers["x-request-id"] = rid;

  // Enhanced debug logging
  logVerbose(`\n[PROXY] ====== New Request ======`);
  logVerbose(`[PROXY] Method: ${req.method}`);
  logVerbose(`[PROXY] Original URL: ${req.url}`);
  logVerbose(`[PROXY] Extracted path: "${path}"`);
  logVerbose(`[PROXY] Constructed URL: ${url}`);
  logVerbose(`[PROXY] Auth header: Bearer ${API_TOKEN?.substring(0, 8)}...`);
  logVerbose(`[PROXY] Backend: ${BACKEND}`);
  if (req.method === "POST" || req.method === "PATCH") {
    logVerbose(`[PROXY] Body:`, JSON.stringify(req.body, null, 2));
  }

  try {
    const upstream = await fetch(url, {
      method: req.method,
      headers,
      body:
        req.method === "POST" || req.method === "DELETE" || req.method === "PATCH"
          ? JSON.stringify(req.body ?? {})
          : undefined,
      // avoid any CDN caching at the edge
      cache: "no-store",
    });

    const text = await upstream.text();
    logVerbose(`[PROXY] Response status: ${upstream.status}`);
    if (isVerboseLogging) {
      const preview = text.substring(0, 200);
      logVerbose(`[PROXY] Response body: ${preview}${text.length > 200 ? "..." : ""}`);
      logVerbose(`[PROXY] ====== End Request ======\n`);
    }

    res
      .status(upstream.status)
      .setHeader("content-type", upstream.headers.get("content-type") || "application/json")
      .setHeader("cache-control", "no-store")
      .send(text);
  } catch (err) {
    console.error(`[PROXY] ERROR: ${err}`);
    console.error(`[PROXY] Error details:`, err);
    logVerbose(`[PROXY] ====== End Request (ERROR) ======\n`);
    res.status(502).json({ error: "Upstream error", detail: String(err) });
  }
}
