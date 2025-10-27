/**
 * Authentication Context
 *
 * Manages user authentication state, tokens, and session persistence.
 * Provides login, register, logout functions and auto token refresh.
 */

import React, { createContext, useCallback, useEffect, useRef, useState } from "react";
import toast from "react-hot-toast";
import * as authApi from "../lib/authApi";
import { logger } from "../lib/logger";

interface AuthContextValue {
  user: authApi.UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: authApi.RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  refreshSession: () => Promise<void>;
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<authApi.UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const refreshTimerRef = useRef<NodeJS.Timeout | null>(null);

  /**
   * Internal refresh function (doesn't show toast)
   */
  const refreshSessionInternal = useCallback(async () => {
    const tokens = authApi.getStoredTokens();
    if (!tokens) throw new Error("No tokens to refresh");

    const newTokens = await authApi.refreshToken(tokens.refreshToken);
    authApi.saveTokens(newTokens);

    // Update user profile
    const profile = await authApi.getCurrentUser(newTokens.access_token);
    setUser(profile);
  }, []);

  /**
   * Start token refresh timer
   */
  const startRefreshTimer = useCallback(() => {
    // Clear existing timer
    if (refreshTimerRef.current) {
      clearTimeout(refreshTimerRef.current);
    }

    // Refresh every 10 minutes (access token expires in 15)
    refreshTimerRef.current = setTimeout(
      async () => {
        try {
          await refreshSessionInternal();
          startRefreshTimer(); // Schedule next refresh
        } catch (error) {
          logger.error("Token refresh failed", error);
          // Let user continue, they'll be logged out on next API call
        }
      },
      10 * 60 * 1000
    ); // 10 minutes
  }, [refreshSessionInternal]);

  /**
   * Public refresh function (for manual refresh)
   */
  const refreshSession = useCallback(async () => {
    try {
      await refreshSessionInternal();
      startRefreshTimer();
    } catch (error) {
      toast.error("Session refresh failed. Please login again.");
      authApi.clearTokens();
      setUser(null);
    }
  }, [refreshSessionInternal, startRefreshTimer]);

  /**
   * Login with email and password
   */
  const login = useCallback(
    async (email: string, password: string) => {
      try {
        const tokens = await authApi.login({ email, password });
        authApi.saveTokens(tokens);

        // Fetch user profile
        const profile = await authApi.getCurrentUser(tokens.access_token);
        setUser(profile);

        startRefreshTimer();
        toast.success(`Welcome back, ${profile.full_name || profile.email}!`);
      } catch (error) {
        if (error instanceof authApi.AuthError) {
          if (error.statusCode === 401) {
            throw new Error("Invalid email or password");
          } else if (error.statusCode === 403) {
            throw new Error("Your account has been disabled");
          }
        }
        throw new Error("Login failed. Please try again.");
      }
    },
    [startRefreshTimer]
  );

  /**
   * Register new user
   */
  const register = useCallback(
    async (data: authApi.RegisterData) => {
      try {
        const tokens = await authApi.register(data);
        authApi.saveTokens(tokens);

        // Fetch user profile
        const profile = await authApi.getCurrentUser(tokens.access_token);
        setUser(profile);

        startRefreshTimer();
        toast.success(`Welcome to PaiiD, ${profile.full_name || profile.email}!`);
      } catch (error) {
        if (error instanceof authApi.AuthError) {
          if (error.statusCode === 400) {
            throw new Error("Email already registered or invalid invite code");
          }
        }
        throw new Error("Registration failed. Please try again.");
      }
    },
    [startRefreshTimer]
  );

  /**
   * Logout user
   */
  const logout = useCallback(async () => {
    const tokens = authApi.getStoredTokens();

    // Clear local state first (optimistic)
    setUser(null);
    authApi.clearTokens();

    if (refreshTimerRef.current) {
      clearTimeout(refreshTimerRef.current);
    }

    // Try to logout on server (invalidate session)
    if (tokens) {
      try {
        await authApi.logout(tokens.accessToken);
      } catch (error) {
        // Ignore errors, we already cleared local state
        logger.warn("Server logout failed", error);
      }
    }

    toast.success("Logged out successfully");
  }, []);

  /**
   * Load user session from stored tokens on mount
   */
  useEffect(() => {
    const loadSession = async () => {
      const tokens = authApi.getStoredTokens();

      if (!tokens) {
        setIsLoading(false);
        return;
      }

      // Check if token is expired
      if (Date.now() >= tokens.expiresAt) {
        // Try to refresh
        try {
          await refreshSessionInternal();
        } catch (error) {
          // Refresh failed, clear session
          authApi.clearTokens();
          setIsLoading(false);
        }
        return;
      }

      // Token is valid, fetch user profile
      try {
        const profile = await authApi.getCurrentUser(tokens.accessToken);
        setUser(profile);
        startRefreshTimer();
      } catch (error) {
        // Token invalid, clear it
        authApi.clearTokens();
      } finally {
        setIsLoading(false);
      }
    };

    loadSession();

    return () => {
      if (refreshTimerRef.current) {
        clearTimeout(refreshTimerRef.current);
      }
    };
  }, [refreshSessionInternal, startRefreshTimer]);

  const value: AuthContextValue = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
    refreshSession,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
