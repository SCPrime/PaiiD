import React, { useEffect, useState } from "react";
import { useWebSocket } from "../hooks/useWebSocket";
import AnimatedCounter from "./ui/AnimatedCounter";
import EnhancedCard from "./ui/EnhancedCard";
import StatusIndicator from "./ui/StatusIndicator";

interface AIRecommendationsProps {
  userId: string;
  className?: string;
  symbols?: string[];
  autoRefresh?: boolean;
  refreshInterval?: number;
}

interface Recommendation {
  symbol: string;
  action: "buy" | "sell" | "hold";
  confidence: number;
  reasoning: string;
  price_target?: number;
  time_horizon: string;
  risk_level: "low" | "medium" | "high";
}

interface RecommendationsData {
  user_id: string;
  buy_recommendations: Recommendation[];
  sell_recommendations: Recommendation[];
  hold_recommendations: Recommendation[];
  overall_risk: string;
  market_outlook: string;
  timestamp: string;
}

const AIRecommendations: React.FC<AIRecommendationsProps> = ({
  userId,
  className,
  symbols = ["AAPL", "MSFT", "GOOGL", "TSLA"],
  autoRefresh = true,
  refreshInterval = 300000, // 5 minutes
}) => {
  const [recommendations, setRecommendations] = useState<RecommendationsData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const { isConnected } = useWebSocket({
    url: process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws",
    userId,
    autoConnect: true,
  });

  const fetchRecommendations = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/ai/recommendations", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: userId,
          symbols: symbols,
          risk_tolerance: "medium",
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setRecommendations(data);
        setLastUpdated(new Date());
      } else {
        throw new Error("Failed to fetch recommendations");
      }
    } catch (err) {
      console.error("Error fetching AI recommendations:", err);
      setError("Failed to load AI recommendations");
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch recommendations on mount
  useEffect(() => {
    fetchRecommendations();
  }, [userId, symbols.join(",")]);

  // Auto-refresh
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(fetchRecommendations, refreshInterval);
    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, userId, symbols.join(",")]);

  const getActionColor = (action: string) => {
    switch (action) {
      case "buy":
        return "text-green-400";
      case "sell":
        return "text-red-400";
      case "hold":
        return "text-yellow-400";
      default:
        return "text-slate-400";
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case "low":
        return "text-green-400";
      case "medium":
        return "text-yellow-400";
      case "high":
        return "text-red-400";
      default:
        return "text-slate-400";
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return "text-green-400";
    if (confidence >= 60) return "text-yellow-400";
    return "text-red-400";
  };

  const RecommendationCard: React.FC<{ recommendation: Recommendation }> = ({ recommendation }) => (
    <EnhancedCard variant="glass" size="sm" className="hover:scale-105 transition-transform">
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="font-mono font-bold text-white text-lg">{recommendation.symbol}</span>
          <div className="flex items-center gap-2">
            <span className={`text-sm font-semibold ${getActionColor(recommendation.action)}`}>
              {recommendation.action.toUpperCase()}
            </span>
            <StatusIndicator
              status={recommendation.confidence >= 70 ? "online" : "warning"}
              size="sm"
            />
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 text-sm">Confidence</span>
            <span
              className={`text-sm font-semibold ${getConfidenceColor(recommendation.confidence)}`}
            >
              {recommendation.confidence}%
            </span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-slate-400 text-sm">Risk Level</span>
            <span className={`text-sm font-semibold ${getRiskColor(recommendation.risk_level)}`}>
              {recommendation.risk_level.toUpperCase()}
            </span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-slate-400 text-sm">Time Horizon</span>
            <span className="text-white text-sm">{recommendation.time_horizon}</span>
          </div>

          {recommendation.price_target && (
            <div className="flex items-center justify-between">
              <span className="text-slate-400 text-sm">Price Target</span>
              <AnimatedCounter
                value={recommendation.price_target}
                prefix="$"
                decimals={2}
                color="neutral"
                className="text-sm font-semibold"
              />
            </div>
          )}
        </div>

        <div className="pt-2 border-t border-slate-700/50">
          <p className="text-slate-300 text-sm leading-relaxed">{recommendation.reasoning}</p>
        </div>
      </div>
    </EnhancedCard>
  );

  if (error) {
    return (
      <EnhancedCard variant="default" className={className}>
        <div className="text-center text-red-400">
          <StatusIndicator status="error" size="sm" />
          <p className="mt-2">Error: {error}</p>
          <button
            onClick={fetchRecommendations}
            className="mt-4 bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Retry
          </button>
        </div>
      </EnhancedCard>
    );
  }

  if (isLoading && !recommendations) {
    return (
      <EnhancedCard variant="default" className={className}>
        <div className="text-center">
          <StatusIndicator status="loading" size="sm" />
          <p className="mt-2 text-slate-400">Loading AI recommendations...</p>
        </div>
      </EnhancedCard>
    );
  }

  if (!recommendations) {
    return (
      <EnhancedCard variant="default" className={className}>
        <div className="text-center text-slate-400">
          <StatusIndicator status="offline" size="sm" />
          <p className="mt-2">No recommendations available</p>
        </div>
      </EnhancedCard>
    );
  }

  const allRecommendations = [
    ...recommendations.buy_recommendations,
    ...recommendations.sell_recommendations,
    ...recommendations.hold_recommendations,
  ];

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h3 className="text-white font-bold text-xl">AI Trading Recommendations</h3>
          <StatusIndicator status={isConnected ? "online" : "offline"} size="sm" />
        </div>

        <div className="flex items-center gap-4">
          {lastUpdated && (
            <span className="text-xs text-slate-400">
              Updated: {lastUpdated.toLocaleTimeString()}
            </span>
          )}
          <button
            onClick={fetchRecommendations}
            disabled={isLoading}
            className="bg-blue-500 hover:bg-blue-600 disabled:bg-slate-600 text-white px-3 py-1 rounded-lg text-sm transition-colors"
          >
            {isLoading ? "..." : "Refresh"}
          </button>
        </div>
      </div>

      {/* Market Outlook */}
      <EnhancedCard variant="gradient" size="md" className="text-center">
        <div className="space-y-2">
          <h4 className="text-white font-semibold">Market Outlook</h4>
          <p className="text-slate-300 capitalize">{recommendations.market_outlook}</p>
          <div className="flex items-center justify-center gap-2">
            <span className="text-slate-400 text-sm">Overall Risk:</span>
            <span className={`text-sm font-semibold ${getRiskColor(recommendations.overall_risk)}`}>
              {recommendations.overall_risk.toUpperCase()}
            </span>
          </div>
        </div>
      </EnhancedCard>

      {/* Recommendations */}
      {allRecommendations.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {allRecommendations.map((recommendation, index) => (
            <RecommendationCard
              key={`${recommendation.symbol}-${index}`}
              recommendation={recommendation}
            />
          ))}
        </div>
      ) : (
        <EnhancedCard variant="default" className="text-center">
          <div className="text-slate-400">
            <StatusIndicator status="offline" size="sm" />
            <p className="mt-2">No recommendations available for the selected symbols</p>
          </div>
        </EnhancedCard>
      )}

      {/* Loading indicator */}
      {isLoading && (
        <div className="text-center">
          <StatusIndicator status="loading" size="sm" />
          <p className="mt-2 text-slate-400">Updating recommendations...</p>
        </div>
      )}
    </div>
  );
};

export default AIRecommendations;
