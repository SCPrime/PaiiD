"""
PostgreSQL Migration Guide
Replace SQLite in-memory with persistent PostgreSQL
"""

# Update backend/.env to require DATABASE_URL
# Example: DATABASE_URL=postgresql://user:pass@localhost:5432/paiid

# Modify backend/app/db/session.py:
# Remove SQLite fallback - make DATABASE_URL mandatory
# Add startup validation that fails if DATABASE_URL missing
