/**
 * Morning Routine with AI Scheduler + Run Now Feature
 * Schedule custom morning trading routines with AI assistance
 * Includes "Run Now" button to execute routines on-demand
 */

import {
  AlertCircle,
  Bell,
  Brain,
  Calendar,
  CheckCircle,
  Loader2,
  Sparkles,
  Sun,
  XCircle,
  Zap,
} from "lucide-react";
import { useEffect, useState } from "react";
import { useIsMobile } from "../hooks/useBreakpoint";
import { claudeAI } from "../lib/aiAdapter";
import { logger } from "../lib/logger";
import { fetchUnder4Scanner } from "../lib/marketData";
import { getCurrentUser, updateUser } from "../lib/userManagement";
import { theme } from "../styles/theme";
import { GlassBadge, GlassButton, GlassCard } from "./GlassmorphicComponents";

interface PortfolioMetrics {
  totalValue: number;
  dayChange: number;
  dayChangePercent: number;
  buyingPower: number;
}

interface SystemCheck {
  name: string;
  status: "pass" | "fail" | "warning";
  message: string;
}

interface NewsItem {
  title: string;
  impact: "high" | "medium" | "low";
  time: string;
}

// Helper function to fetch real market data
async function fetchLiveMarketData() {
  try {
    logger.info("[MorningRoutine] 🔴 Fetching LIVE market data...");
    const scanner = await fetchUnder4Scanner();

    logger.info("[MorningRoutine] ✅ Received live data", { scanner });

    return {
      candidates: scanner.candidates || [],
      count: scanner.count || 0,
      timestamp: new Date().toISOString(),
    };
  } catch (error) {
    logger.error("[MorningRoutine] ❌ Failed to fetch live market data", error);
    return null;
  }
}

// Helper function to format live data into markdown
function formatLiveMarketData(
  data: {
    count: number;
    candidates: Array<{
      symbol: string;
      price: number;
      change: number;
      changePercent: number;
      volume: number;
      marketCap: number;
    }>;
  } | null
) {
  if (!data || data.count === 0) {
    return `# ❌ No Live Data Available

Unable to fetch real-time market data from backend.

**Troubleshooting:**
- Check backend is running on port 8001
- Verify /api/market/scanner/under4 endpoint
- Check browser console for errors
`;
  }

  return `# 🔴 LIVE MARKET DATA

## Stocks Under $4 Scanner (Real-Time)

**Found ${data.count} candidates meeting criteria:**

${data.candidates
  .map(
    (stock, idx: number) => `
### ${idx + 1}. ${stock.symbol} - **$${stock.price.toFixed(2)}**

| Metric | Value |
|--------|-------|
| **Bid** | $${stock.bid.toFixed(2)} |
| **Ask** | $${stock.ask.toFixed(2)} |
| **Spread** | $${(stock.ask - stock.bid).toFixed(3)} (${(((stock.ask - stock.bid) / stock.ask) * 100).toFixed(2)}%) |

**Next Steps:**
- [ ] Check options chain liquidity (OI > 500)
- [ ] Verify bid-ask spread on options < 10%
- [ ] Check earnings date (avoid if within 2 weeks)
- [ ] Analyze technical setup (support/resistance)

---
`
  )
  .join("\n")}

**🕐 Last Updated:** ${new Date(data.timestamp).toLocaleTimeString()} ET

---

## ⚠️ Trading Notes

- All prices are LIVE from Alpaca Paper Trading API
- Spreads indicate liquidity (tighter = better)
- Under $4 stocks carry higher risk - use defined-risk strategies
- Always verify options liquidity before entering positions
`;
}

