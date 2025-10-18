/**
 * Centralized API Client for PaiiD
 *
 * Provides a consistent interface for making API calls to the backend
 * through the /api/proxy endpoint. Includes error handling, logging,
 * and TypeScript type safety.
 *
 * Usage:
 *   import { apiClient } from '@/lib/apiClient';
 *   const positions = await apiClient.get('/positions');
 *   await apiClient.post('/orders', { symbol: 'AAPL', qty: 10 });
 */

import { logger } from "./logger";

export interface APIError extends Error {
  status?: number;
  statusText?: string;
  data?: any;
}

export class APIClient {
  private baseUrl: string;
  private defaultHeaders: HeadersInit;

  constructor(baseUrl = "/api/proxy") {
    this.baseUrl = baseUrl;
    this.defaultHeaders = {
      "Content-Type": "application/json",
    };
  }

  /**
   * Create an API error with additional context
   */
  private createError(message: string, response?: Response, data?: any): APIError {
    const error = new Error(message) as APIError;
    if (response) {
      error.status = response.status;
      error.statusText = response.statusText;
    }
    if (data) {
      error.data = data;
    }
    return error;
  }

  /**
   * Make a GET request
   */
  async get<T = any>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    logger.debug(`GET ${url}`);

    try {
      const response = await fetch(url, {
        method: "GET",
        headers: { ...this.defaultHeaders, ...options?.headers },
        ...options,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw this.createError(
          `GET ${endpoint} failed: ${response.statusText}`,
          response,
          errorData
        );
      }

      const data = await response.json();
      logger.debug(`GET ${url} success`, { data });
      return data;
    } catch (error) {
      logger.error(`GET ${endpoint} error`, error);
      throw error;
    }
  }

  /**
   * Make a POST request
   */
  async post<T = any>(endpoint: string, body?: any, options?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    logger.debug(`POST ${url}`, { body });

    try {
      const response = await fetch(url, {
        method: "POST",
        headers: { ...this.defaultHeaders, ...options?.headers },
        body: body ? JSON.stringify(body) : undefined,
        ...options,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw this.createError(
          `POST ${endpoint} failed: ${response.statusText}`,
          response,
          errorData
        );
      }

      const data = await response.json();
      logger.debug(`POST ${url} success`, { data });
      return data;
    } catch (error) {
      logger.error(`POST ${endpoint} error`, error);
      throw error;
    }
  }

  /**
   * Make a PUT request
   */
  async put<T = any>(endpoint: string, body?: any, options?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    logger.debug(`PUT ${url}`, { body });

    try {
      const response = await fetch(url, {
        method: "PUT",
        headers: { ...this.defaultHeaders, ...options?.headers },
        body: body ? JSON.stringify(body) : undefined,
        ...options,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw this.createError(
          `PUT ${endpoint} failed: ${response.statusText}`,
          response,
          errorData
        );
      }

      const data = await response.json();
      logger.debug(`PUT ${url} success`, { data });
      return data;
    } catch (error) {
      logger.error(`PUT ${endpoint} error`, error);
      throw error;
    }
  }

  /**
   * Make a DELETE request
   */
  async delete<T = any>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    logger.debug(`DELETE ${url}`);

    try {
      const response = await fetch(url, {
        method: "DELETE",
        headers: { ...this.defaultHeaders, ...options?.headers },
        ...options,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw this.createError(
          `DELETE ${endpoint} failed: ${response.statusText}`,
          response,
          errorData
        );
      }

      const data = await response.json();
      logger.debug(`DELETE ${url} success`, { data });
      return data;
    } catch (error) {
      logger.error(`DELETE ${endpoint} error`, error);
      throw error;
    }
  }

  /**
   * Health check endpoint
   */
  async healthCheck(): Promise<{ status: string; time: string }> {
    return this.get("/health");
  }

  /**
   * Get account information
   */
  async getAccount(): Promise<any> {
    return this.get("/account");
  }

  /**
   * Get current positions
   */
  async getPositions(): Promise<any[]> {
    return this.get("/positions");
  }

  /**
   * Get market indices (Dow, NASDAQ)
   */
  async getMarketIndices(): Promise<any> {
    return this.get("/market/indices");
  }

  /**
   * Execute a trade
   */
  async executeTrade(order: {
    symbol: string;
    qty: number;
    side: "buy" | "sell";
    type: "market" | "limit";
    limitPrice?: number;
  }): Promise<any> {
    return this.post("/orders", order);
  }
}

// Singleton instance
export const apiClient = new APIClient();

// Default export
export default apiClient;
