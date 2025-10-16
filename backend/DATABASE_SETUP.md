# Database Setup Guide - See backend/JWT_PRODUCTION_SETUP.md for JWT configuration

## Quick Setup for Render

**Add DATABASE_URL environment variable in Render dashboard:**

```
postgresql://paiid_user:uxjNib9k8jrF1g1OyBlk2pIptxHM9vUG@dpg-d3m9etumcj7s73age4gg-a.oregon-postgres.render.com/paiid_db
```

**Migrations will run automatically on startup** via `start.sh`

## Database Tables Created

- users (authentication + preferences)
- user_sessions (JWT tokens)
- activity_log (audit trail)
- strategies (trading strategies)
- trades (trade history)
- performance (daily snapshots)
- order_templates (saved orders)
- ai_recommendations (AI suggestions)

For full documentation, see comments in `backend/app/models/database.py`
