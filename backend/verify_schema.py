"""
Verify database schema matches SQLAlchemy models after migration.
"""
from sqlalchemy import inspect
from app.db.session import engine

def verify_users_table():
    """Verify users table has correct schema."""
    inspector = inspect(engine)
    columns = inspector.get_columns('users')

    print("=" * 60)
    print("USERS TABLE SCHEMA VERIFICATION")
    print("=" * 60)

    # Create column lookup
    column_dict = {col['name']: col for col in columns}

    # Check for username column
    if 'username' in column_dict:
        username_col = column_dict['username']
        print(f"[OK] username column EXISTS")
        print(f"   Type: {username_col['type']}")
        print(f"   Nullable: {username_col['nullable']}")
    else:
        print("[ERROR] username column MISSING")

    # Check password_hash nullable
    if 'password_hash' in column_dict:
        password_col = column_dict['password_hash']
        print(f"[OK] password_hash column EXISTS")
        print(f"   Type: {password_col['type']}")
        print(f"   Nullable: {password_col['nullable']}")

        if password_col['nullable']:
            print("   [OK] password_hash is NULLABLE (correct for MVP user)")
        else:
            print("   [ERROR] password_hash is NOT NULL (migration may have failed)")
    else:
        print("[ERROR] password_hash column MISSING")

    print("\nAll columns in users table:")
    print("-" * 60)
    for col in columns:
        nullable_str = "NULL" if col['nullable'] else "NOT NULL"
        print(f"{col['name']:20} {str(col['type']):20} {nullable_str}")

    print("=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    verify_users_table()
