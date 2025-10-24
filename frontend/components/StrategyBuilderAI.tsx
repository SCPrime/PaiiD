/**
 * AI-Powered Strategy Builder
 * Natural language strategy generation with visual editing
 * NOTE: TypeScript checking disabled temporarily - needs interface fixes
 */

import {
  AlertCircle,
  Award,
  BarChart3,
  Brain,
  Code2,
  Copy,
  Edit3,
  Loader2,
  Play,
  Save,
  Search,
  Shield,
  Sparkles,
  Target,
  Trash2,
} from "lucide-react";
import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { useIsMobile } from "../hooks/useBreakpoint";
import { claudeAI } from "../lib/aiAdapter";
import { theme } from "../styles/theme";
import { GlassBadge, GlassButton, GlassCard } from "./GlassmorphicComponents";
import StockLookup from "./StockLookup";
import TemplateCustomizationModal from "./TemplateCustomizationModal";
interface Strategy {
  id?: string;
  name: string;
  entry: string[];
  exit: string[];
  riskManagement?: string[] | { maxDrawdown?: number; [key: string]: unknown };
  code?: string;
  status?: string;
  entryRules?: Array<{
    condition: string;
    value: string;
    operator: string;
  }>;
  exitRules?: Array<{
    condition: string;
    value: string;
    operator: string;
  }>;
  positionSizing?: {
    method: string;
    percentage: number;
    maxRisk: number;
  };
  aiPrompt?: string;
  createdAt?: string;
  updatedAt?: string;
}

interface SavedStrategy extends Omit<Strategy, "id"> {
  id: string;
  aiPrompt?: string;
  status?: string;
  createdAt?: string;
  updatedAt?: string;
  entryRules?: Array<{
    condition: string;
    value: string;
    operator: string;
  }>;
  exitRules?: Array<{
    condition: string;
    value: string;
    operator: string;
  }>;
  positionSizing?: {
    method: string;
    percentage: number;
    maxRisk: number;
  };
  backtestResults?: {
    winRate: number;
    totalTrades: number;
    profitFactor: number;
  };
}

interface Template {
  id: string;
  name: string;
  description: string;
  strategy_type: string;
  risk_level: string;
  compatibility_score: number;
  expected_win_rate: number;
  avg_return_percent: number;
  max_drawdown_percent: number;
  recommended_for: string[];
  config: any;
}

