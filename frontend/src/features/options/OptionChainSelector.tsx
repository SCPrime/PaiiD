"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import type { ChangeEvent } from "react";
import { Loader2, Sparkles, X } from "lucide-react";

import {
  OptionChainPayload,
  OptionChainSelection,
  OptionContractQuote,
  OptionExpirationSummary,
  OptionGreeks,
  OptionLegQuote,
  StrategyKey,
} from "./types";

interface OptionChainSelectorProps {
  symbol: string;
  onSelectionChange?: (selection: OptionChainSelection) => void;
  initialStrategy?: StrategyKey;
  apiToken?: string;
}

interface StrategyTemplate {
  key: StrategyKey;
  label: string;
  description: string;
  supportsWidth: boolean;
}

const STRATEGY_TEMPLATES: StrategyTemplate[] = [
  {
    key: "iron_condor",
    label: "Iron Condor",
    description: "Sell ATM call & put, buy protective wings",
    supportsWidth: true,
  },
  {
    key: "butterfly",
    label: "Call Butterfly",
    description: "Long fly centered on ATM strike (1-2-1)",
    supportsWidth: true,
  },
  {
    key: "vertical_call",
    label: "Bull Call Vertical",
    description: "Buy call and sell higher strike call",
    supportsWidth: true,
  },
  {
    key: "vertical_put",
    label: "Bear Put Vertical",
    description: "Buy put and sell lower strike put",
    supportsWidth: true,
  },
  {
    key: "straddle",
    label: "Long Straddle",
    description: "Buy call + buy put at ATM",
    supportsWidth: false,
  },
  {
    key: "strangle",
    label: "Long Strangle",
    description: "Buy OTM call & put",
    supportsWidth: true,
  },
  {
    key: "custom",
    label: "Custom",
    description: "Build legs manually",
    supportsWidth: false,
  },
];

const widthOptions = [
  { label: "Closest strikes", value: 1 },
  { label: "±2 strikes", value: 2 },
  { label: "±3 strikes", value: 3 },
];

