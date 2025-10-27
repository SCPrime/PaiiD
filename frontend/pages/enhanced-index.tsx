import { useEffect, useState } from "react";
import AIChat from "../components/AIChat";
import CommandPalette from "../components/CommandPalette";
import EnhancedDashboard from "../components/EnhancedDashboard";
import KeyboardShortcuts from "../components/KeyboardShortcuts";
import MobileDashboard from "../components/MobileDashboard";
import type { Workflow } from "../components/RadialMenu";
import Settings from "../components/Settings";
import UserSetupAI from "../components/UserSetupAI";
import { useIsMobile } from "../hooks/useBreakpoint";
import { logger } from "../lib/logger";
import { initializeSession } from "../lib/userManagement";

// Development bypass flag
const ENABLE_DEV_BYPASS =
  process.env.NODE_ENV === "development" &&
  typeof window !== "undefined" &&
  window.location.search.includes("bypass=true");

export default function EnhancedDashboardPage() {
  const [isLoading, setIsLoading] = useState(true);
  const [isUserSetup, setIsUserSetup] = useState(ENABLE_DEV_BYPASS);
  const [selectedWorkflow, setSelectedWorkflow] = useState<string>("");
  const [hoveredWorkflow, setHoveredWorkflow] = useState<Workflow | null>(null);
  const [showSettings, setShowSettings] = useState(false);
  const [aiChatOpen, setAiChatOpen] = useState(false);
  const isMobile = useIsMobile();

  // Initialize session and loading state
  useEffect(() => {
    const init = async () => {
      try {
        if (!ENABLE_DEV_BYPASS) {
          await initializeSession();
        }
        setIsLoading(false);
      } catch (error) {
        logger.error("Session initialization failed", error);
        setIsLoading(false);
      }
    };

    init();
  }, []);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Cmd/Ctrl + K for command palette
      if ((event.metaKey || event.ctrlKey) && event.key === "k") {
        event.preventDefault();
        // Command palette is handled by the component
      }

      // Cmd/Ctrl + , for settings
      if ((event.metaKey || event.ctrlKey) && event.key === ",") {
        event.preventDefault();
        setShowSettings(true);
      }

      // Cmd/Ctrl + / for AI chat
      if ((event.metaKey || event.ctrlKey) && event.key === "/") {
        event.preventDefault();
        setAiChatOpen(true);
      }

      // Escape to close modals
      if (event.key === "Escape") {
        setShowSettings(false);
        setAiChatOpen(false);
        setSelectedWorkflow("");
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

  // Show loading state
  if (isLoading) {
    return (
      <div className="h-screen w-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <div className="text-white text-lg font-medium">Loading PaiiD...</div>
          <div className="text-slate-400 text-sm">Initializing your trading dashboard</div>
        </div>
      </div>
    );
  }

  // Show user setup modal if not set up
  if (!ENABLE_DEV_BYPASS && !isUserSetup) {
    return <UserSetupAI onComplete={handleUserSetupComplete} />;
  }

  return (
    <>
      {/* Development Mode Banner */}
      {ENABLE_DEV_BYPASS && (
        <div className="fixed top-0 left-0 right-0 bg-gradient-to-r from-amber-500 to-red-500 text-white py-2 px-4 text-center text-sm font-semibold z-50 shadow-lg">
          🔧 DEVELOPMENT MODE | Onboarding Bypass Active | Press Ctrl+Shift+A for Manual Toggle
        </div>
      )}

      {/* Main Dashboard */}
      {isMobile ? (
        <MobileDashboard
          onWorkflowSelect={setSelectedWorkflow}
          selectedWorkflow={selectedWorkflow}
        />
      ) : (
        <EnhancedDashboard
          selectedWorkflow={selectedWorkflow}
          onWorkflowSelect={setSelectedWorkflow}
          onWorkflowHover={setHoveredWorkflow}
          hoveredWorkflow={hoveredWorkflow}
        />
      )}

      {/* Global Components */}
      <CommandPalette onNavigate={setSelectedWorkflow} />

      <Settings isOpen={showSettings} onClose={() => setShowSettings(false)} />

      <AIChat
        isOpen={aiChatOpen}
        onClose={() => setAiChatOpen(false)}
        initialMessage="Hi! I'm your PaiiD AI assistant. I can help you with trading strategies, build custom workflows, analyze market data, or adjust your preferences. What would you like to know?"
      />

      <KeyboardShortcuts
        onOpenTrade={() => setSelectedWorkflow("execute")}
        onQuickBuy={() => setSelectedWorkflow("execute")}
        onQuickSell={() => setSelectedWorkflow("execute")}
        onCloseModal={() => setSelectedWorkflow("")}
      />
    </>
  );
}
