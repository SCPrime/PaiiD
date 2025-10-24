"use client";

import { useState } from "react";
import { Card, Button } from "./ui";
import { theme } from "../styles/theme";
import { showSuccess, showError } from "../lib/toast";
import { Brain, TrendingUp, Target, Zap, CheckCircle, AlertCircle } from "lucide-react";
import { useIsMobile } from "../hooks/useBreakpoint";

interface TrainingStatus {
  isTraining: boolean;
  progress: number;
  stage: string;
  error: string | null;
}

interface TrainingResult {
  success: boolean;
  message: string;
  regime_labels?: Record<string, string>;
  training_data?: {
    symbol: string;
    lookback_days: number;
  };
  train_accuracy?: number;
  test_accuracy?: number;
  n_samples?: number;
}

export default function MLTrainingDashboard() {
  const isMobile = useIsMobile();

  // Regime Detector Training
  const [regimeStatus, setRegimeStatus] = useState<TrainingStatus>({
    isTraining: false,
    progress: 0,
    stage: "",
    error: null,
  });
  const [regimeResult, setRegimeResult] = useState<TrainingResult | null>(null);
  const [regimeSymbol, setRegimeSymbol] = useState("SPY");
  const [regimeLookback, setRegimeLookback] = useState(730);

  // Strategy Selector Training
  const [strategyStatus, setStrategyStatus] = useState<TrainingStatus>({
    isTraining: false,
    progress: 0,
    stage: "",
    error: null,
  });
  const [strategyResult, setStrategyResult] = useState<TrainingResult | null>(null);
  const [strategySymbols, setStrategySymbols] = useState("SPY,QQQ,IWM,DIA");
  const [strategyLookback, setStrategyLookback] = useState(365);

  const trainRegimeDetector = async () => {
    setRegimeStatus({ isTraining: true, progress: 0, stage: "Initializing...", error: null });
    setRegimeResult(null);

    try {
      // Stage 1: Fetching data
      setRegimeStatus({ isTraining: true, progress: 25, stage: "Fetching market data...", error: null });
      await new Promise(resolve => setTimeout(resolve, 500));

      // Stage 2: Feature engineering
      setRegimeStatus({ isTraining: true, progress: 50, stage: "Engineering features...", error: null });

      // Make API call
      const res = await fetch(
        `/api/proxy/api/ml/train-regime-detector?symbol=${regimeSymbol}&lookback_days=${regimeLookback}`,
        { method: "POST" }
      );

      if (!res.ok) {
        throw new Error(`Training failed: ${res.status}`);
      }

      // Stage 3: Training model
      setRegimeStatus({ isTraining: true, progress: 75, stage: "Training K-Means model...", error: null });
      await new Promise(resolve => setTimeout(resolve, 500));

      const data = await res.json();

      // Stage 4: Complete
      setRegimeStatus({ isTraining: true, progress: 100, stage: "Training complete!", error: null });
      setRegimeResult(data);

      showSuccess(`✅ Regime detector trained on ${regimeSymbol}!`);

      setTimeout(() => {
        setRegimeStatus({ isTraining: false, progress: 100, stage: "Ready", error: null });
      }, 1000);

    } catch (err: unknown) {
      const errorMsg = err instanceof Error ? err.message : "Training failed";
      setRegimeStatus({ isTraining: false, progress: 0, stage: "", error: errorMsg });
      showError(errorMsg);
    }
  };

  const trainStrategySelector = async () => {
    setStrategyStatus({ isTraining: true, progress: 0, stage: "Initializing...", error: null });
    setStrategyResult(null);

    try {
      // Stage 1: Preparing data
      setStrategyStatus({ isTraining: true, progress: 15, stage: "Preparing training data...", error: null });
      await new Promise(resolve => setTimeout(resolve, 500));

      // Stage 2: Running backtests
      setStrategyStatus({ isTraining: true, progress: 40, stage: "Running backtests (this may take 2-5 min)...", error: null });

      // Make API call (this is long-running)
      const symbols = strategySymbols.split(",").map(s => s.trim());
      const queryParams = symbols.map(s => `symbols=${s}`).join("&");
      const res = await fetch(
        `/api/proxy/api/ml/train-strategy-selector?${queryParams}&lookback_days=${strategyLookback}`,
        { method: "POST" }
      );

      if (!res.ok) {
        throw new Error(`Training failed: ${res.status}`);
      }

      // Stage 3: Training Random Forest
      setStrategyStatus({ isTraining: true, progress: 80, stage: "Training Random Forest model...", error: null });
      await new Promise(resolve => setTimeout(resolve, 500));

      const data = await res.json();

      // Stage 4: Complete
      setStrategyStatus({ isTraining: true, progress: 100, stage: "Training complete!", error: null });
      setStrategyResult(data);

      showSuccess(`✅ Strategy selector trained on ${symbols.length} symbols!`);

      setTimeout(() => {
        setStrategyStatus({ isTraining: false, progress: 100, stage: "Ready", error: null });
      }, 1000);

    } catch (err: unknown) {
      const errorMsg = err instanceof Error ? err.message : "Training failed";
      setStrategyStatus({ isTraining: false, progress: 0, stage: "", error: errorMsg });
      showError(errorMsg);
    }
  };

  return (
    <div style={{ padding: isMobile ? theme.spacing.md : theme.spacing.lg }}>
      {/* Header */}
      <div style={{ marginBottom: theme.spacing.xl }}>
        <h2
          style={{
            margin: 0,
            fontSize: isMobile ? "24px" : "32px",
            fontWeight: "700",
            color: theme.colors.text,
            textShadow: theme.glow.purple,
            marginBottom: theme.spacing.xs,
          }}
        >
          🧠 ML Training Dashboard
        </h2>
        <p
          style={{
            margin: 0,
            fontSize: "14px",
            color: theme.colors.textMuted,
          }}
        >
          Train machine learning models in real-time with live progress tracking
        </p>
      </div>

      {/* Regime Detector Training */}
      <Card glow="purple" style={{ marginBottom: theme.spacing.xl }}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: theme.spacing.md,
            marginBottom: theme.spacing.lg,
          }}
        >
          <Brain size={32} color={theme.colors.primary} />
          <div>
            <h3
              style={{
                margin: 0,
                fontSize: "20px",
                fontWeight: "700",
                color: theme.colors.text,
              }}
            >
              Market Regime Detector
            </h3>
            <p
              style={{
                margin: 0,
                marginTop: "4px",
                fontSize: "13px",
                color: theme.colors.textMuted,
              }}
            >
              K-Means clustering to identify market conditions
            </p>
          </div>
        </div>

        {/* Training Form */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: isMobile ? "1fr" : "1fr 1fr auto",
            gap: theme.spacing.md,
            marginBottom: theme.spacing.lg,
          }}
        >
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
              value={regimeSymbol}
              onChange={(e) => setRegimeSymbol(e.target.value.toUpperCase())}
              disabled={regimeStatus.isTraining}
              style={{
                width: "100%",
                padding: "10px 14px",
                background: "rgba(15, 23, 42, 0.5)",
                border: `1px solid ${theme.colors.border}`,
                borderRadius: theme.borderRadius.md,
                color: theme.colors.text,
                fontSize: "14px",
              }}
              placeholder="SPY"
            />
          </div>

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
              Lookback Days
            </label>
            <input
              type="number"
              value={regimeLookback}
              onChange={(e) => setRegimeLookback(parseInt(e.target.value))}
              disabled={regimeStatus.isTraining}
              min={365}
              max={1825}
              style={{
                width: "100%",
                padding: "10px 14px",
                background: "rgba(15, 23, 42, 0.5)",
                border: `1px solid ${theme.colors.border}`,
                borderRadius: theme.borderRadius.md,
                color: theme.colors.text,
                fontSize: "14px",
              }}
            />
          </div>

          <div style={{ display: "flex", alignItems: "flex-end" }}>
            <Button
              onClick={trainRegimeDetector}
              loading={regimeStatus.isTraining}
              variant="primary"
              disabled={regimeStatus.isTraining}
              style={{ width: isMobile ? "100%" : "auto" }}
            >
              <Zap size={16} style={{ marginRight: "6px" }} />
              Train Model
            </Button>
          </div>
        </div>

        {/* Progress Bar */}
        {regimeStatus.isTraining && (
          <div style={{ marginBottom: theme.spacing.lg }}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                marginBottom: theme.spacing.xs,
              }}
            >
              <span style={{ fontSize: "12px", color: theme.colors.textMuted }}>
                {regimeStatus.stage}
              </span>
              <span style={{ fontSize: "12px", color: theme.colors.primary, fontWeight: "700" }}>
                {regimeStatus.progress}%
              </span>
            </div>
            <div
              style={{
                width: "100%",
                height: "8px",
                background: "rgba(15, 23, 42, 0.5)",
                borderRadius: "9999px",
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  width: `${regimeStatus.progress}%`,
                  height: "100%",
                  background: `linear-gradient(90deg, ${theme.colors.primary}, ${theme.colors.secondary})`,
                  transition: "width 0.3s ease",
                  boxShadow: theme.glow.green,
                }}
              />
            </div>
          </div>
        )}

        {/* Training Result */}
        {regimeResult && (
          <div
            style={{
              padding: theme.spacing.md,
              background: "rgba(16, 185, 129, 0.1)",
              border: `2px solid ${theme.colors.primary}`,
              borderRadius: theme.borderRadius.md,
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: theme.spacing.sm,
                marginBottom: theme.spacing.sm,
              }}
            >
              <CheckCircle size={20} color={theme.colors.primary} />
              <span style={{ fontSize: "14px", fontWeight: "700", color: theme.colors.text }}>
                {regimeResult.message}
              </span>
            </div>

            {regimeResult.regime_labels && (
              <div style={{ fontSize: "13px", color: theme.colors.text }}>
                <strong>Detected Regimes:</strong>
                <div style={{ marginTop: theme.spacing.xs }}>
                  {Object.entries(regimeResult.regime_labels).map(([id, label]) => (
                    <div key={id} style={{ padding: "4px 0" }}>
                      • {label.replace(/_/g, " ").toUpperCase()}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Error Display */}
        {regimeStatus.error && (
          <div
            style={{
              padding: theme.spacing.md,
              background: "rgba(239, 68, 68, 0.1)",
              border: `2px solid ${theme.colors.danger}`,
              borderRadius: theme.borderRadius.md,
              display: "flex",
              alignItems: "center",
              gap: theme.spacing.sm,
            }}
          >
            <AlertCircle size={20} color={theme.colors.danger} />
            <span style={{ fontSize: "14px", color: theme.colors.text }}>
              {regimeStatus.error}
            </span>
          </div>
        )}
      </Card>

      {/* Strategy Selector Training */}
      <Card glow="cyan" style={{ marginBottom: theme.spacing.xl }}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: theme.spacing.md,
            marginBottom: theme.spacing.lg,
          }}
        >
          <Target size={32} color={theme.colors.secondary} />
          <div>
            <h3
              style={{
                margin: 0,
                fontSize: "20px",
                fontWeight: "700",
                color: theme.colors.text,
              }}
            >
              Strategy Selector
            </h3>
            <p
              style={{
                margin: 0,
                marginTop: "4px",
                fontSize: "13px",
                color: theme.colors.textMuted,
              }}
            >
              Random Forest to recommend optimal trading strategies
            </p>
          </div>
        </div>

        {/* Training Form */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: isMobile ? "1fr" : "2fr 1fr auto",
            gap: theme.spacing.md,
            marginBottom: theme.spacing.lg,
          }}
        >
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
              Symbols (comma-separated)
            </label>
            <input
              type="text"
              value={strategySymbols}
              onChange={(e) => setStrategySymbols(e.target.value.toUpperCase())}
              disabled={strategyStatus.isTraining}
              style={{
                width: "100%",
                padding: "10px 14px",
                background: "rgba(15, 23, 42, 0.5)",
                border: `1px solid ${theme.colors.border}`,
                borderRadius: theme.borderRadius.md,
                color: theme.colors.text,
                fontSize: "14px",
              }}
              placeholder="SPY,QQQ,IWM,DIA"
            />
          </div>

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
              Lookback Days
            </label>
            <input
              type="number"
              value={strategyLookback}
              onChange={(e) => setStrategyLookback(parseInt(e.target.value))}
              disabled={strategyStatus.isTraining}
              min={180}
              max={730}
              style={{
                width: "100%",
                padding: "10px 14px",
                background: "rgba(15, 23, 42, 0.5)",
                border: `1px solid ${theme.colors.border}`,
                borderRadius: theme.borderRadius.md,
                color: theme.colors.text,
                fontSize: "14px",
              }}
            />
          </div>

          <div style={{ display: "flex", alignItems: "flex-end" }}>
            <Button
              onClick={trainStrategySelector}
              loading={strategyStatus.isTraining}
              variant="primary"
              disabled={strategyStatus.isTraining}
              style={{ width: isMobile ? "100%" : "auto" }}
            >
              <TrendingUp size={16} style={{ marginRight: "6px" }} />
              Train Model
            </Button>
          </div>
        </div>

        {/* Progress Bar */}
        {strategyStatus.isTraining && (
          <div style={{ marginBottom: theme.spacing.lg }}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                marginBottom: theme.spacing.xs,
              }}
            >
              <span style={{ fontSize: "12px", color: theme.colors.textMuted }}>
                {strategyStatus.stage}
              </span>
              <span style={{ fontSize: "12px", color: theme.colors.secondary, fontWeight: "700" }}>
                {strategyStatus.progress}%
              </span>
            </div>
            <div
              style={{
                width: "100%",
                height: "8px",
                background: "rgba(15, 23, 42, 0.5)",
                borderRadius: "9999px",
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  width: `${strategyStatus.progress}%`,
                  height: "100%",
                  background: `linear-gradient(90deg, ${theme.colors.secondary}, ${theme.colors.primary})`,
                  transition: "width 0.3s ease",
                  boxShadow: theme.glow.cyan,
                }}
              />
            </div>
          </div>
        )}

        {/* Training Result */}
        {strategyResult && (
          <div
            style={{
              padding: theme.spacing.md,
              background: "rgba(6, 182, 212, 0.1)",
              border: `2px solid ${theme.colors.secondary}`,
              borderRadius: theme.borderRadius.md,
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: theme.spacing.sm,
                marginBottom: theme.spacing.sm,
              }}
            >
              <CheckCircle size={20} color={theme.colors.secondary} />
              <span style={{ fontSize: "14px", fontWeight: "700", color: theme.colors.text }}>
                Training Complete!
              </span>
            </div>

            <div style={{ fontSize: "13px", color: theme.colors.text }}>
              <div style={{ padding: "4px 0" }}>
                <strong>Train Accuracy:</strong> {((strategyResult.train_accuracy || 0) * 100).toFixed(1)}%
              </div>
              <div style={{ padding: "4px 0" }}>
                <strong>Test Accuracy:</strong> {((strategyResult.test_accuracy || 0) * 100).toFixed(1)}%
              </div>
              <div style={{ padding: "4px 0" }}>
                <strong>Training Samples:</strong> {strategyResult.n_samples || 0}
              </div>
            </div>
          </div>
        )}

        {/* Error Display */}
        {strategyStatus.error && (
          <div
            style={{
              padding: theme.spacing.md,
              background: "rgba(239, 68, 68, 0.1)",
              border: `2px solid ${theme.colors.danger}`,
              borderRadius: theme.borderRadius.md,
              display: "flex",
              alignItems: "center",
              gap: theme.spacing.sm,
            }}
          >
            <AlertCircle size={20} color={theme.colors.danger} />
            <span style={{ fontSize: "14px", color: theme.colors.text }}>
              {strategyStatus.error}
            </span>
          </div>
        )}
      </Card>

      {/* Info Panel */}
      <Card>
        <h4
          style={{
            margin: 0,
            fontSize: "16px",
            fontWeight: "700",
            color: theme.colors.text,
            marginBottom: theme.spacing.md,
          }}
        >
          ℹ️ Training Tips
        </h4>
        <ul style={{ margin: 0, paddingLeft: "20px", color: theme.colors.textMuted, fontSize: "13px" }}>
          <li style={{ marginBottom: theme.spacing.xs }}>
            <strong>Regime Detector:</strong> Train weekly or after major market events (~10 seconds)
          </li>
          <li style={{ marginBottom: theme.spacing.xs }}>
            <strong>Strategy Selector:</strong> Train monthly or quarterly (~2-5 minutes)
          </li>
          <li style={{ marginBottom: theme.spacing.xs }}>
            Use SPY for regime detection (represents overall market)
          </li>
          <li style={{ marginBottom: theme.spacing.xs }}>
            Include multiple symbols for strategy selector (SPY, QQQ, IWM, DIA recommended)
          </li>
          <li>
            Longer lookback periods = more stable models, but less responsive to recent changes
          </li>
        </ul>
      </Card>
    </div>
  );
}
