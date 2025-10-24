# PaiiD Integration Architecture

This document explains how different integration methods connect to the PaiiD platform.

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     AI Integration Layer                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   ChatGPT    │  │    Claude    │  │   OpenAI     │          │
│  │  Custom GPT  │  │   Desktop    │  │     API      │          │
│  │              │  │     (MCP)    │  │              │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                  │                   │
│         │ OpenAPI         │ MCP Protocol     │ SDK Calls        │
│         │ Actions         │ (stdio)          │                  │
│         │                 │                  │                   │
└─────────┼─────────────────┼──────────────────┼───────────────────┘
          │                 │                  │
          │                 │                  │
          ▼                 ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                       PaiiD Backend API                          │
│                   (FastAPI - Port 8001)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────┐       │
│  │              API Routers                              │       │
│  ├──────────────────────────────────────────────────────┤       │
│  │  /api/account      - Account info                    │       │
│  │  /api/positions    - Portfolio positions             │       │
│  │  /api/orders       - Trade execution                 │       │
│  │  /api/market/*     - Market data & quotes            │       │
│  │  /api/ai/*         - AI recommendations              │       │
│  │  /api/claude/*     - Claude API proxy                │       │
│  │  /api/news         - Market news                     │       │
│  └──────────────────────────────────────────────────────┘       │
│                                                                   │
│  Authentication: Bearer Token (API_TOKEN env var)                │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
          │                              │
          │                              │
          ▼                              ▼
┌──────────────────────┐      ┌────────────────────────┐
│   Tradier API        │      │   Alpaca API           │
│   (Market Data)      │      │   (Paper Trading)      │
├──────────────────────┤      ├────────────────────────┤
│ • Real-time quotes   │      │ • Order execution      │
│ • Historical bars    │      │ • Position tracking    │
│ • Options data       │      │ • Account balance      │
│ • Market news        │      │ • Paper trades only    │
└──────────────────────┘      └────────────────────────┘
```

## Integration Methods Comparison

| Method | Setup Time | Best For | Cost |
|--------|-----------|----------|------|
| ChatGPT Custom GPT | 5 min | Trading & Analysis | $20/mo |
| Claude Desktop MCP | 10 min | Development | Free |
| OpenAI API | 30 min | Custom Apps | Pay per use |
| Direct API | Instant | Automation | Free |

## Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Security Layers                         │
├─────────────────────────────────────────────────────────────┤
│  1. HTTPS/TLS Encryption                                     │
│  2. Bearer Token Authentication                              │
│  3. CORS Policy                                              │
│  4. Rate Limiting (optional)                                 │
│  5. Paper Trading Only                                       │
│  6. Environment Variables                                    │
└─────────────────────────────────────────────────────────────┘
```

## Resources

- [OpenAPI Specification](../openapi.yaml)
- [MCP Server Implementation](../mcp-server/)
- [API Documentation](../API_DOCUMENTATION.md)
- [Integration Guide](../CHATGPT_INTEGRATION.md)
