import type { NextApiRequest, NextApiResponse } from 'next';
import Anthropic from '@anthropic-ai/sdk';

/**
 * Direct Claude chat endpoint - bypasses proxy complexity
 * This endpoint allows frontend to call Claude AI directly through our backend
 */
export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  // Only allow POST
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  // Get API key from environment
  const apiKey = process.env.NEXT_PUBLIC_ANTHROPIC_API_KEY || process.env.ANTHROPIC_API_KEY;

  if (!apiKey) {
    console.error('[Claude Chat] ANTHROPIC_API_KEY not found in environment');
    return res.status(503).json({
      error: 'Claude API not configured',
      detail: 'ANTHROPIC_API_KEY missing'
    });
  }

  try {
    const { messages, max_tokens = 2000, system } = req.body;

    if (!messages || !Array.isArray(messages)) {
      return res.status(400).json({ error: 'Invalid request: messages required' });
    }

    console.log('[Claude Chat] Processing request with', messages.length, 'messages');

    // Initialize Anthropic client
    const anthropic = new Anthropic({
      apiKey: apiKey,
    });

    // Build request params
    const params: any = {
      model: 'claude-sonnet-4-5-20250929',
      max_tokens: max_tokens,
      messages: messages,
    };

    // Add system prompt if provided
    if (system) {
      if (typeof system === 'string') {
        params.system = [{ type: 'text', text: system }];
      } else {
        params.system = system;
      }
    }

    // Call Claude API
    const response = await anthropic.messages.create(params);

    // Extract text content
    let content = '';
    if (response.content && response.content.length > 0) {
      const firstBlock = response.content[0];
      if (firstBlock.type === 'text') {
        content = firstBlock.text;
      }
    }

    console.log('[Claude Chat] Response generated successfully');

    return res.status(200).json({
      content: content,
      model: response.model,
      role: 'assistant',
    });

  } catch (error: any) {
    console.error('[Claude Chat] Error:', error.message);
    return res.status(500).json({
      error: 'Claude API error',
      detail: error.message,
    });
  }
}
