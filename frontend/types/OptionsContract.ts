/**
 * TypeScript interface for options contract data
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
