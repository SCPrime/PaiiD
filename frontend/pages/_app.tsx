import type { AppProps } from "next/app";
import Head from "next/head";
import { useEffect, useState } from "react";
import { Toaster } from "react-hot-toast";
import AIChatBot from "../components/AIChatBot";
import { ChatProvider, useChat } from "../components/ChatContext";
import { ErrorBoundary } from "../components/ErrorBoundary";
import StoryboardCanvas from "../components/StoryboardCanvas";
import { TelemetryProvider } from "../components/TelemetryProvider";
import AppHeader from "../components/layout/AppHeader";
import { AuthProvider } from "../contexts/AuthContext";
import { GlowStyleProvider } from "../contexts/GlowStyleContext";
import { ThemeProvider } from "../contexts/ThemeContext";
import { WorkflowProvider } from "../contexts/WorkflowContext";
import { HelpProvider } from "../hooks/useHelp";
import { DEFAULT_HOTKEYS, getHotkeyManager } from "../lib/hotkeyManager";
import { initSentry, setUser } from "../lib/sentry";
import "../styles/animations.css";
import "../styles/globals.css";
import { theme } from "../styles/theme";

interface AppPropsExtended {
  Component: AppProps["Component"];
  pageProps: AppProps["pageProps"];
  userId: string;
  userRole: "owner" | "beta" | "alpha" | "user";
  telemetryEnabled: boolean;
}

function AppContent({
  Component,
  pageProps,
  userId,
  userRole,
  telemetryEnabled,
}: AppPropsExtended) {
  const { isChatOpen, closeChat, openChat } = useChat();
  const [isStoryboardOpen, setIsStoryboardOpen] = useState(false);
  const [buttonPosition, setButtonPosition] = useState({ x: 20, y: 20 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });

  // Initialize hotkey manager
  useEffect(() => {
    if (typeof window === "undefined") return;

    const hotkeyManager = getHotkeyManager();

    // Register storyboard hotkey
    hotkeyManager.register("storyboard", {
      ...DEFAULT_HOTKEYS.STORYBOARD,
      action: () => setIsStoryboardOpen(true),
    });

    // Register AI chat hotkey
    hotkeyManager.register("ai-chat", {
      ...DEFAULT_HOTKEYS.AI_CHAT,
      action: () => openChat(),
    });

    // Register close modal hotkey
    hotkeyManager.register("close-modal", {
      ...DEFAULT_HOTKEYS.CLOSE_MODAL,
      action: () => {
        if (isStoryboardOpen) setIsStoryboardOpen(false);
        if (isChatOpen) closeChat();
      },
    });

    return () => {
      hotkeyManager.unregister("storyboard");
      hotkeyManager.unregister("ai-chat");
      hotkeyManager.unregister("close-modal");
    };
  }, [isStoryboardOpen, isChatOpen, closeChat, openChat]);

  // Handle storyboard button drag
  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    setDragOffset({
      x: e.clientX - buttonPosition.x,
      y: e.clientY - buttonPosition.y,
    });
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (!isDragging) return;

    const newX = e.clientX - dragOffset.x;
    const newY = e.clientY - dragOffset.y;

    // Keep button within viewport
    const maxX = window.innerWidth - 60;
    const maxY = window.innerHeight - 60;

    setButtonPosition({
      x: Math.max(20, Math.min(newX, maxX)),
      y: Math.max(20, Math.min(newY, maxY)),
    });
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  useEffect(() => {
    if (isDragging) {
      document.addEventListener("mousemove", handleMouseMove);
      document.addEventListener("mouseup", handleMouseUp);
      return () => {
        document.removeEventListener("mousemove", handleMouseMove);
        document.removeEventListener("mouseup", handleMouseUp);
      };
    }
  }, [isDragging, dragOffset]);

  return (
    <TelemetryProvider userId={userId} userRole={userRole} enabled={telemetryEnabled}>
      <Head>
        <title>PaiiD Trading Platform</title>
        <meta name="description" content="PaiiD – AI-assisted trading intelligence platform" />
      </Head>

      <a
        href="#main-content"
        style={{
          position: "absolute",
          left: "-9999px",
          top: "auto",
          width: "1px",
          height: "1px",
          overflow: "hidden",
        }}
        onFocus={(event) => {
          Object.assign(event.currentTarget.style, {
            position: "fixed",
            left: "16px",
            top: "16px",
            width: "auto",
            height: "auto",
            padding: "12px 16px",
            backgroundColor: "rgba(15, 24, 40, 0.95)",
            color: theme.colors.text,
            borderRadius: theme.borderRadius.sm,
            border: `1px solid ${theme.colors.border}`,
            zIndex: "10000",
          });
        }}
        onBlur={(event) => {
          Object.assign(event.currentTarget.style, {
            position: "absolute",
            left: "-9999px",
            top: "auto",
            width: "1px",
            height: "1px",
            padding: "0",
            backgroundColor: "transparent",
            border: "none",
            color: "inherit",
          });
        }}
      >
        Skip to main content
      </a>

      <header role="banner">
        <AppHeader onLogoClick={() => window.location.assign("/")} />
      </header>

      <main id="main-content" role="main">
        <Component {...pageProps} />
      </main>

      <AIChatBot isOpen={isChatOpen} onClose={closeChat} />

      {/* Storyboard Canvas */}
      {isStoryboardOpen && <StoryboardCanvas onClose={() => setIsStoryboardOpen(false)} />}

      {/* Floating Storyboard Button */}
      {!isStoryboardOpen && (
        <button
          onMouseDown={handleMouseDown}
          onClick={() => !isDragging && setIsStoryboardOpen(true)}
          style={{
            position: "fixed",
            bottom: `${window.innerHeight - buttonPosition.y - 60}px`,
            right: `${window.innerWidth - buttonPosition.x - 60}px`,
            width: "60px",
            height: "60px",
            backgroundColor: "rgba(99, 102, 241, 0.9)",
            border: "2px solid rgba(129, 140, 248, 0.5)",
            borderRadius: "50%",
            cursor: isDragging ? "grabbing" : "grab",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: "24px",
            color: "white",
            boxShadow: "0 8px 24px rgba(99, 102, 241, 0.4)",
            zIndex: 9999,
            transition: isDragging ? "none" : "transform 0.2s, box-shadow 0.2s",
            transform: isDragging ? "scale(1.1)" : "scale(1)",
          }}
          onMouseEnter={(e) => {
            if (!isDragging) {
              e.currentTarget.style.transform = "scale(1.1)";
              e.currentTarget.style.boxShadow = "0 12px 32px rgba(99, 102, 241, 0.6)";
            }
          }}
          onMouseLeave={(e) => {
            if (!isDragging) {
              e.currentTarget.style.transform = "scale(1)";
              e.currentTarget.style.boxShadow = "0 8px 24px rgba(99, 102, 241, 0.4)";
            }
          }}
          title="Storyboard Mode (Ctrl+Shift+S)"
        >
          📋
        </button>
      )}

      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            backgroundColor: "rgba(30, 41, 59, 0.95)",
            color: theme.colors.text,
            border: "1px solid rgba(16, 185, 129, 0.3)",
            borderRadius: "12px",
            backdropFilter: "blur(10px)",
            boxShadow: "0 8px 32px rgba(0, 0, 0, 0.3)",
          },
          success: {
            iconTheme: {
              primary: theme.colors.success,
              secondary: theme.colors.text,
            },
            style: {
              border: "1px solid rgba(16, 185, 129, 0.5)",
            },
          },
          error: {
            iconTheme: {
              primary: theme.colors.danger,
              secondary: theme.colors.text,
            },
            style: {
              border: "1px solid rgba(239, 68, 68, 0.5)",
            },
          },
          loading: {
            iconTheme: {
              primary: "#7E57C2",
              secondary: theme.colors.text,
            },
          },
        }}
      />
    </TelemetryProvider>
  );
}

