"use client";
import { useEffect, useMemo, useState } from "react";

import { theme } from "../../../styles/theme";
import { OrderPayload, OrderPreviewResponse } from "../types";

interface PreviewModalProps {
  open: boolean;
  orders: OrderPayload[];
  onClose: () => void;
}

const currency = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
});

function formatNumber(value: number | null | undefined): string {
  if (value === null || value === undefined) return "–";
  if (Number.isNaN(value)) return "–";
  return currency.format(value);
}

export function PreviewModal({ open, orders, onClose }: PreviewModalProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [preview, setPreview] = useState<OrderPreviewResponse | null>(null);

  const payload = useMemo(() => ({ orders }), [orders]);

  useEffect(() => {
    if (!open) {
      setPreview(null);
      setError(null);
      return;
    }

    if (!orders.length) {
      setPreview(null);
      setError("Add at least one order to preview risk and exposure.");
      return;
    }

    let cancelled = false;
    const controller = new AbortController();

    async function fetchPreview() {
      try {
        setLoading(true);
        setError(null);
        const response = await fetch("/api/proxy/api/orders/preview", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
          signal: controller.signal,
        });

        if (!response.ok) {
          const message = await response.text();
          throw new Error(message || "Failed to fetch order preview");
        }

        const data: OrderPreviewResponse = await response.json();
        if (!cancelled) {
          setPreview(data);
        }
      } catch (err) {
        if (cancelled) return;
        const message = err instanceof Error ? err.message : "Unexpected error";
        setError(message);
        setPreview(null);
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    fetchPreview();

    return () => {
      cancelled = true;
      controller.abort();
    };
  }, [open, orders, payload]);

  if (!open) return null;

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        backgroundColor: "rgba(0,0,0,0.65)",
        backdropFilter: theme.blur.medium,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 1200,
        padding: theme.spacing.lg,
      }}
      onClick={onClose}
    >
      <div
        style={{
          width: "100%",
          maxWidth: "720px",
          background: theme.background.glass,
          borderRadius: theme.borderRadius.lg,
          border: `1px solid ${theme.colors.border}`,
          boxShadow: `0 24px 60px rgba(0, 0, 0, 0.45), ${theme.glow.green}`,
          padding: theme.spacing.xl,
          color: theme.colors.text,
        }}
        onClick={(event) => event.stopPropagation()}
      >
        <header
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            marginBottom: theme.spacing.lg,
          }}
        >
          <div>
            <h2 style={{ margin: 0, fontSize: "24px", fontWeight: 700 }}>Order Preview</h2>
            <p style={{ margin: 0, color: theme.colors.textMuted, fontSize: "14px" }}>
              Review notional exposure, profit targets, and risk before submitting (Ctrl + Enter to open, Ctrl + Shift + Enter to submit).
            </p>
          </div>
          <button
            onClick={onClose}
            style={{
              background: "transparent",
              border: "none",
              color: theme.colors.textMuted,
              fontSize: "16px",
              cursor: "pointer",
            }}
          >
            Close
          </button>
        </header>

        {loading ? (
          <div
            style={{
              padding: theme.spacing.lg,
              textAlign: "center",
              color: theme.colors.textMuted,
            }}
          >
            Calculating exposure…
          </div>
        ) : error ? (
          <div
            style={{
              padding: theme.spacing.md,
              background: theme.background.card,
              border: `1px solid ${theme.colors.danger}`,
              borderRadius: theme.borderRadius.md,
              color: theme.colors.danger,
            }}
          >
            {error}
          </div>
        ) : preview ? (
          <div style={{ display: "flex", flexDirection: "column", gap: theme.spacing.lg }}>
            <section
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
                gap: theme.spacing.lg,
                background: theme.background.card,
                borderRadius: theme.borderRadius.md,
                padding: theme.spacing.lg,
                border: `1px solid ${theme.colors.border}`,
              }}
            >
              <div>
                <p style={{ margin: 0, color: theme.colors.textMuted, fontSize: "12px" }}>Total Notional</p>
                <strong style={{ fontSize: "20px" }}>{formatNumber(preview.total_notional)}</strong>
              </div>
              <div>
                <p style={{ margin: 0, color: theme.colors.textMuted, fontSize: "12px" }}>Max Potential Profit</p>
                <strong style={{ fontSize: "20px", color: theme.colors.success }}>
                  {formatNumber(preview.total_max_profit)}
                </strong>
              </div>
              <div>
                <p style={{ margin: 0, color: theme.colors.textMuted, fontSize: "12px" }}>Max Potential Loss</p>
                <strong style={{ fontSize: "20px", color: theme.colors.danger }}>
                  {formatNumber(preview.total_max_loss)}
                </strong>
              </div>
            </section>

            <section style={{ maxHeight: "320px", overflowY: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr style={{ color: theme.colors.textMuted, fontSize: "12px", textTransform: "uppercase" }}>
                    <th style={{ textAlign: "left", paddingBottom: theme.spacing.sm }}>Symbol</th>
                    <th style={{ textAlign: "left", paddingBottom: theme.spacing.sm }}>Class</th>
                    <th style={{ textAlign: "right", paddingBottom: theme.spacing.sm }}>Notional</th>
                    <th style={{ textAlign: "right", paddingBottom: theme.spacing.sm }}>Target</th>
                    <th style={{ textAlign: "right", paddingBottom: theme.spacing.sm }}>Stop</th>
                    <th style={{ textAlign: "right", paddingBottom: theme.spacing.sm }}>Max P/L</th>
                    <th style={{ textAlign: "right", paddingBottom: theme.spacing.sm }}>R:R</th>
                  </tr>
                </thead>
                <tbody>
                  {preview.orders.map((order) => (
                    <tr key={`${order.symbol}-${order.order_class}`} style={{ borderTop: `1px solid ${theme.colors.border}` }}>
                      <td style={{ padding: `${theme.spacing.sm} 0` }}>
                        <strong>{order.symbol}</strong>
                        <span style={{ marginLeft: theme.spacing.xs, color: theme.colors.textMuted }}>
                          {order.side.toUpperCase()} · {order.order_type.toUpperCase()}
                        </span>
                      </td>
                      <td style={{ padding: `${theme.spacing.sm} 0`, color: theme.colors.textMuted }}>
                        {order.order_class.toUpperCase()}
                      </td>
                      <td style={{ padding: `${theme.spacing.sm} 0`, textAlign: "right" }}>
                        {formatNumber(order.notional)}
                      </td>
                      <td style={{ padding: `${theme.spacing.sm} 0`, textAlign: "right" }}>
                        {formatNumber(order.take_profit_price)}
                      </td>
                      <td style={{ padding: `${theme.spacing.sm} 0`, textAlign: "right" }}>
                        {formatNumber(order.stop_loss_price)}
                      </td>
                      <td style={{ padding: `${theme.spacing.sm} 0`, textAlign: "right" }}>
                        <span style={{ color: theme.colors.success }}>{formatNumber(order.max_profit)}</span>
                        {" / "}
                        <span style={{ color: theme.colors.danger }}>{formatNumber(order.max_loss)}</span>
                      </td>
                      <td style={{ padding: `${theme.spacing.sm} 0`, textAlign: "right" }}>
                        {order.risk_reward_ratio ? `${order.risk_reward_ratio.toFixed(2)}x` : "–"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </section>
          </div>
        ) : (
          <div style={{ color: theme.colors.textMuted, textAlign: "center" }}>No preview available.</div>
        )}
      </div>
    </div>
  );
}
