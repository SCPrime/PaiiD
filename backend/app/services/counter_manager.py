"""
Counter Manager Service - Tracks all repository metrics and events

Manages running counters for:
- Event counts (commits, pushes, PRs, issues, deployments)
- Issue health metrics
- Project completion progress
- System health indicators
"""

import json
from datetime import datetime, timedelta
from typing import Any

from app.core.redis_client import get_redis


class CounterManager:
    """Manages all monitoring counters with Redis backend"""

    def __init__(self):
        self.redis = None
        self.prefix = "monitor:counter:"

    async def initialize(self):
        """Initialize Redis connection"""
        self.redis = await get_redis()

    async def increment(self, counter_name: str, amount: int = 1) -> int:
        """
        Increment a counter

        Args:
            counter_name: Name of the counter (e.g., 'commits', 'issues_opened')
            amount: Amount to increment by (default: 1)

        Returns:
            New counter value
        """
        if not self.redis:
            await self.initialize()

        key = f"{self.prefix}{counter_name}"
        new_value = await self.redis.incrby(key, amount)

        # Also track in time-series for trending
        timestamp = datetime.utcnow().timestamp()
        await self.redis.zadd(
            f"{self.prefix}timeseries:{counter_name}", {str(timestamp): amount}
        )

        return new_value

    async def get(self, counter_name: str) -> int:
        """
        Get current counter value

        Args:
            counter_name: Name of the counter

        Returns:
            Current counter value (0 if not exists)
        """
        if not self.redis:
            await self.initialize()

        key = f"{self.prefix}{counter_name}"
        value = await self.redis.get(key)
        return int(value) if value else 0

    async def set(self, counter_name: str, value: int):
        """
        Set counter to specific value

        Args:
            counter_name: Name of the counter
            value: Value to set
        """
        if not self.redis:
            await self.initialize()

        key = f"{self.prefix}{counter_name}"
        await self.redis.set(key, value)

    async def get_all(self) -> dict[str, int]:
        """
        Get all counters

        Returns:
            Dictionary of counter names to values
        """
        if not self.redis:
            await self.initialize()

        pattern = f"{self.prefix}*"
        keys = []
        async for key in self.redis.scan_iter(match=pattern):
            if b"timeseries" not in key:
                keys.append(key.decode() if isinstance(key, bytes) else key)

        counters = {}
        for key in keys:
            name = key.replace(self.prefix, "")
            counters[name] = await self.get(name)

        return counters

    async def reset(self, counter_name: str):
        """Reset a counter to 0"""
        await self.set(counter_name, 0)

    async def reset_weekly_counters(self):
        """Reset weekly counters (called by cron every Monday)"""
        weekly_counters = [
            "commits",
            "pushes",
            "pulls_opened",
            "pulls_merged",
            "pulls_closed",
            "issues_opened",
            "issues_closed",
            "deployments",
            "build_failures",
            "test_failures",
            "conflicts",
            "hotfixes",
        ]

        for counter in weekly_counters:
            await self.reset(counter)

    async def get_trend(
        self, counter_name: str, hours: int = 24
    ) -> list[dict[str, Any]]:
        """
        Get counter trend over time

        Args:
            counter_name: Name of the counter
            hours: Number of hours to look back

        Returns:
            List of {timestamp, value} dicts
        """
        if not self.redis:
            await self.initialize()

        key = f"{self.prefix}timeseries:{counter_name}"
        since = (datetime.utcnow() - timedelta(hours=hours)).timestamp()

        # Get all entries since timestamp
        data = await self.redis.zrangebyscore(key, since, "+inf", withscores=True)

        trend = []
        for value, score in data:
            trend.append(
                {
                    "timestamp": datetime.fromtimestamp(score).isoformat(),
                    "value": int(value.decode() if isinstance(value, bytes) else value),
                }
            )

        return trend

    async def get_completion_progress(self) -> dict[str, Any]:
        """
        Get project completion progress

        Returns:
            Completion metrics including overall progress and phase breakdown
        """
        # IMPLEMENTATION NOTE: Progress calculated from TODO.md parsing
        # Future enhancement: Automate parsing of TODO.md checkboxes to populate these counters
        # Current: Manual updates via counter increments when tasks complete
        progress = {
            "overall_progress": await self.get("progress_overall") / 100,
            "phases": {
                "phase_0_prep": {
                    "progress": await self.get("progress_phase_0") / 100,
                    "tasks_completed": await self.get("tasks_completed_phase_0"),
                    "tasks_total": await self.get("tasks_total_phase_0"),
                    "estimated_hours_remaining": await self.get(
                        "hours_remaining_phase_0"
                    ),
                },
                "phase_1_options": {
                    "progress": await self.get("progress_phase_1") / 100,
                    "tasks_completed": await self.get("tasks_completed_phase_1"),
                    "tasks_total": await self.get("tasks_total_phase_1"),
                    "estimated_hours_remaining": await self.get(
                        "hours_remaining_phase_1"
                    ),
                },
                "phase_2_ml": {
                    "progress": await self.get("progress_phase_2") / 100,
                    "tasks_completed": await self.get("tasks_completed_phase_2"),
                    "tasks_total": await self.get("tasks_total_phase_2"),
                    "estimated_hours_remaining": await self.get(
                        "hours_remaining_phase_2"
                    ),
                },
                "phase_3_ui": {
                    "progress": await self.get("progress_phase_3") / 100,
                    "tasks_completed": await self.get("tasks_completed_phase_3"),
                    "tasks_total": await self.get("tasks_total_phase_3"),
                    "estimated_hours_remaining": await self.get(
                        "hours_remaining_phase_3"
                    ),
                },
                "phase_4_cleanup": {
                    "progress": await self.get("progress_phase_4") / 100,
                    "tasks_completed": await self.get("tasks_completed_phase_4"),
                    "tasks_total": await self.get("tasks_total_phase_4"),
                    "estimated_hours_remaining": await self.get(
                        "hours_remaining_phase_4"
                    ),
                },
            },
            "timeline": {
                "total_hours_budgeted": 80,
                "hours_completed": await self.get("hours_completed")
                / 10,  # Stored as tenths
                "hours_remaining": await self.get("hours_remaining") / 10,
                "estimated_completion_date": await self.redis.get(
                    f"{self.prefix}completion_date"
                ),
                "days_behind_schedule": await self.get("days_behind_schedule"),
            },
        }

        return progress

    async def update_phase_progress(
        self, phase: str, tasks_completed: int, tasks_total: int, hours_remaining: float
    ):
        """
        Update progress for a specific phase

        Args:
            phase: Phase identifier (e.g., 'phase_0', 'phase_1')
            tasks_completed: Number of completed tasks
            tasks_total: Total number of tasks
            hours_remaining: Estimated hours remaining
        """
        progress_pct = (
            int(tasks_completed / tasks_total * 100) if tasks_total > 0 else 0
        )

        await self.set(f"progress_{phase}", progress_pct)
        await self.set(f"tasks_completed_{phase}", tasks_completed)
        await self.set(f"tasks_total_{phase}", tasks_total)
        await self.set(f"hours_remaining_{phase}", int(hours_remaining))

        # Recalculate overall progress
        await self.recalculate_overall_progress()

    async def recalculate_overall_progress(self):
        """Recalculate overall project progress from all phases"""
        total_tasks_completed = 0
        total_tasks = 0

        for phase in ["phase_0", "phase_1", "phase_2", "phase_3", "phase_4"]:
            total_tasks_completed += await self.get(f"tasks_completed_{phase}")
            total_tasks += await self.get(f"tasks_total_{phase}")

        overall_pct = (
            int(total_tasks_completed / total_tasks * 100) if total_tasks > 0 else 0
        )
        await self.set("progress_overall", overall_pct)

        # Update hours
        total_hours_remaining = 0
        for phase in ["phase_0", "phase_1", "phase_2", "phase_3", "phase_4"]:
            total_hours_remaining += await self.get(f"hours_remaining_{phase}")

        hours_completed = 80 - total_hours_remaining
        await self.set("hours_completed", int(hours_completed * 10))  # Store as tenths
        await self.set("hours_remaining", int(total_hours_remaining * 10))

    async def record_progress_snapshot(self):
        """
        Record current progress for historical tracking (call daily)

        Stores progress data points for line graph visualization
        """
        date_key = datetime.utcnow().strftime("%Y-%m-%d")
        overall_progress = await self.get("progress_overall")

        # Calculate target progress (assuming linear timeline over 80 days)
        # This would need adjustment based on actual start date
        # For now, we'll store actual progress only

        await self.redis.hset(
            f"{self.prefix}progress_history",
            date_key,
            json.dumps(
                {
                    "completion": overall_progress,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ),
        )

    async def get_progress_history(self, days: int = 30) -> list[dict[str, Any]]:
        """
        Get historical progress data for line graph

        Args:
            days: Number of days to retrieve

        Returns:
            List of progress data points
        """
        history = await self.redis.hgetall(f"{self.prefix}progress_history")

        data_points = []
        for date_str, value_json in history.items():
            if isinstance(date_str, bytes):
                date_str = date_str.decode()
            if isinstance(value_json, bytes):
                value_json = value_json.decode()

            data = json.loads(value_json)
            data_points.append(
                {
                    "date": date_str,
                    "completion": data["completion"],
                    "target": data.get(
                        "target", data["completion"]
                    ),  # Calculate target separately
                }
            )

        # Sort by date
        data_points.sort(key=lambda x: x["date"])

        # Return last N days
        return data_points[-days:] if len(data_points) > days else data_points


# Singleton instance
_counter_manager = None


async def get_counter_manager() -> CounterManager:
    """Get or create CounterManager singleton"""
    global _counter_manager
    if _counter_manager is None:
        _counter_manager = CounterManager()
        await _counter_manager.initialize()
    return _counter_manager
