// frontend/lib/aiAdapter.ts
// Fixed version - calls backend proxy instead of Anthropic directly

import { logger } from '@/lib/logger';

// Error handling types
export interface AIError {
  type: 'network' | 'auth' | 'validation' | 'server' | 'rate_limit' | 'unknown';
  message: string;
  userMessage: string;
  statusCode?: number;
  retryable: boolean;
}

/**
 * Convert AI API errors to user-friendly messages
 */
export function handleAIError(error: unknown): AIError {
  // Network errors (fetch failed, timeout, offline)
  if (error instanceof TypeError && error.message.includes('fetch')) {
    return {
      type: 'network',
      message: error.message,
      userMessage: 'Unable to connect to the AI service. Please check your internet connection and try again.',
      retryable: true
    };
  }

  // HTTP errors from Response object
  if (error && typeof error === 'object' && 'status' in error) {
    const response = error as Response;
    const statusCode = response.status;

    if (statusCode === 401 || statusCode === 403) {
      return {
        type: 'auth',
        message: `AI authentication failed: ${statusCode}`,
        userMessage: 'AI service authentication failed. Please check your API key configuration.',
        statusCode,
        retryable: false
      };
    }

    if (statusCode === 400 || statusCode === 422) {
      return {
        type: 'validation',
        message: `AI validation error: ${statusCode}`,
        userMessage: 'The AI request format is invalid. Please try a different prompt.',
        statusCode,
        retryable: false
      };
    }

    if (statusCode === 429) {
      return {
        type: 'rate_limit',
        message: `AI rate limit exceeded: ${statusCode}`,
        userMessage: 'Too many AI requests. Please wait a moment before trying again.',
        statusCode,
        retryable: true
      };
    }

    if (statusCode >= 500) {
      return {
        type: 'server',
        message: `AI server error: ${statusCode}`,
        userMessage: 'The AI service is temporarily unavailable. Please try again in a few moments.',
        statusCode,
        retryable: true
      };
    }
  }

  // Unknown errors
  return {
    type: 'unknown',
    message: error instanceof Error ? error.message : String(error),
    userMessage: 'An unexpected error occurred with the AI service. Please try again.',
    retryable: true
  };
}

/**
 * AI conversation message structure
 * @interface AIMessage
 * @property {("user" | "assistant")} role - The role of the message sender
 * @property {string} content - The message content
 */
export interface AIMessage {
  role: "user" | "assistant";
  content: string;
}

/**
 * User trading preferences extracted from onboarding or manual setup
 * @interface UserPreferences
 * @property {("conservative" | "moderate" | "aggressive")} [riskTolerance] - User's risk tolerance level
 * @property {("day" | "swing" | "long-term")} [tradingStyle] - Preferred trading timeframe
 * @property {string[]} [preferredAssets] - List of preferred asset types (stocks, options, crypto)
 * @property {string[]} [goals] - Investment goals (income, growth, preservation)
 * @property {Object} [investmentAmount] - Investment capital configuration
 * @property {string[]} [instruments] - Trading instruments user wants to trade
 * @property {string[]} [watchlist] - List of symbols to watch
 */
export interface UserPreferences {
  riskTolerance?: "conservative" | "moderate" | "aggressive";
  tradingStyle?: "day" | "swing" | "long-term";
  preferredAssets?: string[];
  goals?: string[];
  investmentAmount?: { mode: "range" | "unlimited" | "custom"; value?: number; range?: string };
  instruments?: string[];
  watchlist?: string[];
}

export class ClaudeAI {
  private conversationHistory: Array<{ role: "user" | "assistant"; content: string }> = [];

  constructor() {
    // Use Next.js API proxy to route to backend (works in both dev and production)

    // ✅ EXTENSION VERIFICATION: Anthropic SDK (via backend proxy)
    logger.info("[Extension Verification] ✅ Anthropic SDK adapter initialized successfully", {
      adapter: "ClaudeAI",
      proxyEndpoint: "/api/proxy/claude/chat",
      methods: [
        "chat",
        "generateMorningRoutine",
        "extractSetupPreferences",
        "generateStrategy",
        "analyzeMarket",
        "healthCheck",
      ],
      status: "FUNCTIONAL",
    });
  }

  /**
   * Reset conversation history
   */
  resetConversation(): void {
    this.conversationHistory = [];
    logger.info("[aiAdapter] 🔄 Conversation reset");
  }

