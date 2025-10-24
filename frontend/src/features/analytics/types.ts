import type { CandlestickData, Time } from "lightweight-charts";

export interface PositionSlice {
  symbol: string;
  allocation: number;
  costBasis?: number;
  marketValue?: number;
  dayPnl?: number;
}

export interface OptionGreekSnapshot {
  symbol: string;
  expiry?: string;
  delta: number;
  gamma: number;
  theta: number;
  vega: number;
  rho?: number;
}

export type CandleDatum = CandlestickData<Time> & {
  volume?: number;
};

export interface TimeframeOption {
  id: string;
  label: string;
  interval: string;
}
