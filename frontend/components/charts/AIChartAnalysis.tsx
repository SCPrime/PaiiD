import React, { useEffect, useState } from "react";
import { useWebSocket } from "../../hooks/useWebSocket";
import AnimatedCounter from "../ui/AnimatedCounter";
import EnhancedCard from "../ui/EnhancedCard";
import StatusIndicator from "../ui/StatusIndicator";

interface AIChartAnalysisProps {
  symbol: string;
  userId: string;
  className?: string;
  showPatterns?: boolean;
  showPredictions?: boolean;
  showAlerts?: boolean;
}

interface ChartPattern {
  name: string;
  confidence: number;
  signal: "bullish" | "bearish" | "neutral";
  description: string;
  priceTarget?: number;
}

interface AIInsight {
  type: "pattern" | "prediction" | "alert";
  title: string;
  description: string;
  confidence: number;
  impact: "high" | "medium" | "low";
  timestamp: string;
}

const AIChartAnalysis: React.FC<AIChartAnalysisProps> = ({
  symbol,
  userId,
  className,
  showPatterns = true,
  showPredictions: _showPredictions = true,
  showAlerts: _showAlerts = true,
}) => {
  const [patterns, setPatterns] = useState<ChartPattern[]>([]);
  const [insights, setInsights] = useState<AIInsight[]>([]);
  const [_isLoading, _setIsLoading] = useState(false);
  const [_error, _setError] = useState<string | null>(null);

  const { isConnected } = useWebSocket({
    url: process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws",
    userId,
    autoConnect: true,
  });

  // Generate mock AI analysis
  useEffect(() => {
    const generateMockPatterns = (): ChartPattern[] => {
      const patternTypes = [
        { name: "Head and Shoulders", signal: "bearish" as const, confidence: 85 },
        { name: "Double Bottom", signal: "bullish" as const, confidence: 78 },
        { name: "Ascending Triangle", signal: "bullish" as const, confidence: 72 },
        { name: "Descending Triangle", signal: "bearish" as const, confidence: 68 },
        { name: "Cup and Handle", signal: "bullish" as const, confidence: 82 },
        { name: "Flag Pattern", signal: "neutral" as const, confidence: 65 },
      ];

      return patternTypes
        .filter(() => Math.random() > 0.5) // Random selection
        .map((pattern) => ({
          ...pattern,
          description: `AI detected ${pattern.name.toLowerCase()} pattern with ${pattern.confidence}% confidence`,
          priceTarget:
            pattern.signal === "bullish" ? 150 + Math.random() * 50 : 100 + Math.random() * 30,
        }));
    };

    const generateMockInsights = (): AIInsight[] => {
      const insightTypes = [
        {
          type: "pattern" as const,
          title: "Support Level Identified",
          description: `Strong support detected at $${(120 + Math.random() * 20).toFixed(2)}`,
          confidence: 85,
          impact: "high" as const,
        },
        {
          type: "prediction" as const,
          title: "Price Target Prediction",
          description: `AI predicts ${symbol} will reach $${(150 + Math.random() * 30).toFixed(2)} within 30 days`,
          confidence: 72,
          impact: "medium" as const,
        },
        {
          type: "alert" as const,
          title: "Volume Spike Alert",
          description: `Unusual volume increase detected - potential breakout signal`,
          confidence: 68,
          impact: "medium" as const,
        },
        {
          type: "pattern" as const,
          title: "Resistance Breakout",
          description: `Price approaching key resistance at $${(140 + Math.random() * 20).toFixed(2)}`,
          confidence: 78,
          impact: "high" as const,
        },
      ];

      return insightTypes
        .filter(() => Math.random() > 0.3) // Random selection
        .map((insight) => ({
          ...insight,
          timestamp: new Date().toISOString(),
        }));
    };

    setPatterns(generateMockPatterns());
    setInsights(generateMockInsights());
  }, [symbol]);

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case "bullish":
        return "text-green-400";
      case "bearish":
        return "text-red-400";
      default:
        return "text-yellow-400";
    }
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case "high":
        return "text-red-400";
      case "medium":
        return "text-yellow-400";
      default:
        return "text-green-400";
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return "text-green-400";
    if (confidence >= 60) return "text-yellow-400";
    return "text-red-400";
  };

  if (error) {
    return (
      <EnhancedCard variant="default" className={className}>
        <div className="text-center text-red-400">
          <StatusIndicator status="error" size="sm" />
          <p className="mt-2">AI Analysis Error: {error}</p>
        </div>
      </EnhancedCard>
    );
  }

  if (isLoading) {
    return (
      <EnhancedCard variant="default" className={className}>
        <div className="text-center">
          <StatusIndicator status="loading" size="sm" />
          <p className="mt-2 text-slate-400">Analyzing chart patterns...</p>
        </div>
      </EnhancedCard>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h3 className="text-white font-bold text-xl">AI Chart Analysis</h3>
          <StatusIndicator status={isConnected ? "online" : "offline"} size="sm" />
        </div>

        <div className="flex items-center gap-2">
          <span className="text-slate-400 text-sm">{symbol}</span>
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
        </div>
      </div>

      {/* AI Insights Summary */}
      <EnhancedCard variant="gradient" size="lg">
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <span className="text-3xl">🤖</span>
            <div>
              <h4 className="text-white font-bold text-lg">AI Market Intelligence</h4>
              <p className="text-slate-300 text-sm">
                Real-time pattern recognition and predictive analysis
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-slate-400 text-sm">Patterns Detected</div>
              <div className="text-white font-bold text-2xl">{patterns.length}</div>
            </div>
            <div className="text-center">
              <div className="text-slate-400 text-sm">Avg Confidence</div>
              <div className="text-white font-bold text-2xl">
                {patterns.length > 0
                  ? Math.round(patterns.reduce((sum, p) => sum + p.confidence, 0) / patterns.length)
                  : 0}
                %
              </div>
            </div>
            <div className="text-center">
              <div className="text-slate-400 text-sm">Active Insights</div>
              <div className="text-white font-bold text-2xl">{insights.length}</div>
            </div>
          </div>
        </div>
      </EnhancedCard>

      {/* Chart Patterns */}
      {showPatterns && patterns.length > 0 && (
        <div className="space-y-4">
          <h4 className="text-white font-semibold text-lg">Detected Patterns</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {patterns.map((pattern, index) => (
              <EnhancedCard key={index} variant="glass" size="md">
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-white">{pattern.name}</span>
                    <div className="flex items-center gap-2">
                      <span className={`text-sm font-semibold ${getSignalColor(pattern.signal)}`}>
                        {pattern.signal.toUpperCase()}
                      </span>
                      <StatusIndicator
                        status={pattern.confidence >= 80 ? "online" : "warning"}
                        size="sm"
                      />
                    </div>
                  </div>

                  <p className="text-slate-300 text-sm">{pattern.description}</p>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400 text-sm">Confidence</span>
                      <span className={`font-semibold ${getConfidenceColor(pattern.confidence)}`}>
                        {pattern.confidence}%
                      </span>
                    </div>

                    {pattern.priceTarget && (
                      <div className="flex items-center justify-between">
                        <span className="text-slate-400 text-sm">Price Target</span>
                        <AnimatedCounter
                          value={pattern.priceTarget}
                          prefix="$"
                          decimals={2}
                          color="neutral"
                          className="font-semibold"
                        />
                      </div>
                    )}
                  </div>
                </div>
              </EnhancedCard>
            ))}
          </div>
        </div>
      )}

      {/* AI Insights */}
      {insights.length > 0 && (
        <div className="space-y-4">
          <h4 className="text-white font-semibold text-lg">AI Insights</h4>
          <div className="space-y-3">
            {insights.map((insight, index) => (
              <EnhancedCard key={index} variant="glass" size="sm">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-white">{insight.title}</span>
                    <div className="flex items-center gap-2">
                      <span
                        className={`text-xs px-2 py-1 rounded ${getImpactColor(insight.impact)} bg-slate-700`}
                      >
                        {insight.impact.toUpperCase()}
                      </span>
                      <span
                        className={`text-sm font-semibold ${getConfidenceColor(insight.confidence)}`}
                      >
                        {insight.confidence}%
                      </span>
                    </div>
                  </div>

                  <p className="text-slate-300 text-sm">{insight.description}</p>

                  <div className="text-xs text-slate-500">
                    {new Date(insight.timestamp).toLocaleString()}
                  </div>
                </div>
              </EnhancedCard>
            ))}
          </div>
        </div>
      )}

      {/* No Data State */}
      {patterns.length === 0 && insights.length === 0 && (
        <EnhancedCard variant="default" className="text-center">
          <div className="text-slate-400">
            <StatusIndicator status="offline" size="sm" />
            <p className="mt-2">No AI analysis available for {symbol}</p>
            <p className="text-sm">AI is analyzing market data...</p>
          </div>
        </EnhancedCard>
      )}
    </div>
  );
};

export default AIChartAnalysis;
