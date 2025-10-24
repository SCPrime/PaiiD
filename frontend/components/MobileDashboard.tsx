import React, { useEffect, useState } from "react";
import { useIsMobile } from "../hooks/useBreakpoint";
import { enhancedWorkflows } from "./EnhancedRadialMenu";
import AnimatedCounter from "./ui/AnimatedCounter";
import EnhancedCard from "./ui/EnhancedCard";
import StatusIndicator from "./ui/StatusIndicator";

interface MobileDashboardProps {
  onWorkflowSelect: (workflowId: string) => void;
  selectedWorkflow?: string;
}

const MobileDashboard: React.FC<MobileDashboardProps> = ({
  onWorkflowSelect,
  selectedWorkflow,
}) => {
  const isMobile = useIsMobile();
  const [activeTab, setActiveTab] = useState<"workflows" | "content">("workflows");
  const [systemStatus, setSystemStatus] = useState<"online" | "offline" | "warning">("online");

  // Simulate system status
  useEffect(() => {
    const interval = setInterval(() => {
      const statuses: Array<"online" | "offline" | "warning"> = ["online", "online", "warning"];
      setSystemStatus(statuses[Math.floor(Math.random() * statuses.length)]);
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  if (!isMobile) {
    return null; // Don't render on desktop
  }

  const selectedWorkflowData = enhancedWorkflows.find((w) => w.id === selectedWorkflow);

  return (
    <div className="h-screen w-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-4 bg-slate-800/50 backdrop-blur-sm border-b border-slate-700/50">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">P</span>
          </div>
          <div>
            <h1 className="text-white font-bold text-lg">PaiiD</h1>
            <div className="flex items-center gap-2">
              <StatusIndicator status={systemStatus} size="sm" />
              <span className="text-xs text-slate-400">Mobile</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveTab("workflows")}
            className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
              activeTab === "workflows" ? "bg-blue-500 text-white" : "bg-slate-700 text-slate-300"
            }`}
          >
            Workflows
          </button>
          <button
            onClick={() => setActiveTab("content")}
            className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
              activeTab === "content" ? "bg-blue-500 text-white" : "bg-slate-700 text-slate-300"
            }`}
          >
            Content
          </button>
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-hidden">
        {activeTab === "workflows" ? (
          <div className="p-4 space-y-3">
            <h2 className="text-white font-semibold text-lg mb-4">Trading Workflows</h2>

            <div className="grid grid-cols-2 gap-3">
              {enhancedWorkflows.map((workflow) => (
                <EnhancedCard
                  key={workflow.id}
                  variant="glass"
                  size="sm"
                  hover
                  className={`cursor-pointer transition-all duration-200 ${
                    selectedWorkflow === workflow.id
                      ? "ring-2 ring-blue-500 scale-105"
                      : "hover:scale-102"
                  }`}
                  onClick={() => onWorkflowSelect(workflow.id)}
                >
                  <div className="text-center space-y-2">
                    <div className="text-2xl">{workflow.icon}</div>
                    <div className="text-xs font-medium text-white leading-tight">
                      {workflow.name.replace("\n", " ")}
                    </div>
                    <div className="flex items-center justify-center">
                      <StatusIndicator
                        status={workflow.status === "loading" ? "loading" : "online"}
                        size="sm"
                      />
                    </div>
                  </div>
                </EnhancedCard>
              ))}
            </div>
          </div>
        ) : (
          <div className="p-4 h-full overflow-y-auto">
            {selectedWorkflowData ? (
              <EnhancedCard variant="gradient" size="lg" className="h-full">
                <div className="space-y-4">
                  <div className="text-center">
                    <div className="text-4xl mb-2">{selectedWorkflowData.icon}</div>
                    <h3 className="text-xl font-bold text-white">
                      {selectedWorkflowData.name.replace("\n", " ")}
                    </h3>
                    <p className="text-slate-300 text-sm mt-2">
                      {selectedWorkflowData.description}
                    </p>
                  </div>

                  <div className="flex items-center justify-center gap-4 mt-6">
                    <StatusIndicator status={systemStatus} label="System" />
                    <div className="text-sm text-slate-400">
                      <AnimatedCounter
                        value={Math.floor(Math.random() * 100)}
                        suffix="% ready"
                        color="positive"
                      />
                    </div>
                  </div>

                  <div className="mt-8 space-y-3">
                    <button className="w-full bg-blue-500 hover:bg-blue-600 text-white font-medium py-3 px-4 rounded-lg transition-colors">
                      Launch {selectedWorkflowData.name.replace("\n", " ")}
                    </button>
                    <button
                      onClick={() => setActiveTab("workflows")}
                      className="w-full bg-slate-700 hover:bg-slate-600 text-slate-300 font-medium py-2 px-4 rounded-lg transition-colors"
                    >
                      Back to Workflows
                    </button>
                  </div>
                </div>
              </EnhancedCard>
            ) : (
              <EnhancedCard
                variant="gradient"
                size="lg"
                className="h-full flex items-center justify-center"
              >
                <div className="text-center space-y-4">
                  <div className="text-6xl">🚀</div>
                  <h2 className="text-2xl font-bold text-white">Welcome to PaiiD</h2>
                  <p className="text-slate-300">
                    Select a workflow to get started with your trading dashboard.
                  </p>
                  <button
                    onClick={() => setActiveTab("workflows")}
                    className="bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-6 rounded-lg transition-colors"
                  >
                    Choose Workflow
                  </button>
                </div>
              </EnhancedCard>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default MobileDashboard;
