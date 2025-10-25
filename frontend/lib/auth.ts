/**
 * Frontend Authentication Utilities
 * Handles JWT token management, login, logout, and token refresh
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_API_BASE_URL || 'http://127.0.0.1:8001';

// Token storage keys
const ACCESS_TOKEN_KEY = 'paiid_access_token';
const REFRESH_TOKEN_KEY = 'paiid_refresh_token';
const TOKEN_EXPIRY_KEY = 'paiid_token_expiry';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name?: string;
  invite_code?: string;
}

/**
 * Store JWT tokens in localStorage
 */
export function storeTokens(tokens: TokenResponse): void {
  if (typeof window === 'undefined') return;

  localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access_token);
  localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);

  // JWT tokens typically expire in 15 minutes (900000ms)
  const expiryTime = Date.now() + 15 * 60 * 1000;
  localStorage.setItem(TOKEN_EXPIRY_KEY, expiryTime.toString());
}

/**
 * Get the current access token
 */
export function getAccessToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

/**
 * Get the refresh token
 */
export function getRefreshToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

/**
 * Check if token is expired or about to expire (within 1 minute)
 */
export function isTokenExpired(): boolean {
  if (typeof window === 'undefined') return true;

  const expiryStr = localStorage.getItem(TOKEN_EXPIRY_KEY);
  if (!expiryStr) return true;

  const expiry = parseInt(expiryStr, 10);
  const now = Date.now();

  // Consider expired if less than 1 minute remaining
  return now >= expiry - 60000;
}

/**
 * Clear all tokens from storage (logout)
 */
export function clearTokens(): void {
  if (typeof window === 'undefined') return;

  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(TOKEN_EXPIRY_KEY);
}

/**
 * Login with email and password
 */
export async function login(credentials: LoginCredentials): Promise<TokenResponse> {
  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(credentials),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Login failed' }));
    throw new Error(error.detail || 'Login failed');
  }

  const tokens: TokenResponse = await response.json();
  storeTokens(tokens);

  return tokens;
}

/**
 * Register a new user
 */
export async function register(userData: RegisterData): Promise<TokenResponse> {
  const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(userData),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Registration failed' }));
    throw new Error(error.detail || 'Registration failed');
  }

  const tokens: TokenResponse = await response.json();
  storeTokens(tokens);

  return tokens;
}

/**
 * Refresh the access token using the refresh token
 */
export async function refreshAccessToken(): Promise<TokenResponse | null> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return null;

  try {
    const response = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!response.ok) {
      clearTokens();
      return null;
    }

    const tokens: TokenResponse = await response.json();
    storeTokens(tokens);

    return tokens;
  } catch (error) {
    console.error('Token refresh failed:', error);
    clearTokens();
    return null;
  }
}

/**
 * Logout the current user
 */
export async function logout(): Promise<void> {
  const accessToken = getAccessToken();

  if (accessToken) {
    try {
      await fetch(`${API_BASE_URL}/api/auth/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
      });
    } catch (error) {
      console.error('Logout request failed:', error);
    }
  }

  clearTokens();
}

/**
 * Get authorization headers for API requests
 * Automatically refreshes token if expired
 */
export async function getAuthHeaders(): Promise<Record<string, string>> {
  // Check if token is expired
  if (isTokenExpired()) {
    const refreshed = await refreshAccessToken();
    if (!refreshed) {
      // Token refresh failed, user needs to login again
      clearTokens();
      throw new Error('Authentication expired. Please login again.');
    }
  }

  const token = getAccessToken();
  if (!token) {
    throw new Error('No authentication token found. Please login.');
  }

  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  };
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  if (typeof window === 'undefined') return false;

  const token = getAccessToken();
  return token !== null && !isTokenExpired();
}

/**
 * Make an authenticated API request
 */
export async function authenticatedFetch(
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> {
  const headers = await getAuthHeaders();

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      ...headers,
      ...options.headers,
    },
  });

  // If unauthorized, try refreshing token once
  if (response.status === 401) {
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      // Retry request with new token
      const newHeaders = await getAuthHeaders();
      return fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers: {
          ...newHeaders,
          ...options.headers,
        },
      });
    } else {
      // Refresh failed, clear tokens
      clearTokens();
      throw new Error('Session expired. Please login again.');
    }
  }

  return response;
}
