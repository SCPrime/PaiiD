import fs from "fs";
import type { NextApiRequest, NextApiResponse } from "next";
import pathLib from "path";

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
  "options/expirations",
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
]);

const ALLOW_DELETE = new Set<string>([
  // Alpaca endpoints
  "positions",
  "orders",
  "watchlists",
  // Order templates
  "order-templates",
]);

// Allowed origins for CORS (production and development only)
// Prefer env-driven allowlist; fallback to curated defaults
const DEFAULT_ALLOWED_ORIGINS = [
  "http://localhost:3000",
  "http://localhost:3001",
  "http://localhost:3003",
  "http://localhost:3004",
  "http://localhost:3005",
  "http://localhost:3006",
  "http://localhost:3007",
  "http://localhost:3008",
  "http://localhost:3009",
  "http://localhost:3010",
  "https://paiid-frontend.onrender.com",
];

function parseAllowedOriginsEnv(): string[] {
  const raw = process.env.ALLOWED_ORIGINS || "";
  const parsed = raw
    .split(",")
    .map((s) => s.trim())
    .filter((s) => !!s);
  if (parsed.length > 0) {
    console.info(`[PROXY] ✅ Loaded ALLOWED_ORIGINS from env: ${parsed.join(", ")}`);
    return parsed;
  }
  console.warn("[PROXY] ⚠️ ALLOWED_ORIGINS env empty - using default allowlist");
  return DEFAULT_ALLOWED_ORIGINS;
}

const ALLOWED_ORIGINS = new Set<string>(parseAllowedOriginsEnv());

