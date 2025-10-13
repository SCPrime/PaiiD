import { useHotkeys } from 'react-hotkeys-hook';
import { useState } from 'react';
import { Keyboard, X } from 'lucide-react';
import { theme } from '../styles/theme';
import { Button } from './ui';

interface KeyboardShortcutsProps {
  onOpenTrade?: () => void;
  onQuickBuy?: () => void;
  onQuickSell?: () => void;
  onCloseModal?: () => void;
}

export default function KeyboardShortcuts({
  onOpenTrade,
  onQuickBuy,
  onQuickSell,
  onCloseModal,
}: KeyboardShortcutsProps) {
  const [showHelp, setShowHelp] = useState(false);

  // Ctrl+T: Open Execute Trade
  useHotkeys('ctrl+t', (e) => {
    e.preventDefault();
    if (onOpenTrade) onOpenTrade();
  }, { enableOnFormTags: false });

  // Ctrl+B: Quick Buy
  useHotkeys('ctrl+b', (e) => {
    e.preventDefault();
    if (onQuickBuy) onQuickBuy();
  }, { enableOnFormTags: false });

  // Ctrl+S: Quick Sell (override browser save)
  useHotkeys('ctrl+s', (e) => {
    e.preventDefault();
    if (onQuickSell) onQuickSell();
  }, { enableOnFormTags: false });

  // Esc: Close modals
  useHotkeys('esc', (e) => {
    if (showHelp) {
      e.preventDefault();
      setShowHelp(false);
    } else if (onCloseModal) {
      e.preventDefault();
      onCloseModal();
    }
  });

  // Ctrl+/: Show keyboard shortcuts help
  useHotkeys('ctrl+/', (e) => {
    e.preventDefault();
    setShowHelp(!showHelp);
  });

  // Ctrl+K: Show keyboard shortcuts help (alternative)
  useHotkeys('ctrl+k', (e) => {
    e.preventDefault();
    setShowHelp(!showHelp);
  });

  const shortcuts = [
    { keys: 'Ctrl + T', description: 'Open Execute Trade form' },
    { keys: 'Ctrl + B', description: 'Quick Buy (opens trade form with buy selected)' },
    { keys: 'Ctrl + S', description: 'Quick Sell (opens trade form with sell selected)' },
    { keys: 'Esc', description: 'Close modals and dialogs' },
    { keys: 'Ctrl + /', description: 'Show/hide keyboard shortcuts help' },
    { keys: 'Ctrl + K', description: 'Show/hide keyboard shortcuts help (alt)' },
  ];

  return (
    <>
      {/* Help Button - Fixed position in bottom right */}
      <button
        onClick={() => setShowHelp(!showHelp)}
        style={{
          position: 'fixed',
          bottom: theme.spacing.xl,
          right: theme.spacing.xl,
          padding: '12px',
          background: theme.background.card,
          border: `1px solid ${theme.colors.border}`,
          borderRadius: theme.borderRadius.md,
          color: theme.colors.textMuted,
          cursor: 'pointer',
          boxShadow: theme.glow.green,
          zIndex: 1000,
          transition: theme.transitions.normal,
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = 'scale(1.05)';
          e.currentTarget.style.borderColor = theme.colors.primary;
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'scale(1)';
          e.currentTarget.style.borderColor = theme.colors.border;
        }}
        title="Keyboard shortcuts (Ctrl+K)"
      >
        <Keyboard size={20} />
      </button>

      {/* Help Modal */}
      {showHelp && (
        <>
          {/* Backdrop */}
          <div
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'rgba(0, 0, 0, 0.7)',
              backdropFilter: 'blur(4px)',
              zIndex: 9998,
            }}
            onClick={() => setShowHelp(false)}
          />

          {/* Modal */}
          <div
            style={{
              position: 'fixed',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              width: '90%',
              maxWidth: '600px',
              background: theme.background.card,
              border: `1px solid ${theme.colors.border}`,
              borderRadius: theme.borderRadius.lg,
              boxShadow: theme.glow.green,
              padding: theme.spacing.xl,
              zIndex: 9999,
            }}
          >
            {/* Header */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: theme.spacing.lg,
              paddingBottom: theme.spacing.md,
              borderBottom: `1px solid ${theme.colors.border}`,
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing.md }}>
                <div style={{
                  padding: theme.spacing.sm,
                  background: 'rgba(16, 185, 129, 0.1)',
                  borderRadius: theme.borderRadius.md,
                }}>
                  <Keyboard size={24} style={{ color: theme.colors.primary }} />
                </div>
                <h2 style={{
                  fontSize: '24px',
                  fontWeight: '700',
                  color: theme.colors.text,
                  margin: 0,
                }}>
                  Keyboard Shortcuts
                </h2>
              </div>
              <button
                onClick={() => setShowHelp(false)}
                style={{
                  padding: theme.spacing.sm,
                  background: 'transparent',
                  border: 'none',
                  color: theme.colors.textMuted,
                  cursor: 'pointer',
                  borderRadius: theme.borderRadius.sm,
                  transition: theme.transitions.normal,
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = theme.background.input;
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'transparent';
                }}
              >
                <X size={20} />
              </button>
            </div>

            {/* Shortcuts List */}
            <div style={{ marginBottom: theme.spacing.lg }}>
              {shortcuts.map((shortcut, index) => (
                <div
                  key={index}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: theme.spacing.md,
                    marginBottom: theme.spacing.sm,
                    background: index % 2 === 0 ? theme.background.input : 'transparent',
                    borderRadius: theme.borderRadius.sm,
                  }}
                >
                  <span style={{
                    fontSize: '14px',
                    color: theme.colors.text,
                  }}>
                    {shortcut.description}
                  </span>
                  <code style={{
                    padding: '4px 8px',
                    background: theme.background.card,
                    border: `1px solid ${theme.colors.border}`,
                    borderRadius: theme.borderRadius.sm,
                    fontSize: '12px',
                    fontFamily: 'monospace',
                    color: theme.colors.primary,
                    fontWeight: '600',
                  }}>
                    {shortcut.keys}
                  </code>
                </div>
              ))}
            </div>

            {/* Footer */}
            <div style={{
              paddingTop: theme.spacing.md,
              borderTop: `1px solid ${theme.colors.border}`,
              textAlign: 'center',
            }}>
              <p style={{
                fontSize: '13px',
                color: theme.colors.textMuted,
                margin: 0,
              }}>
                Press <code style={{
                  padding: '2px 6px',
                  background: theme.background.input,
                  borderRadius: theme.borderRadius.sm,
                  fontFamily: 'monospace',
                }}>Esc</code> or click outside to close
              </p>
            </div>
          </div>
        </>
      )}
    </>
  );
}
