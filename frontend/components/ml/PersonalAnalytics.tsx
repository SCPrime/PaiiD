/**
 * Personal Analytics Component
 * 
 * Personal trading analytics and insights for friends and family.
 * Tracks performance, identifies patterns, and provides personalized recommendations.
 */

import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  TrendingUp, 
  Target,
  Shield,
  Zap,
  Award,
  AlertTriangle,
  Info,
  RefreshCw,
  Loader2
} from 'lucide-react';
import { HelpTooltip } from '../HelpTooltip';

interface PersonalAnalytics {
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  win_rate: number;
  total_return: number;
  sharpe_ratio: number;
  max_drawdown: number;
  avg_hold_time: number;
  best_trade: number;
  worst_trade: number;
  risk_score: number;
  consistency_score: number;
}

interface TradingPattern {
  pattern_name: string;
  frequency: number;
  success_rate: number;
  avg_return: number;
  description: string;
}

interface PersonalRecommendation {
  type: 'improvement' | 'opportunity' | 'warning';
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  actionable: boolean;
  impact: string;
}

interface PersonalAnalyticsProps {
  userId?: string;
  timeRange?: '7d' | '30d' | '90d' | '1y';
}

export const PersonalAnalytics: React.FC<PersonalAnalyticsProps> = ({ 
  userId = 'demo',
  timeRange = '30d'
}) => {
  const [analytics, setAnalytics] = useState<PersonalAnalytics | null>(null);
  const [patterns, setPatterns] = useState<TradingPattern[]>([]);
  const [recommendations, setRecommendations] = useState<PersonalRecommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadPersonalAnalytics();
  }, [userId, timeRange]);

  const loadPersonalAnalytics = async () => {
    setLoading(true);
    try {
      // Simulate loading personal analytics
      // In production, this would fetch from the backend
      const mockAnalytics: PersonalAnalytics = {
        total_trades: 47,
        winning_trades: 28,
        losing_trades: 19,
        win_rate: 59.6,
        total_return: 12.4,
        sharpe_ratio: 1.23,
        max_drawdown: -8.2,
        avg_hold_time: 5.3,
        best_trade: 15.7,
        worst_trade: -6.8,
        risk_score: 0.65,
        consistency_score: 0.78
      };

      const mockPatterns: TradingPattern[] = [
        {
          pattern_name: 'Momentum Breakouts',
          frequency: 12,
          success_rate: 75.0,
          avg_return: 8.2,
          description: 'You excel at identifying and trading momentum breakouts'
        },
        {
          pattern_name: 'Support Bounces',
          frequency: 8,
          success_rate: 62.5,
          avg_return: 4.1,
          description: 'You have moderate success with support level bounces'
        },
        {
          pattern_name: 'Resistance Rejections',
          frequency: 6,
          success_rate: 33.3,
          avg_return: -2.1,
          description: 'You struggle with resistance level rejections'
        }
      ];

      const mockRecommendations: PersonalRecommendation[] = [
        {
          type: 'improvement',
          title: 'Improve Risk Management',
          description: 'Your average loss (-6.8%) is larger than your average win (8.2%). Consider tighter stop losses.',
          priority: 'high',
          actionable: true,
          impact: 'Could reduce drawdown by 30-40%'
        },
        {
          type: 'opportunity',
          title: 'Leverage Your Strength',
          description: 'You have a 75% success rate with momentum breakouts. Consider increasing position size for these setups.',
          priority: 'medium',
          actionable: true,
          impact: 'Could increase returns by 15-20%'
        },
        {
          type: 'warning',
          title: 'Avoid Resistance Trades',
          description: 'You have a 33% success rate with resistance rejections. Consider avoiding these setups.',
          priority: 'medium',
          actionable: true,
          impact: 'Could improve win rate by 5-10%'
        }
      ];

      setAnalytics(mockAnalytics);
      setPatterns(mockPatterns);
      setRecommendations(mockRecommendations);

    } catch (error) {
      console.error('Failed to load personal analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadPersonalAnalytics();
    setRefreshing(false);
  };

  const getPerformanceColor = (value: number, type: 'return' | 'ratio' | 'rate') => {
    if (type === 'return') {
      return value > 0 ? 'text-green-600' : 'text-red-600';
    }
    if (type === 'ratio') {
      return value > 1.5 ? 'text-green-600' : value > 1.0 ? 'text-yellow-600' : 'text-red-600';
    }
    if (type === 'rate') {
      return value > 60 ? 'text-green-600' : value > 40 ? 'text-yellow-600' : 'text-red-600';
    }
    return 'text-gray-600';
  };

  const getRecommendationIcon = (type: string) => {
    switch (type) {
      case 'improvement': return <TrendingUp className="w-5 h-5 text-blue-500" />;
      case 'opportunity': return <Zap className="w-5 h-5 text-green-500" />;
      case 'warning': return <AlertTriangle className="w-5 h-5 text-orange-500" />;
      default: return <Info className="w-5 h-5 text-gray-500" />;
    }
  };

  const getRecommendationColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'border-red-200 bg-red-50';
      case 'medium': return 'border-yellow-200 bg-yellow-50';
      case 'low': return 'border-green-200 bg-green-50';
      default: return 'border-gray-200 bg-gray-50';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        <span className="ml-3 text-gray-600">Analyzing your trading performance...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <BarChart3 className="w-6 h-6 text-purple-600" />
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Personal Analytics</h3>
            <p className="text-sm text-gray-600">Your trading performance insights</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          <select
            value={timeRange}
            onChange={(_e) => {/* Handle time range change */}}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            aria-label="Select time range for analytics"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="1y">Last year</option>
          </select>
          
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="flex items-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Performance Overview */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white border border-gray-200 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Return</p>
                <p className={`text-2xl font-bold ${getPerformanceColor(analytics.total_return, 'return')}`}>
                  {analytics.total_return > 0 ? '+' : ''}{analytics.total_return}%
                </p>
              </div>
              <TrendingUp className="w-8 h-8 text-green-500" />
            </div>
          </div>

          <div className="bg-white border border-gray-200 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Win Rate</p>
                <p className={`text-2xl font-bold ${getPerformanceColor(analytics.win_rate, 'rate')}`}>
                  {analytics.win_rate}%
                </p>
              </div>
              <Target className="w-8 h-8 text-blue-500" />
            </div>
          </div>

          <div className="bg-white border border-gray-200 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Sharpe Ratio</p>
                <p className={`text-2xl font-bold ${getPerformanceColor(analytics.sharpe_ratio, 'ratio')}`}>
                  {analytics.sharpe_ratio}
                </p>
              </div>
              <Award className="w-8 h-8 text-purple-500" />
            </div>
          </div>

          <div className="bg-white border border-gray-200 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Max Drawdown</p>
                <p className={`text-2xl font-bold ${getPerformanceColor(analytics.max_drawdown, 'return')}`}>
                  {analytics.max_drawdown}%
                </p>
              </div>
              <Shield className="w-8 h-8 text-red-500" />
            </div>
          </div>
        </div>
      )}

      {/* Trading Patterns */}
      {patterns.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-xl p-6">
          <div className="flex items-center space-x-2 mb-4">
            <Target className="w-5 h-5 text-green-600" />
            <h3 className="text-lg font-semibold text-gray-900">Your Trading Patterns</h3>
            <HelpTooltip content="Analysis of your trading patterns and success rates. Use this to identify your strengths and areas for improvement." />
          </div>
          
          <div className="space-y-4">
            {patterns.map((pattern, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <h4 className="font-semibold text-gray-900">{pattern.pattern_name}</h4>
                    <p className="text-sm text-gray-600">{pattern.description}</p>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-blue-600">
                      {pattern.success_rate}%
                    </div>
                    <div className="text-xs text-gray-500">Success Rate</div>
                  </div>
                </div>
                
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <div className="text-gray-500">Frequency</div>
                    <div className="font-medium">{pattern.frequency} trades</div>
                  </div>
                  <div>
                    <div className="text-gray-500">Avg Return</div>
                    <div className={`font-medium ${pattern.avg_return > 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {pattern.avg_return > 0 ? '+' : ''}{pattern.avg_return}%
                    </div>
                  </div>
                  <div>
                    <div className="text-gray-500">Performance</div>
                    <div className="font-medium">
                      {pattern.success_rate > 70 ? 'Excellent' : 
                       pattern.success_rate > 50 ? 'Good' : 'Needs Improvement'}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Personal Recommendations */}
      {recommendations.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-xl p-6">
          <div className="flex items-center space-x-2 mb-4">
            <Zap className="w-5 h-5 text-yellow-600" />
            <h3 className="text-lg font-semibold text-gray-900">Personal Recommendations</h3>
            <HelpTooltip content="AI-generated recommendations based on your trading patterns and performance. Focus on high-priority items first." />
          </div>
          
          <div className="space-y-4">
            {recommendations.map((recommendation, index) => (
              <div
                key={index}
                className={`border rounded-lg p-4 ${getRecommendationColor(recommendation.priority)}`}
              >
                <div className="flex items-start space-x-3">
                  {getRecommendationIcon(recommendation.type)}
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h4 className="font-semibold text-gray-900">{recommendation.title}</h4>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        recommendation.priority === 'high' ? 'bg-red-100 text-red-800' :
                        recommendation.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {recommendation.priority.toUpperCase()}
                      </span>
                    </div>
                    <p className="text-sm text-gray-700 mb-2">{recommendation.description}</p>
                    <div className="flex items-center justify-between">
                      <div className="text-xs text-gray-500">
                        <strong>Impact:</strong> {recommendation.impact}
                      </div>
                      {recommendation.actionable && (
                        <button className="text-xs text-blue-600 hover:text-blue-800 font-medium">
                          Learn More →
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {!analytics && !loading && (
        <div className="text-center py-12">
          <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Trading Data Available</h3>
          <p className="text-gray-600 mb-4">
            Start trading to see your personal analytics and performance insights.
          </p>
          <div className="text-sm text-gray-500">
            Analytics will appear after you make your first trade.
          </div>
        </div>
      )}
    </div>
  );
};
