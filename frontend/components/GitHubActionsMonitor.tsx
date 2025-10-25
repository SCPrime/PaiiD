"use client";

import { CheckCircle, Clock, ExternalLink, RefreshCw, XCircle } from "lucide-react";
import { useEffect, useState } from "react";

interface WorkflowRun {
  id: number;
  name: string;
  status: "completed" | "in_progress" | "queued" | "cancelled" | "failed";
  conclusion: "success" | "failure" | "cancelled" | "skipped" | null;
  created_at: string;
  updated_at: string;
  html_url: string;
  workflow_id: number;
  workflow_name: string;
}

interface Workflow {
  id: number;
  name: string;
  state: "active" | "deleted";
  created_at: string;
  updated_at: string;
  html_url: string;
}

interface GitHubActionsMonitorProps {
  repository: string;
}

export function GitHubActionsMonitor({ repository }: GitHubActionsMonitorProps) {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [runs, setRuns] = useState<WorkflowRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchWorkflows = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch workflows
      const workflowsResponse = await fetch(
        `https://api.github.com/repos/${repository}/actions/workflows`
      );
      
      if (!workflowsResponse.ok) {
        throw new Error(`Failed to fetch workflows: ${workflowsResponse.status}`);
      }
      
      const workflowsData = await workflowsResponse.json();
      setWorkflows(workflowsData.workflows || []);

      // Fetch recent runs
      const runsResponse = await fetch(
        `https://api.github.com/repos/${repository}/actions/runs?per_page=20`
      );
      
      if (!runsResponse.ok) {
        throw new Error(`Failed to fetch runs: ${runsResponse.status}`);
      }
      
      const runsData = await runsResponse.json();
      setRuns(runsData.workflow_runs || []);
      
      setLastUpdated(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch GitHub Actions data");
      console.error("GitHub Actions fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWorkflows();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchWorkflows, 30000);
    return () => clearInterval(interval);
  }, [repository]);

  const getStatusIcon = (status: string, conclusion: string | null) => {
    if (status === "in_progress") {
      return <RefreshCw className="w-4 h-4 text-blue-500 animate-spin" />;
    }
    if (status === "queued") {
      return <Clock className="w-4 h-4 text-yellow-500" />;
    }
    if (conclusion === "success") {
      return <CheckCircle className="w-4 h-4 text-green-500" />;
    }
    if (conclusion === "failure") {
      return <XCircle className="w-4 h-4 text-red-500" />;
    }
    if (conclusion === "cancelled") {
      return <XCircle className="w-4 h-4 text-gray-500" />;
    }
    return <Clock className="w-4 h-4 text-gray-400" />;
  };

  const getStatusColor = (status: string, conclusion: string | null) => {
    if (status === "in_progress") return "text-blue-500";
    if (status === "queued") return "text-yellow-500";
    if (conclusion === "success") return "text-green-500";
    if (conclusion === "failure") return "text-red-500";
    if (conclusion === "cancelled") return "text-gray-500";
    return "text-gray-400";
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const getStatusCounts = () => {
    const counts = {
      success: 0,
      failure: 0,
      running: 0,
      queued: 0,
    };

    runs.forEach((run) => {
      if (run.status === "in_progress") counts.running++;
      else if (run.status === "queued") counts.queued++;
      else if (run.conclusion === "success") counts.success++;
      else if (run.conclusion === "failure") counts.failure++;
    });

    return counts;
  };

  const statusCounts = getStatusCounts();

  if (loading && !lastUpdated) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        <span className="ml-3 text-gray-400">Loading GitHub Actions...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-6">
        <div className="flex items-center gap-2 text-red-400 mb-2">
          <XCircle className="w-5 h-5" />
          <h3 className="font-semibold">Error Loading GitHub Actions</h3>
        </div>
        <p className="text-red-300 text-sm mb-4">{error}</p>
        <button
          onClick={fetchWorkflows}
          className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm font-medium transition-colors"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">GitHub Actions Monitor</h2>
          <p className="text-gray-400 text-sm">
            Repository: <span className="text-blue-400">{repository}</span>
          </p>
          {lastUpdated && (
            <p className="text-gray-500 text-xs mt-1">
              Last updated: {formatDate(lastUpdated.toISOString())}
            </p>
          )}
        </div>
        <button
          onClick={fetchWorkflows}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:cursor-not-allowed text-white rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </button>
      </div>

      {/* Status Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-green-900/20 border border-green-500/30 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-5 h-5 text-green-500" />
            <span className="text-green-400 font-semibold">Success</span>
          </div>
          <div className="text-2xl font-bold text-green-300 mt-1">{statusCounts.success}</div>
        </div>
        
        <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <XCircle className="w-5 h-5 text-red-500" />
            <span className="text-red-400 font-semibold">Failed</span>
          </div>
          <div className="text-2xl font-bold text-red-300 mt-1">{statusCounts.failure}</div>
        </div>
        
        <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <RefreshCw className="w-5 h-5 text-blue-500 animate-spin" />
            <span className="text-blue-400 font-semibold">Running</span>
          </div>
          <div className="text-2xl font-bold text-blue-300 mt-1">{statusCounts.running}</div>
        </div>
        
        <div className="bg-yellow-900/20 border border-yellow-500/30 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <Clock className="w-5 h-5 text-yellow-500" />
            <span className="text-yellow-400 font-semibold">Queued</span>
          </div>
          <div className="text-2xl font-bold text-yellow-300 mt-1">{statusCounts.queued}</div>
        </div>
      </div>

      {/* Recent Runs */}
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <span className="text-xl">🔄</span>
          Recent Workflow Runs
        </h3>
        
        {runs.length === 0 ? (
          <div className="text-center py-8 text-gray-400">
            No workflow runs found
          </div>
        ) : (
          <div className="space-y-3">
            {runs.slice(0, 10).map((run) => (
              <div
                key={run.id}
                className="bg-slate-900/40 border border-slate-700/30 rounded-lg p-4 hover:bg-slate-900/60 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {getStatusIcon(run.status, run.conclusion)}
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-white">{run.name}</span>
                        <span className={`text-sm ${getStatusColor(run.status, run.conclusion)}`}>
                          {run.status === "in_progress" ? "Running" : 
                           run.status === "queued" ? "Queued" :
                           run.conclusion === "success" ? "Success" :
                           run.conclusion === "failure" ? "Failed" :
                           run.conclusion === "cancelled" ? "Cancelled" : "Unknown"}
                        </span>
                      </div>
                      <div className="text-sm text-gray-400">
                        {run.workflow_name} • {formatDate(run.created_at)}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <a
                      href={run.html_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors"
                      title="View in GitHub"
                    >
                      <ExternalLink className="w-4 h-4 text-gray-400" />
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Workflows */}
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <span className="text-xl">⚙️</span>
          Available Workflows
        </h3>
        
        {workflows.length === 0 ? (
          <div className="text-center py-8 text-gray-400">
            No workflows found
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {workflows.map((workflow) => (
              <div
                key={workflow.id}
                className="bg-slate-900/40 border border-slate-700/30 rounded-lg p-4 hover:bg-slate-900/60 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-white">{workflow.name}</div>
                    <div className="text-sm text-gray-400">
                      State: <span className={workflow.state === "active" ? "text-green-400" : "text-red-400"}>
                        {workflow.state}
                      </span>
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      Updated: {formatDate(workflow.updated_at)}
                    </div>
                  </div>
                  
                  <a
                    href={workflow.html_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors"
                    title="View in GitHub"
                  >
                    <ExternalLink className="w-4 h-4 text-gray-400" />
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
