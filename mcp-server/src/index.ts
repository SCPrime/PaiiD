#!/usr/bin/env node

/**
 * PaiiD Trading Platform MCP Server
 * 
 * Model Context Protocol server that allows AI assistants (like Claude Desktop)
 * to interact with the PaiiD Trading Platform API.
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from '@modelcontextprotocol/sdk/types.js';
import fetch from 'node-fetch';
import { config } from 'dotenv';

// Load environment variables
config();

const API_URL = process.env.PAIID_API_URL || 'https://paiid-backend.onrender.com';
const API_TOKEN = process.env.PAIID_API_TOKEN;
const REQUEST_TIMEOUT = parseInt(process.env.REQUEST_TIMEOUT || '30000');

if (!API_TOKEN) {
  console.error('Error: PAIID_API_TOKEN environment variable is required');
  process.exit(1);
}

/**
 * Helper function to make authenticated API requests
 */
async function apiRequest(endpoint: string, options: any = {}) {
  const url = `${API_URL}${endpoint}`;
  const headers = {
    'Authorization': `Bearer ${API_TOKEN}`,
    'Content-Type': 'application/json',
    ...options.headers,
  };

  const response = await fetch(url, {
    ...options,
    headers,
    timeout: REQUEST_TIMEOUT,
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`API request failed: ${response.status} - ${error}`);
  }

  return response.json();
}

/**
 * Define available tools
 */
const tools: Tool[] = [
  {
    name: 'get_account',
    description: 'Get account balance, buying power, and equity information',
    inputSchema: {
      type: 'object',
      properties: {},
      required: [],
    },
  },
  {
    name: 'get_positions',
    description: 'Get all open portfolio positions with current P&L',
    inputSchema: {
      type: 'object',
      properties: {},
      required: [],
    },
  },
  {
    name: 'execute_trade',
    description: 'Execute a paper trade order (buy or sell)',
    inputSchema: {
      type: 'object',
      properties: {
        symbol: {
          type: 'string',
          description: 'Stock ticker symbol (e.g., AAPL)',
        },
        qty: {
          type: 'number',
          description: 'Number of shares',
        },
        side: {
          type: 'string',
          enum: ['buy', 'sell'],
          description: 'Order side',
        },
        type: {
          type: 'string',
          enum: ['market', 'limit', 'stop', 'stop_limit'],
          description: 'Order type',
          default: 'market',
        },
        limitPrice: {
          type: 'number',
          description: 'Limit price (required for limit orders)',
        },
        stopPrice: {
          type: 'number',
          description: 'Stop price (required for stop orders)',
        },
      },
      required: ['symbol', 'qty', 'side', 'type'],
    },
  },
  {
    name: 'get_quote',
    description: 'Get real-time market quote for a symbol',
    inputSchema: {
      type: 'object',
      properties: {
        symbol: {
          type: 'string',
          description: 'Stock ticker symbol',
        },
      },
      required: ['symbol'],
    },
  },
  {
    name: 'get_market_indices',
    description: 'Get current values for major market indices (SPY, QQQ, DIA)',
    inputSchema: {
      type: 'object',
      properties: {},
      required: [],
    },
  },
  {
    name: 'get_historical_bars',
    description: 'Get historical OHLCV price data for a symbol',
    inputSchema: {
      type: 'object',
      properties: {
        symbol: {
          type: 'string',
          description: 'Stock ticker symbol',
        },
        interval: {
          type: 'string',
          enum: ['1min', '5min', '15min', '1hour', '1day'],
          description: 'Bar interval',
          default: '1day',
        },
        start: {
          type: 'string',
          description: 'Start date (YYYY-MM-DD)',
        },
        end: {
          type: 'string',
          description: 'End date (YYYY-MM-DD)',
        },
      },
      required: ['symbol'],
    },
  },
  {
    name: 'get_ai_recommendations',
    description: 'Get AI-generated trade recommendations',
    inputSchema: {
      type: 'object',
      properties: {
        symbols: {
          type: 'string',
          description: 'Comma-separated list of symbols to analyze',
        },
        strategy: {
          type: 'string',
          enum: ['momentum', 'mean_reversion', 'trend_following'],
          description: 'Trading strategy to apply',
        },
      },
      required: [],
    },
  },
  {
    name: 'get_news',
    description: 'Get latest market news articles',
    inputSchema: {
      type: 'object',
      properties: {
        symbols: {
          type: 'string',
          description: 'Filter news by symbols (comma-separated)',
        },
        limit: {
          type: 'number',
          description: 'Number of articles to return',
          default: 20,
        },
      },
      required: [],
    },
  },
  {
    name: 'get_order_history',
    description: 'Get list of submitted orders',
    inputSchema: {
      type: 'object',
      properties: {
        status: {
          type: 'string',
          enum: ['open', 'closed', 'all'],
          description: 'Filter by order status',
        },
        limit: {
          type: 'number',
          description: 'Maximum number of orders to return',
          default: 50,
        },
      },
      required: [],
    },
  },
];

/**
 * Tool handlers
 */
async function handleToolCall(name: string, args: any) {
  switch (name) {
    case 'get_account':
      return await apiRequest('/api/account');

    case 'get_positions':
      return await apiRequest('/api/positions');

    case 'execute_trade':
      return await apiRequest('/api/orders', {
        method: 'POST',
        body: JSON.stringify(args),
      });

    case 'get_quote': {
      const params = new URLSearchParams({ symbol: args.symbol });
      return await apiRequest(`/api/market/quote?${params}`);
    }

    case 'get_market_indices':
      return await apiRequest('/api/market/indices');

    case 'get_historical_bars': {
      const params = new URLSearchParams({
        symbol: args.symbol,
        interval: args.interval || '1day',
        ...(args.start && { start: args.start }),
        ...(args.end && { end: args.end }),
      });
      return await apiRequest(`/api/market/bars?${params}`);
    }

    case 'get_ai_recommendations': {
      const params = new URLSearchParams();
      if (args.symbols) params.append('symbols', args.symbols);
      if (args.strategy) params.append('strategy', args.strategy);
      return await apiRequest(`/api/ai/recommendations?${params}`);
    }

    case 'get_news': {
      const params = new URLSearchParams();
      if (args.symbols) params.append('symbols', args.symbols);
      if (args.limit) params.append('limit', args.limit.toString());
      return await apiRequest(`/api/news?${params}`);
    }

    case 'get_order_history': {
      const params = new URLSearchParams();
      if (args.status) params.append('status', args.status);
      if (args.limit) params.append('limit', args.limit.toString());
      return await apiRequest(`/api/orders?${params}`);
    }

    default:
      throw new Error(`Unknown tool: ${name}`);
  }
}

/**
 * Initialize MCP server
 */
async function main() {
  const server = new Server(
    {
      name: 'paiid-trading-server',
      version: '1.0.0',
    },
    {
      capabilities: {
        tools: {},
      },
    }
  );

  // Handle tool list requests
  server.setRequestHandler(ListToolsRequestSchema, async () => {
    return { tools };
  });

  // Handle tool call requests
  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    try {
      const result = await handleToolCall(request.params.name, request.params.arguments || {});
      
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(result, null, 2),
          },
        ],
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      return {
        content: [
          {
            type: 'text',
            text: `Error: ${errorMessage}`,
          },
        ],
        isError: true,
      };
    }
  });

  // Start server with stdio transport
  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.error('PaiiD MCP Server running on stdio');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
