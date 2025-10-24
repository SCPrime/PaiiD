import { CSSProperties, FC, useCallback, useEffect, useMemo, useState } from "react";
import toast from "react-hot-toast";
import { GlassBadge, GlassButton, GlassCard } from "@/components/GlassmorphicComponents";
import { theme } from "@/styles/theme";
import { FeatureToggleList } from "./FeatureToggleList";
import { HistoryTimeline } from "./HistoryTimeline";
import { ModelSelector } from "./ModelSelector";
import {
  fetchStrategyConfig,
  fetchStrategyHistory,
  fetchStrategyPerformance,
  saveStrategyConfig,
} from "./api";
import { StrategyConfigResponse, StrategyPerformanceLog, StrategyVersion } from "./types";

interface StrategyConfigManagerProps {
  strategyType: string;
}

const MODEL_OPTIONS = [
  {
    value: "paiid-pro",
    label: "PAiiD Pro",
    description: "Highest accuracy multi-factor model tuned for options strategies.",
    latency: "~2.1s",
  },
  {
    value: "paiid-lite",
    label: "PAiiD Lite",
    description: "Cost efficient model ideal for iteration and paper trading.",
    latency: "~1.1s",
  },
  {
    value: "gpt-4o-mini",
    label: "GPT-4o Mini",
    description: "OpenAI hosted baseline for benchmarking alternative agents.",
    latency: "~1.4s",
  },
];

const FEATURE_DEFINITIONS = [
  {
    key: "autoRebalance",
    label: "Auto rebalance",
    description: "Keep allocations within tolerance bands using nightly adjustments.",
  },
  {
    key: "riskOverlay",
    label: "Risk overlay",
    description: "Apply broker risk limits before signals reach execution.",
  },
  {
    key: "notifyOnDrift",
    label: "Notify on drift",
    description: "Send alerts when price deviates beyond configured thresholds.",
  },
];

const CARD_HEADER_STYLE: CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  gap: theme.spacing.md,
  flexWrap: "wrap",
  alignItems: "flex-start",
};

const CARD_BODY_STYLE: CSSProperties = {
  display: "grid",
  gap: theme.spacing.lg,
};

const ACTION_ROW_STYLE: CSSProperties = {
  display: "flex",
  gap: theme.spacing.sm,
  flexWrap: "wrap",
};

const DEFAULT_FEATURE_STATE = FEATURE_DEFINITIONS.reduce<Record<string, boolean>>((acc, feature) => {
  acc[feature.key] = true;
  return acc;
}, {});

