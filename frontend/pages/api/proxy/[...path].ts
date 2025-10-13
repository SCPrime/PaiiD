import type { NextApiRequest, NextApiResponse } from "next";

// NOTE: API routes run server-side and use NON-PREFIXED env vars
// NEXT_PUBLIC_* is for client-side code only!
const BACKEND = process.env.BACKEND_API_BASE_URL || process.env.NEXT_PUBLIC_BACKEND_API_BASE_URL || 'https://paiid-backend.onrender.com';
const API_TOKEN = process.env.API_TOKEN || process.env.NEXT_PUBLIC_API_TOKEN || '';

if (!API_TOKEN) {
  console.error('[PROXY] ⚠️ API_TOKEN not configured in environment variables');
  console.error('[PROXY] ⚠️ Checked: process.env.API_TOKEN and process.env.NEXT_PUBLIC_API_TOKEN');
} else {
  console.log(`[PROXY] ✅ API_TOKEN loaded: ${API_TOKEN.substring(0, 10)}...`);
}

// Exact endpoints our UI uses (paths without /api prefix - added in URL construction)
const ALLOW_GET = new Set<string>([
  "health",
  "settings",
  "portfolio/positions",
  "ai/recommendations",
  "ai/signals",
  "market/historical",
  "screening/opportunities",
  "screening/strategies",
  "market/conditions",
  "market/indices",
  "market/sectors",
  // Live market data endpoints
  "market/quote",
  "market/quotes",
  "market/scanner/under4",
  "market/bars",
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
]);

const ALLOW_POST = new Set<string>([
  "trading/execute",
  "settings",
  "admin/kill",
  // Alpaca endpoints
  "orders",
  "watchlists",
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
]);

function isAllowedOrigin(req: NextApiRequest) {
  // EMERGENCY FIX: Allow ALL requests during debugging
  // This is TEMPORARY to identify the exact issue
  const origin = (req.headers.origin || "").toLowerCase();

  console.log(`[PROXY] ====== ORIGIN CHECK ======`);
  console.log(`[PROXY] Origin header: "${origin}"`);
  console.log(`[PROXY] Referer: "${req.headers.referer || 'none'}"`);
  console.log(`[PROXY] Host: "${req.headers.host || 'none'}"`);
  console.log(`[PROXY] URL: "${req.url}"`);

  // TEMPORARY: Just allow everything and log it
  console.log(`[PROXY] ✅ ALLOWING ALL ORIGINS (emergency debug mode)`);
  return true;
}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  // Log EVERY request for debugging
  console.log(`\n[PROXY] ====== NEW REQUEST ======`);
  console.log(`[PROXY] Method: ${req.method}`);
  console.log(`[PROXY] URL: ${req.url}`);
  console.log(`[PROXY] Origin: ${req.headers.origin || 'NONE'}`);

  // CORS preflight - SET HEADERS FIRST (before origin check)
  if (req.method === "OPTIONS") {
    console.log(`[PROXY] Handling OPTIONS preflight`);
    const origin = req.headers.origin || "*";
    res.setHeader("access-control-allow-origin", origin);
    res.setHeader("access-control-allow-methods", "GET,POST,DELETE,OPTIONS");
    res.setHeader("access-control-allow-headers", "content-type,x-request-id,authorization");
    res.setHeader("access-control-allow-credentials", "true");
    res.status(204).end();
    return;
  }

  const originAllowed = isAllowedOrigin(req);
  console.log(`[PROXY] Origin check result: ${originAllowed ? 'ALLOWED' : 'BLOCKED'}`);

  if (!originAllowed) {
    console.error(`[PROXY] ⛔ REJECTING REQUEST WITH 403`);
    res.status(403).json({ error: "Forbidden (origin)", origin: req.headers.origin || 'none', url: req.url });
    return;
  }

  // Set CORS headers for all successful responses
  const origin = req.headers.origin || "*";
  res.setHeader("access-control-allow-origin", origin);
  res.setHeader("access-control-allow-credentials", "true");

  console.log(`[PROXY] ✅ Origin check passed, proceeding with request`);


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
    const isAllowedPattern = Array.from(ALLOW_GET).some(allowed =>
      path.startsWith(allowed + "/") || path === allowed
    );
    if (!isAllowedPattern) {
      return res.status(405).json({ error: "Not allowed" });
    }
  }
  if (req.method === "POST" && !ALLOW_POST.has(path)) {
    const isAllowedPattern = Array.from(ALLOW_POST).some(allowed =>
      path.startsWith(allowed + "/") || path === allowed
    );
    if (!isAllowedPattern) {
      return res.status(405).json({ error: "Not allowed" });
    }
  }
  if (req.method === "DELETE" && !ALLOW_DELETE.has(path)) {
    const isAllowedPattern = Array.from(ALLOW_DELETE).some(allowed =>
      path.startsWith(allowed + "/") || path === allowed
    );
    if (!isAllowedPattern) {
      return res.status(405).json({ error: "Not allowed" });
    }
  }

  const url = `${BACKEND}/api/${path}`;
  const headers: Record<string, string> = {
    authorization: `Bearer ${API_TOKEN}`,
    "content-type": "application/json",
  };

  // propagate request id if client set one
  const rid = (req.headers["x-request-id"] as string) || "";
  if (rid) headers["x-request-id"] = rid;

  // Enhanced debug logging
  console.log(`\n[PROXY] ====== New Request ======`);
  console.log(`[PROXY] Method: ${req.method}`);
  console.log(`[PROXY] Original URL: ${req.url}`);
  console.log(`[PROXY] Extracted path: "${path}"`);
  console.log(`[PROXY] Constructed URL: ${url}`);
  console.log(`[PROXY] Auth header: Bearer ${API_TOKEN?.substring(0, 8)}...`);
  console.log(`[PROXY] Backend: ${BACKEND}`);
  if (req.method === "POST") {
    console.log(`[PROXY] Body:`, JSON.stringify(req.body, null, 2));
  }

  try {
    const upstream = await fetch(url, {
      method: req.method,
      headers,
      body: (req.method === "POST" || req.method === "DELETE") ? JSON.stringify(req.body ?? {}) : undefined,
      // avoid any CDN caching at the edge
      cache: "no-store",
    });

    const text = await upstream.text();
    console.log(`[PROXY] Response status: ${upstream.status}`);
    console.log(`[PROXY] Response body: ${text.substring(0, 200)}${text.length > 200 ? '...' : ''}`);
    console.log(`[PROXY] ====== End Request ======\n`);

    res
      .status(upstream.status)
      .setHeader("content-type", upstream.headers.get("content-type") || "application/json")
      .setHeader("cache-control", "no-store")
      .send(text);
  } catch (err) {
    console.error(`[PROXY] ERROR: ${err}`);
    console.error(`[PROXY] Error details:`, err);
    console.log(`[PROXY] ====== End Request (ERROR) ======\n`);
    res.status(502).json({ error: "Upstream error", detail: String(err) });
  }
}
