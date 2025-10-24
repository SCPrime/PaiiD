import type { NextApiRequest, NextApiResponse } from "next";

// NOTE: API routes run server-side and use NON-PREFIXED env vars
// NEXT_PUBLIC_* is for client-side code only!
const BACKEND =
  process.env.BACKEND_API_BASE_URL ||
  process.env.NEXT_PUBLIC_BACKEND_API_BASE_URL ||
  "https://paiid-backend.onrender.com";
const API_TOKEN = process.env.API_TOKEN || process.env.NEXT_PUBLIC_API_TOKEN || "";

if (!API_TOKEN) {
  console.error("[PROXY] ⚠️ API_TOKEN not configured in environment variables");
  console.error("[PROXY] ⚠️ Checked: process.env.API_TOKEN and process.env.NEXT_PUBLIC_API_TOKEN");
} else {
  console.info(`[PROXY] ✅ API_TOKEN loaded: ${API_TOKEN.substring(0, 10)}...`);
}

// Exact endpoints our UI uses (paths without /api prefix - added in URL construction)
type HttpMethod = "GET" | "POST" | "DELETE";

const ALLOWED_PATH_PATTERNS: Record<HttpMethod, string[]> = {
  GET: [
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
    "market/quote/:symbol",
    "market/quotes",
    "market/scanner/under4",
    "market/bars",
    "market/bars/:symbol",
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
    "positions/:symbol",
    "orders",
    "orders/:orderId",
    "assets",
    "assets/:symbol",
    "clock",
    "calendar",
    "watchlists",
    "watchlists/:watchlistId",
    // Order templates
    "order-templates",
    "order-templates/:templateId",
    // Claude AI endpoints
    "claude/chat",
    "claude/health",
    // Analytics endpoints
    "portfolio/summary",
    "portfolio/history",
    "analytics/performance",
    // Backtesting endpoints
    "backtesting/run",
    "backtesting/quick-test",
    "backtesting/strategy-templates",
    // Strategy endpoints
    "strategies/templates",
    // SSE streaming endpoints
    "stream/market-indices",
    "stream/positions",
  ],
  POST: [
    "trading/execute",
    "settings",
    "admin/kill",
    // Alpaca endpoints
    "orders",
    "orders/:orderId",
    "watchlists",
    "watchlists/:watchlistId",
    // Order templates
    "order-templates",
    "order-templates/:templateId",
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
  ],
  DELETE: [
    // Alpaca endpoints
    "positions",
    "positions/:symbol",
    "orders",
    "orders/:orderId",
    "watchlists",
    "watchlists/:watchlistId",
    // Order templates
    "order-templates",
    "order-templates/:templateId",
  ],
};

const PATH_REGEX_CACHE = new Map<string, RegExp>();

function patternToRegex(pattern: string): RegExp {
  const cached = PATH_REGEX_CACHE.get(pattern);
  if (cached) {
    return cached;
  }

  let regexString = pattern.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  regexString = regexString.replace(/:([A-Za-z0-9_]+)/g, "[^/]+");
  regexString = regexString.replace(/\*/g, ".*");

  const compiled = new RegExp(`^${regexString}$`);
  PATH_REGEX_CACHE.set(pattern, compiled);
  return compiled;
}

function isPathAllowed(method: string | undefined, path: string): boolean {
  const normalizedMethod = (method ?? "GET").toUpperCase() as keyof typeof ALLOWED_PATH_PATTERNS;
  const patterns = ALLOWED_PATH_PATTERNS[normalizedMethod];

  if (!patterns) {
    return false;
  }

  return patterns.some((pattern) => patternToRegex(pattern).test(path));
}

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
    console.info(`[PROXY] ✅ Origin allowed: ${origin}`);
    return true;
  }

  // Fallback: Check referer for same-origin requests
  if (!origin && referer) {
    try {
      const refererUrl = new URL(referer);
      const refererOrigin = `${refererUrl.protocol}//${refererUrl.host}`;
      if (ALLOWED_ORIGINS.has(refererOrigin)) {
        console.info(`[PROXY] ✅ Referer allowed: ${refererOrigin}`);
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
  console.info(`\n[PROXY] ====== NEW REQUEST ======`);
  console.info(`[PROXY] Method: ${req.method}`);
  console.info(`[PROXY] URL: ${req.url}`);
  console.info(`[PROXY] Origin: ${req.headers.origin || "NONE"}`);

  // CORS preflight - Validate origin first
  if (req.method === "OPTIONS") {
    console.info(`[PROXY] Handling OPTIONS preflight`);
    const origin = req.headers.origin;

    // Only allow preflight from authorized origins
    if (origin && isAllowedOrigin(req)) {
      res.setHeader("access-control-allow-origin", origin);
      res.setHeader("access-control-allow-methods", "GET,POST,DELETE,OPTIONS");
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
  console.info(`[PROXY] Origin check result: ${originAllowed ? "ALLOWED" : "BLOCKED"}`);

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

  console.info(`[PROXY] ✅ Origin check passed, proceeding with request`);

  const parts = (req.query.path as string[]) || [];
  let path = parts.join("/");

  // Handle legacy URLs with /api/ prefix (e.g., /api/proxy/api/health)
  // Strip leading "api/" if present
  if (path.startsWith("api/")) {
    path = path.substring(4);
  }

  // Check if path is allowed based on method
  if (!isPathAllowed(req.method, path)) {
    return res.status(405).json({ error: "Not allowed" });
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
  console.info(`\n[PROXY] ====== New Request ======`);
  console.info(`[PROXY] Method: ${req.method}`);
  console.info(`[PROXY] Original URL: ${req.url}`);
  console.info(`[PROXY] Extracted path: "${path}"`);
  console.info(`[PROXY] Constructed URL: ${url}`);
  console.info(`[PROXY] Auth header: Bearer ${API_TOKEN?.substring(0, 8)}...`);
  console.info(`[PROXY] Backend: ${BACKEND}`);
  if (req.method === "POST") {
    console.info(`[PROXY] Body:`, JSON.stringify(req.body, null, 2));
  }

  try {
    const upstream = await fetch(url, {
      method: req.method,
      headers,
      body:
        req.method === "POST" || req.method === "DELETE"
          ? JSON.stringify(req.body ?? {})
          : undefined,
      // avoid any CDN caching at the edge
      cache: "no-store",
    });

    const text = await upstream.text();
    console.info(`[PROXY] Response status: ${upstream.status}`);
    console.info(
      `[PROXY] Response body: ${text.substring(0, 200)}${text.length > 200 ? "..." : ""}`
    );
    console.info(`[PROXY] ====== End Request ======\n`);

    res
      .status(upstream.status)
      .setHeader("content-type", upstream.headers.get("content-type") || "application/json")
      .setHeader("cache-control", "no-store")
      .send(text);
  } catch (err) {
    console.error(`[PROXY] ERROR: ${err}`);
    console.error(`[PROXY] Error details:`, err);
    console.info(`[PROXY] ====== End Request (ERROR) ======\n`);
    res.status(502).json({ error: "Upstream error", detail: String(err) });
  }
}
