/**
 * Monitor Dashboard Component
 *
 * Real-time monitoring dashboard displaying:
 * - Event counters (commits, PRs, issues, deployments)
 * - Issue health metrics
 * - Project completion progress with line graph
 * - System health indicators
 * - Recent alerts
 */

import React, { useEffect, useState } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface EventCounters {
  commits: number;
  pushes: number;
  pulls_opened: number;
  pulls_merged: number;
  pulls_closed: number;
  issues_opened: number;
  issues_closed: number;
  deployments: number;
  build_failures: number;
  test_failures: number;
  conflicts: number;
}

interface IssueHealth {
  total_issues: number;
  critical_p0: number;
  high_p1: number;
  medium_p2: number;
  assigned: number;
  unassigned: number;
  blocked: number;
  avg_resolution_time_hours: number;
}

interface PhaseProgress {
  progress: number;
  tasks_completed: number;
  tasks_total: number;
  estimated_hours_remaining: number;
}

interface CompletionTracking {
  overall_progress: number;
  phases: {
    phase_0_prep: PhaseProgress;
    phase_1_options: PhaseProgress;
    phase_2_ml: PhaseProgress;
    phase_3_ui: PhaseProgress;
    phase_4_cleanup: PhaseProgress;
  };
  timeline: {
    total_hours_budgeted: number;
    hours_completed: number;
    hours_remaining: number;
    estimated_completion_date: string;
    days_behind_schedule: number;
  };
}

interface SystemHealth {
  frontend_status: string;
  backend_status: string;
  database_status: string;
  redis_status: string;
  last_crash: string | null;
  uptime_percent_7d: number;
  api_error_rate_5m: number;
}

interface Alert {
  id: number;
  severity: string;
  title: string;
  message: string;
  timestamp: string;
  tags: string[];
}

interface ProgressPoint {
  date: string;
  completion: number;
  target: number;
}

interface MonitorData {
  eventCounters: EventCounters;
  issueHealth: IssueHealth;
  completionTracking: CompletionTracking;
  systemHealth: SystemHealth;
  recentAlerts: Alert[];
  timestamp: string;
}

