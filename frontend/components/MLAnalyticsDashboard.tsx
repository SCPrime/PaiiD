"use client";

import { useState, useEffect } from "react";
import { Card, Button } from "./ui";
import { theme } from "../styles/theme";
import { showError } from "../lib/toast";
import { BarChart3, TrendingUp, Activity, Zap, Award, RefreshCw } from "lucide-react";
import { useIsMobile } from "../hooks/useBreakpoint";

interface PredictionMetrics {
  model_id: string;
  model_name: string;
  total_predictions: number;
  correct_predictions: number;
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  confidence_avg: number;
  predictions_today: number;
  predictions_this_week: number;
}

interface FeatureImportance {
  feature_name: string;
  importance_score: number;
  rank: number;
}

interface ModelComparison {
  metric: string;
  regime_detector: number;
  strategy_selector: number;
  pattern_detector: number;
}

interface ConfidenceDistribution {
  confidence_range: string;
  count: number;
  percentage: number;
  accuracy_in_range: number;
}

interface AnalyticsData {
  prediction_metrics: PredictionMetrics[];
  feature_importance: {
    [model_id: string]: FeatureImportance[];
  };
  model_comparison: ModelComparison[];
  confidence_distribution: ConfidenceDistribution[];
  timestamp: string;
}

export default function MLAnalyticsDashboard() {
  const isMobile = useIsMobile();
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState<string>("regime_detector");

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    setIsLoading(true);
    try {
      const res = await fetch("/api/proxy/api/ml/analytics");
      if (!res.ok) throw new Error("Failed to load analytics");
      const analyticsData = await res.json();
      setData(analyticsData);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error";
      showError(`Failed to load analytics: ${errorMessage}`);
    } finally {
      setIsLoading(false);
    }
  };

  const getAccuracyColor = (accuracy: number): string => {
    if (accuracy >= 80) return theme.colors.success;
    if (accuracy >= 60) return theme.colors.warning;
    return theme.colors.error;
  };

  const getMetricColor = (value: number, isHigherBetter: boolean = true): string => {
    if (isHigherBetter) {
      if (value >= 0.8) return theme.colors.success;
      if (value >= 0.6) return theme.colors.warning;
      return theme.colors.error;
    }
    return theme.colors.secondary;
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
            textShadow: theme.glow.green,
            marginBottom: theme.spacing.xs,
            display: "flex",
            alignItems: "center",
            gap: theme.spacing.sm,
          }}
        >
          <BarChart3 size={32} color={theme.colors.primary} />
          ML Analytics Dashboard
        </h2>
        <p
          style={{
            margin: 0,
            fontSize: "14px",
            color: theme.colors.textMuted,
          }}
        >
          Real-time ML model performance tracking and insights
        </p>
      </div>

      {/* Refresh Button */}
      <Card glow="green" style={{ marginBottom: theme.spacing.lg }}>
        <Button onClick={loadAnalytics} loading={isLoading} variant="primary">
          <RefreshCw size={18} />
          Refresh Analytics
        </Button>
      </Card>

      {data && (
        <>
          {/* Prediction Metrics Cards */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: isMobile ? "1fr" : "repeat(3, 1fr)",
              gap: theme.spacing.lg,
              marginBottom: theme.spacing.lg,
            }}
          >
            {data.prediction_metrics.map((metrics, idx) => (
              <Card key={idx} glow="cyan">
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "flex-start",
                    marginBottom: theme.spacing.md,
                  }}
                >
                  <h3
                    style={{
                      margin: 0,
                      fontSize: "18px",
                      fontWeight: "700",
                      color: theme.colors.text,
                    }}
                  >
                    {metrics.model_name}
                  </h3>
                  <Award size={24} color={getAccuracyColor(metrics.accuracy)} />
                </div>

                {/* Accuracy Circle */}
                <div
                  style={{
                    display: "flex",
                    justifyContent: "center",
                    marginBottom: theme.spacing.lg,
                  }}
                >
                  <div
                    style={{
                      width: "120px",
                      height: "120px",
                      borderRadius: "50%",
                      background: `conic-gradient(${getAccuracyColor(metrics.accuracy)} ${metrics.accuracy * 3.6}deg, rgba(15, 23, 42, 0.5) 0deg)`,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      position: "relative",
                    }}
                  >
                    <div
                      style={{
                        width: "100px",
                        height: "100px",
                        borderRadius: "50%",
                        background: theme.colors.background,
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        justifyContent: "center",
                      }}
                    >
                      <div
                        style={{
                          fontSize: "32px",
                          fontWeight: "700",
                          color: getAccuracyColor(metrics.accuracy),
                        }}
                      >
                        {metrics.accuracy.toFixed(1)}%
                      </div>
                      <div
                        style={{
                          fontSize: "11px",
                          color: theme.colors.textMuted,
                        }}
                      >
                        Accuracy
                      </div>
                    </div>
                  </div>
                </div>

                {/* Metrics Grid */}
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(2, 1fr)",
                    gap: theme.spacing.sm,
                    marginBottom: theme.spacing.md,
                  }}
                >
                  <div
                    style={{
                      padding: theme.spacing.sm,
                      background: "rgba(6, 182, 212, 0.1)",
                      borderRadius: theme.borderRadius.sm,
                    }}
                  >
                    <div style={{ fontSize: "11px", color: theme.colors.textMuted }}>PRECISION</div>
                    <div
                      style={{
                        fontSize: "20px",
                        fontWeight: "700",
                        color: getMetricColor(metrics.precision),
                      }}
                    >
                      {(metrics.precision * 100).toFixed(1)}%
                    </div>
                  </div>

                  <div
                    style={{
                      padding: theme.spacing.sm,
                      background: "rgba(139, 92, 246, 0.1)",
                      borderRadius: theme.borderRadius.sm,
                    }}
                  >
                    <div style={{ fontSize: "11px", color: theme.colors.textMuted }}>RECALL</div>
                    <div
                      style={{
                        fontSize: "20px",
                        fontWeight: "700",
                        color: getMetricColor(metrics.recall),
                      }}
                    >
                      {(metrics.recall * 100).toFixed(1)}%
                    </div>
                  </div>

                  <div
                    style={{
                      padding: theme.spacing.sm,
                      background: "rgba(16, 185, 129, 0.1)",
                      borderRadius: theme.borderRadius.sm,
                    }}
                  >
                    <div style={{ fontSize: "11px", color: theme.colors.textMuted }}>F1 SCORE</div>
                    <div
                      style={{
                        fontSize: "20px",
                        fontWeight: "700",
                        color: getMetricColor(metrics.f1_score),
                      }}
                    >
                      {(metrics.f1_score * 100).toFixed(1)}%
                    </div>
                  </div>

                  <div
                    style={{
                      padding: theme.spacing.sm,
                      background: "rgba(251, 191, 36, 0.1)",
                      borderRadius: theme.borderRadius.sm,
                    }}
                  >
                    <div style={{ fontSize: "11px", color: theme.colors.textMuted }}>AVG CONFIDENCE</div>
                    <div
                      style={{
                        fontSize: "20px",
                        fontWeight: "700",
                        color: theme.colors.warning,
                      }}
                    >
                      {(metrics.confidence_avg * 100).toFixed(1)}%
                    </div>
                  </div>
                </div>

                {/* Stats */}
                <div
                  style={{
                    padding: theme.spacing.sm,
                    background: "rgba(15, 23, 42, 0.5)",
                    borderRadius: theme.borderRadius.sm,
                    fontSize: "12px",
                    color: theme.colors.textMuted,
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px" }}>
                    <span>Total Predictions:</span>
                    <span style={{ color: theme.colors.text, fontWeight: "600" }}>
                      {metrics.total_predictions.toLocaleString()}
                    </span>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px" }}>
                    <span>Today:</span>
                    <span style={{ color: theme.colors.secondary, fontWeight: "600" }}>
                      {metrics.predictions_today}
                    </span>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <span>This Week:</span>
                    <span style={{ color: theme.colors.accent, fontWeight: "600" }}>
                      {metrics.predictions_this_week}
                    </span>
                  </div>
                </div>
              </Card>
            ))}
          </div>

          {/* Feature Importance */}
          <Card glow="purple" style={{ marginBottom: theme.spacing.lg }}>
            <h3
              style={{
                fontSize: isMobile ? "18px" : "20px",
                fontWeight: "600",
                color: theme.colors.text,
                marginBottom: theme.spacing.lg,
                display: "flex",
                alignItems: "center",
                gap: theme.spacing.sm,
              }}
            >
              <Zap size={24} color={theme.colors.accent} />
              Feature Importance
            </h3>

            {/* Model Selector */}
            <div
              style={{
                display: "flex",
                gap: theme.spacing.xs,
                marginBottom: theme.spacing.lg,
                flexWrap: "wrap",
              }}
            >
              {Object.keys(data.feature_importance).map((modelId) => (
                <button
                  key={modelId}
                  onClick={() => setSelectedModel(modelId)}
                  style={{
                    padding: "8px 16px",
                    background:
                      selectedModel === modelId
                        ? `linear-gradient(135deg, ${theme.colors.accent}, ${theme.colors.secondary})`
                        : "rgba(15, 23, 42, 0.5)",
                    border: `1px solid ${selectedModel === modelId ? theme.colors.accent : theme.colors.border}`,
                    borderRadius: theme.borderRadius.md,
                    color: theme.colors.text,
                    fontSize: "13px",
                    fontWeight: selectedModel === modelId ? "700" : "400",
                    cursor: "pointer",
                    textTransform: "capitalize",
                    transition: "all 0.2s",
                  }}
                >
                  {modelId.replace(/_/g, " ")}
                </button>
              ))}
            </div>

            {/* Feature Bars */}
            <div style={{ display: "grid", gap: theme.spacing.md }}>
              {data.feature_importance[selectedModel]?.slice(0, 10).map((feature, idx) => (
                <div key={idx}>
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      marginBottom: theme.spacing.xs,
                      fontSize: "13px",
                    }}
                  >
                    <span style={{ color: theme.colors.text, fontWeight: "600" }}>
                      #{feature.rank} {feature.feature_name.replace(/_/g, " ")}
                    </span>
                    <span style={{ color: theme.colors.accent, fontWeight: "700" }}>
                      {(feature.importance_score * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div
                    style={{
                      width: "100%",
                      height: "12px",
                      background: "rgba(15, 23, 42, 0.8)",
                      borderRadius: "6px",
                      overflow: "hidden",
                    }}
                  >
                    <div
                      style={{
                        width: `${feature.importance_score * 100}%`,
                        height: "100%",
                        background: `linear-gradient(90deg, ${theme.colors.accent}, ${theme.colors.secondary})`,
                        borderRadius: "6px",
                        transition: "width 0.5s ease",
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </Card>

          {/* Model Comparison */}
          <Card glow="green" style={{ marginBottom: theme.spacing.lg }}>
            <h3
              style={{
                fontSize: isMobile ? "18px" : "20px",
                fontWeight: "600",
                color: theme.colors.text,
                marginBottom: theme.spacing.lg,
                display: "flex",
                alignItems: "center",
                gap: theme.spacing.sm,
              }}
            >
              <TrendingUp size={24} color={theme.colors.success} />
              Model Performance Comparison
            </h3>

            <div style={{ overflowX: "auto" }}>
              <table
                style={{
                  width: "100%",
                  borderCollapse: "collapse",
                  fontSize: isMobile ? "12px" : "14px",
                }}
              >
                <thead>
                  <tr
                    style={{
                      borderBottom: `2px solid ${theme.colors.border}`,
                    }}
                  >
                    <th
                      style={{
                        padding: theme.spacing.sm,
                        textAlign: "left",
                        color: theme.colors.textMuted,
                        fontWeight: "600",
                        textTransform: "uppercase",
                        fontSize: "11px",
                      }}
                    >
                      Metric
                    </th>
                    <th
                      style={{
                        padding: theme.spacing.sm,
                        textAlign: "center",
                        color: theme.colors.textMuted,
                        fontWeight: "600",
                        textTransform: "uppercase",
                        fontSize: "11px",
                      }}
                    >
                      Regime Detector
                    </th>
                    <th
                      style={{
                        padding: theme.spacing.sm,
                        textAlign: "center",
                        color: theme.colors.textMuted,
                        fontWeight: "600",
                        textTransform: "uppercase",
                        fontSize: "11px",
                      }}
                    >
                      Strategy Selector
                    </th>
                    <th
                      style={{
                        padding: theme.spacing.sm,
                        textAlign: "center",
                        color: theme.colors.textMuted,
                        fontWeight: "600",
                        textTransform: "uppercase",
                        fontSize: "11px",
                      }}
                    >
                      Pattern Detector
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {data.model_comparison.map((row, idx) => {
                    const values = [row.regime_detector, row.strategy_selector, row.pattern_detector];
                    const maxValue = Math.max(...values);

                    return (
                      <tr
                        key={idx}
                        style={{
                          borderBottom: `1px solid ${theme.colors.border}`,
                        }}
                      >
                        <td
                          style={{
                            padding: theme.spacing.sm,
                            color: theme.colors.text,
                            fontWeight: "600",
                          }}
                        >
                          {row.metric}
                        </td>
                        <td
                          style={{
                            padding: theme.spacing.sm,
                            textAlign: "center",
                            color: row.regime_detector === maxValue ? theme.colors.success : theme.colors.text,
                            fontWeight: row.regime_detector === maxValue ? "700" : "400",
                          }}
                        >
                          {row.regime_detector.toFixed(2)}
                          {row.regime_detector === maxValue && " 🏆"}
                        </td>
                        <td
                          style={{
                            padding: theme.spacing.sm,
                            textAlign: "center",
                            color: row.strategy_selector === maxValue ? theme.colors.success : theme.colors.text,
                            fontWeight: row.strategy_selector === maxValue ? "700" : "400",
                          }}
                        >
                          {row.strategy_selector.toFixed(2)}
                          {row.strategy_selector === maxValue && " 🏆"}
                        </td>
                        <td
                          style={{
                            padding: theme.spacing.sm,
                            textAlign: "center",
                            color: row.pattern_detector === maxValue ? theme.colors.success : theme.colors.text,
                            fontWeight: row.pattern_detector === maxValue ? "700" : "400",
                          }}
                        >
                          {row.pattern_detector.toFixed(2)}
                          {row.pattern_detector === maxValue && " 🏆"}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </Card>

          {/* Confidence Distribution */}
          <Card glow="cyan">
            <h3
              style={{
                fontSize: isMobile ? "18px" : "20px",
                fontWeight: "600",
                color: theme.colors.text,
                marginBottom: theme.spacing.lg,
                display: "flex",
                alignItems: "center",
                gap: theme.spacing.sm,
              }}
            >
              <Activity size={24} color={theme.colors.secondary} />
              Confidence Distribution
            </h3>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: isMobile ? "1fr" : "repeat(2, 1fr)",
                gap: theme.spacing.lg,
              }}
            >
              {data.confidence_distribution.map((dist, idx) => (
                <div
                  key={idx}
                  style={{
                    padding: theme.spacing.md,
                    background: "rgba(15, 23, 42, 0.5)",
                    border: `1px solid ${theme.colors.border}`,
                    borderRadius: theme.borderRadius.md,
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      marginBottom: theme.spacing.sm,
                    }}
                  >
                    <span
                      style={{
                        fontSize: "16px",
                        fontWeight: "700",
                        color: theme.colors.text,
                      }}
                    >
                      {dist.confidence_range}
                    </span>
                    <span
                      style={{
                        fontSize: "14px",
                        fontWeight: "600",
                        color: theme.colors.secondary,
                      }}
                    >
                      {dist.count.toLocaleString()} predictions
                    </span>
                  </div>

                  <div
                    style={{
                      display: "grid",
                      gridTemplateColumns: "repeat(2, 1fr)",
                      gap: theme.spacing.sm,
                    }}
                  >
                    <div>
                      <div style={{ fontSize: "11px", color: theme.colors.textMuted }}>
                        PERCENTAGE
                      </div>
                      <div
                        style={{
                          fontSize: "24px",
                          fontWeight: "700",
                          color: theme.colors.accent,
                        }}
                      >
                        {dist.percentage.toFixed(1)}%
                      </div>
                    </div>
                    <div>
                      <div style={{ fontSize: "11px", color: theme.colors.textMuted }}>
                        ACCURACY IN RANGE
                      </div>
                      <div
                        style={{
                          fontSize: "24px",
                          fontWeight: "700",
                          color: getAccuracyColor(dist.accuracy_in_range),
                        }}
                      >
                        {dist.accuracy_in_range.toFixed(1)}%
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </>
      )}
    </div>
  );
}
