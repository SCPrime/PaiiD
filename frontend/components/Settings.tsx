"use client";

import {
  Activity,
  AlertTriangle,
  BarChart3,
  Bell,
  BookOpen,
  Brain,
  CheckCircle2,
  Clock,
  CreditCard,
  Database,
  FileText,
  Lock,
  MessageSquare,
  Newspaper,
  Palette,
  Save,
  Settings as SettingsIcon,
  Shield,
  Target,
  ToggleLeft,
  ToggleRight,
  Users,
} from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import toast from "react-hot-toast";
import { useTheme } from "../contexts/ThemeContext";
import { useIsMobile } from "../hooks/useBreakpoint";
import { clearUserData, getCurrentUser, getUserAnalytics } from "../lib/userManagement";
import ApprovalQueue from "./ApprovalQueue";
import ClaudeAIChat from "./ClaudeAIChat";
import KillSwitchToggle from "./KillSwitchToggle";
import MLAnalyticsDashboard from "./MLAnalyticsDashboard";
import MLModelManagement from "./MLModelManagement";
import MLTrainingDashboard from "./MLTrainingDashboard";
import { MonitorDashboard } from "./MonitorDashboard";
import PatternBacktestDashboard from "./PatternBacktestDashboard";
import PerformanceDashboard from "./admin/PerformanceDashboard";
import PortfolioOptimizer from "./PortfolioOptimizer";
import RiskDashboard from "./RiskDashboard";
import SchedulerSettings from "./SchedulerSettings";
import SentimentDashboard from "./SentimentDashboard";
import SubscriptionManager from "./SubscriptionManager";
import TradingJournal from "./TradingJournal";
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const _MLTrainingDashboard = MLTrainingDashboard; // Reserved for future ML training feature

interface User {
  id: string;
  email: string;
  name: string;
  role: "owner" | "admin" | "beta" | "alpha" | "user";
  tradingMode: "paper" | "live";
  permissions: {
    canTrade: boolean;
    canBacktest: boolean;
    canViewAnalytics: boolean;
    canModifyStrategies: boolean;
  };
  status: "active" | "suspended";
  createdAt: string;
  lastLogin: string;
}

interface ThemeCustomization {
  primaryColor: string;
  accentColor: string;
  successColor: string;
  errorColor: string;
  warningColor: string;
  infoColor: string;
}

interface TelemetryData {
  sessionId: string;
  userId: string;
  action: string;
  component: string;
  timestamp: string;
  metadata: Record<string, unknown>;
}

interface SettingsData {
  defaultExecutionMode: "requires_approval" | "autopilot";
  enableSMSAlerts: boolean;
  enableEmailAlerts: boolean;
  enablePushNotifications: boolean;
  enablePerformanceTracking: boolean;
  minTradesForPerformanceData: number;
  defaultSlippageBudget: number;
  defaultMaxReprices: number;
}

interface SettingsProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function Settings({ isOpen, onClose }: SettingsProps) {
  const isMobile = useIsMobile();
  const currentUserData = getCurrentUser();
  const { theme: currentTheme, toggleTheme } = useTheme();
  const [currentUser] = useState({
    id: currentUserData?.userId || "owner-001",
    role: "owner" as const,
  });
  const isOwner = currentUser.role === "owner";
  const isAdmin = currentUser.role === "owner" || currentUser.role === "admin";

  const [activeTab, setActiveTab] = useState<
    | "personal"
    | "users"
    | "theme"
    | "permissions"
    | "telemetry"
    | "trading"
    | "journal"
    | "risk"
    | "automation"
    | "approvals"
  >("personal");

  const [settings, setSettings] = useState<SettingsData>({
    defaultExecutionMode: "requires_approval",
    enableSMSAlerts: true,
    enableEmailAlerts: true,
    enablePushNotifications: false,
    enablePerformanceTracking: true,
    minTradesForPerformanceData: 10,
    defaultSlippageBudget: 0.4,
    defaultMaxReprices: 4,
  });

  const [users, setUsers] = useState<User[]>([]);
  const [themeCustom, setThemeCustom] = useState<ThemeCustomization>({
    primaryColor: "#10b981",
    accentColor: "#7E57C2",
    successColor: "#10b981",
    errorColor: "#ef4444",
    warningColor: "#f59e0b",
    infoColor: "#14b8a6",
  });
  const [telemetryEnabled, setTelemetryEnabled] = useState(true);
  const [telemetryData, setTelemetryData] = useState<TelemetryData[]>([]);

  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState("");

  // Risk Tolerance State
  const [riskTolerance, setRiskTolerance] = useState<number>(50);
  const [riskLimits, setRiskLimits] = useState<{
    risk_category: string;
    max_position_size_percent: number;
    max_positions: number;
    description: string;
  } | null>(null);
  const [isLoadingRisk, setIsLoadingRisk] = useState(false);

  // Paper Trading Account Balance State
  const [paperAccountBalance, setPaperAccountBalance] = useState<number>(100000);
  const [accountInfo, setAccountInfo] = useState<{
    equity: number;
    cash: number;
    buying_power: number;
  } | null>(null);
  const [isLoadingBalance, setIsLoadingBalance] = useState(false);

  useEffect(() => {
    if (!isOpen) return;

    const savedSettings = localStorage.getItem("allessandra_settings");
    if (savedSettings) {
      try {
        setSettings(JSON.parse(savedSettings));
      } catch (error) {
        console.error("Failed to load settings:", error);
      }
    }

    // Fetch risk tolerance and account balance from backend
    fetchRiskTolerance();
    fetchAccountBalance();

    if (isAdmin) {
      loadMockUsers();
      loadTelemetryData();
    }
  }, [isOpen, isAdmin]);

  const loadMockUsers = () => {
    setUsers([
      {
        id: "owner-001",
        email: "owner@paid.com",
        name: "System Owner",
        role: "owner",
        tradingMode: "paper",
        permissions: {
          canTrade: true,
          canBacktest: true,
          canViewAnalytics: true,
          canModifyStrategies: true,
        },
        status: "active",
        createdAt: "2025-01-01",
        lastLogin: new Date().toISOString().split("T")[0],
      },
      {
        id: "beta-001",
        email: "beta.tester1@paid.com",
        name: "Beta Tester 1",
        role: "beta",
        tradingMode: "paper",
        permissions: {
          canTrade: true,
          canBacktest: true,
          canViewAnalytics: true,
          canModifyStrategies: false,
        },
        status: "active",
        createdAt: "2025-09-15",
        lastLogin: "2025-10-05",
      },
    ]);
  };