const MonitorDashboard: React.FC = () => {
  const [data, setData] = useState<MonitorData | null>(null);
  const [progressHistory, setProgressHistory] = useState<ProgressPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  const fetchData = async () => {
    try {
      const response = await fetch("/api/proxy/api/monitor/dashboard");
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const json = await response.json();
      setData(json);
      setLastUpdate(new Date());
      setError(null);
    } catch (err: any) {
      console.error("Failed to fetch monitor data:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchProgressHistory = async () => {
    try {
      const response = await fetch("/api/proxy/api/monitor/progress?days=30");
      if (!response.ok) return;
      const json = await response.json();
      setProgressHistory(json.history || []);
    } catch (err) {
      console.error("Failed to fetch progress history:", err);
    }
  };

  useEffect(() => {
    fetchData();
    fetchProgressHistory();

    // Refresh every 30 seconds
    const interval = setInterval(() => {
      fetchData();
      fetchProgressHistory();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Loading monitor data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-red-500">
          <h2 className="text-xl font-bold mb-2">Error Loading Dashboard</h2>
          <p>{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-blue-500 text-white rounded"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="monitor-dashboard p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">🔍 PaiiD Repository Monitor</h1>
        <div className="text-sm text-gray-500">Last update: {lastUpdate.toLocaleTimeString()}</div>
      </div>

      {/* Event Counters */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">📊 This Week&apos;s Activity</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          <MetricCard label="Commits" value={data.eventCounters.commits} />
          <MetricCard label="Pushes" value={data.eventCounters.pushes} />
          <MetricCard label="Deployments" value={data.eventCounters.deployments} />
          <MetricCard label="PRs Opened" value={data.eventCounters.pulls_opened} />
          <MetricCard label="PRs Merged" value={data.eventCounters.pulls_merged} />
          <MetricCard label="Issues Opened" value={data.eventCounters.issues_opened} />
          <MetricCard label="Issues Closed" value={data.eventCounters.issues_closed} />
          <MetricCard
            label="Build Failures"
            value={data.eventCounters.build_failures}
            color="red"
          />
          <MetricCard label="Conflicts" value={data.eventCounters.conflicts} color="orange" />
        </div>
      </div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Issue Health */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">🐛 Issue Health</h2>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="font-medium">Total Issues:</span>
              <span className="text-2xl font-bold">{data.issueHealth.total_issues}</span>
            </div>
            <div className="flex justify-between items-center">
              <span>🔴 P0 Critical:</span>
              <span className="text-xl font-bold text-red-600">{data.issueHealth.critical_p0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span>🟠 P1 High:</span>
              <span className="text-xl font-bold text-orange-600">{data.issueHealth.high_p1}</span>
            </div>
            <div className="flex justify-between items-center">
              <span>🟡 P2 Medium:</span>
              <span className="text-xl font-bold text-yellow-600">
                {data.issueHealth.medium_p2}
              </span>
            </div>
            <div className="border-t pt-3 mt-3">
              <div className="flex justify-between text-sm">
                <span>Assigned:</span>
                <span>{data.issueHealth.assigned}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Unassigned:</span>
                <span>{data.issueHealth.unassigned}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Blocked:</span>
                <span>{data.issueHealth.blocked}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Avg Resolution:</span>
                <span>{data.issueHealth.avg_resolution_time_hours.toFixed(1)}h</span>
              </div>
            </div>
          </div>
        </div>

        {/* System Health */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">💚 System Health</h2>
          <div className="space-y-3">
            <StatusIndicator label="Frontend" status={data.systemHealth.frontend_status} />
            <StatusIndicator label="Backend" status={data.systemHealth.backend_status} />
            <StatusIndicator label="Database" status={data.systemHealth.database_status} />
            <StatusIndicator label="Redis" status={data.systemHealth.redis_status} />
            <div className="border-t pt-3 mt-3">
              <div className="flex justify-between text-sm">
                <span>Uptime (7d):</span>
                <span className="font-bold">{data.systemHealth.uptime_percent_7d.toFixed(2)}%</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Error Rate (5m):</span>
                <span className="font-bold">
                  {(data.systemHealth.api_error_rate_5m * 100).toFixed(3)}%
                </span>
              </div>
              {data.systemHealth.last_crash && (
                <div className="flex justify-between text-sm text-red-600">
                  <span>Last Crash:</span>
                  <span>{new Date(data.systemHealth.last_crash).toLocaleString()}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Completion Progress Line Graph */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">📈 Completion Progress Over Time</h2>
        <div className="mb-4">
          <div className="text-3xl font-bold text-blue-600">
            {Math.round(data.completionTracking.overall_progress * 100)}%
          </div>
          <div className="text-sm text-gray-500">
            {data.completionTracking.timeline.hours_completed.toFixed(1)} /{" "}
            {data.completionTracking.timeline.total_hours_budgeted} hours completed
          </div>
        </div>

        {progressHistory.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={progressHistory}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="date"
                tickFormatter={(value) => new Date(value).toLocaleDateString()}
              />
              <YAxis
                domain={[0, 100]}
                label={{ value: "Completion %", angle: -90, position: "insideLeft" }}
              />
              <Tooltip
                formatter={(value: number) => [`${value}%`, ""]}
                labelFormatter={(label) => new Date(label).toLocaleDateString()}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="completion"
                stroke="#3b82f6"
                strokeWidth={3}
                name="Actual Progress"
                dot={{ r: 5 }}
                activeDot={{ r: 8 }}
              />
              <Line
                type="monotone"
                dataKey="target"
                stroke="#10b981"
                strokeWidth={2}
                strokeDasharray="5 5"
                name="Target Progress"
                dot={{ r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-[300px] flex items-center justify-center text-gray-500">
            No historical data available yet
          </div>
        )}

        <div className="grid grid-cols-3 gap-4 mt-4 text-center">
          <div>
            <div className="text-sm text-gray-500">Current</div>
            <div className="text-xl font-bold text-blue-600">
              {Math.round(data.completionTracking.overall_progress * 100)}%
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-500">Hours Remaining</div>
            <div className="text-xl font-bold text-orange-600">
              {data.completionTracking.timeline.hours_remaining.toFixed(1)}h
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-500">Est. Completion</div>
            <div className="text-xl font-bold text-green-600">
              {new Date(
                data.completionTracking.timeline.estimated_completion_date
              ).toLocaleDateString()}
            </div>
          </div>
        </div>
      </div>

      {/* Phase Progress Breakdown */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">🎯 Phase Breakdown</h2>
        <div className="space-y-4">
          {Object.entries(data.completionTracking.phases).map(([phaseKey, phase]) => {
            const phaseName = phaseKey
              .replace("_", " ")
              .split(" ")
              .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
              .join(" ");
            return (
              <div key={phaseKey}>
                <div className="flex justify-between items-center mb-2">
                  <span className="font-medium">{phaseName}</span>
                  <span className="text-sm text-gray-500">
                    {phase.tasks_completed} / {phase.tasks_total} tasks
                  </span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-4">
                  <div
                    className="bg-blue-600 h-4 rounded-full transition-all duration-500"
                    style={{ width: `${phase.progress * 100}%` }}
                  >
                    <span className="text-xs text-white px-2 leading-4">
                      {Math.round(phase.progress * 100)}%
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Recent Alerts */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">🔔 Recent Alerts</h2>
        {data.recentAlerts.length > 0 ? (
          <div className="space-y-2">
            {data.recentAlerts.map((alert) => (
              <AlertCard key={alert.id} alert={alert} />
            ))}
          </div>
        ) : (
          <div className="text-center text-gray-500 py-4">No recent alerts</div>
        )}
      </div>
    </div>
  );
};

// Helper Components

const MetricCard: React.FC<{ label: string; value: number; color?: string }> = ({
  label,
  value,
  color,
}) => {
  const colorClass =
    color === "red" ? "text-red-600" : color === "orange" ? "text-orange-600" : "text-blue-600";

  return (
    <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded">
      <div className="text-sm text-gray-500 mb-1">{label}</div>
      <div className={`text-2xl font-bold ${colorClass}`}>{value}</div>
    </div>
  );
};

const StatusIndicator: React.FC<{ label: string; status: string }> = ({ label, status }) => {
  const statusColors = {
    healthy: "text-green-600",
    degraded: "text-yellow-600",
    down: "text-red-600",
  };

  const statusDots = {
    healthy: "🟢",
    degraded: "🟡",
    down: "🔴",
  };

  return (
    <div className="flex justify-between items-center">
      <span>{label}:</span>
      <span
        className={`font-bold ${statusColors[status as keyof typeof statusColors] || "text-gray-600"}`}
      >
        {statusDots[status as keyof typeof statusDots] || "⚪"} {status}
      </span>
    </div>
  );
};

const AlertCard: React.FC<{ alert: Alert }> = ({ alert }) => {
  const severityColors = {
    critical: "border-red-500 bg-red-50 dark:bg-red-900",
    high: "border-orange-500 bg-orange-50 dark:bg-orange-900",
    medium: "border-yellow-500 bg-yellow-50 dark:bg-yellow-900",
    low: "border-green-500 bg-green-50 dark:bg-green-900",
  };

  const severityEmoji = {
    critical: "🔴",
    high: "🟠",
    medium: "🟡",
    low: "🟢",
  };

  return (
    <div
      className={`border-l-4 p-3 ${severityColors[alert.severity as keyof typeof severityColors]}`}
    >
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <div className="font-semibold">
            {severityEmoji[alert.severity as keyof typeof severityEmoji]} {alert.title}
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-300">{alert.message}</div>
          {alert.tags.length > 0 && (
            <div className="flex gap-2 mt-2">
              {alert.tags.map((tag) => (
                <span key={tag} className="text-xs bg-gray-200 dark:bg-gray-700 px-2 py-1 rounded">
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>
        <div className="text-xs text-gray-500 ml-2">
          {new Date(alert.timestamp).toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
};

export default MonitorDashboard;
