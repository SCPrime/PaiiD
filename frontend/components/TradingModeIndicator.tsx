/**
 * Trading Mode Indicator
 * Prominent indicator showing paper/live trading mode with safety warnings
 */

import { AlertTriangle, Shield, Zap, Settings } from "lucide-react";
import { useState, useEffect } from "react";
import { theme } from "../styles/theme";

interface TradingModeIndicatorProps {
  mode?: "paper" | "live";
  onModeChange?: (mode: "paper" | "live") => void;
  className?: string;
}

export default function TradingModeIndicator({ 
  mode = "paper", 
  onModeChange,
  className = "" 
}: TradingModeIndicatorProps) {
  const [isChanging, setIsChanging] = useState(false);
  const [showWarning, setShowWarning] = useState(false);

  // Get mode from localStorage if not provided
  useEffect(() => {
    const savedMode = localStorage.getItem("trading-mode") as "paper" | "live" | null;
    if (savedMode && onModeChange) {
      onModeChange(savedMode);
    }
  }, [onModeChange]);

  const handleModeChange = async (newMode: "paper" | "live") => {
    if (newMode === "live") {
      setShowWarning(true);
      return;
    }

    setIsChanging(true);
    
    // Save to localStorage
    localStorage.setItem("trading-mode", newMode);
    
    // Call parent handler
    if (onModeChange) {
      onModeChange(newMode);
    }

    // Reset state
    setTimeout(() => {
      setIsChanging(false);
    }, 1000);
  };

  const confirmLiveMode = () => {
    setShowWarning(false);
    handleModeChange("live");
  };

  const cancelLiveMode = () => {
    setShowWarning(false);
  };

  const isLive = mode === "live";
  const isPaper = mode === "paper";

  return (
    <>
      {/* Main Indicator */}
      <div className={`relative ${className}`}>
        <div
          className={`
            flex items-center gap-2 px-4 py-2 rounded-lg font-semibold text-sm
            transition-all duration-300 cursor-pointer
            ${isLive 
              ? "bg-red-100 text-red-800 border-2 border-red-300 hover:bg-red-200" 
              : "bg-green-100 text-green-800 border-2 border-green-300 hover:bg-green-200"
            }
            ${isChanging ? "opacity-50 pointer-events-none" : ""}
          `}
          onClick={() => handleModeChange(isLive ? "paper" : "live")}
          style={{
            backdropFilter: "blur(10px)",
            boxShadow: isLive 
              ? "0 4px 12px rgba(239, 68, 68, 0.2)" 
              : "0 4px 12px rgba(34, 197, 94, 0.2)",
          }}
        >
          {isLive ? (
            <>
              <Zap className="w-4 h-4" />
              <span>LIVE TRADING</span>
              <AlertTriangle className="w-4 h-4" />
            </>
          ) : (
            <>
              <Shield className="w-4 h-4" />
              <span>PAPER TRADING</span>
            </>
          )}
          
          {isChanging && (
            <div className="ml-2">
              <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
            </div>
          )}
        </div>

        {/* Mode Description */}
        <div className="mt-1 text-xs text-gray-600">
          {isLive ? (
            <span className="text-red-600 font-medium">
              ⚠️ Real money at risk - trades will execute
            </span>
          ) : (
            <span className="text-green-600">
              ✅ Safe practice mode - no real money
            </span>
          )}
        </div>
      </div>

      {/* Live Mode Warning Modal */}
      {showWarning && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 max-w-md mx-4 shadow-2xl">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                <AlertTriangle className="w-6 h-6 text-red-600" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-gray-900">Switch to Live Trading?</h3>
                <p className="text-sm text-gray-600">This will use real money</p>
              </div>
            </div>

            <div className="space-y-3 mb-6">
              <div className="flex items-start gap-2 text-sm text-gray-700">
                <span className="text-red-500 mt-0.5">•</span>
                <span>All trades will execute with real money</span>
              </div>
              <div className="flex items-start gap-2 text-sm text-gray-700">
                <span className="text-red-500 mt-0.5">•</span>
                <span>You can lose money on trades</span>
              </div>
              <div className="flex items-start gap-2 text-sm text-gray-700">
                <span className="text-red-500 mt-0.5">•</span>
                <span>Make sure you understand the risks</span>
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={confirmLiveMode}
                className="flex-1 bg-red-600 text-white py-2 px-4 rounded-lg font-semibold hover:bg-red-700 transition-colors"
              >
                Yes, Go Live
              </button>
              <button
                onClick={cancelLiveMode}
                className="flex-1 bg-gray-200 text-gray-800 py-2 px-4 rounded-lg font-semibold hover:bg-gray-300 transition-colors"
              >
                Stay Safe
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

// Compact version for headers/toolbars
export function CompactTradingModeIndicator({ 
  mode = "paper", 
  onModeChange,
  className = "" 
}: TradingModeIndicatorProps) {
  const isLive = mode === "live";

  return (
    <div className={`flex items-center gap-1 ${className}`}>
      <div
        className={`
          w-3 h-3 rounded-full
          ${isLive ? "bg-red-500" : "bg-green-500"}
        `}
      />
      <span className="text-xs font-medium text-gray-600">
        {isLive ? "LIVE" : "PAPER"}
      </span>
    </div>
  );
}
