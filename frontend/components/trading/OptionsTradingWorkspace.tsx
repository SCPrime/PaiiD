import { FormEvent, useMemo, useState } from "react";

import OptionsChain, { OptionContract } from "./OptionsChain";
import { showError, showSuccess } from "../../lib/toast";
import { paidTheme } from "../../styles/paiid-theme";

type OrderSide = "buy_to_open" | "buy_to_close" | "sell_to_open" | "sell_to_close";
type OrderType = "market" | "limit" | "stop" | "stop_limit";

type Duration = "day" | "gtc" | "pre" | "post" | "gtc_pre" | "gtc_post";

const sideOptions: { value: OrderSide; label: string }[] = [
  { value: "buy_to_open", label: "Buy to Open" },
  { value: "sell_to_open", label: "Sell to Open" },
  { value: "buy_to_close", label: "Buy to Close" },
  { value: "sell_to_close", label: "Sell to Close" },
];

const orderTypes: { value: OrderType; label: string }[] = [
  { value: "market", label: "Market" },
  { value: "limit", label: "Limit" },
  { value: "stop", label: "Stop" },
  { value: "stop_limit", label: "Stop Limit" },
];

const durations: { value: Duration; label: string }[] = [
  { value: "day", label: "Day" },
  { value: "gtc", label: "GTC" },
  { value: "pre", label: "Pre-Market" },
  { value: "post", label: "After Hours" },
  { value: "gtc_pre", label: "GTC + Pre" },
  { value: "gtc_post", label: "GTC + Post" },
];

