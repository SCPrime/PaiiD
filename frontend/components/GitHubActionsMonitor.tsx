/**
 * GitHub Actions Monitor Component
 * 
 * Real-time monitoring of GitHub Actions status directly in Cursor.
 * Shows workflow runs, status, and allows quick access to logs.
 */

import React, { useState, useEffect } from 'react';
import { 
  CheckCircle, 
  XCircle, 
  Clock, 
  AlertTriangle, 
  RefreshCw, 
  ExternalLink,
  GitBranch,
  Calendar,
  User,
  Loader2,
  Activity,
  Zap
} from 'lucide-react';

interface WorkflowRun {
  id: number;
  name: string;
  status: 'completed' | 'in_progress' | 'queued' | 'cancelled';
  conclusion: 'success' | 'failure' | 'cancelled' | 'skipped' | null;
  created_at: string;
  updated_at: string;
  head_branch: string;
  head_sha: string;
  html_url: string;
  actor: {
    login: string;
    avatar_url: string;
  };
  workflow_id: number;
  workflow_url: string;
}

interface GitHubActionsMonitorProps {
  repository: string;
  onStatusChange?: (status: 'all_green' | 'has_red' | 'unknown') => void;
}

export const GitHubActionsMonitor: React.FC<GitHubActionsMonitorProps> = ({ 
  repository = 'SCPrime/PaiiD',
  onStatusChange 
}) => {
  const [workflows, setWorkflows] = useState<WorkflowRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadWorkflowRuns();
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadWorkflowRuns, 30000);
    return () => clearInterval(interval);
  }, [repository]);

  const loadWorkflowRuns = async () => {
    setRefreshing(true);
    try {
      // Note: This would need a GitHub token in production
      // For now, we'll simulate the data
      const mockWorkflows: WorkflowRun[] = [
        {
          id: 1,
          name: 'CI/CD Pipeline',
          status: 'completed',
          conclusion: 'success',
          created_at: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
          updated_at: new Date(Date.now() - 2 * 60 * 1000).toISOString(),
          head_branch: 'main',
          head_sha: 'b72d170',
          html_url: `https://github.com/${repository}/actions/runs/1`,
          actor: {
            login: 'SCPrime',
            avatar_url: 'https://github.com/SCPrime.png'
          },
          workflow_id: 1,
          workflow_url: `https://github.com/${repository}/actions/workflows/ci.yml`
        },
        {
          id: 2,
          name: 'ML Intelligence Tests',
          status: 'completed',
          conclusion: 'failure',
          created_at: new Date(Date.now() - 10 * 60 * 1000).toISOString(),
          updated_at: new Date(Date.now() - 8 * 60 * 1000).toISOString(),
          head_branch: 'main',
          head_sha: 'b72d170',
          html_url: `https://github.com/${repository}/actions/runs/2`,
          actor: {
            login: 'SCPrime',
            avatar_url: 'https://github.com/SCPrime.png'
          },
          workflow_id: 2,
          workflow_url: `https://github.com/${repository}/actions/workflows/ml-tests.yml`
        },
        {
          id: 3,
          name: 'Deployment Pipeline',
          status: 'in_progress',
          conclusion: null,
          created_at: new Date(Date.now() - 2 * 60 * 1000).toISOString(),
          updated_at: new Date(Date.now() - 30 * 1000).toISOString(),
          head_branch: 'main',
          head_sha: 'b72d170',
          html_url: `https://github.com/${repository}/actions/runs/3`,
          actor: {
            login: 'SCPrime',
            avatar_url: 'https://github.com/SCPrime.png'
          },
          workflow_id: 3,
          workflow_url: `https://github.com/${repository}/actions/workflows/deploy.yml`
        }
      ];

      setWorkflows(mockWorkflows);
      setLastUpdate(new Date());
      setError(null);

      // Determine overall status
      const hasFailures = mockWorkflows.some(w => w.conclusion === 'failure');
      const hasInProgress = mockWorkflows.some(w => w.status === 'in_progress');
      
      if (hasFailures) {
        onStatusChange?.('has_red');
      } else if (hasInProgress) {
        onStatusChange?.('unknown');
      } else {
        onStatusChange?.('all_green');
      }

    } catch (err) {
      setError('Failed to load GitHub Actions status');
      console.error('GitHub Actions monitor error:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const getStatusIcon = (status: string, conclusion: string | null) => {
    if (status === 'in_progress') {
      return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
    if (conclusion === 'success') {
      return <CheckCircle className="w-5 h-5 text-green-500" />;
    if (conclusion === 'failure') {
      return <XCircle className="w-5 h-5 text-red-500" />;
    if (conclusion === 'cancelled') {
      return <XCircle className="w-5 h-5 text-gray-500" />;
    if (conclusion === 'skipped') {
      return <Clock className="w-5 h-5 text-gray-400" />;
    }
    return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
  };

  const getStatusColor = (status: string, conclusion: string | null) => {
    if (status === 'in_progress') return 'border-blue-200 bg-blue-50';
    if (conclusion === 'success') return 'border-green-200 bg-green-50';
    if (conclusion === 'failure') return 'border-red-200 bg-red-50';
    if (conclusion === 'cancelled') return 'border-gray-200 bg-gray-50';
    return 'border-yellow-200 bg-yellow-50';
  };

  const getStatusText = (status: string, conclusion: string | null) => {
    if (status === 'in_progress') return 'Running';
    if (conclusion === 'success') return 'Success';
    if (conclusion === 'failure') return 'Failed';
    if (conclusion === 'cancelled') return 'Cancelled';
    if (conclusion === 'skipped') return 'Skipped';
    return 'Unknown';
  };

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        <span className="ml-3 text-gray-600">Loading GitHub Actions status...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-gradient-to-r from-green-500 to-blue-600 rounded-lg">
            <Activity className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900">GitHub Actions Monitor</h2>
            <p className="text-sm text-gray-600">Real-time workflow status for {repository}</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          {lastUpdate && (
            <div className="text-sm text-gray-500">
              Last updated: {lastUpdate.toLocaleTimeString()}
            </div>
          )}
          <button
            onClick={loadWorkflowRuns}
            disabled={refreshing}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Status Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white border border-gray-200 rounded-xl p-4">
          <div className="flex items-center space-x-3">
            <CheckCircle className="w-8 h-8 text-green-500" />
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {workflows.filter(w => w.conclusion === 'success').length}
              </div>
              <div className="text-sm text-gray-500">Successful</div>
            </div>
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-xl p-4">
          <div className="flex items-center space-x-3">
            <XCircle className="w-8 h-8 text-red-500" />
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {workflows.filter(w => w.conclusion === 'failure').length}
              </div>
              <div className="text-sm text-gray-500">Failed</div>
            </div>
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-xl p-4">
          <div className="flex items-center space-x-3">
            <Loader2 className="w-8 h-8 text-blue-500" />
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {workflows.filter(w => w.status === 'in_progress').length}
              </div>
              <div className="text-sm text-gray-500">Running</div>
            </div>
          </div>
        </div>
      </div>

      {/* Workflow Runs */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Recent Workflow Runs</h3>
        
        {workflows.length > 0 ? (
          <div className="space-y-3">
            {workflows.map((workflow) => (
              <div
                key={workflow.id}
                className={`border rounded-xl p-4 ${getStatusColor(workflow.status, workflow.conclusion)}`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    {getStatusIcon(workflow.status, workflow.conclusion)}
                    <div>
                      <h4 className="font-semibold text-gray-900">{workflow.name}</h4>
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <div className="flex items-center space-x-1">
                          <GitBranch className="w-4 h-4" />
                          <span>{workflow.head_branch}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Calendar className="w-4 h-4" />
                          <span>{formatTimeAgo(workflow.created_at)}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <User className="w-4 h-4" />
                          <span>{workflow.actor.login}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <div className="text-right">
                      <div className="font-medium text-gray-900">
                        {getStatusText(workflow.status, workflow.conclusion)}
                      </div>
                      <div className="text-sm text-gray-500">
                        {workflow.head_sha.substring(0, 7)}
                      </div>
                    </div>
                    
                    <a
                      href={workflow.html_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center space-x-1 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                    >
                      <ExternalLink className="w-4 h-4" />
                      <span className="text-sm">View</span>
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Workflow Runs</h3>
            <p className="text-gray-600">
              No recent workflow runs found for {repository}.
            </p>
          </div>
        )}
      </div>

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-5 h-5 text-red-500" />
            <span className="font-medium text-red-800">{error}</span>
          </div>
          <p className="text-sm text-red-600 mt-1">
            Check your GitHub token permissions or network connection.
          </p>
        </div>
      )}

      {/* Quick Actions */}
      <div className="bg-white border border-gray-200 rounded-xl p-4">
        <h3 className="font-semibold text-gray-900 mb-3">Quick Actions</h3>
        <div className="flex flex-wrap gap-2">
          <a
            href={`https://github.com/${repository}/actions`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center space-x-2 px-3 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
          >
            <ExternalLink className="w-4 h-4" />
            <span>View All Actions</span>
          </a>
          <a
            href={`https://github.com/${repository}/actions/workflows`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center space-x-2 px-3 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors"
          >
            <Zap className="w-4 h-4" />
            <span>Workflow Files</span>
          </a>
        </div>
      </div>
    </div>
  );
};

export default GitHubActionsMonitor;
