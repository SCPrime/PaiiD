export type RecommendationAction = "BUY" | "SELL" | "HOLD";
export type RecommendationRiskLevel = "Low" | "Medium" | "High";
export type RecommendationVolatilityClass = "Low" | "Medium" | "High";

export interface RecommendationMomentum {
  sma_20: number;
  sma_50: number;
  sma_200: number;
  price_vs_sma_20: number;
  price_vs_sma_50: number;
  price_vs_sma_200: number;
  avg_volume_20d: number;
  volume_strength: string;
  volume_ratio: number;
  trend_alignment: string;
}

export interface RecommendationVolatility {
  atr: number;
  atr_percent: number;
  bb_width: number;
  volatility_class: RecommendationVolatilityClass;
  volatility_score: number;
}

export interface RecommendationIndicators {
  rsi?: number;
  macd?: { macd: number; signal: number; histogram: number };
  bollinger_bands?: { upper: number; middle: number; lower: number };
  moving_averages?: { sma_20?: number; sma_50?: number; sma_200?: number; ema_12?: number };
  trend?: { direction: string; strength: number; support: number; resistance: number };
}

export interface RecommendationTradeData {
  symbol: string;
  side: "buy" | "sell";
  quantity: number;
  orderType: "market" | "limit";
  entryPrice?: number;
  stopLoss?: number;
  takeProfit?: number;
}

export interface Recommendation {
  id?: number;
  symbol: string;
  action: RecommendationAction;
  confidence: number;
  score: number;
  reason: string;
  targetPrice: number;
  currentPrice: number;
  timeframe?: string;
  risk?: RecommendationRiskLevel;
  entryPrice?: number;
  stopLoss?: number;
  takeProfit?: number;
  riskRewardRatio?: number;
  tradeData?: RecommendationTradeData;
  portfolioFit?: string;
  momentum?: RecommendationMomentum;
  volatility?: RecommendationVolatility;
  sector?: string;
  sectorPerformance?: {
    name: string;
    changePercent: number;
    rank: number;
    isLeader: boolean;
    isLaggard: boolean;
  };
  explanation?: string;
  indicators?: RecommendationIndicators;
  marketContext?: string;
  tags?: string[];
}

export interface PortfolioAnalysis {
  totalPositions: number;
  totalValue: number;
  topSectors: Array<{ name: string; percentage: number }>;
  riskScore: number;
  diversificationScore: number;
  recommendations: string[];
}

export type RecommendationSortKey =
  | "confidence"
  | "score"
  | "volatility"
  | "momentum"
  | "risk"
  | "symbol";
export type SortDirection = "asc" | "desc";

export interface RecommendationFilterState {
  search: string;
  minConfidence: number;
  actions: RecommendationAction[];
  riskLevels: RecommendationRiskLevel[];
  volatilityClass: RecommendationVolatilityClass | "All";
  momentumTrend: string | "All";
  sortBy: RecommendationSortKey;
  sortDirection: SortDirection;
}
