export type OptionContract = {
  symbol: string;
  underlying_symbol: string;
  option_type: "call" | "put";
  strike_price: number;
  expiration_date: string;
  bid: number | null;
  ask: number | null;
  last_price: number | null;
  volume: number | null;
  open_interest: number | null;
  delta: number | null;
  gamma: number | null;
  theta: number | null;
  vega: number | null;
  rho: number | null;
  implied_volatility: number | null;
};

export type OptionsFixture = {
  symbol: string;
  expiration_date: string;
  underlying_price: number | null;
  calls: OptionContract[];
  puts: OptionContract[];
  total_contracts: number;
};

export const SPY_OPTIONS_FIXTURE: OptionsFixture = {
  symbol: "SPY",
  expiration_date: "2024-01-19",
  underlying_price: 430.12,
  calls: [
    {
      symbol: "SPY240119C00430000",
      underlying_symbol: "SPY",
      option_type: "call",
      strike_price: 430,
      expiration_date: "2024-01-19",
      bid: 5.5,
      ask: 5.75,
      last_price: 5.62,
      volume: 123,
      open_interest: 456,
      delta: 0.52,
      gamma: 0.08,
      theta: -0.03,
      vega: 0.11,
      rho: 0.04,
      implied_volatility: 0.22,
    },
  ],
  puts: [
    {
      symbol: "SPY240119P00430000",
      underlying_symbol: "SPY",
      option_type: "put",
      strike_price: 430,
      expiration_date: "2024-01-19",
      bid: 5.4,
      ask: 5.6,
      last_price: 5.48,
      volume: 98,
      open_interest: 321,
      delta: -0.48,
      gamma: 0.07,
      theta: -0.02,
      vega: 0.12,
      rho: -0.04,
      implied_volatility: 0.23,
    },
  ],
  total_contracts: 2,
};

export const OPTT_OPTIONS_FIXTURE: OptionsFixture = {
  symbol: "OPTT",
  expiration_date: "2024-02-16",
  underlying_price: 2.85,
  calls: [
    {
      symbol: "OPTT240216C00030000",
      underlying_symbol: "OPTT",
      option_type: "call",
      strike_price: 3,
      expiration_date: "2024-02-16",
      bid: 0.25,
      ask: 0.35,
      last_price: 0.3,
      volume: 420,
      open_interest: 600,
      delta: 0.31,
      gamma: 0.12,
      theta: -0.01,
      vega: 0.05,
      rho: 0,
      implied_volatility: 0.75,
    },
  ],
  puts: [
    {
      symbol: "OPTT240216P00030000",
      underlying_symbol: "OPTT",
      option_type: "put",
      strike_price: 3,
      expiration_date: "2024-02-16",
      bid: 0.45,
      ask: 0.55,
      last_price: 0.5,
      volume: 210,
      open_interest: 350,
      delta: -0.69,
      gamma: 0.15,
      theta: -0.02,
      vega: 0.07,
      rho: -0.01,
      implied_volatility: 0.82,
    },
  ],
  total_contracts: 2,
};

export const OPTIONS_FIXTURES = {
  SPY: SPY_OPTIONS_FIXTURE,
  OPTT: OPTT_OPTIONS_FIXTURE,
};