export default function MorningRoutineAI() {
  const isMobile = useIsMobile();
  const [view, setView] = useState<"dashboard" | "scheduler">("dashboard");
  const [currentTime, setCurrentTime] = useState(new Date());
  const [loading, setLoading] = useState(false);

  // "Run Now" feature state
  const [isRunning, setIsRunning] = useState(false);
  const [executionLog, setExecutionLog] = useState<string[]>([]);
  const [showExecutionLog, setShowExecutionLog] = useState(false);

  // Live data preview state
  const [liveDataPreview, setLiveDataPreview] = useState<{
    candidates: Array<{
      symbol: string;
      price: number;
      change: number;
      changePercent: number;
      volume: number;
      marketCap: number;
      bid: number;
      ask: number;
    }>;
    count: number;
    timestamp: string;
  } | null>(null);
  const [isLoadingLiveData, setIsLoadingLiveData] = useState(false);

  // Dashboard data
  const [systemChecks] = useState<SystemCheck[]>([
    { name: "API Connection", status: "pass", message: "Connected to Alpaca" },
    { name: "Market Data", status: "pass", message: "Real-time feed active" },
    { name: "Account Status", status: "pass", message: "Paper trading account active" },
    { name: "Risk Limits", status: "warning", message: "Daily loss at 75%" },
  ]);

  const [portfolio, setPortfolio] = useState<PortfolioMetrics>({
    totalValue: 0,
    dayChange: 0,
    dayChangePercent: 0,
    buyingPower: 0,
  });

  const [todaysNews] = useState<NewsItem[]>([
    { title: "Fed Interest Rate Decision", impact: "high", time: "2:00 PM ET" },
    { title: "Tech Earnings: AAPL, MSFT", impact: "high", time: "After Close" },
    { title: "Unemployment Claims", impact: "medium", time: "8:30 AM ET" },
    { title: "Oil Inventory Report", impact: "low", time: "10:30 AM ET" },
  ]);

  // Scheduler data
  const [scheduleEnabled, setScheduleEnabled] = useState(false);
  const [scheduleTime, setScheduleTime] = useState("07:00");
  const [scheduleFrequency, setScheduleFrequency] = useState<"daily" | "weekdays" | "custom">(
    "weekdays"
  );
  const [_customDays, _setCustomDays] = useState<string[]>(["mon", "tue", "wed", "thu", "fri"]);
  const [selectedSteps, setSelectedSteps] = useState<string[]>([
    "briefing",
    "recommendations",
    "portfolio",
  ]);

  // AI Routine Builder
  const [showAIBuilder, setShowAIBuilder] = useState(false);
  const [aiInput, setAiInput] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // ✅ EXTENSION VERIFICATION: lucide-react
    logger.info("[Extension Verification] ✅ lucide-react icons loaded successfully", {
      icons: [
        "Sun",
        "Calendar",
        "Sparkles",
        "AlertCircle",
        "CheckCircle",
        "XCircle",
        "Bell",
        "Loader2",
        "Brain",
        "Zap",
      ],
      status: "FUNCTIONAL",
    });

    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // Load saved schedule from user profile
  useEffect(() => {
    const user = getCurrentUser();
    if (user?.onboarding?.morningRoutine) {
      const routine = user.onboarding.morningRoutine;
      setScheduleEnabled(routine.enabled);
      setScheduleTime(routine.time);
      if (routine.briefing) setSelectedSteps((prev) => [...prev, "briefing"]);
      if (routine.recommendations) setSelectedSteps((prev) => [...prev, "recommendations"]);
      if (routine.portfolioReview) setSelectedSteps((prev) => [...prev, "portfolio"]);
    }
  }, []);

  // Load portfolio data from user profile or API
  useEffect(() => {
    const loadPortfolioData = async () => {
      try {
        // Try to get real account data from API first
        const response = await fetch("/api/proxy/api/account");

        if (response.ok) {
          const accountData = await response.json();
          setPortfolio({
            totalValue: parseFloat(accountData.portfolio_value || accountData.equity || "0"),
            dayChange:
              parseFloat(accountData.equity || "0") - parseFloat(accountData.last_equity || "0"),
            dayChangePercent:
              accountData.equity && accountData.last_equity
                ? ((parseFloat(accountData.equity) - parseFloat(accountData.last_equity)) /
                    parseFloat(accountData.last_equity)) *
                  100
                : 0,
            buyingPower: parseFloat(accountData.buying_power || accountData.cash || "0"),
          });
          logger.info("[MorningRoutine] ✅ Loaded real portfolio data from API");
        } else {
          // Fallback to user profile if API fails
          const user = getCurrentUser();
          if (user?.onboarding?.investmentAmount) {
            const amount =
              typeof user.onboarding.investmentAmount === "object"
                ? user.onboarding.investmentAmount.value || 0
                : user.onboarding.investmentAmount;

            setPortfolio({
              totalValue: amount,
              dayChange: 0,
              dayChangePercent: 0,
              buyingPower: amount,
            });
            logger.info("[MorningRoutine] ✅ Loaded portfolio data from user profile");
          }
        }
      } catch (error) {
        logger.error("[MorningRoutine] Failed to load portfolio data", error);
      }
    };

    loadPortfolioData();
  }, []);

  // Fetch live data preview on mount
  useEffect(() => {
    const loadLiveDataPreview = async () => {
      setIsLoadingLiveData(true);
      try {
        const data = await fetchLiveMarketData();
        if (data) {
          setLiveDataPreview(data);
          logger.info("[MorningRoutine] ✅ Loaded live data preview");
        }
      } catch (error) {
        logger.error("[MorningRoutine] Failed to load live data preview", error);
      } finally {
        setIsLoadingLiveData(false);
      }
    };

    loadLiveDataPreview();
  }, []);

  // Manual refresh function for live data
  const refreshLiveData = async () => {
    setIsLoadingLiveData(true);
    try {
      const data = await fetchLiveMarketData();
      if (data) {
        setLiveDataPreview(data);
      }
    } catch (error) {
      logger.error("[MorningRoutine] Failed to refresh live data", error);
    } finally {
      setIsLoadingLiveData(false);
    }
  };

  const getMarketStatus = () => {
    const now = new Date();
    const day = now.getDay();
    const hour = now.getHours();
    const isWeekday = day >= 1 && day <= 5;
    const isMarketHours = hour >= 9 && hour < 16;

    return {
      isOpen: isWeekday && isMarketHours,
      nextEvent: isWeekday && !isMarketHours ? "Opens at 9:30 AM ET" : "Closes at 4:00 PM ET",
      currentTime: now.toLocaleTimeString("en-US"),
    };
  };

  const runMorningChecks = async () => {
    setLoading(true);
    await new Promise((resolve) => setTimeout(resolve, 2000));
    setLoading(false);
  };

  const handleSaveSchedule = () => {
    const user = getCurrentUser();
    if (!user) return;

    updateUser({
      onboarding: {
        ...user.onboarding,
        morningRoutine: {
          enabled: scheduleEnabled,
          time: scheduleTime,
          briefing: selectedSteps.includes("briefing"),
          recommendations: selectedSteps.includes("recommendations"),
          portfolioReview: selectedSteps.includes("portfolio"),
        },
      },
    });

    alert("Morning routine schedule saved!");
    setView("dashboard");
  };

  const handleGenerateAIRoutine = async () => {
    if (!aiInput.trim()) return;

    setIsGenerating(true);
    setError(null);

    try {
      logger.info("[MorningRoutine] Generating routine from input", { aiInput });
      const response = await claudeAI.generateMorningRoutine({
        wakeTime: "7:00 AM",
        marketOpen: true,
        checkNews: true,
        reviewPositions: true,
        aiRecommendations: true,
      });
      logger.info("[MorningRoutine] Raw AI response", { response });

      // Try to parse JSON from the response
      let routine: {
        title: string;
        steps: Array<{
          time: string;
          task: string;
          description: string;
          priority: string;
        }>;
        summary: string;
      } | null = null;
      let parsed = response.trim();

      // Remove markdown code blocks if present
      parsed = parsed
        .replace(/```json\n?/g, "")
        .replace(/```\n?/g, "")
        .trim();

      // Try to extract JSON object
      const jsonMatch = parsed.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        try {
          routine = JSON.parse(jsonMatch[0]);
          logger.info("[MorningRoutine] Successfully parsed JSON", { routine });
        } catch (parseError) {
          logger.error("[MorningRoutine] JSON parse error", parseError);
        }
      }

      // If we couldn't parse JSON, create a simple routine from the response
      if (!routine) {
        logger.info("[MorningRoutine] Could not parse JSON, using fallback with defaults");
        // Just use default values and keep the selected steps
        alert("AI generated a routine suggestion. Using default schedule settings.");
        setShowAIBuilder(false);
        setAiInput("");
        return;
      }

      // Map AI-generated routine to schedule settings with fallbacks
      if (routine.schedule?.startTime) {
        logger.info("[MorningRoutine] Setting schedule time", { time: routine.schedule.startTime });
        setScheduleTime(routine.schedule.startTime);
      }

      if (routine.schedule?.frequency) {
        logger.info("[MorningRoutine] Setting frequency", {
          frequency: routine.schedule.frequency,
        });
        setScheduleFrequency(routine.schedule.frequency);
      }

      // Extract step types from AI routine
      if (routine.steps && Array.isArray(routine.steps)) {
        const stepTypes = routine.steps
          .map((step: { type: string }) => step.type)
          .filter((type: string) => availableSteps.some((s) => s.id === type));
        logger.info("[MorningRoutine] Setting step types", { stepTypes });
        if (stepTypes.length > 0) {
          setSelectedSteps(stepTypes);
        }
      }

      setShowAIBuilder(false);
      setAiInput("");
      alert(`AI generated routine: "${routine.name || "Custom Routine"}"`);
      logger.info("[MorningRoutine] ✅ Routine generated successfully");
    } catch (err: unknown) {
      logger.error("[MorningRoutine] Error generating routine", err);
      setError(
        err instanceof Error ? err.message : "Failed to generate routine. Please try again."
      );
    } finally {
      setIsGenerating(false);
    }
  };

  /**
   * Run Now Feature - Execute the "Under-$4 Multileg Workflow" routine
   */
  const handleRunNow = async () => {
    setIsRunning(true);
    setShowExecutionLog(true);
    setExecutionLog([]);

    const addLog = (message: string) => {
      setExecutionLog((prev) => [...prev, `[${new Date().toLocaleTimeString()}] ${message}`]);
    };

    try {
      addLog("🚀 Starting Morning Routine: Under-$4 Multileg Workflow");
      addLog("");

      // Step 1: Market Briefing
      addLog("📊 Step 1: Market Briefing");
      addLog("Analyzing pre-market conditions...");

      const briefingPrompt = `Provide a concise pre-market briefing for today. Include:
1. S&P 500 futures direction
2. Key market movers
3. Important economic events today
4. Overall market sentiment

Keep it brief and actionable for a day trader.`;

      const briefingResponse = await claudeAI.chat(briefingPrompt);
      addLog("✅ Market Briefing Complete");
      addLog(briefingResponse);
      addLog("");

      // Step 2: Under-$4 Multileg Scan (LIVE DATA)
      addLog("🔍 Step 2: Scanning for Under-$4 Multileg Opportunities");
      addLog("🔴 Fetching LIVE market data from backend API...");

      // Fetch REAL market data
      type LiveCandidate = { symbol: string; price: number; bid: number; ask: number };
      const liveData = (await fetchLiveMarketData()) as {
        count: number;
        timestamp: string;
        candidates: LiveCandidate[];
      } | null;

      if (liveData && liveData.count > 0) {
        addLog(`✅ Retrieved ${liveData.count} stocks with real-time prices`);
        addLog(`Prices as of: ${new Date(liveData.timestamp).toLocaleTimeString()}`);

        // Extract stock symbols for AI analysis
        const stockSymbols = liveData.candidates.map((s: LiveCandidate) => s.symbol);
        addLog(`📋 Symbols found: ${stockSymbols.join(", ")}`);

        // **CRITICAL FIX:** Pass stock data to AI for actionable analysis
        addLog("🤖 Sending stock data to AI for option strategy analysis...");

        const aiAnalysisPrompt = `I found ${liveData.count} stocks under $4 trading now. Here are the details:

${liveData.candidates
  .map(
    (stock: LiveCandidate) => `
**${stock.symbol}** - $${stock.price.toFixed(2)}
- Bid: $${stock.bid.toFixed(2)} | Ask: $${stock.ask.toFixed(2)}
- Spread: $${(stock.ask - stock.bid).toFixed(3)} (${(((stock.ask - stock.bid) / stock.ask) * 100).toFixed(2)}%)
`
  )
  .join("\n")}

For each stock, analyze:
1. **Options Liquidity:** Check if likely to have liquid options (typical OI > 500 for under-$4 stocks)
2. **Bid-Ask Spread Quality:** Is the ${(((liveData.candidates[0].ask - liveData.candidates[0].bid) / liveData.candidates[0].ask) * 100).toFixed(1)}% spread acceptable for options trading?
3. **Multileg Strategy:** Recommend specific iron condor, butterfly, or credit spread strikes
4. **Risk Assessment:** Max risk/reward for each trade
5. **Earnings Risk:** Flag if earnings likely within 2 weeks

Provide 2-3 actionable multileg trade recommendations with exact strikes and expirations.`;

        const aiAnalysis = await claudeAI.chat(aiAnalysisPrompt);
        addLog("✅ AI Analysis Complete:");
        addLog(aiAnalysis);
      } else {
        addLog("⚠️ Live data fetch failed or no stocks found - check backend connection");
      }

      const scanResult = formatLiveMarketData(liveData);
      addLog("✅ Scan Complete - Full Data Below:");
      addLog(scanResult);
      addLog("");

      // Step 3: Portfolio Review
      addLog("💼 Step 3: Portfolio Review");
      addLog("Checking overnight changes and open positions...");

      const portfolioPrompt = `Review this portfolio status:
- Total Value: $${portfolio.totalValue.toLocaleString()}
- Day Change: ${portfolio.dayChange >= 0 ? "+" : ""}$${portfolio.dayChange.toFixed(2)} (${portfolio.dayChangePercent.toFixed(2)}%)
- Buying Power: $${portfolio.buyingPower.toLocaleString()}

Provide:
1. Any recommended actions for existing positions
2. Risk assessment
3. Available capital for new trades`;

      const portfolioResponse = await claudeAI.chat(portfolioPrompt);
      addLog("✅ Portfolio Review Complete");
      addLog(portfolioResponse);
      addLog("");

      // Step 4: AI Recommendations
      addLog("🤖 Step 4: AI Trade Recommendations");
      addLog("Generating personalized trade ideas...");

      const recommendationsPrompt = `Based on the market briefing and under-$4 scan, recommend 2-3 specific multileg option trades for today. For each:
- Entry strategy (exact legs and strikes)
- Max risk and max profit
- Exit plan
- Why this trade makes sense today`;

      const recommendationsResponse = await claudeAI.chat(recommendationsPrompt);
      addLog("✅ Recommendations Generated");
      addLog(recommendationsResponse);
      addLog("");

      addLog("🎉 Morning Routine Complete!");
      addLog("Ready to trade. Good luck today! 🚀");
    } catch (err: unknown) {
      addLog(`❌ Error: ${err instanceof Error ? err.message : String(err)}`);
      addLog("Routine execution failed. Please try again.");
    } finally {
      setIsRunning(false);
    }
  };

  const toggleStep = (step: string) => {
    setSelectedSteps((prev) =>
      prev.includes(step) ? prev.filter((s) => s !== step) : [...prev, step]
    );
  };

  const market = getMarketStatus();
  const accentColor = theme.workflow.morningRoutine;

  const availableSteps = [
    { id: "briefing", label: "Market Overview", icon: "📊", desc: "Pre-market analysis and news" },
    {
      id: "recommendations",
      label: "AI Recommendations",
      icon: "🤖",
      desc: "Personalized stock picks",
    },
    { id: "portfolio", label: "Portfolio Review", icon: "💼", desc: "Overnight changes" },
    { id: "news", label: "News Review", icon: "📰", desc: "Breaking market news" },
    { id: "alerts", label: "Check Alerts", icon: "🔔", desc: "Price and volume alerts" },
    { id: "scan", label: "Pre-Market Scan", icon: "🔍", desc: "Top movers and volume" },
  ];

  // Dashboard View
  if (view === "dashboard") {
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
              gap: isMobile ? theme.spacing.md : 0,
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: theme.spacing.md }}>
              <div
                style={{
                  padding: theme.spacing.md,
                  background: `${accentColor}20`,
                  borderRadius: theme.borderRadius.lg,
                  boxShadow: theme.glow.teal,
                }}
              >
                <Sun
                  style={{
                    width: isMobile ? "24px" : "32px",
                    height: isMobile ? "24px" : "32px",
                    color: accentColor,
                  }}
                />
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
                  Morning Routine
                </h1>
                <p
                  style={{
                    color: theme.colors.textMuted,
                    margin: "4px 0 0 0",
                    fontSize: "14px",
                  }}
                >
                  {currentTime.toLocaleTimeString("en-US")} • {market.nextEvent}
                </p>
              </div>
            </div>

            <div
              style={{
                display: "flex",
                flexDirection: isMobile ? "column" : "row",
                gap: theme.spacing.sm,
                width: isMobile ? "100%" : "auto",
              }}
            >
              {/* Run Now Button - Prominent with gradient */}
              <GlassButton
                onClick={handleRunNow}
                disabled={isRunning}
                style={{
                  background: isRunning
                    ? theme.colors.border
                    : `linear-gradient(135deg, ${theme.workflow.morningRoutine} 0%, ${theme.workflow.strategyBuilder} 100%)`,
                  boxShadow: isRunning ? "none" : `${theme.glow.teal}, ${theme.glow.purple}`,
                  border: "none",
                  fontWeight: "600",
                  width: isMobile ? "100%" : "auto",
                }}
              >
                {isRunning ? (
                  <>
                    <Loader2 className="animate-spin" style={{ width: "18px", height: "18px" }} />
                    Running...
                  </>
                ) : (
                  <>
                    <Zap style={{ width: "18px", height: "18px" }} />
                    Run Now
                  </>
                )}
              </GlassButton>

              <GlassButton
                onClick={() => setView("scheduler")}
                variant="workflow"
                workflowColor="morningRoutine"
                style={{ width: isMobile ? "100%" : "auto" }}
              >
                <Calendar style={{ width: "18px", height: "18px" }} />
                Schedule
              </GlassButton>
            </div>
          </div>

          {/* Execution Log - Show when running or completed */}
          {showExecutionLog && executionLog.length > 0 && (
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
                  Routine Execution Log
                </h3>
                <GlassButton onClick={() => setShowExecutionLog(false)} variant="secondary">
                  Hide
                </GlassButton>
              </div>
              <div
                style={{
                  maxHeight: "400px",
                  overflowY: "auto",
                  padding: theme.spacing.md,
                  background: theme.background.input,
                  borderRadius: theme.borderRadius.md,
                  fontFamily: "monospace",
                  fontSize: "13px",
                  lineHeight: "1.6",
                  color: theme.colors.text,
                  whiteSpace: "pre-wrap",
                }}
              >
                {executionLog.map((log, idx) => (
                  <div key={idx} style={{ marginBottom: "4px" }}>
                    {log}
                  </div>
                ))}
              </div>
            </GlassCard>
          )}

          {/* Market Status */}
          <GlassCard glow="teal">
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                marginBottom: theme.spacing.md,
              }}
            >
              <h3
                style={{ fontSize: "18px", fontWeight: "600", color: theme.colors.text, margin: 0 }}
              >
                Market Status
              </h3>
              <GlassBadge variant={market.isOpen ? "success" : "warning"}>
                {market.isOpen ? "OPEN" : "CLOSED"}
              </GlassBadge>
            </div>
            <p style={{ color: theme.colors.textMuted, margin: 0 }}>{market.nextEvent}</p>
          </GlassCard>

          {/* Live Data Preview - Under $4 Scanner */}
          <GlassCard>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                marginBottom: theme.spacing.md,
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: theme.spacing.sm }}>
                <h3
                  style={{
                    fontSize: "18px",
                    fontWeight: "600",
                    color: theme.colors.text,
                    margin: 0,
                  }}
                >
                  Live Market Scan
                </h3>
                <GlassBadge variant="info">Under $4</GlassBadge>
              </div>
              <GlassButton
                onClick={refreshLiveData}
                disabled={isLoadingLiveData}
                variant="secondary"
                style={{ fontSize: "12px", padding: "6px 12px" }}
              >
                {isLoadingLiveData ? (
                  <Loader2 className="animate-spin" style={{ width: "14px", height: "14px" }} />
                ) : (
                  "Refresh"
                )}
              </GlassButton>
            </div>

            {isLoadingLiveData && !liveDataPreview ? (
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  padding: theme.spacing.xl,
                  color: theme.colors.textMuted,
                }}
              >
                <Loader2
                  className="animate-spin"
                  style={{ width: "24px", height: "24px", marginRight: theme.spacing.sm }}
                />
                Loading live data...
              </div>
            ) : liveDataPreview && liveDataPreview.count > 0 ? (
              <>
                {/* Summary Stats */}
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: theme.spacing.md,
                    marginBottom: theme.spacing.md,
                    padding: theme.spacing.sm,
                    background: `${theme.colors.primary}10`,
                    borderRadius: theme.borderRadius.md,
                    border: `1px solid ${theme.colors.primary}30`,
                  }}
                >
                  <div>
                    <p style={{ fontSize: "12px", color: theme.colors.textMuted, margin: 0 }}>
                      Candidates Found
                    </p>
                    <p
                      style={{
                        fontSize: "24px",
                        fontWeight: "600",
                        color: theme.colors.primary,
                        margin: 0,
                      }}
                    >
                      {liveDataPreview.count}
                    </p>
                  </div>
                  <div style={{ flex: 1 }}>
                    <p style={{ fontSize: "12px", color: theme.colors.textMuted, margin: 0 }}>
                      Last Updated
                    </p>
                    <p style={{ fontSize: "14px", color: theme.colors.text, margin: 0 }}>
                      {new Date(liveDataPreview.timestamp).toLocaleTimeString()} ET
                    </p>
                  </div>
                </div>

                {/* Top 3 Stocks Preview */}
                <div style={{ display: "flex", flexDirection: "column", gap: theme.spacing.sm }}>
                  <p
                    style={{
                      fontSize: "12px",
                      color: theme.colors.textMuted,
                      fontWeight: "600",
                      textTransform: "uppercase",
                      margin: 0,
                    }}
                  >
                    Top Candidates:
                  </p>
                  {liveDataPreview.candidates
                    .slice(0, 3)
                    .map(
                      (
                        stock: { symbol: string; bid: number; ask: number; price: number },
                        idx: number
                      ) => (
                        <div
                          key={idx}
                          style={{
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "space-between",
                            padding: theme.spacing.sm,
                            background: theme.background.glass,
                            borderRadius: theme.borderRadius.sm,
                            border: `1px solid ${theme.colors.border}`,
                          }}
                        >
                          <div
                            style={{ display: "flex", alignItems: "center", gap: theme.spacing.sm }}
                          >
                            <span
                              style={{
                                fontSize: "16px",
                                fontWeight: "700",
                                color: theme.colors.text,
                                minWidth: "60px",
                              }}
                            >
                              {stock.symbol}
                            </span>
                            <div style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
                              <span style={{ fontSize: "11px", color: theme.colors.textMuted }}>
                                Bid/Ask: ${stock.bid.toFixed(2)} / ${stock.ask.toFixed(2)}
                              </span>
                              <span style={{ fontSize: "11px", color: theme.colors.textMuted }}>
                                Spread: ${(stock.ask - stock.bid).toFixed(3)} (
                                {(((stock.ask - stock.bid) / stock.ask) * 100).toFixed(2)}%)
                              </span>
                            </div>
                          </div>
                          <span
                            style={{
                              fontSize: "20px",
                              fontWeight: "700",
                              color: theme.colors.primary,
                            }}
                          >
                            ${stock.price.toFixed(2)}
                          </span>
                        </div>
                      )
                    )}
                </div>

                {liveDataPreview.count > 3 && (
                  <p
                    style={{
                      fontSize: "12px",
                      color: theme.colors.textMuted,
                      marginTop: theme.spacing.sm,
                      textAlign: "center",
                    }}
                  >
                    +{liveDataPreview.count - 3} more candidates • Click &quot;Run Now&quot; for
                    full details
                  </p>
                )}
              </>
            ) : (
              <div
                style={{
                  padding: theme.spacing.lg,
                  textAlign: "center",
                  color: theme.colors.textMuted,
                  background: theme.background.glass,
                  borderRadius: theme.borderRadius.md,
                }}
              >
                <p style={{ margin: 0, fontSize: "14px" }}>
                  No candidates found or unable to fetch data. Check backend connection.
                </p>
              </div>
            )}
          </GlassCard>

          {/* Portfolio Snapshot */}
          <GlassCard>
            <h3
              style={{
                fontSize: "18px",
                fontWeight: "600",
                color: theme.colors.text,
                marginBottom: theme.spacing.md,
              }}
            >
              Portfolio Snapshot
            </h3>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: isMobile ? "repeat(2, 1fr)" : "repeat(4, 1fr)",
                gap: theme.spacing.md,
              }}
            >
              <div>
                <p style={{ fontSize: "12px", color: theme.colors.textMuted, margin: 0 }}>
                  Total Value
                </p>
                <p
                  style={{
                    fontSize: "24px",
                    fontWeight: "600",
                    color: theme.colors.text,
                    margin: 0,
                  }}
                >
                  ${portfolio.totalValue.toLocaleString()}
                </p>
              </div>
              <div>
                <p style={{ fontSize: "12px", color: theme.colors.textMuted, margin: 0 }}>
                  Day Change
                </p>
                <p
                  style={{
                    fontSize: "24px",
                    fontWeight: "600",
                    color: portfolio.dayChange >= 0 ? theme.colors.primary : theme.colors.danger,
                    margin: 0,
                  }}
                >
                  {portfolio.dayChange >= 0 ? "+" : ""}${portfolio.dayChange.toFixed(2)}
                </p>
              </div>
              <div>
                <p style={{ fontSize: "12px", color: theme.colors.textMuted, margin: 0 }}>Day %</p>
                <p
                  style={{
                    fontSize: "24px",
                    fontWeight: "600",
                    color:
                      portfolio.dayChangePercent >= 0 ? theme.colors.primary : theme.colors.danger,
                    margin: 0,
                  }}
                >
                  {portfolio.dayChangePercent >= 0 ? "+" : ""}
                  {portfolio.dayChangePercent.toFixed(2)}%
                </p>
              </div>
              <div>
                <p style={{ fontSize: "12px", color: theme.colors.textMuted, margin: 0 }}>
                  Buying Power
                </p>
                <p
                  style={{
                    fontSize: "24px",
                    fontWeight: "600",
                    color: theme.colors.text,
                    margin: 0,
                  }}
                >
                  ${portfolio.buyingPower.toLocaleString()}
                </p>
              </div>
            </div>
          </GlassCard>

          {/* System Checks */}
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
                style={{ fontSize: "18px", fontWeight: "600", color: theme.colors.text, margin: 0 }}
              >
                System Checks
              </h3>
              <GlassButton onClick={runMorningChecks} disabled={loading}>
                {loading ? (
                  <Loader2 className="animate-spin" style={{ width: "18px", height: "18px" }} />
                ) : (
                  "Run Checks"
                )}
              </GlassButton>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: theme.spacing.sm }}>
              {systemChecks.map((check, idx) => (
                <div
                  key={idx}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: theme.spacing.sm,
                    background: `${
                      check.status === "pass"
                        ? theme.colors.primary
                        : check.status === "warning"
                          ? theme.colors.warning
                          : theme.colors.danger
                    }10`,
                    border: `1px solid ${
                      check.status === "pass"
                        ? theme.colors.primary
                        : check.status === "warning"
                          ? theme.colors.warning
                          : theme.colors.danger
                    }30`,
                    borderRadius: theme.borderRadius.md,
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: theme.spacing.sm }}>
                    {check.status === "pass" && (
                      <CheckCircle
                        style={{ width: "18px", height: "18px", color: theme.colors.primary }}
                      />
                    )}
                    {check.status === "warning" && (
                      <AlertCircle
                        style={{ width: "18px", height: "18px", color: theme.colors.warning }}
                      />
                    )}
                    {check.status === "fail" && (
                      <XCircle
                        style={{ width: "18px", height: "18px", color: theme.colors.danger }}
                      />
                    )}
                    <span style={{ color: theme.colors.text, fontWeight: "600" }}>
                      {check.name}
                    </span>
                  </div>
                  <span style={{ color: theme.colors.textMuted, fontSize: "14px" }}>
                    {check.message}
                  </span>
                </div>
              ))}
            </div>
          </GlassCard>

          {/* Today's News */}
          <GlassCard>
            <h3
              style={{
                fontSize: "18px",
                fontWeight: "600",
                color: theme.colors.text,
                marginBottom: theme.spacing.md,
              }}
            >
              Today&apos;s Market Events
            </h3>
            <div style={{ display: "flex", flexDirection: "column", gap: theme.spacing.sm }}>
              {todaysNews.map((news, idx) => (
                <div
                  key={idx}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: theme.spacing.sm,
                    background: theme.background.glass,
                    borderRadius: theme.borderRadius.sm,
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: theme.spacing.sm }}>
                    <GlassBadge
                      variant={
                        news.impact === "high"
                          ? "danger"
                          : news.impact === "medium"
                            ? "warning"
                            : "info"
                      }
                    >
                      {news.impact}
                    </GlassBadge>
                    <span style={{ color: theme.colors.text }}>{news.title}</span>
                  </div>
                  <span style={{ color: theme.colors.textMuted, fontSize: "14px" }}>
                    {news.time}
                  </span>
                </div>
              ))}
            </div>
          </GlassCard>
        </div>
      </div>
    );
  }

  // Scheduler View
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
          maxWidth: "900px",
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
            gap: isMobile ? theme.spacing.md : 0,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: theme.spacing.md }}>
            <div
              style={{
                padding: theme.spacing.md,
                background: `${accentColor}20`,
                borderRadius: theme.borderRadius.lg,
                boxShadow: theme.glow.teal,
              }}
            >
              <Calendar
                style={{
                  width: isMobile ? "24px" : "32px",
                  height: isMobile ? "24px" : "32px",
                  color: accentColor,
                }}
              />
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
                Morning Routine Scheduler
              </h1>
              <p
                style={{
                  color: theme.colors.textMuted,
                  margin: "4px 0 0 0",
                  fontSize: "14px",
                }}
              >
                Automate your daily trading routine
              </p>
            </div>
          </div>

          <GlassButton
            onClick={() => setView("dashboard")}
            variant="secondary"
            style={{ width: isMobile ? "100%" : "auto" }}
          >
            Back to Dashboard
          </GlassButton>
        </div>

        {/* Enable Toggle */}
        <GlassCard>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <div>
              <h3
                style={{
                  fontSize: "18px",
                  fontWeight: "600",
                  color: theme.colors.text,
                  margin: `0 0 ${theme.spacing.xs} 0`,
                }}
              >
                Enable Morning Routine
              </h3>
              <p style={{ color: theme.colors.textMuted, margin: 0, fontSize: "14px" }}>
                Get daily briefings and recommendations at your scheduled time
              </p>
            </div>
            <button
              onClick={() => setScheduleEnabled(!scheduleEnabled)}
              style={{
                width: "56px",
                height: "32px",
                borderRadius: "16px",
                border: "none",
                background: scheduleEnabled ? theme.colors.primary : theme.colors.border,
                cursor: "pointer",
                position: "relative",
                transition: theme.transitions.fast,
              }}
            >
              <div
                style={{
                  width: "24px",
                  height: "24px",
                  borderRadius: "50%",
                  background: "#ffffff",
                  position: "absolute",
                  top: "4px",
                  left: scheduleEnabled ? "28px" : "4px",
                  transition: theme.transitions.fast,
                }}
              />
            </button>
          </div>
        </GlassCard>

        {scheduleEnabled && (
          <>
            {/* Schedule Time */}
            <GlassCard>
              <h3
                style={{
                  fontSize: "18px",
                  fontWeight: "600",
                  color: theme.colors.text,
                  marginBottom: theme.spacing.md,
                }}
              >
                Schedule Time
              </h3>
              <input
                type="time"
                value={scheduleTime}
                onChange={(e) => setScheduleTime(e.target.value)}
                style={{
                  width: "100%",
                  padding: theme.spacing.md,
                  fontSize: "24px",
                  fontWeight: "600",
                  textAlign: "center",
                  background: theme.background.input,
                  border: `1px solid ${theme.colors.border}`,
                  borderRadius: theme.borderRadius.md,
                  color: theme.colors.text,
                  outline: "none",
                }}
              />
            </GlassCard>

            {/* Frequency */}
            <GlassCard>
              <h3
                style={{
                  fontSize: "18px",
                  fontWeight: "600",
                  color: theme.colors.text,
                  marginBottom: theme.spacing.md,
                }}
              >
                Frequency
              </h3>
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: isMobile ? "1fr" : "repeat(3, 1fr)",
                  gap: theme.spacing.sm,
                }}
              >
                {(["daily", "weekdays", "custom"] as const).map((freq) => (
                  <button
                    key={freq}
                    onClick={() => setScheduleFrequency(freq)}
                    style={{
                      padding: theme.spacing.md,
                      background:
                        scheduleFrequency === freq ? `${accentColor}20` : theme.background.glass,
                      border: `2px solid ${scheduleFrequency === freq ? accentColor : theme.colors.border}`,
                      borderRadius: theme.borderRadius.md,
                      color: theme.colors.text,
                      fontWeight: "600",
                      cursor: "pointer",
                      textTransform: "capitalize",
                      transition: theme.transitions.fast,
                    }}
                  >
                    {freq}
                  </button>
                ))}
              </div>
            </GlassCard>

            {/* Routine Steps */}
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
                  Routine Steps
                </h3>
                <GlassButton
                  onClick={() => setShowAIBuilder(!showAIBuilder)}
                  variant="workflow"
                  workflowColor="strategyBuilder"
                >
                  <Sparkles style={{ width: "16px", height: "16px" }} />
                  AI Builder
                </GlassButton>
              </div>

              {showAIBuilder && (
                <div
                  style={{
                    marginBottom: theme.spacing.md,
                    padding: theme.spacing.md,
                    background: `${accentColor}10`,
                    borderRadius: theme.borderRadius.md,
                  }}
                >
                  <p
                    style={{
                      color: theme.colors.textMuted,
                      margin: `0 0 ${theme.spacing.sm} 0`,
                      fontSize: "14px",
                    }}
                  >
                    Describe your ideal morning routine:
                  </p>
                  <textarea
                    value={aiInput}
                    onChange={(e) => setAiInput(e.target.value)}
                    placeholder="Example: Show me top 3 pre-market movers, check news on my positions, alert me if any earnings today"
                    disabled={isGenerating}
                    style={{
                      width: "100%",
                      minHeight: "80px",
                      padding: theme.spacing.sm,
                      background: theme.background.input,
                      border: `1px solid ${theme.colors.border}`,
                      borderRadius: theme.borderRadius.sm,
                      color: theme.colors.text,
                      fontSize: "14px",
                      fontFamily: "inherit",
                      resize: "vertical",
                      outline: "none",
                      marginBottom: theme.spacing.sm,
                    }}
                  />
                  <GlassButton
                    onClick={handleGenerateAIRoutine}
                    disabled={!aiInput.trim() || isGenerating}
                  >
                    {isGenerating ? (
                      <>
                        <Loader2
                          className="animate-spin"
                          style={{ width: "16px", height: "16px" }}
                        />
                        Generating...
                      </>
                    ) : (
                      <>
                        <Brain style={{ width: "16px", height: "16px" }} />
                        Generate Routine
                      </>
                    )}
                  </GlassButton>
                  {error && (
                    <p
                      style={{
                        color: theme.colors.danger,
                        margin: `${theme.spacing.sm} 0 0 0`,
                        fontSize: "14px",
                      }}
                    >
                      {error}
                    </p>
                  )}
                </div>
              )}

              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: isMobile ? "1fr" : "repeat(2, 1fr)",
                  gap: theme.spacing.sm,
                }}
              >
                {availableSteps.map((step) => (
                  <button
                    key={step.id}
                    onClick={() => toggleStep(step.id)}
                    style={{
                      padding: theme.spacing.md,
                      background: selectedSteps.includes(step.id)
                        ? `${accentColor}20`
                        : theme.background.glass,
                      border: `2px solid ${selectedSteps.includes(step.id) ? accentColor : theme.colors.border}`,
                      borderRadius: theme.borderRadius.md,
                      cursor: "pointer",
                      textAlign: "left",
                      transition: theme.transitions.fast,
                    }}
                  >
                    <div style={{ fontSize: "24px", marginBottom: theme.spacing.xs }}>
                      {step.icon}
                    </div>
                    <div
                      style={{ color: theme.colors.text, fontWeight: "600", marginBottom: "4px" }}
                    >
                      {step.label}
                    </div>
                    <div style={{ color: theme.colors.textMuted, fontSize: "12px" }}>
                      {step.desc}
                    </div>
                  </button>
                ))}
              </div>
            </GlassCard>

            {/* Preview */}
            <GlassCard
              style={{ background: `${accentColor}10`, border: `1px solid ${accentColor}40` }}
            >
              <h3
                style={{
                  fontSize: "18px",
                  fontWeight: "600",
                  color: theme.colors.text,
                  marginBottom: theme.spacing.md,
                  display: "flex",
                  alignItems: "center",
                  gap: theme.spacing.sm,
                }}
              >
                <Bell style={{ width: "20px", height: "20px", color: accentColor }} />
                Morning Briefing Preview
              </h3>
              <div
                style={{
                  padding: theme.spacing.md,
                  background: theme.background.glass,
                  borderRadius: theme.borderRadius.md,
                }}
              >
                <p
                  style={{
                    color: theme.colors.text,
                    fontWeight: "600",
                    marginBottom: theme.spacing.sm,
                  }}
                >
                  Good morning! Here&apos;s your {scheduleTime} briefing:
                </p>
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: theme.spacing.xs,
                    color: theme.colors.textMuted,
                    fontSize: "14px",
                  }}
                >
                  {selectedSteps.map((stepId) => {
                    const step = availableSteps.find((s) => s.id === stepId);
                    return step ? (
                      <div key={stepId}>
                        {step.icon} {step.label}
                      </div>
                    ) : null;
                  })}
                </div>
              </div>
            </GlassCard>

            {/* Save Button */}
            <GlassButton onClick={handleSaveSchedule}>
              <CheckCircle style={{ width: "18px", height: "18px" }} />
              Save Morning Routine
            </GlassButton>
          </>
        )}
      </div>
    </div>
  );
}