export const StrategyConfigManager: FC<StrategyConfigManagerProps> = ({ strategyType }) => {
  const [config, setConfig] = useState<Record<string, unknown>>({});
  const [modelKey, setModelKey] = useState<string>(MODEL_OPTIONS[0].value);
  const [featureFlags, setFeatureFlags] = useState<Record<string, boolean>>(DEFAULT_FEATURE_STATE);
  const [history, setHistory] = useState<StrategyVersion[]>([]);
  const [performance, setPerformance] = useState<StrategyPerformanceLog[]>([]);
  const [version, setVersion] = useState<number>(1);
  const [isDefault, setIsDefault] = useState<boolean>(true);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [lastSavedAt, setLastSavedAt] = useState<string | null>(null);

  const featureDefinitions = useMemo(() => FEATURE_DEFINITIONS, []);

  const mergeFeatureFlags = useCallback(
    (incoming: Record<string, boolean> | undefined): Record<string, boolean> => ({
      ...DEFAULT_FEATURE_STATE,
      ...(incoming || {}),
    }),
    [],
  );

  const loadConfiguration = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data: StrategyConfigResponse = await fetchStrategyConfig(strategyType);
      setConfig(data.config || {});
      setModelKey(data.model_key || MODEL_OPTIONS[0].value);
      setFeatureFlags(mergeFeatureFlags(data.feature_flags));
      setHistory(data.history || []);
      setPerformance(data.performance || []);
      setVersion(data.version || 1);
      setIsDefault(Boolean(data.is_default));
      setLastSavedAt(null);
    } catch (err: any) {
      console.error("Strategy config load error", err);
      setError(err.message || "Unable to load strategy configuration");
    } finally {
      setIsLoading(false);
    }
  }, [mergeFeatureFlags, strategyType]);

  useEffect(() => {
    void loadConfiguration();
  }, [loadConfiguration]);

  const refreshHistory = useCallback(async () => {
    try {
      const [versions, logs] = await Promise.all([
        fetchStrategyHistory(strategyType),
        fetchStrategyPerformance(strategyType),
      ]);
      setHistory(versions);
      setPerformance(logs);
    } catch (err: any) {
      console.error("Strategy history refresh error", err);
      toast.error(err.message || "Failed to refresh history");
    }
  }, [strategyType]);

  const handleToggle = useCallback((key: string, value: boolean) => {
    setFeatureFlags((prev) => ({ ...prev, [key]: value }));
  }, []);

  const handleSave = useCallback(async () => {
    setIsSaving(true);
    setError(null);
    try {
      const saved = await saveStrategyConfig({
        strategy_type: strategyType,
        config,
        model_key: modelKey,
        feature_flags: featureFlags,
        changes_summary: "Updated via strategy control panel",
      });

      setConfig(saved.config || {});
      setModelKey(saved.model_key || MODEL_OPTIONS[0].value);
      setFeatureFlags(mergeFeatureFlags(saved.feature_flags));
      setHistory(saved.history || []);
      setPerformance(saved.performance || []);
      setVersion(saved.version || 1);
      setIsDefault(Boolean(saved.is_default));
      setLastSavedAt(new Date().toISOString());

      toast.success("Strategy settings saved");
    } catch (err: any) {
      console.error("Strategy save error", err);
      const message = err.message || "Failed to save strategy";
      setError(message);
      toast.error(message);
    } finally {
      setIsSaving(false);
    }
  }, [config, featureFlags, mergeFeatureFlags, modelKey, strategyType]);

  const lastSavedMessage = useMemo(() => {
    if (!lastSavedAt) return null;
    return `Last saved ${new Date(lastSavedAt).toLocaleString()}`;
  }, [lastSavedAt]);

  return (
    <GlassCard>
      <div style={CARD_HEADER_STYLE}>
        <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
          <h3 style={{ margin: 0, fontSize: "18px", color: theme.colors.text }}>
            Strategy Controls
          </h3>
          <p style={{ margin: 0, color: theme.colors.textMuted, fontSize: "13px" }}>
            Select the inference model, toggle advanced features, and review version history.
          </p>
        </div>
        <div style={{ display: "flex", gap: theme.spacing.sm, alignItems: "center", flexWrap: "wrap" }}>
          <GlassBadge variant={isDefault ? "info" : "success"}>
            {isDefault ? "Default config" : `v${version}`}
          </GlassBadge>
          <GlassBadge variant="info">{strategyType}</GlassBadge>
        </div>
      </div>

      {error && (
        <div
          style={{
            padding: "12px 16px",
            borderRadius: "12px",
            background: `${theme.colors.danger}15`,
            color: theme.colors.danger,
            border: `1px solid ${theme.colors.danger}40`,
          }}
        >
          {error}
        </div>
      )}

      <div style={CARD_BODY_STYLE}>
        <ModelSelector
          value={modelKey}
          onChange={setModelKey}
          options={MODEL_OPTIONS}
          disabled={isLoading}
        />

        <FeatureToggleList
          features={featureDefinitions}
          values={featureFlags}
          onChange={handleToggle}
          disabled={isLoading}
        />

        <div style={ACTION_ROW_STYLE}>
          <GlassButton onClick={handleSave} disabled={isSaving || isLoading}>
            {isSaving ? "Saving..." : "Save configuration"}
          </GlassButton>
          <GlassButton variant="secondary" onClick={refreshHistory} disabled={isLoading}>
            Refresh history
          </GlassButton>
          {lastSavedMessage && (
            <span style={{ fontSize: "12px", color: "rgba(255,255,255,0.6)", alignSelf: "center" }}>
              {lastSavedMessage}
            </span>
          )}
        </div>

        <HistoryTimeline versions={history} performance={performance} />
      </div>
    </GlassCard>
  );
};

export default StrategyConfigManager;
