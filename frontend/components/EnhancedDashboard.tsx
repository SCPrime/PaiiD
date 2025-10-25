import dynamic from "next/dynamic";
import React, { useEffect, useState } from "react";
import Split from "react-split";
import { useIsMobile } from "../hooks/useBreakpoint";
import RadialMenu, { Workflow, workflows } from "./RadialMenu";
import AnimatedCounter from "./ui/AnimatedCounter";
import EnhancedCard from "./ui/EnhancedCard";
import StatusIndicator from "./ui/StatusIndicator";

// Dynamic imports for better performance
const MorningRoutineAI = dynamic(() => import("./MorningRoutineAI"), {
  loading: () => <LoadingSpinner />,
});
const AIRecommendations = dynamic(() => import("./AIRecommendations"), {
  loading: () => <LoadingSpinner />,
});
const MonitorDashboard = dynamic(
  () => import("./MonitorDashboard").then((mod) => ({ default: mod.MonitorDashboard })),
  { loading: () => <LoadingSpinner /> }
);
const Analytics = dynamic(() => import("./Analytics"), {
  loading: () => <LoadingSpinner />,
});
const Backtesting = dynamic(() => import("./Backtesting"), {
  loading: () => <LoadingSpinner />,
});
const NewsReview = dynamic(() => import("./NewsReview"), {
  loading: () => <LoadingSpinner />,
});
const StrategyBuilderAI = dynamic(() => import("./StrategyBuilderAI"), {
  loading: () => <LoadingSpinner />,
});
const PositionManager = dynamic(() => import("./trading/PositionManager"), {
  loading: () => <LoadingSpinner />,
});

import AIChat from "./AIChat";
import CommandPalette from "./CommandPalette";
import CompletePaiiDLogo from "./CompletePaiiDLogo";
import ExecuteTradeForm from "./ExecuteTradeForm";
import KeyboardShortcuts from "./KeyboardShortcuts";
import MarketScanner from "./MarketScanner";
import Settings from "./Settings";
import RiskCalculator from "./trading/RiskCalculator";

// Loading spinner component
const LoadingSpinner: React.FC = () => (
  <div className="flex items-center justify-center p-8">
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
  </div>
);

interface EnhancedDashboardProps {
  selectedWorkflow?: string;
  onWorkflowSelect: (workflowId: string) => void;
  onWorkflowHover?: (workflow: Workflow | null) => void;
  hoveredWorkflow?: Workflow | null;
}

const EnhancedDashboard: React.FC<EnhancedDashboardProps> = ({
  selectedWorkflow,
  onWorkflowSelect,
  onWorkflowHover,
  hoveredWorkflow,
}) => {
  const isMobile = useIsMobile();
  const [systemStatus, setSystemStatus] = useState<"online" | "offline" | "warning">("online");
  const [connectionCount, setConnectionCount] = useState(0);

  // Simulate system status monitoring
  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate status changes
      const statuses: Array<"online" | "offline" | "warning"> = [
        "online",
        "online",
        "online",
        "warning",
      ];
      setSystemStatus(statuses[Math.floor(Math.random() * statuses.length)]);
      setConnectionCount(Math.floor(Math.random() * 100));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const getWorkflowById = (id: string) => {
    return workflows.find((w) => w.id === id);
  };

  const displayWorkflow = selectedWorkflow ? getWorkflowById(selectedWorkflow) : hoveredWorkflow;

  // Render the active workflow component
  const renderWorkflowContent = () => {
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
          return <Settings isOpen={true} onClose={() => onWorkflowSelect("")} />;
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
        default:
          return null;
      }
    }

    // Show workflow description when hovering
    if (displayWorkflow) {
      return (
        <EnhancedCard variant="glass" size="lg" hover glow className="text-center">
          <div className="space-y-4">
            <div className="text-4xl mb-2">{displayWorkflow.icon}</div>
            <h3 className="text-xl font-bold text-white">
              {displayWorkflow.name.replace("\n", " ")}
            </h3>
            <p className="text-slate-300 leading-relaxed">{displayWorkflow.description}</p>
            <div className="flex items-center justify-center gap-2 mt-4">
              <StatusIndicator status={systemStatus} size="sm" />
              <span className="text-sm text-slate-400">System {systemStatus}</span>
            </div>
          </div>
        </EnhancedCard>
      );
    }

    // Default welcome state
    return (
      <EnhancedCard variant="gradient" size="xl" hover glow className="text-center">
        <div className="space-y-6">
          <div className="text-6xl mb-4">🚀</div>
          <h2 className="text-3xl font-bold text-white mb-4">Welcome to PaiiD</h2>
          <p className="text-slate-300 text-lg leading-relaxed max-w-md mx-auto">
            Your Personal Artificial Intelligence Investment Dashboard. Select a workflow from the
            radial menu to get started.
          </p>
          <div className="flex items-center justify-center gap-4 mt-8">
            <StatusIndicator status={systemStatus} label="System Status" />
            <div className="text-sm text-slate-400">
              <AnimatedCounter value={connectionCount} suffix=" connections" color="positive" />
            </div>
          </div>
        </div>
      </EnhancedCard>
    );
  };

  return (
    <div className="h-full w-full bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <Split
        className="h-full w-full"
        sizes={isMobile ? [100, 0] : [30, 70]}
        minSize={isMobile ? 100 : 200}
        maxSize={isMobile ? 100 : 500}
        expandToMin={false}
        gutterSize={4}
        gutterAlign="center"
        snapOffset={30}
        dragInterval={1}
        direction="horizontal"
      >
        {/* Left Panel - Radial Menu */}
        <div className="flex flex-col items-center justify-center p-4 bg-slate-800/50 backdrop-blur-sm">
          <div className="mb-6">
            <CompletePaiiDLogo />
          </div>
          <RadialMenu
            onWorkflowSelect={onWorkflowSelect}
            onWorkflowHover={onWorkflowHover}
            selectedWorkflow={selectedWorkflow}
            compact={isMobile}
          />
        </div>

        {/* Right Panel - Workflow Content */}
        <div className="flex flex-col h-full bg-slate-900/50 backdrop-blur-sm">
          <div className="flex-1 overflow-hidden">{renderWorkflowContent()}</div>
        </div>
      </Split>

      {/* Global Components */}
      <AIChat isOpen={false} onClose={() => {}} />
      <CommandPalette onNavigate={() => {}} />
      <KeyboardShortcuts />
    </div>
  );
};

export default EnhancedDashboard;
