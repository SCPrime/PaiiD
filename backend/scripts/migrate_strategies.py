"""Comprehensive localStorage migration helper.

This script ingests historic frontend state (exported from browser localStorage)
alongside JSON strategy files and persists them into the relational database.

Usage::

    python scripts/migrate_strategies.py --local-storage path/to/export.json

Prerequisites:
    - DATABASE_URL environment variable must be set
    - Run ``alembic upgrade head`` before executing this script
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


# Fix Windows console encoding for emoji support
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    sys.stdout.reconfigure(encoding="utf-8")

# Add parent directory to path so ``app`` can be imported when executed directly
sys.path.append(str(Path(__file__).parent.parent))

from app.db.session import SessionLocal
from app.models.database import (
    OrderHistory,
    Strategy,
    User,
    UserProfileData,
    UserSettings,
)


LOCAL_STORAGE_KEYS = {
    "user": "allessandra_user",
    "settings": "allessandra_settings",
    "strategies": "ai_trader_strategies",
    "orders": "orderHistory",
    "profile": "paid_user_profile",
}


def _load_json_value(value: Any) -> Any:
    """Attempt to JSON-decode a localStorage value if it is a string."""

    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def parse_local_storage_dump(path: Path) -> dict[str, Any]:
    """Load and normalise a raw localStorage export."""

    with open(path, "r", encoding="utf-8") as handle:
        raw = json.load(handle)

    return {key: _load_json_value(raw.get(key)) for key in raw}


def get_or_create_user(db, exported_user: dict[str, Any] | None) -> User:
    """Resolve the database user that should own migrated records."""

    external_id = None
    if exported_user:
        external_id = exported_user.get("userId")

    query = None
    if external_id:
        query = db.query(User).filter(User.external_id == external_id).first()
    else:
        query = db.query(User).filter(User.id == 1).first()

    if query:
        user = query
    else:
        # Bootstrap a user record when none exists yet
        user = User(
            email=(exported_user or {}).get("email")
            or f"{external_id or 'local-user'}@migrated.local",
            password_hash="migrated",  # placeholder hash (no login via this account)
            full_name=(exported_user or {}).get("displayName"),
            role="personal_only",
            external_id=external_id,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Update metadata when provided
    if exported_user:
        user.full_name = exported_user.get("displayName") or user.full_name
        user.email = exported_user.get("email") or user.email
        user.external_id = exported_user.get("userId") or user.external_id
        preferences = exported_user.get("preferences")
        if preferences:
            # Merge preferences with existing ones instead of overwriting entirely
            merged = dict(user.preferences or {})
            merged.update(preferences)
            user.preferences = merged

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def migrate_user_settings(db, user: User, settings_data: dict[str, Any] | None) -> int:
    if not settings_data:
        return 0

    record = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
    if not record:
        record = UserSettings(user_id=user.id, settings=settings_data)
        db.add(record)
    else:
        merged = dict(record.settings or {})
        merged.update(settings_data)
        record.settings = merged

    db.commit()
    return 1


def migrate_user_profile(
    db,
    user: User,
    profile_type: str,
    profile_data: dict[str, Any] | None,
) -> int:
    if not profile_data:
        return 0

    record = (
        db.query(UserProfileData)
        .filter(
            UserProfileData.user_id == user.id,
            UserProfileData.profile_type == profile_type,
        )
        .first()
    )

    if not record:
        record = UserProfileData(
            user_id=user.id,
            profile_type=profile_type,
            data=profile_data,
        )
        db.add(record)
    else:
        merged = dict(record.data or {})
        merged.update(profile_data)
        record.data = merged

    db.commit()
    return 1


def migrate_strategies_from_directory() -> tuple[int, int]:
    """Migrate JSON files stored in ``strategies/``."""

    db = SessionLocal()
    migrated_count = 0
    failed_count = 0

    try:
        strategies_dir = Path("strategies")
        if not strategies_dir.exists():
            print(f"⚠️  Strategies directory not found: {strategies_dir}")
            return migrated_count, failed_count

        print(f"\n📁 Scanning {strategies_dir} for strategy files...")
        strategy_files = list(strategies_dir.glob("*.json"))

        if not strategy_files:
            print(f"ℹ️  No strategy files found in {strategies_dir}")
            return migrated_count, failed_count

        print(f"📄 Found {len(strategy_files)} strategy file(s)\n")

        for strategy_file in strategy_files:
            try:
                with open(strategy_file, "r", encoding="utf-8") as handle:
                    strategy_data = json.load(handle)

                name = strategy_data.get("name", strategy_file.stem)
                description = strategy_data.get("description")
                strategy_type = strategy_data.get("type", "custom")

                # Match on client_strategy_id (if present) before falling back to name
                client_id = strategy_data.get("id") or strategy_data.get("client_id")
                query = None
                if client_id:
                    query = (
                        db.query(Strategy)
                        .filter(Strategy.client_strategy_id == client_id)
                        .first()
                    )
                if not query:
                    query = db.query(Strategy).filter(Strategy.name == name).first()

                if query:
                    print(f"⏭️  Skipping '{name}' (already exists)")
                    continue

                strategy = Strategy(
                    name=name,
                    description=description,
                    strategy_type=strategy_type,
                    client_strategy_id=client_id,
                    config=strategy_data,
                    is_active=strategy_data.get("is_active", False),
                    is_autopilot=strategy_data.get("is_autopilot", False),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )

                db.add(strategy)
                migrated_count += 1
                print(f"✅ Migrated: '{name}' ({strategy_type})")

            except json.JSONDecodeError as exc:
                print(f"❌ Failed to parse {strategy_file}: invalid JSON - {exc}")
                failed_count += 1
            except Exception as exc:  # noqa: BLE001
                print(f"❌ Failed to migrate {strategy_file}: {exc}")
                failed_count += 1

        if migrated_count > 0:
            db.commit()
            print(
                f"\n✅ Successfully committed {migrated_count} strateg{'y' if migrated_count == 1 else 'ies'} to database"
            )

    except Exception as exc:  # noqa: BLE001
        print(f"\n❌ Migration failed: {exc}")
        db.rollback()
        raise
    finally:
        db.close()

    return migrated_count, failed_count


def migrate_strategies_from_export(db, user: User, strategies: list[dict[str, Any]]) -> int:
    """Persist strategies exported from localStorage."""

    if not strategies:
        return 0

    migrated = 0
    for entry in strategies:
        client_id = entry.get("id") or entry.get("clientId")
        existing = None
        if client_id:
            existing = (
                db.query(Strategy)
                .filter(Strategy.client_strategy_id == client_id)
                .first()
            )

        if not existing and client_id:
            # Fallback: scan existing strategies for matching config ID
            for candidate in db.query(Strategy).filter(Strategy.user_id == user.id).all():
                config = candidate.config or {}
                if isinstance(config, dict) and config.get("id") == client_id:
                    existing = candidate
                    break

        if existing:
            merged = dict(existing.config or {})
            merged.update(entry)
            existing.config = merged
            existing.name = entry.get("name") or existing.name
            existing.strategy_type = entry.get("strategy_type") or existing.strategy_type
            existing.client_strategy_id = client_id or existing.client_strategy_id
            existing.updated_at = datetime.utcnow()
            migrated += 1
            continue

        strategy = Strategy(
            user_id=user.id,
            name=entry.get("name") or entry.get("title") or client_id or "Untitled Strategy",
            description=entry.get("description"),
            strategy_type=entry.get("strategy_type", "custom"),
            client_strategy_id=client_id,
            config=entry,
            is_active=entry.get("status") == "active",
            is_autopilot=bool(entry.get("autopilot")),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(strategy)
        migrated += 1

    db.commit()
    return migrated


def migrate_order_history(db, user: User, orders: list[dict[str, Any]]) -> int:
    if not orders:
        return 0

    migrated = 0
    for order in orders:
        client_id = order.get("id")
        existing = None
        if client_id:
            existing = (
                db.query(OrderHistory)
                .filter(OrderHistory.client_order_id == client_id)
                .first()
            )

        if existing:
            # Update timestamps/status if they changed
            existing.status = order.get("status", existing.status)
            existing.is_dry_run = order.get("dryRun", existing.is_dry_run)
            existing.limit_price = order.get("limitPrice")
            existing.quantity = order.get("qty", existing.quantity)
            existing.order_type = order.get("type", existing.order_type)
            existing.symbol = order.get("symbol", existing.symbol)
            existing.side = order.get("side", existing.side)
            existing.executed_at = (
                datetime.fromisoformat(order["timestamp"])
                if order.get("timestamp")
                else existing.executed_at
            )
            migrated += 1
            continue

        created_at = None
        timestamp = order.get("timestamp")
        if timestamp:
            try:
                normalised = timestamp.replace("Z", "+00:00")
                created_at = datetime.fromisoformat(normalised)
            except ValueError:
                created_at = datetime.utcnow()
        else:
            created_at = datetime.utcnow()

        history = OrderHistory(
            user_id=user.id,
            client_order_id=client_id,
            symbol=order.get("symbol", "UNKNOWN"),
            side=order.get("side", "buy"),
            quantity=float(order.get("qty", 0)),
            order_type=order.get("type", "market"),
            limit_price=order.get("limitPrice"),
            status=order.get("status", "pending"),
            is_dry_run=bool(order.get("dryRun", False)),
            executed_at=created_at,
            created_at=created_at,
        )
        db.add(history)
        migrated += 1

    db.commit()
    return migrated


def migrate_local_storage(path: Path) -> dict[str, int]:
    """Ingest a localStorage export file."""

    parsed = parse_local_storage_dump(path)
    stats = {"users": 0, "settings": 0, "profiles": 0, "strategies": 0, "orders": 0}

    db = SessionLocal()
    try:
        exported_user = parsed.get(LOCAL_STORAGE_KEYS["user"])
        if isinstance(exported_user, dict):
            user = get_or_create_user(db, exported_user)
            stats["users"] = 1
        else:
            user = get_or_create_user(db, None)

        stats["settings"] = migrate_user_settings(
            db, user, parsed.get(LOCAL_STORAGE_KEYS["settings"]) or {}
        )

        stats["profiles"] += migrate_user_profile(
            db,
            user,
            "app_user",
            exported_user if isinstance(exported_user, dict) else None,
        )
        stats["profiles"] += migrate_user_profile(
            db,
            user,
            "investment_profile",
            parsed.get(LOCAL_STORAGE_KEYS["profile"]),
        )

        stats["strategies"] = migrate_strategies_from_export(
            db,
            user,
            parsed.get(LOCAL_STORAGE_KEYS["strategies"]) or [],
        )

        stats["orders"] = migrate_order_history(
            db,
            user,
            parsed.get(LOCAL_STORAGE_KEYS["orders"]) or [],
        )

        print(
            "\n📦 LocalStorage migration summary:\n"
            f"   👤 Users updated:      {stats['users']}\n"
            f"   ⚙️  Settings migrated:  {stats['settings']}\n"
            f"   🧠 Profiles migrated:  {stats['profiles']}\n"
            f"   📈 Strategies migrated: {stats['strategies']}\n"
            f"   📝 Orders migrated:     {stats['orders']}\n"
        )

        return stats
    finally:
        db.close()


def print_current_strategies():
    """Print all strategies currently in database."""

    db = SessionLocal()
    try:
        strategies = db.query(Strategy).all()
        if not strategies:
            print("\nℹ️  No strategies found in database")
            return

        print(f"\n📊 Current Database Strategies ({len(strategies)} total):")
        print("=" * 80)
        for strategy in strategies:
            active_status = "🟢 Active" if strategy.is_active else "⚪ Inactive"
            autopilot_status = "🤖 Autopilot" if strategy.is_autopilot else ""
            client_id = strategy.client_strategy_id or "-"
            print(
                f"{strategy.id:3d} | {active_status} {autopilot_status:12s} | "
                f"{strategy.strategy_type:18s} | {strategy.name} | client_id={client_id}"
            )
        print("=" * 80)
    finally:
        db.close()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Migrate historical frontend state into the database",
    )
    parser.add_argument(
        "--local-storage",
        dest="local_storage",
        type=Path,
        help="Path to JSON export produced from browser localStorage",
    )

    args = parser.parse_args(argv)

    print("\n" + "=" * 80)
    print("🗂️  PaiiD Migration Tool - LocalStorage → PostgreSQL")
    print("=" * 80)

    if args.local_storage:
        if args.local_storage.exists():
            migrate_local_storage(args.local_storage)
        else:
            print(f"⚠️  LocalStorage export not found: {args.local_storage}")

    print_current_strategies()

    migrated, failed = migrate_strategies_from_directory()

    if migrated or failed:
        print_current_strategies()

    print("\n" + "=" * 80)
    print("📈 Migration Summary:")
    print(f"   ✅ File strategies migrated: {migrated}")
    print(f"   ❌ File migrations failed:  {failed}")
    print("=" * 80 + "\n")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
