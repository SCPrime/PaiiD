"""
Equity Curve Tracking Service

Records daily equity snapshots and performance metrics in the SQL database.
Legacy JSON persistence is migrated via Alembic to the new tables.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Callable

from sqlalchemy.orm import Session

from ..db.session import SessionLocal
from ..models.database import EquitySnapshot, Performance
from ..services.tradier_client import get_tradier_client

logger = logging.getLogger(__name__)


class EquityTracker:
    """Tracks portfolio equity snapshots and derived performance metrics."""

    def __init__(self, session_factory: Callable[[], Session] = SessionLocal):
        self._session_factory = session_factory

    def record_snapshot(self) -> dict:
        """Record the latest portfolio equity information in the database."""

        session = self._session_factory()
        try:
            client = get_tradier_client()

            account = client.get_account()
            positions = client.get_positions()

            equity = float(account.get("portfolio_value", 0) or 0)
            cash = float(account.get("cash", 0) or 0)
            positions_value = equity - cash
            num_positions = len(positions)

            timestamp = datetime.utcnow()

            snapshot_model = EquitySnapshot(
                user_id=None,
                timestamp=timestamp,
                equity=equity,
                cash=cash,
                positions_value=positions_value,
                num_positions=num_positions,
                extra_data={"source": "tradier"},
            )
            session.add(snapshot_model)

            performance_model = Performance(
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
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                created_at=timestamp,
            )
            session.add(performance_model)

            session.commit()

            logger.info("✅ Recorded equity snapshot: $%.2f", equity)
            return {
                "timestamp": timestamp.isoformat(),
                "equity": round(equity, 2),
                "cash": round(cash, 2),
                "positions_value": round(positions_value, 2),
                "num_positions": num_positions,
            }
        except Exception as exc:  # pragma: no cover - logging side effect
            session.rollback()
            logger.error("❌ Failed to record equity snapshot: %s", exc)
            raise
        finally:
            session.close()

    def load_history(self) -> list[dict]:
        """Return the full equity history ordered by timestamp."""

        session = self._session_factory()
        try:
            snapshots = (
                session.query(EquitySnapshot)
                .order_by(EquitySnapshot.timestamp.asc())
                .all()
            )
            return [
                {
                    "timestamp": snapshot.timestamp.isoformat(),
                    "equity": snapshot.equity,
                    "cash": snapshot.cash,
                    "positions_value": snapshot.positions_value,
                    "num_positions": snapshot.num_positions,
                }
                for snapshot in snapshots
            ]
        except Exception as exc:  # pragma: no cover - logging side effect
            logger.error("❌ Failed to load equity history: %s", exc)
            return []
        finally:
            session.close()

    def get_history(
        self, start_date: datetime | None = None, end_date: datetime | None = None
    ) -> list[dict]:
        """Return snapshots within an optional date range."""

        session = self._session_factory()
        try:
            query = session.query(EquitySnapshot)
            if start_date:
                query = query.filter(EquitySnapshot.timestamp >= start_date)
            if end_date:
                query = query.filter(EquitySnapshot.timestamp <= end_date)

            snapshots = query.order_by(EquitySnapshot.timestamp.asc()).all()
            return [
                {
                    "timestamp": snapshot.timestamp.isoformat(),
                    "equity": snapshot.equity,
                    "cash": snapshot.cash,
                    "positions_value": snapshot.positions_value,
                    "num_positions": snapshot.num_positions,
                }
                for snapshot in snapshots
            ]
        except Exception as exc:  # pragma: no cover - logging side effect
            logger.error("❌ Failed to query equity history: %s", exc)
            return []
        finally:
            session.close()

    def calculate_metrics(self, period_days: int = 30) -> dict:
        """Calculate rolling performance metrics for the specified period."""

        cutoff = datetime.utcnow() - timedelta(days=period_days)
        history = self.get_history(start_date=cutoff)

        if len(history) < 2:
            return {
                "total_return": 0,
                "total_return_percent": 0,
                "max_drawdown": 0,
                "sharpe_ratio": 0,
                "win_days": 0,
                "loss_days": 0,
            }

        start_equity = history[0]["equity"]
        end_equity = history[-1]["equity"]
        total_return = end_equity - start_equity
        total_return_pct = (total_return / start_equity * 100) if start_equity > 0 else 0

        peak = start_equity
        max_dd = 0.0
        for snapshot in history:
            equity = snapshot["equity"]
            if equity > peak:
                peak = equity
            drawdown = (peak - equity) / peak if peak > 0 else 0
            if drawdown > max_dd:
                max_dd = drawdown

        win_days = 0
        loss_days = 0
        for i in range(1, len(history)):
            prev_equity = history[i - 1]["equity"]
            curr_equity = history[i]["equity"]
            if curr_equity > prev_equity:
                win_days += 1
            elif curr_equity < prev_equity:
                loss_days += 1

        return {
            "total_return": round(total_return, 2),
            "total_return_percent": round(total_return_pct, 2),
            "max_drawdown": round(max_dd * 100, 2),
            "sharpe_ratio": 0,  # Placeholder until risk-free rate & volatility available
            "win_days": win_days,
            "loss_days": loss_days,
        }
