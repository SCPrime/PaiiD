# ChatGPT Fix Prompt - Options Endpoint Path Mismatch

**Copy this to Cursor (Ctrl+L):**

```
FIX OPTIONS ENDPOINT PATH MISMATCH

PROBLEM:
Frontend calls /api/proxy/expirations/{symbol}
Backend expects /api/options/expirations/{symbol}
Result: 403 Forbidden

FIX:
File: frontend/components/trading/OptionsChain.tsx
Line ~87-94: Change all instances of:
  - FROM: '/api/proxy/expirations/'
  - TO: '/api/proxy/options/expirations/'

Also line ~119-130: Change:
  - FROM: '/api/proxy/chain/'
  - TO: '/api/proxy/options/chain/'

VERIFICATION:
After fixing, the frontend should call:
  - /api/proxy/options/expirations/AAPL
  - /api/proxy/options/chain/AAPL

TEST:
Backend works: curl http://127.0.0.1:8001/api/options/expirations/AAPL
Browser should work at: http://localhost:3003

Please update these paths in OptionsChain.tsx.
```

---

## ✅ **After ChatGPT Fixes It:**

Come back to me (Claude) and say: **"ChatGPT fixed the paths"**

I'll verify the fix worked by checking:
1. Reading the updated file
2. Testing the endpoint
3. Confirming no errors in browser console