export default function App({ Component, pageProps }: AppProps) {
  // Initialize Sentry on app startup (client-side only)
  useEffect(() => {
    if (typeof window !== "undefined") {
      initSentry();
    }
  }, []);

  // Get user info from localStorage (or generate unique ID)
  const [user] = useState(() => {
    if (typeof window === "undefined") {
      return { id: "anonymous", role: "user" as const };
    }

    const storedUserId = localStorage.getItem("user-id");
    const userId = storedUserId || `user-${Date.now()}`;

    if (!storedUserId) {
      localStorage.setItem("user-id", userId);
    }

    const storedRole = localStorage.getItem("user-role") as
      | "owner"
      | "beta"
      | "alpha"
      | "user"
      | null;
    const userRole = storedRole || "user";

    return { id: userId, role: userRole };
  });

  // Set Sentry user context when user changes
  useEffect(() => {
    if (typeof window !== "undefined" && user) {
      setUser(user.id, user.role);
    }
  }, [user]);

  // Check if telemetry is enabled from environment variable
  const telemetryEnabled = process.env.NEXT_PUBLIC_TELEMETRY_ENABLED !== "false";

  return (
    <ErrorBoundary>
      <ThemeProvider>
        <GlowStyleProvider>
          <HelpProvider>
            <AuthProvider>
              <ChatProvider>
                <WorkflowProvider>
                  <AppContent
                    Component={Component}
                    pageProps={pageProps}
                    userId={user.id}
                    userRole={user.role}
                    telemetryEnabled={telemetryEnabled}
                  />
                </WorkflowProvider>
              </ChatProvider>
            </AuthProvider>
          </HelpProvider>
        </GlowStyleProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}
