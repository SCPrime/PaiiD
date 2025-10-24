export interface Quote {
  symbol: string;
  price: number;
  bid: number;
  ask: number;
  change?: number;
  changePct?: number;
  timestamp: string;
  source?: string;
  cached?: boolean;
}

export interface IndexData {
  [symbol: string]: {
    price: number;
    prev_close: number;
    change: number;
    change_pct: number;
  };
}

export interface ScannerResult {
  symbol: string;
  price: number;
  bid: number;
  ask: number;
  timestamp: string;
}

export async function fetchQuote(symbol: string): Promise<Quote> {
  const res = await fetch(`/api/proxy/api/market/quote/${symbol}`);
  if (!res.ok) throw new Error(`Failed to fetch quote for ${symbol}`);
  const data = await res.json();
  return data.quote ?? data;
}

export async function fetchQuotes(symbols: string[]): Promise<Record<string, Quote>> {
  const symbolsStr = symbols.join(",");
  const res = await fetch(`/api/proxy/api/market/quotes?symbols=${symbolsStr}`);
  if (!res.ok) throw new Error("Failed to fetch quotes");
  const data = await res.json();
  return data.quotes ?? data;
}

export async function fetchIndices(): Promise<IndexData> {
  const res = await fetch("/api/proxy/api/market/indices");
  if (!res.ok) throw new Error("Failed to fetch indices");
  return await res.json();
}

export async function fetchUnder4Scanner(): Promise<{
  candidates: ScannerResult[];
  count: number;
}> {
  const res = await fetch("/api/proxy/api/market/scanner/under4");
  if (!res.ok) throw new Error("Failed to fetch scanner results");
  const data = await res.json();
  return {
    candidates: data.candidates ?? [],
    count: data.count ?? 0,
  };
}

export async function fetchBars(
  symbol: string,
  timeframe: "1Min" | "5Min" | "1Hour" | "1Day" = "1Day",
  limit: number = 100
): Promise<any> {
  const res = await fetch(
    `/api/proxy/api/market/bars/${symbol}?timeframe=${timeframe}&limit=${limit}`
  );
  if (!res.ok) throw new Error(`Failed to fetch bars for ${symbol}`);
  return await res.json();
}
