/**
 * ML Intelligence Workflow
 * 
 * Comprehensive ML-powered trading intelligence for friends and family.
 * Integrates pattern recognition, market regime detection, and personal analytics.
 */

import {
    BarChart3,
    Brain,
    RefreshCw,
    Settings,
    Shield,
    Target,
    TrendingUp,
    User,
    Zap
} from 'lucide-react';
import React, { useState } from 'react';
import { HelpTooltip } from '../HelpTooltip';
import { MarketRegimeDetector } from '../ml/MarketRegimeDetector';
import { MLIntelligenceDashboard } from '../ml/MLIntelligenceDashboard';
import { PatternRecognition } from '../ml/PatternRecognition';
import { PersonalAnalytics } from '../ml/PersonalAnalytics';

interface MLIntelligenceWorkflowProps {
  onClose?: () => void;
}

type TabType = 'overview' | 'patterns' | 'regime' | 'analytics';

export const MLIntelligenceWorkflow: React.FC<MLIntelligenceWorkflowProps> = ({ onClose }) => {
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [selectedSymbol, setSelectedSymbol] = useState('SPY');
  const [refreshing, setRefreshing] = useState(false);

  const tabs = [
    {
      id: 'overview' as TabType,
      label: 'Overview',
      icon: Brain,
      description: 'Complete ML intelligence dashboard'
    },
    {
      id: 'patterns' as TabType,
      label: 'Patterns',
      icon: Target,
      description: 'Chart pattern recognition'
    },
    {
      id: 'regime' as TabType,
      label: 'Market Regime',
      icon: BarChart3,
      description: 'Market state analysis'
    },
    {
      id: 'analytics' as TabType,
      label: 'Personal Analytics',
      icon: User,
      description: 'Your trading performance'
    }
  ];

  const handleRefresh = async () => {
    setRefreshing(true);
    // Simulate refresh delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    setRefreshing(false);
  };

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'overview':
        return <MLIntelligenceDashboard />;
      case 'patterns':
        return <PatternRecognition symbol={selectedSymbol} />;
      case 'regime':
        return <MarketRegimeDetector symbol={selectedSymbol} />;
      case 'analytics':
        return <PersonalAnalytics />;
      default:
        return <MLIntelligenceDashboard />;
    }
  };

  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">ML Intelligence</h1>
              <p className="text-sm text-gray-600">AI-powered trading insights and analysis</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <select
              value={selectedSymbol}
              onChange={(e) => setSelectedSymbol(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              aria-label="Select symbol for ML analysis"
            >
              <option value="SPY">SPY (S&P 500)</option>
              <option value="QQQ">QQQ (NASDAQ)</option>
              <option value="IWM">IWM (Russell 2000)</option>
              <option value="AAPL">AAPL (Apple)</option>
              <option value="MSFT">MSFT (Microsoft)</option>
              <option value="GOOGL">GOOGL (Google)</option>
              <option value="TSLA">TSLA (Tesla)</option>
            </select>
            
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
            
            {onClose && (
              <button
                onClick={onClose}
                className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
              >
                <Settings className="w-5 h-5" />
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white border-b border-gray-200 px-6">
        <div className="flex space-x-1">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-4 py-3 text-sm font-medium rounded-t-lg transition-colors ${
                  activeTab === tab.id
                    ? 'text-blue-600 bg-blue-50 border-b-2 border-blue-600'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
                <HelpTooltip content={tab.description} />
              </button>
            );
          })}
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-6">
          {renderActiveTab()}
        </div>
      </div>

      {/* Quick Actions Footer */}
      <div className="bg-white border-t border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4 text-sm text-gray-600">
            <div className="flex items-center space-x-1">
              <Zap className="w-4 h-4 text-yellow-500" />
              <span>AI-Powered</span>
            </div>
            <div className="flex items-center space-x-1">
              <Shield className="w-4 h-4 text-green-500" />
              <span>Risk Managed</span>
            </div>
            <div className="flex items-center space-x-1">
              <TrendingUp className="w-4 h-4 text-blue-500" />
              <span>Performance Focused</span>
            </div>
          </div>
          
          <div className="text-xs text-gray-500">
            Last updated: {new Date().toLocaleTimeString()}
          </div>
        </div>
      </div>
    </div>
  );
};
