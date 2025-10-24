"""
Equity Curve Tracking Service

Tracks daily portfolio equity for historical performance analysis.
Stores equity snapshots in JSON files for P&L Dashboard.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

from ..core.time_utils import ensure_utc, utc_now, utc_now_isoformat
from ..services.tradier_client import get_tradier_client


logger = logging.getLogger(__name__)

# Data storage path
EQUITY_DATA_DIR = Path("data/equity")
EQUITY_DATA_DIR.mkdir(parents=True, exist_ok=True)

EQUITY_FILE = EQUITY_DATA_DIR / "equity_history.json"


class EquityTracker:
    """Tracks daily equity snapshots for performance analysis"""

    def __init__(self):
        self.data_file = EQUITY_FILE

    def record_snapshot(self) -> dict:
        """
        Record current portfolio equity snapshot

        Returns dict with:
            - timestamp
            - equity (total portfolio value)
            - cash
            - positions_value
            - num_positions
        """
        try:
            client = get_tradier_client()

            # Get account data
            account = client.get_account()
            positions = client.get_positions()

            # Calculate values
            equity = float(account.get("portfolio_value", 0))
            cash = float(account.get("cash", 0))
            positions_value = equity - cash
            num_positions = len(positions)

            # Create snapshot
            snapshot = {
                "timestamp": utc_now_isoformat(),
                "equity": round(equity, 2),
                "cash": round(cash, 2),
                "positions_value": round(positions_value, 2),
                "num_positions": num_positions,
            }

            # Append to history
            history = self.load_history()
            history.append(snapshot)

            # Save updated history
            self.save_history(history)

            logger.info(f"✅ Recorded equity snapshot: ${equity:.2f}")
            return snapshot

        except Exception as e:
            logger.error(f"❌ Failed to record equity snapshot: {e!s}")
            raise

    def load_history(self) -> list[dict]:
        """Load equity history from file"""
        try:
            if self.data_file.exists():
                with open(self.data_file) as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"❌ Failed to load equity history: {e!s}")
            return []

    def save_history(self, history: list[dict]):
        """Save equity history to file"""
        try:
            with open(self.data_file, "w") as f:
                json.dump(history, f, indent=2)
            logger.info(f"✅ Saved equity history ({len(history)} snapshots)")
        except Exception as e:
            logger.error(f"❌ Failed to save equity history: {e!s}")
            raise

    def get_history(
        self, start_date: datetime | None = None, end_date: datetime | None = None
    ) -> list[dict]:
        """
        Get equity history within date range

        Args:
            start_date: Filter snapshots after this date
            end_date: Filter snapshots before this date

        Returns:
            List of equity snapshots
        """
        history = self.load_history()

        start_dt = ensure_utc(start_date) if start_date else None
        end_dt = ensure_utc(end_date) if end_date else None

        if not start_dt and not end_dt:
            return history

        # Filter by date range
        filtered = []
        for snapshot in history:
            snapshot_date = ensure_utc(
                datetime.fromisoformat(snapshot["timestamp"].replace("Z", "+00:00"))
            )

            if start_dt and snapshot_date < start_dt:
                continue

            if end_dt and snapshot_date > end_dt:
                continue

            filtered.append(snapshot)

        return filtered

    def calculate_metrics(self, period_days: int = 30) -> dict:
        """
        Calculate performance metrics from equity history

        Args:
            period_days: Number of days to analyze

        Returns:
            Dict with performance metrics:
                - total_return
                - max_drawdown
                - sharpe_ratio (simplified)
                - win_days
                - loss_days
        """
        history = self.load_history()

        if not history:
            return {
                "total_return": 0,
                "max_drawdown": 0,
                "sharpe_ratio": 0,
                "win_days": 0,
                "loss_days": 0,
            }

        # Get snapshots within period
        cutoff_dt = utc_now() - timedelta(days=period_days)
        recent_snapshots = [
            s
            for s in history
            if ensure_utc(
                datetime.fromisoformat(s["timestamp"].replace("Z", "+00:00"))
            )
            >= cutoff_dt
        ]

        if len(recent_snapshots) < 2:
            return {
                "total_return": 0,
                "max_drawdown": 0,
                "sharpe_ratio": 0,
                "win_days": 0,
                "loss_days": 0,
            }

        # Calculate total return
        start_equity = recent_snapshots[0]["equity"]
        end_equity = recent_snapshots[-1]["equity"]
        total_return = end_equity - start_equity
        total_return_pct = (total_return / start_equity * 100) if start_equity > 0 else 0

        # Calculate max drawdown
        peak = start_equity
        max_dd = 0
        for snapshot in recent_snapshots:
            equity = snapshot["equity"]
            if equity > peak:
                peak = equity
            dd = (peak - equity) / peak if peak > 0 else 0
            if dd > max_dd:
                max_dd = dd

        # Count winning/losing days
        win_days = 0
        loss_days = 0
        for i in range(1, len(recent_snapshots)):
            prev_equity = recent_snapshots[i - 1]["equity"]
            curr_equity = recent_snapshots[i]["equity"]
            if curr_equity > prev_equity:
                win_days += 1
            elif curr_equity < prev_equity:
                loss_days += 1

        # Simplified Sharpe ratio
        # Calculate daily returns
        daily_returns = []
        for i in range(1, len(recent_snapshots)):
            prev_equity = recent_snapshots[i - 1]["equity"]
            curr_equity = recent_snapshots[i]["equity"]
            daily_return = (curr_equity - prev_equity) / prev_equity if prev_equity > 0 else 0
            daily_returns.append(daily_return)

        if daily_returns:
            avg_return = sum(daily_returns) / len(daily_returns)
            # Standard deviation
            variance = sum((r - avg_return) ** 2 for r in daily_returns) / len(daily_returns)
            std_dev = variance**0.5

            # Sharpe ratio (assuming 0% risk-free rate)
            sharpe = (avg_return / std_dev * (252**0.5)) if std_dev > 0 else 0
        else:
            sharpe = 0

        return {
            "total_return": round(total_return, 2),
            "total_return_percent": round(total_return_pct, 2),
            "max_drawdown": round(max_dd * 100, 2),
            "sharpe_ratio": round(sharpe, 2),
            "win_days": win_days,
            "loss_days": loss_days,
            "num_snapshots": len(recent_snapshots),
        }


# Singleton instance
_equity_tracker = None


def get_equity_tracker() -> EquityTracker:
    """Get singleton EquityTracker instance"""
    global _equity_tracker
    if _equity_tracker is None:
        _equity_tracker = EquityTracker()
    return _equity_tracker