// Basic startup validation (non-fatal in dev, emits clear logs in prod)
if (!BACKEND) {
  console.error("[PROXY] ❌ BACKEND_API_BASE_URL not configured");
}

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

  // Extract path first (needed for streaming endpoint check)
  const parts = (req.query.path as string[]) || [];
  let path = parts.join("/");

  // Handle legacy URLs with /api/ prefix (e.g., /api/proxy/api/health)
  // Strip leading "api/" if present
  if (path.startsWith("api/")) {
    path = path.substring(4);
  }

  // Special handling for SSE streaming endpoints - allow same-origin without Origin header
  const isStreamingEndpoint = path.startsWith("stream/");
  const originAllowed = isStreamingEndpoint ? true : isAllowedOrigin(req);

  console.info(
    `[PROXY] Path: ${path}, Streaming: ${isStreamingEndpoint}, Origin check: ${originAllowed ? "ALLOWED" : "BLOCKED"}`
  );

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

  // Diagnostic endpoint: list allowed prefixes and backend
  if (path === "_routes") {
    const body = {
      backend: BACKEND,
      allowed: {
        GET: Array.from(ALLOW_GET.values()),
        POST: Array.from(ALLOW_POST.values()),
        DELETE: Array.from(ALLOW_DELETE.values()),
      },
    };
    res.status(200).json(body);
    return;
  }

  // Load additional allowlist prefixes from OpenAPI export (optional, env-gated)
  let openApiPrefixes: Set<string> | null = null;
  const useOpenApiAllowlist =
    (process.env.USE_OPENAPI_ALLOWLIST || "false").toLowerCase() === "true";
  if (useOpenApiAllowlist) {
    try {
      const candidates = [
        pathLib.resolve(process.cwd(), "docs", "api_endpoints.json"),
        pathLib.resolve(process.cwd(), "..", "docs", "api_endpoints.json"),
      ];
      for (const p of candidates) {
        if (fs.existsSync(p)) {
          const raw = fs.readFileSync(p, "utf-8");
          const json = JSON.parse(raw);
          const prefixes = new Set<string>();
          // Accept both formats: flat list of paths or nested by router
          if (Array.isArray(json?.endpoints)) {
            for (const ep of json.endpoints) {
              const full: string = ep.path || ep;
              const rel = full.startsWith("/api/") ? full.slice(5) : full.replace(/^\//, "");
              const parts = rel.split("/");
              const base = parts.slice(0, 2).join("/") || rel;
              prefixes.add(base);
            }
          } else if (json?.routers) {
            for (const r of json.routers) {
              for (const pth of r.paths || []) {
                const rel = pth.startsWith("/api/") ? pth.slice(5) : pth.replace(/^\//, "");
                const parts = rel.split("/");
                const base = parts.slice(0, 2).join("/") || rel;
                prefixes.add(base);
              }
            }
          }
          openApiPrefixes = prefixes;
          console.info(`[PROXY] ✅ OpenAPI allowlist loaded (${prefixes.size} prefixes) from ${p}`);
          break;
        }
      }
      if (!openApiPrefixes) {
        console.warn("[PROXY] ⚠️ OpenAPI allowlist enabled but api_endpoints.json not found");
      }
    } catch (e) {
      console.warn(`[PROXY] ⚠️ Failed to load OpenAPI allowlist: ${String(e)}`);
    }
  }

  // Check if path is allowed based on method
  // Supports both exact matches and path parameters (e.g., market/quote/AAPL)
  function isPathAllowed(path: string, allowedSet: Set<string>): boolean {
    // Check exact match first
    if (allowedSet.has(path)) {
      return true;
    }

    // Check if path matches any allowed pattern with parameters
    // Examples:
    //   path: "market/quote/AAPL" matches "market/quote"
    //   path: "options/chain/AAPL" matches "options/chain"
    //   path: "news/company/AAPL" matches "news/company"
    for (const allowed of allowedSet) {
      if (path.startsWith(allowed + "/")) {
        // Path has additional segments after allowed base
        return true;
      }
    }

    return false;
  }

  function isPathAllowedOpenAPI(path: string): boolean {
    if (!openApiPrefixes) return false;
    if (openApiPrefixes.has(path)) return true;
    for (const pref of openApiPrefixes) {
      if (pref && path.startsWith(pref + "/")) return true;
    }
    return false;
  }

  if (req.method === "GET" && !(isPathAllowed(path, ALLOW_GET) || isPathAllowedOpenAPI(path))) {
    console.error(`[PROXY] ⛔ GET path not allowed: "${path}"`);
    return res.status(405).json({
      error: "Not allowed",
      path,
      method: req.method,
      hint: "Check allowed paths in proxy configuration",
    });
  }
  if (req.method === "POST" && !(isPathAllowed(path, ALLOW_POST) || isPathAllowedOpenAPI(path))) {
    console.error(`[PROXY] ⛔ POST path not allowed: "${path}"`);
    return res.status(405).json({
      error: "Not allowed",
      path,
      method: req.method,
    });
  }
  if (
    req.method === "DELETE" &&
    !(isPathAllowed(path, ALLOW_DELETE) || isPathAllowedOpenAPI(path))
  ) {
    console.error(`[PROXY] ⛔ DELETE path not allowed: "${path}"`);
    return res.status(405).json({
      error: "Not allowed",
      path,
      method: req.method,
    });
  }

  // Determine auth mode by path
  function deriveAuthMode(path: string): "apiToken" | "jwt" | "none" {
    if (
      path.startsWith("telemetry/") ||
      path.startsWith("monitor/") ||
      path.startsWith("analytics/")
    ) {
      return "apiToken";
    }
    if (
      path.startsWith("users/") ||
      path.startsWith("orders/") ||
      path.startsWith("portfolio/") ||
      path.startsWith("settings/")
    ) {
      return "jwt";
    }
    return "none";
  }

  const routeAuthAware = (process.env.ROUTE_AUTH_AWARE_ENABLED || "true").toLowerCase() === "true";
  const authMode = routeAuthAware ? deriveAuthMode(path) : "apiToken";

  // Preserve query parameters from original request
  const queryString = req.url?.split("?")[1] || "";
  const url = `${BACKEND}/api/${path}${queryString ? "?" + queryString : ""}`;

  const headers: Record<string, string> = {
    "content-type": "application/json",
  };

  // Authorization handling based on route-aware mode
  if (authMode === "apiToken") {
    if (!API_TOKEN) {
      console.error("[PROXY] ❌ Missing API_TOKEN for service-to-service endpoint");
    } else {
      headers["authorization"] = `Bearer ${API_TOKEN}`;
    }
  } else if (authMode === "jwt") {
    const incomingAuth = (req.headers["authorization"] as string) || "";
    if (incomingAuth.toLowerCase().startsWith("bearer ")) {
      headers["authorization"] = incomingAuth;
    } else {
      console.warn("[PROXY] ⚠️ JWT mode but no Bearer token present in request");
    }
  }

  // propagate request id if client set one
  const rid = (req.headers["x-request-id"] as string) || "";
  if (rid) headers["x-request-id"] = rid;

  // Enhanced debug logging
  console.info(`\n[PROXY] ====== New Request ======`);
  console.info(`[PROXY] Method: ${req.method}`);
  console.info(`[PROXY] Original URL: ${req.url}`);
  console.info(`[PROXY] Extracted path: "${path}"`);
  console.info(`[PROXY] Constructed URL: ${url}`);
  console.info(
    `[PROXY] Auth mode: ${authMode} (routeAware=${routeAuthAware}) | Auth header set: ${headers["authorization"] ? "yes" : "no"}`
  );
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
