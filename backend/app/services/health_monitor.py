"""Production Health Monitoring Service."""
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import psutil
import requests

logger = logging.getLogger(__name__)


class HealthMonitor:
    """Collects runtime metrics for zombie process detection."""

    def __init__(self):
        self.start_time = datetime.now()
        self.request_count = 0
        self.error_count = 0
        self.response_times: List[float] = []
        self.last_request_at: Optional[datetime] = None
        self.recent_requests: List[Dict[str, object]] = []

        backend_root = Path(__file__).resolve().parents[2]
        repo_root = backend_root.parent
        self._pid_directories = [
            backend_root / ".run",
            repo_root / "frontend" / ".run",
        ]

    def get_system_health(self) -> dict:
        """Get comprehensive system health metrics."""

        cpu_percent = psutil.cpu_percent(interval=0.2)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

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

        process_metrics = self._get_current_process_metrics()

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
            "process": process_metrics,
            "application": {
                "total_requests": self.request_count,
                "total_errors": self.error_count,
                "error_rate_percent": error_rate,
                "avg_response_time_ms": avg_response_time * 1000,
                "requests_per_minute": self.request_count / (uptime / 60)
                if uptime > 0
                else 0,
                "last_request_at": self.last_request_at.isoformat()
                if self.last_request_at
                else None,
                "recent_requests": self.recent_requests[-10:],
            },
            "managed_processes": self._managed_processes_snapshot(),
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
                "last_checked": datetime.now().isoformat()
            }
        except Exception as e:
            dependencies["tradier"] = {
                "status": "down",
                "error": str(e),
                "last_checked": datetime.now().isoformat()
            }
        
        # Check Alpaca API
        try:
            start = time.time()
            resp = requests.get("https://paper-api.alpaca.markets/v2/account", timeout=5)
            dependencies["alpaca"] = {
                "status": "up" if resp.status_code < 500 else "down",
                "response_time_ms": (time.time() - start) * 1000,
                "last_checked": datetime.now().isoformat()
            }
        except Exception as e:
            dependencies["alpaca"] = {
                "status": "down",
                "error": str(e),
                "last_checked": datetime.now().isoformat()
            }

        return dependencies
    
    def record_request(
        self,
        response_time: float,
        is_error: bool = False,
        *,
        method: str = "",
        path: str = "",
        status_code: int = 0,
        error: Optional[str] = None,
    ) -> None:
        """Record request metrics."""

        self.request_count += 1
        if is_error:
            self.error_count += 1
        self.response_times.append(response_time)
        self.last_request_at = datetime.now()

        request_entry: Dict[str, object] = {
            "timestamp": self.last_request_at.isoformat(),
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": round(response_time * 1000, 2),
        }
        if error:
            request_entry["error"] = error

        self.recent_requests.append(request_entry)
        if len(self.recent_requests) > 50:
            self.recent_requests = self.recent_requests[-50:]

        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]

    def _managed_processes_snapshot(self) -> List[Dict[str, object]]:
        """Inspect PID files tracked by the process manager."""

        snapshots: List[Dict[str, object]] = []

        for directory in self._pid_directories:
            if not directory.exists():
                continue

            for pid_file in directory.glob("*.pid"):
                try:
                    pid = int(pid_file.read_text().strip())
                except ValueError:
                    snapshots.append(
                        {
                            "name": pid_file.stem,
                            "status": "invalid",
                            "pid": pid_file.read_text().strip(),
                            "source": str(pid_file),
                        }
                    )
                    continue

                process_info = {
                    "name": pid_file.stem,
                    "pid": pid,
                    "source": str(pid_file),
                }

                if psutil.pid_exists(pid):
                    proc = psutil.Process(pid)
                    process_info.update(
                        {
                            "status": "running",
                            "create_time": datetime.fromtimestamp(
                                proc.create_time()
                            ).isoformat(),
                            "cpu_percent": proc.cpu_percent(interval=0.0),
                            "memory_mb": proc.memory_info().rss / 1024 / 1024,
                        }
                    )
                else:
                    process_info["status"] = "stale"

                snapshots.append(process_info)

        return snapshots

    def _get_current_process_metrics(self) -> Dict[str, object]:
        """Capture metrics for the current FastAPI process."""

        process = psutil.Process(os.getpid())
        with process.oneshot():
            cpu = process.cpu_percent(interval=0.0)
            mem = process.memory_info().rss / 1024 / 1024
            num_threads = process.num_threads()
            open_files = [f.path for f in process.open_files()]

        return {
            "pid": process.pid,
            "cpu_percent": cpu,
            "memory_mb": mem,
            "num_threads": num_threads,
            "open_files": open_files,
        }


# Global instance
health_monitor = HealthMonitor()
