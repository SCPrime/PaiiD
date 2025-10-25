import { useEffect, useState } from "react";
import { Card } from "./ui";

/**
 * GitHub Repository Monitor Dashboard
 *
 * Displays real-time repository activity metrics and event counters
 */

interface CounterData {
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
  hotfixes: number;
}

interface DashboardData {
  event_counters: CounterData;
  timestamp: string;
  status: string;
}

interface HealthData {
  status: string;
  services: {
    counter_manager?: string;
    webhook_handler?: string;
    redis?: string;
  };
  timestamp: string;
}

export function MonitorDashboard() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [healthData, setHealthData] = useState<HealthData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  useEffect(() => {
    const fetchData = async () => {
      try {
        setError(null);

        // Fetch health (no auth required)
        const healthResponse = await fetch("/api/proxy/api/monitor/health");
        if (healthResponse.ok) {
          const healthJson = await healthResponse.json();
          setHealthData(healthJson);
        }

        // Fetch dashboard data (auth required)
        const dashboardResponse = await fetch("/api/proxy/api/monitor/dashboard");
        if (dashboardResponse.ok) {
          const dashboardJson = await dashboardResponse.json();
          setDashboardData(dashboardJson);
          setLastUpdate(new Date());
        } else if (dashboardResponse.status === 401) {
          setError("Authentication required. Please log in.");
        } else {
          setError(`Failed to fetch dashboard data: ${dashboardResponse.statusText}`);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch monitor data");
      } finally {
        setLoading(false);
      }
    };

    fetchData();

    // Refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8" role="status" aria-live="polite">
        <div
          className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"
          aria-label="Loading monitor data"
        ></div>
        <span className="sr-only">Loading monitor data, please wait...</span>
      </div>
    );
  }

  if (error) {
    return (
      <Card className="p-6" role="alert" aria-live="assertive">
        <div className="text-red-500">
          <h3 className="text-lg font-semibold mb-2">Error Loading Monitor Data</h3>
          <p>{error}</p>
        </div>
      </Card>
    );
  }

  const counters = dashboardData?.event_counters;

  return (
    <div className="space-y-6" role="main" aria-label="Repository Monitor Dashboard">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">🔍 Repository Monitor</h1>
          <p className="text-muted-foreground mt-1">Real-time GitHub activity tracking</p>
        </div>
        <div className="text-right" aria-live="polite" aria-atomic="true">
          <div className="text-sm text-muted-foreground">Last Update</div>
          <div className="text-sm font-medium">{lastUpdate.toLocaleTimeString()}</div>
        </div>
      </div>

      {/* Health Status */}
      {healthData && (
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            💚 System Health
            {healthData.status === "healthy" ? (
              <span className="text-green-500">✅</span>
            ) : (
              <span className="text-red-500">❌</span>
            )}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <StatusIndicator
              label="Counter Manager"
              status={healthData.services.counter_manager || "unknown"}
            />
            <StatusIndicator
              label="Webhook Handler"
              status={healthData.services.webhook_handler || "unknown"}
            />
            <StatusIndicator label="Redis" status={healthData.services.redis || "unknown"} />
          </div>
        </Card>
      )}

      {/* Main Metrics Grid */}
      {counters && (
        <>
          {/* Git Activity */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">📊 This Week&apos;s Activity</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <MetricCard label="Commits" value={counters.commits} icon="💾" color="blue" />
              <MetricCard label="Pushes" value={counters.pushes} icon="🚀" color="purple" />
              <MetricCard
                label="Deployments"
                value={counters.deployments}
                icon="🎯"
                color="green"
              />
              <MetricCard label="Hotfixes" value={counters.hotfixes} icon="🔥" color="red" />
            </div>
          </Card>

          {/* Pull Requests */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">🔀 Pull Requests</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <MetricCard label="Opened" value={counters.pulls_opened} icon="📝" color="blue" />
              <MetricCard label="Merged" value={counters.pulls_merged} icon="✅" color="green" />
              <MetricCard label="Closed" value={counters.pulls_closed} icon="❌" color="gray" />
            </div>
          </Card>

          {/* Issues */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">🐛 Issues</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <MetricCard label="Opened" value={counters.issues_opened} icon="📋" color="blue" />
              <MetricCard label="Closed" value={counters.issues_closed} icon="✅" color="green" />
            </div>
            {counters.issues_opened > 0 && (
              <div className="mt-4 p-4 bg-muted rounded-lg">
                <div className="text-sm font-medium">Resolution Rate</div>
                <div className="text-2xl font-bold">
                  {Math.round((counters.issues_closed / counters.issues_opened) * 100)}%
                </div>
                <div className="text-sm text-muted-foreground">
                  {counters.issues_closed} closed / {counters.issues_opened} opened
                </div>
              </div>
            )}
          </Card>

          {/* Quality Metrics */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">✨ Quality Metrics</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <MetricCard
                label="Build Failures"
                value={counters.build_failures}
                icon="🚫"
                color={counters.build_failures > 0 ? "red" : "green"}
                alert={counters.build_failures > 0}
              />
              <MetricCard
                label="Test Failures"
                value={counters.test_failures}
                icon="⚠️"
                color={counters.test_failures > 0 ? "red" : "green"}
                alert={counters.test_failures > 0}
              />
              <MetricCard
                label="Merge Conflicts"
                value={counters.conflicts}
                icon="⚔️"
                color={counters.conflicts > 0 ? "red" : "green"}
                alert={counters.conflicts > 0}
              />
            </div>
          </Card>
        </>
      )}

      {/* Footer */}
      <div className="text-center text-sm text-muted-foreground">
        <p>Data refreshes automatically every 30 seconds</p>
      </div>
    </div>
  );
}

interface MetricCardProps {
  label: string;
  value: number;
  icon: string;
  color?: "blue" | "green" | "red" | "purple" | "gray";
  alert?: boolean;
}

function MetricCard({ label, value, icon, color = "blue", alert = false }: MetricCardProps) {
  const colorClasses = {
    blue: "bg-blue-50 dark:bg-blue-950 text-blue-600 dark:text-blue-400",
    green: "bg-green-50 dark:bg-green-950 text-green-600 dark:text-green-400",
    red: "bg-red-50 dark:bg-red-950 text-red-600 dark:text-red-400",
    purple: "bg-purple-50 dark:bg-purple-950 text-purple-600 dark:text-purple-400",
    gray: "bg-gray-50 dark:bg-gray-800 text-gray-600 dark:text-gray-400",
  };

  return (
    <div
      className={`p-4 rounded-lg transition-all ${colorClasses[color]} ${
        alert ? "ring-2 ring-red-500 animate-pulse" : ""
      }`}
    >
      <div className="flex items-center gap-2 mb-2">
        <span className="text-2xl">{icon}</span>
        <div className="text-sm font-medium opacity-75">{label}</div>
      </div>
      <div className="text-3xl font-bold">{value.toLocaleString()}</div>
    </div>
  );
}

interface StatusIndicatorProps {
  label: string;
  status: string;
}

function StatusIndicator({ label, status }: StatusIndicatorProps) {
  const isHealthy = status === "ready" || status === "connected";

  return (
    <div className="flex items-center gap-3 p-3 bg-muted rounded-lg">
      <div className="flex-shrink-0">
        {isHealthy ? (
          <span className="text-green-500 text-2xl">✅</span>
        ) : (
          <span className="text-red-500 text-2xl">❌</span>
        )}
      </div>
      <div>
        <div className="font-medium">{label}</div>
        <div className="text-sm text-muted-foreground capitalize">{status}</div>
      </div>
    </div>
  );
}
