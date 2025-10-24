import type { NextApiRequest, NextApiResponse } from "next";

import "@/pages/api/_startup";

/**
 * Claude chat endpoint - proxies to backend
 * Routes frontend requests to backend Claude API
 */
export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  // Only allow POST
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  // Get backend URL from environment variable (production default)
  const BACKEND_URL =
    process.env.NEXT_PUBLIC_BACKEND_API_BASE_URL || "https://paiid-backend.onrender.com";

  try {
    const { messages, max_tokens = 2000, system } = req.body;

    if (!messages || !Array.isArray(messages)) {
      return res.status(400).json({ error: "Invalid request: messages required" });
    }

    console.info("[Claude Chat API] Proxying to backend:", BACKEND_URL);

    // Call backend Claude endpoint
    const response = await fetch(`${BACKEND_URL}/api/claude/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        messages,
        max_tokens,
        system,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: "Unknown error" }));
      console.error("[Claude Chat API] Backend error:", response.status, errorData);
      return res.status(response.status).json({
        error: "Backend error",
        detail: errorData.detail || errorData.message,
      });
    }

    const data = await response.json();
    console.info("[Claude Chat API] ✅ Response received from backend");

    return res.status(200).json(data);
  } catch (error: any) {
    console.error("[Claude Chat API] Error:", error.message);
    return res.status(500).json({
      error: "Proxy error",
      detail: error.message,
    });
  }
}
