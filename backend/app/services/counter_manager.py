"""
Counter Manager Service
Manages all monitoring counters with Redis backend for real-time tracking
"""

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from ..core.config import get_settings
from ..core.redis_client import get_redis


logger = logging.getLogger(__name__)
settings = get_settings()


class CounterManager:
    """Manages all monitoring counters with Redis backend"""

    def __init__(self):
        self.redis = get_redis()
        self.prefix = "monitor:counter:"

    async def increment(self, counter_name: str, amount: int = 1) -> int:
        """
        Increment a counter

        Args:
            counter_name: Name of the counter
            amount: Amount to increment by

        Returns:
            New counter value
        """
        try:
            key = f"{self.prefix}{counter_name}"
            new_value = await self.redis.incrby(key, amount)

            # Also track in time-series for trending
            timestamp = datetime.now(UTC).timestamp()
            await self.redis.zadd(
                f"{self.prefix}timeseries:{counter_name}", {str(timestamp): amount}
            )

            logger.debug(
                f"Incremented counter {counter_name} by {amount} to {new_value}"
            )
            return new_value

        except Exception as e:
            logger.error(f"Error incrementing counter {counter_name}: {e}")
            return 0

    async def get(self, counter_name: str) -> int:
        """
        Get current counter value

        Args:
            counter_name: Name of the counter

        Returns:
            Counter value (0 if not found)
        """
        try:
            key = f"{self.prefix}{counter_name}"
            value = await self.redis.get(key)
            return int(value) if value else 0

        except Exception as e:
            logger.error(f"Error getting counter {counter_name}: {e}")
            return 0

    async def get_all(self) -> dict[str, int]:
        """
        Get all counters

        Returns:
            Dictionary of counter names to values
        """
        try:
            pattern = f"{self.prefix}*"
            keys = await self.redis.keys(pattern)
            counters = {}

            for key in keys:
                # Skip timeseries keys
                if "timeseries" in key:
                    continue

                name = key.replace(self.prefix, "")
                value = await self.redis.get(key)
                counters[name] = int(value) if value else 0

            return counters

        except Exception as e:
            logger.error(f"Error getting all counters: {e}")
            return {}

    async def set(self, counter_name: str, value: int) -> bool:
        """
        Set counter to specific value

        Args:
            counter_name: Name of the counter
            value: Value to set

        Returns:
            True if successful
        """
        try:
            key = f"{self.prefix}{counter_name}"
            await self.redis.set(key, value)
            logger.debug(f"Set counter {counter_name} to {value}")
            return True

        except Exception as e:
            logger.error(f"Error setting counter {counter_name}: {e}")
            return False

    async def reset(self, counter_name: str) -> bool:
        """
        Reset counter to zero

        Args:
            counter_name: Name of the counter

        Returns:
            True if successful
        """
        return await self.set(counter_name, 0)

    async def reset_weekly_counters(self) -> int:
        """
        Reset weekly counters (called by cron/scheduler)

        Returns:
            Number of counters reset
        """
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

        reset_count = 0
        for counter in weekly_counters:
            if await self.reset(counter):
                reset_count += 1

        logger.info(f"Reset {reset_count} weekly counters")
        return reset_count

    async def get_trend(
        self, counter_name: str, hours: int = 24
    ) -> list[dict[str, Any]]:
        """
        Get counter trend over time

        Args:
            counter_name: Name of the counter
            hours: Number of hours to look back

        Returns:
            List of {"timestamp": float, "value": int} dicts
        """
        try:
            key = f"{self.prefix}timeseries:{counter_name}"
            since = (datetime.now(UTC) - timedelta(hours=hours)).timestamp()

            # Get all entries since timestamp
            data = await self.redis.zrangebyscore(key, since, "+inf", withscores=True)

            return [
                {"timestamp": float(score), "value": int(float(value))}
                for value, score in data
            ]

        except Exception as e:
            logger.error(f"Error getting trend for {counter_name}: {e}")
            return []

    async def cleanup_old_timeseries(self, days: int = 90) -> int:
        """
        Clean up timeseries data older than specified days

        Args:
            days: Number of days to keep

        Returns:
            Number of entries removed
        """
        try:
            pattern = f"{self.prefix}timeseries:*"
            keys = await self.redis.keys(pattern)
            cutoff = (datetime.now(UTC) - timedelta(days=days)).timestamp()

            total_removed = 0
            for key in keys:
                removed = await self.redis.zremrangebyscore(key, "-inf", cutoff)
                total_removed += removed

            logger.info(f"Cleaned up {total_removed} old timeseries entries")
            return total_removed

        except Exception as e:
            logger.error(f"Error cleaning up timeseries: {e}")
            return 0


# Global instance
_counter_manager: CounterManager | None = None


def get_counter_manager() -> CounterManager:
    """Get or create counter manager instance"""
    global _counter_manager
    if _counter_manager is None:
        _counter_manager = CounterManager()
    return _counter_manager
