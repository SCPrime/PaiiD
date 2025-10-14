/**
 * Template Customization Modal
 * Allows users to customize strategy template parameters before cloning
 */

import { useState } from 'react';
import { X, Copy, BarChart3, TrendingUp, Shield, Target } from 'lucide-react';
import { GlassCard, GlassButton, GlassInput } from './GlassmorphicComponents';
import { theme } from '../styles/theme';
import toast from 'react-hot-toast';

interface Template {
  id: string;
  name: string;
  description: string;
  strategy_type: string;
  risk_level: string;
  compatibility_score: number;
  expected_win_rate: number;
  avg_return_percent: number;
  max_drawdown_percent: number;
  recommended_for: string[];
  config: any;
}

interface TemplateCustomizationModalProps {
  template: Template | null;
  onClose: () => void;
  onCloneSuccess?: () => void;
}

export default function TemplateCustomizationModal({
  template,
  onClose,
  onCloneSuccess,
}: TemplateCustomizationModalProps) {
  const [customName, setCustomName] = useState('');
  const [positionSize, setPositionSize] = useState(0);
  const [stopLoss, setStopLoss] = useState(0);
  const [takeProfit, setTakeProfit] = useState(0);
  const [maxPositions, setMaxPositions] = useState(0);
  const [rsiPeriod, setRsiPeriod] = useState(14);
  const [isCloning, setIsCloning] = useState(false);

  // Initialize form values when template changes
  useState(() => {
    if (template) {
      setCustomName(`${template.name} (My Copy)`);
      setPositionSize(template.config?.position_size_percent || 10);
      setMaxPositions(template.config?.max_positions || 5);
      setRsiPeriod(template.config?.rsi_period || 14);

      // Extract stop loss and take profit from exit rules
      const exitRules = template.config?.exit_rules || [];
      const stopLossRule = exitRules.find((r: any) => r.type === 'stop_loss');
      const takeProfitRule = exitRules.find((r: any) => r.type === 'take_profit');

      setStopLoss(stopLossRule?.value || 3);
      setTakeProfit(takeProfitRule?.value || 8);
    }
  });

  if (!template) return null;

  const handleClone = async () => {
    const apiToken = process.env.NEXT_PUBLIC_API_TOKEN || '';
    const baseUrl = process.env.NEXT_PUBLIC_BACKEND_API_BASE_URL || 'https://paiid-backend.onrender.com';

    setIsCloning(true);

    try {
      // Build config overrides
      const configOverrides: any = {
        position_size_percent: positionSize,
        max_positions: maxPositions,
        rsi_period: rsiPeriod,
      };

      // Update exit rules
      const exitRules = [...(template.config.exit_rules || [])];
      const stopLossIndex = exitRules.findIndex((r: any) => r.type === 'stop_loss');
      const takeProfitIndex = exitRules.findIndex((r: any) => r.type === 'take_profit');

      if (stopLossIndex >= 0) {
        exitRules[stopLossIndex] = { ...exitRules[stopLossIndex], value: stopLoss };
      }
      if (takeProfitIndex >= 0) {
        exitRules[takeProfitIndex] = { ...exitRules[takeProfitIndex], value: takeProfit };
      }

      configOverrides.exit_rules = exitRules;

      const response = await fetch(`${baseUrl}/api/strategies/templates/${template.id}/clone`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${apiToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          custom_name: customName,
          customize_config: true,
          config_overrides: configOverrides,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to clone template: ${response.status}`);
      }

      const data = await response.json();
      toast.success(`Strategy "${customName}" created successfully!`);
      onClose();
      if (onCloneSuccess) onCloneSuccess();
    } catch (err: any) {
      console.error('Clone template error:', err);
      toast.error(err.message || 'Failed to clone template');
    } finally {
      setIsCloning(false);
    }
  };

  const getRiskColor = (risk: string) => {
    if (risk === 'Conservative') return theme.colors.success;
    if (risk === 'Moderate') return theme.colors.warning;
    return theme.colors.danger;
  };

  // Calculate changes from template defaults
  const originalPositionSize = template.config?.position_size_percent || 10;
  const originalMaxPositions = template.config?.max_positions || 5;
  const originalStopLoss = template.config?.exit_rules?.find((r: any) => r.type === 'stop_loss')?.value || 3;
  const originalTakeProfit = template.config?.exit_rules?.find((r: any) => r.type === 'take_profit')?.value || 8;

  const hasChanges =
    positionSize !== originalPositionSize ||
    maxPositions !== originalMaxPositions ||
    stopLoss !== originalStopLoss ||
    takeProfit !== originalTakeProfit ||
    customName !== `${template.name} (My Copy)`;

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0, 0, 0, 0.8)',
        backdropFilter: 'blur(4px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
        padding: theme.spacing.lg,
      }}
      onClick={onClose}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          maxWidth: '700px',
          width: '100%',
          maxHeight: '90vh',
          overflowY: 'auto',
          background: theme.background.primary,
          border: `1px solid ${theme.colors.border}`,
          borderRadius: theme.borderRadius.lg,
          padding: theme.spacing.xl,
        }}
      >
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: theme.spacing.lg }}>
          <div style={{ flex: 1 }}>
            <h2 style={{ fontSize: '24px', fontWeight: '600', color: theme.colors.text, margin: `0 0 ${theme.spacing.xs} 0` }}>
              Customize Template
            </h2>
            <p style={{ fontSize: '14px', color: theme.colors.textMuted, margin: 0 }}>
              {template.name}
            </p>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              color: theme.colors.textMuted,
              cursor: 'pointer',
              padding: theme.spacing.xs,
              borderRadius: theme.borderRadius.md,
              transition: theme.transitions.fast,
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = `${theme.colors.danger}20`;
              e.currentTarget.style.color = theme.colors.danger;
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'transparent';
              e.currentTarget.style.color = theme.colors.textMuted;
            }}
          >
            <X style={{ width: '20px', height: '20px' }} />
          </button>
        </div>

        {/* Template Info Banner */}
        <div
          style={{
            padding: theme.spacing.md,
            background: `${getRiskColor(template.risk_level)}10`,
            border: `1px solid ${getRiskColor(template.risk_level)}40`,
            borderRadius: theme.borderRadius.md,
            marginBottom: theme.spacing.lg,
          }}
        >
          <div style={{ display: 'flex', gap: theme.spacing.md, alignItems: 'center', flexWrap: 'wrap' }}>
            <div>
              <span style={{ fontSize: '11px', color: theme.colors.textMuted, textTransform: 'uppercase' }}>Risk</span>
              <p style={{ fontSize: '14px', fontWeight: '600', color: getRiskColor(template.risk_level), margin: 0 }}>
                {template.risk_level}
              </p>
            </div>
            <div>
              <span style={{ fontSize: '11px', color: theme.colors.textMuted, textTransform: 'uppercase' }}>Win Rate</span>
              <p style={{ fontSize: '14px', fontWeight: '600', color: theme.colors.text, margin: 0 }}>
                {template.expected_win_rate}%
              </p>
            </div>
            <div>
              <span style={{ fontSize: '11px', color: theme.colors.textMuted, textTransform: 'uppercase' }}>Avg Return</span>
              <p style={{ fontSize: '14px', fontWeight: '600', color: theme.colors.success, margin: 0 }}>
                +{template.avg_return_percent}%
              </p>
            </div>
            <div>
              <span style={{ fontSize: '11px', color: theme.colors.textMuted, textTransform: 'uppercase' }}>Max DD</span>
              <p style={{ fontSize: '14px', fontWeight: '600', color: theme.colors.danger, margin: 0 }}>
                -{template.max_drawdown_percent}%
              </p>
            </div>
          </div>
        </div>

        {/* Customization Form */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing.lg }}>
          {/* Strategy Name */}
          <div>
            <label style={{ display: 'block', fontSize: '13px', fontWeight: '600', color: theme.colors.text, marginBottom: theme.spacing.xs }}>
              Strategy Name
            </label>
            <input
              type="text"
              value={customName}
              onChange={(e) => setCustomName(e.target.value)}
              placeholder="Enter custom name"
              style={{
                width: '100%',
                padding: theme.spacing.md,
                background: theme.background.input,
                border: `1px solid ${theme.colors.border}`,
                borderRadius: theme.borderRadius.md,
                color: theme.colors.text,
                fontSize: '14px',
                outline: 'none',
              }}
            />
          </div>

          {/* Position Sizing */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: theme.spacing.xs }}>
              <label style={{ fontSize: '13px', fontWeight: '600', color: theme.colors.text }}>
                <Target style={{ width: '14px', height: '14px', display: 'inline', marginRight: '6px' }} />
                Position Size
              </label>
              <span style={{ fontSize: '16px', fontWeight: '600', color: theme.workflow.strategyBuilder }}>
                {positionSize}%
              </span>
            </div>
            <input
              type="range"
              min="1"
              max="20"
              step="0.5"
              value={positionSize}
              onChange={(e) => setPositionSize(parseFloat(e.target.value))}
              style={{ width: '100%' }}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: theme.colors.textMuted, marginTop: '4px' }}>
              <span>Conservative (1%)</span>
              <span>Original: {originalPositionSize}%</span>
              <span>Aggressive (20%)</span>
            </div>
          </div>

          {/* Stop Loss & Take Profit */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: theme.spacing.md }}>
            <div>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: '600', color: theme.colors.text, marginBottom: theme.spacing.xs }}>
                <Shield style={{ width: '14px', height: '14px', display: 'inline', marginRight: '6px' }} />
                Stop Loss %
              </label>
              <input
                type="number"
                min="0.5"
                max="20"
                step="0.5"
                value={stopLoss}
                onChange={(e) => setStopLoss(parseFloat(e.target.value) || 0)}
                style={{
                  width: '100%',
                  padding: theme.spacing.md,
                  background: theme.background.input,
                  border: `1px solid ${theme.colors.border}`,
                  borderRadius: theme.borderRadius.md,
                  color: theme.colors.text,
                  fontSize: '14px',
                  outline: 'none',
                }}
              />
              <p style={{ fontSize: '11px', color: theme.colors.textMuted, margin: '4px 0 0 0' }}>
                Original: {originalStopLoss}%
              </p>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: '600', color: theme.colors.text, marginBottom: theme.spacing.xs }}>
                <TrendingUp style={{ width: '14px', height: '14px', display: 'inline', marginRight: '6px' }} />
                Take Profit %
              </label>
              <input
                type="number"
                min="1"
                max="50"
                step="0.5"
                value={takeProfit}
                onChange={(e) => setTakeProfit(parseFloat(e.target.value) || 0)}
                style={{
                  width: '100%',
                  padding: theme.spacing.md,
                  background: theme.background.input,
                  border: `1px solid ${theme.colors.border}`,
                  borderRadius: theme.borderRadius.md,
                  color: theme.colors.text,
                  fontSize: '14px',
                  outline: 'none',
                }}
              />
              <p style={{ fontSize: '11px', color: theme.colors.textMuted, margin: '4px 0 0 0' }}>
                Original: {originalTakeProfit}%
              </p>
            </div>
          </div>

          {/* Max Positions */}
          <div>
            <label style={{ display: 'block', fontSize: '13px', fontWeight: '600', color: theme.colors.text, marginBottom: theme.spacing.xs }}>
              <BarChart3 style={{ width: '14px', height: '14px', display: 'inline', marginRight: '6px' }} />
              Max Positions
            </label>
            <input
              type="number"
              min="1"
              max="10"
              step="1"
              value={maxPositions}
              onChange={(e) => setMaxPositions(parseInt(e.target.value) || 0)}
              style={{
                width: '100%',
                padding: theme.spacing.md,
                background: theme.background.input,
                border: `1px solid ${theme.colors.border}`,
                borderRadius: theme.borderRadius.md,
                color: theme.colors.text,
                fontSize: '14px',
                outline: 'none',
              }}
            />
            <p style={{ fontSize: '11px', color: theme.colors.textMuted, margin: '4px 0 0 0' }}>
              Original: {originalMaxPositions} | Diversification vs. concentration tradeoff
            </p>
          </div>

          {/* Changes Indicator */}
          {hasChanges && (
            <div
              style={{
                padding: theme.spacing.sm,
                background: `${theme.colors.info}10`,
                border: `1px solid ${theme.colors.info}40`,
                borderRadius: theme.borderRadius.md,
                fontSize: '13px',
                color: theme.colors.info,
              }}
            >
              You've made custom changes to this template
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', gap: theme.spacing.sm, marginTop: theme.spacing.xl }}>
          <GlassButton
            variant="secondary"
            onClick={onClose}
            disabled={isCloning}
            style={{ flex: 1 }}
          >
            Cancel
          </GlassButton>
          <GlassButton
            variant="workflow"
            workflowColor="primary"
            onClick={handleClone}
            disabled={isCloning || !customName.trim()}
            style={{ flex: 1 }}
          >
            {isCloning ? (
              <>
                <div className="animate-spin" style={{ width: '16px', height: '16px', border: '2px solid currentColor', borderTopColor: 'transparent', borderRadius: '50%' }} />
                Cloning...
              </>
            ) : (
              <>
                <Copy style={{ width: '16px', height: '16px' }} />
                Clone Strategy
              </>
            )}
          </GlassButton>
        </div>
      </div>
    </div>
  );
}
