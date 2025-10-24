# PaiiD Frontend

Next.js frontend application for the PaiiD platform.

## Features

- Real-time connection to backend API
- Interactive trading controls
- Portfolio position display
- Dry run execution for safe testing

## Deployment

This frontend is designed to be deployed on Vercel.

### Vercel Deployment

1. Connect your repository to Vercel
2. Set Root Directory to `frontend/`
3. Configure environment variables:
   - `NEXT_PUBLIC_API_BASE_URL`: Your backend API URL (e.g., Render service URL)
   - `NEXT_PUBLIC_API_TOKEN`: Authentication token (must match backend)

### Environment Variables

- `NEXT_PUBLIC_API_BASE_URL`: Backend API base URL (required)
- `NEXT_PUBLIC_API_TOKEN`: Authentication token (required)

## Development

```bash
cd frontend
npm install
npm run dev
```

### Testing

- **Unit tests**: `npm test`
- **E2E smoke tests**:
  1. Install Playwright browsers (one-time): `npx playwright install`
  2. Run the suite: `npm run test:e2e`

The E2E suite includes mocked options chain API flows and radial workflow coverage for the
interactive dashboard pages (`/test-options` and `/test-radial`).

## Pages

- `/` - Main dashboard
- `/new` - New trading session (replicated functionality for demo)

## Features

- **Health Check**: Verify backend connectivity
- **Positions**: View current portfolio positions
- **Execute (Dry)**: Test trade execution without live trading