export default function OptionsTradingWorkspace() {
  const theme = paidTheme;
  const [symbol, setSymbol] = useState("AAPL");
  const [minVolume, setMinVolume] = useState<number>(50);
  const [minOpenInterest, setMinOpenInterest] = useState<number>(50);
  const [selectedContract, setSelectedContract] = useState<OptionContract | null>(null);
  const [side, setSide] = useState<OrderSide>("buy_to_open");
  const [orderType, setOrderType] = useState<OrderType>("market");
  const [duration, setDuration] = useState<Duration>("day");
  const [quantity, setQuantity] = useState<number>(1);
  const [price, setPrice] = useState<string>("");
  const [stop, setStop] = useState<string>("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canSubmit = useMemo(() => {
    if (!selectedContract) return false;
    if (!quantity || quantity <= 0) return false;
    if ((orderType === "limit" || orderType === "stop_limit") && !price) return false;
    if ((orderType === "stop" || orderType === "stop_limit") && !stop) return false;
    return true;
  }, [selectedContract, quantity, orderType, price, stop]);

  const resetOrderFields = () => {
    setQuantity(1);
    setPrice("");
    setStop("");
    setSide("buy_to_open");
    setOrderType("market");
    setDuration("day");
  };

  const placeOrder = async (preview = false) => {
    if (!selectedContract) {
      setError("Select an option contract first.");
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      const token = process.env.NEXT_PUBLIC_API_TOKEN;
      const response = await fetch("/api/proxy/options/orders", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          symbol,
          option_symbol: selectedContract.symbol,
          side,
          quantity,
          order_type: orderType,
          duration,
          price: price ? Number(price) : undefined,
          stop: stop ? Number(stop) : undefined,
          preview,
        }),
      });

      if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        throw new Error(payload.detail || response.statusText);
      }

      const result = await response.json();

      if (preview) {
        showSuccess("Preview generated successfully");
      } else {
        showSuccess(`Order submitted (ID: ${result.order_id || "pending"})`);
        resetOrderFields();
      }
      setError(null);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to place order";
      setError(message);
      showError(message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    await placeOrder(false);
  };

  const handlePreview = async () => {
    await placeOrder(true);
  };

  const selectedMid = useMemo(() => {
    if (!selectedContract) return null;
    const { bid, ask } = selectedContract;
    if (bid !== undefined && ask !== undefined) {
      return ((bid + ask) / 2).toFixed(2);
    }
    return selectedContract.mid_price?.toFixed(2) ?? null;
  }, [selectedContract]);

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "minmax(0, 420px) 1fr",
        gap: theme.spacing.lg,
        alignItems: "flex-start",
        width: "100%",
      }}
    >
      <div
        style={{
          background: theme.colors.glass,
          border: `1px solid ${theme.colors.glassBorder}`,
          borderRadius: theme.borderRadius.lg,
          padding: theme.spacing.lg,
          display: "flex",
          flexDirection: "column",
          gap: theme.spacing.md,
        }}
      >
        <div>
          <h2
            style={{
              margin: 0,
              color: theme.colors.text,
              fontSize: "22px",
              letterSpacing: "0.04em",
            }}
          >
            Options Trade Ticket
          </h2>
          <p style={{ margin: 0, color: theme.colors.textMuted, fontSize: "13px" }}>
            Configure paper-trade orders routed through Tradier with real-time validation.
          </p>
        </div>

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: theme.spacing.md }}>
          <div>
            <label style={{ display: "block", color: theme.colors.textMuted, marginBottom: theme.spacing.xs }}>Symbol</label>
            <input
              value={symbol}
              onChange={(e) => setSymbol(e.target.value.toUpperCase())}
              placeholder="AAPL"
              style={{
                width: "100%",
                background: theme.colors.glass,
                border: `1px solid ${theme.colors.glassBorder}`,
                borderRadius: theme.borderRadius.md,
                padding: `${theme.spacing.xs} ${theme.spacing.md}`,
                color: theme.colors.text,
                fontSize: "14px",
                textTransform: "uppercase",
              }}
            />
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(2, minmax(0, 1fr))", gap: theme.spacing.md }}>
            <div>
              <label style={{ display: "block", color: theme.colors.textMuted, marginBottom: theme.spacing.xs }}>Side</label>
              <select
                value={side}
                onChange={(e) => setSide(e.target.value as OrderSide)}
                style={{
                  width: "100%",
                  background: theme.colors.glass,
                  border: `1px solid ${theme.colors.glassBorder}`,
                  borderRadius: theme.borderRadius.md,
                  padding: `${theme.spacing.xs} ${theme.spacing.sm}`,
                  color: theme.colors.text,
                  fontSize: "14px",
                }}
              >
                {sideOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label style={{ display: "block", color: theme.colors.textMuted, marginBottom: theme.spacing.xs }}>Quantity</label>
              <input
                type="number"
                min={1}
                value={quantity}
                onChange={(e) => setQuantity(Number(e.target.value))}
                style={{
                  width: "100%",
                  background: theme.colors.glass,
                  border: `1px solid ${theme.colors.glassBorder}`,
                  borderRadius: theme.borderRadius.md,
                  padding: `${theme.spacing.xs} ${theme.spacing.sm}`,
                  color: theme.colors.text,
                  fontSize: "14px",
                }}
              />
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(2, minmax(0, 1fr))", gap: theme.spacing.md }}>
            <div>
              <label style={{ display: "block", color: theme.colors.textMuted, marginBottom: theme.spacing.xs }}>Order Type</label>
              <select
                value={orderType}
                onChange={(e) => setOrderType(e.target.value as OrderType)}
                style={{
                  width: "100%",
                  background: theme.colors.glass,
                  border: `1px solid ${theme.colors.glassBorder}`,
                  borderRadius: theme.borderRadius.md,
                  padding: `${theme.spacing.xs} ${theme.spacing.sm}`,
                  color: theme.colors.text,
                  fontSize: "14px",
                }}
              >
                {orderTypes.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label style={{ display: "block", color: theme.colors.textMuted, marginBottom: theme.spacing.xs }}>Duration</label>
              <select
                value={duration}
                onChange={(e) => setDuration(e.target.value as Duration)}
                style={{
                  width: "100%",
                  background: theme.colors.glass,
                  border: `1px solid ${theme.colors.glassBorder}`,
                  borderRadius: theme.borderRadius.md,
                  padding: `${theme.spacing.xs} ${theme.spacing.sm}`,
                  color: theme.colors.text,
                  fontSize: "14px",
                }}
              >
                {durations.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {(orderType === "limit" || orderType === "stop_limit") && (
            <div>
              <label style={{ display: "block", color: theme.colors.textMuted, marginBottom: theme.spacing.xs }}>Limit Price</label>
              <input
                type="number"
                min={0}
                step="0.01"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                style={{
                  width: "100%",
                  background: theme.colors.glass,
                  border: `1px solid ${theme.colors.glassBorder}`,
                  borderRadius: theme.borderRadius.md,
                  padding: `${theme.spacing.xs} ${theme.spacing.sm}`,
                  color: theme.colors.text,
                  fontSize: "14px",
                }}
              />
            </div>
          )}

          {(orderType === "stop" || orderType === "stop_limit") && (
            <div>
              <label style={{ display: "block", color: theme.colors.textMuted, marginBottom: theme.spacing.xs }}>Stop Price</label>
              <input
                type="number"
                min={0}
                step="0.01"
                value={stop}
                onChange={(e) => setStop(e.target.value)}
                style={{
                  width: "100%",
                  background: theme.colors.glass,
                  border: `1px solid ${theme.colors.glassBorder}`,
                  borderRadius: theme.borderRadius.md,
                  padding: `${theme.spacing.xs} ${theme.spacing.sm}`,
                  color: theme.colors.text,
                  fontSize: "14px",
                }}
              />
            </div>
          )}

          {selectedContract ? (
            <div
              style={{
                background: `${theme.colors.accent}10`,
                border: `1px solid ${theme.colors.accent}40`,
                borderRadius: theme.borderRadius.md,
                padding: theme.spacing.md,
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
                <strong style={{ color: theme.colors.accent }}>{selectedContract.symbol}</strong>
                <span style={{ color: theme.colors.textMuted, fontSize: "12px" }}>
                  IV {selectedContract.implied_volatility ? `${(selectedContract.implied_volatility * 100).toFixed(2)}%` : "—"}
                </span>
              </div>
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
                  gap: theme.spacing.xs,
                  marginTop: theme.spacing.sm,
                  color: theme.colors.text,
                  fontSize: "12px",
                }}
              >
                <span>Bid: {selectedContract.bid?.toFixed(2) ?? "—"}</span>
                <span>Ask: {selectedContract.ask?.toFixed(2) ?? "—"}</span>
                <span>Mid: {selectedMid ?? "—"}</span>
                <span>OI: {selectedContract.open_interest?.toLocaleString() ?? "—"}</span>
                <span>Delta: {selectedContract.delta?.toFixed(3) ?? "—"}</span>
                <span>Theta: {selectedContract.theta?.toFixed(3) ?? "—"}</span>
              </div>
            </div>
          ) : (
            <div
              style={{
                background: `${theme.colors.textMuted}10`,
                border: `1px dashed ${theme.colors.glassBorder}`,
                borderRadius: theme.borderRadius.md,
                padding: theme.spacing.md,
                color: theme.colors.textMuted,
                fontSize: "12px",
              }}
            >
              Select an option contract from the chain to populate ticket details.
            </div>
          )}

          {error && (
            <div
              style={{
                background: `${theme.colors.error}15`,
                border: `1px solid ${theme.colors.error}40`,
                borderRadius: theme.borderRadius.md,
                padding: theme.spacing.sm,
                color: theme.colors.error,
                fontSize: "12px",
              }}
            >
              {error}
            </div>
          )}

          <div style={{ display: "flex", gap: theme.spacing.md }}>
            <button
              type="submit"
              disabled={!canSubmit || submitting}
              style={{
                flex: 1,
                background: canSubmit ? theme.colors.accent : theme.colors.glass,
                color: canSubmit ? theme.colors.background : theme.colors.textMuted,
                border: `1px solid ${theme.colors.accent}`,
                borderRadius: theme.borderRadius.md,
                padding: `${theme.spacing.xs} ${theme.spacing.md}`,
                fontWeight: 600,
                cursor: canSubmit && !submitting ? "pointer" : "not-allowed",
                transition: `all ${theme.animation.duration.normal}`,
              }}
            >
              {submitting ? "Submitting…" : "Place Order"}
            </button>
            <button
              type="button"
              onClick={handlePreview}
              disabled={!canSubmit || submitting}
              style={{
                flex: 1,
                background: theme.colors.glass,
                color: theme.colors.text,
                border: `1px solid ${theme.colors.glassBorder}`,
                borderRadius: theme.borderRadius.md,
                padding: `${theme.spacing.xs} ${theme.spacing.md}`,
                fontWeight: 600,
                cursor: canSubmit && !submitting ? "pointer" : "not-allowed",
              }}
            >
              Preview
            </button>
          </div>
        </form>

        <div
          style={{
            borderTop: `1px solid ${theme.colors.glassBorder}`,
            paddingTop: theme.spacing.md,
            display: "grid",
            gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
            gap: theme.spacing.md,
          }}
        >
          <div>
            <label style={{ display: "block", color: theme.colors.textMuted, marginBottom: theme.spacing.xs }}>
              Min Daily Volume
            </label>
            <input
              type="number"
              min={0}
              value={minVolume}
              onChange={(e) => setMinVolume(Number(e.target.value))}
              style={{
                width: "100%",
                background: theme.colors.glass,
                border: `1px solid ${theme.colors.glassBorder}`,
                borderRadius: theme.borderRadius.md,
                padding: `${theme.spacing.xs} ${theme.spacing.sm}`,
                color: theme.colors.text,
                fontSize: "14px",
              }}
            />
          </div>
          <div>
            <label style={{ display: "block", color: theme.colors.textMuted, marginBottom: theme.spacing.xs }}>
              Min Open Interest
            </label>
            <input
              type="number"
              min={0}
              value={minOpenInterest}
              onChange={(e) => setMinOpenInterest(Number(e.target.value))}
              style={{
                width: "100%",
                background: theme.colors.glass,
                border: `1px solid ${theme.colors.glassBorder}`,
                borderRadius: theme.borderRadius.md,
                padding: `${theme.spacing.xs} ${theme.spacing.sm}`,
                color: theme.colors.text,
                fontSize: "14px",
              }}
            />
          </div>
        </div>
      </div>

      <div style={{ width: "100%" }}>
        <OptionsChain
          symbol={symbol}
          variant="inline"
          minVolume={minVolume}
          minOpenInterest={minOpenInterest}
          selectedContract={selectedContract}
          onSelectContract={setSelectedContract}
        />
      </div>
    </div>
  );
}
