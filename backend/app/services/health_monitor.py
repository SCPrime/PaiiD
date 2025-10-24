"""
Production Health Monitoring Service
"""

import logging
import time
from datetime import datetime

import psutil
import requests


logger = logging.getLogger(__name__)


class HealthMonitor:
    def __init__(self):
        self.start_time = datetime.now()
        self.request_count = 0
        self.error_count = 0
        self.response_times: list[float] = []
        self.cache_hits = 0
        self.cache_misses = 0

    def get_system_health(self) -> dict:
        """Get comprehensive system health metrics"""

        # CPU and Memory
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        # Application metrics
        uptime = (datetime.now() - self.start_time).total_seconds()
        avg_response_time = (
            sum(self.response_times[-100:]) / len(self.response_times[-100:])
            if self.response_times
            else 0
        )
        error_rate = (
            (self.error_count / self.request_count * 100)
            if self.request_count > 0
            else 0
        )

        return {
            "status": "healthy"
            if cpu_percent < 80 and memory.percent < 85
            else "degraded",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": uptime,
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_mb": memory.used / 1024 / 1024,
                "memory_total_mb": memory.total / 1024 / 1024,
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / 1024 / 1024 / 1024,
            },
            "application": {
                "total_requests": self.request_count,
                "total_errors": self.error_count,
                "error_rate_percent": error_rate,
                "avg_response_time_ms": avg_response_time * 1000,
                "requests_per_minute": self.request_count / (uptime / 60)
                if uptime > 0
                else 0,
                "cache_hits": self.cache_hits,
                "cache_misses": self.cache_misses,
                "cache_hit_rate_percent": (
                    (self.cache_hits / (self.cache_hits + self.cache_misses) * 100)
                    if (self.cache_hits + self.cache_misses) > 0
                    else 0
                ),
            },
            "dependencies": self._check_dependencies(),
        }

    def _check_dependencies(self) -> dict:
        """Check health of external dependencies"""
        dependencies = {}

        # Check Tradier API
        try:
            start = time.time()
            resp = requests.get("https://api.tradier.com/v1/markets/quotes", timeout=5)
            dependencies["tradier"] = {
                "status": "up" if resp.status_code < 500 else "down",
                "response_time_ms": (time.time() - start) * 1000,
                "last_checked": datetime.now().isoformat(),
            }
        except Exception as e:
            dependencies["tradier"] = {
                "status": "down",
                "error": str(e),
                "last_checked": datetime.now().isoformat(),
            }

        # Check Alpaca API
        try:
            start = time.time()
            resp = requests.get(
                "https://paper-api.alpaca.markets/v2/account", timeout=5
            )
            dependencies["alpaca"] = {
                "status": "up" if resp.status_code < 500 else "down",
                "response_time_ms": (time.time() - start) * 1000,
                "last_checked": datetime.now().isoformat(),
            }
        except Exception as e:
            dependencies["alpaca"] = {
                "status": "down",
                "error": str(e),
                "last_checked": datetime.now().isoformat(),
            }

        return dependencies

    def record_request(self, response_time: float, is_error: bool = False):
        """Record request metrics"""
        self.request_count += 1
        if is_error:
            self.error_count += 1
        self.response_times.append(response_time)

        # Keep only last 1000 response times
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]

    def record_cache_hit(self):
        self.cache_hits += 1

    def record_cache_miss(self):
        self.cache_misses += 1


# Global instance
health_monitor = HealthMonitor()
