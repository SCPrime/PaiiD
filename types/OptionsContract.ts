/**
 * TypeScript interface for an options contract
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
  option_type: 'call' | 'put';
  greeks: Greeks;
}

export const exampleContract: OptionsContract = {
  symbol: 'AAPL',
  strike_price: 150.0,
  expiration_date: '2024-01-19',
  option_type: 'call',
  greeks: {
    delta: 0.65,
    gamma: 0.02,
    theta: -0.15,
    vega: 0.25,
  },
};
