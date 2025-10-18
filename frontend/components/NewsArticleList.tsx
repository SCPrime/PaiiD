import React from "react";
import { useIsMobile } from "../hooks/useBreakpoint";

interface NewsArticle {
  title: string;
  summary?: string;
  url: string;
  source: string;
  published_at: string;
  sentiment?: "positive" | "negative" | "neutral";
}

interface NewsArticleListProps {
  symbol: string;
  articles: NewsArticle[];
  loading?: boolean;
  onArticleClick?: (article: NewsArticle) => void;
}

const NewsArticleList: React.FC<NewsArticleListProps> = ({
  symbol,
  articles,
  loading = false,
  onArticleClick,
}) => {
  const isMobile = useIsMobile();

  const theme = {
    bg: "rgba(15, 23, 42, 0.7)",
    bgLight: "rgba(30, 41, 59, 0.8)",
    text: "#e2e8f0",
    textMuted: "#94a3b8",
    primary: "#10b981",
    warning: "#eab308",
    danger: "#ef4444",
    border: "rgba(148, 163, 184, 0.2)",
  };

  const getSentimentColor = (sentiment: string | undefined): string => {
    switch (sentiment) {
      case "positive":
        return theme.primary;
      case "negative":
        return theme.danger;
      case "neutral":
      default:
        return theme.textMuted;
    }
  };

  const getSentimentBadge = (sentiment: string | undefined): string => {
    switch (sentiment) {
      case "positive":
        return "📈 Bullish";
      case "negative":
        return "📉 Bearish";
      case "neutral":
      default:
        return "➖ Neutral";
    }
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (diffInSeconds < 60) return "Just now";
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`;

    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: date.getFullYear() !== now.getFullYear() ? "numeric" : undefined,
    });
  };

  const handleArticleClick = (article: NewsArticle) => {
    if (onArticleClick) {
      onArticleClick(article);
    } else {
      window.open(article.url, "_blank", "noopener,noreferrer");
    }
  };

  return (
    <div
      style={{
        padding: isMobile ? "16px" : "24px",
        background: theme.bg,
        borderRadius: "12px",
        border: `1px solid ${theme.border}`,
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "16px",
        }}
      >
        <h3
          style={{
            fontSize: "18px",
            fontWeight: 600,
            color: theme.text,
            margin: 0,
          }}
        >
          News - {symbol}
        </h3>
        <div
          style={{
            fontSize: "12px",
            color: theme.textMuted,
          }}
        >
          {articles.length} article{articles.length !== 1 ? "s" : ""}
        </div>
      </div>

      {loading ? (
        <div
          style={{
            padding: "40px",
            textAlign: "center",
            color: theme.textMuted,
            fontSize: "14px",
          }}
        >
          Loading news articles...
        </div>
      ) : articles.length > 0 ? (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "12px",
          }}
        >
          {articles.map((article, idx) => (
            <div
              key={idx}
              onClick={() => handleArticleClick(article)}
              style={{
                padding: "16px",
                background: theme.bgLight,
                borderRadius: "8px",
                cursor: "pointer",
                border: `1px solid transparent`,
                transition: "all 0.2s ease",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = theme.primary;
                e.currentTarget.style.background = "rgba(30, 41, 59, 1)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = "transparent";
                e.currentTarget.style.background = theme.bgLight;
              }}
            >
              {/* Title */}
              <div
                style={{
                  fontSize: isMobile ? "14px" : "15px",
                  fontWeight: 600,
                  color: theme.text,
                  marginBottom: "8px",
                  lineHeight: "1.4",
                }}
              >
                {article.title}
              </div>

              {/* Summary (if available) */}
              {article.summary && (
                <div
                  style={{
                    fontSize: "13px",
                    color: theme.textMuted,
                    marginBottom: "8px",
                    lineHeight: "1.5",
                  }}
                >
                  {article.summary.length > 150
                    ? `${article.summary.substring(0, 150)}...`
                    : article.summary}
                </div>
              )}

              {/* Meta Info */}
              <div
                style={{
                  display: "flex",
                  flexWrap: "wrap",
                  alignItems: "center",
                  gap: "12px",
                  fontSize: "12px",
                  color: theme.textMuted,
                }}
              >
                <span style={{ fontWeight: 600 }}>{article.source}</span>
                <span>•</span>
                <span>{formatDate(article.published_at)}</span>
                {article.sentiment && (
                  <>
                    <span>•</span>
                    <span
                      style={{
                        color: getSentimentColor(article.sentiment),
                        fontWeight: 600,
                      }}
                    >
                      {getSentimentBadge(article.sentiment)}
                    </span>
                  </>
                )}
                <span
                  style={{
                    marginLeft: "auto",
                    color: theme.primary,
                    fontSize: "11px",
                    fontWeight: 600,
                  }}
                >
                  Read more →
                </span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div
          style={{
            padding: "40px",
            textAlign: "center",
            color: theme.textMuted,
            fontSize: "14px",
          }}
        >
          <div style={{ fontSize: "32px", marginBottom: "12px" }}>📰</div>
          <div>No news articles available for {symbol}</div>
          <div style={{ fontSize: "12px", marginTop: "8px" }}>News integration coming soon</div>
        </div>
      )}

      <div
        style={{
          marginTop: "16px",
          padding: "12px",
          background: "rgba(16, 185, 129, 0.1)",
          borderRadius: "8px",
          border: `1px solid rgba(16, 185, 129, 0.2)`,
          fontSize: "12px",
          color: theme.textMuted,
          textAlign: "center",
        }}
      >
        💡 News sentiment analysis powered by Tradier + AI
      </div>
    </div>
  );
};

export default NewsArticleList;
