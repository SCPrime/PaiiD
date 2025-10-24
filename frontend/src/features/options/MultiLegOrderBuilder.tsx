"use client";

import { useEffect, useMemo, useState } from "react";
import type { ChangeEvent, FormEvent } from "react";
import { Loader2, Send } from "lucide-react";

import {
  OptionChainSelection,
  OptionLegQuote,
  OptionGreeks,
  StrategyKey,
} from "./types";

interface MultiLegOrderResponse {
  id: number;
  symbol: string;
  strategy: StrategyKey;
  order_type: "debit" | "credit" | "even";
  net_price: number;
  underlying_price?: number | null;
  status: string;
  notes?: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  legs: Array<{
    id: number;
    action: "BUY" | "SELL";
    option_type: "call" | "put";
    strike: number;
    expiration: string;
    quantity: number;
    price?: number | null;
    contract_symbol: string;
    implied_volatility?: number | null;
    delta?: number | null;
    gamma?: number | null;
    theta?: number | null;
    vega?: number | null;
    rho?: number | null;
  }>;
  order_submission: Array<Record<string, unknown>>;
}

interface MultiLegOrderBuilderProps {
  symbol: string;
  selection: OptionChainSelection | null;
  apiToken?: string;
  onSubmitSuccess?: (order: MultiLegOrderResponse) => void;
}

interface AggregatedGreeks {
  delta: number;
  gamma: number;
  theta: number;
  vega: number;
  rho: number;
}

const STRATEGY_OPTIONS: Array<{ key: StrategyKey; label: string }> = [
  { key: "iron_condor", label: "Iron Condor" },
  { key: "butterfly", label: "Butterfly" },
  { key: "vertical_call", label: "Vertical (Call)" },
  { key: "vertical_put", label: "Vertical (Put)" },
  { key: "straddle", label: "Straddle" },
  { key: "strangle", label: "Strangle" },
  { key: "custom", label: "Custom" },
];