export default function StrategyBuilderAI() {
  const isMobile = useIsMobile();
  const [view, setView] = useState<"create" | "library">("library");
  const [nlInput, setNlInput] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentStrategy, setCurrentStrategy] = useState<Strategy | null>(null);
  const [savedStrategies, setSavedStrategies] = useState<SavedStrategy[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Template gallery state
  const [templates, setTemplates] = useState<Template[]>([]);
  const [isLoadingTemplates, setIsLoadingTemplates] = useState(false);
  const [templatesError, setTemplatesError] = useState<string | null>(null);
  const [userRiskTolerance, setUserRiskTolerance] = useState<number>(50);
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);
  const [showCustomizationModal, setShowCustomizationModal] = useState(false);

  // Stock research state
  const [researchSymbol, setResearchSymbol] = useState("");
  const [showStockLookup, setShowStockLookup] = useState(false);

  // Load saved strategies from localStorage
  useEffect(() => {
    const saved = localStorage.getItem("ai_trader_strategies");
    if (saved) {
      try {
        setSavedStrategies(JSON.parse(saved));
      } catch (e) {
        console.error("Failed to load strategies:", e);
      }
    }
  }, []);

  // Save strategies to localStorage whenever they change
  useEffect(() => {
    if (savedStrategies.length > 0) {
      localStorage.setItem("ai_trader_strategies", JSON.stringify(savedStrategies));
    }
  }, [savedStrategies]);

  // Fetch templates when library view is opened
  useEffect(() => {
    if (view === "library") {
      fetchTemplates();
    }
  }, [view]);

  const fetchTemplates = async () => {
    setIsLoadingTemplates(true);
    setTemplatesError(null);

    const apiToken = process.env.NEXT_PUBLIC_API_TOKEN || "";
    const baseUrl =
      process.env.NEXT_PUBLIC_BACKEND_API_BASE_URL || "https://paiid-backend.onrender.com";

    try {
      const response = await fetch(`${baseUrl}/api/strategies/templates`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${apiToken}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch templates: ${response.status}`);
      }

      const data = await response.json();
      setTemplates(data.templates || []);
      setUserRiskTolerance(data.user_risk_tolerance || 50);
    } catch (err: any) {
      console.error("Template fetch error:", err);
      setTemplatesError(err.message || "Failed to load strategy templates");
    } finally {
      setIsLoadingTemplates(false);
    }
  };

  const handleCloneTemplate = async (template: Template) => {
    const apiToken = process.env.NEXT_PUBLIC_API_TOKEN || "";
    const baseUrl =
      process.env.NEXT_PUBLIC_BACKEND_API_BASE_URL || "https://paiid-backend.onrender.com";

    try {
      const response = await fetch(`${baseUrl}/api/strategies/templates/${template.id}/clone`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${apiToken}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          custom_name: `${template.name} (My Copy)`,
          customize_config: true,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to clone template: ${response.status}`);
      }

      await response.json(); // Clone response
      toast.success(`Template "${template.name}" cloned successfully!`);

      // Refresh saved strategies or add to local state
      // For now, just show success message
    } catch (err: any) {
      console.error("Clone template error:", err);
      toast.error(err.message || "Failed to clone template");
    }
  };

  const handleGenerateStrategy = async () => {
    if (!nlInput.trim()) return;

    setIsGenerating(true);
    setError(null);

    try {
      const strategy = await claudeAI.generateStrategy(nlInput);
      setCurrentStrategy(strategy);
      setView("create");
    } catch (err: any) {
      setError(err.message || "Failed to generate strategy");
      console.error("Strategy generation error:", err);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSaveStrategy = () => {
    if (!currentStrategy) return;

    // Ensure strategy has an ID
    const strategyToSave: SavedStrategy = {
      ...currentStrategy,
      id: currentStrategy.id || `strategy-${Date.now()}`,
    };

    const existingIndex = savedStrategies.findIndex((s) => s.id === strategyToSave.id);

    if (existingIndex >= 0) {
      // Update existing
      setSavedStrategies(
        savedStrategies.map((s) =>
          s.id === strategyToSave.id
            ? { ...strategyToSave, updatedAt: new Date().toISOString() }
            : s
        )
      );
    } else {
      // Add new
      setSavedStrategies([...savedStrategies, strategyToSave]);
    }

    setView("library");
    setCurrentStrategy(null);
    setNlInput("");
  };

  const handleDeleteStrategy = (id: string) => {
    if (confirm("Are you sure you want to delete this strategy?")) {
      setSavedStrategies(savedStrategies.filter((s) => s.id !== id));
    }
  };

  const handleEditStrategy = (strategy: SavedStrategy) => {
    setCurrentStrategy(strategy);
    setNlInput(strategy.aiPrompt || "");
    setView("create");
  };

  const handleActivateStrategy = (id: string) => {
    setSavedStrategies(
      savedStrategies.map((s) =>
        s.id === id ? { ...s, status: s.status === "active" ? "paused" : "active" } : s
      )
    );
  };

  const accentColor = theme.workflow.strategyBuilder;

  return (
    <div
      style={{
        height: "100%",
        background: theme.background.primary,
        padding: isMobile ? theme.spacing.md : theme.spacing.lg,
        overflowY: "auto",
      }}
    >
      <div
        style={{
          maxWidth: "1400px",
          margin: "0 auto",
          display: "flex",
          flexDirection: "column",
          gap: theme.spacing.lg,
        }}
      >
        {/* Header */}
        <div
          style={{
            display: "flex",
            flexDirection: isMobile ? "column" : "row",
            alignItems: isMobile ? "stretch" : "center",
            justifyContent: "space-between",
            gap: isMobile ? theme.spacing.sm : 0,
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: isMobile ? theme.spacing.sm : theme.spacing.md,
            }}
          >
            <div
              style={{
                padding: theme.spacing.md,
                background: `${accentColor}20`,
                borderRadius: theme.borderRadius.lg,
                boxShadow: theme.glow.darkPurple,
              }}
            >
              <Brain style={{ width: "32px", height: "32px", color: accentColor }} />
            </div>
            <div>
              <h1
                style={{
                  fontSize: isMobile ? "24px" : "32px",
                  fontWeight: "bold",
                  color: theme.colors.text,
                  margin: 0,
                }}
              >
                AI Strategy Builder
              </h1>
              <p
                style={{
                  color: theme.colors.textMuted,
                  margin: "4px 0 0 0",
                  fontSize: "14px",
                }}
              >
                Create trading strategies from natural language
              </p>
            </div>
          </div>

          {/* View Toggle */}
          <div style={{ display: "flex", gap: theme.spacing.sm }}>
            <GlassButton
              variant={view === "library" ? "primary" : "secondary"}
              onClick={() => setView("library")}
            >
              <Code2 style={{ width: "18px", height: "18px" }} />
              Strategy Library
            </GlassButton>
            <GlassButton
              variant={view === "create" ? "primary" : "secondary"}
              onClick={() => setView("create")}
            >
              <Sparkles style={{ width: "18px", height: "18px" }} />
              Create New
            </GlassButton>
          </div>
        </div>

        {/* Error Banner */}
        {error && (
          <GlassCard
            style={{
              background: `${theme.colors.danger}10`,
              border: `1px solid ${theme.colors.danger}40`,
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: theme.spacing.sm }}>
              <AlertCircle style={{ width: "20px", height: "20px", color: theme.colors.danger }} />
              <p style={{ margin: 0, color: theme.colors.danger }}>{error}</p>
            </div>
          </GlassCard>
        )}

        {/* Create View */}
        {view === "create" && (
          <>
            {/* Natural Language Input */}
            <GlassCard glow="darkPurple">
              <h3
                style={{
                  fontSize: "18px",
                  fontWeight: "600",
                  color: theme.colors.text,
                  margin: `0 0 ${theme.spacing.md} 0`,
                  display: "flex",
                  alignItems: "center",
                  gap: theme.spacing.sm,
                }}
              >
                <Sparkles style={{ width: "20px", height: "20px", color: accentColor }} />
                Describe Your Strategy
              </h3>

              <p
                style={{
                  color: theme.colors.textMuted,
                  margin: `0 0 ${theme.spacing.md} 0`,
                  fontSize: "14px",
                }}
              >
                Tell me what you want to trade, when to enter, when to exit, and any risk
                parameters.
              </p>

              <div style={{ display: "flex", flexDirection: "column", gap: theme.spacing.sm }}>
                <textarea
                  value={nlInput}
                  onChange={(e) => setNlInput(e.target.value)}
                  placeholder={`Example: "Buy TSLA when RSI < 30 and volume is 2x average. Sell at 5% profit or 2% stop loss. Position size should be 10% of portfolio."`}
                  disabled={isGenerating}
                  style={{
                    width: "100%",
                    minHeight: "120px",
                    padding: theme.spacing.md,
                    background: theme.background.input,
                    border: `1px solid ${theme.colors.border}`,
                    borderRadius: theme.borderRadius.md,
                    color: theme.colors.text,
                    fontSize: "14px",
                    fontFamily: "inherit",
                    resize: "vertical",
                    outline: "none",
                    transition: theme.transitions.fast,
                  }}
                />

                <div style={{ display: "flex", gap: theme.spacing.sm }}>
                  <GlassButton
                    onClick={handleGenerateStrategy}
                    disabled={!nlInput.trim() || isGenerating}
                    style={{ flex: 1 }}
                  >
                    {isGenerating ? (
                      <>
                        <Loader2
                          className="animate-spin"
                          style={{ width: "18px", height: "18px" }}
                        />
                        Generating Strategy...
                      </>
                    ) : (
                      <>
                        <Sparkles style={{ width: "18px", height: "18px" }} />
                        Generate Strategy
                      </>
                    )}
                  </GlassButton>

                  {currentStrategy && (
                    <GlassButton
                      onClick={handleSaveStrategy}
                      variant="workflow"
                      workflowColor="strategyBuilder"
                    >
                      <Save style={{ width: "18px", height: "18px" }} />
                      Save Strategy
                    </GlassButton>
                  )}
                </div>
              </div>
            </GlassCard>

            {/* Stock Research Section */}
            <GlassCard>
              <h3
                style={{
                  fontSize: "18px",
                  fontWeight: "600",
                  color: theme.colors.text,
                  margin: `0 0 ${theme.spacing.md} 0`,
                  display: "flex",
                  alignItems: "center",
                  gap: theme.spacing.sm,
                }}
              >
                <Search style={{ width: "20px", height: "20px", color: theme.colors.info }} />
                Research Symbol
              </h3>

              <p
                style={{
                  color: theme.colors.textMuted,
                  margin: `0 0 ${theme.spacing.md} 0`,
                  fontSize: "14px",
                }}
              >
                Look up stock data and technical indicators before building your strategy
              </p>

              <div
                style={{
                  display: "flex",
                  gap: theme.spacing.sm,
                  marginBottom: showStockLookup ? theme.spacing.lg : 0,
                }}
              >
                <input
                  type="text"
                  value={researchSymbol}
                  onChange={(e) => setResearchSymbol(e.target.value.toUpperCase())}
                  placeholder="Enter symbol (e.g., AAPL, TSLA)"
                  style={{
                    flex: 1,
                    padding: theme.spacing.md,
                    background: theme.background.input,
                    border: `1px solid ${theme.colors.border}`,
                    borderRadius: theme.borderRadius.md,
                    color: theme.colors.text,
                    fontSize: "14px",
                    outline: "none",
                  }}
                />
                <GlassButton
                  onClick={() => {
                    if (researchSymbol.trim()) {
                      setShowStockLookup(true);
                    }
                  }}
                  disabled={!researchSymbol.trim()}
                >
                  <Search style={{ width: "18px", height: "18px" }} />
                  Research
                </GlassButton>
                {showStockLookup && (
                  <GlassButton variant="secondary" onClick={() => setShowStockLookup(false)}>
                    Close
                  </GlassButton>
                )}
              </div>

              {showStockLookup && researchSymbol.trim() && (
                <div
                  style={{
                    marginTop: theme.spacing.md,
                    padding: theme.spacing.lg,
                    background: theme.background.input,
                    border: `1px solid ${theme.colors.border}`,
                    borderRadius: theme.borderRadius.lg,
                  }}
                >
                  <StockLookup
                    initialSymbol={researchSymbol.trim()}
                    showChart={true}
                    showIndicators={true}
                    showCompanyInfo={true}
                    showNews={false}
                    enableAIAnalysis={true}
                    onSymbolSelect={(sym) => setResearchSymbol(sym)}
                  />
                </div>
              )}
            </GlassCard>

            {/* Generated Strategy Preview */}
            {currentStrategy && (
              <GlassCard>
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    marginBottom: theme.spacing.md,
                  }}
                >
                  <h3
                    style={{
                      fontSize: "18px",
                      fontWeight: "600",
                      color: theme.colors.text,
                      margin: 0,
                    }}
                  >
                    {currentStrategy.name}
                  </h3>
                  <GlassBadge variant="custom" customColor={accentColor}>
                    {currentStrategy.status}
                  </GlassBadge>
                </div>

                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: isMobile ? "1fr" : "1fr 1fr",
                    gap: theme.spacing.lg,
                  }}
                >
                  {/* Entry Rules */}
                  <div>
                    <h4
                      style={{
                        fontSize: "14px",
                        fontWeight: "600",
                        color: theme.colors.primary,
                        margin: `0 0 ${theme.spacing.sm} 0`,
                        textTransform: "uppercase",
                        letterSpacing: "0.5px",
                      }}
                    >
                      <Target
                        style={{
                          width: "16px",
                          height: "16px",
                          display: "inline",
                          marginRight: "6px",
                        }}
                      />
                      Entry Rules
                    </h4>
                    <div
                      style={{ display: "flex", flexDirection: "column", gap: theme.spacing.xs }}
                    >
                      {currentStrategy.entryRules?.map((rule, idx) => (
                        <div
                          key={idx}
                          style={{
                            padding: theme.spacing.sm,
                            background: `${theme.colors.primary}10`,
                            border: `1px solid ${theme.colors.primary}30`,
                            borderRadius: theme.borderRadius.sm,
                            fontSize: "13px",
                            color: theme.colors.text,
                          }}
                        >
                          {rule.indicator} {rule.operator} {rule.value}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Exit Rules */}
                  <div>
                    <h4
                      style={{
                        fontSize: "14px",
                        fontWeight: "600",
                        color: theme.colors.danger,
                        margin: `0 0 ${theme.spacing.sm} 0`,
                        textTransform: "uppercase",
                        letterSpacing: "0.5px",
                      }}
                    >
                      <Shield
                        style={{
                          width: "16px",
                          height: "16px",
                          display: "inline",
                          marginRight: "6px",
                        }}
                      />
                      Exit Rules
                    </h4>
                    <div
                      style={{ display: "flex", flexDirection: "column", gap: theme.spacing.xs }}
                    >
                      {currentStrategy.exitRules?.map((rule, idx) => (
                        <div
                          key={idx}
                          style={{
                            padding: theme.spacing.sm,
                            background: `${theme.colors.danger}10`,
                            border: `1px solid ${theme.colors.danger}30`,
                            borderRadius: theme.borderRadius.sm,
                            fontSize: "13px",
                            color: theme.colors.text,
                          }}
                        >
                          {rule.type === "take_profit" ? "Take Profit" : "Stop Loss"}: {rule.value}%
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Position Sizing & Risk */}
                <div
                  style={{
                    marginTop: theme.spacing.md,
                    padding: theme.spacing.md,
                    background: `${accentColor}10`,
                    border: `1px solid ${accentColor}30`,
                    borderRadius: theme.borderRadius.md,
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                    }}
                  >
                    <div>
                      <p style={{ fontSize: "12px", color: theme.colors.textMuted, margin: 0 }}>
                        Position Size
                      </p>
                      <p
                        style={{
                          fontSize: "16px",
                          fontWeight: "600",
                          color: theme.colors.text,
                          margin: 0,
                        }}
                      >
                        {currentStrategy.positionSizing?.value || 0}% of Portfolio
                      </p>
                    </div>
                    <div>
                      <p
                        style={{
                          fontSize: "12px",
                          color: theme.colors.textMuted,
                          margin: 0,
                          textAlign: "right",
                        }}
                      >
                        Max Drawdown
                      </p>
                      <p
                        style={{
                          fontSize: "16px",
                          fontWeight: "600",
                          color: theme.colors.text,
                          margin: 0,
                          textAlign: "right",
                        }}
                      >
                        {typeof currentStrategy.riskManagement === "object" &&
                        !Array.isArray(currentStrategy.riskManagement) &&
                        currentStrategy.riskManagement?.maxDrawdown
                          ? (currentStrategy.riskManagement.maxDrawdown * 100).toFixed(0)
                          : "0"}
                        %
                      </p>
                    </div>
                  </div>
                </div>
              </GlassCard>
            )}
          </>
        )}

        {/* Library View */}
        {view === "library" && (
          <>
            {/* Template Gallery Section */}
            <div>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  marginBottom: theme.spacing.md,
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: theme.spacing.sm }}>
                  <Award style={{ width: "24px", height: "24px", color: accentColor }} />
                  <h2
                    style={{
                      fontSize: "24px",
                      fontWeight: "600",
                      color: theme.colors.text,
                      margin: 0,
                    }}
                  >
                    Strategy Templates
                  </h2>
                </div>
                <div style={{ fontSize: "13px", color: theme.colors.textMuted }}>
                  Your Risk Tolerance:{" "}
                  <span style={{ color: accentColor, fontWeight: "600" }}>
                    {userRiskTolerance}%
                  </span>
                </div>
              </div>

              {/* Loading State */}
              {isLoadingTemplates && (
                <GlassCard>
                  <div style={{ textAlign: "center", padding: theme.spacing.xl }}>
                    <Loader2
                      className="animate-spin"
                      style={{
                        width: "48px",
                        height: "48px",
                        color: accentColor,
                        margin: "0 auto 16px",
                      }}
                    />
                    <p style={{ color: theme.colors.textMuted, margin: 0 }}>
                      Loading strategy templates...
                    </p>
                  </div>
                </GlassCard>
              )}

              {/* Error State */}
              {templatesError && !isLoadingTemplates && (
                <GlassCard
                  style={{
                    background: `${theme.colors.warning}10`,
                    border: `1px solid ${theme.colors.warning}40`,
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: theme.spacing.sm }}>
                    <AlertCircle
                      style={{ width: "20px", height: "20px", color: theme.colors.warning }}
                    />
                    <p style={{ margin: 0, color: theme.colors.warning }}>{templatesError}</p>
                  </div>
                </GlassCard>
              )}

              {/* Template Grid */}
              {!isLoadingTemplates && !templatesError && templates.length > 0 && (
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: isMobile ? "1fr" : "repeat(auto-fill, minmax(400px, 1fr))",
                    gap: theme.spacing.md,
                    marginBottom: theme.spacing.xl,
                  }}
                >
                  {templates.map((template) => {
                    const getRiskColor = (risk: string) => {
                      if (risk === "Conservative") return theme.workflow.activePositions;
                      if (risk === "Moderate") return theme.colors.warning;
                      return theme.colors.danger;
                    };

                    const getCompatibilityColor = (score: number) => {
                      if (score >= 80) return theme.workflow.activePositions;
                      if (score >= 60) return theme.colors.warning;
                      return theme.colors.textMuted;
                    };

                    return (
                      <GlassCard key={template.id} style={{ position: "relative" }}>
                        {/* Compatibility Badge */}
                        <div
                          style={{
                            position: "absolute",
                            top: theme.spacing.md,
                            right: theme.spacing.md,
                            padding: "6px 12px",
                            background: `${getCompatibilityColor(template.compatibility_score)}20`,
                            border: `1px solid ${getCompatibilityColor(template.compatibility_score)}`,
                            borderRadius: theme.borderRadius.md,
                            display: "flex",
                            alignItems: "center",
                            gap: "6px",
                          }}
                        >
                          <BarChart3
                            style={{
                              width: "14px",
                              height: "14px",
                              color: getCompatibilityColor(template.compatibility_score),
                            }}
                          />
                          <span
                            style={{
                              fontSize: "13px",
                              fontWeight: "600",
                              color: getCompatibilityColor(template.compatibility_score),
                            }}
                          >
                            {Math.round(template.compatibility_score)}% Match
                          </span>
                        </div>

                        {/* Template Header */}
                        <div style={{ marginBottom: theme.spacing.md, paddingRight: "100px" }}>
                          <h3
                            style={{
                              fontSize: "18px",
                              fontWeight: "600",
                              color: theme.colors.text,
                              margin: `0 0 ${theme.spacing.xs} 0`,
                            }}
                          >
                            {template.name}
                          </h3>
                          <GlassBadge
                            variant="custom"
                            customColor={getRiskColor(template.risk_level)}
                          >
                            {template.risk_level}
                          </GlassBadge>
                        </div>

                        {/* Description */}
                        <p
                          style={{
                            fontSize: "13px",
                            color: theme.colors.textMuted,
                            margin: `0 0 ${theme.spacing.md} 0`,
                            lineHeight: "1.5",
                          }}
                        >
                          {template.description}
                        </p>

                        {/* Performance Metrics */}
                        <div
                          style={{
                            display: "grid",
                            gridTemplateColumns: isMobile ? "1fr" : "1fr 1fr 1fr",
                            gap: theme.spacing.sm,
                            marginBottom: theme.spacing.md,
                            padding: theme.spacing.sm,
                            background: `${accentColor}10`,
                            borderRadius: theme.borderRadius.sm,
                          }}
                        >
                          <div>
                            <p
                              style={{ fontSize: "11px", color: theme.colors.textMuted, margin: 0 }}
                            >
                              Win Rate
                            </p>
                            <p
                              style={{
                                fontSize: "16px",
                                fontWeight: "600",
                                color: theme.colors.primary,
                                margin: 0,
                              }}
                            >
                              {template.expected_win_rate}%
                            </p>
                          </div>
                          <div>
                            <p
                              style={{ fontSize: "11px", color: theme.colors.textMuted, margin: 0 }}
                            >
                              Avg Return
                            </p>
                            <p
                              style={{
                                fontSize: "16px",
                                fontWeight: "600",
                                color: theme.workflow.activePositions,
                                margin: 0,
                              }}
                            >
                              {template.avg_return_percent > 0 ? "+" : ""}
                              {template.avg_return_percent}%
                            </p>
                          </div>
                          <div>
                            <p
                              style={{ fontSize: "11px", color: theme.colors.textMuted, margin: 0 }}
                            >
                              Max DD
                            </p>
                            <p
                              style={{
                                fontSize: "16px",
                                fontWeight: "600",
                                color: theme.colors.danger,
                                margin: 0,
                              }}
                            >
                              -{template.max_drawdown_percent}%
                            </p>
                          </div>
                        </div>

                        {/* Recommended For */}
                        {template.recommended_for && template.recommended_for.length > 0 && (
                          <div style={{ marginBottom: theme.spacing.md }}>
                            <p
                              style={{
                                fontSize: "11px",
                                color: theme.colors.textMuted,
                                margin: `0 0 ${theme.spacing.xs} 0`,
                                textTransform: "uppercase",
                                letterSpacing: "0.5px",
                              }}
                            >
                              Best For
                            </p>
                            <div
                              style={{ display: "flex", flexWrap: "wrap", gap: theme.spacing.xs }}
                            >
                              {template.recommended_for.map((rec, idx) => (
                                <span
                                  key={idx}
                                  style={{
                                    fontSize: "12px",
                                    padding: "4px 8px",
                                    background: `${theme.colors.info}20`,
                                    border: `1px solid ${theme.colors.info}40`,
                                    borderRadius: theme.borderRadius.sm,
                                    color: theme.colors.info,
                                  }}
                                >
                                  {rec}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Clone Buttons */}
                        <div style={{ display: "flex", gap: theme.spacing.sm }}>
                          <GlassButton
                            onClick={() => handleCloneTemplate(template)}
                            variant="secondary"
                            style={{ flex: 1 }}
                          >
                            <Copy style={{ width: "16px", height: "16px" }} />
                            Quick Clone
                          </GlassButton>
                          <GlassButton
                            onClick={() => {
                              setSelectedTemplate(template);
                              setShowCustomizationModal(true);
                            }}
                            variant="workflow"
                            workflowColor="strategyBuilder"
                            style={{ flex: 1 }}
                          >
                            <Edit3 style={{ width: "16px", height: "16px" }} />
                            Customize
                          </GlassButton>
                        </div>
                      </GlassCard>
                    );
                  })}
                </div>
              )}
            </div>

            {/* My Strategies Section */}
            <div>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: theme.spacing.sm,
                  marginBottom: theme.spacing.md,
                }}
              >
                <Code2 style={{ width: "24px", height: "24px", color: accentColor }} />
                <h2
                  style={{
                    fontSize: "24px",
                    fontWeight: "600",
                    color: theme.colors.text,
                    margin: 0,
                  }}
                >
                  My Strategies
                </h2>
              </div>

              {savedStrategies.length === 0 ? (
                <GlassCard>
                  <div style={{ textAlign: "center", padding: theme.spacing.xl }}>
                    <Brain
                      style={{
                        width: "64px",
                        height: "64px",
                        color: theme.colors.textMuted,
                        margin: "0 auto 16px",
                      }}
                    />
                    <h3 style={{ color: theme.colors.text, margin: `0 0 ${theme.spacing.sm} 0` }}>
                      No Custom Strategies Yet
                    </h3>
                    <p
                      style={{ color: theme.colors.textMuted, margin: `0 0 ${theme.spacing.md} 0` }}
                    >
                      Clone a template above or create your own from scratch
                    </p>
                    <GlassButton onClick={() => setView("create")}>
                      <Sparkles style={{ width: "18px", height: "18px" }} />
                      Create Strategy
                    </GlassButton>
                  </div>
                </GlassCard>
              ) : (
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: isMobile ? "1fr" : "repeat(auto-fill, minmax(350px, 1fr))",
                    gap: theme.spacing.md,
                  }}
                >
                  {savedStrategies.map((strategy) => (
                    <GlassCard key={strategy.id}>
                      <div style={{ marginBottom: theme.spacing.md }}>
                        <div
                          style={{
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "space-between",
                            marginBottom: theme.spacing.sm,
                          }}
                        >
                          <h3
                            style={{
                              fontSize: "18px",
                              fontWeight: "600",
                              color: theme.colors.text,
                              margin: 0,
                            }}
                          >
                            {strategy.name}
                          </h3>
                          <GlassBadge
                            variant="custom"
                            customColor={
                              strategy.status === "active"
                                ? theme.colors.primary
                                : strategy.status === "testing"
                                  ? theme.colors.warning
                                  : theme.colors.textMuted
                            }
                          >
                            {strategy.status}
                          </GlassBadge>
                        </div>

                        <p style={{ fontSize: "12px", color: theme.colors.textMuted, margin: 0 }}>
                          Created{" "}
                          {strategy.createdAt
                            ? new Date(strategy.createdAt).toLocaleDateString()
                            : "Unknown"}
                        </p>
                      </div>

                      {strategy.aiPrompt && (
                        <p
                          style={{
                            fontSize: "13px",
                            color: theme.colors.textMuted,
                            margin: `0 0 ${theme.spacing.md} 0`,
                            fontStyle: "italic",
                            overflow: "hidden",
                            textOverflow: "ellipsis",
                            display: "-webkit-box",
                            WebkitLineClamp: 2,
                            WebkitBoxOrient: "vertical",
                          }}
                        >
                          &quot;{strategy.aiPrompt}&quot;
                        </p>
                      )}

                      <div
                        style={{
                          display: "grid",
                          gridTemplateColumns: isMobile ? "1fr" : "1fr 1fr",
                          gap: theme.spacing.sm,
                          marginBottom: theme.spacing.md,
                          padding: theme.spacing.sm,
                          background: `${accentColor}10`,
                          borderRadius: theme.borderRadius.sm,
                        }}
                      >
                        <div>
                          <p style={{ fontSize: "11px", color: theme.colors.textMuted, margin: 0 }}>
                            Entry Rules
                          </p>
                          <p
                            style={{
                              fontSize: "16px",
                              fontWeight: "600",
                              color: theme.colors.primary,
                              margin: 0,
                            }}
                          >
                            {strategy.entryRules?.length || 0}
                          </p>
                        </div>
                        <div>
                          <p style={{ fontSize: "11px", color: theme.colors.textMuted, margin: 0 }}>
                            Exit Rules
                          </p>
                          <p
                            style={{
                              fontSize: "16px",
                              fontWeight: "600",
                              color: theme.colors.danger,
                              margin: 0,
                            }}
                          >
                            {strategy.exitRules?.length || 0}
                          </p>
                        </div>
                      </div>

                      {strategy.backtestResults && (
                        <div
                          style={{
                            marginBottom: theme.spacing.md,
                            padding: theme.spacing.sm,
                            background: `${theme.colors.primary}10`,
                            borderRadius: theme.borderRadius.sm,
                          }}
                        >
                          <p
                            style={{
                              fontSize: "11px",
                              color: theme.colors.textMuted,
                              margin: `0 0 4px 0`,
                            }}
                          >
                            Backtest Results
                          </p>
                          <div style={{ display: "flex", justifyContent: "space-between" }}>
                            <span style={{ fontSize: "13px", color: theme.colors.text }}>
                              Win Rate: {strategy.backtestResults.winRate}%
                            </span>
                            <span style={{ fontSize: "13px", color: theme.colors.text }}>
                              Trades: {strategy.backtestResults.totalTrades}
                            </span>
                          </div>
                        </div>
                      )}

                      <div style={{ display: "flex", gap: theme.spacing.sm }}>
                        <GlassButton
                          onClick={() => handleEditStrategy(strategy)}
                          variant="secondary"
                          style={{ flex: 1 }}
                        >
                          <Edit3 style={{ width: "16px", height: "16px" }} />
                          Edit
                        </GlassButton>
                        <GlassButton
                          onClick={() => handleActivateStrategy(strategy.id)}
                          variant="workflow"
                          workflowColor={strategy.status === "active" ? "settings" : "execute"}
                          style={{ flex: 1 }}
                        >
                          <Play style={{ width: "16px", height: "16px" }} />
                          {strategy.status === "active" ? "Pause" : "Activate"}
                        </GlassButton>
                        <GlassButton
                          onClick={() => handleDeleteStrategy(strategy.id)}
                          variant="danger"
                        >
                          <Trash2 style={{ width: "16px", height: "16px" }} />
                        </GlassButton>
                      </div>
                    </GlassCard>
                  ))}
                </div>
              )}
            </div>
          </>
        )}
      </div>

      {/* Template Customization Modal */}
      {showCustomizationModal && (
        <TemplateCustomizationModal
          template={selectedTemplate}
          onClose={() => {
            setShowCustomizationModal(false);
            setSelectedTemplate(null);
          }}
          onCloneSuccess={() => {
            fetchTemplates(); // Refresh templates after cloning
          }}
        />
      )}
    </div>
  );
}
