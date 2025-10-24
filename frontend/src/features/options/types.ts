export type StrategyKey =
  | "iron_condor"
  | "butterfly"
  | "vertical_call"
  | "vertical_put"
  | "straddle"
  | "strangle"
  | "custom";

export interface OptionGreeks {
  delta?: number | null;
  gamma?: number | null;
  theta?: number | null;
  vega?: number | null;
  rho?: number | null;
}

export interface OptionContractQuote {
  symbol: string;
  underlying_symbol: string;
  option_type: "call" | "put";
  strike_price: number;
  expiration_date: string;
  bid?: number | null;
  ask?: number | null;
  last_price?: number | null;
  mark_price?: number | null;
  volume?: number | null;
  open_interest?: number | null;
  implied_volatility?: number | null;
  greeks?: OptionGreeks;
  days_to_expiration: number;
}

export interface OptionLegQuote {
  id: string;
  action: "BUY" | "SELL";
  optionType: "call" | "put";
  strike: number;
  expiration: string;
  quantity: number;
  price?: number;
  contractSymbol: string;
  underlyingPrice?: number | null;
  impliedVolatility?: number | null;
  greeks?: OptionGreeks;
  metadata?: Record<string, unknown>;
}

export interface OptionChainSelection {
  strategy: StrategyKey;
  legs: OptionLegQuote[];
  underlyingPrice?: number | null;
}

export interface OptionExpirationSummary {
  date: string;
  days_to_expiry: number;
}

export interface OptionChainPayload {
  symbol: string;
  expiration_date: string;
  underlying_price?: number | null;
  calls: OptionContractQuote[];
  puts: OptionContractQuote[];
  total_contracts: number;
}
