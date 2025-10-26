#!/usr/bin/env python3
"""
Test Database Setup Script
Creates and populates test database for integration tests
"""

import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.core.jwt import hash_password
from app.models.database import Base, User


def setup_test_database():
    """Set up test database with sample data"""

    # Test database URL
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test_integration.db"

    # Create engine and session
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create tables
    print("Creating test database tables...")
    Base.metadata.create_all(bind=engine)

    # Create session
    db = SessionLocal()

    try:
        # Create test users
        test_users = [
            {
                "email": "trader@test.com",
                "password": "TestP@ss123",
                "name": "Test Trader",
                "risk_tolerance": "moderate",
                "is_active": True,
            },
            {
                "email": "admin@test.com",
                "password": "AdminP@ss123",
                "name": "Test Admin",
                "risk_tolerance": "conservative",
                "is_active": True,
            },
            {
                "email": "aggressive@test.com",
                "password": "AggressiveP@ss123",
                "name": "Aggressive Trader",
                "risk_tolerance": "aggressive",
                "is_active": True,
            },
        ]

        print("Creating test users...")
        for user_data in test_users:
            # Check if user already exists
            existing_user = (
                db.query(User).filter(User.email == user_data["email"]).first()
            )
            if existing_user:
                print(f"User {user_data['email']} already exists, skipping...")
                continue

            user = User(
                email=user_data["email"],
                password_hash=hash_password(user_data["password"]),
                name=user_data["name"],
                risk_tolerance=user_data["risk_tolerance"],
                is_active=user_data["is_active"],
            )
            db.add(user)
            print(f"Created user: {user_data['email']}")

        # Commit changes
        db.commit()
        print("Test database setup completed successfully!")

        # Print test credentials
        print("\n" + "=" * 50)
        print("TEST CREDENTIALS:")
        print("=" * 50)
        for user_data in test_users:
            print(f"Email: {user_data['email']}")
            print(f"Password: {user_data['password']}")
            print(f"Risk Tolerance: {user_data['risk_tolerance']}")
            print("-" * 30)

    except Exception as e:
        print(f"Error setting up test database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def cleanup_test_database():
    """Clean up test database"""
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test_integration.db"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )

    print("Cleaning up test database...")
    Base.metadata.drop_all(bind=engine)
    print("Test database cleaned up!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test Database Setup")
    parser.add_argument("--cleanup", action="store_true", help="Clean up test database")

    args = parser.parse_args()

    if args.cleanup:
        cleanup_test_database()
    else:
        setup_test_database()
