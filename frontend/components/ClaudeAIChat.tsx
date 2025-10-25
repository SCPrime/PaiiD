"use client";

import { Bot, Loader, Send, Sparkles, User } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { useIsMobile } from "../hooks/useBreakpoint";
import { showError } from "../lib/toast";
import { theme } from "../styles/theme";
import { Button, Card } from "./ui";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export default function ClaudeAIChat() {
  const isMobile = useIsMobile();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "👋 Hi! I'm your AI trading assistant powered by Claude. Ask me anything about:\n\n• Market regime analysis\n• Chart patterns\n• Strategy recommendations\n• Technical indicators\n• Trading concepts\n\nTry asking: \"What's the current market regime for AAPL?\"",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      // Check if query is about market regime
      if (
        input.toLowerCase().includes("market regime") ||
        input.toLowerCase().includes("regime for")
      ) {
        const symbolMatch = input.match(/\b([A-Z]{1,5})\b/);
        const symbol = symbolMatch ? symbolMatch[1] : "SPY";

        // Fetch ML market regime
        const res = await fetch(`/api/proxy/api/ml/market-regime?symbol=${symbol}`);
        if (res.ok) {
          const data = await res.json();
          const assistantMessage: Message = {
            id: (Date.now() + 1).toString(),
            role: "assistant",
            content: `📊 **Market Regime for ${data.symbol}:**\n\n**${data.regime.replace(/_/g, " ").toUpperCase()}** (${(data.confidence * 100).toFixed(0)}% confidence)\n\n**Key Metrics:**\n• RSI: ${data.features.rsi.toFixed(1)}\n• Volatility: ${(data.features.volatility * 100).toFixed(1)}%\n• Trend Strength: ${data.features.trend_strength.toFixed(1)}\n\n**Recommended Strategies:**\n${data.recommended_strategies.map((s: string) => `• ${s.replace(/-/g, " ")}`).join("\n")}`,
            timestamp: new Date(),
          };
          setMessages((prev) => [...prev, assistantMessage]);
          setIsLoading(false);
          return;
        }
      }

      // Check if query is about patterns
      if (input.toLowerCase().includes("pattern") || input.toLowerCase().includes("chart")) {
        const symbolMatch = input.match(/\b([A-Z]{1,5})\b/);
        const symbol = symbolMatch ? symbolMatch[1] : "SPY";

        const res = await fetch(
          `/api/proxy/api/ml/detect-patterns?symbol=${symbol}&min_confidence=0.7`
        );
        if (res.ok) {
          const data = await res.json();
          if (data.patterns.length > 0) {
            const patternList = data.patterns
              .map(
                (p: unknown) =>
                  `• **${(p as any).pattern_type.replace(/_/g, " ").toUpperCase()}** (${(p as any).signal}) - ${((p as any).confidence * 100).toFixed(0)}% confidence\n  Target: $${(p as any).target_price.toFixed(2)} | Stop: $${(p as any).stop_loss.toFixed(2)}`
              )
              .join("\n\n");
            const assistantMessage: Message = {
              id: (Date.now() + 1).toString(),
              role: "assistant",
              content: `📊 **Patterns Detected for ${data.symbol}:**\n\n${patternList}`,
              timestamp: new Date(),
            };
            setMessages((prev) => [...prev, assistantMessage]);
            setIsLoading(false);
            return;
          } else {
            const assistantMessage: Message = {
              id: (Date.now() + 1).toString(),
              role: "assistant",
              content: `No high-confidence patterns detected for ${symbol} at the moment. Try asking about a different symbol or lower the confidence threshold.`,
              timestamp: new Date(),
            };
            setMessages((prev) => [...prev, assistantMessage]);
            setIsLoading(false);
            return;
          }
        }
      }

      // Check if query is about strategy recommendations
      if (input.toLowerCase().includes("strategy") || input.toLowerCase().includes("recommend")) {
        const symbolMatch = input.match(/\b([A-Z]{1,5})\b/);
        const symbol = symbolMatch ? symbolMatch[1] : "SPY";

        const res = await fetch(`/api/proxy/api/ml/recommend-strategy?symbol=${symbol}&top_n=3`);
        if (res.ok) {
          const data = await res.json();
          const strategyList = data.recommendations
            .map(
              (r: unknown, idx: number) =>
                `${idx + 1}. **${r.strategy_id.replace(/-/g, " ").toUpperCase()}** - ${(r.probability * 100).toFixed(0)}% probability`
            )
            .join("\n");
          const assistantMessage: Message = {
            id: (Date.now() + 1).toString(),
            role: "assistant",
            content: `🎯 **Strategy Recommendations for ${data.symbol}:**\n\nMarket is currently **${data.market_regime.replace(/_/g, " ").toUpperCase()}** (${(data.regime_confidence * 100).toFixed(0)}% confidence)\n\n**Top Strategies:**\n${strategyList}`,
            timestamp: new Date(),
          };
          setMessages((prev) => [...prev, assistantMessage]);
          setIsLoading(false);
          return;
        }
      }

      // Fallback: Use Claude API directly
      const res = await fetch("/api/proxy/api/claude/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: [
            {
              role: "system",
              content:
                "You are an expert trading assistant. Help users with market analysis, strategy recommendations, and trading concepts. Keep responses concise and actionable. When users ask about specific stocks, guide them to use the ML features: market regime detection, pattern recognition, and strategy recommendations.",
            },
            { role: "user", content: input },
          ],
        }),
      });

      if (!res.ok) {
        throw new Error("AI response failed");
      }

      const data = await res.json();
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content:
          data.response ||
          data.content ||
          "I'm having trouble responding right now. Please try asking about market regime, patterns, or strategy recommendations for specific symbols (e.g., 'What's the market regime for AAPL?')",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: unknown) {
      showError("Failed to get AI response");
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content:
          "Sorry, I encountered an error. Try asking about:\n• Market regime for a symbol\n• Patterns in a stock\n• Strategy recommendations\n\nExample: 'What patterns do you see in AAPL?'",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const quickQuestions = [
    "What's the market regime for SPY?",
    "Show me patterns in AAPL",
    "Recommend strategies for TSLA",
    "What does RSI mean?",
  ];

  return (
    <div style={{ padding: isMobile ? theme.spacing.md : theme.spacing.lg }}>
      {/* Header */}
      <div style={{ marginBottom: theme.spacing.lg }}>
        <h2
          style={{
            margin: 0,
            fontSize: isMobile ? "24px" : "32px",
            fontWeight: "700",
            color: theme.colors.text,
            textShadow: theme.glow.cyan,
            marginBottom: theme.spacing.xs,
            display: "flex",
            alignItems: "center",
            gap: theme.spacing.sm,
          }}
        >
          <Sparkles size={32} color={theme.colors.secondary} />
          Claude AI Trading Assistant
        </h2>
        <p
          style={{
            margin: 0,
            fontSize: "14px",
            color: theme.colors.textMuted,
          }}
        >
          Ask questions in natural language - powered by Claude AI
        </p>
      </div>

      {/* Chat Container */}
      <Card glow="cyan" style={{ marginBottom: theme.spacing.lg }}>
        {/* Messages */}
        <div
          style={{
            height: isMobile ? "400px" : "500px",
            overflowY: "auto",
            padding: theme.spacing.md,
            marginBottom: theme.spacing.lg,
          }}
        >
          {messages.map((msg) => (
            <div
              key={msg.id}
              style={{
                display: "flex",
                gap: theme.spacing.md,
                marginBottom: theme.spacing.lg,
                alignItems: "flex-start",
              }}
            >
              {/* Avatar */}
              <div
                style={{
                  flexShrink: 0,
                  width: "40px",
                  height: "40px",
                  borderRadius: "50%",
                  background:
                    msg.role === "assistant"
                      ? `linear-gradient(135deg, ${theme.colors.secondary}, ${theme.colors.primary})`
                      : `linear-gradient(135deg, ${theme.colors.primary}, ${theme.colors.secondary})`,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  boxShadow: msg.role === "assistant" ? theme.glow.cyan : theme.glow.green,
                }}
              >
                {msg.role === "assistant" ? (
                  <Bot size={20} color="white" />
                ) : (
                  <User size={20} color="white" />
                )}
              </div>

              {/* Message Content */}
              <div style={{ flex: 1 }}>
                <div
                  style={{
                    fontSize: "12px",
                    color: theme.colors.textMuted,
                    marginBottom: theme.spacing.xs,
                  }}
                >
                  {msg.role === "assistant" ? "Claude AI" : "You"} •{" "}
                  {msg.timestamp.toLocaleTimeString()}
                </div>
                <div
                  style={{
                    fontSize: "14px",
                    color: theme.colors.text,
                    lineHeight: "1.6",
                    whiteSpace: "pre-wrap",
                    wordBreak: "break-word",
                  }}
                >
                  {msg.content}
                </div>
              </div>
            </div>
          ))}

          {isLoading && (
            <div
              style={{
                display: "flex",
                gap: theme.spacing.md,
                alignItems: "center",
              }}
            >
              <div
                style={{
                  width: "40px",
                  height: "40px",
                  borderRadius: "50%",
                  background: `linear-gradient(135deg, ${theme.colors.secondary}, ${theme.colors.primary})`,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  boxShadow: theme.glow.cyan,
                }}
              >
                <Loader size={20} color="white" className="animate-spin" />
              </div>
              <div style={{ fontSize: "14px", color: theme.colors.textMuted }}>
                Claude is thinking...
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Quick Questions */}
        {messages.length === 1 && (
          <div style={{ marginBottom: theme.spacing.lg }}>
            <div
              style={{
                fontSize: "12px",
                color: theme.colors.textMuted,
                marginBottom: theme.spacing.sm,
                textTransform: "uppercase",
                letterSpacing: "0.5px",
              }}
            >
              Quick Questions:
            </div>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: isMobile ? "1fr" : "repeat(2, 1fr)",
                gap: theme.spacing.sm,
              }}
            >
              {quickQuestions.map((q, idx) => (
                <button
                  key={idx}
                  onClick={() => setInput(q)}
                  style={{
                    padding: theme.spacing.sm,
                    background: "rgba(6, 182, 212, 0.1)",
                    border: `1px solid ${theme.colors.secondary}`,
                    borderRadius: theme.borderRadius.md,
                    color: theme.colors.text,
                    fontSize: "13px",
                    cursor: "pointer",
                    textAlign: "left",
                    transition: "all 0.2s",
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = "rgba(6, 182, 212, 0.2)";
                    e.currentTarget.style.borderColor = theme.colors.secondary;
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = "rgba(6, 182, 212, 0.1)";
                    e.currentTarget.style.borderColor = theme.colors.secondary;
                  }}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input Area */}
        <div style={{ display: "flex", gap: theme.spacing.sm }}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading}
            placeholder="Ask about market regime, patterns, strategies..."
            style={{
              flex: 1,
              padding: "12px 16px",
              background: "rgba(15, 23, 42, 0.5)",
              border: `1px solid ${theme.colors.border}`,
              borderRadius: theme.borderRadius.md,
              color: theme.colors.text,
              fontSize: "14px",
            }}
          />
          <Button
            onClick={sendMessage}
            loading={isLoading}
            disabled={!input.trim() || isLoading}
            variant="primary"
          >
            <Send size={18} />
          </Button>
        </div>
      </Card>
    </div>
  );
}
