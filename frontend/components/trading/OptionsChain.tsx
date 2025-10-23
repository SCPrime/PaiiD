import { useEffect, useState } from "react";

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

interface OptionContract {
  symbol: string;
  underlying_symbol: string;
  option_type: "call" | "put";
  strike_price: number;
  expiration_date: string;

  // Market data
  bid?: number;
  ask?: number;
  last_price?: number;
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
}

interface OptionsChainData {
  symbol: string;
  expiration_date: string;
  underlying_price?: number;
  calls: OptionContract[];
  puts: OptionContract[];
  total_contracts: number;
}

interface ExpirationDate {
  date: string;
  days_to_expiry: number;
}

interface OptionsChainProps {
  symbol: string;
  onClose?: () => void;
}

type FilterType = "all" | "calls" | "puts";

export default function OptionsChain({ symbol, onClose }: OptionsChainProps) {
  const [chainData, setChainData] = useState<OptionsChainData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedExpiration, setSelectedExpiration] = useState<string>("");
  const [expirations, setExpirations] = useState<ExpirationDate[]>([]);
  const [filter, setFilter] = useState<FilterType>("all");

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
  }, [symbol, selectedExpiration]);

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

      const response = await fetch(
        `/api/proxy/options/chain/${symbol}?expiration=${selectedExpiration}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to fetch options chain: ${response.statusText}`);
      }

      const data: OptionsChainData = await response.json();
      setChainData(data);
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

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: "rgba(15, 23, 42, 0.95)",
        backdropFilter: "blur(10px)",
        zIndex: 9999,
        overflowY: "auto",
        padding: "40px 20px",
      }}
    >
      <div
        style={{
          maxWidth: "1600px",
          margin: "0 auto",
          background: "rgba(30, 41, 59, 0.8)",
          borderRadius: "16px",
          padding: "32px",
          border: "1px solid rgba(148, 163, 184, 0.1)",
        }}
      >
        {/* Header */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "24px",
          }}
        >
          <div>
            <h2 style={{ color: "white", fontSize: "28px", fontWeight: "bold", margin: 0 }}>
              Options Chain: {symbol}
            </h2>
            {chainData?.underlying_price && (
              <p style={{ color: "#94a3b8", fontSize: "16px", marginTop: "8px" }}>
                Underlying Price: ${chainData.underlying_price.toFixed(2)}
              </p>
            )}
            {chainData && (
              <p style={{ color: "#64748b", fontSize: "14px", marginTop: "4px" }}>
                {chainData.total_contracts} contracts • Expiration: {chainData.expiration_date}
              </p>
            )}
          </div>
          <button
            onClick={onClose}
            style={{
              background: "rgba(239, 68, 68, 0.2)",
              color: "#fca5a5",
              border: "1px solid rgba(239, 68, 68, 0.3)",
              padding: "10px 20px",
              borderRadius: "8px",
              cursor: "pointer",
              fontSize: "14px",
              fontWeight: "500",
            }}
          >
            Close
          </button>
        </div>

        {/* Controls Row */}
        <div style={{ display: "flex", gap: "16px", marginBottom: "24px", flexWrap: "wrap" }}>
          {/* Expiration Selector */}
          <div style={{ flex: "1", minWidth: "250px" }}>
            <label
              style={{ color: "#cbd5e1", fontSize: "14px", display: "block", marginBottom: "8px" }}
            >
              Expiration Date:
            </label>
            <select
              value={selectedExpiration}
              onChange={(e) => setSelectedExpiration(e.target.value)}
              style={{
                background: "rgba(15, 23, 42, 0.6)",
                color: "white",
                border: "1px solid rgba(148, 163, 184, 0.2)",
                padding: "12px 16px",
                borderRadius: "8px",
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

          {/* Filter Toggle */}
          <div style={{ flex: "1", minWidth: "250px" }}>
            <label
              style={{ color: "#cbd5e1", fontSize: "14px", display: "block", marginBottom: "8px" }}
            >
              Filter:
            </label>
            <div style={{ display: "flex", gap: "8px" }}>
              {(["all", "calls", "puts"] as FilterType[]).map((filterType) => (
                <button
                  key={filterType}
                  onClick={() => setFilter(filterType)}
                  style={{
                    flex: 1,
                    background:
                      filter === filterType ? "rgba(16, 185, 129, 0.2)" : "rgba(15, 23, 42, 0.6)",
                    color: filter === filterType ? "#10b981" : "#94a3b8",
                    border: `1px solid ${filter === filterType ? "rgba(16, 185, 129, 0.3)" : "rgba(148, 163, 184, 0.2)"}`,
                    padding: "12px 16px",
                    borderRadius: "8px",
                    cursor: "pointer",
                    fontSize: "14px",
                    fontWeight: "500",
                    textTransform: "capitalize",
                  }}
                >
                  {filterType}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div style={{ textAlign: "center", padding: "40px", color: "#94a3b8" }}>
            <p>Loading options chain...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div
            style={{
              background: "rgba(239, 68, 68, 0.1)",
              border: "1px solid rgba(239, 68, 68, 0.3)",
              borderRadius: "8px",
              padding: "16px",
              color: "#fca5a5",
              marginBottom: "24px",
            }}
          >
            <strong>Error:</strong> {error}
          </div>
        )}

        {/* Options Chain Table */}
        {chainData && !loading && filteredStrikes.length > 0 && (
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
              <thead>
                <tr style={{ borderBottom: "1px solid rgba(148, 163, 184, 0.2)" }}>
                  <th
                    colSpan={6}
                    style={{
                      padding: "12px 8px",
                      color: "#10b981",
                      textAlign: "center",
                      background: "rgba(16, 185, 129, 0.05)",
                    }}
                  >
                    CALLS
                  </th>
                  <th
                    style={{
                      padding: "12px 8px",
                      color: "#cbd5e1",
                      textAlign: "center",
                      background: "rgba(148, 163, 184, 0.05)",
                      fontWeight: "bold",
                    }}
                  >
                    STRIKE
                  </th>
                  <th
                    colSpan={6}
                    style={{
                      padding: "12px 8px",
                      color: "#ef4444",
                      textAlign: "center",
                      background: "rgba(239, 68, 68, 0.05)",
                    }}
                  >
                    PUTS
                  </th>
                </tr>
                <tr
                  style={{
                    borderBottom: "1px solid rgba(148, 163, 184, 0.2)",
                    color: "#94a3b8",
                    fontSize: "12px",
                  }}
                >
                  <th style={{ padding: "8px 4px", textAlign: "right" }}>Bid</th>
                  <th style={{ padding: "8px 4px", textAlign: "right" }}>Ask</th>
                  <th style={{ padding: "8px 4px", textAlign: "right" }}>Delta</th>
                  <th style={{ padding: "8px 4px", textAlign: "right" }}>Gamma</th>
                  <th style={{ padding: "8px 4px", textAlign: "right" }}>Theta</th>
                  <th style={{ padding: "8px 4px", textAlign: "right" }}>Vega</th>
                  <th style={{ padding: "8px 8px", textAlign: "center" }}>Price</th>
                  <th style={{ padding: "8px 4px", textAlign: "left" }}>Bid</th>
                  <th style={{ padding: "8px 4px", textAlign: "left" }}>Ask</th>
                  <th style={{ padding: "8px 4px", textAlign: "left" }}>Delta</th>
                  <th style={{ padding: "8px 4px", textAlign: "left" }}>Gamma</th>
                  <th style={{ padding: "8px 4px", textAlign: "left" }}>Theta</th>
                  <th style={{ padding: "8px 4px", textAlign: "left" }}>Vega</th>
                </tr>
              </thead>
              <tbody>
                {filteredStrikes.map(([strike, { call, put }]) => (
                  <tr
                    key={strike}
                    style={{
                      borderBottom: "1px solid rgba(148, 163, 184, 0.1)",
                      transition: "background 0.2s",
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background = "rgba(148, 163, 184, 0.05)";
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = "transparent";
                    }}
                  >
                    {/* Call Side */}
                    <td
                      style={{
                        padding: "8px 4px",
                        textAlign: "right",
                        color: call ? "#cbd5e1" : "#64748b",
                      }}
                    >
                      {call?.bid?.toFixed(2) || "—"}
                    </td>
                    <td
                      style={{
                        padding: "8px 4px",
                        textAlign: "right",
                        color: call ? "#cbd5e1" : "#64748b",
                      }}
                    >
                      {call?.ask?.toFixed(2) || "—"}
                    </td>
                    <td style={{ padding: "8px 4px", textAlign: "right" }}>
                      {formatGreek(call?.delta, "delta")}
                    </td>
                    <td style={{ padding: "8px 4px", textAlign: "right" }}>
                      {formatGreek(call?.gamma, "gamma")}
                    </td>
                    <td style={{ padding: "8px 4px", textAlign: "right" }}>
                      {formatGreek(call?.theta, "theta")}
                    </td>
                    <td style={{ padding: "8px 4px", textAlign: "right" }}>
                      {formatGreek(call?.vega, "vega")}
                    </td>

                    {/* Strike */}
                    <td
                      style={{
                        padding: "8px 8px",
                        textAlign: "center",
                        color: "white",
                        fontWeight: "bold",
                        fontSize: "14px",
                      }}
                    >
                      ${strike.toFixed(2)}
                    </td>

                    {/* Put Side */}
                    <td
                      style={{
                        padding: "8px 4px",
                        textAlign: "left",
                        color: put ? "#cbd5e1" : "#64748b",
                      }}
                    >
                      {put?.bid?.toFixed(2) || "—"}
                    </td>
                    <td
                      style={{
                        padding: "8px 4px",
                        textAlign: "left",
                        color: put ? "#cbd5e1" : "#64748b",
                      }}
                    >
                      {put?.ask?.toFixed(2) || "—"}
                    </td>
                    <td style={{ padding: "8px 4px", textAlign: "left" }}>
                      {formatGreek(put?.delta, "delta")}
                    </td>
                    <td style={{ padding: "8px 4px", textAlign: "left" }}>
                      {formatGreek(put?.gamma, "gamma")}
                    </td>
                    <td style={{ padding: "8px 4px", textAlign: "left" }}>
                      {formatGreek(put?.theta, "theta")}
                    </td>
                    <td style={{ padding: "8px 4px", textAlign: "left" }}>
                      {formatGreek(put?.vega, "vega")}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* No Data State */}
        {chainData && !loading && filteredStrikes.length === 0 && (
          <div style={{ textAlign: "center", padding: "40px", color: "#94a3b8" }}>
            <p>No {filter !== "all" ? filter : "options"} available for this expiration.</p>
          </div>
        )}
      </div>
    </div>
  );
}
