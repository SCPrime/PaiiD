"""Add positions table and migrate equity history"""

from __future__ import annotations

import json
from collections.abc import Sequence
from datetime import datetime
from pathlib import Path

import sqlalchemy as sa
from sqlalchemy import orm

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "4b3a2394d1ce"
down_revision: str | Sequence[str] | None = "037b216f2ed1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _performance_table() -> sa.Table:
    return sa.table(
        "performance",
        sa.column("id", sa.Integer),
        sa.column("user_id", sa.Integer),
        sa.column("date", sa.DateTime),
        sa.column("portfolio_value", sa.Float),
        sa.column("cash", sa.Float),
        sa.column("positions_value", sa.Float),
        sa.column("num_positions", sa.Integer),
        sa.column("total_pnl", sa.Float),
        sa.column("total_pnl_percent", sa.Float),
        sa.column("day_pnl", sa.Float),
        sa.column("day_pnl_percent", sa.Float),
        sa.column("sharpe_ratio", sa.Float),
        sa.column("max_drawdown", sa.Float),
        sa.column("max_drawdown_percent", sa.Float),
        sa.column("volatility", sa.Float),
        sa.column("total_trades", sa.Integer),
        sa.column("winning_trades", sa.Integer),
        sa.column("losing_trades", sa.Integer),
        sa.column("win_rate", sa.Float),
        sa.column("created_at", sa.DateTime),
    )


def _equity_snapshots_table() -> sa.Table:
    return sa.table(
        "equity_snapshots",
        sa.column("id", sa.Integer),
        sa.column("user_id", sa.Integer),
        sa.column("timestamp", sa.DateTime),
        sa.column("equity", sa.Float),
        sa.column("cash", sa.Float),
        sa.column("positions_value", sa.Float),
        sa.column("num_positions", sa.Integer),
        sa.column("extra_data", sa.JSON),
    )


def upgrade() -> None:
    """Upgrade schema and migrate seed data from file-based storage."""

    # Schema changes: positions table + trades.position_id foreign key
    op.create_table(
        "positions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("symbol", sa.String(length=20), nullable=False),
        sa.Column("option_symbol", sa.String(length=50), nullable=True),
        sa.Column("asset_class", sa.String(length=20), nullable=False, server_default=sa.text("'option'")),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("avg_entry_price", sa.Float(), nullable=False),
        sa.Column("current_price", sa.Float(), nullable=True),
        sa.Column("market_value", sa.Float(), nullable=True),
        sa.Column("cost_basis", sa.Float(), nullable=True),
        sa.Column("unrealized_pl", sa.Float(), nullable=True),
        sa.Column("unrealized_pl_percent", sa.Float(), nullable=True),
        sa.Column("expiration", sa.Date(), nullable=True),
        sa.Column("days_to_expiry", sa.Integer(), nullable=True),
        sa.Column("greeks", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'open'")),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("opened_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("closed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_positions_id"), "positions", ["id"], unique=False)
    op.create_index(op.f("ix_positions_symbol"), "positions", ["symbol"], unique=False)
    op.create_index(op.f("ix_positions_option_symbol"), "positions", ["option_symbol"], unique=False)
    op.create_index(op.f("ix_positions_asset_class"), "positions", ["asset_class"], unique=False)
    op.create_index(op.f("ix_positions_status"), "positions", ["status"], unique=False)
    op.create_index(op.f("ix_positions_opened_at"), "positions", ["opened_at"], unique=False)

    op.add_column("trades", sa.Column("position_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_trades_position_id"), "trades", ["position_id"], unique=False)
    op.create_foreign_key(
        "fk_trades_position_id",
        "trades",
        "positions",
        ["position_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # Data migration: import legacy equity snapshots stored as JSON
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    performance_table = _performance_table()
    equity_table = _equity_snapshots_table()

    try:
        # Only migrate if tables are empty to avoid duplicating data on re-run
        perf_exists = session.execute(sa.select(sa.func.count()).select_from(performance_table)).scalar()
        equity_exists = session.execute(sa.select(sa.func.count()).select_from(equity_table)).scalar()

        data_dir = Path(__file__).resolve().parents[2] / "data" / "equity"
        data_file = data_dir / "equity_history.json"

        if data_file.exists() and (not perf_exists and not equity_exists):
            with data_file.open() as fh:
                try:
                    snapshots: list[dict] = json.load(fh)
                except json.JSONDecodeError:
                    snapshots = []

            for snapshot in snapshots:
                timestamp_raw = snapshot.get("timestamp")
                if not timestamp_raw:
                    continue

                try:
                    timestamp = datetime.fromisoformat(timestamp_raw)
                except ValueError:
                    continue

                equity = float(snapshot.get("equity", 0) or 0)
                cash = float(snapshot.get("cash", 0) or 0)
                positions_value = float(snapshot.get("positions_value", 0) or 0)
                num_positions = int(snapshot.get("num_positions", 0) or 0)

                session.execute(
                    equity_table.insert().values(
                        user_id=None,
                        timestamp=timestamp,
                        equity=equity,
                        cash=cash,
                        positions_value=positions_value,
                        num_positions=num_positions,
                        extra_data={},
                    )
                )

                session.execute(
                    performance_table.insert().values(
                        user_id=None,
                        date=timestamp,
                        portfolio_value=equity,
                        cash=cash,
                        positions_value=positions_value,
                        num_positions=num_positions,
                        total_pnl=0.0,
                        total_pnl_percent=0.0,
                        day_pnl=0.0,
                        day_pnl_percent=0.0,
                        sharpe_ratio=None,
                        max_drawdown=None,
                        max_drawdown_percent=None,
                        volatility=None,
                        total_trades=0,
                        winning_trades=0,
                        losing_trades=0,
                        win_rate=None,
                        created_at=timestamp,
                    )
                )

            if snapshots:
                session.commit()
    finally:
        session.close()


def downgrade() -> None:
    """Downgrade schema changes."""

    op.drop_constraint("fk_trades_position_id", "trades", type_="foreignkey")
    op.drop_index(op.f("ix_trades_position_id"), table_name="trades")
    op.drop_column("trades", "position_id")

    op.drop_index(op.f("ix_positions_opened_at"), table_name="positions")
    op.drop_index(op.f("ix_positions_status"), table_name="positions")
    op.drop_index(op.f("ix_positions_asset_class"), table_name="positions")
    op.drop_index(op.f("ix_positions_option_symbol"), table_name="positions")
    op.drop_index(op.f("ix_positions_symbol"), table_name="positions")
    op.drop_index(op.f("ix_positions_id"), table_name="positions")
    op.drop_table("positions")