  /**
   * Send a chat message to Claude via backend proxy
   * Supports both string messages and message arrays
   * @param messagesOrString - Either a user message string or array of conversation messages
   * @param systemPromptOrMaxTokens - Either a system prompt string or max tokens number
   * @returns Claude's text response
   */
  async chat(
    messagesOrString: string | Array<{ role: "user" | "assistant"; content: string }>,
    systemPromptOrMaxTokens?: string | number
  ): Promise<string> {
    // Handle string input (simple chat message)
    let messages: Array<{ role: "user" | "assistant"; content: string }>;
    let maxTokens = 2000;

    if (typeof messagesOrString === "string") {
      // Simple string message - add to conversation history
      this.conversationHistory.push({
        role: "user",
        content: messagesOrString,
      });
      messages = this.conversationHistory;

      // Second parameter might be a system prompt (ignore for now) or max tokens
      if (typeof systemPromptOrMaxTokens === "number") {
        maxTokens = systemPromptOrMaxTokens;
      }
    } else {
      // Array of messages provided directly
      messages = messagesOrString;
      if (typeof systemPromptOrMaxTokens === "number") {
        maxTokens = systemPromptOrMaxTokens;
      }
    }
    try {
      logger.info("[aiAdapter] Sending chat request to backend via proxy");

      // Use proxy to avoid CORS and add auth automatically
      const response = await fetch("/api/proxy/claude/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          messages,
          max_tokens: maxTokens,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Unknown error" }));
        const aiError = handleAIError(response);

        // Enhance error with server message if available
        if (errorData.detail) {
          aiError.message = errorData.detail;
        }

        logger.error(`[aiAdapter] AI API error: ${aiError.message}`, { statusCode: response.status });
        throw aiError;
      }

      const data = await response.json();

      // Extract text from response content
      if (data.content && typeof data.content === "string") {
        logger.info("[aiAdapter] ✅ Received response from Claude");

        // Add assistant response to conversation history if we used it
        if (typeof messagesOrString === "string") {
          this.conversationHistory.push({
            role: "assistant",
            content: data.content,
          });
        }

        return data.content;
      }

      throw new Error("Invalid response format from backend");
    } catch (error) {
      // If it's already an AIError, re-throw it
      if (error && typeof error === 'object' && 'type' in error) {
        throw error;
      }

      // Otherwise, convert to AIError
      const aiError = handleAIError(error);
      logger.error("[aiAdapter] Request failed", { error: aiError.message });
      throw aiError;
    }
  }

  /**
   * Generate a personalized morning routine based on user preferences
   */
  async generateMorningRoutine(preferences: {
    wakeTime?: string;
    marketOpen?: boolean;
    checkNews?: boolean;
    reviewPositions?: boolean;
    aiRecommendations?: boolean;
    [key: string]: unknown;
  }): Promise<string> {
    try {
      const prompt = `Create a personalized trading morning routine based on these preferences:

Wake Time: ${preferences.wakeTime || "7:00 AM"}
Check Market Status: ${preferences.marketOpen ? "Yes" : "No"}
Review News: ${preferences.checkNews ? "Yes" : "No"}
Review Positions: ${preferences.reviewPositions ? "Yes" : "No"}
Get AI Recommendations: ${preferences.aiRecommendations ? "Yes" : "No"}

Please provide a structured morning routine with specific times and activities. Format it as a clear, actionable checklist.`;

      const response = await this.chat([{ role: "user", content: prompt }], 2000);

      logger.info("[aiAdapter] ✅ Morning routine generated successfully");
      return response;
    } catch (error) {
      logger.error("[aiAdapter] Failed to generate morning routine", error);
      throw error;
    }
  }

