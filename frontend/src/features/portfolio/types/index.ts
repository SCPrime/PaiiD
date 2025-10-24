export interface PortfolioGreekTotals {
  delta: number;
  gamma: number;
  theta: number;
  vega: number;
  rho: number;
}

export interface PortfolioGreekBreakdown {
  symbol: string;
  quantity: number;
  side: string;
  multiplier: number;
  greeks: Record<string, number>;
  exposures: Record<string, number>;
}

export interface PortfolioGreekAnalytics {
  totals: PortfolioGreekTotals;
  breakdown: PortfolioGreekBreakdown[];
}

export interface EquityHistoryPoint {
  timestamp: string;
  equity: number;
  cash: number;
  positions_value: number;
}

export interface PortfolioHistoryResponse {
  period: string;
  start_date: string;
  end_date: string;
  data: EquityHistoryPoint[];
  is_simulated: boolean;
}
