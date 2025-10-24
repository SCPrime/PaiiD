import { useEffect, useMemo, useState } from "react";

interface OrderBookEntry {
  price: number;
  size: number;
}

interface OrderBookSnapshot {
  bids: OrderBookEntry[];
  asks: OrderBookEntry[];
  timestamp?: string;
}

export interface OrderBookPanelProps {
  symbol: string;
}

/**
 * Light-weight order book panel that consumes the existing price SSE feed.
 *
 * Tradier's streaming API does not expose a full depth-of-market stream, so we
 * synthesise a shallow order book using bid/ask quotes delivered by the price
 * SSE channel. This keeps the component responsive while we iterate on richer
 * level-2 data.
 */
export function OrderBookPanel({ symbol }: OrderBookPanelProps) {
  const [orderBook, setOrderBook] = useState<OrderBookSnapshot>({ bids: [], asks: [] });
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const eventSource = new EventSource(`/api/proxy/api/stream/prices?symbols=${symbol}`);

    eventSource.onopen = () => {
      setConnected(true);
      setError(null);
    };

    const onPriceUpdate = (event: MessageEvent) => {
      try {
        const payload = JSON.parse(event.data) as Record<string, unknown>;
        const data = payload[symbol];
        if (!data) {
          return;
        }

        const entry = data as Record<string, unknown>;
        const sizeValue = Number(entry.size ?? 0);
        const size = Number.isFinite(sizeValue) ? sizeValue : 0;
        const bidPrice = Number(entry.bid);
        const askPrice = Number(entry.ask);
        const bids: OrderBookEntry[] = Number.isFinite(bidPrice)
          ? [{ price: bidPrice, size }]
          : [];
        const asks: OrderBookEntry[] = Number.isFinite(askPrice)
          ? [{ price: askPrice, size }]
          : [];

        setOrderBook({
          bids,
          asks,
          timestamp: typeof entry.timestamp === "string" ? entry.timestamp : undefined,
        });
      } catch (err) {
        console.error("Failed to parse order book payload", err);
        setError("Unable to parse order book update");
      }
    };

    eventSource.addEventListener("price_update", onPriceUpdate);

    eventSource.onerror = () => {
      setConnected(false);
      setError("Disconnected from order book stream");
    };

    return () => {
      eventSource.removeEventListener("price_update", onPriceUpdate);
      eventSource.close();
    };
  }, [symbol]);

  const formattedTimestamp = useMemo(() => {
    if (!orderBook.timestamp) {
      return "";
    }
    const date = new Date(orderBook.timestamp);
    return `${date.toLocaleTimeString()}`;
  }, [orderBook.timestamp]);

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-700">Order Book</h3>
        <span className={`text-xs font-medium ${connected ? "text-emerald-600" : "text-amber-600"}`}>
          {connected ? "Streaming" : "Connecting"}
        </span>
      </div>
      {error ? (
        <div className="rounded border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-700">
          {error}
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4 text-xs text-slate-700">
          <div>
            <h4 className="mb-2 font-semibold text-emerald-600">Bids</h4>
            <ul className="space-y-1">
              {orderBook.bids.length === 0 ? (
                <li className="text-slate-400">No bids</li>
              ) : (
                orderBook.bids.map((entry, idx) => (
                  <li key={idx} className="flex justify-between">
                    <span>${entry.price.toFixed(2)}</span>
                    <span>{Number.isFinite(entry.size) ? entry.size.toFixed(0) : "-"}</span>
                  </li>
                ))
              )}
            </ul>
          </div>
          <div>
            <h4 className="mb-2 font-semibold text-rose-600">Asks</h4>
            <ul className="space-y-1">
              {orderBook.asks.length === 0 ? (
                <li className="text-slate-400">No asks</li>
              ) : (
                orderBook.asks.map((entry, idx) => (
                  <li key={idx} className="flex justify-between">
                    <span>${entry.price.toFixed(2)}</span>
                    <span>{Number.isFinite(entry.size) ? entry.size.toFixed(0) : "-"}</span>
                  </li>
                ))
              )}
            </ul>
          </div>
        </div>
      )}
      <div className="mt-3 text-right text-[10px] text-slate-400">
        {formattedTimestamp && `Updated ${formattedTimestamp}`}
      </div>
    </div>
  );
}
