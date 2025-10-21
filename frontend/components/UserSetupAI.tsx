/**
 * AI-Guided User Setup
 * Conversational onboarding with Claude AI
 */

import { useState, useRef, useEffect, useMemo } from "react";
import {
  Brain,
  Sparkles,
  MessageCircle,
  Send,
  Loader2,
  Check,
  ArrowRight,
  Target,
  Shield,
  TrendingUp,
  DollarSign,
} from "lucide-react";
import { theme } from "../styles/theme";
import { LOGO_ANIMATION_KEYFRAME } from "../styles/logoConstants";
import { claudeAI, UserPreferences } from "../lib/aiAdapter";
import { createUser } from "../lib/userManagement";
import dynamic from "next/dynamic";
import PaiiDLogo from "./PaiiDLogo";

const UserSetup = dynamic(() => import("./UserSetup"), { ssr: false });

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface UserSetupAIProps {
  onComplete: () => void;
}

export default function UserSetupAI({ onComplete }: UserSetupAIProps) {
  const [setupMethod, setSetupMethod] = useState<"manual" | "ai" | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [extractedPrefs, setExtractedPrefs] = useState<Partial<UserPreferences> | null>(null);
  const [showReview, setShowReview] = useState(false);
  const [userName, setUserName] = useState<string>("");
  const [userEmail, setUserEmail] = useState<string>("");
  const [conversationStep, setConversationStep] = useState<"name" | "email" | "trading" | "done">(
    "name"
  );
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Generate consistent particle positions (fixes hydration)
  const particles = useMemo(() => {
    return Array.from({ length: 20 }, (_, i) => ({
      id: i,
      left: Math.random() * 100,
      top: Math.random() * 100,
      duration: 3 + Math.random() * 4,
      delay: Math.random() * 2,
      translateX: Math.random() * 50 - 25,
      translateY: Math.random() * 50 - 25,
    }));
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Owner bypass keyboard combo (Ctrl+Shift+A or Cmd+Shift+A)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Check for Ctrl+Shift+A (Windows/Linux) or Cmd+Shift+A (Mac)
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === "A") {
        e.preventDefault();
        console.info("[UserSetupAI] 🔓 Admin bypass activated during onboarding");

        // Set localStorage flags
        if (typeof window !== "undefined") {
          localStorage.setItem("user-setup-complete", "true");
          localStorage.setItem("admin-bypass", "true");
          localStorage.setItem("bypass-timestamp", new Date().toISOString());
        }

        // Skip onboarding
        alert("🔓 Admin bypass activated! Skipping to dashboard...");
        onComplete();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onComplete]);

  // Initialize AI setup
  const startAISetup = () => {
    setSetupMethod("ai");
    setConversationStep("name");
    setMessages([
      {
        role: "assistant",
        content: `Hi! I'm your AI trading assistant. I'll help you set up your PaiiD account.\n\nFirst, what should I call you? (You can type "skip" or press Enter to remain anonymous)`,
      },
    ]);
  };

  // Handle AI conversation
  const handleSendMessage = async () => {
    if (isProcessing) return;

    const userMessage = input.trim();
    setInput("");

    // Handle empty input for skipping
    if (!userMessage) {
      if (conversationStep === "name") {
        // User pressed Enter without typing - remain anonymous
        setMessages((prev) => [...prev, { role: "user", content: "(skip)" }]);
        setUserName("PaiiD User");
        setConversationStep("email");
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: `No problem! I'll call you "PaiiD User".\n\nWould you like to provide an email address for account recovery and notifications? (Optional - type "skip" or press Enter to continue without email)`,
          },
        ]);
        return;
      } else if (conversationStep === "email") {
        // User pressed Enter without email - skip
        setMessages((prev) => [...prev, { role: "user", content: "(skip)" }]);
        setUserEmail("");
        setConversationStep("trading");
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: `Got it! Now let's set up your trading preferences.\n\nTell me about your trading goals. For example:\n\n• "I want to day-trade tech stocks with $25K, focusing on momentum"\n• "I'm interested in swing trading with $5K, moderate risk"\n• "I want to learn options trading with $1000"\n• "I have my own strategies I'd like help executing"\n\nWhat are your goals?`,
          },
        ]);
        return;
      }
    }

    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setIsProcessing(true);

    try {
      if (conversationStep === "name") {
        // Handle name input
        const isSkip =
          userMessage.toLowerCase() === "skip" || userMessage.toLowerCase() === "anonymous";
        const name = isSkip ? "PaiiD User" : userMessage;
        setUserName(name);
        setConversationStep("email");

        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: `Nice to meet you, ${name}!\n\nWould you like to provide an email address for account recovery and notifications? (Optional - type "skip" or press Enter to continue without email)`,
          },
        ]);
      } else if (conversationStep === "email") {
        // Handle email input
        const isSkip = userMessage.toLowerCase() === "skip";
        const email = isSkip ? "" : userMessage;
        setUserEmail(email);
        setConversationStep("trading");

        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: `${email ? "Great! " : ""}Now let's set up your trading preferences.\n\nTell me about your trading goals. For example:\n\n• "I want to day-trade tech stocks with $25K, focusing on momentum"\n• "I'm interested in swing trading with $5K, moderate risk"\n• "I want to learn options trading with $1000"\n\nWhat are your goals?`,
          },
        ]);
      } else if (conversationStep === "trading") {
        // Extract trading preferences from user's message
        const prefs = await claudeAI.extractSetupPreferences(userMessage);
        setExtractedPrefs(prefs);

        // Generate confirmation message
        const responseMessage = `Perfect! I've extracted your trading preferences. Let me show you what I understood so you can verify everything is correct.`;

        setMessages((prev) => [...prev, { role: "assistant", content: responseMessage }]);
        setConversationStep("done");
        setShowReview(true);
      }
    } catch (error: any) {
      if (conversationStep === "trading") {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: `I'm having trouble understanding. This usually means the backend is offline.\n\nYou can:\n1. Try rephrasing: "I want to trade stocks with $10K, moderate risk, swing trading style"\n2. Click "Skip to Dashboard" below to proceed without AI setup`,
          },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: `Sorry, I encountered an error (backend may be offline). Click "Skip to Dashboard" below to proceed.`,
          },
        ]);
      }
    } finally {
      setIsProcessing(false);
    }
  };

  // Complete setup
  const handleComplete = () => {
    if (!extractedPrefs) return;

    // Create user with collected name, email (if provided), and trading preferences
    createUser(
      userName || "PaiiD User", // Use collected name or default
      userEmail || undefined, // Use collected email or undefined
      undefined, // No test group
      {
        setupMethod: "ai-guided",
        aiConversation: messages.map((m) => ({ role: m.role, content: m.content })),
        riskTolerance: extractedPrefs.riskTolerance,
        preferredStrategy: extractedPrefs.tradingStyle,
        investmentAmount: extractedPrefs.investmentAmount,
        investmentTypes: extractedPrefs.instruments,
        completedAt: new Date().toISOString(),
      }
    );

    console.info("[UserSetupAI] User created:", {
      name: userName || "PaiiD User",
      email: userEmail || "not provided",
      preferences: extractedPrefs,
    });
    onComplete();
  };

  // Method selection screen
  if (!setupMethod) {
    return (
      <div
        style={{
          height: "100vh",
          width: "100vw",
          background: theme.background.primary,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: "16px 12px",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            maxWidth: "800px",
            width: "100%",
            position: "relative",
            display: "flex",
            flexDirection: "column",
            gap: "0px",
          }}
        >
          {/* Particle Background for "aii" area */}
          <div
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              overflow: "hidden",
              pointerEvents: "none",
              opacity: 0.3,
            }}
          >
            {particles.map((particle) => (
              <div
                key={particle.id}
                style={{
                  position: "absolute",
                  width: "2px",
                  height: "2px",
                  backgroundColor: "#45f0c0",
                  borderRadius: "50%",
                  left: `${particle.left}%`,
                  top: `${particle.top}%`,
                  animation: `float-${particle.id} ${particle.duration}s ease-in-out infinite`,
                  animationDelay: `${particle.delay}s`,
                  boxShadow: "0 0 4px rgba(69, 240, 192, 0.8)",
                }}
              />
            ))}
          </div>

          {/* Centered Compact Logo Header */}
          <div
            style={{
              textAlign: "center",
              marginBottom: "8px",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: "4px",
              position: "relative",
            }}
          >
            {/* Compact PaiiD Logo - Click π to launch v46 capabilities interface */}
            <PaiiDLogo size="small" showSubtitle={true} />

            {/* Instruction box */}
            <div
              style={{
                padding: "8px 16px",
                background: "rgba(69, 240, 192, 0.1)",
                border: "1px solid rgba(69, 240, 192, 0.3)",
                borderRadius: "6px",
                color: "#45f0c0",
                fontSize: "11px",
                fontFamily: '"Inter", sans-serif',
                marginBottom: "4px",
              }}
            >
              Click the <span style={{ fontWeight: "bold" }}>π</span> symbol to launch{" "}
              <span style={{ fontWeight: "bold" }}>PaiiD</span> Assistant interface
            </div>

            {/* Additional subtitle: Set up prompt */}
            <p
              style={{
                fontSize: "12px",
                color: "#94a3b8",
                margin: 0,
                letterSpacing: "0.5px",
              }}
            >
              Let&apos;s set up your trading account
            </p>

            {/* Owner bypass hint */}
            <div
              style={{
                fontSize: "9px",
                color: "#475569",
                marginTop: "2px",
                padding: "3px 6px",
                background: "rgba(26, 117, 96, 0.1)",
                borderRadius: "4px",
                border: "1px solid rgba(26, 117, 96, 0.2)",
              }}
            >
              <kbd
                style={{
                  background: "rgba(26, 117, 96, 0.2)",
                  padding: "2px 5px",
                  borderRadius: "2px",
                  fontFamily: "monospace",
                  color: "#45f0c0",
                  fontSize: "8px",
                }}
              >
                Ctrl+Shift+A
              </kbd>{" "}
              admin bypass
            </div>
          </div>

          {/* Method Cards */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: theme.spacing.sm }}>
            {/* AI-Guided Setup */}
            <button
              onClick={startAISetup}
              style={{
                padding: "10px",
                background: theme.background.glass,
                backdropFilter: theme.blur.light,
                border: `2px solid ${theme.workflow.strategyBuilder}40`,
                borderRadius: theme.borderRadius.xl,
                cursor: "pointer",
                transition: theme.transitions.normal,
                textAlign: "center",
                boxShadow: theme.glow.darkPurple,
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = "translateY(-4px)";
                e.currentTarget.style.boxShadow = `0 8px 32px ${theme.workflow.strategyBuilder}40`;
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = "translateY(0)";
                e.currentTarget.style.boxShadow = theme.glow.darkPurple;
              }}
            >
              <Brain
                style={{
                  width: "36px",
                  height: "36px",
                  color: theme.workflow.strategyBuilder,
                  margin: `0 auto 6px`,
                }}
              />
              <h3 style={{ color: theme.colors.text, marginBottom: "5px", fontSize: "18px" }}>
                AI-Guided Setup
              </h3>
              <p
                style={{
                  color: theme.colors.textMuted,
                  marginBottom: "6px",
                  lineHeight: 1.4,
                  fontSize: "12px",
                }}
              >
                Chat with Claude AI to set up your account. Just describe your trading goals
                naturally.
              </p>
              <div
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: theme.spacing.xs,
                  color: theme.workflow.strategyBuilder,
                  fontWeight: "600",
                  fontSize: "12px",
                }}
              >
                <Sparkles style={{ width: "13px", height: "13px" }} />
                Recommended
              </div>
            </button>

            {/* Manual Setup */}
            <button
              onClick={() => setSetupMethod("manual")}
              style={{
                padding: "10px",
                background: theme.background.glass,
                backdropFilter: theme.blur.light,
                border: `1px solid ${theme.colors.border}`,
                borderRadius: theme.borderRadius.xl,
                cursor: "pointer",
                transition: theme.transitions.normal,
                textAlign: "center",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = "translateY(-4px)";
                e.currentTarget.style.borderColor = theme.colors.primary;
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = "translateY(0)";
                e.currentTarget.style.borderColor = theme.colors.border;
              }}
            >
              <Target
                style={{
                  width: "36px",
                  height: "36px",
                  color: theme.colors.primary,
                  margin: `0 auto 6px`,
                }}
              />
              <h3 style={{ color: theme.colors.text, marginBottom: "5px", fontSize: "18px" }}>
                Manual Setup
              </h3>
              <p
                style={{
                  color: theme.colors.textMuted,
                  marginBottom: "6px",
                  lineHeight: 1.4,
                  fontSize: "12px",
                }}
              >
                Fill out a traditional form with dropdowns and inputs. More control over each field.
              </p>
              <div style={{ height: "18px" }}></div>
            </button>
          </div>
        </div>
      </div>
    );
  }

  // AI Chat Interface
  if (setupMethod === "ai" && !showReview) {
    return (
      <div
        style={{
          minHeight: "100vh",
          width: "100vw",
          background: theme.background.primary,
          display: "flex",
          flexDirection: "column",
          padding: theme.spacing.lg,
        }}
      >
        <div
          style={{
            maxWidth: "900px",
            width: "100%",
            margin: "0 auto",
            display: "flex",
            flexDirection: "column",
            flex: 1,
          }}
        >
          {/* Header */}
          <div
            style={{
              background: theme.background.glass,
              backdropFilter: theme.blur.light,
              border: `1px solid ${theme.workflow.strategyBuilder}40`,
              borderRadius: theme.borderRadius.xl,
              padding: theme.spacing.lg,
              marginBottom: theme.spacing.lg,
              display: "flex",
              alignItems: "center",
              gap: theme.spacing.md,
            }}
          >
            <Brain
              style={{ width: "32px", height: "32px", color: theme.workflow.strategyBuilder }}
            />
            <div>
              <h2 style={{ color: theme.colors.text, margin: 0, fontSize: "24px" }}>
                AI Setup Assistant
              </h2>
              <p style={{ color: theme.colors.textMuted, margin: 0, fontSize: "14px" }}>
                Tell me about your trading goals
              </p>
            </div>
          </div>

          {/* Messages */}
          <div
            style={{
              flex: 1,
              overflowY: "auto",
              background: theme.background.glass,
              backdropFilter: theme.blur.light,
              border: `1px solid ${theme.colors.border}`,
              borderRadius: theme.borderRadius.xl,
              padding: theme.spacing.lg,
              marginBottom: theme.spacing.md,
            }}
          >
            {messages.map((msg, idx) => (
              <div
                key={idx}
                style={{
                  display: "flex",
                  justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
                  marginBottom: theme.spacing.md,
                }}
              >
                <div
                  style={{
                    maxWidth: "75%",
                    padding: theme.spacing.md,
                    borderRadius: theme.borderRadius.lg,
                    background:
                      msg.role === "user"
                        ? `linear-gradient(135deg, ${theme.colors.primary}, ${theme.colors.secondary})`
                        : `${theme.workflow.strategyBuilder}20`,
                    border:
                      msg.role === "user"
                        ? "none"
                        : `1px solid ${theme.workflow.strategyBuilder}40`,
                    color: theme.colors.text,
                    whiteSpace: "pre-wrap",
                    lineHeight: 1.6,
                  }}
                >
                  {msg.content}
                </div>
              </div>
            ))}
            {isProcessing && (
              <div
                style={{
                  display: "flex",
                  justifyContent: "flex-start",
                  marginBottom: theme.spacing.md,
                }}
              >
                <div
                  style={{
                    padding: theme.spacing.md,
                    borderRadius: theme.borderRadius.lg,
                    background: `${theme.workflow.strategyBuilder}20`,
                    border: `1px solid ${theme.workflow.strategyBuilder}40`,
                  }}
                >
                  <Loader2
                    className="animate-spin"
                    style={{ width: "20px", height: "20px", color: theme.workflow.strategyBuilder }}
                  />
                </div>
              </div>
            )}

            {/* Quick Action Buttons (only show on trading step) */}
            {conversationStep === "trading" && !isProcessing && (
              <div style={{ marginBottom: theme.spacing.md }}>
                <p
                  style={{
                    color: theme.colors.textMuted,
                    fontSize: "14px",
                    marginBottom: theme.spacing.sm,
                    textAlign: "center",
                  }}
                >
                  Or click an example:
                </p>
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(2, 1fr)",
                    gap: theme.spacing.sm,
                  }}
                >
                  {[
                    {
                      emoji: "📊",
                      text: "Day Trading - $25K",
                      fullText: "I want to day-trade tech stocks with $25K, focusing on momentum",
                    },
                    {
                      emoji: "📈",
                      text: "Swing Trading - $5K",
                      fullText: "I'm interested in swing trading with $5K, moderate risk",
                    },
                    {
                      emoji: "💡",
                      text: "Learn Options - $1K",
                      fullText: "I want to learn options trading with $1000",
                    },
                    {
                      emoji: "🎯",
                      text: "My Own Strategies",
                      fullText: "I have my own strategies I'd like help executing",
                    },
                  ].map((option, idx) => (
                    <button
                      key={idx}
                      onClick={async () => {
                        // Show text in input briefly
                        setInput(option.fullText);

                        // Submit immediately (no delay)
                        setMessages((prev) => [
                          ...prev,
                          { role: "user", content: option.fullText },
                        ]);
                        setInput("");
                        setIsProcessing(true);

                        try {
                          // Extract trading preferences from clicked option
                          const prefs = await claudeAI.extractSetupPreferences(option.fullText);
                          setExtractedPrefs(prefs);
                          setMessages((prev) => [
                            ...prev,
                            {
                              role: "assistant",
                              content: `Perfect! I've extracted your trading preferences. Let me show you what I understood so you can verify everything is correct.`,
                            },
                          ]);
                          setConversationStep("done");
                          setShowReview(true);
                        } catch (error) {
                          setMessages((prev) => [
                            ...prev,
                            {
                              role: "assistant",
                              content: `I'm having trouble understanding. This usually means the backend is offline.\n\nYou can:\n1. Try rephrasing: "I want to trade stocks with $10K, moderate risk, swing trading style"\n2. Click "Skip to Dashboard" below to proceed without AI setup`,
                            },
                          ]);
                        } finally {
                          setIsProcessing(false);
                        }
                      }}
                      style={{
                        padding: theme.spacing.sm,
                        background: theme.background.glass,
                        backdropFilter: theme.blur.light,
                        border: `1px solid ${theme.colors.border}`,
                        borderRadius: theme.borderRadius.lg,
                        color: theme.colors.text,
                        fontSize: "13px",
                        fontWeight: "500",
                        cursor: "pointer",
                        transition: theme.transitions.fast,
                        textAlign: "center",
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.borderColor = theme.workflow.strategyBuilder;
                        e.currentTarget.style.background = `${theme.workflow.strategyBuilder}15`;
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.borderColor = theme.colors.border;
                        e.currentTarget.style.background = theme.background.glass;
                      }}
                    >
                      <div>{option.emoji}</div>
                      <div style={{ marginTop: "4px" }}>{option.text}</div>
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div style={{ display: "flex", flexDirection: "column", gap: theme.spacing.sm }}>
            <div style={{ display: "flex", gap: theme.spacing.sm }}>
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
                placeholder={
                  conversationStep === "name"
                    ? "Enter your name..."
                    : conversationStep === "email"
                      ? "Enter your email..."
                      : "Describe your trading goals..."
                }
                disabled={isProcessing}
                style={{
                  flex: 1,
                  padding: theme.spacing.md,
                  background: theme.background.input,
                  border: `1px solid ${theme.colors.border}`,
                  borderRadius: theme.borderRadius.lg,
                  color: theme.colors.text,
                  fontSize: "16px",
                  outline: "none",
                  transition: theme.transitions.fast,
                }}
              />
              <button
                onClick={handleSendMessage}
                disabled={!input.trim() || isProcessing}
                style={{
                  padding: `${theme.spacing.md} ${theme.spacing.lg}`,
                  background: `linear-gradient(135deg, ${theme.colors.primary}, ${theme.colors.secondary})`,
                  border: "none",
                  borderRadius: theme.borderRadius.lg,
                  color: "#ffffff",
                  fontWeight: "600",
                  cursor: !input.trim() || isProcessing ? "not-allowed" : "pointer",
                  opacity: !input.trim() || isProcessing ? 0.5 : 1,
                  display: "flex",
                  alignItems: "center",
                  gap: theme.spacing.xs,
                  transition: theme.transitions.fast,
                }}
              >
                {isProcessing ? (
                  <Loader2 className="animate-spin" style={{ width: "20px", height: "20px" }} />
                ) : (
                  <Send style={{ width: "20px", height: "20px" }} />
                )}
              </button>
            </div>

            {/* Skip to Dashboard Button */}
            <button
              onClick={() => {
                localStorage.setItem("user-setup-complete", "true");
                localStorage.setItem("manual-skip", "true");
                onComplete();
              }}
              style={{
                width: "100%",
                padding: theme.spacing.md,
                background: theme.background.glass,
                backdropFilter: theme.blur.light,
                border: `1px solid ${theme.colors.border}`,
                borderRadius: theme.borderRadius.lg,
                color: theme.colors.text,
                fontWeight: "600",
                cursor: "pointer",
                transition: theme.transitions.fast,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: theme.spacing.sm,
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = theme.colors.primary;
                e.currentTarget.style.background = `${theme.colors.primary}15`;
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = theme.colors.border;
                e.currentTarget.style.background = theme.background.glass;
              }}
            >
              <ArrowRight style={{ width: "18px", height: "18px" }} />
              Skip to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Review Screen
  if (showReview && extractedPrefs) {
    return (
      <div
        style={{
          minHeight: "100vh",
          width: "100vw",
          background: theme.background.primary,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: theme.spacing.lg,
        }}
      >
        <div style={{ maxWidth: "700px", width: "100%" }}>
          {/* Header */}
          <div style={{ textAlign: "center", marginBottom: theme.spacing.xl }}>
            <Check
              style={{
                width: "64px",
                height: "64px",
                color: theme.colors.primary,
                margin: `0 auto ${theme.spacing.md}`,
              }}
            />
            <h2
              style={{
                color: theme.colors.text,
                margin: `0 0 ${theme.spacing.sm} 0`,
                fontSize: "32px",
              }}
            >
              Review Your Setup
            </h2>
            <p style={{ color: theme.colors.textMuted }}>
              Here&apos;s what we configured for {userName || "you"}
            </p>
          </div>

          {/* Preferences Card */}
          <div
            style={{
              background: theme.background.glass,
              backdropFilter: theme.blur.light,
              border: `1px solid ${theme.colors.border}`,
              borderRadius: theme.borderRadius.xl,
              padding: theme.spacing.xl,
              marginBottom: theme.spacing.lg,
            }}
          >
            <div style={{ display: "grid", gap: theme.spacing.lg }}>
              {/* User Name */}
              {userName && (
                <div>
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: theme.spacing.sm,
                      marginBottom: theme.spacing.sm,
                    }}
                  >
                    <MessageCircle
                      style={{
                        width: "20px",
                        height: "20px",
                        color: theme.workflow.strategyBuilder,
                      }}
                    />
                    <h4 style={{ color: theme.colors.text, margin: 0 }}>Name</h4>
                  </div>
                  <p style={{ color: theme.colors.textMuted, margin: 0, paddingLeft: "28px" }}>
                    {userName}
                  </p>
                </div>
              )}

              {/* User Email */}
              {userEmail && (
                <div>
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: theme.spacing.sm,
                      marginBottom: theme.spacing.sm,
                    }}
                  >
                    <MessageCircle
                      style={{ width: "20px", height: "20px", color: theme.colors.info }}
                    />
                    <h4 style={{ color: theme.colors.text, margin: 0 }}>Email</h4>
                  </div>
                  <p style={{ color: theme.colors.textMuted, margin: 0, paddingLeft: "28px" }}>
                    {userEmail}
                  </p>
                </div>
              )}

              {/* Investment Amount */}
              {extractedPrefs.investmentAmount && (
                <div>
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: theme.spacing.sm,
                      marginBottom: theme.spacing.sm,
                    }}
                  >
                    <DollarSign
                      style={{ width: "20px", height: "20px", color: theme.colors.primary }}
                    />
                    <h4 style={{ color: theme.colors.text, margin: 0 }}>Investment Amount</h4>
                  </div>
                  <p style={{ color: theme.colors.textMuted, margin: 0, paddingLeft: "28px" }}>
                    {extractedPrefs.investmentAmount.mode === "unlimited"
                      ? "Unlimited"
                      : `$${extractedPrefs.investmentAmount.value?.toLocaleString()}`}
                  </p>
                </div>
              )}

              {/* Risk Tolerance */}
              {extractedPrefs.riskTolerance && (
                <div>
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: theme.spacing.sm,
                      marginBottom: theme.spacing.sm,
                    }}
                  >
                    <Shield
                      style={{ width: "20px", height: "20px", color: theme.colors.warning }}
                    />
                    <h4 style={{ color: theme.colors.text, margin: 0 }}>Risk Tolerance</h4>
                  </div>
                  <p
                    style={{
                      color: theme.colors.textMuted,
                      margin: 0,
                      paddingLeft: "28px",
                      textTransform: "capitalize",
                    }}
                  >
                    {extractedPrefs.riskTolerance}
                  </p>
                </div>
              )}

              {/* Trading Style */}
              {extractedPrefs.tradingStyle && (
                <div>
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: theme.spacing.sm,
                      marginBottom: theme.spacing.sm,
                    }}
                  >
                    <TrendingUp
                      style={{ width: "20px", height: "20px", color: theme.colors.secondary }}
                    />
                    <h4 style={{ color: theme.colors.text, margin: 0 }}>Trading Style</h4>
                  </div>
                  <p
                    style={{
                      color: theme.colors.textMuted,
                      margin: 0,
                      paddingLeft: "28px",
                      textTransform: "capitalize",
                    }}
                  >
                    {extractedPrefs.tradingStyle}
                  </p>
                </div>
              )}

              {/* Instruments */}
              {extractedPrefs.instruments && extractedPrefs.instruments.length > 0 && (
                <div>
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: theme.spacing.sm,
                      marginBottom: theme.spacing.sm,
                    }}
                  >
                    <Target
                      style={{
                        width: "20px",
                        height: "20px",
                        color: theme.workflow.strategyBuilder,
                      }}
                    />
                    <h4 style={{ color: theme.colors.text, margin: 0 }}>Instruments</h4>
                  </div>
                  <p style={{ color: theme.colors.textMuted, margin: 0, paddingLeft: "28px" }}>
                    {extractedPrefs.instruments.join(", ")}
                  </p>
                </div>
              )}

              {/* Watchlist */}
              {extractedPrefs.watchlist && extractedPrefs.watchlist.length > 0 && (
                <div>
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: theme.spacing.sm,
                      marginBottom: theme.spacing.sm,
                    }}
                  >
                    <MessageCircle
                      style={{ width: "20px", height: "20px", color: theme.colors.info }}
                    />
                    <h4 style={{ color: theme.colors.text, margin: 0 }}>Watchlist</h4>
                  </div>
                  <p style={{ color: theme.colors.textMuted, margin: 0, paddingLeft: "28px" }}>
                    {extractedPrefs.watchlist.join(", ")}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Actions */}
          <div style={{ display: "flex", gap: theme.spacing.md }}>
            <button
              onClick={() => {
                setShowReview(false);
                setConversationStep("trading");
                setMessages((prev) => [
                  ...prev,
                  {
                    role: "assistant",
                    content:
                      "No problem! What would you like to change? Just describe your updated trading preferences.",
                  },
                ]);
              }}
              style={{
                flex: 1,
                padding: theme.spacing.md,
                background: theme.background.glass,
                backdropFilter: theme.blur.light,
                border: `1px solid ${theme.colors.border}`,
                borderRadius: theme.borderRadius.lg,
                color: theme.colors.text,
                fontWeight: "600",
                cursor: "pointer",
                transition: theme.transitions.fast,
              }}
            >
              Make Changes
            </button>
            <button
              onClick={handleComplete}
              style={{
                flex: 2,
                padding: theme.spacing.md,
                background: `linear-gradient(135deg, ${theme.colors.primary}, ${theme.colors.secondary})`,
                border: "none",
                borderRadius: theme.borderRadius.lg,
                color: "#ffffff",
                fontWeight: "600",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: theme.spacing.sm,
                transition: theme.transitions.fast,
              }}
            >
              Complete Setup
              <ArrowRight style={{ width: "20px", height: "20px" }} />
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Manual setup - use the full UserSetup component
  if (setupMethod === "manual") {
    return <UserSetup onComplete={onComplete} />;
  }

  return (
    <>
      {null}
      {/* CSS Animations */}
      <style jsx global>{`
        ${LOGO_ANIMATION_KEYFRAME}

        ${particles
          .map(
            (particle) => `
          @keyframes float-${particle.id} {
            0%, 100% {
              transform: translate(0, 0) scale(1);
              opacity: 0.3;
            }
            50% {
              transform: translate(${particle.translateX}px, ${particle.translateY}px) scale(1.5);
              opacity: 0.8;
            }
          }
        `
          )
          .join("\n")}
      `}</style>
    </>
  );
}
