"use client";

import { AlertTriangle, CheckCircle2, Power, Shield } from "lucide-react";
import { useEffect, useState } from "react";
import { logger } from "../lib/logger";
import { showError, showSuccess } from "../lib/toast";

interface KillSwitchToggleProps {
  /** Whether component is standalone or embedded in Settings */
  standalone?: boolean;
}

export default function KillSwitchToggle({ standalone = false }: KillSwitchToggleProps) {
  const [tradingHalted, setTradingHalted] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(false);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [pendingState, setPendingState] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastChecked, setLastChecked] = useState<Date | null>(null);

  // Fetch current kill-switch status
  const fetchStatus = async () => {
    try {
      const res = await fetch("/api/proxy/api/orders");
      if (res.ok) {
        // If orders endpoint works, trading is active
        setTradingHalted(false);
        setLastChecked(new Date());
      }
    } catch (err: unknown) {
      logger.error("Error fetching kill-switch status", err);
      setError("Unable to determine status");
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const handleToggle = async () => {
    setLoading(true);
    setError(null);

    try {
      const res = await fetch("/api/proxy/api/admin/kill", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(pendingState),
      });

      if (!res.ok) {
        throw new Error(`Failed to update kill-switch: ${res.status}`);
      }

      const data = await res.json();
      setTradingHalted(data.tradingHalted);
      setShowConfirmation(false);
      setLastChecked(new Date());

      // Show success toast
      showSuccess(
        data.tradingHalted
          ? "✅ Trading halted successfully - All order submissions blocked"
          : "▶️ Trading resumed - Orders can now be submitted"
      );
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Failed to update kill-switch";
      setError(errorMessage);
      logger.error("Kill-switch error", err);

      // Show error toast
      showError(`Failed to update kill-switch: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const openConfirmation = (newState: boolean) => {
    setPendingState(newState);
    setShowConfirmation(true);
  };

  const containerClass = standalone
    ? "p-6 bg-slate-800/50 border border-slate-700/50 rounded-xl"
    : "space-y-4";

  return (
    <div className={containerClass}>
      {/* Header (only for standalone) */}
      {standalone && (
        <div className="flex items-center gap-2 mb-4">
          <Power size={24} className="text-red-400" />
          <h3 className="text-xl font-semibold text-white">Kill Switch</h3>
        </div>
      )}

      {/* Current Status */}
      <div className="p-4 bg-slate-900/40 border border-slate-700/30 rounded-lg">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            <div
              className={`w-4 h-4 rounded-full animate-pulse ${
                tradingHalted === null
                  ? "bg-gray-500"
                  : tradingHalted
                    ? "bg-red-500"
                    : "bg-green-500"
              }`}
            />
            <div>
              <div className="text-sm font-medium text-slate-300">Trading Status</div>
              <div
                className={`text-2xl font-bold ${
                  tradingHalted === null
                    ? "text-gray-400"
                    : tradingHalted
                      ? "text-red-400"
                      : "text-green-400"
                }`}
              >
                {tradingHalted === null ? "Loading..." : tradingHalted ? "HALTED" : "ACTIVE"}
              </div>
            </div>
          </div>

          {/* Toggle Button */}
          {tradingHalted !== null && (
            <button
              onClick={() => openConfirmation(!tradingHalted)}
              disabled={loading}
              className={`px-6 py-3 rounded-lg font-semibold transition-all ${
                tradingHalted
                  ? "bg-green-500/20 hover:bg-green-500/30 text-green-400 border-2 border-green-500"
                  : "bg-red-500/20 hover:bg-red-500/30 text-red-400 border-2 border-red-500"
              } ${loading ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
            >
              {loading ? "Updating..." : tradingHalted ? "▶ Resume Trading" : "⏸ Halt Trading"}
            </button>
          )}
        </div>

        {lastChecked && (
          <div className="text-xs text-slate-500">
            Last checked: {lastChecked.toLocaleTimeString()}
          </div>
        )}
      </div>

      {/* Warning Message */}
      {!tradingHalted && tradingHalted !== null && (
        <div className="p-3 bg-green-500/10 border border-green-500/30 rounded flex items-start gap-2">
          <CheckCircle2 size={16} className="text-green-400 mt-0.5 flex-shrink-0" />
          <div className="text-sm text-green-400">
            <strong>Trading Active:</strong> All order submissions are being processed normally.
          </div>
        </div>
      )}

      {tradingHalted && (
        <div className="p-3 bg-red-500/10 border border-red-500/30 rounded flex items-start gap-2">
          <AlertTriangle size={16} className="text-red-400 mt-0.5 flex-shrink-0" />
          <div className="text-sm text-red-400">
            <strong>Trading Halted:</strong> All order submissions are currently blocked. No new
            trades can be executed until trading is resumed.
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="p-3 bg-red-500/10 border border-red-500/30 rounded flex items-start gap-2">
          <AlertTriangle size={16} className="text-red-400 mt-0.5 flex-shrink-0" />
          <div className="text-sm text-red-400">{error}</div>
        </div>
      )}

      {/* Admin Only Notice */}
      <div className="p-3 bg-purple-500/10 border border-purple-500/30 rounded flex items-start gap-2">
        <Shield size={16} className="text-purple-400 mt-0.5 flex-shrink-0" />
        <div className="text-sm text-purple-400">
          <strong>Admin Only:</strong> Only system administrators can toggle the kill switch. This
          immediately affects all users.
        </div>
      </div>

      {/* Confirmation Modal */}
      {showConfirmation && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
          <div className="bg-slate-800 border-2 border-slate-700 rounded-xl p-6 max-w-md w-full mx-4 shadow-2xl">
            <div className="flex items-center gap-3 mb-4">
              <AlertTriangle
                size={32}
                className={pendingState ? "text-red-500" : "text-green-500"}
              />
              <h3 className="text-xl font-bold text-white">
                {pendingState ? "Halt Trading?" : "Resume Trading?"}
              </h3>
            </div>

            <p className="text-slate-300 mb-6">
              {pendingState ? (
                <>
                  Are you sure you want to{" "}
                  <strong className="text-red-400">halt all trading</strong>? This will immediately
                  block all order submissions from all users until you resume trading.
                </>
              ) : (
                <>
                  Are you sure you want to{" "}
                  <strong className="text-green-400">resume trading</strong>? This will allow all
                  users to submit orders again.
                </>
              )}
            </p>

            <div className="flex gap-3">
              <button
                onClick={() => setShowConfirmation(false)}
                className="flex-1 px-4 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium transition-all"
              >
                Cancel
              </button>
              <button
                onClick={handleToggle}
                disabled={loading}
                className={`flex-1 px-4 py-3 rounded-lg font-semibold transition-all ${
                  pendingState
                    ? "bg-red-500 hover:bg-red-600 text-white"
                    : "bg-green-500 hover:bg-green-600 text-white"
                } ${loading ? "opacity-50 cursor-not-allowed" : ""}`}
              >
                {loading
                  ? "Processing..."
                  : pendingState
                    ? "Yes, Halt Trading"
                    : "Yes, Resume Trading"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
