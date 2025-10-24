# AI-Assisted Debugging Setup for PaiiD

**Status:** Enhanced with MCP-based browser debugging (October 2025)
**Compatible with:** VS Code, Cursor IDE

---

## Overview

This document provides setup instructions for AI-assisted debugging tools that enable Claude (via Cursor) to autonomously inspect browser state, console logs, network traffic, and runtime errors without manual intervention.

## Phase 1: Essential Setup (Implemented)

### 1. VS Code Settings Enhanced

**File:** `.vscode/settings.json`

Added settings for:
- ✅ TypeScript project diagnostics
- ✅ CodeLens and inline suggestions
- ✅ Console Ninja configuration
- ✅ Error Lens inline error display
- ✅ Playwright E2E testing

### 2. Current Extensions Installed

Check which extensions are already active:

```bash
# List installed extensions
code --list-extensions
```

**Already configured:**
- Prettier (esbenp.prettier-vscode)
- ESLint (dbaeumer.vscode-eslint)
- Python (ms-python.python)
- Ruff (charliermarsh.ruff)

---

## Phase 2: MCP Server Setup (Recommended)

### Chrome DevTools MCP (Essential for AI Browser Control)

**Installation:**
```bash
npm install -g chrome-devtools-mcp
```

**Configuration for Cursor:**

Create/edit Cursor MCP settings file:

**Windows:** `%APPDATA%\Cursor\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest"],
      "env": {
        "BROWSER_PATH": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
      }
    }
  }
}
```

**Capabilities:**
- AI can launch Chrome with localhost URLs
- Inspect console.log output and errors
- Analyze network requests/responses
- Run Lighthouse performance audits
- Take screenshots of issues
- Execute clicks, typing, navigation

### Console Ninja MCP (Essential for Runtime Logs)

**Installation:**

1. Install Console Ninja extension:
```bash
code --install-extension WallabyJs.console-ninja
```

2. MCP server auto-installs to `~/.console-ninja/mcp/`

**Configuration for Cursor:**

Add to MCP settings:
```json
{
  "mcpServers": {
    "console-ninja": {
      "command": "node",
      "args": ["C:\\Users\\SSaint-Cyr\\.console-ninja\\mcp\\index.js"]
    }
  }
}
```

**Capabilities:**
- Real-time console.log inline in editor
- Runtime errors with stack traces
- Network request logging (PRO version)
- React Hooks dependency tracking (PRO version)
- Server-side + client-side logging for Next.js

---

## Phase 3: Additional Extensions (Optional)

### Error Lens (Highly Recommended)

```bash
code --install-extension usernamehw.errorlens
```

Displays diagnostic messages inline at problem lines. Works with TypeScript, ESLint, Webpack errors.

### Playwright (E2E Testing)

```bash
cd frontend
npm install -D @playwright/test
npx playwright install
code --install-extension ms-playwright.playwright
```

**Create test example:**

`frontend/tests/options-chain.spec.ts`:
```typescript
import { test, expect } from '@playwright/test';

test('OPTT options chain loads with Greeks', async ({ page }) => {
  await page.goto('http://localhost:3000/test-options');

  await page.fill('input[type="text"]', 'OPTT');
  await page.click('button:has-text("Load Options Chain")');

  // Wait for options table
  await expect(page.locator('table')).toBeVisible({ timeout: 10000 });

  // Verify Greeks columns present
  await expect(page.locator('th:has-text("Delta")')).toBeVisible();
  await expect(page.locator('th:has-text("Gamma")')).toBeVisible();
  await expect(page.locator('th:has-text("Theta")')).toBeVisible();
  await expect(page.locator('th:has-text("Vega")')).toBeVisible();

  // Verify data loaded
  const contractCount = await page.locator('tbody tr').count();
  expect(contractCount).toBeGreaterThan(0);
});
```

Run tests:
```bash
npx playwright test
npx playwright test --ui  # Visual test runner
```

### Thunder Client (API Testing)

```bash
code --install-extension rangav.vscode-thunder-client
```

**Benefits:**
- Test backend endpoints directly in VS Code
- Save requests in collections (Git-friendly JSON)
- Environment variables for dev/prod
- AI can read/modify/execute API requests

**Example request:**

Create `.vscode/thunder-tests/thunderclient.json`:
```json
{
  "requests": [
    {
      "name": "OPTT Expirations",
      "method": "GET",
      "url": "http://localhost:8001/api/options/expirations/OPTT",
      "headers": [
        {
          "name": "Authorization",
          "value": "Bearer tuGlKvrYEoiJcv7r7oIy7zXM9pqVnaxN_74obFz6lVo"
        }
      ]
    },
    {
      "name": "OPTT Options Chain",
      "method": "GET",
      "url": "http://localhost:8001/api/options/chain/OPTT?expiration=2025-11-21",
      "headers": [
        {
          "name": "Authorization",
          "value": "Bearer tuGlKvrYEoiJcv7r7oIy7zXM9pqVnaxN_74obFz6lVo"
        }
      ]
    }
  ]
}
```

### Edge DevTools (Network Panel)

```bash
code --install-extension ms-edgedevtools.vscode-edge-devtools
```

Embeds full Edge DevTools in VS Code for DOM inspection, Network monitoring, and CSS debugging.

---

## Debug Configurations

