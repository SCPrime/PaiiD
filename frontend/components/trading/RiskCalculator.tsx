import { useState } from "react";

interface OptionsProposal {
  symbol: string;
  option_symbol: string;
  contract_type: string;
  strike: number;
  expiration: string;
  premium: number;
  quantity: number;
  underlying_price: number;
  greeks: {
    delta: number;
    gamma: number;
    theta: number;
    vega: number;
  };
  max_risk: number;
  max_profit: number;
  breakeven: number;
  probability_of_profit: number;
  risk_reward_ratio: number;
  margin_requirement: number;
}

interface RiskCalculatorProps {
  onCreateProposal: (proposal: OptionsProposal) => void;
  onExecuteProposal: (proposal: OptionsProposal, limitPrice?: number) => void;
}

export default function RiskCalculator({
  onCreateProposal,
  onExecuteProposal,
}: RiskCalculatorProps) {
  const [symbol, setSymbol] = useState("SPY");
  const [optionSymbol, setOptionSymbol] = useState("");
  const [quantity, setQuantity] = useState(1);
  const [proposal, setProposal] = useState<OptionsProposal | null>(null);
  const [limitPrice, setLimitPrice] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCreateProposal = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/proxy/api/proposals/create", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${process.env.NEXT_PUBLIC_API_TOKEN}`,
        },
        body: JSON.stringify({
          symbol,
          option_symbol: optionSymbol,
          quantity,
          order_type: "limit",
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to create proposal");
      }

      const data = await response.json();
      const newProposal = data.proposal;
      setProposal(newProposal);
      setLimitPrice(newProposal.premium.toFixed(2));
      onCreateProposal(newProposal);
    } catch (err: unknown) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleExecuteProposal = async () => {
    if (!proposal) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/proxy/api/proposals/execute", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${process.env.NEXT_PUBLIC_API_TOKEN}`,
        },
        body: JSON.stringify({
          proposal,
          limit_price: limitPrice ? parseFloat(limitPrice) : null,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to execute proposal");
      }

      const data = await response.json();
      onExecuteProposal(proposal, limitPrice ? parseFloat(limitPrice) : undefined);
      alert(`Order submitted successfully! Order ID: ${data.order_id}`);

      // Reset form
      setProposal(null);
      setOptionSymbol("");
      setLimitPrice("");
    } catch (err: unknown) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        padding: "20px",
        background: "rgba(15, 23, 42, 0.6)",
        backdropFilter: "blur(10px)",
        borderRadius: "12px",
        border: "1px solid rgba(100, 116, 139, 0.3)",
      }}
    >
      <h2 style={{ color: "#e2e8f0", marginBottom: "20px" }}>Options Risk Calculator</h2>

      {/* Input Form */}
      <div style={{ marginBottom: "20px" }}>
        <div style={{ marginBottom: "12px" }}>
          <label style={{ display: "block", color: "#cbd5e1", marginBottom: "4px" }}>
            Underlying Symbol
          </label>
          <input
            type="text"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
            style={{
              width: "100%",
              padding: "8px 12px",
              background: "rgba(30, 41, 59, 0.8)",
              border: "1px solid rgba(100, 116, 139, 0.3)",
              borderRadius: "6px",
              color: "#e2e8f0",
              fontSize: "14px",
            }}
            placeholder="SPY"
          />
        </div>

        <div style={{ marginBottom: "12px" }}>
          <label style={{ display: "block", color: "#cbd5e1", marginBottom: "4px" }}>
            Option Symbol (OCC Format)
          </label>
          <input
            type="text"
            value={optionSymbol}
            onChange={(e) => setOptionSymbol(e.target.value.toUpperCase())}
            style={{
              width: "100%",
              padding: "8px 12px",
              background: "rgba(30, 41, 59, 0.8)",
              border: "1px solid rgba(100, 116, 139, 0.3)",
              borderRadius: "6px",
              color: "#e2e8f0",
              fontSize: "14px",
            }}
            placeholder="SPY250117C00590000"
          />
          <small style={{ color: "#94a3b8", fontSize: "12px" }}>
            Example: SPY250117C00590000 (SPY Jan 17 2025 $590 Call)
          </small>
        </div>

        <div style={{ marginBottom: "12px" }}>
          <label style={{ display: "block", color: "#cbd5e1", marginBottom: "4px" }}>
            Quantity
          </label>
          <input
            type="number"
            value={quantity}
            onChange={(e) => setQuantity(parseInt(e.target.value) || 1)}
            min="1"
            style={{
              width: "100%",
              padding: "8px 12px",
              background: "rgba(30, 41, 59, 0.8)",
              border: "1px solid rgba(100, 116, 139, 0.3)",
              borderRadius: "6px",
              color: "#e2e8f0",
              fontSize: "14px",
            }}
          />
        </div>

        <button
          onClick={handleCreateProposal}
          disabled={loading || !optionSymbol}
          style={{
            width: "100%",
            padding: "10px",
            background: loading
              ? "rgba(100, 116, 139, 0.5)"
              : "linear-gradient(135deg, #1a7560 0%, #0d5a4a 100%)",
            color: "#fff",
            border: "none",
            borderRadius: "6px",
            fontSize: "14px",
            fontWeight: "600",
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          {loading ? "Analyzing..." : "Create Proposal"}
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div
          style={{
            padding: "12px",
            background: "rgba(239, 68, 68, 0.1)",
            border: "1px solid rgba(239, 68, 68, 0.3)",
            borderRadius: "6px",
            color: "#fca5a5",
            marginBottom: "20px",
          }}
        >
          {error}
        </div>
      )}

      {/* Proposal Display */}
      {proposal && (
        <div
          style={{
            padding: "20px",
            background: "rgba(30, 41, 59, 0.8)",
            border: "1px solid rgba(100, 116, 139, 0.3)",
            borderRadius: "8px",
            marginBottom: "20px",
          }}
        >
          <h3 style={{ color: "#e2e8f0", marginBottom: "16px" }}>Trade Proposal</h3>

          {/* Contract Details */}
          <div style={{ marginBottom: "16px" }}>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
              <div>
                <span style={{ color: "#94a3b8", fontSize: "12px" }}>Type</span>
                <div style={{ color: "#e2e8f0", fontWeight: "600", textTransform: "uppercase" }}>
                  {proposal.contract_type}
                </div>
              </div>
              <div>
                <span style={{ color: "#94a3b8", fontSize: "12px" }}>Strike</span>
                <div style={{ color: "#e2e8f0", fontWeight: "600" }}>
                  ${proposal.strike.toFixed(2)}
                </div>
              </div>
              <div>
                <span style={{ color: "#94a3b8", fontSize: "12px" }}>Premium</span>
                <div style={{ color: "#10b981", fontWeight: "600" }}>
                  ${proposal.premium.toFixed(2)}
                </div>
              </div>
              <div>
                <span style={{ color: "#94a3b8", fontSize: "12px" }}>Expiration</span>
                <div style={{ color: "#e2e8f0", fontWeight: "600" }}>{proposal.expiration}</div>
              </div>
            </div>
          </div>

          {/* Greeks */}
          <div style={{ marginBottom: "16px" }}>
            <h4 style={{ color: "#cbd5e1", fontSize: "14px", marginBottom: "8px" }}>Greeks</h4>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr 1fr", gap: "8px" }}>
              <div>
                <span style={{ color: "#94a3b8", fontSize: "11px" }}>Delta</span>
                <div style={{ color: "#e2e8f0", fontSize: "13px", fontWeight: "600" }}>
                  {proposal.greeks.delta.toFixed(3)}
                </div>
              </div>
              <div>
                <span style={{ color: "#94a3b8", fontSize: "11px" }}>Gamma</span>
                <div style={{ color: "#e2e8f0", fontSize: "13px", fontWeight: "600" }}>
                  {proposal.greeks.gamma.toFixed(3)}
                </div>
              </div>
              <div>
                <span style={{ color: "#94a3b8", fontSize: "11px" }}>Theta</span>
                <div style={{ color: "#e2e8f0", fontSize: "13px", fontWeight: "600" }}>
                  {proposal.greeks.theta.toFixed(3)}
                </div>
              </div>
              <div>
                <span style={{ color: "#94a3b8", fontSize: "11px" }}>Vega</span>
                <div style={{ color: "#e2e8f0", fontSize: "13px", fontWeight: "600" }}>
                  {proposal.greeks.vega.toFixed(3)}
                </div>
              </div>
            </div>
          </div>

          {/* Risk Metrics */}
          <div style={{ marginBottom: "16px" }}>
            <h4 style={{ color: "#cbd5e1", fontSize: "14px", marginBottom: "8px" }}>
              Risk Analysis
            </h4>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
              <div>
                <span style={{ color: "#94a3b8", fontSize: "12px" }}>Max Risk</span>
                <div style={{ color: "#ef4444", fontWeight: "600" }}>
                  ${proposal.max_risk.toFixed(2)}
                </div>
              </div>
              <div>
                <span style={{ color: "#94a3b8", fontSize: "12px" }}>Max Profit</span>
                <div style={{ color: "#10b981", fontWeight: "600" }}>
                  {proposal.max_profit === 999999
                    ? "Unlimited"
                    : `$${proposal.max_profit.toFixed(2)}`}
                </div>
              </div>
              <div>
                <span style={{ color: "#94a3b8", fontSize: "12px" }}>Breakeven</span>
                <div style={{ color: "#e2e8f0", fontWeight: "600" }}>
                  ${proposal.breakeven.toFixed(2)}
                </div>
              </div>
              <div>
                <span style={{ color: "#94a3b8", fontSize: "12px" }}>Probability</span>
                <div style={{ color: "#e2e8f0", fontWeight: "600" }}>
                  {proposal.probability_of_profit.toFixed(1)}%
                </div>
              </div>
            </div>
          </div>

          {/* Execution Section */}
          <div>
            <label
              style={{ display: "block", color: "#cbd5e1", marginBottom: "4px", fontSize: "14px" }}
            >
              Limit Price
            </label>
            <input
              type="number"
              value={limitPrice}
              onChange={(e) => setLimitPrice(e.target.value)}
              step="0.01"
              style={{
                width: "100%",
                padding: "8px 12px",
                background: "rgba(15, 23, 42, 0.8)",
                border: "1px solid rgba(100, 116, 139, 0.3)",
                borderRadius: "6px",
                color: "#e2e8f0",
                fontSize: "14px",
                marginBottom: "12px",
              }}
            />
            <button
              onClick={handleExecuteProposal}
              disabled={loading}
              style={{
                width: "100%",
                padding: "12px",
                background: loading
                  ? "rgba(100, 116, 139, 0.5)"
                  : "linear-gradient(135deg, #10b981 0%, #059669 100%)",
                color: "#fff",
                border: "none",
                borderRadius: "6px",
                fontSize: "14px",
                fontWeight: "600",
                cursor: loading ? "not-allowed" : "pointer",
              }}
            >
              {loading ? "Executing..." : "Execute Trade (Paper Trading)"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
