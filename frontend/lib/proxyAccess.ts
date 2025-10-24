export const ALLOW_GET = new Set<string>([
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
  "market/status",
  // Live market data endpoints
  "market/quote",
  "market/quotes",
  "market/scanner/under4",
  "market/bars",
  // Options endpoints
  "options/greeks",
  "options/chain",
  "options/chains",
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

export const ALLOW_POST = new Set<string>([
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

export const ALLOW_DELETE = new Set<string>([
  // Alpaca endpoints
  "positions",
  "orders",
  "watchlists",
  // Order templates
  "order-templates",
]);

export function isPathAllowed(path: string, allowedSet: Set<string>): boolean {
  if (allowedSet.has(path)) {
    return true;
  }

  const allowList = Array.from(allowedSet);
  for (let index = 0; index < allowList.length; index += 1) {
    const allowed = allowList[index];

    if (!allowed) {
      continue;
    }

    if (path === allowed || path.startsWith(`${allowed}/`)) {
      return true;
    }
  }

  return false;
}
