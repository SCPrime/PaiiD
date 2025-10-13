# PostgreSQL Database Setup - NEXT STEPS

## ✅ Completed Setup

The following has been configured and committed:

1. **SQLAlchemy Dependencies** - Added to `requirements.txt`
2. **Database Session Management** - Created `app/db/session.py`
3. **Database Models** - Created 5 models in `app/models/database.py`:
   - `User` - User accounts and preferences
   - `Strategy` - Trading strategy configurations
   - `Trade` - Trade execution records
   - `Performance` - Daily performance snapshots
   - `EquitySnapshot` - Intraday equity tracking
4. **Alembic Migrations** - Initialized migration system
5. **Initial Migration** - Created migration `0952a611cdfb` with full schema
6. **Migration Script** - Created `scripts/migrate_strategies.py` for data migration

## 🔴 REQUIRED: Manual Configuration Steps

### Step 1: Get PostgreSQL Connection String from Render

1. Go to your Render Dashboard: https://dashboard.render.com
2. Find your PostgreSQL instance
3. Copy the **Internal Database URL** (starts with `postgresql://`)
   - Format: `postgresql://user:password@host:port/database`

### Step 2: Add DATABASE_URL to .env File

Edit `backend/.env` and add:

```bash
DATABASE_URL=postgresql://user:password@host:port/database
```

**IMPORTANT**: Replace with your actual connection string from Render.

### Step 3: Apply Database Migration

Run the following commands to create all tables in PostgreSQL:

```bash
cd backend
python -m alembic upgrade head
```

Expected output:
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 0952a611cdfb, Initial schema: users, strategies, trades, performance, equity_snapshots
```

### Step 4: Migrate Existing Strategies (Optional)

If you have existing strategies in `strategies/` directory or localStorage backups:

```bash
cd backend
python scripts/migrate_strategies.py
```

This will:
- Scan `strategies/*.json` files
- Import them into the PostgreSQL database
- Skip duplicates automatically
- Report success/failure for each strategy

## 📋 Verification

After completing the manual steps, verify the setup:

```bash
# Check database connection
cd backend
python -c "from app.db.session import SessionLocal; db = SessionLocal(); print('✅ Database connection successful'); db.close()"

# Check tables exist
python -c "from app.db.session import engine; from sqlalchemy import inspect; inspector = inspect(engine); tables = inspector.get_table_names(); print(f'✅ Found {len(tables)} tables:', tables)"

# List current migration
python -m alembic current
```

Expected output:
```
✅ Database connection successful
✅ Found 5 tables: ['users', 'strategies', 'trades', 'performance', 'equity_snapshots']
0952a611cdfb (head)
```

## 🔧 Troubleshooting

### "Can't connect to database"
- Verify DATABASE_URL is set correctly in `.env`
- Check that PostgreSQL instance is running on Render
- Ensure IP address is whitelisted (if required)

### "No module named 'psycopg2'"
```bash
pip install -r requirements.txt
```

### "relation already exists"
If tables were already created, you can mark migration as complete without running it:
```bash
python -m alembic stamp head
```

### "Migration version mismatch"
Check current version:
```bash
python -m alembic current
python -m alembic history
```

## 📁 Database Schema Overview

### Users Table
- Stores user accounts and preferences (JSON)
- Alpaca account ID for linking to trading API
- One-to-many with strategies and trades

### Strategies Table
- Strategy configuration stored as JSON
- Performance metrics (win rate, Sharpe ratio, max drawdown)
- Active/autopilot flags
- Linked to user (optional, nullable for system strategies)

### Trades Table
- Complete trade execution records
- Broker order IDs for reconciliation
- P&L tracking
- Status: pending, filled, partially_filled, cancelled, failed
- Linked to user and strategy

### Performance Table
- Daily portfolio snapshots
- P&L metrics (daily and total)
- Risk metrics (Sharpe, max drawdown, volatility)
- Trade statistics (win rate, total trades)

### Equity Snapshots Table
- Intraday equity tracking for charts
- Timestamps for time-series data
- Extra metadata as JSON

## 🔐 Security Notes

- **Never commit** the `.env` file with DATABASE_URL
- Database credentials are in environment variables only
- PostgreSQL uses SSL by default on Render
- Foreign key cascades protect referential integrity

## 🚀 Next Phase

Once database setup is complete, Phase 2.5 continues with:
- **Task 2**: Redis Production Setup (caching)
- **Task 3**: Sentry Error Tracking
- **Task 4**: Critical Backend Tests

---

**Need Help?** Check the Alembic docs: https://alembic.sqlalchemy.org/
