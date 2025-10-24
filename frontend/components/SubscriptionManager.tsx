/**
 * Subscription Manager Component
 *
 * Handles subscription tier display, upgrades, usage tracking, and billing.
 *
 * Phase 2E: Monetization Engine - Payment UI
 */

import React, { useState, useEffect } from 'react';
import { CreditCard, TrendingUp, Check, X, Zap, Crown, Gift } from 'lucide-react';

interface SubscriptionTier {
  name: string;
  price: number;
  limits: {
    ml_predictions_per_month: number;
    backtests_per_month: number;
    strategies: number;
    watchlist_size: number;
    news_articles_per_day: number;
    portfolio_optimization: boolean;
    advanced_ml: boolean;
    priority_support: boolean;
  };
}

interface Subscription {
  tier: string;
  status: string;
  price: number;
  is_active: boolean;
  is_trial: boolean;
  current_period_end: string | null;
  days_until_renewal: number | null;
  cancel_at_period_end: boolean;
  limits: SubscriptionTier['limits'];
}

interface UsageData {
  feature: string;
  current_usage: number;
  limit: number;
  percentage_used: number;
  within_limit: boolean;
}

const SubscriptionManager: React.FC = () => {
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [tiers, setTiers] = useState<Record<string, SubscriptionTier>>({});
  const [usage, setUsage] = useState<Record<string, UsageData>>({});
  const [loading, setLoading] = useState(true);
  const [upgrading, setUpgrading] = useState(false);
  const [selectedTier, setSelectedTier] = useState<string | null>(null);

  useEffect(() => {
    fetchSubscriptionData();
  }, []);

  const fetchSubscriptionData = async () => {
    try {
      setLoading(true);

      // Fetch current subscription
      const subRes = await fetch('/api/proxy/api/subscription/current', {
        headers: {
          Authorization: `Bearer ${process.env.NEXT_PUBLIC_API_TOKEN}`,
        },
      });
      const subData = await subRes.json();
      setSubscription(subData);

      // Fetch available tiers
      const tiersRes = await fetch('/api/proxy/api/subscription/tiers', {
        headers: {
          Authorization: `Bearer ${process.env.NEXT_PUBLIC_API_TOKEN}`,
        },
      });
      const tiersData = await tiersRes.json();
      setTiers(tiersData.tiers);

      // Fetch usage data
      const features = ['ml_prediction', 'backtest', 'strategy', 'news'];
      const usagePromises = features.map(async (feature) => {
        const res = await fetch(`/api/proxy/api/subscription/usage/${feature}`, {
          headers: {
            Authorization: `Bearer ${process.env.NEXT_PUBLIC_API_TOKEN}`,
          },
        });
        return { feature, data: await res.json() };
      });

      const usageResults = await Promise.all(usagePromises);
      const usageMap: Record<string, UsageData> = {};
      usageResults.forEach(({ feature, data }) => {
        usageMap[feature] = data;
      });
      setUsage(usageMap);

      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch subscription data:', error);
      setLoading(false);
    }
  };

  const handleUpgrade = async (tier: string) => {
    try {
      setUpgrading(true);
      setSelectedTier(tier);

      // Create checkout session
      const res = await fetch('/api/proxy/api/subscription/checkout-session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${process.env.NEXT_PUBLIC_API_TOKEN}`,
        },
        body: JSON.stringify({
          tier,
          trial_days: tier === 'pro' ? 7 : null, // 7-day trial for Pro
        }),
      });

      const data = await res.json();

      // Redirect to Stripe Checkout
      if (data.url) {
        window.location.href = data.url;
      }
    } catch (error) {
      console.error('Upgrade failed:', error);
      setUpgrading(false);
      setSelectedTier(null);
    }
  };

  const handleManageBilling = async () => {
    try {
      const res = await fetch('/api/proxy/api/subscription/billing-portal', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${process.env.NEXT_PUBLIC_API_TOKEN}`,
        },
      });

      const data = await res.json();

      // Redirect to Stripe Billing Portal
      if (data.url) {
        window.location.href = data.url;
      }
    } catch (error) {
      console.error('Failed to open billing portal:', error);
    }
  };

  const getTierIcon = (tier: string) => {
    switch (tier) {
      case 'free':
        return <Gift size={24} />;
      case 'pro':
        return <Zap size={24} />;
      case 'premium':
        return <Crown size={24} />;
      default:
        return <CreditCard size={24} />;
    }
  };

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'free':
        return '#94a3b8';
      case 'pro':
        return '#10b981';
      case 'premium':
        return '#f59e0b';
      default:
        return '#64748b';
    }
  };

  const renderUsageBar = (usageData: UsageData) => {
    const { current_usage, limit, percentage_used, within_limit } = usageData;
    const displayLimit = limit === -1 ? '∞' : limit;

    return (
      <div style={{ marginBottom: '20px' }}>
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            marginBottom: '8px',
            fontSize: '14px',
            color: '#cbd5e1',
          }}
        >
          <span style={{ textTransform: 'capitalize' }}>
            {usageData.feature.replace('_', ' ')}
          </span>
          <span style={{ color: within_limit ? '#10b981' : '#ef4444' }}>
            {current_usage} / {displayLimit}
          </span>
        </div>
        <div
          style={{
            width: '100%',
            height: '8px',
            background: 'rgba(51, 65, 85, 0.6)',
            borderRadius: '4px',
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              width: limit === -1 ? '0%' : `${Math.min(percentage_used, 100)}%`,
              height: '100%',
              background:
                percentage_used > 90
                  ? 'linear-gradient(90deg, #ef4444 0%, #dc2626 100%)'
                  : percentage_used > 70
                  ? 'linear-gradient(90deg, #f59e0b 0%, #d97706 100%)'
                  : 'linear-gradient(90deg, #10b981 0%, #059669 100%)',
              transition: 'width 0.3s ease',
            }}
          />
        </div>
      </div>
    );
  };

  const renderTierCard = (tierId: string, tier: SubscriptionTier) => {
    const isCurrent = subscription?.tier === tierId;
    const color = getTierColor(tierId);

    return (
      <div
        key={tierId}
        style={{
          background: isCurrent
            ? 'rgba(16, 185, 129, 0.1)'
            : 'rgba(15, 23, 42, 0.6)',
          border: isCurrent
            ? '2px solid rgba(16, 185, 129, 0.5)'
            : '1px solid rgba(71, 85, 105, 0.3)',
          borderRadius: '12px',
          padding: '24px',
          backdropFilter: 'blur(10px)',
          flex: 1,
          minWidth: '280px',
          position: 'relative',
          transition: 'transform 0.2s ease, box-shadow 0.2s ease',
        }}
        onMouseEnter={(e) => {
          if (!isCurrent) {
            e.currentTarget.style.transform = 'translateY(-4px)';
            e.currentTarget.style.boxShadow = '0 8px 24px rgba(0, 0, 0, 0.3)';
          }
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'translateY(0)';
          e.currentTarget.style.boxShadow = 'none';
        }}
      >
        {isCurrent && (
          <div
            style={{
              position: 'absolute',
              top: '12px',
              right: '12px',
              background: 'rgba(16, 185, 129, 0.2)',
              color: '#10b981',
              padding: '4px 12px',
              borderRadius: '12px',
              fontSize: '12px',
              fontWeight: 600,
            }}
          >
            CURRENT
          </div>
        )}

        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '16px' }}>
          <div style={{ color, marginRight: '12px' }}>{getTierIcon(tierId)}</div>
          <div>
            <h3 style={{ margin: 0, fontSize: '24px', color: '#fff' }}>
              {tier.name}
            </h3>
            <p style={{ margin: '4px 0 0 0', fontSize: '32px', fontWeight: 700, color }}>
              ${tier.price}
              <span style={{ fontSize: '16px', color: '#94a3b8', fontWeight: 400 }}>
                /month
              </span>
            </p>
          </div>
        </div>

        <div style={{ marginBottom: '20px' }}>
          <div style={{ fontSize: '14px', color: '#cbd5e1', marginBottom: '12px' }}>
            <strong>Features:</strong>
          </div>
          {renderFeatureList(tier.limits)}
        </div>

        {!isCurrent && (
          <button
            onClick={() => handleUpgrade(tierId)}
            disabled={upgrading && selectedTier === tierId}
            style={{
              width: '100%',
              padding: '12px',
              background:
                tierId === 'premium'
                  ? 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)'
                  : 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              border: 'none',
              borderRadius: '8px',
              color: '#fff',
              fontSize: '16px',
              fontWeight: 600,
              cursor: upgrading && selectedTier === tierId ? 'not-allowed' : 'pointer',
              opacity: upgrading && selectedTier === tierId ? 0.6 : 1,
            }}
          >
            {upgrading && selectedTier === tierId ? 'Loading...' : `Upgrade to ${tier.name}`}
          </button>
        )}
      </div>
    );
  };

  const renderFeatureList = (limits: SubscriptionTier['limits']) => {
    const features = [
      {
        label: 'ML Predictions',
        value: limits.ml_predictions_per_month === -1 ? 'Unlimited' : `${limits.ml_predictions_per_month}/month`,
      },
      {
        label: 'Backtests',
        value: limits.backtests_per_month === -1 ? 'Unlimited' : `${limits.backtests_per_month}/month`,
      },
      {
        label: 'Strategies',
        value: limits.strategies === -1 ? 'Unlimited' : limits.strategies,
      },
      {
        label: 'Portfolio Optimization',
        value: limits.portfolio_optimization,
      },
      {
        label: 'Advanced ML',
        value: limits.advanced_ml,
      },
      {
        label: 'Priority Support',
        value: limits.priority_support,
      },
    ];

    return (
      <div style={{ fontSize: '13px', color: '#cbd5e1' }}>
        {features.map((feature, idx) => (
          <div
            key={idx}
            style={{
              display: 'flex',
              alignItems: 'center',
              marginBottom: '8px',
            }}
          >
            {typeof feature.value === 'boolean' ? (
              feature.value ? (
                <Check size={16} color="#10b981" style={{ marginRight: '8px' }} />
              ) : (
                <X size={16} color="#64748b" style={{ marginRight: '8px' }} />
              )
            ) : (
              <Check size={16} color="#10b981" style={{ marginRight: '8px' }} />
            )}
            <span>
              {feature.label}
              {typeof feature.value !== 'boolean' && `: ${feature.value}`}
            </span>
          </div>
        ))}
      </div>
    );
  };

  if (loading) {
    return (
      <div
        style={{
          padding: '40px',
          textAlign: 'center',
          color: '#94a3b8',
        }}
      >
        Loading subscription details...
      </div>
    );
  }

  return (
    <div style={{ padding: '20px' }}>
      {/* Current Subscription Summary */}
      {subscription && (
        <div
          style={{
            background: 'rgba(15, 23, 42, 0.6)',
            borderRadius: '12px',
            padding: '24px',
            marginBottom: '32px',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(71, 85, 105, 0.3)',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h2 style={{ margin: '0 0 8px 0', fontSize: '28px', color: '#fff' }}>
                Your Subscription
              </h2>
              <p style={{ margin: 0, fontSize: '16px', color: '#94a3b8' }}>
                {subscription.tier.charAt(0).toUpperCase() + subscription.tier.slice(1)} Plan •{' '}
                {subscription.is_trial ? 'Trial Period' : subscription.status}
              </p>
            </div>
            {subscription.tier !== 'free' && (
              <button
                onClick={handleManageBilling}
                style={{
                  padding: '12px 24px',
                  background: 'rgba(71, 85, 105, 0.3)',
                  border: '1px solid rgba(148, 163, 184, 0.3)',
                  borderRadius: '8px',
                  color: '#cbd5e1',
                  fontSize: '14px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                }}
              >
                <CreditCard size={16} />
                Manage Billing
              </button>
            )}
          </div>

          {/* Usage Stats */}
          <div style={{ marginTop: '32px' }}>
            <h3 style={{ margin: '0 0 20px 0', fontSize: '18px', color: '#cbd5e1' }}>
              Usage This Month
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
              {Object.values(usage).map((usageData) => renderUsageBar(usageData))}
            </div>
          </div>
        </div>
      )}

      {/* Available Tiers */}
      <div style={{ marginBottom: '32px' }}>
        <h2 style={{ margin: '0 0 24px 0', fontSize: '28px', color: '#fff' }}>
          Available Plans
        </h2>
        <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
          {Object.entries(tiers).map(([tierId, tier]) => renderTierCard(tierId, tier))}
        </div>
      </div>

      {/* Billing Info */}
      {subscription && subscription.tier !== 'free' && (
        <div
          style={{
            background: 'rgba(15, 23, 42, 0.4)',
            borderRadius: '8px',
            padding: '16px',
            fontSize: '14px',
            color: '#94a3b8',
            border: '1px solid rgba(71, 85, 105, 0.2)',
          }}
        >
          <p style={{ margin: 0 }}>
            {subscription.cancel_at_period_end ? (
              <>
                Your subscription will end on{' '}
                {subscription.current_period_end
                  ? new Date(subscription.current_period_end).toLocaleDateString()
                  : 'N/A'}
              </>
            ) : (
              <>
                Next billing date:{' '}
                {subscription.current_period_end
                  ? new Date(subscription.current_period_end).toLocaleDateString()
                  : 'N/A'}{' '}
                ({subscription.days_until_renewal} days)
              </>
            )}
          </p>
        </div>
      )}
    </div>
  );
};

export default SubscriptionManager;