export default function MultiLegOrderBuilder({
  symbol,
  selection,
  apiToken,
  onSubmitSuccess,
}: MultiLegOrderBuilderProps) {
  const token = apiToken ?? process.env.NEXT_PUBLIC_API_TOKEN;

  const [legs, setLegs] = useState<OptionLegQuote[]>([]);
  const [strategy, setStrategy] = useState<StrategyKey>(selection?.strategy ?? "custom");
  const [underlyingPrice, setUnderlyingPrice] = useState<number | null>(selection?.underlyingPrice ?? null);
  const [notes, setNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitResult, setSubmitResult] = useState<MultiLegOrderResponse | null>(null);

  useEffect(() => {
    if (!selection) return;

    setStrategy(selection.strategy);
    setUnderlyingPrice(selection.underlyingPrice ?? null);
    setLegs(
      selection.legs.map((leg) => ({
        ...leg,
        quantity: leg.quantity ?? 1,
        price: leg.price ?? undefined,
      })),
    );
  }, [selection]);

  const summary = useMemo(() => {
    const totalPremium = legs.reduce((sum, leg) => {
      const legPrice = leg.price ?? 0;
      const multiplier = leg.action === "BUY" ? 1 : -1;
      return sum + multiplier * legPrice * leg.quantity;
    }, 0);

    const totalContracts = legs.reduce((sum, leg) => sum + leg.quantity, 0);

    const orderType = totalPremium > 0 ? "debit" : totalPremium < 0 ? "credit" : "even";

    return {
      netPremium: totalPremium,
      totalContracts,
      orderType,
      notionals: totalPremium * 100,
    };
  }, [legs]);

  const aggregatedGreeks = useMemo(() => {
    const totals: AggregatedGreeks = {
      delta: 0,
      gamma: 0,
      theta: 0,
      vega: 0,
      rho: 0,
    };

    legs.forEach((leg) => {
      if (!leg.greeks) return;
      const multiplier = leg.action === "BUY" ? 1 : -1;
      const contractMultiplier = multiplier * leg.quantity * 100;
      const greeks = leg.greeks as OptionGreeks;
      totals.delta += (greeks.delta ?? 0) * contractMultiplier;
      totals.gamma += (greeks.gamma ?? 0) * contractMultiplier;
      totals.theta += (greeks.theta ?? 0) * contractMultiplier;
      totals.vega += (greeks.vega ?? 0) * contractMultiplier;
      totals.rho += (greeks.rho ?? 0) * contractMultiplier;
    });

    return totals;
  }, [legs]);

  const handleQuantityChange = (id: string, event: ChangeEvent<HTMLInputElement>) => {
    const nextValue = Number(event.target.value);
    if (Number.isNaN(nextValue) || nextValue <= 0) return;

    setLegs((prev) => prev.map((leg) => (leg.id === id ? { ...leg, quantity: nextValue } : leg)));
  };

  const handlePriceChange = (id: string, event: ChangeEvent<HTMLInputElement>) => {
    const raw = event.target.value;
    const nextValue = raw === "" ? undefined : Number(raw);
    if (nextValue !== undefined && Number.isNaN(nextValue)) return;

    setLegs((prev) => prev.map((leg) => (leg.id === id ? { ...leg, price: nextValue } : leg)));
  };

  const removeLeg = (id: string) => {
    setLegs((prev) => prev.filter((leg) => leg.id !== id));
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setSubmitError(null);
    setSubmitResult(null);

    if (legs.length < 2) {
      setSubmitError("Add at least two legs to create a multi-leg order.");
      return;
    }

    setSubmitting(true);

    try {
      const payload = {
        symbol,
        strategy,
        net_price: summary.netPremium,
        underlying_price: underlyingPrice ?? undefined,
        order_type: summary.orderType,
        notes: notes || undefined,
        metadata: {
          builder: "MultiLegOrderBuilder",
          sourceStrategy: selection?.strategy,
        },
        legs: legs.map((leg) => ({
          action: leg.action,
          option_type: leg.optionType,
          strike: leg.strike,
          expiration: leg.expiration,
          quantity: leg.quantity,
          price: leg.price,
          underlying_price: leg.underlyingPrice ?? underlyingPrice ?? undefined,
          implied_volatility: leg.impliedVolatility,
          metadata: leg.metadata ?? {},
        })),
      };

      const response = await fetch(`/api/proxy/options/multi-leg/orders`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const detail = await response.json().catch(() => ({}));
        throw new Error(detail.detail || `Order submission failed (${response.status})`);
      }

      const data: MultiLegOrderResponse = await response.json();
      setSubmitResult(data);
      onSubmitSuccess?.(data);
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : "Failed to submit order");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-4 rounded-xl border border-slate-700/60 bg-slate-900/60 p-4 text-slate-100 shadow-xl"
    >
      <header className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold tracking-wide text-emerald-300">
            Multi-Leg Order · {symbol.toUpperCase()}
          </h2>
          <p className="text-sm text-slate-400">Configure quantities, prices, and submit to backend for persistence.</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <label className="text-xs uppercase text-slate-400">Strategy</label>
          <select
            value={strategy}
            onChange={(event) => setStrategy(event.target.value as StrategyKey)}
            className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none"
          >
            {STRATEGY_OPTIONS.map((option) => (
              <option key={option.key} value={option.key}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </header>

      <div className="grid gap-4 md:grid-cols-[2fr,1fr]">
        <div className="overflow-hidden rounded-xl border border-slate-800/80">
          <table className="w-full border-collapse text-sm">
            <thead className="bg-slate-900/70 text-xs uppercase tracking-wide text-slate-400">
              <tr>
                <th className="px-3 py-2 text-left">Leg</th>
                <th className="px-3 py-2 text-left">Qty</th>
                <th className="px-3 py-2 text-left">Price</th>
                <th className="px-3 py-2 text-left">IV</th>
                <th className="px-3 py-2 text-left">Delta</th>
                <th className="px-3 py-2 text-left">Theta</th>
                <th className="px-3 py-2 text-left">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/70 bg-slate-900/30">
              {legs.length === 0 && (
                <tr>
                  <td colSpan={7} className="px-3 py-3 text-center text-sm text-slate-400">
                    No legs selected. Use the chain selector to add legs.
                  </td>
                </tr>
              )}
              {legs.map((leg) => (
                <tr key={leg.id}>
                  <td className="px-3 py-2">
                    <div className="flex flex-col">
                      <span className={`text-xs font-semibold ${leg.action === "BUY" ? "text-emerald-300" : "text-rose-300"}`}>
                        {leg.action}
                      </span>
                      <span className="text-slate-200">
                        {leg.optionType.toUpperCase()} {leg.strike.toFixed(2)} · {leg.expiration}
                      </span>
                    </div>
                  </td>
                  <td className="px-3 py-2">
                    <input
                      type="number"
                      min={1}
                      value={leg.quantity}
                      onChange={(event) => handleQuantityChange(leg.id, event)}
                      className="w-20 rounded border border-slate-700 bg-slate-900 px-2 py-1 text-sm text-slate-100 focus:border-emerald-500 focus:outline-none"
                    />
                  </td>
                  <td className="px-3 py-2">
                    <input
                      type="number"
                      step="0.01"
                      value={leg.price ?? ""}
                      onChange={(event) => handlePriceChange(leg.id, event)}
                      placeholder="Mid"
                      className="w-24 rounded border border-slate-700 bg-slate-900 px-2 py-1 text-sm text-slate-100 focus:border-emerald-500 focus:outline-none"
                    />
                  </td>
                  <td className="px-3 py-2 text-xs text-slate-400">{formatPercent(leg.impliedVolatility)}</td>
                  <td className="px-3 py-2 text-xs text-slate-400">{formatNumber(leg.greeks?.delta)}</td>
                  <td className="px-3 py-2 text-xs text-slate-400">{formatNumber(leg.greeks?.theta)}</td>
                  <td className="px-3 py-2 text-right">
                    <button
                      type="button"
                      onClick={() => removeLeg(leg.id)}
                      className="text-xs text-rose-300 hover:text-rose-200"
                    >
                      Remove
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <aside className="space-y-3 rounded-xl border border-slate-800/80 bg-slate-900/40 p-3">
          <div>
            <label className="text-xs uppercase text-slate-400">Underlying Price</label>
            <input
              type="number"
              step="0.01"
              value={underlyingPrice ?? ""}
              onChange={(event) => {
                if (event.target.value === "") {
                  setUnderlyingPrice(null);
                  return;
                }
                const next = Number(event.target.value);
                if (!Number.isNaN(next)) {
                  setUnderlyingPrice(next);
                }
              }}
              placeholder="e.g. 425.15"
              className="mt-1 w-full rounded border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 focus:border-emerald-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="text-xs uppercase text-slate-400">Notes</label>
            <textarea
              value={notes}
              onChange={(event) => setNotes(event.target.value)}
              rows={3}
              className="mt-1 w-full resize-none rounded border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 focus:border-emerald-500 focus:outline-none"
            />
          </div>

          <div className="rounded-lg border border-emerald-500/40 bg-emerald-500/10 p-3 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-slate-200">Net Premium</span>
              <span className="font-semibold text-emerald-200">{formatCurrency(summary.netPremium)}</span>
            </div>
            <div className="flex items-center justify-between text-slate-300">
              <span>Order Type</span>
              <span className="uppercase">{summary.orderType}</span>
            </div>
            <div className="flex items-center justify-between text-slate-300">
              <span>Total Contracts</span>
              <span>{summary.totalContracts}</span>
            </div>
            <div className="flex items-center justify-between text-slate-300">
              <span>Notional (×100)</span>
              <span>{formatCurrency(summary.notionals)}</span>
            </div>
          </div>

          <div className="rounded-lg border border-slate-800/70 bg-slate-900/60 p-3 text-xs text-slate-300">
            <h4 className="mb-2 text-slate-200">Aggregated Greeks</h4>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <span className="text-slate-400">Delta</span>
                <div className="font-semibold text-slate-200">{aggregatedGreeks.delta.toFixed(2)}</div>
              </div>
              <div>
                <span className="text-slate-400">Gamma</span>
                <div className="font-semibold text-slate-200">{aggregatedGreeks.gamma.toFixed(4)}</div>
              </div>
              <div>
                <span className="text-slate-400">Theta (per day)</span>
                <div className="font-semibold text-slate-200">{aggregatedGreeks.theta.toFixed(2)}</div>
              </div>
              <div>
                <span className="text-slate-400">Vega</span>
                <div className="font-semibold text-slate-200">{aggregatedGreeks.vega.toFixed(2)}</div>
              </div>
              <div>
                <span className="text-slate-400">Rho</span>
                <div className="font-semibold text-slate-200">{aggregatedGreeks.rho.toFixed(2)}</div>
              </div>
            </div>
          </div>
        </aside>
      </div>

      {submitError && (
        <div className="rounded-lg border border-red-500/40 bg-red-500/10 px-3 py-2 text-sm text-red-200">
          {submitError}
        </div>
      )}

      {submitResult && (
        <div className="space-y-3 rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-3 text-sm text-emerald-100">
          <div className="flex items-center justify-between">
            <span>Order saved (ID #{submitResult.id})</span>
            <span className="text-xs uppercase">Status: {submitResult.status}</span>
          </div>
          <div className="grid gap-2 text-slate-100">
            <div className="flex items-center justify-between">
              <span>Net Premium</span>
              <span>{formatCurrency(submitResult.net_price)}</span>
            </div>
            <div>
              <span className="text-slate-300">Submission Payload</span>
              <pre className="mt-1 max-h-48 overflow-auto rounded bg-slate-900/60 p-2 text-xs text-emerald-200">
                {JSON.stringify(submitResult.order_submission, null, 2)}
              </pre>
            </div>
          </div>
        </div>
      )}

      <div className="flex justify-end">
        <button
          type="submit"
          className="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 font-semibold text-white shadow hover:bg-emerald-500 disabled:cursor-not-allowed disabled:opacity-60"
          disabled={submitting}
        >
          {submitting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
          Persist Multi-Leg Order
        </button>
      </div>
    </form>
  );
}

function formatCurrency(value: number) {
  const formatted = Number.isFinite(value) ? value : 0;
  return `$${formatted.toFixed(2)}`;
}

function formatPercent(value?: number | null) {
  if (value === undefined || value === null) return "—";
  return `${(value * 100).toFixed(1)}%`;
}

function formatNumber(value?: number | null) {
  if (value === undefined || value === null) return "—";
  return value.toFixed(3);
}
