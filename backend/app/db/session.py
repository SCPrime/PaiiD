"""
Database Session Management

Provides SQLAlchemy engine, session, and base for models.
Falls back to SQLite in-memory if DATABASE_URL not configured.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

from ..core.config import settings

# Create engine based on configuration
if settings.DATABASE_URL:
    # Production: Use PostgreSQL
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using
        echo=False,  # Set to True for SQL debugging
    )
    print(f"[OK] Database engine created: PostgreSQL", flush=True)
else:
    # Development fallback: SQLite in memory
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    print(f"[WARNING] DATABASE_URL not set - using SQLite in-memory fallback", flush=True)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency for FastAPI routes

    Usage:
        @router.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            # Use db here
            pass
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables
    Call this on startup to create all tables
    """
    from ..models import database  # Import models to register them

    Base.metadata.create_all(bind=engine)
    print(f"[OK] Database tables initialized", flush=True)
