"""
"""Migrate strategy files from disk/localStorage into the PostgreSQL database."""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# Fix Windows console encoding for emoji support
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = REPO_ROOT / ".env"

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)

# Add backend package to PYTHONPATH so the config helpers are discoverable
sys.path.append(str(REPO_ROOT))

from app.core.bootstrap import emit_startup_summary  # noqa: E402
from app.core.config import Settings  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402
from app.models.database import Strategy  # noqa: E402


SETTINGS = Settings()
VALIDATION_REPORT = emit_startup_summary(
    settings=SETTINGS,
    application="strategy-migrator",
    env_path=ENV_PATH,
)

if VALIDATION_REPORT.has_errors:
    print(
        "❌ Prelaunch validations failed. Fix the configuration before running migrations.",
        flush=True,
    )
    sys.exit(1)


def migrate_strategies_from_directory():
    """Migrate strategies from strategies/ directory"""
    db = SessionLocal()
    migrated_count = 0
    failed_count = 0

    try:
        # Check if strategies directory exists
        strategies_dir = REPO_ROOT / "strategies"
        if not strategies_dir.exists():
            print(f"⚠️  Strategies directory not found: {strategies_dir}")
            return migrated_count, failed_count

        print(f"\n📁 Scanning {strategies_dir} for strategy files...")

        # Read strategy files
        strategy_files = list(strategies_dir.glob("*.json"))

        if not strategy_files:
            print(f"ℹ️  No strategy files found in {strategies_dir}")
            return migrated_count, failed_count

        print(f"📄 Found {len(strategy_files)} strategy file(s)\n")

        for strategy_file in strategy_files:
            try:
                with open(strategy_file) as f:
                    strategy_data = json.load(f)

                # Extract strategy metadata
                name = strategy_data.get("name", strategy_file.stem)
                description = strategy_data.get("description")
                strategy_type = strategy_data.get("type", "custom")

                # Check if strategy already exists
                existing = db.query(Strategy).filter(Strategy.name == name).first()
                if existing:
                    print(f"⏭️  Skipping '{name}' (already exists)")
                    continue

                # Create strategy record
                strategy = Strategy(
                    name=name,
                    description=description,
                    strategy_type=strategy_type,
                    config=strategy_data,
                    is_active=False,
                    is_autopilot=False,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )

                db.add(strategy)
                migrated_count += 1
                print(f"✅ Migrated: '{name}' ({strategy_type})")

            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse {strategy_file}: Invalid JSON - {e}")
                failed_count += 1
            except Exception as e:
                print(f"❌ Failed to migrate {strategy_file}: {e}")
                failed_count += 1

        # Commit all migrations
        if migrated_count > 0:
            db.commit()
            print(
                f"\n✅ Successfully committed {migrated_count} strateg{'y' if migrated_count == 1 else 'ies'} to database"
            )

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

    return migrated_count, failed_count


def print_current_strategies():
    """Print all strategies currently in database"""
    db = SessionLocal()
    try:
        strategies = db.query(Strategy).all()
        if not strategies:
            print("\nℹ️  No strategies found in database")
            return

        print(f"\n📊 Current Database Strategies ({len(strategies)} total):")
        print("=" * 80)
        for s in strategies:
            active_status = "🟢 Active" if s.is_active else "⚪ Inactive"
            autopilot_status = "🤖 Autopilot" if s.is_autopilot else ""
            print(
                f"{s.id:3d} | {active_status} {autopilot_status:12s} | {s.strategy_type:18s} | {s.name}"
            )
        print("=" * 80)
    finally:
        db.close()


def main():
    """Main migration function"""
    print("\n" + "=" * 80)
    print("🗂️  Strategy Migration Tool - LocalStorage → PostgreSQL")
    print("=" * 80)

    try:
        # Show current database strategies
        print_current_strategies()

        # Migrate from directory
        migrated, failed = migrate_strategies_from_directory()

        # Show updated database
        if migrated > 0:
            print_current_strategies()

        # Summary
        print("\n" + "=" * 80)
        print("📈 Migration Summary:")
        print(f"   ✅ Migrated: {migrated}")
        print(f"   ❌ Failed:   {failed}")
        print("   ⏭️  Skipped:  (duplicates not counted)")
        print("=" * 80 + "\n")

        if failed > 0:
            print("⚠️  Some strategies failed to migrate. Check errors above.")
            sys.exit(1)
        elif migrated == 0:
            print("ℹ️  No new strategies to migrate.")
        else:
            print("✅ Migration completed successfully!")

    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
