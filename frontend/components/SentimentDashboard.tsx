"use client";

import { useState, useEffect } from "react";
import { Card, Button } from "./ui";
import { theme } from "../styles/theme";
import { showError, showSuccess } from "../lib/toast";
import { Newspaper, TrendingUp, TrendingDown, Minus, RefreshCw, Sparkles } from "lucide-react";
import { useIsMobile } from "../hooks/useBreakpoint";

interface NewsSentiment {
  article_id: string;
  title: string;
  source: string;
  published_at: string;
  url: string;
  sentiment: "bullish" | "bearish" | "neutral";
  sentiment_score: number;
  confidence: number;
  key_topics: string[];
  impact_score: number;
}

interface SentimentAnalysis {
  symbol: string;
  overall_sentiment: "bullish" | "bearish" | "neutral";
  sentiment_score: number;
  confidence: number;
  bullish_count: number;
  bearish_count: number;
  neutral_count: number;
  total_articles: number;
  avg_impact: number;
  top_topics: string[];
  articles: NewsSentiment[];
  timestamp: string;
}

export default function SentimentDashboard() {
  const isMobile = useIsMobile();
  const [symbol, setSymbol] = useState("SPY");
  const [lookbackHours, setLookbackHours] = useState(24);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<SentimentAnalysis | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(false);

  // Auto-refresh every 5 minutes if enabled
  useEffect(() => {
    if (!autoRefresh || !result) return;

    const interval = setInterval(() => {
      analyzeSentiment();
    }, 5 * 60 * 1000); // 5 minutes

    return () => clearInterval(interval);
  }, [autoRefresh, result]);

  const analyzeSentiment = async () => {
    if (!symbol.trim()) {
      showError("Please enter a symbol");
      return;
    }

    setIsLoading(true);

    try {
      const res = await fetch(
        `/api/proxy/api/sentiment/analyze?symbol=${symbol.toUpperCase()}&lookback_hours=${lookbackHours}`
      );

      if (!res.ok) {
        throw new Error(`Sentiment analysis failed: ${res.statusText}`);
      }

      const data = await res.json();
      setResult(data);
      showSuccess(`Analyzed ${data.total_articles} articles for ${data.symbol}`);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error";
      showError(`Analysis failed: ${errorMessage}`);
    } finally {
      setIsLoading(false);
    }
  };

  const getSentimentColor = (sentiment: string): string => {
    switch (sentiment) {
      case "bullish":
        return theme.colors.success;
      case "bearish":
        return theme.colors.error;
      case "neutral":
        return theme.colors.textMuted;
      default:
        return theme.colors.text;
    }
  };

  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment) {
      case "bullish":
        return <TrendingUp size={24} color={theme.colors.success} />;
      case "bearish":
        return <TrendingDown size={24} color={theme.colors.error} />;
      case "neutral":
        return <Minus size={24} color={theme.colors.textMuted} />;
      default:
        return <Minus size={24} />;
    }
  };

  const getSentimentEmoji = (sentiment: string): string => {
    switch (sentiment) {
      case "bullish":
        return "🚀";
      case "bearish":
        return "📉";
      case "neutral":
        return "➡️";
      default:
        return "❓";
    }
  };

  const formatTimestamp = (timestamp: string): string => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffMins = Math.floor(diffMs / (1000 * 60));

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <div style={{ padding: isMobile ? theme.spacing.md : theme.spacing.lg }}>
      {/* Header */}
      <div style={{ marginBottom: theme.spacing.lg }}>
        <h2
          style={{
            margin: 0,
            fontSize: isMobile ? "24px" : "32px",
            fontWeight: "700",
            color: theme.colors.text,
            textShadow: theme.glow.cyan,
            marginBottom: theme.spacing.xs,
            display: "flex",
            alignItems: "center",
            gap: theme.spacing.sm,
          }}
        >
          <Newspaper size={32} color={theme.colors.secondary} />
          News Sentiment Dashboard
        </h2>
        <p
          style={{
            margin: 0,
            fontSize: "14px",
            color: theme.colors.textMuted,
          }}
        >
          Real-time AI-powered news sentiment analysis
        </p>
      </div>

      {/* Configuration Card */}
      <Card glow="cyan" style={{ marginBottom: theme.spacing.lg }}>
        <h3
          style={{
            fontSize: isMobile ? "18px" : "20px",
            fontWeight: "600",
            color: theme.colors.text,
            marginBottom: theme.spacing.lg,
          }}
        >
          Analysis Configuration
        </h3>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: isMobile ? "1fr" : "repeat(2, 1fr)",
            gap: theme.spacing.md,
            marginBottom: theme.spacing.lg,
          }}
        >
          {/* Symbol Input */}
          <div>
            <label
              style={{
                display: "block",
                fontSize: "12px",
                color: theme.colors.textMuted,
                marginBottom: theme.spacing.xs,
                textTransform: "uppercase",
                letterSpacing: "0.5px",
              }}
            >
              Symbol
            </label>
            <input
              type="text"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value.toUpperCase())}
              disabled={isLoading}
              placeholder="SPY"
              style={{
                width: "100%",
                padding: "12px",
                background: "rgba(15, 23, 42, 0.5)",
                border: `1px solid ${theme.colors.border}`,
                borderRadius: theme.borderRadius.md,
                color: theme.colors.text,
                fontSize: "14px",
              }}
            />
          </div>

          {/* Lookback Hours */}
          <div>
            <label
              style={{
                display: "block",
                fontSize: "12px",
                color: theme.colors.textMuted,
                marginBottom: theme.spacing.xs,
                textTransform: "uppercase",
                letterSpacing: "0.5px",
              }}
            >
              Lookback Period: {lookbackHours} hours
            </label>
            <input
              type="range"
              min="6"
              max="168"
              step="6"
              value={lookbackHours}
              onChange={(e) => setLookbackHours(Number(e.target.value))}
              disabled={isLoading}
              style={{
                width: "100%",
                height: "8px",
                borderRadius: "4px",
                outline: "none",
                opacity: isLoading ? 0.5 : 1,
              }}
            />
            <div
              style={{
                fontSize: "11px",
                color: theme.colors.textMuted,
                marginTop: theme.spacing.xs,
              }}
            >
              6 hours - 7 days
            </div>
          </div>
        </div>

        <div
          style={{
            display: "flex",
            gap: theme.spacing.sm,
            alignItems: "center",
            flexWrap: "wrap",
          }}
        >
          <Button
            onClick={analyzeSentiment}
            loading={isLoading}
            disabled={isLoading || !symbol.trim()}
            variant="primary"
            style={{ flex: isMobile ? "1" : "0" }}
          >
            {isLoading ? "Analyzing..." : "Analyze Sentiment"}
          </Button>

          {result && (
            <label
              style={{
                display: "flex",
                alignItems: "center",
                gap: theme.spacing.xs,
                fontSize: "14px",
                color: theme.colors.text,
                cursor: "pointer",
              }}
            >
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                style={{ cursor: "pointer" }}
              />
              <RefreshCw size={16} />
              Auto-refresh (5min)
            </label>
          )}
        </div>
      </Card>

      {/* Results */}
      {result && (
        <>
          {/* Overall Sentiment Card */}
          <Card glow="purple" style={{ marginBottom: theme.spacing.lg }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                marginBottom: theme.spacing.lg,
              }}
            >
              <h3
                style={{
                  fontSize: isMobile ? "18px" : "20px",
                  fontWeight: "600",
                  color: theme.colors.text,
                  margin: 0,
                }}
              >
                {getSentimentEmoji(result.overall_sentiment)} Market Sentiment - {result.symbol}
              </h3>
              <div
                style={{
                  fontSize: "12px",
                  color: theme.colors.textMuted,
                }}
              >
                {formatTimestamp(result.timestamp)}
              </div>
            </div>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: isMobile ? "1fr" : "repeat(4, 1fr)",
                gap: theme.spacing.md,
                marginBottom: theme.spacing.lg,
              }}
            >
              {/* Overall Sentiment */}
              <div
                style={{
                  padding: theme.spacing.md,
                  background: `rgba(${
                    result.overall_sentiment === "bullish"
                      ? "16, 185, 129"
                      : result.overall_sentiment === "bearish"
                        ? "239, 68, 68"
                        : "148, 163, 184"
                  }, 0.1)`,
                  border: `2px solid ${getSentimentColor(result.overall_sentiment)}`,
                  borderRadius: theme.borderRadius.md,
                  textAlign: "center",
                }}
              >
                <div style={{ marginBottom: theme.spacing.sm }}>
                  {getSentimentIcon(result.overall_sentiment)}
                </div>
                <div
                  style={{
                    fontSize: "24px",
                    fontWeight: "700",
                    color: getSentimentColor(result.overall_sentiment),
                    textTransform: "uppercase",
                  }}
                >
                  {result.overall_sentiment}
                </div>
                <div
                  style={{
                    fontSize: "12px",
                    color: theme.colors.textMuted,
                    marginTop: theme.spacing.xs,
                  }}
                >
                  {(result.confidence * 100).toFixed(0)}% confidence
                </div>
              </div>

              {/* Sentiment Score */}
              <div
                style={{
                  padding: theme.spacing.md,
                  background: "rgba(139, 92, 246, 0.1)",
                  border: `1px solid ${theme.colors.accent}`,
                  borderRadius: theme.borderRadius.md,
                }}
              >
                <div
                  style={{
                    fontSize: "12px",
                    color: theme.colors.textMuted,
                    marginBottom: theme.spacing.xs,
                  }}
                >
                  SENTIMENT SCORE
                </div>
                <div
                  style={{
                    fontSize: "32px",
                    fontWeight: "700",
                    color: theme.colors.accent,
                  }}
                >
                  {result.sentiment_score >= 0 ? "+" : ""}
                  {result.sentiment_score.toFixed(2)}
                </div>
                <div
                  style={{
                    fontSize: "11px",
                    color: theme.colors.textMuted,
                  }}
                >
                  -1.0 (bearish) to +1.0 (bullish)
                </div>
              </div>

              {/* Article Breakdown */}
              <div
                style={{
                  padding: theme.spacing.md,
                  background: "rgba(6, 182, 212, 0.1)",
                  border: `1px solid ${theme.colors.secondary}`,
                  borderRadius: theme.borderRadius.md,
                }}
              >
                <div
                  style={{
                    fontSize: "12px",
                    color: theme.colors.textMuted,
                    marginBottom: theme.spacing.xs,
                  }}
                >
                  ARTICLES ANALYZED
                </div>
                <div
                  style={{
                    fontSize: "32px",
                    fontWeight: "700",
                    color: theme.colors.secondary,
                  }}
                >
                  {result.total_articles}
                </div>
                <div
                  style={{
                    fontSize: "11px",
                    color: theme.colors.textMuted,
                  }}
                >
                  <span style={{ color: theme.colors.success }}>{result.bullish_count} 🚀</span> /{" "}
                  <span style={{ color: theme.colors.error }}>{result.bearish_count} 📉</span> /{" "}
                  <span>{result.neutral_count} ➡️</span>
                </div>
              </div>

              {/* Impact Score */}
              <div
                style={{
                  padding: theme.spacing.md,
                  background: "rgba(16, 185, 129, 0.1)",
                  border: `1px solid ${theme.colors.success}`,
                  borderRadius: theme.borderRadius.md,
                }}
              >
                <div
                  style={{
                    fontSize: "12px",
                    color: theme.colors.textMuted,
                    marginBottom: theme.spacing.xs,
                  }}
                >
                  AVG IMPACT
                </div>
                <div
                  style={{
                    fontSize: "32px",
                    fontWeight: "700",
                    color: theme.colors.success,
                  }}
                >
                  {(result.avg_impact * 100).toFixed(0)}%
                </div>
                <div
                  style={{
                    fontSize: "11px",
                    color: theme.colors.textMuted,
                  }}
                >
                  Market moving potential
                </div>
              </div>
            </div>

            {/* Top Topics */}
            {result.top_topics.length > 0 && (
              <div>
                <div
                  style={{
                    fontSize: "12px",
                    color: theme.colors.textMuted,
                    marginBottom: theme.spacing.sm,
                    textTransform: "uppercase",
                    letterSpacing: "0.5px",
                  }}
                >
                  <Sparkles size={14} style={{ display: "inline", marginRight: "4px" }} />
                  Trending Topics:
                </div>
                <div
                  style={{
                    display: "flex",
                    gap: theme.spacing.xs,
                    flexWrap: "wrap",
                  }}
                >
                  {result.top_topics.map((topic, idx) => (
                    <div
                      key={idx}
                      style={{
                        padding: "6px 12px",
                        background: "rgba(139, 92, 246, 0.2)",
                        border: `1px solid ${theme.colors.accent}`,
                        borderRadius: theme.borderRadius.sm,
                        fontSize: "13px",
                        color: theme.colors.accent,
                        fontWeight: "600",
                      }}
                    >
                      {topic}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </Card>

          {/* News Articles */}
          <Card glow="green" style={{ marginBottom: theme.spacing.lg }}>
            <h3
              style={{
                fontSize: isMobile ? "18px" : "20px",
                fontWeight: "600",
                color: theme.colors.text,
                marginBottom: theme.spacing.lg,
              }}
            >
              📰 Recent News Articles
            </h3>

            {result.articles.length === 0 ? (
              <div
                style={{
                  textAlign: "center",
                  padding: theme.spacing.xl,
                  color: theme.colors.textMuted,
                }}
              >
                No articles found for this symbol in the selected time period.
              </div>
            ) : (
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "1fr",
                  gap: theme.spacing.md,
                }}
              >
                {result.articles.slice(0, 10).map((article, idx) => (
                  <a
                    key={idx}
                    href={article.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      padding: theme.spacing.md,
                      background: "rgba(15, 23, 42, 0.5)",
                      border: `1px solid ${getSentimentColor(article.sentiment)}`,
                      borderRadius: theme.borderRadius.md,
                      textDecoration: "none",
                      display: "block",
                      transition: "all 0.2s",
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background = "rgba(15, 23, 42, 0.8)";
                      e.currentTarget.style.transform = "translateY(-2px)";
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = "rgba(15, 23, 42, 0.5)";
                      e.currentTarget.style.transform = "translateY(0)";
                    }}
                  >
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "flex-start",
                        marginBottom: theme.spacing.sm,
                      }}
                    >
                      <div
                        style={{
                          flex: 1,
                          fontSize: "16px",
                          fontWeight: "600",
                          color: theme.colors.text,
                          lineHeight: "1.4",
                        }}
                      >
                        {article.title}
                      </div>
                      <div
                        style={{
                          marginLeft: theme.spacing.sm,
                          padding: "4px 12px",
                          background: `rgba(${
                            article.sentiment === "bullish"
                              ? "16, 185, 129"
                              : article.sentiment === "bearish"
                                ? "239, 68, 68"
                                : "148, 163, 184"
                          }, 0.2)`,
                          border: `1px solid ${getSentimentColor(article.sentiment)}`,
                          borderRadius: theme.borderRadius.sm,
                          fontSize: "12px",
                          color: getSentimentColor(article.sentiment),
                          fontWeight: "700",
                          textTransform: "uppercase",
                          whiteSpace: "nowrap",
                        }}
                      >
                        {article.sentiment}
                      </div>
                    </div>

                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        fontSize: "12px",
                        color: theme.colors.textMuted,
                      }}
                    >
                      <div>
                        {article.source} • {formatTimestamp(article.published_at)}
                      </div>
                      <div>
                        Confidence: {(article.confidence * 100).toFixed(0)}% | Impact:{" "}
                        {(article.impact_score * 100).toFixed(0)}%
                      </div>
                    </div>

                    {article.key_topics.length > 0 && (
                      <div
                        style={{
                          marginTop: theme.spacing.sm,
                          display: "flex",
                          gap: theme.spacing.xs,
                          flexWrap: "wrap",
                        }}
                      >
                        {article.key_topics.slice(0, 3).map((topic, topicIdx) => (
                          <span
                            key={topicIdx}
                            style={{
                              padding: "2px 8px",
                              background: "rgba(139, 92, 246, 0.15)",
                              border: `1px solid ${theme.colors.accent}`,
                              borderRadius: theme.borderRadius.xs,
                              fontSize: "11px",
                              color: theme.colors.accent,
                            }}
                          >
                            {topic}
                          </span>
                        ))}
                      </div>
                    )}
                  </a>
                ))}
              </div>
            )}
          </Card>
        </>
      )}
    </div>
  );
}
