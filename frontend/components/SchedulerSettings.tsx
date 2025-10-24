import React, { useState, useEffect, useCallback, useRef } from "react";
import {
  Clock,
  Play,
  Pause,
  Trash2,
  Plus,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Calendar,
  Bell,
} from "lucide-react";
import useExecutionHistory from "../hooks/useExecutionHistory";

interface Schedule {
  id: string;
  name: string;
  type: "morning_routine" | "news_review" | "ai_recs" | "custom";
  enabled: boolean;
  cron_expression: string;
  timezone: string;
  requires_approval: boolean;
  last_run?: string;
  next_run?: string;
  status: "active" | "paused" | "error";
}

export default function SchedulerSettings() {
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [loading, setLoading] = useState(true);
  const [scheduleError, setScheduleError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [globalPaused, setGlobalPaused] = useState(false);
  const [activeTab, setActiveTab] = useState<"schedules" | "history">("schedules");
  const historyInitializedRef = useRef(false);

  const {
    items: executions,
    loading: historyLoading,
    error: historyError,
    hasMore: hasMoreExecutions,
    loadNextPage,
    refresh: refreshExecutions,
    total: totalExecutions,
  } = useExecutionHistory({ pageSize: 10, autoStart: false });

  // New schedule form state
  const [newSchedule, setNewSchedule] = useState({
    name: "",
    type: "morning_routine" as Schedule["type"],
    cron_expression: "0 9 * * 1-5",
    timezone: "America/New_York",
    requires_approval: true,
    enabled: true,
  });

  const fetchSchedules = useCallback(async () => {
    try {
      const response = await fetch("/api/proxy/scheduler/schedules");
      const data = await response.json();
      setSchedules(data);
      setScheduleError(null);
      setLoading(false);
    } catch (error) {
      console.error("Failed to fetch schedules:", error);
      setScheduleError("Failed to load schedules. Try again shortly.");
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSchedules();
    const interval = setInterval(() => {
      fetchSchedules();
      if (historyInitializedRef.current) {
        refreshExecutions();
      }
    }, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [fetchSchedules, refreshExecutions]);

  useEffect(() => {
    if (activeTab === "history" && !historyInitializedRef.current) {
      historyInitializedRef.current = true;
      refreshExecutions();
    }
  }, [activeTab, refreshExecutions]);

  const toggleSchedule = useCallback(
    async (id: string, enabled: boolean) => {
      try {
        await fetch(`/api/proxy/scheduler/schedules/${id}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ enabled }),
        });
        fetchSchedules();
      } catch (error) {
        console.error("Failed to toggle schedule:", error);
      }
    },
    [fetchSchedules]
  );

  const deleteSchedule = useCallback(
    async (id: string) => {
      if (!confirm("Are you sure you want to delete this schedule?")) return;
      try {
        await fetch(`/api/proxy/scheduler/schedules/${id}`, { method: "DELETE" });
        fetchSchedules();
      } catch (error) {
        console.error("Failed to delete schedule:", error);
      }
    },
    [fetchSchedules]
  );

  const createSchedule = useCallback(async () => {
    try {
      await fetch("/api/proxy/scheduler/schedules", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newSchedule),
      });
      setShowCreateModal(false);
      setNewSchedule({
        name: "",
        type: "morning_routine",
        cron_expression: "0 9 * * 1-5",
        timezone: "America/New_York",
        requires_approval: true,
        enabled: true,
      });
      fetchSchedules();
    } catch (error) {
      console.error("Failed to create schedule:", error);
    }
  }, [fetchSchedules, newSchedule]);

  const pauseAllSchedules = useCallback(async () => {
    if (!confirm("⚠️ PAUSE ALL SCHEDULES? This will immediately stop all automated trading."))
      return;
    try {
      await fetch("/api/proxy/scheduler/pause-all", { method: "POST" });
      setGlobalPaused(true);
      fetchSchedules();
    } catch (error) {
      console.error("Failed to pause all schedules:", error);
    }
  }, [fetchSchedules]);

  const resumeAllSchedules = useCallback(async () => {
    try {
      await fetch("/api/proxy/scheduler/resume-all", { method: "POST" });
      setGlobalPaused(false);
      fetchSchedules();
    } catch (error) {
      console.error("Failed to resume schedules:", error);
    }
  }, [fetchSchedules]);

  const getCronDescription = (cron: string) => {
    const descriptions: { [key: string]: string } = {
      "0 9 * * 1-5": "Weekdays at 9:00 AM",
      "0 8 * * 1-5": "Weekdays at 8:00 AM",
      "30 9 * * 1-5": "Weekdays at 9:30 AM",
      "0 10 * * 1-5": "Weekdays at 10:00 AM",
      "0 */4 * * 1-5": "Every 4 hours (weekdays)",
      "0 9,15 * * 1-5": "Weekdays at 9 AM & 3 PM",
    };
    return descriptions[cron] || cron;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "text-green-400";
      case "completed":
        return "text-green-400";
      case "paused":
        return "text-yellow-400";
      case "error":
        return "text-red-400";
      case "failed":
        return "text-red-400";
      case "running":
        return "text-blue-400";
      case "awaiting_approval":
        return "text-purple-400";
      default:
        return "text-slate-400";
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64 text-white">Loading schedules...</div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header with Emergency Controls */}
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div className="space-y-2">
            <h2 className="text-3xl font-bold text-white flex items-center gap-3">
              <Clock className="text-cyan-400" size={32} />
              Automation & Scheduling
            </h2>
            <p className="text-slate-400 mt-2">Manage automated trading schedules and approvals</p>
          </div>
          <div
            className="flex flex-wrap gap-3"
            role="group"
            aria-label="Emergency scheduling controls"
          >
            {globalPaused ? (
              <button
                onClick={resumeAllSchedules}
                className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 flex items-center gap-2 transition-all"
                aria-label="Resume all schedules"
              >
                <Play className="w-4 h-4" />
                Resume All
              </button>
            ) : (
              <button
                onClick={pauseAllSchedules}
                className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 flex items-center gap-2 transition-all"
                aria-label="Pause all schedules"
              >
                <Pause className="w-4 h-4" />
                Emergency Pause All
              </button>
            )}
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-4 py-2 bg-cyan-500 text-white rounded-lg hover:bg-cyan-600 flex items-center gap-2 transition-all"
              aria-label="Create new schedule"
            >
              <Plus className="w-4 h-4" />
              New Schedule
            </button>
          </div>
        </div>

        {/* Global Status Alert */}
        {globalPaused && (
          <div
            className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 flex items-center gap-3"
            role="status"
            aria-live="polite"
          >
            <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0" />
            <div className="flex-1">
              <p className="font-semibold text-red-400">All Schedules Paused</p>
              <p className="text-sm text-red-300">Automated trading is currently disabled</p>
            </div>
          </div>
        )}

        {scheduleError && (
          <div
            className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 text-sm text-red-300"
            role="alert"
          >
            {scheduleError}
          </div>
        )}

        {/* Tabs */}
        <div
          className="flex gap-4 border-b border-slate-700"
          role="tablist"
          aria-label="Scheduler sections"
        >
          <button
            onClick={() => setActiveTab("schedules")}
            id="scheduler-tab-schedules"
            role="tab"
            aria-selected={activeTab === "schedules"}
            aria-controls="scheduler-panel-schedules"
            className={`pb-3 px-1 font-medium transition-colors ${
              activeTab === "schedules"
                ? "border-b-2 border-cyan-400 text-cyan-400"
                : "text-slate-400 hover:text-white"
            }`}
          >
            Active Schedules ({schedules.length})
          </button>
          <button
            onClick={() => setActiveTab("history")}
            id="scheduler-tab-history"
            role="tab"
            aria-selected={activeTab === "history"}
            aria-controls="scheduler-panel-history"
            className={`pb-3 px-1 font-medium transition-colors ${
              activeTab === "history"
                ? "border-b-2 border-cyan-400 text-cyan-400"
                : "text-slate-400 hover:text-white"
            }`}
          >
            Execution History
          </button>
        </div>

        {/* Schedules Tab */}
        {activeTab === "schedules" && (
          <div
            id="scheduler-panel-schedules"
            role="tabpanel"
            aria-labelledby="scheduler-tab-schedules"
            className="space-y-4"
          >
            {schedules.length === 0 ? (
              <div className="text-center py-12 bg-slate-800/50 rounded-xl border border-slate-700">
                <Clock className="w-12 h-12 text-slate-400 mx-auto mb-3" />
                <p className="text-slate-300">No schedules configured</p>
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="mt-4 px-4 py-2 bg-cyan-500 text-white rounded-lg hover:bg-cyan-600 transition-all"
                >
                  Create Your First Schedule
                </button>
              </div>
            ) : (
              schedules.map((schedule) => (
                <div
                  key={schedule.id}
                  className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-white">{schedule.name}</h3>
                        <span
                          className={`px-2 py-1 text-xs font-medium rounded-full bg-slate-900/50 ${getStatusColor(schedule.status)}`}
                        >
                          {schedule.status}
                        </span>
                        {schedule.requires_approval && (
                          <span className="px-2 py-1 text-xs font-medium bg-purple-500/20 text-purple-400 rounded-full flex items-center gap-1">
                            <Bell className="w-3 h-3" />
                            Requires Approval
                          </span>
                        )}
                      </div>
                      <div className="grid grid-cols-2 gap-4 text-sm text-slate-400">
                        <div>
                          <span className="font-medium text-slate-300">Type:</span>{" "}
                          {schedule.type.replace("_", " ").toUpperCase()}
                        </div>
                        <div>
                          <span className="font-medium text-slate-300">Schedule:</span>{" "}
                          {getCronDescription(schedule.cron_expression)}
                        </div>
                        <div>
                          <span className="font-medium text-slate-300">Timezone:</span>{" "}
                          {schedule.timezone}
                        </div>
                        <div>
                          <span className="font-medium text-slate-300">Next Run:</span>{" "}
                          {schedule.next_run
                            ? new Date(schedule.next_run).toLocaleString()
                            : "Not scheduled"}
                        </div>
                      </div>
                      {schedule.last_run && (
                        <div className="mt-2 text-xs text-slate-500">
                          Last run: {new Date(schedule.last_run).toLocaleString()}
                        </div>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => toggleSchedule(schedule.id, !schedule.enabled)}
                        className={`p-2 rounded-lg transition-colors ${
                          schedule.enabled
                            ? "bg-green-500/20 text-green-400 hover:bg-green-500/30"
                            : "bg-slate-700 text-slate-400 hover:bg-slate-600"
                        }`}
                        title={schedule.enabled ? "Disable" : "Enable"}
                        aria-label={`${schedule.enabled ? "Disable" : "Enable"} ${schedule.name}`}
                      >
                        {schedule.enabled ? (
                          <Pause className="w-4 h-4" />
                        ) : (
                          <Play className="w-4 h-4" />
                        )}
                      </button>
                      <button
                        onClick={() => deleteSchedule(schedule.id)}
                        className="p-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition-colors"
                        title="Delete"
                        aria-label={`Delete ${schedule.name}`}
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* History Tab */}
        {activeTab === "history" && (
          <div
            id="scheduler-panel-history"
            role="tabpanel"
            aria-labelledby="scheduler-tab-history"
            className="space-y-3"
          >
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-400" aria-live="polite">
                {historyLoading
                  ? "Loading execution history..."
                  : `${executions.length} of ${totalExecutions} runs displayed`}
              </span>
              <button
                onClick={refreshExecutions}
                className="text-sm text-cyan-300 hover:text-cyan-200 underline"
                disabled={historyLoading}
                aria-label="Refresh execution history"
              >
                Refresh
              </button>
            </div>

            {historyError && (
              <div
                className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 text-sm text-red-300"
                role="alert"
              >
                {historyError}
              </div>
            )}

            {!historyLoading && executions.length === 0 && !historyError && (
              <div className="text-center py-12 bg-slate-800/50 rounded-xl border border-slate-700">
                <Calendar className="w-12 h-12 text-slate-400 mx-auto mb-3" />
                <p className="text-slate-300">No execution history yet</p>
              </div>
            )}

            {executions.map((execution) => (
              <div
                key={execution.id}
                className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-4"
              >
                <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                  <div className="flex-1">
                    <div className="flex flex-wrap items-center gap-3 mb-1">
                      <span className="font-medium text-white">{execution.schedule_name}</span>
                      <span
                        className={`px-2 py-1 text-xs font-medium rounded-full bg-slate-900/50 ${getStatusColor(execution.status)}`}
                      >
                        {execution.status}
                      </span>
                    </div>
                    <div className="text-sm text-slate-400 space-y-1">
                      <div>Started: {new Date(execution.started_at).toLocaleString()}</div>
                      {execution.completed_at && (
                        <div>Completed: {new Date(execution.completed_at).toLocaleString()}</div>
                      )}
                    </div>
                    {execution.error && (
                      <div className="mt-2 text-sm text-red-400 bg-red-500/10 rounded p-2 border border-red-500/30">
                        Error: {execution.error}
                      </div>
                    )}
                    {execution.result && (
                      <div className="mt-2 text-sm text-slate-400 bg-slate-900/50 rounded p-2">
                        {execution.result}
                      </div>
                    )}
                  </div>
                  <div className="flex items-center gap-2" aria-hidden="true">
                    {execution.status === "completed" && (
                      <CheckCircle className="w-5 h-5 text-green-400" />
                    )}
                    {execution.status === "failed" && <XCircle className="w-5 h-5 text-red-400" />}
                  </div>
                </div>
              </div>
            ))}

            {hasMoreExecutions && (
              <div className="flex justify-center">
                <button
                  onClick={loadNextPage}
                  className="px-4 py-2 bg-slate-800 text-cyan-200 border border-slate-700 rounded-lg hover:bg-slate-700 disabled:opacity-60"
                  disabled={historyLoading}
                  aria-label="Load more execution history"
                >
                  {historyLoading ? "Loading…" : "Load more"}
                </button>
              </div>
            )}
          </div>
        )}

        {/* Create Schedule Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 max-w-lg w-full mx-4">
              <h3 className="text-xl font-bold text-white mb-4">Create New Schedule</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">
                    Schedule Name
                  </label>
                  <input
                    type="text"
                    value={newSchedule.name}
                    onChange={(e) => setNewSchedule({ ...newSchedule, name: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-600 rounded-lg text-white outline-none focus:ring-2 focus:ring-cyan-500/50"
                    placeholder="e.g., Daily Morning Analysis"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">
                    Schedule Type
                  </label>
                  <select
                    value={newSchedule.type}
                    onChange={(e) =>
                      setNewSchedule({ ...newSchedule, type: e.target.value as Schedule["type"] })
                    }
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-600 rounded-lg text-white outline-none focus:ring-2 focus:ring-cyan-500/50"
                  >
                    <option value="morning_routine">Morning Routine</option>
                    <option value="news_review">News Review</option>
                    <option value="ai_recs">AI Recommendations</option>
                    <option value="custom">Custom Action</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">
                    Schedule (Cron)
                  </label>
                  <select
                    value={newSchedule.cron_expression}
                    onChange={(e) =>
                      setNewSchedule({ ...newSchedule, cron_expression: e.target.value })
                    }
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-600 rounded-lg text-white outline-none focus:ring-2 focus:ring-cyan-500/50"
                  >
                    <option value="0 9 * * 1-5">Weekdays at 9:00 AM</option>
                    <option value="0 8 * * 1-5">Weekdays at 8:00 AM</option>
                    <option value="30 9 * * 1-5">Weekdays at 9:30 AM</option>
                    <option value="0 10 * * 1-5">Weekdays at 10:00 AM</option>
                    <option value="0 */4 * * 1-5">Every 4 hours (weekdays)</option>
                    <option value="0 9,15 * * 1-5">Weekdays at 9 AM & 3 PM</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">Timezone</label>
                  <select
                    value={newSchedule.timezone}
                    onChange={(e) => setNewSchedule({ ...newSchedule, timezone: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-600 rounded-lg text-white outline-none focus:ring-2 focus:ring-cyan-500/50"
                  >
                    <option value="America/New_York">Eastern Time (ET)</option>
                    <option value="America/Chicago">Central Time (CT)</option>
                    <option value="America/Denver">Mountain Time (MT)</option>
                    <option value="America/Los_Angeles">Pacific Time (PT)</option>
                  </select>
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="requires_approval"
                    checked={newSchedule.requires_approval}
                    onChange={(e) =>
                      setNewSchedule({ ...newSchedule, requires_approval: e.target.checked })
                    }
                    className="rounded"
                  />
                  <label htmlFor="requires_approval" className="text-sm text-slate-300">
                    Require human approval before executing trades
                  </label>
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 px-4 py-2 border border-slate-600 text-slate-300 rounded-lg hover:bg-slate-700 transition-all"
                >
                  Cancel
                </button>
                <button
                  onClick={createSchedule}
                  disabled={!newSchedule.name}
                  className="flex-1 px-4 py-2 bg-cyan-500 text-white rounded-lg hover:bg-cyan-600 disabled:bg-slate-600 disabled:cursor-not-allowed transition-all"
                >
                  Create Schedule
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
