# PaiiD MCP Server

Model Context Protocol (MCP) server for the PaiiD Trading Platform. This server allows AI assistants like Claude Desktop to interact with the PaiiD API.

## What is MCP?

The Model Context Protocol (MCP) is an open standard that enables AI assistants to securely access external tools and data sources. This server implements MCP to expose PaiiD's trading functionality to compatible AI clients.

## Features

- 🔐 Secure authentication with API tokens
- 📊 Portfolio and account management
- 💹 Real-time market data
- 🤖 AI-powered trade recommendations
- 📰 Market news and sentiment
- 🔄 Order execution and tracking

## Installation

```bash
cd mcp-server
npm install
npm run build
```

## Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and set your configuration:
   ```env
   PAIID_API_URL=https://paiid-backend.onrender.com
   PAIID_API_TOKEN=your_api_token_here
   ```

## Usage

### With Claude Desktop

Add to your Claude Desktop configuration file:

**macOS/Linux**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

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

Restart Claude Desktop, and the PaiiD tools will be available.

### With Other MCP Clients

Run the server directly:

```bash
npm start
```

Or in development mode with auto-rebuild:

```bash
npm run dev
```

The server communicates over stdio and follows the MCP specification.

## Available Tools

### Portfolio Management

- **get_account**: Get account balance and buying power
- **get_positions**: View all open positions with P&L
- **get_order_history**: List submitted orders

### Trading

- **execute_trade**: Submit buy/sell orders (paper trading)
  - Parameters: symbol, qty, side, type, limitPrice, stopPrice

### Market Data

- **get_quote**: Real-time quote for a symbol
- **get_market_indices**: Major indices (SPY, QQQ, DIA)
- **get_historical_bars**: Historical OHLCV data
- **get_news**: Latest market news

### AI Analysis

- **get_ai_recommendations**: AI-generated trade ideas
  - Parameters: symbols, strategy

## Example Usage in Claude Desktop

```
User: "Show me my portfolio positions"
Claude: [Uses get_positions tool] Here are your current positions...

User: "What's the current price of AAPL?"
Claude: [Uses get_quote tool] AAPL is currently trading at...

User: "Buy 10 shares of MSFT at market price"
Claude: [Uses execute_trade tool] I've submitted an order to buy 10 shares of MSFT...
```

## Development

### Project Structure

```
mcp-server/
├── src/
│   └── index.ts          # Main MCP server implementation
├── dist/                 # Compiled JavaScript (generated)
├── package.json          # Dependencies
├── tsconfig.json         # TypeScript configuration
├── .env.example          # Environment template
└── README.md            # This file
```

### Building

```bash
npm run build
```

### Cleaning

```bash
npm run clean
```

## Error Handling

The server handles errors gracefully:

- API connection failures
- Authentication errors
- Invalid parameters
- Timeout errors

All errors are returned in MCP-compliant format with descriptive messages.

## Security

- API token is stored in environment variables (never in code)
- All API requests use HTTPS
- Paper trading only by default (no real money)
- Token is sent via Authorization header (not URL)

## Troubleshooting

### Server won't start

- Check that `PAIID_API_TOKEN` is set correctly
- Verify Node.js version is 18 or higher
- Run `npm install` to ensure dependencies are installed

### Claude Desktop can't find server

- Verify the path in `claude_desktop_config.json` is absolute
- Check that `dist/index.js` exists (run `npm run build`)
- Restart Claude Desktop after config changes

### API requests failing

- Verify backend is running: https://paiid-backend.onrender.com/api/health
- Check API token is valid
- Ensure PAIID_API_URL is correct in configuration

### Tools not appearing in Claude

- Restart Claude Desktop completely
- Check Claude Desktop's MCP status (look for connection indicator)
- View logs: Claude Desktop has a developer console for debugging

## Contributing

See the main [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines.

## License

MIT License - See [LICENSE](../LICENSE) for details.

## Related Documentation

- [Main Integration Guide](../CHATGPT_INTEGRATION.md)
- [API Documentation](../API_DOCUMENTATION.md)
- [OpenAPI Spec](../openapi.yaml)
