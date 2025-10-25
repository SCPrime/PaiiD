"use client";
import { theme } from "../styles/theme";

interface ConfirmDialogProps {
  isOpen: boolean;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  confirmVariant?: "primary" | "danger" | "warning";
  onConfirm: () => void;
  onCancel: () => void;
  // Enhanced props for trade preview
  orderDetails?: {
    symbol: string;
    side: "buy" | "sell";
    qty: number;
    type: "market" | "limit";
    limitPrice?: number;
    asset_class?: "stock" | "option";
    option_type?: "call" | "put";
    strike_price?: number;
    expiration_date?: string;
  };
  riskWarning?: boolean;
}

export default function ConfirmDialog({
  isOpen,
  title,
  message,
  confirmText = "Confirm",
  cancelText = "Cancel",
  confirmVariant = "primary",
  onConfirm,
  onCancel,
  orderDetails,
  riskWarning = false,
}: ConfirmDialogProps) {
  if (!isOpen) return null;

  const variantStyles = {
    primary: {
      background: theme.colors.primary,
      glow: theme.glow.green,
    },
    danger: {
      background: theme.colors.danger,
      glow: theme.glow.red,
    },
    warning: {
      background: theme.colors.warning,
      glow: theme.glow.orange,
    },
  };

  const variant = variantStyles[confirmVariant];

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: "rgba(0, 0, 0, 0.7)",
        backdropFilter: theme.blur.medium,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 1000,
        animation: "fadeIn 0.2s ease",
      }}
      onClick={onCancel}
    >
      <div
        style={{
          background: theme.background.glass,
          backdropFilter: theme.blur.light,
          border: `1px solid ${theme.colors.border}`,
          borderRadius: theme.borderRadius.lg,
          boxShadow: `0 20px 60px rgba(0, 0, 0, 0.5), ${theme.glow.green}`,
          padding: theme.spacing.xl,
          maxWidth: "500px",
          width: "90%",
          animation: "slideUp 0.3s ease",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2
          style={{
            color: theme.colors.text,
            fontSize: "24px",
            fontWeight: "700",
            marginBottom: theme.spacing.md,
            textAlign: "center",
          }}
        >
          {title}
        </h2>

        <p
          style={{
            color: theme.colors.textMuted,
            fontSize: "16px",
            lineHeight: "1.6",
            marginBottom: theme.spacing.xl,
            textAlign: "center",
          }}
        >
          {message}
        </p>

        {/* Trade Preview */}
        {orderDetails && (
          <div
            style={{
              background: theme.background.glass,
              border: `1px solid ${theme.colors.border}`,
              borderRadius: theme.borderRadius.md,
              padding: theme.spacing.lg,
              marginBottom: theme.spacing.lg,
            }}
          >
            <h3
              style={{
                color: theme.colors.text,
                fontSize: "18px",
                fontWeight: "600",
                marginBottom: theme.spacing.md,
                textAlign: "center",
              }}
            >
              📊 Trade Preview
            </h3>
            
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: theme.spacing.sm }}>
              <div>
                <span style={{ color: theme.colors.textMuted, fontSize: "14px" }}>Symbol:</span>
                <div style={{ color: theme.colors.text, fontWeight: "600" }}>{orderDetails.symbol}</div>
              </div>
              <div>
                <span style={{ color: theme.colors.textMuted, fontSize: "14px" }}>Side:</span>
                <div style={{ 
                  color: orderDetails.side === "buy" ? theme.colors.success : theme.colors.danger, 
                  fontWeight: "600" 
                }}>
                  {orderDetails.side.toUpperCase()}
                </div>
              </div>
              <div>
                <span style={{ color: theme.colors.textMuted, fontSize: "14px" }}>Quantity:</span>
                <div style={{ color: theme.colors.text, fontWeight: "600" }}>{orderDetails.qty}</div>
              </div>
              <div>
                <span style={{ color: theme.colors.textMuted, fontSize: "14px" }}>Type:</span>
                <div style={{ color: theme.colors.text, fontWeight: "600" }}>{orderDetails.type.toUpperCase()}</div>
              </div>
              {orderDetails.limitPrice && (
                <div style={{ gridColumn: "1 / -1" }}>
                  <span style={{ color: theme.colors.textMuted, fontSize: "14px" }}>Limit Price:</span>
                  <div style={{ color: theme.colors.text, fontWeight: "600" }}>${orderDetails.limitPrice}</div>
                </div>
              )}
              {orderDetails.asset_class === "option" && (
                <>
                  <div>
                    <span style={{ color: theme.colors.textMuted, fontSize: "14px" }}>Option Type:</span>
                    <div style={{ color: theme.colors.text, fontWeight: "600" }}>
                      {orderDetails.option_type?.toUpperCase()}
                    </div>
                  </div>
                  <div>
                    <span style={{ color: theme.colors.textMuted, fontSize: "14px" }}>Strike:</span>
                    <div style={{ color: theme.colors.text, fontWeight: "600" }}>
                      ${orderDetails.strike_price}
                    </div>
                  </div>
                </>
              )}
            </div>

            {/* Risk Warning */}
            {riskWarning && (
              <div
                style={{
                  background: "rgba(239, 68, 68, 0.1)",
                  border: "1px solid rgba(239, 68, 68, 0.3)",
                  borderRadius: theme.borderRadius.md,
                  padding: theme.spacing.md,
                  marginTop: theme.spacing.md,
                }}
              >
                <div style={{ 
                  color: theme.colors.danger, 
                  fontWeight: "600", 
                  marginBottom: theme.spacing.xs,
                  display: "flex",
                  alignItems: "center",
                  gap: theme.spacing.xs,
                }}>
                  ⚠️ Risk Warning
                </div>
                <div style={{ color: theme.colors.textMuted, fontSize: "14px", lineHeight: "1.5" }}>
                  This trade involves real money. Make sure you understand the risks and have done your research.
                </div>
              </div>
            )}
          </div>
        )}

        <div
          style={{
            display: "flex",
            gap: theme.spacing.md,
            justifyContent: "center",
          }}
        >
          <button
            onClick={onCancel}
            style={{
              padding: `${theme.spacing.md} ${theme.spacing.lg}`,
              background: theme.background.card,
              border: `1px solid ${theme.colors.border}`,
              borderRadius: theme.borderRadius.md,
              color: theme.colors.textMuted,
              fontSize: "16px",
              fontWeight: "600",
              cursor: "pointer",
              transition: theme.transitions.normal,
              minWidth: "120px",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = theme.background.cardHover;
              e.currentTarget.style.borderColor = theme.colors.borderHover;
              e.currentTarget.style.color = theme.colors.text;
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = theme.background.card;
              e.currentTarget.style.borderColor = theme.colors.border;
              e.currentTarget.style.color = theme.colors.textMuted;
            }}
          >
            {cancelText}
          </button>

          <button
            onClick={onConfirm}
            style={{
              padding: `${theme.spacing.md} ${theme.spacing.lg}`,
              background: variant.background,
              border: "none",
              borderRadius: theme.borderRadius.md,
              color: "white",
              fontSize: "16px",
              fontWeight: "700",
              cursor: "pointer",
              transition: theme.transitions.normal,
              boxShadow: variant.glow,
              minWidth: "120px",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-2px)";
              e.currentTarget.style.boxShadow = `0 8px 20px rgba(0, 0, 0, 0.3), ${variant.glow}`;
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "translateY(0)";
              e.currentTarget.style.boxShadow = variant.glow;
            }}
          >
            {confirmText}
          </button>
        </div>
      </div>

      <style jsx>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }

        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
}
