import { useEffect, useState } from "react";
import { paidTheme } from "../../styles/paiid-theme";

/**
 * Options Chain Component
 *
 * Displays options chain with calls/puts, strikes, Greeks, and execution interface.
 * Phase 1 Implementation:
 * - Fetch options chain from backend with Greeks
 * - Display calls and puts side-by-side
 * - Show Greeks with color coding
 * - Filter by call/put/both
 * - Expiration selector
 */

export interface OptionContract {
  symbol: string;
  underlying_symbol: string;
  option_type: "call" | "put";
  strike_price: number;
  expiration_date: string;

  // Market data
  bid?: number;
  ask?: number;
  last_price?: number;
  mid_price?: number;
  volume?: number;
  open_interest?: number;

  // Greeks
  delta?: number;
  gamma?: number;
  theta?: number;
  vega?: number;
  rho?: number;

  // Implied volatility
  implied_volatility?: number;
  multiplier?: number;
  updated_at?: string;
}

interface OptionsChainData {
  symbol: string;
  expiration_date: string;
  underlying_price?: number;
  calls: OptionContract[];
  puts: OptionContract[];
  total_contracts: number;
  greeks_exposure: {
    calls: OptionsGreeksExposure;
    puts: OptionsGreeksExposure;
    net: OptionsGreeksExposure;
  };
  as_of?: string;
}

interface ExpirationDate {
  date: string;
  days_to_expiry: number;
}

interface OptionsGreeksExposure {
  delta: number;
  gamma: number;
  theta: number;
  vega: number;
  rho: number;
}

type OptionsChainVariant = "modal" | "inline";

interface OptionsChainProps {
  symbol: string;
  onClose?: () => void;
  variant?: OptionsChainVariant;
  onSelectContract?: (contract: OptionContract) => void;
  selectedContract?: OptionContract | null;
  minVolume?: number;
  minOpenInterest?: number;
}

type FilterType = "all" | "calls" | "puts";

