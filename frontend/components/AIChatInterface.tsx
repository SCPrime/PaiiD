import React, { useEffect, useRef, useState } from "react";
import { useWebSocket } from "../hooks/useWebSocket";
import EnhancedCard from "./ui/EnhancedCard";
import StatusIndicator from "./ui/StatusIndicator";

interface AIChatInterfaceProps {
  userId: string;
  className?: string;
  isOpen?: boolean;
  onClose?: () => void;
}

interface ChatMessage {
  id: string;
  type: "user" | "ai";
  message: string;
  timestamp: string;
  confidence?: number;
  suggested_actions?: string[];
}

const AIChatInterface: React.FC<AIChatInterfaceProps> = ({
  userId,
  className,
  isOpen = true,
  onClose,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { isConnected: wsConnected, sendMessage: _sendMessage } = useWebSocket({
    url: process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws",
    userId,
    autoConnect: true,
  });

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Update connection status
  useEffect(() => {
    setIsConnected(wsConnected);
  }, [wsConnected]);

  const sendChatMessage = async (message: string) => {
    if (!message.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: "user",
      message: message.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage("");
    setIsLoading(true);

    try {
      // Send message to AI service
      const response = await fetch("/api/ai/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: userId,
          message: message.trim(),
          context: {
            user_id: userId,
            timestamp: new Date().toISOString(),
            market_status: "open",
          },
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const aiMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          type: "ai",
          message: data.ai_response || "I'm sorry, I couldn't process that request.",
          timestamp: data.timestamp,
          confidence: data.confidence,
          suggested_actions: data.suggested_actions,
        };

        setMessages((prev) => [...prev, aiMessage]);
      } else {
        throw new Error("Failed to get AI response");
      }
    } catch (error) {
      console.error("Error sending chat message:", error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: "ai",
        message: "I'm sorry, I encountered an error. Please try again.",
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendChatMessage(inputMessage);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendChatMessage(inputMessage);
    }
  };

  if (!isOpen) {
    return null;
  }

  return (
    <div className={`fixed inset-0 z-50 flex items-center justify-center ${className}`}>
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />

      <EnhancedCard
        variant="glass"
        size="xl"
        className="relative w-full max-w-4xl h-[80vh] flex flex-col"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-700/50">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">AI</span>
            </div>
            <div>
              <h2 className="text-white font-bold text-lg">PaiiD AI Assistant</h2>
              <div className="flex items-center gap-2">
                <StatusIndicator status={isConnected ? "online" : "offline"} size="sm" />
                <span className="text-xs text-slate-400">
                  {isConnected ? "Connected" : "Disconnected"}
                </span>
              </div>
            </div>
          </div>

          <button onClick={onClose} className="text-slate-400 hover:text-white transition-colors">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="text-center text-slate-400 py-8">
              <div className="text-4xl mb-4">🤖</div>
              <p className="text-lg font-medium">Hi! I&apos;m your PaiiD AI assistant.</p>
              <p className="text-sm mt-2">
                Ask me about market conditions, trading strategies, or portfolio analysis.
              </p>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.type === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-3 ${
                    message.type === "user"
                      ? "bg-blue-500 text-white"
                      : "bg-slate-700 text-slate-200"
                  }`}
                >
                  <div className="flex items-start gap-2">
                    {message.type === "ai" && (
                      <div className="w-6 h-6 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                        <span className="text-white text-xs font-bold">AI</span>
                      </div>
                    )}
                    <div className="flex-1">
                      <p className="text-sm">{message.message}</p>
                      {message.confidence && (
                        <div className="text-xs text-slate-400 mt-1">
                          Confidence: {message.confidence}%
                        </div>
                      )}
                      {message.suggested_actions && message.suggested_actions.length > 0 && (
                        <div className="mt-2">
                          <p className="text-xs text-slate-400 mb-1">Suggested actions:</p>
                          <div className="flex flex-wrap gap-1">
                            {message.suggested_actions.map((action, index) => (
                              <span
                                key={index}
                                className="text-xs bg-slate-600 text-slate-300 px-2 py-1 rounded"
                              >
                                {action}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-slate-700 text-slate-200 rounded-lg p-3">
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                    <span className="text-white text-xs font-bold">AI</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" />
                    <div
                      className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"
                      style={{ animationDelay: "0.1s" }}
                    />
                    <div
                      className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"
                      style={{ animationDelay: "0.2s" }}
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-4 border-t border-slate-700/50">
          <form onSubmit={handleSubmit} className="flex gap-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me about the market..."
              className="flex-1 bg-slate-800 text-white placeholder-slate-400 border border-slate-600 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!inputMessage.trim() || isLoading}
              className="bg-blue-500 hover:bg-blue-600 disabled:bg-slate-600 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg transition-colors"
            >
              {isLoading ? "..." : "Send"}
            </button>
          </form>
        </div>
      </EnhancedCard>
    </div>
  );
};

export default AIChatInterface;
