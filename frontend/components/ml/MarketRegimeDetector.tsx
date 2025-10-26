/**
 * Market Regime Detector Component
 *
 * Detects current market regime and provides strategy recommendations.
 * Makes complex market analysis accessible for friends and family.
 */

import {
  BarChart3,
  Loader2,
  Minus,
  RefreshCw,
  Target,
  TrendingDown,
  TrendingUp,
  Zap,
} from "lucide-react";
import React, { useEffect, useState } from "react";
import { logger } from "../../lib/logger";
import HelpTooltip from "../HelpTooltip";

interface MarketRegime {
  regime: "trending_bullish" | "trending_bearish" | "ranging" | "high_volatility";
  confidence: number;
  features: {
    trend_direction: number;
    trend_strength: number;
    volatility: number;
    rsi: number;
    volume_trend: number;
  };
  recommended_strategies: string[];
  cluster_id: number;
}

interface StrategyRecommendation {
  strategy_id: string;
  probability: number;
  confidence: number;
  description: string;
  risk_level: "low" | "medium" | "high";
  expected_return: number;
  time_horizon: string;
}

interface MarketRegimeDetectorProps {
  symbol?: string;
  onRegimeChange?: (regime: MarketRegime) => void;
}

export const MarketRegimeDetector: React.FC<MarketRegimeDetectorProps> = ({
  symbol = "SPY",
  onRegimeChange,
}) => {
  const [regime, setRegime] = useState<MarketRegime | null>(null);
  const [strategyRecommendations, setStrategyRecommendations] = useState<StrategyRecommendation[]>(
    []
  );
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedStrategy, setSelectedStrategy] = useState<string | null>(null);

  useEffect(() => {
    loadMarketRegime();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [symbol]);

  const loadMarketRegime = async () => {
    setLoading(true);
    try {
      // Load market regime
      const regimeResponse = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_API_BASE_URL}/api/ml/market-regime?symbol=${symbol}&lookback_days=90`
      );
      const regimeData = await regimeResponse.json();

      if (regimeData.regime) {
        setRegime(regimeData);
        onRegimeChange?.(regimeData);
      }

      // Load strategy recommendations
      const strategyResponse = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_API_BASE_URL}/api/ml/recommend-strategy?symbol=${symbol}&lookback_days=90&top_n=5`
      );
      const strategyData = await strategyResponse.json();

      if (strategyData.recommendations) {
        setStrategyRecommendations(strategyData.recommendations);
      }
    } catch (error) {
      logger.error("Failed to load market regime", error);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadMarketRegime();
    setRefreshing(false);
  };

  const getRegimeIcon = (regimeType: string) => {
    switch (regimeType) {
      case "trending_bullish":
        return <TrendingUp className="w-6 h-6 text-green-500" />;
      case "trending_bearish":
        return <TrendingDown className="w-6 h-6 text-red-500" />;
      case "ranging":
        return <Minus className="w-6 h-6 text-gray-500" />;
      case "high_volatility":
        return <BarChart3 className="w-6 h-6 text-orange-500" />;
      default:
        return <Target className="w-6 h-6 text-blue-500" />;
    }
  };

  const getRegimeColor = (regimeType: string) => {
    switch (regimeType) {
      case "trending_bullish":
        return "text-green-600 bg-green-50 border-green-200";
      case "trending_bearish":
        return "text-red-600 bg-red-50 border-red-200";
      case "ranging":
        return "text-gray-600 bg-gray-50 border-gray-200";
      case "high_volatility":
        return "text-orange-600 bg-orange-50 border-orange-200";
      default:
        return "text-blue-600 bg-blue-50 border-blue-200";
    }
  };

  const getRegimeDescription = (regimeType: string, _confidence: number) => {
    const descriptions = {
      trending_bullish: {
        title: "Bullish Trend",
        description:
          "Market is in a strong upward trend with positive momentum. This is typically a good time for growth strategies.",
        characteristics: [
          "Rising prices",
          "High volume on up days",
          "Higher highs and higher lows",
          "Positive sentiment",
        ],
        strategy_focus: "Focus on momentum and trend-following strategies",
      },
      trending_bearish: {
        title: "Bearish Trend",
        description:
          "Market is in a downward trend with negative momentum. This requires defensive strategies and risk management.",
        characteristics: [
          "Falling prices",
          "High volume on down days",
          "Lower highs and lower lows",
          "Negative sentiment",
        ],
        strategy_focus: "Focus on defensive and contrarian strategies",
      },
      ranging: {
        title: "Sideways Market",
        description:
          "Market is moving sideways with no clear direction. This is ideal for range-bound trading strategies.",
        characteristics: [
          "Price bouncing between support and resistance",
          "Low volatility",
          "Mixed signals",
          "Consolidation",
        ],
        strategy_focus: "Focus on mean reversion and range trading",
      },
      high_volatility: {
        title: "High Volatility",
        description:
          "Market is experiencing high volatility with large price swings. This requires careful risk management.",
        characteristics: [
          "Large daily price swings",
          "Increased uncertainty",
          "High volume",
          "Rapid changes",
        ],
        strategy_focus: "Focus on volatility strategies and risk management",
      },
    };

    return (
      descriptions[regimeType as keyof typeof descriptions] || {
        title: "Unknown Regime",
        description: "Market regime is unclear.",
        characteristics: [],
        strategy_focus: "Monitor market conditions",
      }
    );
  };

  const getStrategyDescription = (strategyId: string) => {
    const descriptions = {
      "trend-following-ma-crossover": {
        name: "Moving Average Crossover",
        description:
          "Buy when short-term MA crosses above long-term MA, sell when it crosses below.",
        risk_level: "medium",
        time_horizon: "Medium-term (weeks to months)",
        best_for: "Trending markets",
      },
      "momentum-breakout": {
        name: "Momentum Breakout",
        description: "Buy when price breaks above resistance with high volume.",
        risk_level: "high",
        time_horizon: "Short to medium-term (days to weeks)",
        best_for: "Strong trending markets",
      },
      "mean-reversion-bb-rsi": {
        name: "Mean Reversion (Bollinger Bands + RSI)",
        description: "Buy when price is oversold (low RSI, near lower Bollinger Band).",
        risk_level: "medium",
        time_horizon: "Short-term (days to weeks)",
        best_for: "Ranging markets",
      },
      "support-resistance-bounce": {
        name: "Support/Resistance Bounce",
        description: "Buy at support levels, sell at resistance levels.",
        risk_level: "low",
        time_horizon: "Short-term (days)",
        best_for: "Ranging markets",
      },
      "volatility-breakout": {
        name: "Volatility Breakout",
        description: "Trade breakouts during high volatility periods.",
        risk_level: "high",
        time_horizon: "Short-term (days)",
        best_for: "High volatility markets",
      },
      "options-straddle": {
        name: "Options Straddle",
        description:
          "Buy both call and put options to profit from large moves in either direction.",
        risk_level: "high",
        time_horizon: "Short-term (days to weeks)",
        best_for: "High volatility markets",
      },
    };

    return (
      descriptions[strategyId as keyof typeof descriptions] || {
        name: strategyId.replace("-", " ").toUpperCase(),
        description: "Strategy details not available.",
        risk_level: "medium",
        time_horizon: "Medium-term",
        best_for: "General market conditions",
      }
    );
  };

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case "low":
        return "text-green-600 bg-green-50";
      case "medium":
        return "text-yellow-600 bg-yellow-50";
      case "high":
        return "text-red-600 bg-red-50";
      default:
        return "text-gray-600 bg-gray-50";
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        <span className="ml-3 text-gray-600">Analyzing market regime...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <BarChart3 className="w-6 h-6 text-blue-600" />
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Market Regime Analysis</h3>
            <p className="text-sm text-gray-600">AI-powered market state detection</p>
          </div>
        </div>

        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          <RefreshCw className={`w-4 h-4 ${refreshing ? "animate-spin" : ""}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Market Regime Card */}
      {regime && (
        <div className={`border rounded-xl p-6 ${getRegimeColor(regime.regime)}`}>
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center space-x-3">
              {getRegimeIcon(regime.regime)}
              <div>
                <h4 className="text-xl font-semibold text-gray-900">
                  {getRegimeDescription(regime.regime, regime.confidence).title}
                </h4>
                <p className="text-gray-600">
                  {getRegimeDescription(regime.regime, regime.confidence).description}
                </p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-blue-600">
                {Math.round(regime.confidence * 100)}%
              </div>
              <div className="text-sm text-gray-500">Confidence</div>
            </div>
          </div>

          {/* Market Characteristics */}
          <div className="mb-4">
            <h5 className="font-medium text-gray-900 mb-2">Market Characteristics:</h5>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {regime.features.trend_direction > 0 ? "+" : ""}
                  {Math.round(regime.features.trend_direction * 100)}%
                </div>
                <div className="text-xs text-gray-500">Trend Direction</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {Math.round(regime.features.trend_strength * 100)}%
                </div>
                <div className="text-xs text-gray-500">Trend Strength</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {Math.round(regime.features.volatility * 100)}%
                </div>
                <div className="text-xs text-gray-500">Volatility</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {Math.round(regime.features.rsi)}
                </div>
                <div className="text-xs text-gray-500">RSI</div>
              </div>
            </div>
          </div>

          {/* Strategy Focus */}
          <div className="p-3 bg-white bg-opacity-50 rounded-lg">
            <div className="flex items-center space-x-2 mb-2">
              <Zap className="w-4 h-4 text-blue-600" />
              <span className="font-medium text-gray-900">Strategy Focus:</span>
            </div>
            <p className="text-sm text-gray-700">
              {getRegimeDescription(regime.regime, regime.confidence).strategy_focus}
            </p>
          </div>
        </div>
      )}

      {/* Strategy Recommendations */}
      {strategyRecommendations.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-xl p-6">
          <div className="flex items-center space-x-2 mb-4">
            <Target className="w-5 h-5 text-purple-600" />
            <h3 className="text-lg font-semibold text-gray-900">Recommended Strategies</h3>
            <HelpTooltip content="AI-recommended trading strategies based on current market conditions. Higher probability strategies are more likely to succeed in the current regime." />
          </div>

          <div className="space-y-3">
            {strategyRecommendations.map((strategy, index) => {
              const strategyInfo = getStrategyDescription(strategy.strategy_id);
              return (
                <div
                  key={index}
                  className={`border rounded-lg p-4 cursor-pointer transition-all hover:shadow-md ${
                    selectedStrategy === strategy.strategy_id ? "ring-2 ring-blue-500" : ""
                  }`}
                  onClick={() =>
                    setSelectedStrategy(
                      selectedStrategy === strategy.strategy_id ? null : strategy.strategy_id
                    )
                  }
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <h4 className="font-semibold text-gray-900">{strategyInfo.name}</h4>
                        <span
                          className={`px-2 py-1 rounded-full text-xs font-medium ${getRiskColor(strategyInfo.risk_level)}`}
                        >
                          {strategyInfo.risk_level.toUpperCase()}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{strategyInfo.description}</p>
                      <div className="flex items-center space-x-4 text-xs text-gray-500">
                        <span>⏱️ {strategyInfo.time_horizon}</span>
                        <span>🎯 {strategyInfo.best_for}</span>
                      </div>
                    </div>

                    <div className="text-right">
                      <div className="text-lg font-bold text-blue-600">
                        {Math.round(strategy.probability * 100)}%
                      </div>
                      <div className="text-xs text-gray-500">Success Probability</div>
                    </div>
                  </div>

                  {/* Expanded Details */}
                  {selectedStrategy === strategy.strategy_id && (
                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <h5 className="font-medium text-gray-900 mb-2">Strategy Details</h5>
                          <div className="space-y-1 text-sm text-gray-600">
                            <div>
                              <strong>Risk Level:</strong> {strategyInfo.risk_level}
                            </div>
                            <div>
                              <strong>Time Horizon:</strong> {strategyInfo.time_horizon}
                            </div>
                            <div>
                              <strong>Best For:</strong> {strategyInfo.best_for}
                            </div>
                          </div>
                        </div>
                        <div>
                          <h5 className="font-medium text-gray-900 mb-2">Performance Metrics</h5>
                          <div className="space-y-1 text-sm text-gray-600">
                            <div>
                              <strong>Confidence:</strong> {Math.round(strategy.confidence * 100)}%
                            </div>
                            <div>
                              <strong>Expected Return:</strong> {strategy.expected_return}%
                            </div>
                            <div>
                              <strong>Probability:</strong> {Math.round(strategy.probability * 100)}
                              %
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Empty State */}
      {!regime && !loading && (
        <div className="text-center py-12">
          <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Market Data Available</h3>
          <p className="text-gray-600 mb-4">
            Unable to analyze market regime for {symbol}. Please try refreshing or check back later.
          </p>
          <button
            onClick={handleRefresh}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      )}
    </div>
  );
};
