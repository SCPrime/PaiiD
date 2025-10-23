/**
 * TypeScript interface for options contract data
 * Includes symbol, pricing, expiration, type, and Greeks
 */

export interface Greeks {
  delta: number;
  gamma: number;
  theta: number;
  vega: number;
}

export interface OptionsContract {
  symbol: string;
  strike_price: number;
  expiration_date: string;
  option_type: "call" | "put";
  greeks: Greeks;
}

// Optional: Extended interface with additional common fields
export interface ExtendedOptionsContract extends OptionsContract {
  bid?: number;
  ask?: number;
  last_price?: number;
  volume?: number;
  open_interest?: number;
  implied_volatility?: number;
}
