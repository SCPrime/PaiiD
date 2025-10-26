import React, { useEffect, useState } from "react";
import { useWebSocket } from "../hooks/useWebSocket";
import { logger } from "../lib/logger";
import AnimatedCounter from "./ui/AnimatedCounter";
import EnhancedCard from "./ui/EnhancedCard";
import StatusIndicator from "./ui/StatusIndicator";

interface SentimentDashboardProps {
  userId: string;
  className?: string;
  symbols?: string[];
  autoRefresh?: boolean;
  refreshInterval?: number;
}

interface SentimentData {
  symbols: string[];
  overall_sentiment: string;
  combined_score: number;
  news_sentiment: {
    sentiment_score: number;
    confidence: number;
    articles_analyzed: number;
  };
  social_sentiment: {
    sentiment_score: number;
    confidence: number;
    posts_analyzed: number;
  };
  timestamp: string;
}

const SentimentDashboard: React.FC<SentimentDashboardProps> = ({
  userId,
  className,
  symbols = ["AAPL", "MSFT", "GOOGL", "TSLA"],
  autoRefresh = true,
  refreshInterval = 300000, // 5 minutes
}) => {
  const [sentimentData, setSentimentData] = useState<SentimentData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const { isConnected } = useWebSocket({
    url: process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws",
    userId,
    autoConnect: true,
  });

  const fetchSentimentData = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/ai/sentiment/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          symbols: symbols,
          days_back: 7,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setSentimentData(data);
        setLastUpdated(new Date());
      } else {
        throw new Error("Failed to fetch sentiment data");
      }
    } catch (err) {
      logger.error("Error fetching sentiment data", err);
      setError("Failed to load sentiment data");
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch sentiment data on mount
  useEffect(() => {
    fetchSentimentData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [symbols.join(",")]);

  // Auto-refresh
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(fetchSentimentData, refreshInterval);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [autoRefresh, refreshInterval, symbols.join(",")]);

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment.toLowerCase()) {
      case "bullish":
        return "text-green-400";
      case "bearish":
        return "text-red-400";
      case "neutral":
        return "text-yellow-400";
      default:
        return "text-slate-400";
    }
  };

  const getScoreColor = (score: number) => {
    if (score > 20) return "positive";
    if (score < -20) return "negative";
    return "neutral";
  };

  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment.toLowerCase()) {
      case "bullish":
        return "📈";
      case "bearish":
        return "📉";
      case "neutral":
        return "➡️";
      default:
        return "❓";
    }
  };

  if (error) {
    return (
      <EnhancedCard variant="default" className={className}>
        <div className="text-center text-red-400">
          <StatusIndicator status="error" size="sm" />
          <p className="mt-2">Error: {error}</p>
          <button
            onClick={fetchSentimentData}
            className="mt-4 bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Retry
          </button>
        </div>
      </EnhancedCard>
    );
  }

  if (isLoading && !sentimentData) {
    return (
      <EnhancedCard variant="default" className={className}>
        <div className="text-center">
          <StatusIndicator status="loading" size="sm" />
          <p className="mt-2 text-slate-400">Loading sentiment analysis...</p>
        </div>
      </EnhancedCard>
    );
  }

  if (!sentimentData) {
    return (
      <EnhancedCard variant="default" className={className}>
        <div className="text-center text-slate-400">
          <StatusIndicator status="offline" size="sm" />
          <p className="mt-2">No sentiment data available</p>
        </div>
      </EnhancedCard>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h3 className="text-white font-bold text-xl">Market Sentiment Analysis</h3>
          <StatusIndicator status={isConnected ? "online" : "offline"} size="sm" />
        </div>

        <div className="flex items-center gap-4">
          {lastUpdated && (
            <span className="text-xs text-slate-400">
              Updated: {lastUpdated.toLocaleTimeString()}
            </span>
          )}
          <button
            onClick={fetchSentimentData}
            disabled={isLoading}
            className="bg-blue-500 hover:bg-blue-600 disabled:bg-slate-600 text-white px-3 py-1 rounded-lg text-sm transition-colors"
          >
            {isLoading ? "..." : "Refresh"}
          </button>
        </div>
      </div>

      {/* Overall Sentiment */}
      <EnhancedCard variant="gradient" size="lg" className="text-center">
        <div className="space-y-4">
          <div className="flex items-center justify-center gap-3">
            <span className="text-4xl">{getSentimentIcon(sentimentData.overall_sentiment)}</span>
            <h4 className="text-white font-bold text-2xl">Overall Sentiment</h4>
          </div>

          <div className="space-y-2">
            <p
              className={`text-3xl font-bold ${getSentimentColor(sentimentData.overall_sentiment)}`}
            >
              {sentimentData.overall_sentiment.toUpperCase()}
            </p>

            <AnimatedCounter
              value={sentimentData.combined_score}
              prefix={sentimentData.combined_score >= 0 ? "+" : ""}
              decimals={1}
              color={getScoreColor(sentimentData.combined_score)}
              className="text-2xl font-semibold"
            />
          </div>
        </div>
      </EnhancedCard>

      {/* Sentiment Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* News Sentiment */}
        <EnhancedCard variant="glass" size="md">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h5 className="text-white font-semibold text-lg">News Sentiment</h5>
              <StatusIndicator status="online" size="sm" />
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Sentiment Score</span>
                <AnimatedCounter
                  value={sentimentData.news_sentiment.sentiment_score}
                  prefix={sentimentData.news_sentiment.sentiment_score >= 0 ? "+" : ""}
                  decimals={1}
                  color={getScoreColor(sentimentData.news_sentiment.sentiment_score)}
                  className="text-lg font-semibold"
                />
              </div>

              <div className="flex items-center justify-between">
                <span className="text-slate-400">Confidence</span>
                <span className="text-white font-semibold">
                  {sentimentData.news_sentiment.confidence}%
                </span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-slate-400">Articles Analyzed</span>
                <span className="text-white font-semibold">
                  {sentimentData.news_sentiment.articles_analyzed}
                </span>
              </div>
            </div>
          </div>
        </EnhancedCard>

        {/* Social Sentiment */}
        <EnhancedCard variant="glass" size="md">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h5 className="text-white font-semibold text-lg">Social Sentiment</h5>
              <StatusIndicator status="online" size="sm" />
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Sentiment Score</span>
                <AnimatedCounter
                  value={sentimentData.social_sentiment.sentiment_score}
                  prefix={sentimentData.social_sentiment.sentiment_score >= 0 ? "+" : ""}
                  decimals={1}
                  color={getScoreColor(sentimentData.social_sentiment.sentiment_score)}
                  className="text-lg font-semibold"
                />
              </div>

              <div className="flex items-center justify-between">
                <span className="text-slate-400">Confidence</span>
                <span className="text-white font-semibold">
                  {sentimentData.social_sentiment.confidence}%
                </span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-slate-400">Posts Analyzed</span>
                <span className="text-white font-semibold">
                  {sentimentData.social_sentiment.posts_analyzed}
                </span>
              </div>
            </div>
          </div>
        </EnhancedCard>
      </div>

      {/* Symbols Analyzed */}
      <EnhancedCard variant="default" size="sm">
        <div className="flex items-center justify-between">
          <span className="text-slate-400">Symbols Analyzed</span>
          <div className="flex items-center gap-2">
            {sentimentData.symbols.map((symbol, _index) => (
              <span
                key={symbol}
                className="bg-slate-700 text-white px-2 py-1 rounded text-sm font-mono"
              >
                {symbol}
              </span>
            ))}
          </div>
        </div>
      </EnhancedCard>

      {/* Loading indicator */}
      {isLoading && (
        <div className="text-center">
          <StatusIndicator status="loading" size="sm" />
          <p className="mt-2 text-slate-400">Updating sentiment analysis...</p>
        </div>
      )}
    </div>
  );
};

export default SentimentDashboard;
