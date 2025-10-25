import dynamic from "next/dynamic";
import { useEffect, useState } from "react";
import Split from "react-split";
import RadialMenu, { Workflow, workflows } from "../components/RadialMenu";
import { LOGO_ANIMATION_KEYFRAME } from "../styles/logoConstants";

import ExecuteTradeForm from "../components/ExecuteTradeForm";
import MobileDashboard from "../components/MobileDashboard";
import Settings from "../components/Settings";
import UserSetupAI from "../components/UserSetupAI";

// Dynamic imports for code splitting (loads only when needed)
const MorningRoutineAI = dynamic(() => import("../components/MorningRoutineAI"), {
  loading: () => (
    <div className="flex items-center justify-center p-8">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
    </div>
  ),
});
const AIRecommendations = dynamic(() => import("../components/AIRecommendations"), {
  loading: () => (
    <div className="flex items-center justify-center p-8">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
    </div>
  ),
});
const MonitorDashboard = dynamic(
  () => import("../components/MonitorDashboard").then((mod) => ({ default: mod.MonitorDashboard })),
  {
    loading: () => (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    ),
  }
);
const Analytics = dynamic(() => import("../components/Analytics"), {
  loading: () => (
    <div className="flex items-center justify-center p-8">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
    </div>
  ),
});
const Backtesting = dynamic(() => import("../components/Backtesting"), {
  loading: () => (
    <div className="flex items-center justify-center p-8">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
    </div>
  ),
});
const MLIntelligenceWorkflow = dynamic(
  () => import("../components/workflows/MLIntelligenceWorkflow"),
  {
    loading: () => (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    ),
  }
);
const GitHubActionsMonitor = dynamic(() => import("../components/GitHubActionsMonitor"), {
  loading: () => (
    <div className="flex items-center justify-center p-8">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
    </div>
  ),
});
const NewsReview = dynamic(() => import("../components/NewsReview"), {
  loading: () => (
    <div className="flex items-center justify-center p-8">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
    </div>
  ),
});
const StrategyBuilderAI = dynamic(() => import("../components/StrategyBuilderAI"), {
  loading: () => (
    <div className="flex items-center justify-center p-8">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
    </div>
  ),
});
const PositionManager = dynamic(() => import("../components/trading/PositionManager"), {
  loading: () => (
    <div className="flex items-center justify-center p-8">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
    </div>
  ),
});

import AIChat from "../components/AIChat";
import CommandPalette from "../components/CommandPalette";
import CompletePaiiDLogo from "../components/CompletePaiiDLogo";
import HelpPanel from "../components/HelpPanel";
import KeyboardShortcuts from "../components/KeyboardShortcuts";
import MarketScanner from "../components/MarketScanner";
import TradingModeIndicator from "../components/TradingModeIndicator";
import RiskCalculator from "../components/trading/RiskCalculator";
import { ToastContainer, useToast } from "../components/ui/Toast";
import { useIsMobile } from "../hooks/useBreakpoint";
import { HelpProvider, useHelp } from "../hooks/useHelp";
import { initializeSession } from "../lib/userManagement";

