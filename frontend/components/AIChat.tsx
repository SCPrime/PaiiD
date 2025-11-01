/**
 * AI Chat Component
 * Reusable AI chat interface that can be triggered from anywhere in the app
 */

import { Brain, Loader2, Send, Sparkles, X } from "lucide-react";
import React, { useEffect, useRef, useState } from "react";
import { AIMessage, claudeAI } from "../lib/aiAdapter";
import { logger } from "../lib/logger";
import { cn, glassVariants } from "../lib/utils";

interface AIChatProps {
  isOpen: boolean;
  onClose: () => void;
  systemPrompt?: string;
  initialMessage?: string;
  onResponse?: (response: string) => void;
}

export function AIChat({
  isOpen,
  onClose,
  systemPrompt,
  initialMessage = "Hi! I'm your PaiiD AI assistant. I can help you with trading strategies, analyze market data, or adjust your preferences. What would you like to know?",
  onResponse,
}: AIChatProps) {
  const [messages, setMessages] = useState<AIMessage[]>([
    { role: "assistant", content: initialMessage },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Reset conversation when closed
  useEffect(() => {
    if (!isOpen) {
      claudeAI.resetConversation();
      setMessages([{ role: "assistant", content: initialMessage }]);
      setInput("");
    }
  }, [isOpen, initialMessage]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await claudeAI.chat(userMessage, systemPrompt);
      setMessages((prev) => [...prev, { role: "assistant", content: response }]);

      if (onResponse) {
        onResponse(response);
      }
    } catch (error) {
      logger.error("[AIChat] Error", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "I'm sorry, I encountered an error. Please try again.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 backdrop-blur-lg"
      onClick={onClose}
    >
      <div
        className="relative w-full max-w-2xl max-h-[80vh] mx-4"
        onClick={(e) => e.stopPropagation()}
      >
        <div
          className={cn(
            glassVariants.dialog,
            "flex flex-col h-[600px] overflow-hidden p-0 shadow-[0_25px_50px_-12px_rgba(22,163,148,0.35)]"
          )}
        >
          {/* Header */}
          <div className="px-6 py-4 border-b border-teal-500/20 bg-gradient-to-r from-[#16a394] via-[#00ACC1] to-[#7E57C2]">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="relative">
                  <Brain className="w-6 h-6 text-slate-100" />
                  <Sparkles className="absolute -top-1 -right-1 w-3 h-3 text-[#45f0c0]" />
                </div>
                <div>
                  <h2 className="text-lg font-semibold text-slate-100">PaiiD AI Assistant</h2>
                  <p className="text-xs text-slate-100/80">Powered by Claude Sonnet 4.5</p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="p-2 rounded-lg hover:bg-slate-100/15 transition-colors"
              >
                <X className="w-5 h-5 text-slate-100" />
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-slate-900/50">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={cn(
                    "max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap shadow-lg",
                    msg.role === "user"
                      ? "bg-gradient-to-r from-[#16a394] via-[#00ACC1] to-[#7E57C2] text-slate-100 shadow-[0_8px_20px_rgba(126,87,194,0.25)]"
                      : "bg-slate-900/70 text-slate-200 border border-teal-500/20 backdrop-blur-md shadow-[0_4px_16px_rgba(15,24,40,0.45)]"
                  )}
                >
                  <p>{msg.content}</p>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="rounded-2xl border border-teal-500/20 bg-slate-900/70 px-4 py-3 backdrop-blur-md">
                  <Loader2 className="w-5 h-5 animate-spin text-[#7E57C2]" />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="p-4 border-t border-teal-500/20 bg-slate-950/60 backdrop-blur-lg">
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask anything about trading..."
                disabled={isLoading}
                className={cn(
                  glassVariants.input,
                  "flex-1 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-400 shadow-[0_2px_12px_rgba(15,24,40,0.45)] focus:outline-none focus:ring-2 focus:ring-[#16a394] disabled:opacity-50"
                )}
              />
              <button
                onClick={handleSend}
                disabled={!input.trim() || isLoading}
                className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-[#16a394] via-[#00ACC1] to-[#7E57C2] px-6 py-3 font-semibold text-slate-100 shadow-[0_10px_30px_rgba(22,163,148,0.35)] transition-all hover:shadow-[0_12px_32px_rgba(126,87,194,0.35)] disabled:cursor-not-allowed disabled:opacity-50"
              >
                {isLoading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * AI Chat Trigger Button
 * Click the "ai" in "PaiiD" logo to open chat
 */
interface AILogoTriggerProps {
  onClick: () => void;
}

export function AILogoTrigger({ onClick }: AILogoTriggerProps) {
  return (
    <div className="flex flex-col select-none">
      <div className="flex items-center gap-1 text-2xl font-bold">
        <span className="text-[#00ACC1]">P</span>
        <span
          className="relative cursor-pointer text-[#7E57C2] transition-transform hover:scale-110 group"
          onClick={onClick}
        >
          ai
          <Sparkles className="absolute -top-1 -right-1 w-3 h-3 text-[#45f0c0] opacity-0 transition-opacity group-hover:opacity-100" />
        </span>
        <span className="text-[#00ACC1]">D</span>
      </div>
      <div className="mt-0.5 text-xs text-slate-300">
        Personal Artificial Intelligence Dashboard
      </div>
      <div className="text-[10px] text-slate-400">10 Stage Workflow</div>
    </div>
  );
}

export default AIChat;
