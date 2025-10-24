"use client";

import { useEffect, useState } from "react";

interface HealthMetrics {
  status: string;
  timestamp: string;
  uptime_seconds: number;
  system: {
    cpu_percent: number;
    memory_percent: number;
    disk_percent: number;
  };
  application: {
    total_requests: number;
    total_errors: number;
    error_rate_percent: number;
    avg_response_time_ms: number;
    requests_per_minute: number;
  };
  dependencies: Record<
    string,
    {
      status: string;
      response_time_ms?: number;
      last_check?: string;
      error?: string;
    }
  >;
}

export default function PerformanceDashboard() {
  const [metrics, setMetrics] = useState<HealthMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 30000); // Every 30s
    return () => clearInterval(interval);
  }, []);

  const fetchMetrics = async () => {
    try {
      const res = await fetch("/api/proxy/health/detailed");
      const data = await res.json();
      setMetrics(data);
    } catch (error) {
      console.error("Failed to fetch metrics:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="p-6">Loading metrics...</div>;
  if (!metrics) return <div className="p-6">Failed to load metrics</div>;

  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    return `${days}d ${hours}h ${mins}m`;
  };

  const getStatusColor = (value: number, thresholds: [number, number]) => {
    if (value < thresholds[0]) return "text-green-400";
    if (value < thresholds[1]) return "text-yellow-400";
    return "text-red-400";
  };

  return (
    <div className="p-6 space-y-6">
      <h2 className="text-2xl font-bold">Production Metrics</h2>

      {/* Status Badge */}
      <div className="flex items-center gap-3">
        <div
          className={`px-4 py-2 rounded-full font-semibold ${
            metrics.status === "healthy" ? "bg-green-900 text-green-100" : "bg-red-900 text-red-100"
          }`}
        >
          {metrics.status.toUpperCase()}
        </div>
        <div className="text-gray-400">Uptime: {formatUptime(metrics.uptime_seconds)}</div>
      </div>

      {/* System Metrics */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-gray-800 rounded-lg p-4">
          <div className="text-sm text-gray-400">CPU Usage</div>
          <div
            className={`text-3xl font-bold ${getStatusColor(metrics.system.cpu_percent, [70, 85])}`}
          >
            {metrics.system.cpu_percent.toFixed(1)}%
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4">
          <div className="text-sm text-gray-400">Memory Usage</div>
          <div
            className={`text-3xl font-bold ${getStatusColor(metrics.system.memory_percent, [75, 90])}`}
          >
            {metrics.system.memory_percent.toFixed(1)}%
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4">
          <div className="text-sm text-gray-400">Disk Usage</div>
          <div
            className={`text-3xl font-bold ${getStatusColor(metrics.system.disk_percent, [80, 95])}`}
          >
            {metrics.system.disk_percent.toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Application Metrics */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-xl font-bold mb-4">Application Performance</h3>
        <div className="grid grid-cols-2 gap-6">
          <div>
            <div className="text-sm text-gray-400">Total Requests</div>
            <div className="text-2xl font-bold">
              {metrics.application.total_requests.toLocaleString()}
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-400">Requests/Min</div>
            <div className="text-2xl font-bold">
              {metrics.application.requests_per_minute.toFixed(1)}
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-400">Error Rate</div>
            <div
              className={`text-2xl font-bold ${getStatusColor(metrics.application.error_rate_percent, [1, 5])}`}
            >
              {metrics.application.error_rate_percent.toFixed(2)}%
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-400">Avg Response Time</div>
            <div
              className={`text-2xl font-bold ${getStatusColor(metrics.application.avg_response_time_ms, [200, 500])}`}
            >
              {metrics.application.avg_response_time_ms.toFixed(0)}ms
            </div>
          </div>
        </div>
      </div>

      {/* Dependencies */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-xl font-bold mb-4">External Services</h3>
        <div className="space-y-3">
          {Object.entries(metrics.dependencies).map(([name, dep]) => (
            <div
              key={name}
              className="flex justify-between items-center border-b border-gray-700 pb-2"
            >
              <div className="font-semibold capitalize">{name}</div>
              <div className="flex items-center gap-3">
                <div className={dep.status === "up" ? "text-green-400" : "text-red-400"}>
                  {dep.status.toUpperCase()}
                </div>
                {dep.response_time_ms && (
                  <div className="text-sm text-gray-400">{dep.response_time_ms.toFixed(0)}ms</div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="text-xs text-gray-500">
        Last updated: {new Date(metrics.timestamp).toLocaleString()}
      </div>
    </div>
  );
}
