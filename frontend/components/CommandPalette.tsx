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
      {/* Backdrop */}
      <div
        style={{
          position: "fixed",
          inset: 0,
          zIndex: 9999,
          background: "rgba(0, 0, 0, 0.7)",
          backdropFilter: "blur(4px)",
        }}
        onClick={() => setIsOpen(false)}
      />

      {/* Command Palette */}
      <div
        style={{
          position: "fixed",
          top: "20%",
          left: "50%",
          transform: "translateX(-50%)",
          zIndex: 10000,
          width: "90%",
          maxWidth: "600px",
          background: "rgba(15, 23, 42, 0.95)",
          border: "1px solid rgba(71, 85, 105, 0.5)",
          borderRadius: "16px",
          boxShadow: "0 24px 48px rgba(0, 0, 0, 0.5)",
          backdropFilter: "blur(20px)",
          overflow: "hidden",
        }}
      >
        {/* Search Input */}
        <div
          style={{
            padding: "20px",
            borderBottom: "1px solid rgba(71, 85, 105, 0.3)",
            display: "flex",
            alignItems: "center",
            gap: "12px",
          }}
        >
          <Search size={20} color="#94a3b8" />
          <input
            type="text"
            placeholder="Search commands..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            autoFocus
            style={{
              flex: 1,
              background: "transparent",
              border: "none",
              outline: "none",
              color: "#fff",
              fontSize: "16px",
              fontFamily: "inherit",
            }}
          />
          <kbd
            style={{
              padding: "4px 8px",
              background: "rgba(51, 65, 85, 0.6)",
              borderRadius: "4px",
              fontSize: "12px",
              color: "#94a3b8",
              border: "1px solid rgba(71, 85, 105, 0.3)",
            }}
          >
            ESC
          </kbd>
        </div>

        {/* Command List */}
        <div
          style={{
            maxHeight: "400px",
            overflowY: "auto",
            padding: "8px",
          }}
        >
          {filteredCommands.length === 0 ? (
            <div
              style={{
                padding: "40px",
                textAlign: "center",
                color: "#64748b",
                fontSize: "14px",
              }}
            >
              No commands found
            </div>
          ) : (
            filteredCommands.map((cmd, idx) => {
              const Icon = cmd.icon;
              const isSelected = idx === selectedIndex;

              return (
                <div
                  key={cmd.id}
                  onClick={() => {
                    cmd.action();
                    setIsOpen(false);
                    setSearch("");
                  }}
                  onMouseEnter={() => setSelectedIndex(idx)}
                  style={{
                    padding: "12px 16px",
                    borderRadius: "8px",
                    background: isSelected ? "rgba(16, 185, 129, 0.15)" : "transparent",
                    border: isSelected
                      ? "1px solid rgba(16, 185, 129, 0.3)"
                      : "1px solid transparent",
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    gap: "12px",
                    marginBottom: "4px",
                    transition: "all 0.15s ease",
                  }}
                >
                  <div
                    style={{
                      width: "40px",
                      height: "40px",
                      borderRadius: "8px",
                      background: isSelected ? "rgba(16, 185, 129, 0.2)" : "rgba(51, 65, 85, 0.4)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                    }}
                  >
                    <Icon size={20} color={isSelected ? "#10b981" : "#94a3b8"} />
                  </div>
                  <div style={{ flex: 1 }}>
                    <div
                      style={{
                        fontSize: "14px",
                        fontWeight: 600,
                        color: isSelected ? "#10b981" : "#fff",
                        marginBottom: "2px",
                      }}
                    >
                      {cmd.label}
                    </div>
                    <div
                      style={{
                        fontSize: "12px",
                        color: "#94a3b8",
                      }}
                    >
                      {cmd.description}
                    </div>
                  </div>
                  {isSelected && (
                    <kbd
                      style={{
                        padding: "4px 8px",
                        background: "rgba(16, 185, 129, 0.2)",
                        borderRadius: "4px",
                        fontSize: "11px",
                        color: "#10b981",
                        border: "1px solid rgba(16, 185, 129, 0.3)",
                      }}
                    >
                      ↵
                    </kbd>
                  )}
                </div>
              );
            })
          )}
        </div>

        {/* Footer */}
        <div
          style={{
            padding: "12px 20px",
            borderTop: "1px solid rgba(71, 85, 105, 0.3)",
            display: "flex",
            gap: "16px",
            fontSize: "12px",
            color: "#64748b",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <kbd
              style={{
                padding: "2px 6px",
                background: "rgba(51, 65, 85, 0.4)",
                borderRadius: "3px",
                fontSize: "11px",
                border: "1px solid rgba(71, 85, 105, 0.3)",
              }}
            >
              ↑↓
            </kbd>
            Navigate
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <kbd
              style={{
                padding: "2px 6px",
                background: "rgba(51, 65, 85, 0.4)",
                borderRadius: "3px",
                fontSize: "11px",
                border: "1px solid rgba(71, 85, 105, 0.3)",
              }}
            >
              ↵
            </kbd>
            Select
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <kbd
              style={{
                padding: "2px 6px",
                background: "rgba(51, 65, 85, 0.4)",
                borderRadius: "3px",
                fontSize: "11px",
                border: "1px solid rgba(71, 85, 105, 0.3)",
              }}
            >
              ESC
            </kbd>
            Close
          </div>
        </div>
      </div>
    </>
  );
};

export default CommandPalette;
