import type { Page } from "@playwright/test";

type OptionContract = {
  symbol: string;
  underlying_symbol: string;
  option_type: "call" | "put";
  strike_price: number;
  expiration_date: string;
  bid?: number;
  ask?: number;
  last_price?: number;
  volume?: number;
  open_interest?: number;
  delta?: number;
  gamma?: number;
  theta?: number;
  vega?: number;
  rho?: number;
  implied_volatility?: number;
};

type ChainResponse = {
  symbol: string;
  expiration_date: string;
  underlying_price: number;
  calls: OptionContract[];
  puts: OptionContract[];
  total_contracts: number;
};

type ExpirationResponse = {
  date: string;
  days_to_expiry: number;
};

const BASE_SYMBOL = "OPTT";
const EXPIRATION_FIXTURES: Record<string, ExpirationResponse[]> = {
  [BASE_SYMBOL]: [
    { date: "2025-01-17", days_to_expiry: 92 },
    { date: "2025-02-21", days_to_expiry: 127 },
  ],
};

function buildContract(
  option_type: "call" | "put",
  strike_price: number,
  expiration_date: string,
  overrides: Partial<OptionContract> = {}
): OptionContract {
  const prefix = `${BASE_SYMBOL}${expiration_date.replace(/-/g, "").slice(2)}`;
  const typeCode = option_type === "call" ? "C" : "P";
  const strike = (strike_price * 1000).toString().padStart(8, "0");

  return {
    symbol: `${prefix}${typeCode}${strike}`,
    underlying_symbol: BASE_SYMBOL,
    option_type,
    strike_price,
    expiration_date,
    bid: 1.1,
    ask: 1.3,
    last_price: 1.2,
    volume: 125,
    open_interest: 432,
    delta: option_type === "call" ? 0.42 : -0.38,
    gamma: 0.07,
    theta: option_type === "call" ? -0.05 : -0.04,
    vega: 0.12,
    rho: option_type === "call" ? 0.02 : -0.02,
    implied_volatility: 0.41,
    ...overrides,
  };
}

function buildChain(expiration: string): ChainResponse {
  const strikes = [10, 12.5, 15];

  const calls = strikes.map((strike) => buildContract("call", strike, expiration));
  const puts = strikes.map((strike) => buildContract("put", strike, expiration));

  return {
    symbol: BASE_SYMBOL,
    expiration_date: expiration,
    underlying_price: 11.85,
    calls,
    puts,
    total_contracts: calls.length + puts.length,
  };
}

const CHAIN_FIXTURE: Record<string, ChainResponse> = {
  [`${BASE_SYMBOL}::2025-01-17`]: buildChain("2025-01-17"),
  [`${BASE_SYMBOL}::2025-02-21`]: buildChain("2025-02-21"),
};

function extractSymbolFromUrl(url: URL): string {
  const segments = url.pathname.split("/");
  return segments[segments.length - 1].toUpperCase();
}

export async function mockOptionsEndpoints(page: Page): Promise<void> {
  await page.route("**/api/proxy/options/expirations/**", async (route) => {
    const url = new URL(route.request().url());
    const symbol = extractSymbolFromUrl(url);
    const data = EXPIRATION_FIXTURES[symbol];

    if (!data) {
      await route.fulfill({
        status: 404,
        contentType: "application/json",
        body: JSON.stringify({ detail: `Unknown symbol: ${symbol}` }),
      });
      return;
    }

    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(data),
    });
  });

  await page.route("**/api/proxy/options/chain/**", async (route) => {
    const url = new URL(route.request().url());
    const symbol = extractSymbolFromUrl(url);
    const expiration = url.searchParams.get("expiration") ?? "";

    if (!EXPIRATION_FIXTURES[symbol]) {
      await route.fulfill({
        status: 404,
        contentType: "application/json",
        body: JSON.stringify({ detail: `Unknown symbol: ${symbol}` }),
      });
      return;
    }

    const key = `${symbol}::${expiration}`;
    const chain =
      CHAIN_FIXTURE[key] ?? buildChain(expiration || EXPIRATION_FIXTURES[symbol][0].date);

    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(chain),
    });
  });
}