export default function Dashboard() {
  // Development bypass: Skip onboarding in development mode
  const ENABLE_DEV_BYPASS = process.env.NODE_ENV === "development";

  const [selectedWorkflow, setSelectedWorkflow] = useState<string>("");
  const [hoveredWorkflow, setHoveredWorkflow] = useState<Workflow | null>(null);
  const [showSettings, setShowSettings] = useState(false);
  const [isUserSetup, setIsUserSetup] = useState(false); // Start with onboarding
  const [isLoading, setIsLoading] = useState(true);
  const [aiChatOpen, setAiChatOpen] = useState(false);
  const [tradingMode, setTradingMode] = useState<"paper" | "live">("paper");

  // Help system
  const { isHelpPanelOpen, openHelpPanel, closeHelpPanel } = useHelp();

  // Toast notifications
  const toast = useToast();

  // Detect mobile viewport
  const isMobile = useIsMobile();

  // Check if user is set up on mount
  useEffect(() => {
    const setupComplete =
      typeof window !== "undefined"
        ? localStorage.getItem("user-setup-complete") === "true"
        : false;

    setIsUserSetup(setupComplete);
    setIsLoading(false);
  }, []);

  // Owner bypass keyboard combo (Ctrl+Shift+A or Cmd+Shift+A)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Check for Ctrl+Shift+A (Windows/Linux) or Cmd+Shift+A (Mac)
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === "A") {
        e.preventDefault();
        console.info("[PaiiD] 🔓 Admin bypass activated");

        // Set localStorage flags
        if (typeof window !== "undefined") {
          localStorage.setItem("user-setup-complete", "true");
          localStorage.setItem("admin-bypass", "true");
          localStorage.setItem("bypass-timestamp", new Date().toISOString());
        }

        // Skip onboarding
        setIsUserSetup(true);
        initializeSession();

        // Show notification (you can replace with a toast library)
        alert("🔓 Admin bypass activated! Welcome to PaiiD.");
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  // Handle user setup completion
  const handleUserSetupComplete = () => {
    setIsUserSetup(true);
    initializeSession();
  };

  // Show loading state briefly
  if (isLoading) {
    return null;
  }

  // Show user setup modal if not set up (unless development bypass is enabled)
  if (!ENABLE_DEV_BYPASS && !isUserSetup) {
    return <UserSetupAI onComplete={handleUserSetupComplete} />;
  }

  // Use mobile dashboard for mobile devices
  if (isMobile) {
    return (
      <MobileDashboard onWorkflowSelect={setSelectedWorkflow} selectedWorkflow={selectedWorkflow} />
    );
  }

  const getWorkflowById = (id: string) => {
    return workflows.find((w) => w.id === id);
  };

  const displayWorkflow = selectedWorkflow ? getWorkflowById(selectedWorkflow) : hoveredWorkflow;

  // Render the active workflow component or description
  const renderWorkflowContent = () => {
    // If a workflow is selected, render its component
    if (selectedWorkflow) {
      switch (selectedWorkflow) {
        case "morning-routine":
          return <MorningRoutineAI />;

        case "active-positions":
          return <PositionManager />;

        case "execute":
          return <ExecuteTradeForm />;

        case "proposal-review":
          return <RiskCalculator onCreateProposal={() => {}} onExecuteProposal={() => {}} />;

        case "research":
          return <MarketScanner />;

        case "proposals":
          return <AIRecommendations />;

        case "settings":
          return <Settings isOpen={true} onClose={() => setSelectedWorkflow("")} />;

        case "pnl-dashboard":
          return <Analytics />;

        case "news-review":
          return <NewsReview />;

        case "strategy-builder":
          return <StrategyBuilderAI />;

        case "backtesting":
          return <Backtesting />;

        case "monitor":
          return <MonitorDashboard />;

        case "ml-intelligence":
          return <MLIntelligenceWorkflow onClose={() => setSelectedWorkflow(null)} />;

        case "github-monitor":
          return <GitHubActionsMonitor repository="SCPrime/PaiiD" />;

        default:
          return null;
      }
    }

    // If hovering (but not selected), show description
    if (displayWorkflow) {
      return (
        <div
          style={{
            background: "rgba(30, 41, 59, 0.8)",
            backdropFilter: "blur(10px)",
            border: `1px solid ${displayWorkflow.color}40`,
            borderRadius: "16px",
            padding: "20px",
            minHeight: "100px",
            animation: "slideUp 0.4s ease-out",
          }}
        >
          <h4
            style={{
              color: displayWorkflow.color,
              fontSize: "1.1rem",
              margin: 0,
              marginBottom: "10px",
            }}
          >
            {displayWorkflow.icon} {displayWorkflow.name.replace("\n", " ")}
          </h4>
          <p
            style={{
              color: "#cbd5e1",
              lineHeight: 1.5,
              margin: 0,
            }}
          >
            {displayWorkflow.description}
          </p>
        </div>
      );
    }

    // Default welcome message
    return (
      <div
        style={{
          background: "rgba(30, 41, 59, 0.8)",
          backdropFilter: "blur(10px)",
          border: "1px solid rgba(255, 255, 255, 0.1)",
          borderRadius: "16px",
          padding: "20px",
          minHeight: "100px",
        }}
      >
        <h4
          style={{
            color: "#7E57C2",
            fontSize: "1.1rem",
            margin: 0,
            marginBottom: "10px",
          }}
        >
          Welcome to Your Trading Dashboard
        </h4>
        <p
          style={{
            color: "#cbd5e1",
            lineHeight: 1.5,
            margin: 0,
          }}
        >
          Select a workflow stage from the radial menu above to begin. Each segment represents a key
          phase in your trading routine, from morning market analysis to strategy execution.
        </p>
      </div>
    );
  };

  return (
    <HelpProvider>
      {/* Command Palette (Cmd+K) */}
      <CommandPalette onNavigate={setSelectedWorkflow} />

      {/* Development Mode Banner */}
      {ENABLE_DEV_BYPASS && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            background: "linear-gradient(90deg, #f59e0b 0%, #ef4444 100%)",
            color: "#fff",
            padding: "8px 16px",
            textAlign: "center",
            fontSize: "13px",
            fontWeight: "600",
            zIndex: 9999,
            boxShadow: "0 2px 8px rgba(0,0,0,0.3)",
          }}
        >
          🔧 DEVELOPMENT MODE | Onboarding Bypass Active | Press Ctrl+Shift+A for Manual Toggle
        </div>
      )}

      {!selectedWorkflow ? (
        // Full screen view when no workflow selected
        <div
          style={{
            width: "100vw",
            height: "100vh",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "flex-start",
            background: "linear-gradient(135deg, #0f1828 0%, #1a2a3f 100%)",
            overflow: "hidden",
            padding: 0,
            margin: 0,
            position: "relative",
            paddingTop: ENABLE_DEV_BYPASS ? "40px" : "0",
          }}
        >
          {/* Radial Menu Container - centered and scaled to fit */}
          <div
            style={{
              flex: 1,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              width: "100%",
              maxHeight: "calc(100vh - 60px)",
              overflow: "hidden",
              paddingTop: "0",
              paddingBottom: "0",
            }}
          >
            <div
              style={{
                transform: "scale(0.65)",
                transformOrigin: "center center",
              }}
            >
              <RadialMenu
                onWorkflowSelect={setSelectedWorkflow}
                onWorkflowHover={setHoveredWorkflow}
              />
            </div>
          </div>

          {/* Bottom Info Bar - absolute positioned */}
          <div
            style={{
              position: "absolute",
              bottom: 0,
              left: 0,
              right: 0,
              background: "rgba(15, 24, 40, 0.95)",
              backdropFilter: "blur(10px)",
              borderTop: "1px solid rgba(16, 185, 129, 0.2)",
              padding: isMobile ? "12px 16px" : "16px 24px",
              display: "flex",
              justifyContent: isMobile ? "center" : "space-between",
              alignItems: "center",
              zIndex: 10,
              flexDirection: isMobile ? "column" : "row",
              gap: isMobile ? "8px" : "0",
            }}
          >
            {/* Empty left space for symmetry - hide on mobile */}
            {!isMobile && <div></div>}

            {/* Keyboard Hints - hide on mobile (touch devices don't use keyboard) */}
            {!isMobile && (
              <div
                style={{
                  fontSize: "0.875rem",
                  color: "#94a3b8",
                  display: "flex",
                  alignItems: "center",
                  gap: "12px",
                }}
              >
                <span>
                  <kbd
                    style={{
                      background: "rgba(255, 255, 255, 0.1)",
                      padding: "2px 8px",
                      borderRadius: "4px",
                      fontFamily: "monospace",
                      color: "#e2e8f0",
                      marginRight: "4px",
                    }}
                  >
                    Tab
                  </kbd>
                  focus
                </span>
                <span>
                  <kbd
                    style={{
                      background: "rgba(255, 255, 255, 0.1)",
                      padding: "2px 8px",
                      borderRadius: "4px",
                      fontFamily: "monospace",
                      color: "#e2e8f0",
                      marginRight: "4px",
                    }}
                  >
                    Enter
                  </kbd>
                  select
                </span>
                <span>
                  <kbd
                    style={{
                      background: "rgba(255, 255, 255, 0.1)",
                      padding: "2px 8px",
                      borderRadius: "4px",
                      fontFamily: "monospace",
                      color: "#e2e8f0",
                      marginRight: "4px",
                    }}
                  >
                    ← →
                  </kbd>
                  rotate
                </span>
                <span>
                  <kbd
                    style={{
                      background: "rgba(26, 117, 96, 0.2)",
                      padding: "2px 8px",
                      borderRadius: "4px",
                      fontFamily: "monospace",
                      color: "#45f0c0",
                      marginRight: "4px",
                      boxShadow: "0 0 8px rgba(69, 240, 192, 0.3)",
                    }}
                  >
                    Ctrl+Shift+A
                  </kbd>
                  admin
                </span>
              </div>
            )}

            {/* Hover Description */}
            <div
              style={{
                color: "#cbd5e1",
                fontSize: isMobile ? "12px" : "14px",
                fontStyle: "italic",
                maxWidth: isMobile ? "100%" : "300px",
                textAlign: isMobile ? "center" : "right",
                padding: isMobile ? "0 8px" : "0",
              }}
            >
              {hoveredWorkflow
                ? hoveredWorkflow.description
                : isMobile
                  ? "Tap a segment"
                  : "Hover over segments for details"}
            </div>
          </div>
        </div>
      ) : isMobile ? (
        // Mobile: Stacked layout (no split view)
        <div
          style={{
            width: "100%",
            height: "100vh",
            display: "flex",
            flexDirection: "column",
            background: "linear-gradient(135deg, #0f1828 0%, #1a2a3f 100%)",
            overflow: "hidden",
          }}
        >
          {/* Mobile Header with Back Button */}
          <div
            style={{
              padding: "12px 16px",
              background: "rgba(15, 24, 40, 0.95)",
              borderBottom: "1px solid rgba(16, 185, 129, 0.2)",
              display: "flex",
              alignItems: "center",
              gap: "12px",
              minHeight: "56px",
            }}
          >
            {/* Back Button */}
            <button
              onClick={() => setSelectedWorkflow("")}
              style={{
                background: "rgba(16, 185, 129, 0.1)",
                border: "1px solid rgba(16, 185, 129, 0.3)",
                borderRadius: "8px",
                padding: "8px 12px",
                color: "#10b981",
                fontSize: "14px",
                fontWeight: "600",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: "4px",
              }}
            >
              ← Menu
            </button>

            {/* Current Workflow Title */}
            {displayWorkflow && (
              <div
                style={{
                  flex: 1,
                  fontSize: "16px",
                  fontWeight: "700",
                  color: displayWorkflow.color,
                }}
              >
                {displayWorkflow.icon} {displayWorkflow.name.replace("\n", " ")}
              </div>
            )}
          </div>

          {/* Workflow Content - Full Width */}
          <div
            style={{
              flex: 1,
              overflowY: "auto",
              overflowX: "hidden",
              padding: "16px",
              color: "#e2e8f0",
            }}
          >
            {renderWorkflowContent()}
          </div>
        </div>
      ) : (
        // Desktop/Tablet: Split view when workflow selected
        <Split
          sizes={[40, 60]}
          minSize={[350, 400]}
          expandToMin={false}
          gutterSize={8}
          gutterAlign="center"
          snapOffset={30}
          dragInterval={1}
          direction="horizontal"
          cursor="col-resize"
          className="split"
        >
          {/* Left panel - radial menu with header */}
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              height: "100vh",
              background: "linear-gradient(135deg, #0f1828 0%, #1a2a3f 100%)",
              overflow: "hidden",
            }}
          >
            {/* Header with Logo, Help, and Trading Mode */}
            <div
              style={{
                padding: "20px 16px 10px",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: "12px",
              }}
            >
              {/* Logo */}
              <CompletePaiiDLogo size={64} />

              {/* Help Button */}
              <button
                onClick={openHelpPanel}
                style={{
                  background: "rgba(59, 130, 246, 0.1)",
                  border: "1px solid rgba(59, 130, 246, 0.3)",
                  borderRadius: "8px",
                  padding: "8px 12px",
                  color: "#3b82f6",
                  fontSize: "12px",
                  fontWeight: "600",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: "4px",
                  transition: "all 0.2s ease",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = "rgba(59, 130, 246, 0.2)";
                  e.currentTarget.style.transform = "translateY(-1px)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = "rgba(59, 130, 246, 0.1)";
                  e.currentTarget.style.transform = "translateY(0)";
                }}
              >
                ❓ Help
              </button>

              {/* Trading Mode Indicator */}
              <TradingModeIndicator mode={tradingMode} onModeChange={setTradingMode} />
            </div>

            {/* Radial Menu */}
            <div
              style={{
                flex: 1,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <div
                style={{
                  transform: "scale(0.5)",
                  transformOrigin: "center center",
                }}
              >
                <RadialMenu
                  onWorkflowSelect={setSelectedWorkflow}
                  onWorkflowHover={setHoveredWorkflow}
                  selectedWorkflow={selectedWorkflow}
                  compact={true}
                />
              </div>
            </div>
          </div>

          {/* Right panel - workflow content */}
          <div
            style={{
              overflowY: "auto",
              overflowX: "hidden",
              height: "100vh",
              background: "linear-gradient(135deg, #0f1828 0%, #1a2a3f 100%)",
              padding: "20px",
              color: "#e2e8f0",
            }}
          >
            {renderWorkflowContent()}
          </div>
        </Split>
      )}

      {/* Animations */}
      <style jsx>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(-20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes pulse {
          0%,
          100% {
            opacity: 1;
            transform: scale(1);
          }
          50% {
            opacity: 0.6;
            transform: scale(1.2);
          }
        }

        @keyframes slideInRight {
          from {
            opacity: 0;
            transform: translateX(100px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }

        ${LOGO_ANIMATION_KEYFRAME}

        /* React-split gutter styles - Claude-inspired */
        :global(.split-container) {
          width: 100%;
        }

        :global(.gutter) {
          background-color: rgba(30, 41, 59, 0.8) !important;
          background-repeat: no-repeat;
          background-position: center;
          transition: all 0.2s ease;
          border: none !important;
          position: relative;
          backdrop-filter: blur(10px);
        }

        :global(.gutter:hover) {
          background-color: rgba(16, 185, 129, 0.15) !important;
        }

        :global(.gutter:active) {
          background-color: rgba(16, 185, 129, 0.25) !important;
        }

        :global(.gutter-horizontal) {
          cursor: col-resize !important;
          position: relative;
        }

        /* Grip indicator - vertical dots like Claude */
        :global(.gutter-horizontal::before) {
          content: "";
          position: absolute;
          left: 50%;
          top: 50%;
          transform: translate(-50%, -50%);
          width: 3px;
          height: 40px;
          background: linear-gradient(
            to bottom,
            transparent 0%,
            rgba(16, 185, 129, 0.4) 20%,
            rgba(16, 185, 129, 0.6) 50%,
            rgba(16, 185, 129, 0.4) 80%,
            transparent 100%
          );
          border-radius: 2px;
          transition: all 0.2s ease;
        }

        :global(.gutter-horizontal:hover::before) {
          background: linear-gradient(
            to bottom,
            transparent 0%,
            rgba(16, 185, 129, 0.6) 20%,
            rgba(16, 185, 129, 0.9) 50%,
            rgba(16, 185, 129, 0.6) 80%,
            transparent 100%
          );
          height: 60px;
          box-shadow: 0 0 10px rgba(16, 185, 129, 0.3);
        }

        :global(.gutter-horizontal:active::before) {
          background: rgba(16, 185, 129, 1);
          height: 80px;
          box-shadow: 0 0 20px rgba(16, 185, 129, 0.5);
        }

        :global(.left-panel),
        :global(.right-panel) {
          overflow-y: auto;
          height: 100vh;
        }
      `}</style>

      {/* Settings Modal */}
      <Settings isOpen={showSettings} onClose={() => setShowSettings(false)} />

      {/* AI Chat Modal */}
      <AIChat
        isOpen={aiChatOpen}
        onClose={() => setAiChatOpen(false)}
        initialMessage="Hi! I'm your PaiiD AI assistant. I can help you with trading strategies, build custom workflows, analyze market data, or adjust your preferences. What would you like to know?"
      />

      {/* Keyboard Shortcuts */}
      <KeyboardShortcuts
        onOpenTrade={() => setSelectedWorkflow("execute")}
        onQuickBuy={() => setSelectedWorkflow("execute")}
        onQuickSell={() => setSelectedWorkflow("execute")}
        onCloseModal={() => setSelectedWorkflow("")}
      />

      {/* Help Panel */}
      <HelpPanel isOpen={isHelpPanelOpen} onClose={closeHelpPanel} />

      {/* Toast Notifications */}
      <ToastContainer toasts={toast.toasts} onRemove={toast.removeToast} />
    </HelpProvider>
  );
}
