"""Minimal psutil fallback used in offline test environments.

This module provides just enough of the psutil API used by the
:mod:`app.services.health_monitor` module so that the health checks keep
working even when the real psutil dependency cannot be installed (e.g. in
restricted CI sandboxes).

The implementation relies entirely on the Python standard library, so the
figures are best-effort approximations and should not be considered a full
replacement for psutil. Production deployments should install the official
package to get accurate metrics across platforms.
"""
from __future__ import annotations

import os
import shutil
import time
from dataclasses import dataclass

__all__ = ["cpu_percent", "virtual_memory", "disk_usage"]


def _clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    """Clamp *value* to the inclusive ``[minimum, maximum]`` range."""
    return max(minimum, min(value, maximum))


def cpu_percent(interval: float = 0.0) -> float:
    """Return a coarse estimate of CPU utilisation.

    The implementation is intentionally simple: it samples the 1-minute load
    average, normalises it by the number of CPUs, and clamps the result to the
    0-100 range. When *interval* is positive we sleep for that duration to mimic
    psutil's blocking behaviour.
    """
    if interval and interval > 0:
        time.sleep(interval)

    try:
        load_avg, _, _ = os.getloadavg()
        cpu_count = os.cpu_count() or 1
        utilisation = (load_avg / cpu_count) * 100.0
        return _clamp(utilisation)
    except (OSError, ValueError):
        # ``os.getloadavg`` is not available on all platforms; fall back to 0.
        return 0.0


@dataclass
class _MemoryInfo:
    total: int
    available: int
    used: int
    percent: float


def virtual_memory() -> _MemoryInfo:
    """Return basic memory usage statistics.

    We rely on ``/proc/meminfo`` which is present on Linux (the environment
    used in the kata). If the file is unavailable we return zeroed metrics to
    avoid raising an exception in the health monitor.
    """
    try:
        meminfo: dict[str, int] = {}
        with open("/proc/meminfo", "r", encoding="utf-8") as fh:
            for line in fh:
                if ":" not in line:
                    continue
                key, raw_value = line.split(":", 1)
                parts = raw_value.strip().split()
                if not parts:
                    continue
                # Values are reported in kB; convert to bytes.
                meminfo[key] = int(parts[0]) * 1024

        total = meminfo.get("MemTotal", 0)
        available = meminfo.get("MemAvailable", meminfo.get("MemFree", 0))
        used = max(total - available, 0)
        percent = (used / total * 100.0) if total else 0.0
        return _MemoryInfo(total=total, available=available, used=used, percent=percent)
    except (FileNotFoundError, PermissionError, ValueError):
        return _MemoryInfo(total=0, available=0, used=0, percent=0.0)


@dataclass
class _DiskUsage:
    total: int
    used: int
    free: int
    percent: float


def disk_usage(path: str = "/") -> _DiskUsage:
    """Return disk usage statistics for *path*."""
    try:
        usage = shutil.disk_usage(path)
        percent = (usage.used / usage.total * 100.0) if usage.total else 0.0
        return _DiskUsage(total=usage.total, used=usage.used, free=usage.free, percent=percent)
    except (FileNotFoundError, PermissionError, OSError):
        return _DiskUsage(total=0, used=0, free=0, percent=0.0)