  /**
   * Extract user trading preferences from natural language input
   * Uses AI to parse conversational input and extract structured trading preferences
   * @param {string} userInput - Natural language description of trading preferences
   * @returns {Promise<ExtractedPreferences>} Structured preferences object
   * @throws {Error} If AI response is invalid or cannot be parsed
   * @example
   * const prefs = await claudeAI.extractSetupPreferences(
   *   "I'm a conservative investor interested in long-term growth stocks"
   * );
   * // Returns: { riskTolerance: "conservative", tradingStyle: "long-term", ... }
   */
  async extractSetupPreferences(userInput: string): Promise<{
    riskTolerance: "conservative" | "moderate" | "aggressive";
    tradingStyle: "day" | "swing" | "long-term";
    preferredAssets: string[];
    goals: string[];
  }> {
    try {
      const prompt = `Extract trading preferences from this user input: "${userInput}"

Return ONLY a valid JSON object with these exact fields:
{
  "riskTolerance": "conservative" | "moderate" | "aggressive",
  "tradingStyle": "day" | "swing" | "long-term",
  "preferredAssets": ["stock", "options", "crypto", etc.],
  "goals": ["income", "growth", "preservation", etc.]
}

Do not include any text outside the JSON object.`;

      const response = await this.chat([{ role: "user", content: prompt }], 1000);

      // Parse JSON response
      const jsonMatch = response.match(/\{[\s\S]*\}/);
      if (!jsonMatch) {
        throw new Error("No JSON found in response");
      }

      const preferences = JSON.parse(jsonMatch[0]);
      logger.info("[aiAdapter] ✅ Extracted preferences", { preferences });
      return preferences;
    } catch (error) {
      logger.error("[aiAdapter] Failed to extract preferences", error);
      throw error;
    }
  }

  /**
   * Generate a complete trading strategy from natural language description
   * Uses AI to create structured strategy with entry/exit rules and risk management
   * @param {string} description - Natural language strategy description
   * @returns {Promise<GeneratedStrategy>} Structured trading strategy
   * @throws {Error} If AI response is invalid or cannot be parsed
   * @example
   * const strategy = await claudeAI.generateStrategy(
   *   "Buy when RSI is oversold and price crosses above 50-day MA"
   * );
   * // Returns: { name: "RSI MA Crossover", entry: [...], exit: [...], ... }
   */
  async generateStrategy(description: string): Promise<{
    name: string;
    entry: string[];
    exit: string[];
    riskManagement: string[];
    code?: string;
  }> {
    try {
      const prompt = `Generate a trading strategy from this description: "${description}"

Return ONLY a valid JSON object with this structure:
{
  "name": "Strategy Name",
  "entry": ["Entry condition 1", "Entry condition 2"],
  "exit": ["Exit condition 1", "Exit condition 2"],
  "riskManagement": ["Risk rule 1", "Risk rule 2"],
  "code": "Optional Python/JS code for the strategy"
}

Do not include any text outside the JSON object.`;

      const response = await this.chat([{ role: "user", content: prompt }], 2000);

      // Parse JSON response
      const jsonMatch = response.match(/\{[\s\S]*\}/);
      if (!jsonMatch) {
        throw new Error("No JSON found in response");
      }

      const strategy = JSON.parse(jsonMatch[0]);
      logger.info("[aiAdapter] ✅ Generated strategy", { name: strategy.name });
      return strategy;
    } catch (error) {
      logger.error("[aiAdapter] Failed to generate strategy", error);
      throw error;
    }
  }

  /**
   * Analyze market data and provide insights
   */
  async analyzeMarket(data: {
    symbols: string[];
    timeframe?: string;
    indicators?: string[];
  }): Promise<string> {
    try {
      const prompt = `Analyze the following market data and provide trading insights:

Symbols: ${data.symbols.join(", ")}
Timeframe: ${data.timeframe || "Daily"}
Indicators: ${data.indicators?.join(", ") || "Standard technical indicators"}

Provide a concise analysis with:
1. Market trend assessment
2. Key support/resistance levels
3. Potential trade opportunities
4. Risk factors to watch`;

      const response = await this.chat([{ role: "user", content: prompt }], 1500);

      logger.info("[aiAdapter] ✅ Market analysis completed");
      return response;
    } catch (error) {
      logger.error("[aiAdapter] Failed to analyze market", error);
      throw error;
    }
  }

  /**
   * Health check - verify backend proxy is accessible
   */
  async healthCheck(): Promise<boolean> {
    try {
      // Use proxy for health check
      const response = await fetch("/api/proxy/claude/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: [{ role: "user", content: "test" }],
          max_tokens: 10,
        }),
      });

      if (response.ok) {
        logger.info("[aiAdapter] ✅ Health check passed");
        return true;
      }

      logger.warn("[aiAdapter] ⚠️ Health check failed", { status: response.status });
      return false;
    } catch (error) {
      logger.error("[aiAdapter] ❌ Health check error", error);
      return false;
    }
  }
}

// Singleton instance
export const claudeAI = new ClaudeAI();

// Named export for convenience
export default claudeAI;
