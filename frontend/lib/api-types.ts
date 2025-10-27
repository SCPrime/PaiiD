/**
 * PaiiD Trading Platform API Type Definitions
 *
 * Auto-generated TypeScript interfaces matching backend Pydantic models
 * Last updated: 2025-10-27
 * Backend API version: 1.0.0
 */

// ============================================================================
// PORTFOLIO TYPES
// ============================================================================

export interface PositionResponse {
  symbol: string;
  quantity: number;
  cost_basis: number;
  market_value: number;
  unrealized_pl: number;
  unrealized_plpc: number;
  change_today: number;
}

export interface PositionsResponse {
  data: PositionResponse[];
  count: number;
  timestamp: string;
}

export interface AccountResponse {
  data: {
    account_number?: string;
    total_equity?: number;
    total_cash?: number;
    option_buying_power?: number;
    [key: string]: any;
  };
  timestamp: string;
}

// ============================================================================
// ANALYTICS TYPES
// ============================================================================

export interface PortfolioSummary {
  total_value: number;
  cash: number;
  buying_power: number;
  total_pl: number;
  total_pl_percent: number;
  day_pl: number;
  day_pl_percent: number;
  num_positions: number;
  num_winning: number;
  num_losing: number;
  largest_winner?: {
    symbol: string;
    pl: number;
    pl_percent: number;
  };
  largest_loser?: {
    symbol: string;
    pl: number;
    pl_percent: number;
  };
}

export interface EquityPoint {
  timestamp: string;
  equity: number;
  cash: number;
  positions_value: number;
}

export interface PortfolioHistory {
  period: '1D' | '1W' | '1M' | '3M' | '1Y' | 'ALL';
  start_date: string;
  end_date: string;
  data: EquityPoint[];
  is_simulated: boolean;
}

export interface PerformanceMetrics {
  total_return: number;
  total_return_percent: number;
  sharpe_ratio: number;
  max_drawdown: number;
  max_drawdown_percent: number;
  win_rate: number;
  avg_win: number;
  avg_loss: number;
  profit_factor: number;
  num_trades: number;
  num_wins: number;
  num_losses: number;
  current_streak: number;
  best_day: number;
  worst_day: number;
}

// ============================================================================
// MARKET DATA TYPES
// ============================================================================

export interface QuoteResponse {
  symbol: string;
  bid: number;
  ask: number;
  last: number;
  volume: number;
  timestamp: string;
  cached?: boolean;
}