export default function OptionChainSelector({
  symbol,
  onSelectionChange,
  initialStrategy = "custom",
  apiToken,
}: OptionChainSelectorProps) {
  const token = apiToken ?? process.env.NEXT_PUBLIC_API_TOKEN;

  const [expirations, setExpirations] = useState<OptionExpirationSummary[]>([]);
  const [selectedExpiration, setSelectedExpiration] = useState<string>("");
  const [chainData, setChainData] = useState<OptionChainPayload | null>(null);
  const [loadingExpirations, setLoadingExpirations] = useState(false);
  const [loadingChain, setLoadingChain] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedStrategy, setSelectedStrategy] = useState<StrategyKey>(initialStrategy);
  const [widthSteps, setWidthSteps] = useState<number>(1);
  const [selectedLegs, setSelectedLegs] = useState<OptionLegQuote[]>([]);
  const [templateMessage, setTemplateMessage] = useState<string | null>(null);

  const fetchExpirations = useCallback(async () => {
    setLoadingExpirations(true);
    setError(null);

    try {
      const response = await fetch(`/api/proxy/options/expirations/${symbol}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });

      if (!response.ok) {
        throw new Error(`Unable to fetch expirations (${response.status})`);
      }

      const data: OptionExpirationSummary[] = await response.json();
      setExpirations(data);
      if (data.length > 0) {
        setSelectedExpiration((prev) => prev || data[0].date);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load expirations");
    } finally {
      setLoadingExpirations(false);
    }
  }, [symbol, token]);

  const fetchChain = useCallback(async () => {
    if (!selectedExpiration) {
      return;
    }

    setLoadingChain(true);
    setError(null);
    setTemplateMessage(null);

    try {
      const response = await fetch(
        `/api/proxy/options/chains/${symbol}?expiration=${encodeURIComponent(selectedExpiration)}`,
        {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        },
      );

      if (!response.ok) {
        throw new Error(`Unable to fetch chain (${response.status})`);
      }

      const data: OptionChainPayload = await response.json();
      setChainData(data);
      setSelectedLegs([]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load options chain");
    } finally {
      setLoadingChain(false);
    }
  }, [selectedExpiration, symbol, token]);

  useEffect(() => {
    fetchExpirations();
  }, [fetchExpirations]);

  useEffect(() => {
    if (selectedExpiration) {
      fetchChain();
    }
  }, [selectedExpiration, fetchChain]);

  useEffect(() => {
    if (!onSelectionChange) return;

    onSelectionChange({
      strategy: selectedStrategy,
      legs: selectedLegs,
      underlyingPrice: chainData?.underlying_price ?? null,
    });
  }, [selectedLegs, selectedStrategy, chainData?.underlying_price, onSelectionChange]);

  const strikeRows = useMemo(() => {
    if (!chainData) return [] as Array<{ strike: number; call?: OptionContractQuote; put?: OptionContractQuote }>;

    const map = new Map<number, { strike: number; call?: OptionContractQuote; put?: OptionContractQuote }>();

    const push = (contract: OptionContractQuote) => {
      const entry = map.get(contract.strike_price) ?? { strike: contract.strike_price };
      if (contract.option_type === "call") {
        entry.call = contract;
      } else {
        entry.put = contract;
      }
      map.set(contract.strike_price, entry);
    };

    chainData.calls.forEach(push);
    chainData.puts.forEach(push);

    return Array.from(map.values()).sort((a, b) => a.strike - b.strike);
  }, [chainData]);

  const callsSorted = useMemo(
    () => (chainData ? [...chainData.calls].sort((a, b) => a.strike_price - b.strike_price) : []),
    [chainData],
  );

  const putsSorted = useMemo(
    () => (chainData ? [...chainData.puts].sort((a, b) => a.strike_price - b.strike_price) : []),
    [chainData],
  );

  const underlyingPrice = chainData?.underlying_price ?? null;

  const applyTemplate = useCallback(
    (strategy: StrategyKey) => {
      if (!chainData) return;

      const template = STRATEGY_TEMPLATES.find((item) => item.key === strategy);
      if (!template) return;

      if (strategy === "custom") {
        setSelectedStrategy("custom");
        setTemplateMessage("Switched to manual leg selection.");
        return;
      }

      const underlying = underlyingPrice ?? callsSorted[0]?.strike_price ?? putsSorted[0]?.strike_price;
      if (!underlying) {
        setTemplateMessage("Unable to determine underlying price for template generation.");
        return;
      }

      const callIndex = findClosestIndex(callsSorted, underlying);
      const putIndex = findClosestIndex(putsSorted, underlying);

      if (callIndex < 0 || putIndex < 0) {
        setTemplateMessage("Not enough option strikes available for template.");
        return;
      }

      const legBuilder = (contract: OptionContractQuote, action: "BUY" | "SELL", quantity = 1, metadata?: Record<string, unknown>): OptionLegQuote => ({
        id: `${contract.symbol}-${action}`,
        action,
        optionType: contract.option_type,
        strike: contract.strike_price,
        expiration: contract.expiration_date,
        quantity,
        price: derivePrice(contract),
        contractSymbol: contract.symbol,
        underlyingPrice,
        impliedVolatility: contract.implied_volatility ?? undefined,
        greeks: contract.greeks as OptionGreeks | undefined,
        metadata: {
          source: "template",
          strategy,
          ...(metadata ?? {}),
        },
      });

      const legs: OptionLegQuote[] = [];

      switch (strategy) {
        case "iron_condor": {
          const shortCall = callsSorted[callIndex];
          const shortPut = putsSorted[putIndex];
          const longCall = callsSorted[Math.min(callIndex + widthSteps, callsSorted.length - 1)];
          const longPut = putsSorted[Math.max(putIndex - widthSteps, 0)];

          if (!shortCall || !shortPut || !longCall || !longPut) {
            setTemplateMessage("Not enough strikes to build iron condor.");
            return;
          }

          legs.push(
            legBuilder(shortCall, "SELL", 1, { leg: "short_call" }),
            legBuilder(shortPut, "SELL", 1, { leg: "short_put" }),
            legBuilder(longCall, "BUY", 1, { leg: "long_call" }),
            legBuilder(longPut, "BUY", 1, { leg: "long_put" }),
          );
          break;
        }
        case "butterfly": {
          const center = callsSorted[callIndex];
          const lower = callsSorted[Math.max(callIndex - widthSteps, 0)];
          const upper = callsSorted[Math.min(callIndex + widthSteps, callsSorted.length - 1)];
          if (!center || !lower || !upper) {
            setTemplateMessage("Not enough call strikes to build butterfly.");
            return;
          }
          legs.push(
            legBuilder(lower, "BUY", 1, { leg: "long_lower" }),
            legBuilder(center, "SELL", 2, { leg: "short_center" }),
            legBuilder(upper, "BUY", 1, { leg: "long_upper" }),
          );
          break;
        }
        case "vertical_call": {
          const buyLeg = callsSorted[Math.max(callIndex, 0)];
          const sellLeg = callsSorted[Math.min(callIndex + widthSteps, callsSorted.length - 1)];
          if (!buyLeg || !sellLeg) {
            setTemplateMessage("Not enough call strikes to build vertical spread.");
            return;
          }
          legs.push(
            legBuilder(buyLeg, "BUY", 1, { leg: "long_call" }),
            legBuilder(sellLeg, "SELL", 1, { leg: "short_call" }),
          );
          break;
        }
        case "vertical_put": {
          const buyLeg = putsSorted[Math.max(putIndex, 0)];
          const sellLeg = putsSorted[Math.max(putIndex - widthSteps, 0)];
          if (!buyLeg || !sellLeg) {
            setTemplateMessage("Not enough put strikes to build vertical spread.");
            return;
          }
          legs.push(
            legBuilder(buyLeg, "BUY", 1, { leg: "long_put" }),
            legBuilder(sellLeg, "SELL", 1, { leg: "short_put" }),
          );
          break;
        }
        case "straddle": {
          const atmCall = callsSorted[callIndex];
          const atmPut = putsSorted[putIndex];
          if (!atmCall || !atmPut) {
            setTemplateMessage("ATM call/put not available for straddle.");
            return;
          }
          legs.push(
            legBuilder(atmCall, "BUY", 1, { leg: "long_call" }),
            legBuilder(atmPut, "BUY", 1, { leg: "long_put" }),
          );
          break;
        }
        case "strangle": {
          const callLeg = callsSorted[Math.min(callIndex + widthSteps, callsSorted.length - 1)];
          const putLeg = putsSorted[Math.max(putIndex - widthSteps, 0)];
          if (!callLeg || !putLeg) {
            setTemplateMessage("Unable to find strikes for strangle.");
            return;
          }
          legs.push(
            legBuilder(callLeg, "BUY", 1, { leg: "long_call" }),
            legBuilder(putLeg, "BUY", 1, { leg: "long_put" }),
          );
          break;
        }
        default:
          break;
      }

      if (legs.length === 0) {
        return;
      }

      setSelectedStrategy(strategy);
      setSelectedLegs(legs);
      setTemplateMessage(`${template.label} template applied (${legs.length} legs).`);
    },
    [callsSorted, chainData, underlyingPrice, widthSteps, putsSorted],
  );

  const handleStrategyChange = (event: ChangeEvent<HTMLSelectElement>) => {
    const nextStrategy = event.target.value as StrategyKey;
    setSelectedStrategy(nextStrategy);
    applyTemplate(nextStrategy);
  };

  const handleManualToggle = (contract: OptionContractQuote, action: "BUY" | "SELL") => {
    setSelectedStrategy("custom");
    setTemplateMessage(null);

    const id = `${contract.symbol}-${action}`;
    setSelectedLegs((prev) => {
      const exists = prev.some((leg) => leg.id === id);
      if (exists) {
        return prev.filter((leg) => leg.id !== id);
      }
      const newLeg: OptionLegQuote = {
        id,
        action,
        optionType: contract.option_type,
        strike: contract.strike_price,
        expiration: contract.expiration_date,
        quantity: 1,
        price: derivePrice(contract),
        contractSymbol: contract.symbol,
        underlyingPrice,
        impliedVolatility: contract.implied_volatility ?? undefined,
        greeks: contract.greeks as OptionGreeks | undefined,
        metadata: { source: "manual" },
      };
      return [...prev, newLeg];
    });
  };

  const removeLeg = (id: string) => {
    setSelectedLegs((prev) => prev.filter((leg) => leg.id !== id));
  };

  const clearSelection = () => {
    setSelectedLegs([]);
    setSelectedStrategy("custom");
    setTemplateMessage(null);
  };

  const isLegSelected = (contract: OptionContractQuote, action: "BUY" | "SELL") =>
    selectedLegs.some((leg) => leg.contractSymbol === contract.symbol && leg.action === action);

  return (
    <div className="space-y-4 rounded-xl border border-slate-700/60 bg-slate-900/60 p-4 text-slate-100 shadow-xl">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold tracking-wide text-cyan-300">
            Options Chain · {symbol.toUpperCase()}
          </h2>
          {underlyingPrice && (
            <p className="text-sm text-slate-400">Underlying: ${underlyingPrice.toFixed(2)}</p>
          )}
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <select
            value={selectedExpiration}
            onChange={(event) => setSelectedExpiration(event.target.value)}
            className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm focus:border-cyan-500 focus:outline-none"
          >
            {expirations.map((exp) => (
              <option key={exp.date} value={exp.date}>
                {exp.date} · {exp.days_to_expiry} DTE
              </option>
            ))}
          </select>
          <div className="flex items-center gap-2">
            <select
              value={selectedStrategy}
              onChange={handleStrategyChange}
              className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm focus:border-cyan-500 focus:outline-none"
            >
              {STRATEGY_TEMPLATES.map((template) => (
                <option key={template.key} value={template.key}>
                  {template.label}
                </option>
              ))}
            </select>
            <select
              value={widthSteps}
              onChange={(event) => setWidthSteps(Number(event.target.value))}
              className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm focus:border-cyan-500 focus:outline-none"
              disabled={!STRATEGY_TEMPLATES.find((t) => t.key === selectedStrategy)?.supportsWidth}
            >
              {widthOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            <button
              type="button"
              onClick={() => applyTemplate(selectedStrategy)}
              className="inline-flex items-center gap-1 rounded-lg bg-cyan-600 px-3 py-2 text-sm font-semibold text-white shadow hover:bg-cyan-500"
            >
              <Sparkles size={16} /> Apply
            </button>
            <button
              type="button"
              onClick={clearSelection}
              className="inline-flex items-center gap-1 rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-300 hover:border-slate-500"
            >
              <X size={16} /> Clear
            </button>
          </div>
        </div>
      </header>

      {templateMessage && (
        <div className="rounded-lg border border-cyan-500/40 bg-cyan-500/10 px-3 py-2 text-sm text-cyan-200">
          {templateMessage}
        </div>
      )}

      {error && (
        <div className="rounded-lg border border-red-500/40 bg-red-500/10 px-3 py-2 text-sm text-red-200">
          {error}
        </div>
      )}

      {(loadingExpirations || loadingChain) && (
        <div className="flex items-center gap-2 text-sm text-slate-400">
          <Loader2 className="h-4 w-4 animate-spin" /> Loading options data...
        </div>
      )}

      {!loadingChain && chainData && (
        <div className="overflow-hidden rounded-xl border border-slate-800/80">
          <table className="w-full table-fixed border-collapse text-sm">
            <thead className="bg-slate-900/70 text-slate-400">
              <tr>
                <th className="px-3 py-2 text-left">Strike</th>
                <th className="px-3 py-2 text-left">Call (Buy/Sell)</th>
                <th className="px-3 py-2 text-left">Call IV</th>
                <th className="px-3 py-2 text-left">Put (Buy/Sell)</th>
                <th className="px-3 py-2 text-left">Put IV</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80 bg-slate-900/40">
              {strikeRows.map((row) => (
                <tr key={row.strike}>
                  <td className="px-3 py-2 font-medium text-slate-200">{row.strike.toFixed(2)}</td>
                  <td className="px-3 py-2">
                    {row.call ? (
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-xs text-slate-400">
                          {formatPrice(row.call.mark_price ?? row.call.last_price)}
                        </span>
                        <div className="flex gap-1">
                          <button
                            type="button"
                            onClick={() => handleManualToggle(row.call!, "BUY")}
                            className={`rounded px-2 py-1 text-xs font-semibold ${
                              isLegSelected(row.call, "BUY")
                                ? "bg-emerald-600 text-white"
                                : "bg-slate-800 text-emerald-300 hover:bg-slate-700"
                            }`}
                          >
                            Buy
                          </button>
                          <button
                            type="button"
                            onClick={() => handleManualToggle(row.call!, "SELL")}
                            className={`rounded px-2 py-1 text-xs font-semibold ${
                              isLegSelected(row.call, "SELL")
                                ? "bg-rose-600 text-white"
                                : "bg-slate-800 text-rose-300 hover:bg-slate-700"
                            }`}
                          >
                            Sell
                          </button>
                        </div>
                      </div>
                    ) : (
                      <span className="text-xs text-slate-500">—</span>
                    )}
                  </td>
                  <td className="px-3 py-2 text-xs text-slate-400">
                    {formatPercent(row.call?.implied_volatility)}
                  </td>
                  <td className="px-3 py-2">
                    {row.put ? (
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-xs text-slate-400">
                          {formatPrice(row.put.mark_price ?? row.put.last_price)}
                        </span>
                        <div className="flex gap-1">
                          <button
                            type="button"
                            onClick={() => handleManualToggle(row.put!, "BUY")}
                            className={`rounded px-2 py-1 text-xs font-semibold ${
                              isLegSelected(row.put, "BUY")
                                ? "bg-emerald-600 text-white"
                                : "bg-slate-800 text-emerald-300 hover:bg-slate-700"
                            }`}
                          >
                            Buy
                          </button>
                          <button
                            type="button"
                            onClick={() => handleManualToggle(row.put!, "SELL")}
                            className={`rounded px-2 py-1 text-xs font-semibold ${
                              isLegSelected(row.put, "SELL")
                                ? "bg-rose-600 text-white"
                                : "bg-slate-800 text-rose-300 hover:bg-slate-700"
                            }`}
                          >
                            Sell
                          </button>
                        </div>
                      </div>
                    ) : (
                      <span className="text-xs text-slate-500">—</span>
                    )}
                  </td>
                  <td className="px-3 py-2 text-xs text-slate-400">
                    {formatPercent(row.put?.implied_volatility)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <section className="rounded-xl border border-slate-800/60 bg-slate-900/30 p-3">
        <h3 className="flex items-center gap-2 text-sm font-semibold text-slate-200">
          Selected Legs
          <span className="rounded-full bg-slate-800 px-2 py-0.5 text-xs text-slate-300">
            {selectedLegs.length}
          </span>
        </h3>
        {selectedLegs.length === 0 ? (
          <p className="mt-2 text-sm text-slate-400">Use the table above or a template to stage legs.</p>
        ) : (
          <div className="mt-2 space-y-2">
            {selectedLegs.map((leg) => (
              <div
                key={leg.id}
                className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-slate-800 bg-slate-900/60 px-3 py-2 text-sm"
              >
                <div className="flex flex-wrap items-center gap-3">
                  <span
                    className={`rounded px-2 py-0.5 text-xs font-semibold ${
                      leg.action === "BUY" ? "bg-emerald-600/40 text-emerald-200" : "bg-rose-600/40 text-rose-200"
                    }`}
                  >
                    {leg.action}
                  </span>
                  <span className="text-slate-200">
                    {leg.optionType.toUpperCase()} {leg.strike.toFixed(2)} · {leg.expiration}
                  </span>
                  <span className="text-xs text-slate-400">Qty {leg.quantity}</span>
                  {leg.price !== undefined && (
                    <span className="text-xs text-slate-400">{formatPrice(leg.price)}</span>
                  )}
                  {leg.impliedVolatility !== undefined && (
                    <span className="text-xs text-slate-500">IV {formatPercent(leg.impliedVolatility)}</span>
                  )}
                </div>
                <button
                  type="button"
                  onClick={() => removeLeg(leg.id)}
                  className="text-xs text-slate-400 hover:text-slate-200"
                >
                  Remove
                </button>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

function derivePrice(contract: OptionContractQuote): number | undefined {
  const values = [contract.mark_price, contract.last_price, contract.bid && contract.ask ? (contract.bid + contract.ask) / 2 : null];
  const price = values.find((value) => value !== null && value !== undefined && value > 0);
  return typeof price === "number" ? parseFloat(price.toFixed(2)) : undefined;
}

function formatPrice(value?: number | null) {
  if (value === undefined || value === null) return "—";
  return `$${value.toFixed(2)}`;
}

function formatPercent(value?: number | null) {
  if (value === undefined || value === null) return "—";
  return `${(value * 100).toFixed(1)}%`;
}

function findClosestIndex(options: OptionContractQuote[], target: number): number {
  if (options.length === 0) return -1;
  let closest = 0;
  let minDiff = Math.abs(options[0].strike_price - target);
  for (let i = 1; i < options.length; i += 1) {
    const diff = Math.abs(options[i].strike_price - target);
    if (diff < minDiff) {
      closest = i;
      minDiff = diff;
    }
  }
  return closest;
}
