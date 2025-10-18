/**
 * Authentication API Client
 *
 * Provides functions to interact with the backend auth endpoints.
 * All requests go through the Next.js API proxy.
 */

const API_BASE = "/api/proxy/api";

export interface RegisterData {
  email: string;
  password: string;
  full_name?: string;
  invite_code?: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface UserProfile {
  id: number;
  email: string;
  full_name: string | null;
  role: string;
  is_active: boolean;
  created_at: string;
  last_login_at: string | null;
  preferences: Record<string, any>;
}

export class AuthError extends Error {
  constructor(
    public statusCode: number,
    message: string
  ) {
    super(message);
    this.name = "AuthError";
  }
}

/**
 * Register a new user
 */
export async function register(data: RegisterData): Promise<TokenResponse> {
  const response = await fetch(`${API_BASE}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Registration failed" }));
    throw new AuthError(response.status, error.detail || "Registration failed");
  }

  return response.json();
}

/**
 * Login with email and password
 */
export async function login(data: LoginData): Promise<TokenResponse> {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Login failed" }));
    throw new AuthError(response.status, error.detail || "Login failed");
  }

  return response.json();
}

/**
 * Logout (invalidate all sessions)
 */
export async function logout(accessToken: string): Promise<void> {
  const response = await fetch(`${API_BASE}/auth/logout`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok && response.status !== 401) {
    // 401 means already logged out, which is fine
    throw new AuthError(response.status, "Logout failed");
  }
}

/**
 * Refresh tokens
 */
export async function refreshToken(refreshToken: string): Promise<TokenResponse> {
  const response = await fetch(`${API_BASE}/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });

  if (!response.ok) {
    throw new AuthError(response.status, "Token refresh failed");
  }

  return response.json();
}

/**
 * Get current user profile
 */
export async function getCurrentUser(accessToken: string): Promise<UserProfile> {
  const response = await fetch(`${API_BASE}/auth/me`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    throw new AuthError(response.status, "Failed to fetch user profile");
  }

  return response.json();
}

/**
 * Token storage helpers
 */
export const TOKEN_STORAGE_KEY = "paiid_tokens";

export interface StoredTokens {
  accessToken: string;
  refreshToken: string;
  expiresAt: number; // Timestamp when access token expires
}

export function saveTokens(tokens: TokenResponse): void {
  const stored: StoredTokens = {
    accessToken: tokens.access_token,
    refreshToken: tokens.refresh_token,
    expiresAt: Date.now() + 15 * 60 * 1000, // 15 minutes from now
  };

  if (typeof window !== "undefined") {
    localStorage.setItem(TOKEN_STORAGE_KEY, JSON.stringify(stored));
  }
}

export function getStoredTokens(): StoredTokens | null {
  if (typeof window === "undefined") return null;

  const stored = localStorage.getItem(TOKEN_STORAGE_KEY);
  if (!stored) return null;

  try {
    return JSON.parse(stored);
  } catch {
    return null;
  }
}

export function clearTokens(): void {
  if (typeof window !== "undefined") {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
  }
}

export function isTokenExpiringSoon(storedTokens: StoredTokens): boolean {
  // Refresh if token expires in less than 2 minutes
  return Date.now() >= storedTokens.expiresAt - 2 * 60 * 1000;
}