export default function OptionsChain({
  symbol,
  onClose,
  variant = "modal",
  onSelectContract,
  selectedContract,
  minVolume,
  minOpenInterest,
}: OptionsChainProps) {
  const [chainData, setChainData] = useState<OptionsChainData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedExpiration, setSelectedExpiration] = useState<string>("");
  const [expirations, setExpirations] = useState<ExpirationDate[]>([]);
  const [filter, setFilter] = useState<FilterType>("all");
  const [localSelection, setLocalSelection] = useState<string | null>(null);

  // Fetch available expirations
  useEffect(() => {
    if (symbol) {
      fetchExpirations();
    }
  }, [symbol]);

  // Fetch options chain when expiration selected
  useEffect(() => {
    if (symbol && selectedExpiration) {
      fetchOptionsChain();
    }
  }, [symbol, selectedExpiration, minVolume, minOpenInterest]);

  const fetchExpirations = async () => {
    try {
      const token = process.env.NEXT_PUBLIC_API_TOKEN;

      const response = await fetch(`/api/proxy/options/expirations/${symbol}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch expirations: ${response.statusText}`);
      }

      const data: ExpirationDate[] = await response.json();
      setExpirations(data);

      // Auto-select first expiration
      if (data.length > 0) {
        setSelectedExpiration(data[0].date);
      }
    } catch (err) {
      console.error("Error fetching expirations:", err);
      setError(err instanceof Error ? err.message : "Failed to fetch expirations");
    }
  };

  const fetchOptionsChain = async () => {
    setLoading(true);
    setError(null);

    try {
      const token = process.env.NEXT_PUBLIC_API_TOKEN;

      const params = new URLSearchParams({ expiration: selectedExpiration });
      if (minVolume !== undefined) {
        params.append("min_volume", String(minVolume));
      }
      if (minOpenInterest !== undefined) {
        params.append("min_open_interest", String(minOpenInterest));
      }

      const response = await fetch(`/api/proxy/options/chains/${symbol}?${params.toString()}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch options chain: ${response.statusText}`);
      }

      const data: OptionsChainData = await response.json();
      setChainData(data);
      if (data && selectedContract) {
        const match = [...data.calls, ...data.puts].find((c) => c.symbol === selectedContract.symbol);
        if (!match) {
          setLocalSelection(null);
        }
      }
    } catch (err) {
      console.error("Error fetching options chain:", err);
      setError(err instanceof Error ? err.message : "Failed to fetch options chain");
    } finally {
      setLoading(false);
    }
  };

  // TODO: Implement trade execution
  // const handleExecuteTrade = (contract: OptionContract, side: "buy" | "sell") => {
  //   console.log("Execute", side, "for", contract.symbol);
  // };

  // Format Greeks with color coding
  const formatGreek = (value: number | undefined, type: string) => {
    if (value === undefined || value === null) return "—";

    let color = "#94a3b8";
    if (type === "delta") {
      color = value > 0 ? "#10b981" : "#ef4444";
    } else if (type === "theta") {
      color = value < 0 ? "#ef4444" : "#10b981";
    }

    return <span style={{ color }}>{value.toFixed(4)}</span>;
  };

  // Group calls and puts by strike
  const getStrikeMap = () => {
    if (!chainData) return new Map();

    const strikeMap = new Map<number, { call?: OptionContract; put?: OptionContract }>();

    chainData.calls.forEach((call) => {
      const existing = strikeMap.get(call.strike_price) || {};
      strikeMap.set(call.strike_price, { ...existing, call });
    });

    chainData.puts.forEach((put) => {
      const existing = strikeMap.get(put.strike_price) || {};
      strikeMap.set(put.strike_price, { ...existing, put });
    });

    return new Map(Array.from(strikeMap.entries()).sort((a, b) => a[0] - b[0]));
  };

  const strikeMap = getStrikeMap();

  // Filter strikes based on filter type
  const filteredStrikes = Array.from(strikeMap.entries()).filter(([_, contracts]) => {
    if (filter === "calls") return contracts.call !== undefined;
    if (filter === "puts") return contracts.put !== undefined;
    return true;
  });

  const theme = paidTheme;
  const isModal = variant === "modal";
  const activeSelection = selectedContract?.symbol ?? localSelection;

  const handleContractSelect = (contract?: OptionContract) => {
    if (!contract) return;
    setLocalSelection(contract.symbol);
    onSelectContract?.(contract);
  };

  const formatExposure = (value: number) => {
    if (!Number.isFinite(value)) {
      return "—";
    }
    const abs = Math.abs(value);
    if (abs >= 1_000_000) {
      return `${(value / 1_000_000).toFixed(2)}M`;
    }
    if (abs >= 1_000) {
      return `${(value / 1_000).toFixed(2)}K`;
    }
    return value.toFixed(2);
  };


    const content = (
    <div
      style={{
        maxWidth: isModal ? "1600px" : "100%",
        margin: isModal ? "0 auto" : 0,
        background: theme.colors.glass,
        borderRadius: theme.borderRadius.lg,
        padding: theme.spacing.lg,
        border: `1px solid ${theme.colors.glassBorder}`,
        boxShadow: theme.effects.glowSubtle(theme.colors.accent),
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: theme.spacing.md,
          marginBottom: theme.spacing.md,
        }}
      >
        <div>
          <h2
            style={{
              margin: 0,
              color: theme.colors.text,
              fontSize: "24px",
              letterSpacing: "0.02em",
            }}
          >
            Options Chain — {symbol.toUpperCase()}
          </h2>
          {chainData?.underlying_price && (
            <p style={{ margin: 0, color: theme.colors.textMuted, fontSize: "14px" }}>
              Underlying ${chainData.underlying_price.toFixed(2)} · Exp {chainData.expiration_date}
            </p>
          )}
          {chainData?.as_of && (
            <p style={{ margin: 0, color: theme.colors.textDim, fontSize: "12px" }}>
              Updated {new Date(chainData.as_of).toLocaleString()}
            </p>
          )}
        </div>
        {isModal && onClose && (
          <button
            onClick={onClose}
            style={{
              background: `${theme.colors.error}20`,
              color: theme.colors.error,
              border: `1px solid ${theme.colors.error}50`,
              padding: `${theme.spacing.xs} ${theme.spacing.md}`,
              borderRadius: theme.borderRadius.md,
              cursor: "pointer",
              fontWeight: 600,
              transition: `all ${theme.animation.duration.normal}`,
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = `${theme.colors.error}30`;
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = `${theme.colors.error}20`;
            }}
          >
            Close
          </button>
        )}
      </div>

      {/* Controls Row */}
      <div
        style={{
          display: "flex",
          gap: theme.spacing.md,
          marginBottom: theme.spacing.md,
          flexWrap: "wrap",
        }}
      >
        <div style={{ flex: "1 1 240px" }}>
          <label
            style={{
              color: theme.colors.textMuted,
              fontSize: "14px",
              display: "block",
              marginBottom: theme.spacing.xs,
            }}
          >
            Expiration Date
          </label>
          <select
            value={selectedExpiration}
            onChange={(e) => setSelectedExpiration(e.target.value)}
            style={{
              background: theme.colors.glass,
              color: theme.colors.text,
              border: `1px solid ${theme.colors.glassBorder}`,
              padding: `${theme.spacing.xs} ${theme.spacing.md}`,
              borderRadius: theme.borderRadius.md,
              fontSize: "14px",
              width: "100%",
            }}
          >
            <option value="">Select Expiration</option>
            {expirations.map((exp) => (
              <option key={exp.date} value={exp.date}>
                {exp.date} ({exp.days_to_expiry} days)
              </option>
            ))}
          </select>
        </div>

        <div style={{ flex: "1 1 240px" }}>
          <label
            style={{
              color: theme.colors.textMuted,
              fontSize: "14px",
              display: "block",
              marginBottom: theme.spacing.xs,
            }}
          >
            View
          </label>
          <div style={{ display: "flex", gap: theme.spacing.xs }}>
            {(["all", "calls", "puts"] as FilterType[]).map((filterType) => {
              const isActive = filter === filterType;
              return (
                <button
                  key={filterType}
                  onClick={() => setFilter(filterType)}
                  style={{
                    flex: 1,
                    background: isActive ? `${theme.colors.accent}20` : theme.colors.glass,
                    color: isActive ? theme.colors.accent : theme.colors.textMuted,
                    border: `1px solid ${isActive ? theme.colors.accent : theme.colors.glassBorder}`,
                    padding: `${theme.spacing.xs} ${theme.spacing.sm}`,
                    borderRadius: theme.borderRadius.md,
                    cursor: "pointer",
                    fontWeight: 600,
                    transition: `all ${theme.animation.duration.normal}`,
                  }}
                >
                  {filterType.toUpperCase()}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {chainData?.greeks_exposure && (
        <div
          style={{
            display: "flex",
            gap: theme.spacing.md,
            marginBottom: theme.spacing.lg,
            flexWrap: "wrap",
          }}
        >
          {(["calls", "puts", "net"] as const).map((bucket) => {
            const exposure = chainData.greeks_exposure[bucket];
            const label = bucket === "calls" ? "Call Exposure" : bucket === "puts" ? "Put Exposure" : "Net Exposure";
            const color =
              bucket === "calls"
                ? theme.colors.success
                : bucket === "puts"
                ? theme.colors.error
                : theme.colors.accent;
            return (
              <div
                key={bucket}
                style={{
                  flex: "1 1 260px",
                  background: `${color}15`,
                  border: `1px solid ${color}40`,
                  borderRadius: theme.borderRadius.md,
                  padding: theme.spacing.md,
                }}
              >
                <p
                  style={{
                    margin: 0,
                    marginBottom: theme.spacing.xs,
                    color,
                    fontWeight: 600,
                    letterSpacing: "0.03em",
                  }}
                >
                  {label}
                </p>
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
                    gap: theme.spacing.xs,
                    color: theme.colors.text,
                    fontSize: "12px",
                  }}
                >
                  {(
                    [
                      ["Delta", exposure.delta],
                      ["Gamma", exposure.gamma],
                      ["Theta", exposure.theta],
                      ["Vega", exposure.vega],
                      ["Rho", exposure.rho],
                    ] as const
                  ).map(([name, value]) => (
                    <div key={name} style={{ display: "flex", justifyContent: "space-between", gap: theme.spacing.xs }}>
                      <span style={{ color: theme.colors.textMuted }}>{name}</span>
                      <span style={{ fontFamily: theme.typography.fontFamily.mono }}>{formatExposure(value)}</span>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {error && (
        <div
          style={{
            marginBottom: theme.spacing.md,
            background: `${theme.colors.error}15`,
            border: `1px solid ${theme.colors.error}40`,
            color: theme.colors.error,
            borderRadius: theme.borderRadius.md,
            padding: theme.spacing.sm,
          }}
        >
          {error}
        </div>
      )}

      {loading && (
        <p style={{ color: theme.colors.textMuted, marginBottom: theme.spacing.md }}>Loading options chain…</p>
      )}

      {chainData && filteredStrikes.length > 0 && (
        <div style={{ overflowX: "auto", borderRadius: theme.borderRadius.md }}>
          <table style={{ width: "100%", borderCollapse: "collapse", minWidth: "960px" }}>
            <thead>
              <tr>
                <th
                  colSpan={6}
                  style={{
                    padding: "12px 8px",
                    color: theme.colors.success,
                    textAlign: "center",
                    background: `${theme.colors.success}15`,
                    fontWeight: 600,
                    fontSize: "13px",
                    letterSpacing: "0.03em",
                  }}
                >
                  CALLS
                </th>
                <th
                  style={{
                    padding: "12px 8px",
                    color: theme.colors.text,
                    textAlign: "center",
                    background: `${theme.colors.glassBorder}`,
                    fontWeight: 600,
                    fontSize: "13px",
                    letterSpacing: "0.03em",
                  }}
                >
                  STRIKE
                </th>
                <th
                  colSpan={6}
                  style={{
                    padding: "12px 8px",
                    color: theme.colors.error,
                    textAlign: "center",
                    background: `${theme.colors.error}15`,
                    fontWeight: 600,
                    fontSize: "13px",
                    letterSpacing: "0.03em",
                  }}
                >
                  PUTS
                </th>
              </tr>
              <tr
                style={{
                  borderBottom: `1px solid ${theme.colors.glassBorder}`,
                  color: theme.colors.textMuted,
                  fontSize: "12px",
                }}
              >
                {[
                  "Bid",
                  "Ask",
                  "Delta",
                  "Gamma",
                  "Theta",
                  "Vega",
                  "Price",
                  "Bid",
                  "Ask",
                  "Delta",
                  "Gamma",
                  "Theta",
                  "Vega",
                ].map((header, idx) => (
                  <th key={`${header}-${idx}`} style={{ padding: "8px 4px", textAlign: idx === 6 ? "center" : idx < 6 ? "right" : "left" }}>
                    {header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filteredStrikes.map(([strike, { call, put }]) => {
                const callSelected = call && activeSelection === call.symbol;
                const putSelected = put && activeSelection === put.symbol;
                const callCellBase = {
                  padding: "8px 4px",
                  textAlign: "right" as const,
                  color: call ? theme.colors.text : theme.colors.textMuted,
                  background: callSelected ? `${theme.colors.accent}20` : "transparent",
                  border: callSelected ? `1px solid ${theme.colors.accent}60` : "none",
                  cursor: call ? "pointer" : "default",
                  transition: `all ${theme.animation.duration.fast}`,
                };
                const putCellBase = {
                  padding: "8px 4px",
                  textAlign: "left" as const,
                  color: put ? theme.colors.text : theme.colors.textMuted,
                  background: putSelected ? `${theme.colors.error}15` : "transparent",
                  border: putSelected ? `1px solid ${theme.colors.error}60` : "none",
                  cursor: put ? "pointer" : "default",
                  transition: `all ${theme.animation.duration.fast}`,
                };

                return (
                  <tr key={strike} style={{ borderBottom: `1px solid ${theme.colors.glassBorder}` }}>
                    <td
                      style={callCellBase}
                      onClick={() => handleContractSelect(call)}
                    >
                      {call?.bid !== undefined ? call.bid.toFixed(2) : "—"}
                    </td>
                    <td
                      style={callCellBase}
                      onClick={() => handleContractSelect(call)}
                    >
                      {call?.ask !== undefined ? call.ask.toFixed(2) : "—"}
                    </td>
                    <td style={callCellBase} onClick={() => handleContractSelect(call)}>
                      {formatGreek(call?.delta, "delta")}
                    </td>
                    <td style={callCellBase} onClick={() => handleContractSelect(call)}>
                      {formatGreek(call?.gamma, "gamma")}
                    </td>
                    <td style={callCellBase} onClick={() => handleContractSelect(call)}>
                      {formatGreek(call?.theta, "theta")}
                    </td>
                    <td style={callCellBase} onClick={() => handleContractSelect(call)}>
                      {formatGreek(call?.vega, "vega")}
                    </td>
                    <td
                      style={{
                        padding: "8px 8px",
                        textAlign: "center",
                        color: theme.colors.text,
                        fontWeight: 600,
                        fontSize: "14px",
                        fontFamily: theme.typography.fontFamily.mono,
                      }}
                    >
                      ${strike.toFixed(2)}
                    </td>
                    <td
                      style={putCellBase}
                      onClick={() => handleContractSelect(put)}
                    >
                      {put?.bid !== undefined ? put.bid.toFixed(2) : "—"}
                    </td>
                    <td
                      style={putCellBase}
                      onClick={() => handleContractSelect(put)}
                    >
                      {put?.ask !== undefined ? put.ask.toFixed(2) : "—"}
                    </td>
                    <td style={putCellBase} onClick={() => handleContractSelect(put)}>
                      {formatGreek(put?.delta, "delta")}
                    </td>
                    <td style={putCellBase} onClick={() => handleContractSelect(put)}>
                      {formatGreek(put?.gamma, "gamma")}
                    </td>
                    <td style={putCellBase} onClick={() => handleContractSelect(put)}>
                      {formatGreek(put?.theta, "theta")}
                    </td>
                    <td style={putCellBase} onClick={() => handleContractSelect(put)}>
                      {formatGreek(put?.vega, "vega")}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {chainData && !loading && filteredStrikes.length === 0 && (
        <div style={{ textAlign: "center", padding: theme.spacing.lg, color: theme.colors.textMuted }}>
          <p>No {filter !== "all" ? filter : "options"} available for this expiration.</p>
        </div>
      )}
    </div>
  );

  if (isModal) {
    return (
      <div
        style={{
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: "rgba(5, 10, 20, 0.9)",
          backdropFilter: theme.effects.blur,
          zIndex: 9999,
          overflowY: "auto",
          padding: theme.spacing.lg,
        }}
      >
        {content}
      </div>
    );
  }

  return content;

}
