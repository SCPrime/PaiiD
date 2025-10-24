"""Production Health Monitoring Service."""
import logging
import os
import shutil
import time
from types import SimpleNamespace

import requests

from ..core.time_utils import utc_now, utc_now_isoformat

try:  # pragma: no cover - exercised indirectly via shim behaviour
    import psutil  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - import shim path
    psutil = None

logger = logging.getLogger(__name__)


def _cpu_percent(interval: float = 0.0) -> float:
    """Return CPU utilisation percentage with a graceful fallback."""
    if psutil:
        return psutil.cpu_percent(interval=interval)

    try:
        load1, _, _ = os.getloadavg()
        cpu_count = os.cpu_count() or 1
        return min(100.0, (load1 / cpu_count) * 100.0)
    except (OSError, AttributeError):
        return 0.0


def _memory_stats() -> SimpleNamespace:
    """Return memory usage statistics in a psutil-compatible namespace."""
    if psutil:
        return psutil.virtual_memory()

    mem_total = mem_available = None
    try:
        with open("/proc/meminfo", "r", encoding="utf-8") as meminfo:
            for line in meminfo:
                key, value = line.split(":", 1)
                if key in {"MemTotal", "MemAvailable"}:
                    mem_value = int(value.strip().split()[0]) * 1024
                    if key == "MemTotal":
                        mem_total = mem_value
                    else:
                        mem_available = mem_value
        if mem_total and mem_available is not None:
            used = mem_total - mem_available
            percent = (used / mem_total) * 100.0 if mem_total else 0.0
            return SimpleNamespace(
                percent=percent,
                used=used,
                total=mem_total,
            )
    except (OSError, ValueError):
        pass

    return SimpleNamespace(percent=0.0, used=0, total=0)


def _disk_usage(path: str = "/") -> SimpleNamespace:
    """Return disk usage statistics mirroring psutil's interface."""
    if psutil:
        return psutil.disk_usage(path)

    usage = shutil.disk_usage(path)
    used = usage.total - usage.free
    percent = (used / usage.total) * 100.0 if usage.total else 0.0
    return SimpleNamespace(percent=percent, free=usage.free, total=usage.total)


class HealthMonitor:
    def __init__(self):
        self.start_time = utc_now()
        self.request_count = 0
        self.error_count = 0
        self.response_times: list[float] = []
        
    def get_system_health(self) -> dict:
        """Get comprehensive system health metrics"""
        
        # CPU and Memory
        cpu_percent = _cpu_percent(interval=1.0)
        memory = _memory_stats()
        disk = _disk_usage("/")

        # Application metrics
        uptime = (utc_now() - self.start_time).total_seconds()
        avg_response_time = (
            sum(self.response_times[-100:]) / len(self.response_times[-100:])
            if self.response_times else 0
        )
        error_rate = (
            (self.error_count / self.request_count * 100)
            if self.request_count > 0 else 0
        )

        return {
            "status": "healthy" if cpu_percent < 80 and memory.percent < 85 else "degraded",
            "timestamp": utc_now_isoformat(),
            "uptime_seconds": uptime,
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_mb": memory.used / 1024 / 1024,
                "memory_total_mb": memory.total / 1024 / 1024,
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / 1024 / 1024 / 1024
            },
            "application": {
                "total_requests": self.request_count,
                "total_errors": self.error_count,
                "error_rate_percent": error_rate,
                "avg_response_time_ms": avg_response_time * 1000,
                "requests_per_minute": self.request_count / (uptime / 60) if uptime > 0 else 0
            },
            "dependencies": self._check_dependencies()
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
                "last_checked": utc_now_isoformat(),
            }
        except Exception as e:
            dependencies["tradier"] = {
                "status": "down",
                "error": str(e),
                "last_checked": utc_now_isoformat(),
            }
        
        # Check Alpaca API
        try:
            start = time.time()
            resp = requests.get("https://paper-api.alpaca.markets/v2/account", timeout=5)
            dependencies["alpaca"] = {
                "status": "up" if resp.status_code < 500 else "down",
                "response_time_ms": (time.time() - start) * 1000,
                "last_checked": utc_now_isoformat(),
            }
        except Exception as e:
            dependencies["alpaca"] = {
                "status": "down",
                "error": str(e),
                "last_checked": utc_now_isoformat(),
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


# Global instance
health_monitor = HealthMonitor()
