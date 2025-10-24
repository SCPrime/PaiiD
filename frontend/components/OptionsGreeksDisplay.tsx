import { useEffect, useState } from "react";

interface GreeksData {
  symbol: string;
  strike: number;
  expiry: string;
  option_type: "call" | "put";

  // Greeks
  delta: number;
  gamma: number;
  theta: number;
  vega: number;
  rho: number;

  // Pricing
  theoretical_price: number;
  intrinsic_value: number;
  extrinsic_value: number;
  probability_itm: number;

  // Market data (optional)
  market_price?: number;
  implied_volatility?: number;
  volume?: number;
  open_interest?: number;

  timestamp: string;
  source: string;
}

interface OptionsGreeksDisplayProps {
  symbol: string;
  strike: number;
  expiry: string; // YYYY-MM-DD format
  optionType: "call" | "put";
}

export default function OptionsGreeksDisplay({
  symbol,
  strike,
  expiry,
  optionType,
}: OptionsGreeksDisplayProps) {
  const [greeksData, setGreeksData] = useState<GreeksData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!symbol || !strike || !expiry || !optionType) {
      return;
    }

    // Validate expiry is not in the past (with some buffer)
    const expiryDate = new Date(expiry);
    const today = new Date();
    today.setHours(0, 0, 0, 0); // Start of day

    if (expiryDate < today) {
      // Only log if it's not the default/placeholder date
      const todayStr = today.toISOString().split("T")[0];
      if (expiry !== todayStr) {
        console.warn("[OptionsGreeks] Skipping fetch - expiry is in the past:", expiry);
      }
      setError("Please select a future expiration date");
      return;
    }

    const fetchGreeks = async () => {
      setLoading(true);
      setError(null);

      try {
        const params = new URLSearchParams({
          symbol,
          strike: strike.toString(),
          expiration: expiry,
          option_type: optionType,
        });

        const response = await fetch(`/api/proxy/options/greeks?${params}`);

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || "Failed to fetch Greeks");
        }

        const data: GreeksData = await response.json();
        setGreeksData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
        console.error("[OptionsGreeks] Error fetching Greeks:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchGreeks();
  }, [symbol, strike, expiry, optionType]);

  if (loading) {
    return (
      <div
        style={{
          padding: "16px",
          background: "rgba(15, 23, 42, 0.6)",
          backdropFilter: "blur(10px)",
          borderRadius: "8px",
          border: "1px solid rgba(100, 116, 139, 0.3)",
          textAlign: "center",
        }}
      >
        <div style={{ color: "#94a3b8", fontSize: "14px" }}>Calculating Greeks...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div
        style={{
          padding: "16px",
          background: "rgba(239, 68, 68, 0.1)",
          backdropFilter: "blur(10px)",
          borderRadius: "8px",
          border: "1px solid rgba(239, 68, 68, 0.3)",
        }}
      >
        <div style={{ color: "#ef4444", fontSize: "14px" }}>Error: {error}</div>
      </div>
    );
  }

  if (!greeksData) {
    return null;
  }

  // Helper function to get color based on Greek value and type
  const getGreekColor = (greekName: string, value: number): string => {
    switch (greekName) {
      case "delta":
        // For calls: positive delta is bullish (green)
        // For puts: negative delta is bearish (red is appropriate)
        return value > 0 ? "#10b981" : "#ef4444";
      case "theta":
        // Negative theta is bad for option buyers (red)
        return value < 0 ? "#ef4444" : "#10b981";
      case "gamma":
      case "vega":
        // Higher gamma/vega is more volatility exposure (neutral to slightly positive)
        return value > 0.05 ? "#10b981" : "#94a3b8";
      default:
        return "#94a3b8";
    }
  };

  const greeksGrid = [
    {
      name: "Delta",
      value: greeksData.delta,
      tooltip: "Rate of change in option price per $1 move in underlying stock",
      format: (v: number) => v.toFixed(4),
    },
    {
      name: "Gamma",
      value: greeksData.gamma,
      tooltip: "Rate of change in delta per $1 move in underlying stock",
      format: (v: number) => v.toFixed(4),
    },
    {
      name: "Theta",
      value: greeksData.theta,
      tooltip: "Option price decay per day (time decay)",
      format: (v: number) => `${v.toFixed(4)}/day`,
    },
    {
      name: "Vega",
      value: greeksData.vega,
      tooltip: "Change in option price per 1% change in implied volatility",
      format: (v: number) => v.toFixed(4),
    },
    {
      name: "Rho",
      value: greeksData.rho,
      tooltip: "Change in option price per 1% change in interest rate",
      format: (v: number) => v.toFixed(4),
    },
  ];

  return (
    <div
      style={{
        background: "rgba(15, 23, 42, 0.6)",
        backdropFilter: "blur(10px)",
        borderRadius: "8px",
        border: "1px solid rgba(100, 116, 139, 0.3)",
        padding: "16px",
      }}
    >
      {/* Header */}
      <div style={{ marginBottom: "16px" }}>
        <h3
          style={{
            margin: 0,
            fontSize: "16px",
            fontWeight: 600,
            color: "#f1f5f9",
            marginBottom: "8px",
          }}
        >
          Options Greeks
        </h3>
        <div
          style={{
            fontSize: "12px",
            color: "#94a3b8",
          }}
        >
          {symbol.toUpperCase()} ${strike} {optionType.toUpperCase()} (Exp: {expiry})
        </div>
      </div>

      {/* Pricing Summary */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
          gap: "12px",
          marginBottom: "16px",
          padding: "12px",
          background: "rgba(30, 41, 59, 0.5)",
          borderRadius: "6px",
        }}
      >
        <div>
          <div style={{ fontSize: "11px", color: "#94a3b8", marginBottom: "4px" }}>
            Theoretical Price
          </div>
          <div style={{ fontSize: "16px", fontWeight: 600, color: "#10b981" }}>
            ${greeksData.theoretical_price.toFixed(2)}
          </div>
        </div>

        {greeksData.market_price && (
          <div>
            <div style={{ fontSize: "11px", color: "#94a3b8", marginBottom: "4px" }}>
              Market Price
            </div>
            <div style={{ fontSize: "16px", fontWeight: 600, color: "#f1f5f9" }}>
              ${greeksData.market_price.toFixed(2)}
            </div>
          </div>
        )}

        <div>
          <div style={{ fontSize: "11px", color: "#94a3b8", marginBottom: "4px" }}>
            Probability ITM
          </div>
          <div
            style={{
              fontSize: "16px",
              fontWeight: 600,
              color: greeksData.probability_itm > 0.5 ? "#10b981" : "#ef4444",
            }}
          >
            {(greeksData.probability_itm * 100).toFixed(1)}%
          </div>
        </div>

        {greeksData.implied_volatility && (
          <div>
            <div style={{ fontSize: "11px", color: "#94a3b8", marginBottom: "4px" }}>
              Implied Vol
            </div>
            <div style={{ fontSize: "16px", fontWeight: 600, color: "#f1f5f9" }}>
              {(greeksData.implied_volatility * 100).toFixed(1)}%
            </div>
          </div>
        )}
      </div>

      {/* Greeks Grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(100px, 1fr))",
          gap: "12px",
        }}
      >
        {greeksGrid.map((greek) => (
          <div
            key={greek.name}
            title={greek.tooltip}
            style={{
              padding: "12px",
              background: "rgba(30, 41, 59, 0.5)",
              borderRadius: "6px",
              border: "1px solid rgba(100, 116, 139, 0.2)",
              cursor: "help",
              transition: "all 0.2s",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = "rgba(30, 41, 59, 0.8)";
              e.currentTarget.style.borderColor = "rgba(100, 116, 139, 0.5)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = "rgba(30, 41, 59, 0.5)";
              e.currentTarget.style.borderColor = "rgba(100, 116, 139, 0.2)";
            }}
          >
            <div
              style={{
                fontSize: "11px",
                color: "#94a3b8",
                marginBottom: "4px",
                fontWeight: 500,
              }}
            >
              {greek.name}
            </div>
            <div
              style={{
                fontSize: "16px",
                fontWeight: 600,
                color: getGreekColor(greek.name.toLowerCase(), greek.value),
              }}
            >
              {greek.format(greek.value)}
            </div>
          </div>
        ))}
      </div>

      {/* Value Breakdown */}
      <div
        style={{
          marginTop: "12px",
          padding: "12px",
          background: "rgba(30, 41, 59, 0.3)",
          borderRadius: "6px",
          fontSize: "12px",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px" }}>
          <span style={{ color: "#94a3b8" }}>Intrinsic Value:</span>
          <span style={{ color: "#f1f5f9", fontWeight: 500 }}>
            ${greeksData.intrinsic_value.toFixed(2)}
          </span>
        </div>
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <span style={{ color: "#94a3b8" }}>Extrinsic Value:</span>
          <span style={{ color: "#f1f5f9", fontWeight: 500 }}>
            ${greeksData.extrinsic_value.toFixed(2)}
          </span>
        </div>
      </div>

      {/* Market Data (if available) */}
      {(greeksData.volume || greeksData.open_interest) && (
        <div
          style={{
            marginTop: "12px",
            padding: "12px",
            background: "rgba(30, 41, 59, 0.3)",
            borderRadius: "6px",
            fontSize: "12px",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px" }}>
            <span style={{ color: "#94a3b8" }}>Volume:</span>
            <span style={{ color: "#f1f5f9", fontWeight: 500 }}>
              {greeksData.volume?.toLocaleString() || "N/A"}
            </span>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <span style={{ color: "#94a3b8" }}>Open Interest:</span>
            <span style={{ color: "#f1f5f9", fontWeight: 500 }}>
              {greeksData.open_interest?.toLocaleString() || "N/A"}
            </span>
          </div>
        </div>
      )}

      {/* Data Source Footer */}
      <div
        style={{
          marginTop: "12px",
          paddingTop: "12px",
          borderTop: "1px solid rgba(100, 116, 139, 0.2)",
          fontSize: "11px",
          color: "#64748b",
          textAlign: "center",
        }}
      >
        Calculated using Black-Scholes-Merton model • Data from Tradier API
      </div>
    </div>
  );
}