export interface HistoricalBar {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface HistoricalBarsResponse {
  symbol: string;
  interval: 'daily' | 'weekly' | 'monthly';
  start_date: string;
  end_date: string;
  bars: HistoricalBar[];
  count: number;
}

export interface IndexData {
  last: number;
  change: number;
  changePercent: number;
}

export interface IndicesResponse {
  dow: IndexData;
  nasdaq: IndexData;
  source: string;
  cached?: boolean;
}

export interface MarketCondition {
  name: string;
  value: string;
  status: 'favorable' | 'neutral' | 'unfavorable';
  details?: string;
}

export interface MarketConditionsResponse {
  conditions: MarketCondition[];
  timestamp: string;
  overallSentiment: 'bullish' | 'neutral' | 'bearish';
  recommendedActions: string[];
  source: string;
}

export interface SectorData {
  name: string;
  symbol: string;
  changePercent: number;
  last: number;
  rank: number;
}

export interface SectorPerformanceResponse {
  sectors: SectorData[];
  timestamp: string;
  leader: string;
  laggard: string;
  source: string;
}

// ============================================================================
// AI RECOMMENDATION TYPES
// ============================================================================

export interface TradeData {
  symbol: string;
  side: 'buy' | 'sell';
  quantity: number;
  orderType: 'market' | 'limit';
  entryPrice?: number;
  stopLoss?: number;
  takeProfit?: number;
}

export interface Recommendation {
  symbol: string;
  action: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  score: number;
  reason: string;
  targetPrice: number;
  currentPrice: number;
  timeframe: string;
  risk: 'Low' | 'Medium' | 'High';
  entryPrice?: number;
  stopLoss?: number;
  takeProfit?: number;
  riskRewardRatio?: number;
  indicators?: Record<string, any>;
  tradeData?: TradeData;
  portfolioFit?: string;
  momentum?: Record<string, any>;
  volatility?: Record<string, any>;
  sector?: string;
  sectorPerformance?: Record<string, any>;
  explanation?: string;
}

export interface PortfolioAnalysis {
  totalPositions: number;
  totalValue: number;
  topSectors: Array<{ name: string; percentage: number }>;
  riskScore: number;
  diversificationScore: number;
  recommendations: string[];
}

export interface RecommendationsResponse {
  recommendations: Recommendation[];
  portfolioAnalysis?: PortfolioAnalysis;
  generated_at: string;
  model_version: string;
}

export interface SymbolAnalysis {
  symbol: string;
  current_price: number;
  analysis: string;
  momentum: string;
  trend: string;
  support_level: number;
  resistance_level: number;
  risk_assessment: string;
  entry_suggestion: string;
  exit_suggestion: string;
  stop_loss_suggestion: number;
  take_profit_suggestion: number;
  confidence_score: number;
  key_indicators: Record<string, any>;
  summary: string;
}

// ============================================================================
// ORDER TYPES
// ============================================================================

export interface OrderResponse {
  accepted: boolean;
  dryRun: boolean;
  duplicate?: boolean;
  orders: Array<{
    symbol: string;
    side: string;
    qty: number;
    type: string;
    limit_price?: number;
    alpaca_order_id?: string;
    status?: string;
  }>;
}

export interface OrderTemplateResponse {
  id: number;
  user_id?: number;
  name: string;
  description?: string;
  symbol: string;
  side: string;
  quantity: number;
  order_type: string;
  limit_price?: number;
  created_at: string;
  updated_at: string;
  last_used_at?: string;
}

// ============================================================================
// HEALTH CHECK TYPES
// ============================================================================

export interface HealthResponse {
  status: string;
  time: string;
}

export interface DetailedHealthResponse {
  status: string;
  timestamp: string;
  components: Record<string, any>;
  metrics?: Record<string, any>;
}

// ============================================================================
// API CLIENT FUNCTIONS
// ============================================================================

/**
 * Fetches portfolio summary with equity, P&L, and largest positions.
 * @returns {Promise<PortfolioSummary>} Portfolio summary data
 * @throws {Error} If API request fails
 */
export async function getPortfolioSummary(): Promise<PortfolioSummary> {
  const response = await fetch('/api/proxy/portfolio/summary', {
    headers: { 'Authorization': `Bearer ${process.env.NEXT_PUBLIC_API_TOKEN}` }
  });
  if (!response.ok) throw new Error('Failed to fetch portfolio summary');
  return response.json();
}

/**
 * Fetches historical portfolio equity data
 * @param period - Time period (1D, 1W, 1M, 3M, 1Y, ALL)
 * @returns {Promise<PortfolioHistory>} Portfolio history data
 * @throws {Error} If API request fails
 */
export async function getPortfolioHistory(period: string = '1M'): Promise<PortfolioHistory> {
  const response = await fetch(`/api/proxy/portfolio/history?period=${period}`, {
    headers: { 'Authorization': `Bearer ${process.env.NEXT_PUBLIC_API_TOKEN}` }
  });
  if (!response.ok) throw new Error('Failed to fetch portfolio history');
  return response.json();
}

/**
 * Fetches comprehensive performance metrics
 * @param period - Time period for calculations
 * @returns {Promise<PerformanceMetrics>} Performance metrics
 * @throws {Error} If API request fails
 */
export async function getPerformanceMetrics(period: string = '1M'): Promise<PerformanceMetrics> {
  const response = await fetch(`/api/proxy/analytics/performance?period=${period}`, {
    headers: { 'Authorization': `Bearer ${process.env.NEXT_PUBLIC_API_TOKEN}` }
  });
  if (!response.ok) throw new Error('Failed to fetch performance metrics');
  return response.json();
}

/**
 * Fetches current positions from Tradier account
 * @returns {Promise<PositionsResponse>} Positions list
 * @throws {Error} If API request fails
 */
export async function getPositions(): Promise<PositionsResponse> {
  const response = await fetch('/api/proxy/positions', {
    headers: { 'Authorization': `Bearer ${process.env.NEXT_PUBLIC_API_TOKEN}` }
  });
  if (!response.ok) throw new Error('Failed to fetch positions');
  return response.json();
}

/**
 * Fetches real-time quote for a symbol
 * @param symbol - Stock symbol (e.g., "AAPL")
 * @returns {Promise<QuoteResponse>} Real-time quote data
 * @throws {Error} If API request fails
 */
export async function getQuote(symbol: string): Promise<QuoteResponse> {
  const response = await fetch(`/api/proxy/market/quote/${symbol}`, {
    headers: { 'Authorization': `Bearer ${process.env.NEXT_PUBLIC_API_TOKEN}` }
  });
  if (!response.ok) throw new Error(`Failed to fetch quote for ${symbol}`);
  return response.json();
}

/**
 * Fetches AI-powered trading recommendations
 * @returns {Promise<RecommendationsResponse>} AI recommendations
 * @throws {Error} If API request fails
 */
export async function getRecommendations(): Promise<RecommendationsResponse> {
  const response = await fetch('/api/proxy/ai/recommendations', {
    headers: { 'Authorization': `Bearer ${process.env.NEXT_PUBLIC_API_TOKEN}` }
  });
  if (!response.ok) throw new Error('Failed to fetch AI recommendations');
  return response.json();
}

/**
 * Fetches major market indices (Dow Jones, NASDAQ)
 * @returns {Promise<IndicesResponse>} Market indices data
 * @throws {Error} If API request fails
 */
export async function getMarketIndices(): Promise<IndicesResponse> {
  const response = await fetch('/api/proxy/market/indices', {
    headers: { 'Authorization': `Bearer ${process.env.NEXT_PUBLIC_API_TOKEN}` }
  });
  if (!response.ok) throw new Error('Failed to fetch market indices');
  return response.json();
}