### Next.js Full-Stack Debugging

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Next.js: debug full stack",
      "type": "node-terminal",
      "request": "launch",
      "command": "npm run dev",
      "cwd": "${workspaceFolder}/frontend",
      "serverReadyAction": {
        "pattern": "- Local:.+(https?://.+)",
        "uriFormat": "%s",
        "action": "debugWithChrome"
      }
    },
    {
      "name": "Backend: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app.main:app",
        "--reload",
        "--port",
        "8001"
      ],
      "cwd": "${workspaceFolder}/backend",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/backend"
      }
    },
    {
      "name": "Chrome: localhost:3000",
      "type": "chrome",
      "request": "launch",
      "url": "http://localhost:3000",
      "webRoot": "${workspaceFolder}/frontend",
      "sourceMaps": true
    }
  ],
  "compounds": [
    {
      "name": "Full Stack (Frontend + Backend)",
      "configurations": ["Next.js: debug full stack", "Backend: FastAPI"]
    }
  ]
}
```

---

## Testing Workflows

### 1. Manual Browser Testing

```bash
# Start servers
cd backend && python -m uvicorn app.main:app --reload --port 8001
cd frontend && npm run dev

# Navigate to test page
# http://localhost:3000/test-options
# Enter OPTT, click "Load Options Chain"
# Verify Greeks display
```

### 2. AI-Assisted Testing (with MCP)

**In Cursor chat:**
```
"Launch Chrome and navigate to http://localhost:3000/test-options"
"Test the OPTT options chain and check for console errors"
"Run a Lighthouse audit on the test page"
```

Claude will autonomously:
1. Launch Chrome
2. Navigate to URL
3. Inspect console for errors
4. Check network requests
5. Report any issues found

### 3. Playwright Automated Testing

```bash
# Run all tests
npx playwright test

# Run specific test
npx playwright test options-chain

# Debug mode (pauses execution)
npx playwright test --debug

# UI mode (visual test runner)
npx playwright test --ui

# Generate test from recording
npx playwright codegen http://localhost:3000/test-options
```

### 4. API Testing with Thunder Client

1. Open Thunder Client panel (sidebar)
2. Select "OPTT Expirations" request
3. Click "Send"
4. Verify response contains 4 expiration dates
5. Select "OPTT Options Chain" request
6. Click "Send"
7. Verify 14 contracts with Greeks

---

## AI Debugging Capabilities (with MCP)

### What Claude Can Do Autonomously

**With Chrome DevTools MCP:**
- ✅ Launch browser with specific URL
- ✅ Read console.log output
- ✅ Inspect network requests (headers, body, timing)
- ✅ Capture screenshots
- ✅ Run Lighthouse performance audits
- ✅ Execute user interactions (click, type, scroll)
- ✅ Verify fixes in real-time

**With Console Ninja MCP:**
- ✅ Access historical runtime logs
- ✅ Query specific log entries by file/line
- ✅ Access full stack traces
- ✅ See runtime values inline

**Example AI Workflow:**
```
User: "Test the OPTT options chain for errors"

AI Actions:
1. Launches Chrome → http://localhost:3000/test-options
2. Types "OPTT" in symbol input
3. Clicks "Load Options Chain"
4. Inspects console for errors
5. Checks network request to /api/proxy/options/chain/OPTT
6. Verifies 14 contracts returned
7. Confirms Greeks present in response
8. Reports: "✅ OPTT loaded successfully, no errors found"
```

---

## Troubleshooting

### MCP Servers Not Working

**Check Cursor MCP settings:**
```bash
# Windows
%APPDATA%\Cursor\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json
```

**Verify paths:**
- Chrome path: `C:\Program Files\Google\Chrome\Application\chrome.exe`
- Console Ninja MCP: `C:\Users\SSaint-Cyr\.console-ninja\mcp\index.js`

**Restart Cursor** after configuration changes.

### Console Ninja Not Showing Logs

1. Check extension installed: `code --list-extensions | grep console-ninja`
2. Verify `console-ninja.featureSet` in `.vscode/settings.json`
3. Restart dev server (`npm run dev`)
4. Check Console Ninja output panel for errors

### Playwright Tests Failing

```bash
# Install browsers
npx playwright install

# Check Playwright config
npx playwright test --list

# Debug specific test
npx playwright test options-chain --debug
```

### Backend Not Accessible

```bash
# Verify backend running
curl http://localhost:8001/api/health

# Check port in use
netstat -ano | findstr ":8001"

# Restart backend
cd backend && python -m uvicorn app.main:app --reload --port 8001
```

---

## Extension Installation Checklist

### Required for Phase 1
- [x] Prettier (already installed)
- [x] ESLint (already installed)
- [ ] Console Ninja (`code --install-extension WallabyJs.console-ninja`)
- [ ] Error Lens (`code --install-extension usernamehw.errorlens`)

### Recommended for AI Debugging
- [ ] Chrome DevTools MCP (configure in Cursor MCP settings)
- [ ] Console Ninja MCP (auto-installs with extension)
- [ ] Playwright (`code --install-extension ms-playwright.playwright`)
- [ ] Thunder Client (`code --install-extension rangav.vscode-thunder-client`)

### Optional Enhancements
- [ ] Edge DevTools (`code --install-extension ms-edgedevtools.vscode-edge-devtools`)
- [ ] Wallaby.js (commercial, real-time testing)

---

## Next Steps for PaiiD Project

### Immediate (Post-Phase 1)
1. Install Error Lens for inline error visibility
2. Install Console Ninja for runtime debugging
3. Configure Chrome DevTools MCP for AI browser control
4. Create Playwright tests for OptionsChain component

### Phase 2 Enhancements
1. Add E2E tests for full trading workflow
2. Set up CI/CD with Playwright tests
3. Configure network monitoring for API debugging
4. Implement automated Lighthouse audits

### Long-term
1. Upgrade to Console Ninja PRO for network logging
2. Consider Wallaby.js for real-time test feedback
3. Integrate performance monitoring
4. Set up error tracking (Sentry)

---

**Last Updated:** October 22, 2025
**Phase:** 1 Complete, Debugging Tools Ready
**Status:** MCP Configuration Pending User Installation
