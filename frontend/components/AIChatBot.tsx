"use client";

import { useEffect, useRef, useState } from "react";

import { cn, glassVariants } from "../lib/utils";

interface AIChatBotProps {
  isOpen: boolean;
  onClose: () => void;
}

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export default function AIChatBot({ isOpen, onClose }: AIChatBotProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content: "Hello! I'm PaiiD, your personal trading assistant. How can I help you today?",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsTyping(true);

    setTimeout(() => {
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content:
          "I'm processing your request. This is a demo response. In production, this would connect to Claude API.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMessage]);
      setIsTyping(false);
    }, 1500);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (!isOpen) {
    return null;
  }

  return (
    <>
      <div
        className="fixed inset-0 z-[990] bg-slate-950/70 backdrop-blur-md transition-opacity"
        onClick={onClose}
      />

      <div className="fixed inset-x-0 bottom-0 z-[1000] flex justify-center px-4 pb-4">
        <div
          className={cn(
            glassVariants.dialog,
            "flex h-[40vh] w-full max-w-4xl flex-col border-t-2 border-[#45f0c0]/40 p-0 shadow-[0_-18px_45px_-18px_rgba(69,240,192,0.45)]"
          )}
        >
          <header className="flex items-center justify-between border-b border-[#45f0c0]/25 bg-gradient-to-r from-[#16a394]/70 via-[#00ACC1]/70 to-[#7E57C2]/70 px-6 py-4">
            <div className="flex items-center gap-3">
              <span className="h-3 w-3 rounded-full bg-[#45f0c0] shadow-[0_0_12px_rgba(69,240,192,0.85)]" />
              <span className="text-lg font-semibold italic text-[#f1f5f9]">
                Pa
                <span className="text-[#45f0c0] drop-shadow-[0_0_8px_rgba(69,240,192,0.5)]">
                  ii
                </span>
                D Assistant
              </span>
            </div>
            <button
              onClick={onClose}
              className="rounded-lg px-2 py-1 text-xl text-[#cbd5e1] transition hover:bg-white/10 hover:text-[#f1f5f9]"
            >
              ×
            </button>
          </header>

          <div className="flex-1 space-y-4 overflow-y-auto px-6 py-5">
            {messages.map((message) => (
              <div
                key={message.id}
                className={cn("flex", message.role === "user" ? "justify-end" : "justify-start")}
              >
                <div
                  className={cn(
                    "max-w-[70%] rounded-2xl border px-4 py-3 text-sm leading-relaxed text-[#e2e8f0] shadow-lg",
                    message.role === "user"
                      ? "border-[#45f0c0]/40 bg-[#45f0c0]/20"
                      : "border-[#94a3b8]/30 bg-[#1a2a3f]/85"
                  )}
                >
                  <div>{message.content}</div>
                  <div
                    className="mt-2 text-[11px] font-medium text-[#94a3b8]"
                    suppressHydrationWarning
                  >
                    {message.timestamp.toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))}

            {isTyping && (
              <div className="flex items-center gap-2 px-2">
                {[0, 0.18, 0.36].map((delay, index) => (
                  <span
                    // eslint-disable-next-line react/no-array-index-key
                    key={index}
                    className="h-2 w-2 rounded-full bg-[#45f0c0]"
                    style={{
                      animation: "ai-chat-bounce 1.2s infinite ease-in-out",
                      animationDelay: `${delay}s`,
                    }}
                  />
                ))}
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          <footer className="flex gap-3 border-t border-[#45f0c0]/25 px-6 py-4">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about trading..."
              className={cn(
                glassVariants.input,
                "flex-1 rounded-xl border border-[#45f0c0]/30 bg-transparent px-4 py-3 text-sm text-[#e2e8f0] placeholder-[#94a3b8] shadow-[0_6px_20px_rgba(15,24,40,0.4)] focus:outline-none focus:ring-2 focus:ring-[#16a394]"
              )}
            />
            <button
              onClick={handleSend}
              disabled={!input.trim()}
              className={cn(
                "rounded-xl px-6 py-3 font-semibold text-[#0f172a] transition",
                "bg-[#45f0c0] shadow-[0_12px_30px_rgba(69,240,192,0.35)] hover:shadow-[0_16px_40px_rgba(69,240,192,0.45)]",
                !input.trim() && "cursor-not-allowed opacity-60 shadow-none"
              )}
            >
              Send
            </button>
          </footer>
        </div>
      </div>

      <style>{`
        @keyframes ai-chat-bounce {
          0%, 80%, 100% { transform: scale(0); opacity: 0.4; }
          40% { transform: scale(1); opacity: 1; }
        }
      `}</style>
    </>
  );
}
