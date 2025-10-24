import { useMemo } from "react";

import { useMarketStream } from "@/hooks/useMarketStream";

export interface QuoteTickerProps {
  symbols: string[];
  autoReconnect?: boolean;
}

export function QuoteTicker({ symbols, autoReconnect = true }: QuoteTickerProps) {
  const { prices, connected, error } = useMarketStream(symbols, {
    autoReconnect,
    debug: process.env.NODE_ENV !== "production",
  });

  const rows = useMemo(() => {
    return symbols.map((symbol) => {
      const priceValue = Number(prices[symbol]?.price ?? 0);
      const type = prices[symbol]?.type ?? "trade";
      const timestamp = prices[symbol]?.timestamp;
      const bidValue = Number(prices[symbol]?.bid ?? NaN);
      const askValue = Number(prices[symbol]?.ask ?? NaN);

      return {
        symbol,
        price: Number.isFinite(priceValue) ? priceValue : 0,
        type,
        timestamp,
        bid: Number.isFinite(bidValue) ? bidValue : undefined,
        ask: Number.isFinite(askValue) ? askValue : undefined,
      };
    });
  }, [symbols, prices]);

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-700">Live Quotes</h3>
        <span
          className={`text-xs font-medium ${connected ? "text-emerald-600" : "text-amber-600"}`}
        >
          {connected ? "Streaming" : "Connecting"}
        </span>
      </div>
      {error ? (
        <div className="rounded border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-700">
          {error}
        </div>
      ) : (
        <table className="w-full table-auto border-collapse text-left text-xs">
          <thead>
            <tr className="text-slate-500">
              <th className="pb-2">Symbol</th>
              <th className="pb-2">Last</th>
              <th className="pb-2">Bid</th>
              <th className="pb-2">Ask</th>
              <th className="pb-2">Type</th>
              <th className="pb-2">Updated</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(({ symbol, price, type, timestamp, bid, ask }) => (
              <tr key={symbol} className="border-t border-slate-100 text-slate-700">
                <td className="py-2 font-medium">{symbol}</td>
                <td className="py-2">{price ? price.toFixed(2) : "-"}</td>
                <td className="py-2">{bid ? bid.toFixed(2) : "-"}</td>
                <td className="py-2">{ask ? ask.toFixed(2) : "-"}</td>
                <td className="py-2 capitalize">{type}</td>
                <td className="py-2 text-slate-400">
                  {timestamp ? new Date(timestamp).toLocaleTimeString() : ""}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
