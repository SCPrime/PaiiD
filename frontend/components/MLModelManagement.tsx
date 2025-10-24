"use client";

import { useState, useEffect } from "react";
import { Card, Button } from "./ui";
import { theme } from "../styles/theme";
import { showError, showSuccess } from "../lib/toast";
import { Database, RefreshCw, CheckCircle, AlertTriangle, TrendingUp, Calendar, Activity } from "lucide-react";
import { useIsMobile } from "../hooks/useBreakpoint";

interface ModelMetrics {
  model_id: string;
  model_type: string;
  version: string;
  accuracy: number;
  samples_trained: number;
  last_trained: string;
  training_duration_seconds: number;
  status: "active" | "training" | "stale" | "error";
  features_count: number;
  hyperparameters: Record<string, any>;
}

interface ModelHealth {
  model_id: string;
  health_score: number;
  prediction_accuracy: number;
  days_since_training: number;
  total_predictions: number;
  requires_retraining: boolean;
  issues: string[];
  recommendations: string[];
}

interface ModelManagementData {
  models: ModelMetrics[];
  health_checks: ModelHealth[];
  next_scheduled_training: string | null;
  auto_retrain_enabled: boolean;
  system_status: "healthy" | "degraded" | "critical";
}

export default function MLModelManagement() {
  const isMobile = useIsMobile();
  const [data, setData] = useState<ModelManagementData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [retrainingModel, setRetrainingModel] = useState<string | null>(null);

  useEffect(() => {
    loadModelStatus();
  }, []);

  const loadModelStatus = async () => {
    setIsLoading(true);
    try {
      const res = await fetch("/api/proxy/api/ml/models/status");
      if (!res.ok) throw new Error("Failed to load model status");
      const modelData = await res.json();
      setData(modelData);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error";
      showError(`Failed to load models: ${errorMessage}`);
    } finally {
      setIsLoading(false);
    }
  };

  const retrainModel = async (modelId: string) => {
    setRetrainingModel(modelId);
    try {
      const res = await fetch(`/api/proxy/api/ml/models/${modelId}/retrain`, {
        method: "POST",
      });
      if (!res.ok) throw new Error("Retraining failed");
      const result = await res.json();
      showSuccess(`Model ${modelId} retrained successfully!`);
      await loadModelStatus(); // Refresh data
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error";
      showError(`Retraining failed: ${errorMessage}`);
    } finally {
      setRetrainingModel(null);
    }
  };

  const toggleAutoRetrain = async () => {
    try {
      const newState = !data?.auto_retrain_enabled;
      const res = await fetch("/api/proxy/api/ml/models/auto-retrain", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ enabled: newState }),
      });
      if (!res.ok) throw new Error("Failed to toggle auto-retrain");
      showSuccess(`Auto-retrain ${newState ? "enabled" : "disabled"}`);
      await loadModelStatus();
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error";
      showError(`Failed to toggle auto-retrain: ${errorMessage}`);
    }
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case "active":
      case "healthy":
        return theme.colors.success;
      case "training":
      case "degraded":
        return theme.colors.warning;
      case "stale":
      case "critical":
      case "error":
        return theme.colors.error;
      default:
        return theme.colors.textMuted;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "active":
      case "healthy":
        return <CheckCircle size={20} color={theme.colors.success} />;
      case "training":
        return <RefreshCw size={20} color={theme.colors.warning} className="animate-spin" />;
      case "stale":
      case "degraded":
      case "critical":
      case "error":
        return <AlertTriangle size={20} color={theme.colors.error} />;
      default:
        return <Activity size={20} />;
    }
  };

  const getHealthScoreColor = (score: number): string => {
    if (score >= 80) return theme.colors.success;
    if (score >= 60) return theme.colors.warning;
    return theme.colors.error;
  };

  const formatDuration = (seconds: number): string => {
    if (seconds < 60) return `${seconds}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
    return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return "Today";
    if (diffDays === 1) return "Yesterday";
    if (diffDays < 7) return `${diffDays} days ago`;
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
            textShadow: theme.glow.green,
            marginBottom: theme.spacing.xs,
            display: "flex",
            alignItems: "center",
            gap: theme.spacing.sm,
          }}
        >
          <Database size={32} color={theme.colors.primary} />
          ML Model Management
        </h2>
        <p
          style={{
            margin: 0,
            fontSize: "14px",
            color: theme.colors.textMuted,
          }}
        >
          Monitor model health, versions, and performance
        </p>
      </div>

      {/* Controls */}
      <Card glow="green" style={{ marginBottom: theme.spacing.lg }}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: theme.spacing.md,
          }}
        >
          <Button onClick={loadModelStatus} loading={isLoading} variant="primary">
            <RefreshCw size={18} />
            Refresh Status
          </Button>

          {data && (
            <label
              style={{
                display: "flex",
                alignItems: "center",
                gap: theme.spacing.sm,
                fontSize: "14px",
                color: theme.colors.text,
                cursor: "pointer",
              }}
            >
              <input
                type="checkbox"
                checked={data.auto_retrain_enabled}
                onChange={toggleAutoRetrain}
                style={{ cursor: "pointer" }}
              />
              <Activity size={16} />
              Auto-retrain enabled
            </label>
          )}

          {data?.next_scheduled_training && (
            <div
              style={{
                fontSize: "13px",
                color: theme.colors.textMuted,
              }}
            >
              <Calendar size={14} style={{ display: "inline", marginRight: "4px" }} />
              Next training: {formatDate(data.next_scheduled_training)}
            </div>
          )}
        </div>
      </Card>

      {/* System Status */}
      {data && (
        <Card
          glow={data.system_status === "healthy" ? "green" : data.system_status === "degraded" ? "yellow" : "red"}
          style={{ marginBottom: theme.spacing.lg }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: theme.spacing.md,
            }}
          >
            {getStatusIcon(data.system_status)}
            <div>
              <h3
                style={{
                  margin: 0,
                  fontSize: "18px",
                  fontWeight: "600",
                  color: getStatusColor(data.system_status),
                  textTransform: "uppercase",
                }}
              >
                System Status: {data.system_status}
              </h3>
              <p
                style={{
                  margin: 0,
                  fontSize: "13px",
                  color: theme.colors.textMuted,
                  marginTop: theme.spacing.xs,
                }}
              >
                {data.models.length} models active •{" "}
                {data.health_checks.filter((h) => h.requires_retraining).length} require retraining
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* Models Grid */}
      {data && (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: isMobile ? "1fr" : "repeat(auto-fit, minmax(400px, 1fr))",
            gap: theme.spacing.lg,
          }}
        >
          {data.models.map((model, idx) => {
            const health = data.health_checks.find((h) => h.model_id === model.model_id);

            return (
              <Card key={idx} glow="cyan" style={{ position: "relative" }}>
                {/* Model Header */}
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "flex-start",
                    marginBottom: theme.spacing.md,
                  }}
                >
                  <div>
                    <h3
                      style={{
                        margin: 0,
                        fontSize: "20px",
                        fontWeight: "700",
                        color: theme.colors.text,
                      }}
                    >
                      {model.model_type.replace(/_/g, " ").toUpperCase()}
                    </h3>
                    <div
                      style={{
                        fontSize: "12px",
                        color: theme.colors.textMuted,
                        marginTop: theme.spacing.xs,
                      }}
                    >
                      v{model.version} • {model.model_id}
                    </div>
                  </div>

                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: theme.spacing.xs,
                      padding: "6px 12px",
                      background: `rgba(${model.status === "active" ? "16, 185, 129" : model.status === "training" ? "251, 191, 36" : "239, 68, 68"}, 0.2)`,
                      border: `1px solid ${getStatusColor(model.status)}`,
                      borderRadius: theme.borderRadius.sm,
                    }}
                  >
                    {getStatusIcon(model.status)}
                    <span
                      style={{
                        fontSize: "12px",
                        fontWeight: "700",
                        color: getStatusColor(model.status),
                        textTransform: "uppercase",
                      }}
                    >
                      {model.status}
                    </span>
                  </div>
                </div>

                {/* Model Metrics */}
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
                    <div style={{ fontSize: "11px", color: theme.colors.textMuted }}>ACCURACY</div>
                    <div
                      style={{
                        fontSize: "24px",
                        fontWeight: "700",
                        color: theme.colors.secondary,
                      }}
                    >
                      {(model.accuracy * 100).toFixed(1)}%
                    </div>
                  </div>

                  <div
                    style={{
                      padding: theme.spacing.sm,
                      background: "rgba(139, 92, 246, 0.1)",
                      borderRadius: theme.borderRadius.sm,
                    }}
                  >
                    <div style={{ fontSize: "11px", color: theme.colors.textMuted }}>SAMPLES</div>
                    <div
                      style={{
                        fontSize: "24px",
                        fontWeight: "700",
                        color: theme.colors.accent,
                      }}
                    >
                      {model.samples_trained.toLocaleString()}
                    </div>
                  </div>

                  <div
                    style={{
                      padding: theme.spacing.sm,
                      background: "rgba(16, 185, 129, 0.1)",
                      borderRadius: theme.borderRadius.sm,
                    }}
                  >
                    <div style={{ fontSize: "11px", color: theme.colors.textMuted }}>FEATURES</div>
                    <div
                      style={{
                        fontSize: "24px",
                        fontWeight: "700",
                        color: theme.colors.success,
                      }}
                    >
                      {model.features_count}
                    </div>
                  </div>

                  <div
                    style={{
                      padding: theme.spacing.sm,
                      background: "rgba(251, 191, 36, 0.1)",
                      borderRadius: theme.borderRadius.sm,
                    }}
                  >
                    <div style={{ fontSize: "11px", color: theme.colors.textMuted }}>TRAINING TIME</div>
                    <div
                      style={{
                        fontSize: "20px",
                        fontWeight: "700",
                        color: theme.colors.warning,
                      }}
                    >
                      {formatDuration(model.training_duration_seconds)}
                    </div>
                  </div>
                </div>

                {/* Health Info */}
                {health && (
                  <div
                    style={{
                      padding: theme.spacing.md,
                      background: "rgba(15, 23, 42, 0.5)",
                      borderRadius: theme.borderRadius.md,
                      marginBottom: theme.spacing.md,
                    }}
                  >
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        marginBottom: theme.spacing.sm,
                      }}
                    >
                      <span style={{ fontSize: "13px", color: theme.colors.textMuted }}>Health Score</span>
                      <span
                        style={{
                          fontSize: "20px",
                          fontWeight: "700",
                          color: getHealthScoreColor(health.health_score),
                        }}
                      >
                        {health.health_score.toFixed(0)}%
                      </span>
                    </div>

                    <div
                      style={{
                        width: "100%",
                        height: "8px",
                        background: "rgba(15, 23, 42, 0.8)",
                        borderRadius: "4px",
                        overflow: "hidden",
                      }}
                    >
                      <div
                        style={{
                          width: `${health.health_score}%`,
                          height: "100%",
                          background: `linear-gradient(90deg, ${getHealthScoreColor(health.health_score)}, ${theme.colors.primary})`,
                          transition: "width 0.3s ease",
                        }}
                      />
                    </div>

                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        marginTop: theme.spacing.sm,
                        fontSize: "12px",
                        color: theme.colors.textMuted,
                      }}
                    >
                      <span>Last trained: {formatDate(model.last_trained)}</span>
                      <span>{health.total_predictions.toLocaleString()} predictions</span>
                    </div>

                    {/* Issues */}
                    {health.issues.length > 0 && (
                      <div style={{ marginTop: theme.spacing.sm }}>
                        {health.issues.map((issue, issueIdx) => (
                          <div
                            key={issueIdx}
                            style={{
                              fontSize: "12px",
                              color: theme.colors.error,
                              padding: "4px 8px",
                              background: "rgba(239, 68, 68, 0.1)",
                              borderRadius: theme.borderRadius.xs,
                              marginBottom: theme.spacing.xs,
                            }}
                          >
                            ⚠️ {issue}
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Recommendations */}
                    {health.recommendations.length > 0 && (
                      <div style={{ marginTop: theme.spacing.sm }}>
                        {health.recommendations.slice(0, 2).map((rec, recIdx) => (
                          <div
                            key={recIdx}
                            style={{
                              fontSize: "12px",
                              color: theme.colors.secondary,
                              padding: "4px 8px",
                              background: "rgba(6, 182, 212, 0.1)",
                              borderRadius: theme.borderRadius.xs,
                              marginBottom: theme.spacing.xs,
                            }}
                          >
                            💡 {rec}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* Actions */}
                <div style={{ display: "flex", gap: theme.spacing.sm }}>
                  <Button
                    onClick={() => retrainModel(model.model_id)}
                    loading={retrainingModel === model.model_id}
                    disabled={model.status === "training" || retrainingModel !== null}
                    variant="primary"
                    style={{ flex: 1 }}
                  >
                    {retrainingModel === model.model_id ? "Retraining..." : "Retrain Model"}
                  </Button>

                  {health?.requires_retraining && (
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        padding: "0 12px",
                        background: "rgba(239, 68, 68, 0.2)",
                        border: `1px solid ${theme.colors.error}`,
                        borderRadius: theme.borderRadius.md,
                        fontSize: "12px",
                        fontWeight: "700",
                        color: theme.colors.error,
                      }}
                    >
                      RETRAIN NEEDED
                    </div>
                  )}
                </div>

                {/* Hyperparameters (collapsed) */}
                <details style={{ marginTop: theme.spacing.md }}>
                  <summary
                    style={{
                      fontSize: "12px",
                      color: theme.colors.textMuted,
                      cursor: "pointer",
                      textTransform: "uppercase",
                      letterSpacing: "0.5px",
                    }}
                  >
                    Hyperparameters
                  </summary>
                  <div
                    style={{
                      marginTop: theme.spacing.sm,
                      padding: theme.spacing.sm,
                      background: "rgba(15, 23, 42, 0.5)",
                      borderRadius: theme.borderRadius.sm,
                      fontSize: "12px",
                      fontFamily: "monospace",
                      color: theme.colors.text,
                    }}
                  >
                    {Object.entries(model.hyperparameters).map(([key, value]) => (
                      <div key={key}>
                        <span style={{ color: theme.colors.secondary }}>{key}</span>:{" "}
                        <span style={{ color: theme.colors.accent }}>{JSON.stringify(value)}</span>
                      </div>
                    ))}
                  </div>
                </details>
              </Card>
            );
          })}
        </div>
      )}

      {/* Empty State */}
      {!isLoading && !data && (
        <Card glow="cyan">
          <div
            style={{
              textAlign: "center",
              padding: theme.spacing.xl,
              color: theme.colors.textMuted,
            }}
          >
            <Database size={48} color={theme.colors.textMuted} style={{ marginBottom: theme.spacing.md }} />
            <p>Click "Refresh Status" to load model information</p>
          </div>
        </Card>
      )}
    </div>
  );
}
