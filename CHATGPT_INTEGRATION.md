# ChatGPT Integration Guide for PaiiD

This guide explains how to connect the PaiiD repository to ChatGPT in multiple ways. Choose the approach that best fits your needs.

## Table of Contents

1. [ChatGPT Custom GPT with Actions](#1-chatgpt-custom-gpt-with-actions)
2. [Model Context Protocol (MCP) Server](#2-model-context-protocol-mcp-server)
3. [OpenAI API Integration](#3-openai-api-integration)
4. [GitHub Copilot Integration](#4-github-copilot-integration)

---

## 1. ChatGPT Custom GPT with Actions

Create a Custom GPT that can interact with your deployed PaiiD API.

### Prerequisites

- ChatGPT Plus subscription
- Deployed PaiiD backend (https://paiid-backend.onrender.com)
- API token for authentication

### Step 1: Create OpenAPI Specification

The OpenAPI spec is located at `/openapi.yaml` in the root directory. This file describes all available API endpoints.

### Step 2: Create Custom GPT

1. Go to https://chat.openai.com/gpts/editor
2. Click "Create a GPT"
3. Configure the GPT:
   - **Name**: PaiiD Trading Assistant
   - **Description**: AI-powered trading platform assistant that can check portfolio, execute trades, and provide market analysis
   - **Instructions**: See `chatgpt-instructions.txt`

### Step 3: Add Actions

1. In the GPT Editor, go to "Configure" → "Actions"
2. Click "Create new action"
3. Import the OpenAPI schema from `/openapi.yaml`
4. Configure authentication:
   - Type: API Key
   - Header name: `Authorization`
   - Value: `Bearer YOUR_API_TOKEN`
5. Set the server URL: `https://paiid-backend.onrender.com`

### Step 4: Test the GPT

Try these example prompts:
- "What's my current portfolio status?"
- "Show me my active positions"
- "Execute a paper trade: buy 10 shares of AAPL"
- "What are the market indices showing?"

### Available Actions

The Custom GPT can:
- ✅ Check portfolio positions and balances
- ✅ View active positions and P&L
- ✅ Execute paper trades (buy/sell)
- ✅ Get real-time market data and quotes
- ✅ Retrieve market indices (SPY, QQQ, DIA)
- ✅ Access AI recommendations
- ✅ Check system health

---

## 2. Model Context Protocol (MCP) Server

Use PaiiD with Claude Desktop or other MCP-compatible clients.

### What is MCP?

Model Context Protocol allows AI assistants to access external tools and data sources. Claude Desktop can use MCP servers to interact with your PaiiD instance.

### Setup for Claude Desktop

1. **Install Claude Desktop** (if not already installed)
   - Download from: https://claude.ai/download

2. **Configure MCP Server**

   Edit your Claude Desktop config file:
   
   **macOS/Linux**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

   ```json
   {
     "mcpServers": {
       "paiid-trading": {
         "command": "npx",
         "args": [
           "-y",
           "@modelcontextprotocol/server-fetch"
         ],
         "env": {
           "PAIID_API_URL": "https://paiid-backend.onrender.com",
           "PAIID_API_TOKEN": "your_api_token_here"
         }
       }
     }
   }
   ```

3. **Restart Claude Desktop**

4. **Test the Integration**

   In Claude Desktop, try:
   - "Use the paiid-trading tool to check my portfolio"
   - "What positions do I have open?"
   - "Get current market data for SPY"

### Custom MCP Server (Advanced)

For more control, you can create a custom MCP server. See `/mcp-server/` directory for implementation:

```bash
cd mcp-server
npm install
npm run build
npm start
```

Configure in Claude Desktop:
```json
{
  "mcpServers": {
    "paiid": {
      "command": "node",
      "args": ["/path/to/PaiiD/mcp-server/dist/index.js"],
      "env": {
        "PAIID_API_URL": "https://paiid-backend.onrender.com",
        "PAIID_API_TOKEN": "your_api_token_here"
      }
    }
  }
}
```

---

## 3. OpenAI API Integration

Replace or supplement Claude AI with OpenAI's GPT models.

### Backend Integration

1. **Install OpenAI SDK**

   ```bash
   cd backend
   pip install openai
   ```

2. **Add Environment Variable**

   In `backend/.env`:
   ```env
   OPENAI_API_KEY=sk-proj-your-key-here
   ```

3. **Create OpenAI Router** (optional)

   The repository already uses Claude (Anthropic). To add OpenAI support:

   ```python
   # backend/app/routers/openai_router.py
   from openai import OpenAI
   from fastapi import APIRouter
   
   router = APIRouter(prefix="/openai", tags=["openai"])
   client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
   
   @router.post("/chat")
   async def openai_chat(request: ChatRequest):
       response = client.chat.completions.create(
           model="gpt-4o",
           messages=[{"role": m.role, "content": m.content} for m in request.messages]
       )
       return {"content": response.choices[0].message.content}
   ```

4. **Register Router**

   In `backend/app/main.py`:
   ```python
   from app.routers import openai_router
   app.include_router(openai_router.router, prefix="/api")
   ```

### Frontend Integration

1. **Install OpenAI SDK**

   ```bash
   cd frontend
   npm install openai
   ```

2. **Add Environment Variable**

   In `frontend/.env.local`:
   ```env
   NEXT_PUBLIC_OPENAI_API_KEY=sk-proj-your-key-here
   ```

3. **Create OpenAI Adapter**

   ```typescript
   // frontend/lib/openaiAdapter.ts
   import OpenAI from 'openai';
   
   const openai = new OpenAI({
     apiKey: process.env.NEXT_PUBLIC_OPENAI_API_KEY,
     dangerouslyAllowBrowser: true // For client-side usage
   });
   
   export async function chatWithGPT(messages: any[]) {
     const response = await openai.chat.completions.create({
       model: 'gpt-4o',
       messages: messages
     });
     return response.choices[0].message.content;
   }
   ```

### Switching AI Providers

To allow users to choose between Claude and GPT:

```typescript
// frontend/components/AIProvider.tsx
export function useAI(provider: 'claude' | 'openai') {
  if (provider === 'openai') {
    return useOpenAI();
  }
  return useClaude();
}
```

---

## 4. GitHub Copilot Integration

Use GitHub Copilot to assist with development in this repository.

### Setup

1. **Install GitHub Copilot**
   - VS Code Extension: Search "GitHub Copilot" in Extensions
   - JetBrains: https://plugins.jetbrains.com/plugin/17718-github-copilot

2. **Sign in to GitHub**
   - Must have GitHub Copilot subscription
   - Authorize VS Code/IDE to access GitHub

3. **Enable Copilot**
   - Open VS Code settings
   - Search "Copilot"
   - Enable "GitHub Copilot: Enable"

### Using Copilot with PaiiD

GitHub Copilot will understand:
- **Frontend**: React, TypeScript, Next.js patterns
- **Backend**: FastAPI, Python async patterns
- **Trading**: Alpaca API, market data structures
- **AI**: Anthropic Claude SDK patterns

**Tip**: Open `CLAUDE.md` in your editor to give Copilot context about the project architecture.

### Copilot Chat

Use Copilot Chat for:
- "Explain how the radial menu works"
- "Help me add a new workflow component"
- "Debug this API endpoint"
- "Refactor this component to match the theme"

---

## Configuration Files Reference

### OpenAPI Specification
Located at: `/openapi.yaml`

### Custom GPT Instructions
Located at: `/chatgpt-instructions.txt`

### MCP Server
Located at: `/mcp-server/`

### Example Requests

**Portfolio Status:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://paiid-backend.onrender.com/api/account
```

**Execute Trade:**
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","qty":10,"side":"buy","type":"market"}' \
  https://paiid-backend.onrender.com/api/orders
```

**Market Data:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://paiid-backend.onrender.com/api/market/indices
```

---

## Security Considerations

⚠️ **Important Security Notes:**

1. **API Keys**: Never commit API keys to the repository
2. **Authentication**: Always use environment variables for tokens
3. **CORS**: Configure ALLOW_ORIGIN in backend .env
4. **Paper Trading**: Default configuration uses Alpaca Paper Trading (no real money)
5. **Rate Limiting**: API has rate limits to prevent abuse

### Setting Up Authentication

1. Generate a secure API token:
   ```bash
   openssl rand -base64 32
   ```

2. Set in backend `.env`:
   ```env
   API_TOKEN=your_generated_token
   ```

3. Use in all API requests:
   ```
   Authorization: Bearer your_generated_token
   ```

---

## Troubleshooting

### Custom GPT Issues

**Problem**: "Action authentication failed"
- Solution: Check API token in GPT Actions configuration
- Verify token format: `Bearer <token>`

**Problem**: "Could not reach server"
- Solution: Ensure backend is deployed and running
- Check URL: https://paiid-backend.onrender.com/api/health

### MCP Server Issues

**Problem**: "MCP server not found"
- Solution: Restart Claude Desktop after config changes
- Check config file path is correct

**Problem**: "Connection refused"
- Solution: Verify PAIID_API_URL is correct
- Ensure backend is accessible from your machine

### OpenAI Integration Issues

**Problem**: "OpenAI API key not configured"
- Solution: Set OPENAI_API_KEY in .env files
- Restart both frontend and backend servers

**Problem**: "Rate limit exceeded"
- Solution: OpenAI has usage limits based on your plan
- Consider implementing caching or request throttling

---

## Example Use Cases

### Trading Assistant GPT

**Prompt**: "I want to build a diversified tech portfolio with $10,000. What should I buy?"

**GPT Response**: 
1. Checks current market conditions via `/api/market/indices`
2. Gets AI recommendations via `/api/ai/recommendations`
3. Suggests allocation and asks for confirmation
4. Executes trades via `/api/orders`

### Portfolio Monitor

**Prompt**: "Give me a daily portfolio summary"

**GPT Response**:
1. Calls `/api/account` for balance
2. Calls `/api/positions` for positions
3. Formats P&L data
4. Suggests actions based on performance

### Market Analysis

**Prompt**: "What's happening in the market today?"

**GPT Response**:
1. Calls `/api/market/indices` for SPY/QQQ/DIA
2. Calls `/api/news` for latest headlines
3. Provides sentiment analysis
4. Suggests trading opportunities

---

## Additional Resources

- **API Documentation**: `/API_DOCUMENTATION.md`
- **Architecture Guide**: `/CLAUDE.md`
- **Development Setup**: `/DEVELOPER_SETUP.md`
- **Contributing**: `/CONTRIBUTING.md`

---

## Support

For issues with ChatGPT integration:
1. Check this guide first
2. Review API documentation
3. Test API endpoints manually with curl
4. Open a GitHub issue with details

---

**Built for AI-first trading** 🤖📈
