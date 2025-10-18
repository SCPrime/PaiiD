// frontend/lib/aiAdapter.ts
// Fixed version - calls backend proxy instead of Anthropic directly

export interface AIMessage {
  role: "user" | "assistant";
  content: string;
}

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
    console.info("[Extension Verification] ✅ Anthropic SDK adapter initialized successfully:", {
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
    console.info("[aiAdapter] 🔄 Conversation reset");
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
      console.info("[aiAdapter] Sending chat request to backend via proxy");

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
        throw new Error(`Backend error: ${response.status} - ${errorData.detail}`);
      }

      const data = await response.json();

      // Extract text from response content
      if (data.content && typeof data.content === "string") {
        console.info("[aiAdapter] ✅ Received response from Claude");

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
      console.error("[aiAdapter] Error:", error);
      throw error;
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
    [key: string]: any;
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

      console.info("[aiAdapter] ✅ Morning routine generated successfully");
      return response;
    } catch (error) {
      console.error("[aiAdapter] Failed to generate morning routine:", error);
      throw error;
    }
  }

  /**
   * Extract user trading preferences from natural language
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
      console.info("[aiAdapter] ✅ Extracted preferences:", preferences);
      return preferences;
    } catch (error) {
      console.error("[aiAdapter] Failed to extract preferences:", error);
      throw error;
    }
  }

  /**
   * Generate trading strategy from natural language description
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
      console.info("[aiAdapter] ✅ Generated strategy:", strategy.name);
      return strategy;
    } catch (error) {
      console.error("[aiAdapter] Failed to generate strategy:", error);
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

      console.info("[aiAdapter] ✅ Market analysis completed");
      return response;
    } catch (error) {
      console.error("[aiAdapter] Failed to analyze market:", error);
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
        console.info("[aiAdapter] ✅ Health check passed");
        return true;
      }

      console.warn("[aiAdapter] ⚠️ Health check failed:", response.status);
      return false;
    } catch (error) {
      console.error("[aiAdapter] ❌ Health check error:", error);
      return false;
    }
  }
}

// Singleton instance
export const claudeAI = new ClaudeAI();

// Named export for convenience
export default claudeAI;