  const loadTelemetryData = () => {
    const mockData: TelemetryData[] = [
      {
        sessionId: "sess-001",
        userId: "beta-001",
        action: "execute_trade",
        component: "ExecuteTradeForm",
        timestamp: new Date().toISOString(),
        metadata: { symbol: "AAPL", side: "buy", quantity: 10 },
      },
    ];
    setTelemetryData(mockData);
  };

  // Fetch Risk Tolerance from Backend
  const fetchRiskTolerance = async () => {
    try {
      const apiToken = process.env.NEXT_PUBLIC_API_TOKEN;
      const baseUrl = process.env.NEXT_PUBLIC_BACKEND_API_BASE_URL || "/api/proxy/api";

      const response = await fetch(`${baseUrl}/users/preferences`, {
        headers: {
          Authorization: `Bearer ${apiToken}`,
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        const data = await response.json();
        setRiskTolerance(data.risk_tolerance || 50);

        // Fetch risk limits
        const limitsResponse = await fetch(`${baseUrl}/users/risk-limits`, {
          headers: {
            Authorization: `Bearer ${apiToken}`,
            "Content-Type": "application/json",
          },
        });

        if (limitsResponse.ok) {
          const limitsData = await limitsResponse.json();
          setRiskLimits(limitsData);
        }
      }
    } catch (error) {
      console.error("Failed to fetch risk tolerance:", error);
    }
  };

  // Fetch Account Balance from Backend
  const fetchAccountBalance = async () => {
    try {
      const apiToken = process.env.NEXT_PUBLIC_API_TOKEN;
      const baseUrl = process.env.NEXT_PUBLIC_BACKEND_API_BASE_URL || "/api/proxy/api";

      const response = await fetch(`${baseUrl}/account`, {
        headers: {
          Authorization: `Bearer ${apiToken}`,
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        const data = await response.json();
        setAccountInfo({
          equity: parseFloat(data.equity || data.portfolio_value || "0"),
          cash: parseFloat(data.cash || "0"),
          buying_power: parseFloat(data.buying_power || "0"),
        });
        setPaperAccountBalance(parseFloat(data.equity || data.portfolio_value || "100000"));
      }
    } catch (error) {
      console.error("Failed to fetch account balance:", error);
    }
  };

  // Update Risk Tolerance with Debounce
  const updateRiskTolerance = useCallback(async (newValue: number) => {
    setIsLoadingRisk(true);

    try {
      const apiToken = process.env.NEXT_PUBLIC_API_TOKEN;
      const baseUrl = process.env.NEXT_PUBLIC_BACKEND_API_BASE_URL || "/api/proxy/api";

      const response = await fetch(`${baseUrl}/users/preferences`, {
        method: "PATCH",
        headers: {
          Authorization: `Bearer ${apiToken}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ risk_tolerance: newValue }),
      });

      if (response.ok) {
        const data = await response.json();
        setRiskTolerance(data.risk_tolerance);

        // Refresh risk limits
        const limitsResponse = await fetch(`${baseUrl}/users/risk-limits`, {
          headers: {
            Authorization: `Bearer ${apiToken}`,
            "Content-Type": "application/json",
          },
        });

        let limitsData = null;
        if (limitsResponse.ok) {
          limitsData = await limitsResponse.json();
          setRiskLimits(limitsData);
        }

        const riskCategory =
          limitsData?.risk_category ||
          (newValue <= 33 ? "Conservative" : newValue <= 66 ? "Moderate" : "Aggressive");
        toast.success(`Risk tolerance updated to ${newValue}% (${riskCategory})`);
      } else {
        toast.error("Failed to update risk tolerance");
      }
    } catch (error) {
      console.error("Failed to update risk tolerance:", error);
      toast.error("Failed to update risk tolerance");
    } finally {
      setIsLoadingRisk(false);
    }
  }, []);

  // Update Paper Account Balance
  const updatePaperAccountBalance = async () => {
    setIsLoadingBalance(true);

    try {
      const apiToken = process.env.NEXT_PUBLIC_API_TOKEN;
      const baseUrl = process.env.NEXT_PUBLIC_BACKEND_API_BASE_URL || "/api/proxy/api";

      const response = await fetch(`${baseUrl}/users/preferences`, {
        method: "PATCH",
        headers: {
          Authorization: `Bearer ${apiToken}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ paper_account_balance: paperAccountBalance }),
      });

      if (response.ok) {
        toast.success(`Paper account balance updated to $${paperAccountBalance.toLocaleString()}`);
        // Refresh account info after update
        await fetchAccountBalance();
      } else {
        toast.error("Failed to update paper account balance");
      }
    } catch (error) {
      console.error("Failed to update paper account balance:", error);
      toast.error("Failed to update paper account balance");
    } finally {
      setIsLoadingBalance(false);
    }
  };

  const updateSetting = <K extends keyof SettingsData>(key: K, value: SettingsData[K]) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
    setHasUnsavedChanges(true);
  };

  const handleSaveSettings = async () => {
    setIsSaving(true);
    setSaveMessage("");

    localStorage.setItem("allessandra_settings", JSON.stringify(settings));

    await new Promise((resolve) => setTimeout(resolve, 1500));

    setIsSaving(false);
    setHasUnsavedChanges(false);
    setSaveMessage("Settings saved successfully!");

    setTimeout(() => {
      setSaveMessage("");
    }, 3000);
  };

  const handleReset = () => {
    const defaultSettings: SettingsData = {
      defaultExecutionMode: "requires_approval",
      enableSMSAlerts: true,
      enableEmailAlerts: true,
      enablePushNotifications: false,
      enablePerformanceTracking: true,
      minTradesForPerformanceData: 10,
      defaultSlippageBudget: 0.4,
      defaultMaxReprices: 4,
    };
    setSettings(defaultSettings);
    setHasUnsavedChanges(true);
  };

  const toggleUserStatus = (userId: string) => {
    if (!isOwner) return;
    setUsers(
      users.map((user) =>
        user.id === userId
          ? { ...user, status: user.status === "active" ? "suspended" : "active" }
          : user
      )
    );
    setHasUnsavedChanges(true);
  };

  const updateUserPermission = (
    userId: string,
    permission: keyof User["permissions"],
    value: boolean
  ) => {
    if (!isOwner) return;
    setUsers(
      users.map((user) =>
        user.id === userId
          ? { ...user, permissions: { ...user.permissions, [permission]: value } }
          : user
      )
    );
    setHasUnsavedChanges(true);
  };

  const toggleTradingMode = (userId: string) => {
    if (!isOwner && userId !== currentUser.id) return;
    setUsers(
      users.map((user) =>
        user.id === userId
          ? { ...user, tradingMode: user.tradingMode === "paper" ? "live" : "paper" }
          : user
      )
    );
    setHasUnsavedChanges(true);
  };

  const exportTelemetryReport = () => {
    const dataStr = JSON.stringify(telemetryData, null, 2);
    const dataBlob = new Blob([dataStr], { type: "application/json" });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `telemetry-${new Date().toISOString()}.json`;
    link.click();
  };

  if (!isOpen) return null;

  const analytics = currentUserData ? getUserAnalytics() : null;

  const tabs = [
    { id: "personal", label: "Personal Settings", icon: SettingsIcon, alwaysShow: true },
    { id: "subscription", label: "Subscription & Billing", icon: CreditCard, alwaysShow: true },
    { id: "journal", label: "Trading Journal", icon: BookOpen, alwaysShow: true },
    { id: "risk", label: "Risk Control", icon: Shield, alwaysShow: true },
    { id: "ml-training", label: "ML Training", icon: Brain, alwaysShow: true },
    { id: "pattern-backtest", label: "Pattern Backtest", icon: BarChart3, alwaysShow: true },
    { id: "ml-models", label: "ML Models", icon: Database, alwaysShow: true },
    { id: "ml-analytics", label: "ML Analytics", icon: Activity, alwaysShow: true },
    { id: "portfolio-optimizer", label: "Portfolio Optimizer", icon: Target, alwaysShow: true },
    { id: "sentiment", label: "News Sentiment", icon: Newspaper, alwaysShow: true },
    { id: "ai-chat", label: "AI Chat", icon: MessageSquare, alwaysShow: true },
    { id: "automation", label: "Automation", icon: Clock, alwaysShow: true },
    { id: "approvals", label: "Approvals", icon: CheckCircle2, alwaysShow: true },
    { id: "users", label: "User Management", icon: Users, adminOnly: true },
    { id: "theme", label: "Theme", icon: Palette, adminOnly: true },
    { id: "permissions", label: "Permissions", icon: Lock, adminOnly: true },
    { id: "telemetry", label: "Telemetry", icon: Database, adminOnly: true },
    { id: "trading", label: "Trading Control", icon: Activity, adminOnly: true },
    { id: "performance", label: "Performance Monitor", icon: Activity, adminOnly: true },
    { id: "github-monitor", label: "GitHub Monitor", icon: Activity, adminOnly: true },
  ].filter((tab) => tab.alwaysShow || (tab.adminOnly && isAdmin));

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 50,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "16px",
        background: "rgba(0, 0, 0, 0.7)",
        backdropFilter: "blur(10px)",
        overflowY: "auto",
        color: "#e2e8f0",
      }}
    >
      <div
        style={{
          background: "rgba(30, 41, 59, 0.8)",
          backdropFilter: "blur(20px)",
          border: "1px solid rgba(16, 185, 129, 0.3)",
          borderRadius: "20px",
          boxShadow: "0 0 40px rgba(16, 185, 129, 0.15)",
          maxWidth: isMobile ? "95vw" : "1200px",
          width: "100%",
          maxHeight: "90vh",
          overflow: "hidden",
          display: "flex",
          flexDirection: "column",
          margin: isMobile ? "16px 0" : "32px 0",
        }}
      >
        {/* Header */}
        <div
          style={{
            padding: "16px 24px",
            borderBottom: "1px solid rgba(0, 172, 193, 0.2)",
            background:
              "linear-gradient(to right, rgba(0, 172, 193, 0.1), rgba(126, 87, 194, 0.1), rgba(0, 172, 193, 0.1))",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                <SettingsIcon size={28} style={{ color: "#00ACC1" }} />
                <h2 style={{ fontSize: "24px", fontWeight: "bold", color: "#ffffff", margin: 0 }}>
                  {isOwner ? "Master Control Panel" : "Settings"}
                </h2>
              </div>
              <p style={{ fontSize: "14px", color: "#cbd5e1", marginTop: "4px", marginBottom: 0 }}>
                {isOwner
                  ? "System-wide configuration and user management"
                  : "Configure your trading preferences and automation"}
              </p>
            </div>
            <button
              onClick={onClose}
              style={{
                padding: "8px 16px",
                background: "rgba(30, 41, 59, 0.8)",
                border: "1px solid rgba(100, 116, 139, 0.5)",
                color: "#ffffff",
                borderRadius: "8px",
                cursor: "pointer",
                transition: "all 0.15s ease",
              }}
            >
              ✕ Close
            </button>
          </div>

          {isOwner && (
            <div className="mt-3 px-3 py-2 bg-purple-500/20 border border-purple-500/30 rounded flex items-center gap-2">
              <Shield size={16} className="text-purple-400" />
              <p className="text-sm text-purple-400 font-semibold">
                System Owner Access - Full Control Enabled
              </p>
            </div>
          )}

          {saveMessage && (
            <div className="mt-3 px-3 py-2 bg-green-500/20 border border-green-500/30 rounded flex items-center gap-2">
              <CheckCircle2 size={16} className="text-green-400" />
              <p className="text-sm text-green-400 font-semibold">{saveMessage}</p>
            </div>
          )}
        </div>

        {/* Tabs */}
        <div className="px-6 py-3 border-b border-cyan-500/20 bg-slate-900/50 flex gap-2 overflow-x-auto">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as string)}
                className={`
                  px-4 py-2.5 rounded-lg font-medium text-sm transition-all flex items-center gap-2 whitespace-nowrap
                  ${
                    isActive
                      ? "text-white border-2 shadow-lg"
                      : "text-slate-400 hover:bg-slate-700/80 border-2 border-slate-700/30 hover:border-cyan-400/30"
                  }
                `}
                style={
                  isActive
                    ? {
                        background:
                          "linear-gradient(to right, rgba(0, 172, 193, 0.2), rgba(126, 87, 194, 0.2))",
                        borderColor: "rgba(0, 172, 193, 0.5)",
                        backdropFilter: "blur(10px)",
                        boxShadow: "0 0 20px rgba(0, 172, 193, 0.15)",
                      }
                    : {
                        background: "rgba(30, 41, 59, 0.6)",
                        backdropFilter: "blur(8px)",
                      }
                }
              >
                <Icon size={16} />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Content */}
        <div
          style={{
            flex: 1,
            overflowY: "auto",
            padding: "24px",
            background: "rgba(15, 23, 42, 0.2)",
            color: "#e2e8f0",
          }}
        >
          {activeTab === "personal" && (
            <div className="space-y-6">
              {currentUserData && (
                <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-5">
                  <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <span className="text-xl">👤</span>
                    User Information
                  </h3>

                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 bg-slate-900/40 border border-slate-700/30 rounded-lg">
                      <div>
                        <div className="text-xs text-slate-400 mb-1">Display Name</div>
                        <div className="text-sm font-medium text-white">
                          {currentUserData.displayName}
                        </div>
                      </div>
                    </div>

                    {currentUserData.email && (
                      <div className="flex items-center justify-between p-3 bg-slate-900/40 border border-slate-700/30 rounded-lg">
                        <div>
                          <div className="text-xs text-slate-400 mb-1">Email</div>
                          <div className="text-sm font-medium text-white">
                            {currentUserData.email}
                          </div>
                        </div>
                      </div>
                    )}

                    {analytics && (
                      <div
                        className="grid gap-3"
                        style={{ gridTemplateColumns: isMobile ? "1fr" : "repeat(2, 1fr)" }}
                      >
                        <div className="p-3 bg-slate-900/40 border border-slate-700/30 rounded-lg">
                          <div className="text-xs text-slate-400 mb-1">Account Age</div>
                          <div className="text-sm font-semibold text-cyan-400">
                            {analytics.accountAge}
                          </div>
                        </div>
                        <div className="p-3 bg-slate-900/40 border border-slate-700/30 rounded-lg">
                          <div className="text-xs text-slate-400 mb-1">Total Sessions</div>
                          <div className="text-sm font-semibold text-purple-400">
                            {analytics.totalSessions}
                          </div>
                        </div>
                      </div>
                    )}

                    <button
                      onClick={() => {
                        if (
                          window.confirm(
                            "Are you sure you want to clear all user data? This will log you out."
                          )
                        ) {
                          clearUserData();
                          window.location.reload();
                        }
                      }}
                      className="w-full mt-2 px-4 py-2 bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 text-red-400 rounded-lg transition-all text-sm font-medium"
                    >
                      🗑️ Clear User Data & Logout
                    </button>
                  </div>
                </div>
              )}

              <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-5">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <span className="text-xl">🤖</span>
                  Trading Mode
                </h3>

                <div className="space-y-3">
                  <label className="flex items-start gap-3 p-4 bg-slate-900/40 border border-slate-700/30 rounded-lg cursor-pointer hover:border-cyan-500/50 transition-all">
                    <input
                      type="radio"
                      name="executionMode"
                      value="requires_approval"
                      checked={settings.defaultExecutionMode === "requires_approval"}
                      onChange={() => updateSetting("defaultExecutionMode", "requires_approval")}
                      className="mt-1"
                    />
                    <div>
                      <div className="text-sm font-semibold text-white mb-1">
                        Requires Approval (Recommended)
                      </div>
                      <div className="text-xs text-slate-400">
                        All trades require your manual approval via SMS/Email before execution.
                      </div>
                    </div>
                  </label>

                  <label className="flex items-start gap-3 p-4 bg-slate-900/40 border border-slate-700/30 rounded-lg cursor-pointer hover:border-purple-500/50 transition-all">
                    <input
                      type="radio"
                      name="executionMode"
                      value="autopilot"
                      checked={settings.defaultExecutionMode === "autopilot"}
                      onChange={() => updateSetting("defaultExecutionMode", "autopilot")}
                      className="mt-1"
                    />
                    <div>
                      <div className="text-sm font-semibold text-white mb-1">Autopilot Mode</div>
                      <div className="text-xs text-slate-400">
                        Trades execute automatically based on strategy rules.
                      </div>
                    </div>
                  </label>
                </div>
              </div>

              <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-5">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Palette size={20} />
                  Appearance
                </h3>

                <div className="space-y-3">
                  {/* Theme Toggle */}
                  <div className="flex items-center justify-between">
                    <div>
                      <label className="text-slate-200 font-medium block mb-1">Theme</label>
                      <p className="text-sm text-slate-400">Switch between dark and light mode</p>
                    </div>
                    <button
                      onClick={toggleTheme}
                      className="relative inline-flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-200 hover:scale-105"
                      style={{
                        background:
                          currentTheme === "dark"
                            ? "linear-gradient(135deg, #1e293b 0%, #0f172a 100%)"
                            : "linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)",
                        border:
                          currentTheme === "dark"
                            ? "1px solid rgba(148, 163, 184, 0.3)"
                            : "1px solid rgba(203, 213, 225, 0.5)",
                        boxShadow:
                          currentTheme === "dark"
                            ? "0 4px 12px rgba(0, 0, 0, 0.3)"
                            : "0 4px 12px rgba(0, 0, 0, 0.1)",
                      }}
                    >
                      {theme === "dark" ? (
                        <>
                          <span className="text-slate-300">🌙</span>
                          <span className="text-sm font-medium text-slate-300">Dark</span>
                        </>
                      ) : (
                        <>
                          <span className="text-slate-700">☀️</span>
                          <span className="text-sm font-medium text-slate-700">Light</span>
                        </>
                      )}
                    </button>
                  </div>

                  {/* Theme Preview */}
                  <div
                    className="p-4 rounded-lg border"
                    style={{
                      background: theme === "dark" ? "#0f172a" : "#ffffff",
                      borderColor:
                        theme === "dark" ? "rgba(71, 85, 105, 0.3)" : "rgba(203, 213, 225, 0.5)",
                    }}
                  >
                    <div className="flex items-center gap-3 mb-2">
                      <div
                        className="w-10 h-10 rounded-full"
                        style={{
                          background: "linear-gradient(135deg, #10b981 0%, #059669 100%)",
                        }}
                      />
                      <div>
                        <div
                          className="text-sm font-medium"
                          style={{ color: theme === "dark" ? "#ffffff" : "#0f172a" }}
                        >
                          Theme Preview
                        </div>
                        <div
                          className="text-xs"
                          style={{ color: theme === "dark" ? "#94a3b8" : "#64748b" }}
                        >
                          Your interface will look like this
                        </div>
                      </div>
                    </div>
                    <div
                      className="text-xs p-2 rounded"
                      style={{
                        background:
                          theme === "dark" ? "rgba(30, 41, 59, 0.6)" : "rgba(248, 250, 252, 0.8)",
                        color: theme === "dark" ? "#cbd5e1" : "#475569",
                      }}
                    >
                      ✓ Saved to localStorage
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-5">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Bell size={20} />
                  Notifications
                </h3>

                <div className="space-y-3">
                  {[
                    {
                      key: "enableSMSAlerts",
                      label: "SMS Alerts",
                      desc: "Text messages for trade proposals",
                    },
                    {
                      key: "enableEmailAlerts",
                      label: "Email Alerts",
                      desc: "Email notifications for trades",
                    },
                    {
                      key: "enablePushNotifications",
                      label: "Push Notifications",
                      desc: "Browser push notifications",
                    },
                  ].map(({ key, label, desc }) => (
                    <label
                      key={key}
                      className="flex items-center justify-between p-3 bg-slate-900/40 border border-slate-700/30 rounded-lg cursor-pointer hover:border-cyan-500/30 transition-all"
                    >
                      <div>
                        <div className="text-sm font-medium text-white">{label}</div>
                        <div className="text-xs text-slate-400">{desc}</div>
                      </div>
                      <input
                        type="checkbox"
                        checked={settings[key as keyof SettingsData] as boolean}
                        onChange={(e) => updateSetting(key as keyof SettingsData, e.target.checked)}
                        className="w-5 h-5"
                      />
                    </label>
                  ))}
                </div>
              </div>

              {/* Paper Trading Account Balance Section */}
              <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-5">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <span className="text-xl">💵</span>
                  Paper Trading Account Balance
                </h3>

                <div className="space-y-4">
                  {/* Current Account Info Display */}
                  {accountInfo && (
                    <div className="p-4 bg-slate-900/40 border border-slate-700/30 rounded-lg">
                      <div
                        className="grid gap-3"
                        style={{ gridTemplateColumns: isMobile ? "1fr" : "repeat(3, 1fr)" }}
                      >
                        <div>
                          <div className="text-xs text-slate-400 mb-1">Total Equity</div>
                          <div className="text-lg font-semibold text-white">
                            ${accountInfo.equity.toLocaleString()}
                          </div>
                        </div>
                        <div>
                          <div className="text-xs text-slate-400 mb-1">Available Cash</div>
                          <div className="text-lg font-semibold text-cyan-400">
                            ${accountInfo.cash.toLocaleString()}
                          </div>
                        </div>
                        <div>
                          <div className="text-xs text-slate-400 mb-1">Buying Power</div>
                          <div className="text-lg font-semibold text-purple-400">
                            ${accountInfo.buying_power.toLocaleString()}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Balance Input */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <label className="block text-sm font-medium text-slate-300">
                        Set Paper Account Balance ($)
                      </label>
                      {isLoadingBalance && (
                        <div className="text-xs text-cyan-400 animate-pulse">Updating...</div>
                      )}
                    </div>
                    <div className="flex gap-2">
                      <input
                        type="number"
                        min="1000"
                        max="10000000"
                        step="1000"
                        value={paperAccountBalance}
                        onChange={(e) => setPaperAccountBalance(Number(e.target.value))}
                        className="flex-1 px-4 py-3 bg-slate-900/60 border border-slate-700/50 rounded-lg text-white font-semibold text-lg outline-none focus:ring-2 focus:ring-cyan-500/50"
                        placeholder="100000"
                      />
                      <button
                        onClick={updatePaperAccountBalance}
                        disabled={isLoadingBalance}
                        className="px-6 py-3 bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-600 hover:to-purple-600 text-white font-semibold rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {isLoadingBalance ? "Updating..." : "Update"}
                      </button>
                    </div>
                    <div className="flex justify-between text-xs text-slate-400 mt-2">
                      <span>Min: $1,000</span>
                      <span>Default: $100,000</span>
                      <span>Max: $10,000,000</span>
                    </div>
                  </div>

                  {/* Info Banner */}
                  <div className="p-3 bg-yellow-500/10 border border-yellow-500/30 rounded flex items-start gap-2">
                    <AlertTriangle size={16} className="text-yellow-400 mt-0.5" />
                    <p className="text-xs text-yellow-400">
                      <strong>Paper Trading Only:</strong> This setting controls your simulated
                      account balance for paper trading. Real money trading requires separate
                      authentication and approval.
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-5">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Lock size={20} />
                  Risk Parameters
                </h3>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Slippage Budget (%)
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="1"
                      step="0.05"
                      value={settings.defaultSlippageBudget}
                      onChange={(e) =>
                        updateSetting("defaultSlippageBudget", Number(e.target.value))
                      }
                      className="w-full px-4 py-3 bg-slate-900/60 border border-slate-700/50 rounded-lg text-white outline-none focus:ring-2 focus:ring-cyan-500/50"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Max Order Reprices
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="10"
                      value={settings.defaultMaxReprices}
                      onChange={(e) => updateSetting("defaultMaxReprices", Number(e.target.value))}
                      className="w-full px-4 py-3 bg-slate-900/60 border border-slate-700/50 rounded-lg text-white outline-none focus:ring-2 focus:ring-cyan-500/50"
                    />
                  </div>
                </div>
              </div>

              {/* Risk Tolerance Slider Section */}
              <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-5">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Target size={20} className="text-cyan-400" />
                  Risk Tolerance Profile
                </h3>

                <div className="space-y-4">
                  {/* Current Risk Level Display */}
                  <div className="p-4 bg-slate-900/40 border border-slate-700/30 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <div className="text-sm font-medium text-slate-300">Current Risk Level</div>
                      <div
                        className={`px-3 py-1 rounded-full text-sm font-semibold ${
                          riskTolerance <= 33
                            ? "bg-green-500/20 text-green-400 border border-green-500/30"
                            : riskTolerance <= 66
                              ? "bg-yellow-500/20 text-yellow-400 border border-yellow-500/30"
                              : "bg-red-500/20 text-red-400 border border-red-500/30"
                        }`}
                      >
                        {riskLimits?.risk_category ||
                          (riskTolerance <= 33
                            ? "Conservative"
                            : riskTolerance <= 66
                              ? "Moderate"
                              : "Aggressive")}
                      </div>
                    </div>
                    <div className="text-2xl font-bold text-white">{riskTolerance}%</div>
                    <div className="text-xs text-slate-400 mt-1">
                      {riskLimits?.description || "Loading limits..."}
                    </div>
                  </div>

                  {/* Risk Tolerance Slider */}
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <label className="block text-sm font-medium text-slate-300">
                        Adjust Risk Tolerance (0-100%)
                      </label>
                      {isLoadingRisk && (
                        <div className="text-xs text-cyan-400 animate-pulse">Updating...</div>
                      )}
                    </div>

                    {/* Color-coded slider background */}
                    <div className="relative h-3 rounded-full bg-gradient-to-r from-green-500/30 via-yellow-500/30 to-red-500/30 mb-2">
                      {/* Slider track markers */}
                      <div className="absolute top-0 left-1/3 w-px h-full bg-slate-600"></div>
                      <div className="absolute top-0 left-2/3 w-px h-full bg-slate-600"></div>
                    </div>

                    <input
                      type="range"
                      min="0"
                      max="100"
                      step="1"
                      value={riskTolerance}
                      onChange={(e) => {
                        const newValue = Number(e.target.value);
                        setRiskTolerance(newValue);
                      }}
                      onMouseUp={(e) => {
                        const newValue = Number((e.target as HTMLInputElement).value);
                        updateRiskTolerance(newValue);
                      }}
                      onTouchEnd={(e) => {
                        const newValue = Number((e.target as HTMLInputElement).value);
                        updateRiskTolerance(newValue);
                      }}
                      className="w-full h-2 rounded-lg appearance-none cursor-pointer"
                      style={{
                        background: `linear-gradient(to right,
                          ${
                            riskTolerance <= 33
                              ? "#10b981"
                              : riskTolerance <= 66
                                ? "#f59e0b"
                                : "#ef4444"
                          } ${riskTolerance}%,
                          rgba(100, 116, 139, 0.3) ${riskTolerance}%)`,
                      }}
                    />

                    <div className="flex justify-between text-xs text-slate-400 mt-2">
                      <span className="text-green-400">Conservative (0-33%)</span>
                      <span className="text-yellow-400">Moderate (34-66%)</span>
                      <span className="text-red-400">Aggressive (67-100%)</span>
                    </div>
                  </div>

                  {/* Position Sizing Limits Display */}
                  {riskLimits && (
                    <div
                      className="grid gap-3 mt-4"
                      style={{ gridTemplateColumns: isMobile ? "1fr" : "repeat(2, 1fr)" }}
                    >
                      <div className="p-3 bg-slate-900/40 border border-slate-700/30 rounded-lg">
                        <div className="text-xs text-slate-400 mb-1">Max Position Size</div>
                        <div className="text-lg font-semibold text-cyan-400">
                          {riskLimits.max_position_size_percent}%
                        </div>
                      </div>
                      <div className="p-3 bg-slate-900/40 border border-slate-700/30 rounded-lg">
                        <div className="text-xs text-slate-400 mb-1">Max Concurrent Positions</div>
                        <div className="text-lg font-semibold text-purple-400">
                          {riskLimits.max_positions}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Info Banner */}
                  <div className="p-3 bg-cyan-500/10 border border-cyan-500/30 rounded flex items-start gap-2 mt-4">
                    <Shield size={16} className="text-cyan-400 mt-0.5" />
                    <p className="text-xs text-cyan-400">
                      <strong>Backend Safeguards:</strong> Position sizing limits are enforced
                      server-side to prevent excessive risk exposure. Strategy templates
                      automatically adjust to your risk profile.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === "subscription" && <SubscriptionManager />}
          {activeTab === "journal" && <TradingJournal />}
          {activeTab === "risk" && <RiskDashboard />}
          {activeTab === "ml-training" && (
            <div className="min-h-[500px]">
              <MLTrainingDashboard />
            </div>
          )}
          {activeTab === "pattern-backtest" && (
            <div className="min-h-[500px]">
              <PatternBacktestDashboard />
            </div>
          )}
          {activeTab === "ml-models" && (
            <div className="min-h-[500px]">
              <MLModelManagement />
            </div>
          )}
          {activeTab === "ml-analytics" && (
            <div className="min-h-[500px]">
              <MLAnalyticsDashboard />
            </div>
          )}
          {activeTab === "portfolio-optimizer" && (
            <div className="min-h-[500px]">
              <PortfolioOptimizer />
            </div>
          )}
          {activeTab === "sentiment" && (
            <div className="min-h-[500px]">
              <SentimentDashboard />
            </div>
          )}
          {activeTab === "ai-chat" && (
            <div className="min-h-[500px]">
              <ClaudeAIChat />
            </div>
          )}
          {activeTab === "automation" && (
            <div className="min-h-[500px]">
              <SchedulerSettings />
            </div>
          )}
          {activeTab === "approvals" && (
            <div className="min-h-[500px]">
              <ApprovalQueue />
            </div>
          )}

          {activeTab === "users" && isAdmin && (
            <UserManagementTab
              users={users}
              isOwner={isOwner}
              currentUserId={currentUser.id}
              onToggleStatus={toggleUserStatus}
            />
          )}

          {activeTab === "theme" && isAdmin && (
            <ThemeCustomizationTab
              themeCustom={themeCustom}
              onUpdate={(key: keyof ThemeCustomization, value: string) => {
                setThemeCustom({ ...themeCustom, [key]: value });
                setHasUnsavedChanges(true);
              }}
            />
          )}

          {activeTab === "permissions" && isAdmin && (
            <PermissionsTab
              users={users}
              isOwner={isOwner}
              onUpdatePermission={updateUserPermission}
            />
          )}

          {activeTab === "telemetry" && isAdmin && (
            <TelemetryTab
              enabled={telemetryEnabled}
              data={telemetryData}
              users={users}
              onToggle={() => setTelemetryEnabled(!telemetryEnabled)}
              onExport={exportTelemetryReport}
            />
          )}

          {activeTab === "trading" && isAdmin && (
            <TradingControlTab
              users={users}
              isOwner={isOwner}
              currentUserId={currentUser.id}
              onToggleTradingMode={toggleTradingMode}
            />
          )}

          {activeTab === "performance" && isAdmin && <PerformanceDashboard />}

          {activeTab === "github-monitor" && isAdmin && <MonitorDashboard />}
        </div>

        {/* Footer */}
        <div
          style={{
            padding: "16px 24px",
            borderTop: "1px solid rgba(0, 172, 193, 0.2)",
            background: "rgba(15, 23, 42, 0.5)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <button
            onClick={handleReset}
            style={{
              padding: "8px 16px",
              background: "rgba(30, 41, 59, 0.8)",
              border: "1px solid rgba(100, 116, 139, 0.5)",
              color: "#ffffff",
              borderRadius: "8px",
              cursor: "pointer",
              transition: "all 0.15s ease",
              fontSize: "14px",
            }}
          >
            Reset to Defaults
          </button>
          <div style={{ display: "flex", gap: "12px" }}>
            <button
              onClick={onClose}
              style={{
                padding: "8px 20px",
                background: "rgba(30, 41, 59, 0.8)",
                border: "1px solid rgba(100, 116, 139, 0.5)",
                color: "#ffffff",
                borderRadius: "8px",
                cursor: "pointer",
                transition: "all 0.15s ease",
              }}
            >
              Cancel
            </button>
            <button
              onClick={handleSaveSettings}
              disabled={isSaving}
              style={{
                padding: "8px 20px",
                background: "linear-gradient(to right, #00ACC1, #7E57C2)",
                color: "#ffffff",
                fontWeight: "600",
                borderRadius: "8px",
                border: "none",
                cursor: isSaving ? "not-allowed" : "pointer",
                opacity: isSaving ? 0.5 : 1,
                transition: "all 0.15s ease",
                display: "flex",
                alignItems: "center",
                gap: "8px",
              }}
            >
              <Save size={18} />
              {isSaving ? "Saving..." : hasUnsavedChanges ? "Save Changes" : "✓ Saved"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function UserManagementTab({ users, isOwner, currentUserId, onToggleStatus }: unknown) {
  const isMobile = useIsMobile();

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
        <Users size={20} />
        User Management
      </h3>

      {users.map((user: User) => (
        <div key={user.id} className="p-4 bg-slate-800/50 border border-slate-700/50 rounded-xl">
          <div className="flex justify-between items-start mb-3">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <h4 className="text-white font-semibold">{user.name}</h4>
                <span
                  className={`px-2 py-1 rounded text-xs font-semibold ${
                    user.role === "owner"
                      ? "bg-purple-500/20 text-purple-400"
                      : user.role === "beta"
                        ? "bg-cyan-500/20 text-cyan-400"
                        : user.role === "alpha"
                          ? "bg-yellow-500/20 text-yellow-400"
                          : "bg-slate-500/20 text-slate-400"
                  }`}
                >
                  {user.role.toUpperCase()}
                </span>
                <span
                  className={`px-2 py-1 rounded text-xs font-semibold ${
                    user.status === "active"
                      ? "bg-green-500/20 text-green-400"
                      : "bg-red-500/20 text-red-400"
                  }`}
                >
                  {user.status.toUpperCase()}
                </span>
              </div>
              <p className="text-sm text-slate-400">{user.email}</p>
            </div>

            {isOwner && user.id !== currentUserId && (
              <button
                onClick={() => onToggleStatus(user.id)}
                className={`px-3 py-1 rounded text-sm font-medium ${
                  user.status === "active"
                    ? "bg-red-500/20 text-red-400 hover:bg-red-500/30"
                    : "bg-green-500/20 text-green-400 hover:bg-green-500/30"
                }`}
              >
                {user.status === "active" ? "Suspend" : "Activate"}
              </button>
            )}
          </div>

          <div
            className="grid gap-2 text-sm"
            style={{ gridTemplateColumns: isMobile ? "1fr" : "repeat(3, 1fr)" }}
          >
            <div>
              <div className="text-xs text-slate-500">Created</div>
              <div className="text-white">{user.createdAt}</div>
            </div>
            <div>
              <div className="text-xs text-slate-500">Last Login</div>
              <div className="text-white">{user.lastLogin}</div>
            </div>
            <div>
              <div className="text-xs text-slate-500">Trading Mode</div>
              <div
                className={`font-semibold ${user.tradingMode === "live" ? "text-red-400" : "text-yellow-400"}`}
              >
                {user.tradingMode.toUpperCase()}
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

function ThemeCustomizationTab({ themeCustom, onUpdate }: unknown) {
  const isMobile = useIsMobile();

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
        <Palette size={20} />
        Theme Customization
      </h3>

      <div
        className="grid gap-4"
        style={{ gridTemplateColumns: isMobile ? "1fr" : "repeat(2, 1fr)" }}
      >
        {Object.entries(themeCustom).map(([key, value]) => (
          <div key={key}>
            <label className="block text-sm font-medium text-slate-300 mb-2 capitalize">
              {key.replace(/([A-Z])/g, " $1").trim()}
            </label>
            <div className="flex gap-2">
              <input
                type="color"
                value={value as string}
                onChange={(e) => onUpdate(key, e.target.value)}
                className="w-16 h-10 rounded border border-slate-700/50 cursor-pointer"
              />
              <input
                type="text"
                value={value as string}
                onChange={(e) => onUpdate(key, e.target.value)}
                className="flex-1 px-3 py-2 bg-slate-900/60 border border-slate-700/50 rounded text-white"
              />
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 p-3 bg-purple-500/10 border border-purple-500/30 rounded flex items-start gap-2">
        <AlertTriangle size={16} className="text-purple-400 mt-0.5" />
        <p className="text-sm text-purple-400">
          Theme changes will apply system-wide to all users after saving.
        </p>
      </div>
    </div>
  );
}

function PermissionsTab({ users, isOwner, onUpdatePermission }: unknown) {
  const isMobile = useIsMobile();

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
        <Shield size={20} />
        User Permissions
      </h3>

      {users.map((user: User) => (
        <div key={user.id} className="p-4 bg-slate-800/50 border border-slate-700/50 rounded-xl">
          <h4 className="text-white font-semibold mb-3">
            {user.name} ({user.role})
          </h4>

          <div
            className="grid gap-3"
            style={{ gridTemplateColumns: isMobile ? "1fr" : "repeat(2, 1fr)" }}
          >
            {Object.entries(user.permissions).map(([permission, enabled]) => (
              <label
                key={permission}
                className="flex items-center gap-2 cursor-pointer"
                style={{ opacity: isOwner ? 1 : 0.6 }}
              >
                <input
                  type="checkbox"
                  checked={enabled as boolean}
                  onChange={(e) =>
                    isOwner && onUpdatePermission(user.id, permission, e.target.checked)
                  }
                  disabled={!isOwner}
                  className="w-4 h-4"
                />
                <span className="text-sm text-white">
                  {permission.replace(/([A-Z])/g, " $1").trim()}
                </span>
              </label>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

function TelemetryTab({ enabled, data, users, onToggle, onExport }: unknown) {
  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          <Database size={20} />
          Telemetry & Usage Logs
        </h3>

        <button
          onClick={onToggle}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
            enabled
              ? "bg-green-500/20 text-green-400 border border-green-500/50"
              : "bg-slate-800/80 text-slate-400 border border-slate-700/50"
          }`}
        >
          {enabled ? <ToggleRight size={20} /> : <ToggleLeft size={20} />}
          {enabled ? "Enabled" : "Disabled"}
        </button>
      </div>

      {enabled && data.length > 0 && (
        <>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-700/50">
                  <th className="px-3 py-2 text-left text-xs text-slate-400 font-semibold">Time</th>
                  <th className="px-3 py-2 text-left text-xs text-slate-400 font-semibold">User</th>
                  <th className="px-3 py-2 text-left text-xs text-slate-400 font-semibold">
                    Component
                  </th>
                  <th className="px-3 py-2 text-left text-xs text-slate-400 font-semibold">
                    Action
                  </th>
                </tr>
              </thead>
              <tbody>
                {data.map((log: TelemetryData, i: number) => (
                  <tr key={i} className="border-b border-slate-700/30">
                    <td className="px-3 py-2 text-sm text-white">
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </td>
                    <td className="px-3 py-2 text-sm text-white">
                      {users.find((u: User) => u.id === log.userId)?.name || log.userId}
                    </td>
                    <td className="px-3 py-2 text-sm text-slate-400">{log.component}</td>
                    <td className="px-3 py-2">
                      <span className="px-2 py-1 bg-cyan-500/20 text-cyan-400 rounded text-xs font-semibold">
                        {log.action}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <button
            onClick={onExport}
            className="flex items-center gap-2 px-4 py-2 bg-cyan-500 hover:bg-cyan-600 text-white rounded-lg font-medium transition-all"
          >
            <FileText size={18} />
            Export Report
          </button>
        </>
      )}
    </div>
  );
}

function TradingControlTab({ users, isOwner, currentUserId, onToggleTradingMode }: unknown) {
  return (
    <div className="space-y-6">
      {/* Kill Switch Section */}
      <div>
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <Activity size={20} />
          Emergency Kill Switch
        </h3>
        <KillSwitchToggle />
      </div>

      {/* Trading Mode Control Section */}
      <div>
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <Activity size={20} />
          Trading Mode Control (Paper vs Live)
        </h3>

        {!isOwner && (
          <div className="p-3 bg-red-500/10 border border-red-500/30 rounded flex items-start gap-2 mb-4">
            <AlertTriangle size={16} className="text-red-400 mt-0.5" />
            <p className="text-sm text-red-400">
              Only the system owner can toggle between Paper and Live trading modes.
            </p>
          </div>
        )}

        {users.map((user: User) => (
          <div key={user.id} className="p-4 bg-slate-800/50 border border-slate-700/50 rounded-xl">
            <div className="flex justify-between items-center">
              <div>
                <h4 className="text-white font-semibold">{user.name}</h4>
                <p className="text-sm text-slate-400">{user.email}</p>
              </div>

              <div className="flex items-center gap-4">
                <div className="text-right">
                  <div className="text-xs text-slate-400 uppercase">Trading Mode</div>
                  <div
                    className={`text-2xl font-bold ${user.tradingMode === "live" ? "text-red-400" : "text-yellow-400"}`}
                  >
                    {user.tradingMode.toUpperCase()}
                  </div>
                </div>

                <button
                  onClick={() => onToggleTradingMode(user.id)}
                  disabled={!isOwner && user.id !== currentUserId}
                  className={`p-3 rounded-lg border-2 transition-all ${
                    user.tradingMode === "live"
                      ? "bg-red-500/20 border-red-500"
                      : "bg-yellow-500/20 border-yellow-500"
                  } ${!isOwner && user.id !== currentUserId ? "opacity-50 cursor-not-allowed" : "cursor-pointer hover:opacity-80"}`}
                >
                  {user.tradingMode === "live" ? (
                    <ToggleRight size={32} className="text-red-400" />
                  ) : (
                    <ToggleLeft size={32} className="text-yellow-400" />
                  )}
                </button>
              </div>
            </div>

            {user.tradingMode === "live" && (
              <div className="mt-3 p-2 bg-red-500/10 border border-red-500/30 rounded flex items-center gap-2">
                <AlertTriangle size={14} className="text-red-400" />
                <span className="text-xs text-red-400 font-semibold">
                  LIVE TRADING ACTIVE: Real money will be used for all trades.
                </span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
