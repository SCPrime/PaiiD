# Quick Start: Connect PaiiD to ChatGPT Custom GPT

This is a 5-minute guide to create a Custom GPT that can interact with your PaiiD trading platform.

## Prerequisites

✅ ChatGPT Plus subscription  
✅ Deployed PaiiD backend (https://paiid-backend.onrender.com)  
✅ API token from your backend `.env` file

## Step-by-Step Instructions

### 1. Get Your API Token

Your API token is in the backend `.env` file:

```env
API_TOKEN=rnd_bDRqi1TvLvd3rC78yvUSgDraH2Kl
```

**⚠️ Important:** This token grants access to your trading account. Keep it secure!

### 2. Create Custom GPT

1. Go to: https://chat.openai.com/gpts/editor
2. Click **"Create a GPT"**
3. Switch to **"Configure"** tab

### 3. Configure Basic Settings

**Name:**
```
PaiiD Trading Assistant
```

**Description:**
```
AI-powered trading assistant for the PaiiD platform. Can check portfolio positions, execute paper trades, analyze market data, and provide trade recommendations.
```

**Instructions:**
```
You are the PaiiD Trading Assistant. You help users manage their investment portfolio through the PaiiD Trading Platform API.

CORE CAPABILITIES:
- Check portfolio positions and P&L
- Execute paper trades (buy/sell)
- Get real-time market quotes
- View market indices (SPY, QQQ, DIA)
- Access AI trade recommendations
- Retrieve market news

IMPORTANT RULES:
1. This is PAPER TRADING - no real money is at risk
2. ALWAYS confirm trade details before executing
3. Present data in clear, formatted tables
4. Use $ for currency, % for percentages
5. Explain financial concepts when needed

BEFORE EXECUTING TRADES:
1. Get current quote
2. Calculate estimated cost
3. Show trade preview
4. Wait for user confirmation
5. Then execute

Be professional, clear, and helpful. Celebrate wins, be supportive with losses.
```

**Conversation Starters:**
```
What's my current portfolio status?
Show me today's market performance
Get me a quote for AAPL
Buy 10 shares of MSFT
```

### 4. Add Actions

1. Click **"Create new action"**
2. In the **Schema** field, paste the following:

```yaml
openapi: 3.0.3
info:
  title: PaiiD Trading Platform API
  version: 1.0.0
servers:
  - url: https://paiid-backend.onrender.com
paths:
  /api/account:
    get:
      operationId: getAccount
      summary: Get account balance and buying power
      responses:
        '200':
          description: Account information
  /api/positions:
    get:
      operationId: getPositions
      summary: Get all portfolio positions
      responses:
        '200':
          description: List of positions
  /api/market/quote:
    get:
      operationId: getQuote
      summary: Get real-time quote for a symbol
      parameters:
        - name: symbol
          in: query
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Quote data
  /api/market/indices:
    get:
      operationId: getMarketIndices
      summary: Get major market indices (SPY, QQQ, DIA)
      responses:
        '200':
          description: Indices data
  /api/orders:
    post:
      operationId: executeOrder
      summary: Execute a trade order
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [symbol, qty, side, type]
              properties:
                symbol:
                  type: string
                qty:
                  type: integer
                side:
                  type: string
                  enum: [buy, sell]
                type:
                  type: string
                  enum: [market, limit]
      responses:
        '200':
          description: Order submitted
```

### 5. Configure Authentication

1. Under **Authentication**, select **"API Key"**
2. Set:
   - **Auth Type:** API Key
   - **API Key:** `Bearer YOUR_API_TOKEN_HERE` (replace with your actual token)
   - **Auth Location:** Header
   - **Header Name:** `Authorization`

**Example:**
```
Bearer rnd_bDRqi1TvLvd3rC78yvUSgDraH2Kl
```

### 6. Configure Privacy

- Set to **"Only me"** for private use
- Or **"Anyone with a link"** to share with team

### 7. Save and Test

1. Click **"Create"** in top-right
2. Test with these prompts:

```
Check my portfolio

What's AAPL trading at?

Show me market indices

Buy 5 shares of TSLA
```

## Example Conversation

**You:** Check my portfolio

**GPT:** Let me check your portfolio status...

*Your Portfolio Summary:*
```
Account Value: $125,430.50
Cash Balance: $50,000.00
Buying Power: $75,000.00

Open Positions (3):
• AAPL: 10 shares @ $152.30 | P&L: +$18.00 (+1.20%)
• MSFT: 5 shares @ $380.45 | P&L: -$12.50 (-0.66%)
• TSLA: 8 shares @ $235.60 | P&L: +$45.20 (+2.40%)

Total P&L: +$50.70 (+0.42%)
```

---

**You:** Buy 10 shares of NVDA

**GPT:** Let me get the current price...

*Trade Preview:*
```
Symbol: NVDA
Action: BUY
Quantity: 10 shares
Current Price: $485.20
Estimated Cost: $4,852.00
```

Should I proceed with this order?

**You:** Yes

**GPT:** ✓ Order submitted successfully! Order ID: abc123xyz

## Advanced Features

### Custom Prompts

Try these advanced queries:

- "Analyze my portfolio risk"
- "What are the best performing tech stocks today?"
- "Should I buy or sell AAPL based on current market?"
- "Show me news for my positions"

### Adding More Endpoints

To add more functionality, edit the Actions schema and include additional endpoints from the [full OpenAPI spec](./openapi.yaml):

- `/api/market/bars` - Historical data
- `/api/ai/recommendations` - AI trade ideas
- `/api/news` - Market news
- `/api/orders` (GET) - Order history

## Troubleshooting

### "Could not reach the action's server"

- ✅ Check backend is running: https://paiid-backend.onrender.com/api/health
- ✅ Verify API token is correct
- ✅ Ensure token includes "Bearer " prefix

### "Authentication failed"

- ✅ Token format: `Bearer <token>` (with space)
- ✅ Header name: `Authorization`
- ✅ Auth location: Header

### "Invalid symbol" or data errors

- ✅ Use correct ticker symbols (e.g., AAPL not Apple)
- ✅ Check market is open (errors may occur outside trading hours)
- ✅ Verify backend has valid Tradier/Alpaca credentials

## Security Tips

🔒 **Never share your API token publicly**  
🔒 **Use "Only me" privacy setting for personal trading**  
🔒 **This is paper trading - no real money at risk**  
🔒 **Revoke token if compromised (generate new one in backend)**

## Next Steps

✨ **Want more features?** See the [full integration guide](./CHATGPT_INTEGRATION.md)

📖 **API Reference:** [OpenAPI Spec](./openapi.yaml)

🤖 **Claude Desktop:** See [MCP Server Setup](./mcp-server/README.md)

💻 **OpenAI API:** See [OpenAI Integration](./CHATGPT_INTEGRATION.md#3-openai-api-integration)

## Need Help?

- Check [API Documentation](./API_DOCUMENTATION.md)
- Test endpoints with curl
- Open GitHub issue with details

---

**Happy Trading! 📈🤖**
