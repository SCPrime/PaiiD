/**
 * Command Palette Component
 *
 * Keyboard-driven command palette for quick actions (Cmd+K / Ctrl+K).
 *
 * Phase 4B: UX Polish - Command Palette
 */

import {
  Activity,
  BarChart3,
  Brain,
  CreditCard,
  MessageSquare,
  Newspaper,
  Search,
  Settings,
  Target,
  TrendingUp,
} from "lucide-react";
import React, { useCallback, useEffect, useState } from "react";

import { cn, glassVariants } from "../lib/utils";

interface Command {
  id: string;
  label: string;
  description: string;
  icon: React.ElementType;
  action: () => void;
  keywords?: string[];
}

interface CommandPaletteProps {
  onNavigate: (section: string) => void;
}

const CommandPalette: React.FC<CommandPaletteProps> = ({ onNavigate }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);

  const commands: Command[] = [
    {
      id: "positions",
      label: "View Positions",
      description: "See active trading positions",
      icon: TrendingUp,
      action: () => onNavigate("positions"),
      keywords: ["trade", "portfolio", "holdings"],
    },
    {
      id: "execute",
      label: "Execute Trade",
      description: "Place a new order",
      icon: Target,
      action: () => onNavigate("execute"),
      keywords: ["buy", "sell", "order", "trade"],
    },
    {
      id: "analytics",
      label: "Analytics Dashboard",
      description: "View P&L and performance",
      icon: BarChart3,
      action: () => onNavigate("analytics"),
      keywords: ["pnl", "profit", "loss", "performance", "metrics"],
    },
    {
      id: "ml-training",
      label: "ML Training",
      description: "Train machine learning models",
      icon: Brain,
      action: () => onNavigate("ml-training"),
      keywords: ["ai", "machine learning", "model", "train"],
    },
    {
      id: "ml-analytics",
      label: "ML Analytics",
      description: "View ML model performance",
      icon: Activity,
      action: () => onNavigate("ml-analytics"),
      keywords: ["ai", "accuracy", "predictions"],
    },
    {
      id: "portfolio-optimizer",
      label: "Portfolio Optimizer",
      description: "Optimize portfolio allocation",
      icon: Target,
      action: () => onNavigate("portfolio-optimizer"),
      keywords: ["optimize", "allocation", "rebalance"],
    },
    {
      id: "news",
      label: "News Sentiment",
      description: "Analyze market sentiment",
      icon: Newspaper,
      action: () => onNavigate("news"),
      keywords: ["sentiment", "headlines", "analysis"],
    },
    {
      id: "ai-chat",
      label: "AI Chat",
      description: "Chat with Claude AI",
      icon: MessageSquare,
      action: () => onNavigate("ai-chat"),
      keywords: ["claude", "assistant", "help", "chat"],
    },
    {
      id: "subscription",
      label: "Subscription & Billing",
      description: "Manage subscription",
      icon: CreditCard,
      action: () => onNavigate("subscription"),
      keywords: ["billing", "payment", "upgrade", "plan"],
    },
    {
      id: "settings",
      label: "Settings",
      description: "Configure application",
      icon: Settings,
      action: () => onNavigate("settings"),
      keywords: ["preferences", "config", "options"],
    },
  ];

  const filteredCommands = commands.filter((cmd) => {
    const searchLower = search.toLowerCase();
    return (
      cmd.label.toLowerCase().includes(searchLower) ||
      cmd.description.toLowerCase().includes(searchLower) ||
      cmd.keywords?.some((k) => k.includes(searchLower))
    );
  });

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      // Open with Cmd+K or Ctrl+K
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setIsOpen((prev) => !prev);
        setSearch("");
        setSelectedIndex(0);
      }

      // Close with Escape
      if (e.key === "Escape") {
        setIsOpen(false);
      }

      if (!isOpen) return;

      // Navigate with arrow keys
      if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedIndex((prev) => Math.min(prev + 1, filteredCommands.length - 1));
      }

      if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedIndex((prev) => Math.max(prev - 1, 0));
      }

      // Execute with Enter
      if (e.key === "Enter" && filteredCommands[selectedIndex]) {
        e.preventDefault();
        filteredCommands[selectedIndex].action();
        setIsOpen(false);
        setSearch("");
      }
    },
    [isOpen, filteredCommands, selectedIndex]
  );

  useEffect(() => {
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);

  useEffect(() => {
    // Reset selection when search changes
    setSelectedIndex(0);
  }, [search]);

  if (!isOpen) return null;

  return (
    <>
      <div
        className="fixed inset-0 z-[9999] bg-slate-950/70 backdrop-blur-sm"
        onClick={() => setIsOpen(false)}
      />

      <div
        className={cn(
          glassVariants.dialog,
          "fixed top-[20%] left-1/2 z-[10000] w-[90%] max-w-xl -translate-x-1/2 overflow-hidden border border-teal-500/20 shadow-[0_30px_80px_-20px_rgba(15,24,40,0.75)]"
        )}
      >
        <div className="flex items-center gap-3 border-b border-slate-500/30 bg-slate-900/70 px-6 py-5">
          <Search className="h-5 w-5 text-slate-400" />
          <input
            type="text"
            placeholder="Search commands..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            autoFocus
            className="flex-1 bg-transparent text-base text-slate-100 placeholder-slate-500 focus:outline-none"
          />
          <kbd className="rounded-md border border-slate-500/40 bg-slate-800/60 px-2 py-1 text-xs font-medium text-slate-300">
            ESC
          </kbd>
        </div>

        <div className="max-h-[420px] overflow-y-auto px-3 py-2">
          {filteredCommands.length === 0 ? (
            <div className="px-8 py-12 text-center text-sm text-slate-400">No commands found</div>
          ) : (
            filteredCommands.map((cmd, idx) => {
              const Icon = cmd.icon;
              const isSelected = idx === selectedIndex;

              return (
                <button
                  type="button"
                  key={cmd.id}
                  onClick={() => {
                    cmd.action();
                    setIsOpen(false);
                    setSearch("");
                  }}
                  onMouseEnter={() => setSelectedIndex(idx)}
                  className={cn(
                    "group flex w-full items-center gap-3 rounded-xl border px-4 py-3 text-left transition",
                    isSelected
                      ? "border-[#16a394]/40 bg-[#16a394]/10 shadow-[0_10px_25px_-12px_rgba(22,163,148,0.6)]"
                      : "border-transparent bg-transparent hover:border-[#16a394]/25 hover:bg-[#16a394]/5"
                  )}
                >
                  <span
                    className={cn(
                      "flex h-10 w-10 items-center justify-center rounded-xl border",
                      isSelected
                        ? "border-[#16a394]/40 bg-[#16a394]/20"
                        : "border-slate-600/40 bg-slate-900/60"
                    )}
                  >
                    <Icon
                      className={cn("h-5 w-5", isSelected ? "text-[#16a394]" : "text-slate-400")}
                    />
                  </span>
                  <span className="flex-1">
                    <span
                      className={cn(
                        "block text-sm font-semibold",
                        isSelected ? "text-[#16a394]" : "text-slate-100"
                      )}
                    >
                      {cmd.label}
                    </span>
                    <span className="block text-xs text-slate-400">{cmd.description}</span>
                  </span>
                  {isSelected && (
                    <kbd className="rounded-md border border-[#16a394]/30 bg-[#16a394]/20 px-2 py-1 text-[11px] font-medium text-[#16a394]">
                      ↵
                    </kbd>
                  )}
                </button>
              );
            })
          )}
        </div>

        <div className="flex gap-4 border-t border-slate-500/30 bg-slate-900/70 px-6 py-3 text-[11px] text-slate-400">
          <span className="flex items-center gap-2">
            <kbd className="rounded border border-slate-500/40 bg-slate-800/60 px-1.5 py-0.5">
              ↑↓
            </kbd>
            Navigate
          </span>
          <span className="flex items-center gap-2">
            <kbd className="rounded border border-slate-500/40 bg-slate-800/60 px-1.5 py-0.5">
              ↵
            </kbd>
            Select
          </span>
          <span className="flex items-center gap-2">
            <kbd className="rounded border border-slate-500/40 bg-slate-800/60 px-1.5 py-0.5">
              ESC
            </kbd>
            Close
          </span>
        </div>
      </div>
    </>
  );
};

export default CommandPalette;
