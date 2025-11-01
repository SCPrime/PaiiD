import { useEffect, useState } from "react";
import { Badge } from "./ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";

interface ExecutionRecord {
  id: number;
  user_id: number;
  strategy_type: string;
  market_key: string;
  trade_summary: {
    counts: {
      total: number;
      buy_call: number;
      sell_put: number;
      buy_token: number;
    };
    options: {
      collateral_required: number;
      premium_estimate_usd: number;
    };
    dex: {
      usd_allocation: number;
      tokens: string[];
    };
  };
  execution_summary: {
    status_counts: Record<string, number>;
    options: {
      collateral_committed: number;
      premium_spent_usd: number;
    };
    dex: {
      usd_allocation: number;
      tokens: string[];
    };
  };
  timestamp: string;
}

export default function ExecutionHistoryDashboard() {
  const [history, setHistory] = useState<ExecutionRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      const response = await fetch("/api/proxy/api/strategies/execution-history?limit=50");

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      setHistory(data.history || []);
    } catch (err) {
      console.error("Failed to fetch execution history:", err);
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadgeVariant = (
    status: string
  ): "default" | "success" | "destructive" | "warning" | "secondary" => {
    if (status === "submitted" || status === "completed") return "success";
    if (status === "error" || status === "failed") return "destructive";
    if (status === "pending_signature" || status === "manual_required") return "warning";
    return "secondary";
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-slate-400">Loading execution history...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-red-950/50 border border-red-500/30 rounded-xl">
        <p className="text-red-400 font-semibold">Failed to load execution history</p>
        <p className="text-sm text-slate-400 mt-1">{error}</p>
        <button
          onClick={fetchHistory}
          className="mt-4 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md text-sm font-semibold transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  if (history.length === 0) {
    return (
      <div className="p-8 text-center">
        <p className="text-slate-400">No strategy executions yet.</p>
        <p className="text-sm text-slate-500 mt-2">
          Run a strategy to see execution history appear here.
        </p>
      </div>
    );
  }

  return (
    <div className="p-6 bg-slate-800/80 backdrop-blur-md border border-white/10 rounded-xl">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-slate-100 mb-2">Strategy Execution History</h2>
        <p className="text-sm text-slate-400">
          Recent automated strategy runs with trade summaries
        </p>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Timestamp</TableHead>
            <TableHead>Strategy</TableHead>
            <TableHead>Market</TableHead>
            <TableHead>Trades</TableHead>
            <TableHead>Options</TableHead>
            <TableHead>DEX</TableHead>
            <TableHead>Status</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {history.map((record) => {
            const summary = record.trade_summary;
            const execution = record.execution_summary;
            const statusEntries = Object.entries(execution.status_counts);

            return (
              <TableRow key={record.id}>
                <TableCell className="font-mono text-xs">
                  {formatTimestamp(record.timestamp)}
                </TableCell>
                <TableCell>
                  <div className="font-semibold text-teal-400">{record.strategy_type}</div>
                </TableCell>
                <TableCell>
                  <Badge variant="secondary">{record.market_key}</Badge>
                </TableCell>
                <TableCell>
                  <div className="text-sm">
                    <div>Total: {summary.counts.total}</div>
                    {summary.counts.buy_call > 0 && (
                      <div className="text-xs text-slate-400">Calls: {summary.counts.buy_call}</div>
                    )}
                    {summary.counts.sell_put > 0 && (
                      <div className="text-xs text-slate-400">Puts: {summary.counts.sell_put}</div>
                    )}
                    {summary.counts.buy_token > 0 && (
                      <div className="text-xs text-slate-400">
                        Tokens: {summary.counts.buy_token}
                      </div>
                    )}
                  </div>
                </TableCell>
                <TableCell>
                  {execution.options.collateral_committed > 0 && (
                    <div className="text-sm">
                      <div className="text-slate-300">
                        ${execution.options.collateral_committed.toLocaleString()}
                      </div>
                      <div className="text-xs text-slate-500">collateral</div>
                    </div>
                  )}
                  {execution.options.premium_spent_usd > 0 && (
                    <div className="text-sm">
                      <div className="text-slate-300">
                        ${execution.options.premium_spent_usd.toLocaleString()}
                      </div>
                      <div className="text-xs text-slate-500">premium</div>
                    </div>
                  )}
                  {execution.options.collateral_committed === 0 &&
                    execution.options.premium_spent_usd === 0 && (
                      <div className="text-xs text-slate-500">—</div>
                    )}
                </TableCell>
                <TableCell>
                  {execution.dex.usd_allocation > 0 ? (
                    <div className="text-sm">
                      <div className="text-slate-300">
                        ${execution.dex.usd_allocation.toLocaleString()}
                      </div>
                      <div className="text-xs text-slate-500">
                        {execution.dex.tokens.length} token(s)
                      </div>
                    </div>
                  ) : (
                    <div className="text-xs text-slate-500">—</div>
                  )}
                </TableCell>
                <TableCell>
                  <div className="flex flex-wrap gap-1">
                    {statusEntries.map(([status, count]) => (
                      <Badge key={status} variant={getStatusBadgeVariant(status)}>
                        {status}: {count}
                      </Badge>
                    ))}
                  </div>
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>

      <div className="mt-4 text-xs text-slate-500 text-right">
        Showing last {history.length} execution(s)
      </div>
    </div>
  );
}
