/**
 * ML Intelligence Dashboard
 * 
 * Enterprise-grade ML features made accessible for friends and family:
 * - Pattern recognition with visual explanations
 * - Market regime detection with strategy recommendations
 * - Personal analytics and insights
 */

import {
    Brain,
    CheckCircle,
    Loader2,
    RefreshCw,
    Shield,
    Target,
    TrendingUp,
    Zap
} from 'lucide-react';
import React, { useEffect, useState } from 'react';
import { HelpTooltip } from '../HelpTooltip';
import { useToast } from '../ui/Toast';

interface MLInsight {
  id: string;
  type: 'pattern' | 'regime' | 'strategy' | 'risk';
  title: string;
  description: string;
  confidence: number;
  actionable: boolean;
  impact: 'high' | 'medium' | 'low';
  timestamp: string;
  details?: Record<string, unknown>;
}

interface MarketRegime {
  regime: string;
  confidence: number;
  description: string;
  recommended_strategies: string[];
  features: {
    trend_direction: number;
    trend_strength: number;
    volatility: number;
    rsi: number;
  };
}

interface Pattern {
  pattern_type: string;
  signal: string;
  confidence: number;
  description: string;
  target_price?: number;
  stop_loss?: number;
  key_levels: Record<string, number>;
}

export const MLIntelligenceDashboard: React.FC = () => {
  const [insights, setInsights] = useState<MLInsight[]>([]);
  const [marketRegime, setMarketRegime] = useState<MarketRegime | null>(null);
  const [patterns, setPatterns] = useState<Pattern[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedSymbol, setSelectedSymbol] = useState('SPY');
  const { toast } = useToast();

  // Load ML insights on component mount
  useEffect(() => {
    loadMLInsights();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedSymbol]);

  const loadMLInsights = async () => {
    setLoading(true);
    try {
      // Load market regime
      const regimeResponse = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_API_BASE_URL}/api/ml/market-regime?symbol=${selectedSymbol}&lookback_days=90`
      );
      const regimeData = await regimeResponse.json();
      
      if (regimeData.regime) {
        setMarketRegime(regimeData);
      }

      // Load patterns
      const patternsResponse = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_API_BASE_URL}/api/ml/detect-patterns?symbol=${selectedSymbol}&lookback_days=90&min_confidence=0.6`
      );
      const patternsData = await patternsResponse.json();
      
      if (patternsData.patterns) {
        setPatterns(patternsData.patterns);
      }

      // Generate insights from the data
      generateInsights(regimeData, patternsData.patterns || []);

    } catch (error) {
      console.error('Failed to load ML insights:', error);
      toast({
        title: 'ML Analysis Failed',
        description: 'Unable to load market intelligence. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const generateInsights = (regimeData: MarketRegime | null, patterns: Pattern[]) => {
    const newInsights: MLInsight[] = [];

    // Market regime insight
    if (regimeData.regime) {
      newInsights.push({
        id: 'market-regime',
        type: 'regime',
        title: `Market is ${regimeData.regime.replace('_', ' ')}`,
        description: getRegimeDescription(regimeData.regime, regimeData.confidence),
        confidence: regimeData.confidence,
        actionable: true,
        impact: regimeData.confidence > 0.8 ? 'high' : 'medium',
        timestamp: new Date().toISOString(),
        details: regimeData,
      });
    }

    // Pattern insights
    patterns.forEach((pattern, index) => {
      newInsights.push({
        id: `pattern-${index}`,
        type: 'pattern',
        title: `${pattern.pattern_type.replace('_', ' ')} detected`,
        description: pattern.description,
        confidence: pattern.confidence,
        actionable: true,
        impact: pattern.confidence > 0.8 ? 'high' : 'medium',
        timestamp: new Date().toISOString(),
        details: pattern,
      });
    });

    // Strategy recommendations
    if (regimeData.recommended_strategies?.length > 0) {
      newInsights.push({
        id: 'strategy-recommendation',
        type: 'strategy',
        title: 'Strategy Recommendations',
        description: `Consider these strategies: ${regimeData.recommended_strategies.join(', ')}`,
        confidence: regimeData.confidence,
        actionable: true,
        impact: 'high',
        timestamp: new Date().toISOString(),
        details: regimeData.recommended_strategies,
      });
    }

    setInsights(newInsights);
  };

  const getRegimeDescription = (regime: string, confidence: number) => {
    const descriptions = {
      'trending_bullish': 'Market is in a strong upward trend with positive momentum.',
      'trending_bearish': 'Market is in a downward trend with negative momentum.',
      'ranging': 'Market is moving sideways with no clear direction.',
      'high_volatility': 'Market is experiencing high volatility with large price swings.',
    };
    
    const baseDescription = descriptions[regime as keyof typeof descriptions] || 'Market state is unclear.';
    const confidenceText = confidence > 0.8 ? 'High confidence' : confidence > 0.6 ? 'Moderate confidence' : 'Low confidence';
    
    return `${baseDescription} (${confidenceText}: ${Math.round(confidence * 100)}%)`;
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadMLInsights();
    setRefreshing(false);
    toast({
      title: 'ML Analysis Updated',
      description: 'Market intelligence has been refreshed with latest data.',
    });
  };

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'pattern': return <Target className="w-5 h-5" />;
      case 'regime': return <TrendingUp className="w-5 h-5" />;
      case 'strategy': return <Zap className="w-5 h-5" />;
      case 'risk': return <Shield className="w-5 h-5" />;
      default: return <Brain className="w-5 h-5" />;
    }
  };

  const getInsightColor = (impact: string) => {
    switch (impact) {
      case 'high': return 'text-red-600 bg-red-50 border-red-200';
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'low': return 'text-green-600 bg-green-50 border-green-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        <span className="ml-2 text-gray-600">Analyzing market intelligence...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Brain className="w-8 h-8 text-blue-600" />
          <div>
            <h2 className="text-2xl font-bold text-gray-900">ML Intelligence</h2>
            <p className="text-gray-600">AI-powered market analysis for smarter decisions</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          <select
            value={selectedSymbol}
            onChange={(e) => setSelectedSymbol(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            aria-label="Select symbol for analysis"
          >
            <option value="SPY">SPY (S&P 500)</option>
            <option value="QQQ">QQQ (NASDAQ)</option>
            <option value="IWM">IWM (Russell 2000)</option>
            <option value="AAPL">AAPL (Apple)</option>
            <option value="MSFT">MSFT (Microsoft)</option>
          </select>
          
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Market Regime Card */}
      {marketRegime && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-6">
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-3">
              <TrendingUp className="w-6 h-6 text-blue-600" />
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Market Regime</h3>
                <p className="text-gray-600">{marketRegime.regime.replace('_', ' ').toUpperCase()}</p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-blue-600">
                {Math.round(marketRegime.confidence * 100)}%
              </div>
              <div className="text-sm text-gray-500">Confidence</div>
            </div>
          </div>
          
          <p className="mt-3 text-gray-700">{getRegimeDescription(marketRegime.regime, marketRegime.confidence)}</p>
          
          {marketRegime.recommended_strategies?.length > 0 && (
            <div className="mt-4">
              <h4 className="text-sm font-medium text-gray-900 mb-2">Recommended Strategies:</h4>
              <div className="flex flex-wrap gap-2">
                {marketRegime.recommended_strategies.map((strategy, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
                  >
                    {strategy.replace('_', ' ')}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Insights Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {insights.map((insight) => (
          <div
            key={insight.id}
            className={`border rounded-xl p-4 ${getInsightColor(insight.impact)}`}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center space-x-2">
                {getInsightIcon(insight.type)}
                <span className="font-medium text-sm">{insight.title}</span>
              </div>
              <div className="flex items-center space-x-1">
                <CheckCircle className="w-4 h-4 text-green-500" />
                <span className="text-xs text-gray-500">
                  {Math.round(insight.confidence * 100)}%
                </span>
              </div>
            </div>
            
            <p className="text-sm text-gray-700 mb-3">{insight.description}</p>
            
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-500">
                {new Date(insight.timestamp).toLocaleTimeString()}
              </span>
              {insight.actionable && (
                <button className="text-xs text-blue-600 hover:text-blue-800 font-medium">
                  View Details →
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Patterns Section */}
      {patterns.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-xl p-6">
          <div className="flex items-center space-x-2 mb-4">
            <Target className="w-5 h-5 text-purple-600" />
            <h3 className="text-lg font-semibold text-gray-900">Detected Patterns</h3>
            <HelpTooltip content="Technical analysis patterns detected in recent price action. These can signal potential trading opportunities." />
          </div>
          
          <div className="space-y-3">
            {patterns.map((pattern, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className={`w-3 h-3 rounded-full ${
                    pattern.signal === 'bullish' ? 'bg-green-500' : 
                    pattern.signal === 'bearish' ? 'bg-red-500' : 'bg-gray-500'
                  }`} />
                  <div>
                    <div className="font-medium text-gray-900">
                      {pattern.pattern_type.replace('_', ' ').toUpperCase()}
                    </div>
                    <div className="text-sm text-gray-600">{pattern.description}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium text-gray-900">
                    {Math.round(pattern.confidence * 100)}% confidence
                  </div>
                  <div className="text-xs text-gray-500">{pattern.signal}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {insights.length === 0 && !loading && (
        <div className="text-center py-12">
          <Brain className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Insights Available</h3>
          <p className="text-gray-600 mb-4">
            ML analysis is still processing. Try refreshing or check back in a few minutes.
          </p>
          <button
            onClick={handleRefresh}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Refresh Analysis
          </button>
        </div>
      )}
    </div>
  );
};
