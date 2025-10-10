# PaiiD Deployment Checklist

## Frontend (Vercel)
Environment Variables Required:
- NEXT_PUBLIC_BACKEND_URL=https://paiid-backend.onrender.com
- (No other public env vars needed)

## Backend (Render)
Environment Variables Required:
- API_TOKEN=[from backend/.env]
- TRADIER_API_KEY=[from backend/.env]
- TRADIER_ACCOUNT_ID=[from backend/.env]
- ANTHROPIC_API_KEY=[from backend/.env]
- ALLOW_ORIGIN=https://paiid-snowy.vercel.app

## Verification Steps
- [x] Frontend builds without errors
- [x] Backend imports successful
- [x] All API keys documented
- [x] CORS configured correctly
