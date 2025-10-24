# PaiiD Integration Options - Complete Overview

This document provides a high-level overview of all the ways you can connect and interact with the PaiiD Trading Platform.

## 🎯 Quick Navigation

| Integration Method | Best For | Setup Time | Documentation |
|-------------------|----------|------------|---------------|
| [ChatGPT Custom GPT](#chatgpt-custom-gpt) | ChatGPT Plus users | 5 minutes | [Quick Start](./CHATGPT_QUICKSTART.md) |
| [Claude Desktop (MCP)](#claude-desktop-mcp) | Claude Desktop users | 10 minutes | [MCP Server](./mcp-server/README.md) |
| [OpenAI API](#openai-api-integration) | Developers | 30 minutes | [Full Guide](./CHATGPT_INTEGRATION.md#3-openai-api-integration) |
| [GitHub Copilot](#github-copilot) | Developers | 5 minutes | [Full Guide](./CHATGPT_INTEGRATION.md#4-github-copilot-integration) |
| [Direct API](#direct-api-access) | Advanced users | Instant | [API Docs](./API_DOCUMENTATION.md) |

---

## ChatGPT Custom GPT

### What is it?
Create a custom ChatGPT that can interact with your PaiiD trading account through natural language.

### What you can do:
- ✅ Check portfolio and positions
- ✅ Execute paper trades
- ✅ Get real-time market data
- ✅ Receive AI recommendations
- ✅ View market news

### Requirements:
- ChatGPT Plus subscription ($20/month)
- Deployed PaiiD backend
- API token

### Setup:
1. Go to https://chat.openai.com/gpts/editor
2. Import the OpenAPI schema from `openapi.yaml`
3. Add your API token for authentication
4. Start chatting!

📖 **Full Guide:** [CHATGPT_QUICKSTART.md](./CHATGPT_QUICKSTART.md)

### Example Usage:
```
You: Check my portfolio
GPT: Your portfolio is worth $125,430.50 with 3 open positions...

You: Buy 10 shares of AAPL
GPT: Current price is $152.30. This will cost $1,523. Confirm?

You: Yes
GPT: ✓ Order submitted! Order ID: abc123xyz
```

---

## Claude Desktop (MCP)

### What is it?
Model Context Protocol server that connects Claude Desktop to your PaiiD API.

### What you can do:
- ✅ All ChatGPT GPT features
- ✅ More advanced analysis
- ✅ Better code generation
- ✅ Local execution (no cloud dependency)

### Requirements:
- Claude Desktop app (free)
- Node.js 18+
- PaiiD backend running

### Setup:
1. Install MCP server: `cd mcp-server && npm install && npm run build`
2. Configure Claude Desktop (edit `claude_desktop_config.json`)
3. Restart Claude Desktop
4. Tools appear automatically

📖 **Full Guide:** [mcp-server/README.md](./mcp-server/README.md)

### Example Usage:
```
You: Use the paiid tool to check my positions
Claude: I'll check your positions... [uses get_positions tool]

Your current positions:
• AAPL: 10 shares, +$18.00 (+1.20%)
• MSFT: 5 shares, -$12.50 (-0.66%)
• TSLA: 8 shares, +$45.20 (+2.40%)
```

---

## OpenAI API Integration

### What is it?
Replace or supplement Claude AI with OpenAI's GPT models in the PaiiD application.

### What you can do:
- ✅ Use GPT-4 for recommendations
- ✅ Switch between Claude and GPT
- ✅ Custom AI workflows
- ✅ Embedded chat in PaiiD UI

### Requirements:
- OpenAI API key
- Developer access to codebase
- Python & Node.js development environment

### Setup:
1. Install OpenAI SDK (Python & JavaScript)
2. Add API key to environment
3. Create OpenAI router/adapter
4. Update frontend to use OpenAI

📖 **Full Guide:** [CHATGPT_INTEGRATION.md](./CHATGPT_INTEGRATION.md#3-openai-api-integration)

### Code Example:
```python
# backend/app/routers/openai_router.py
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@router.post("/chat")
async def openai_chat(request: ChatRequest):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=request.messages
    )
    return {"content": response.choices[0].message.content}
```

---

## GitHub Copilot

### What is it?
AI pair programmer that understands PaiiD's codebase and helps with development.

### What you can do:
- ✅ Generate component code
- ✅ Debug issues
- ✅ Refactor existing code
- ✅ Write tests
- ✅ Explain complex code

### Requirements:
- GitHub Copilot subscription
- VS Code or JetBrains IDE
- Clone of PaiiD repository

### Setup:
1. Install GitHub Copilot extension
2. Sign in to GitHub
3. Open PaiiD project
4. Start coding!

📖 **Full Guide:** [CHATGPT_INTEGRATION.md](./CHATGPT_INTEGRATION.md#4-github-copilot-integration)

### Usage Tips:
- Open `CLAUDE.md` for project context
- Use comments to describe what you want
- Accept/reject suggestions with Tab/Esc
- Use Copilot Chat for explanations

---

## Direct API Access

### What is it?
Raw HTTP API for building custom integrations.

### What you can do:
- ✅ Build custom clients
- ✅ Integrate with other tools
- ✅ Automate workflows
- ✅ Create dashboards

### Requirements:
- Basic HTTP/REST knowledge
- API token
- Any programming language

### Setup:
Just make authenticated HTTP requests!

📖 **API Docs:** [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)  
📖 **OpenAPI Spec:** [openapi.yaml](./openapi.yaml)

### Example (curl):
```bash
# Get account info
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://paiid-backend.onrender.com/api/account

# Execute trade
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","qty":10,"side":"buy","type":"market"}' \
  https://paiid-backend.onrender.com/api/orders
```

### Example (Python):
```python
import requests

headers = {"Authorization": "Bearer YOUR_TOKEN"}
response = requests.get(
    "https://paiid-backend.onrender.com/api/positions",
    headers=headers
)
positions = response.json()
```

### Example (JavaScript):
```javascript
const response = await fetch(
  'https://paiid-backend.onrender.com/api/market/quote?symbol=AAPL',
  {
    headers: {
      'Authorization': 'Bearer YOUR_TOKEN'
    }
  }
);
const quote = await response.json();
```

---

## Comparison Matrix

| Feature | ChatGPT GPT | Claude MCP | OpenAI API | Copilot | Direct API |
|---------|-------------|------------|------------|---------|------------|
| **Ease of Setup** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Natural Language** | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Trade Execution** | ✅ | ✅ | ✅ | ❌ | ✅ |
| **Code Generation** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ |
| **Custom Integration** | ❌ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ | ⭐⭐⭐⭐⭐ |
| **Offline Use** | ❌ | ⭐⭐⭐ | ❌ | ⭐⭐⭐ | ✅ |
| **Cost** | $20/mo | Free | Pay per use | $10/mo | Free |

---

## Which One Should I Choose?

### For Trading & Portfolio Management:
👉 **ChatGPT Custom GPT** - Easiest setup, great natural language interface

### For Development & Code Assistance:
👉 **GitHub Copilot** or **Claude Desktop MCP** - Best for writing code

### For Custom Applications:
👉 **Direct API** or **OpenAI API Integration** - Full control

### For Advanced Analysis:
👉 **Claude Desktop MCP** - Most powerful reasoning

---

## Getting Your API Token

All integration methods require an API token. Get it from your backend `.env` file:

```env
API_TOKEN=rnd_bDRqi1TvLvd3rC78yvUSgDraH2Kl
```

**Security Notes:**
- ⚠️ Never commit tokens to Git
- ⚠️ Don't share tokens publicly
- ⚠️ Revoke and regenerate if compromised
- ⚠️ This is paper trading (no real money)

---

## Common Issues

### "Could not connect to server"
- Verify backend is running: https://paiid-backend.onrender.com/api/health
- Check API URL is correct
- Ensure no firewall blocking

### "Authentication failed"
- Check token format: `Bearer <token>` (with space)
- Verify token matches backend `.env`
- Ensure header name is `Authorization`

### "Invalid symbol" errors
- Use correct ticker symbols (AAPL not Apple)
- Check if market is open
- Verify Tradier API credentials in backend

---

## Next Steps

1. **Choose your integration method** from the table above
2. **Follow the setup guide** linked for that method
3. **Test with simple queries** (check portfolio, get quote)
4. **Explore advanced features** (AI recommendations, news, etc.)

---

## Support & Resources

- 📖 [Full Integration Guide](./CHATGPT_INTEGRATION.md)
- 🚀 [Quick Start for ChatGPT](./CHATGPT_QUICKSTART.md)
- 📚 [API Documentation](./API_DOCUMENTATION.md)
- 🤖 [MCP Server Guide](./mcp-server/README.md)
- 💻 [Developer Setup](./DEVELOPER_SETUP.md)
- 🐛 [GitHub Issues](https://github.com/SCPrime/PaiiD/issues)

---

**Ready to connect? Pick your integration method and get started! 🚀**
