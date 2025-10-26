# Database Schema Migration - TODO

## 🎯 Issue

The `users` table in the PostgreSQL database has a schema mismatch with the current SQLAlchemy models, preventing full end-to-end testing of authenticated endpoints.

## ❌ Current Error

```
AttributeError: 'User' object has no attribute 'username'
```

**or**

```
sqlalchemy.exc.IntegrityError: null value in column "password_hash" violates not-null constraint
```

## 🔍 Root Cause

The database table was created with an older schema that may:
1. Have a `username` column that the model now expects to be nullable
2. Be missing the `username` column entirely (causing AttributeError when loading existing records)
3. Have `password_hash` as NOT NULL but the code tries to create users with empty string

## ✅ Solutions (Choose One)

### Option 1: Alembic Migration (Recommended)

**Best for production** - Creates a versioned migration history.

```bash
# Install Alembic if not already installed
pip install alembic

# Initialize Alembic (if not already done)
cd backend
alembic init alembic

# Configure alembic.ini
# Set: sqlalchemy.url = postgresql://...

# Configure env.py
# Import: from app.models.database import Base
# Set: target_metadata = Base.metadata

# Generate migration
alembic revision --autogenerate -m "add_username_field_to_users"

# Review the generated migration file
# Located in: alembic/versions/xxxx_add_username_field_to_users.py

# Apply migration
alembic upgrade head
```

**Expected Migration**:
```python
def upgrade():
    # Add username column if it doesn't exist
    op.add_column('users', sa.Column('username', sa.String(255), nullable=True))

    # Alter password_hash to be nullable (if needed)
    op.alter_column('users', 'password_hash', nullable=True)
```

### Option 2: Manual SQL (Quick Fix)

**Best for development** - Fast but no migration history.

```sql
-- Connect to your PostgreSQL database
psql -U your_username -d paiid_db

-- Check current schema
\d users

-- Add username column if missing
ALTER TABLE users ADD COLUMN IF NOT EXISTS username VARCHAR(255);

-- Make password_hash nullable if needed
ALTER TABLE users ALTER COLUMN password_hash DROP NOT NULL;
```

### Option 3: Drop and Recreate (Nuclear Option)

**⚠️ WARNING: This deletes all data!**

Only use in development if you don't care about existing data.

```python
# In Python console or script
from app.db.session import engine
from app.models.database import Base

# Drop all tables (CASCADE to handle foreign keys)
Base.metadata.drop_all(engine)

# Recreate all tables with current schema
Base.metadata.create_all(engine)
```

## 📋 Current User Model Schema

According to `backend/app/models/database.py` (lines 16-57):

```python
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)  # ← Currently NOT NULL
    full_name = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True)  # ← Added for compatibility

    # Role-based access control
    role = Column(String(50), default="personal_only", nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # ... (other fields)
```

## 🎯 Recommended Approach

1. **Use Alembic** for proper migration management
2. **Make `password_hash` nullable** to allow MVP user creation with empty password
3. **Keep `username` as nullable** for backward compatibility

## ✅ Verification Steps

After applying the migration:

```bash
# Start backend
cd backend
python -m uvicorn app.main:app --reload --port 8001

# Test API token auth
curl -H "Authorization: Bearer tuGlKvrYEoiJcv7r7oIy7zXM9pqVnaxN_74obFz6lVo" \
  http://127.0.0.1:8001/api/health/detailed

# Expected response
{"status":"healthy", "timestamp":"...", ...}
```

## 📊 Current State vs. Desired State

| Field | Database | Model | Action Needed |
|-------|----------|-------|---------------|
| `id` | ✅ Exists | ✅ Defined | No change |
| `email` | ✅ Exists | ✅ Defined | No change |
| `password_hash` | ❌ NOT NULL | ✅ NOT NULL | Make nullable |
| `full_name` | ❓ Unknown | ✅ Nullable | Add if missing |
| `username` | ❓ May exist | ✅ Nullable | Add if missing |
| `role` | ✅ Exists | ✅ Defined | No change |
| `is_active` | ✅ Exists | ✅ Defined | No change |

## 🚀 Next Steps

1. Choose migration approach (Alembic recommended)
2. Backup database if production
3. Apply migration
4. Test authenticated endpoints
5. Update this document with results

---

**Created**: 2025-10-26
**Priority**: Medium (blocks full endpoint testing)
**Related**: JWT_FIX_SUMMARY.md (authentication logic is working, this is just schema)
