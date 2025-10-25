from datetime import datetime, timedelta
from typing import Any
import json
import logging
import psutil
import redis

"""
Performance Monitor
Comprehensive monitoring and analytics for system performance optimization
"""

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Comprehensive performance monitoring and analytics"""

    def __init__(self):
        self.redis_client = redis.Redis(
            host="localhost", port=6379, db=8, decode_responses=True
        )
        self.metrics = {
            "api_requests": 0,
            "api_response_times": [],
            "database_queries": 0,
            "database_query_times": [],
            "cache_hits": 0,
            "cache_misses": 0,
            "memory_usage": [],
            "cpu_usage": [],
            "disk_io": [],
            "network_io": [],
        }
        self.alerts = []
        self.thresholds = {
            "api_response_time_ms": 1000,
            "database_query_time_ms": 500,
            "memory_usage_percent": 80,
            "cpu_usage_percent": 80,
            "cache_hit_rate_percent": 70,
        }

    async def setup_monitoring(self):
        """Setup comprehensive performance monitoring"""
        try:
            # Configure monitoring intervals
            monitoring_config = {
                "system_metrics_interval": 30,  # seconds
                "api_metrics_interval": 10,  # seconds
                "database_metrics_interval": 60,  # seconds
                "alert_check_interval": 30,  # seconds
                "report_generation_interval": 300,  # 5 minutes
            }

            self.redis_client.setex(
                "monitoring_config", 3600, json.dumps(monitoring_config)
            )

            # Setup alert thresholds
            self.redis_client.setex(
                "alert_thresholds", 3600, json.dumps(self.thresholds)
            )

            logger.info("Performance monitoring configured successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to setup monitoring: {e}")
            return False

    async def collect_system_metrics(self) -> dict[str, Any]:
        """Collect comprehensive system performance metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()

            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()

            # Disk metrics
            disk = psutil.disk_usage("/")
            disk_io = psutil.disk_io_counters()

            # Network metrics
            network_io = psutil.net_io_counters()

            # Process metrics
            process = psutil.Process()
            process_memory = process.memory_info()
            process_cpu = process.cpu_percent()

            system_metrics = {
                "timestamp": datetime.now().isoformat(),
                "cpu": {
                    "percent": cpu_percent,
                    "count": cpu_count,
                    "frequency_mhz": cpu_freq.current if cpu_freq else None,
                },
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "used_gb": round(memory.used / (1024**3), 2),
                    "percent": memory.percent,
                    "swap_total_gb": round(swap.total / (1024**3), 2),
                    "swap_used_gb": round(swap.used / (1024**3), 2),
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "percent": round((disk.used / disk.total) * 100, 2),
                    "read_bytes": disk_io.read_bytes if disk_io else 0,
                    "write_bytes": disk_io.write_bytes if disk_io else 0,
                },
                "network": {
                    "bytes_sent": network_io.bytes_sent,
                    "bytes_recv": network_io.bytes_recv,
                    "packets_sent": network_io.packets_sent,
                    "packets_recv": network_io.packets_recv,
                },
                "process": {
                    "memory_mb": round(process_memory.rss / (1024**2), 2),
                    "cpu_percent": process_cpu,
                },
            }

            # Store metrics
            self.redis_client.setex(
                f"system_metrics:{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                3600,  # 1 hour
                json.dumps(system_metrics),
            )

            return system_metrics

        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return {}

    async def collect_api_metrics(self) -> dict[str, Any]:
        """Collect API performance metrics"""
        try:
            # Get API metrics from Redis
            api_metrics_data = self.redis_client.get("api_performance:latest")
            if api_metrics_data:
                api_metrics = json.loads(api_metrics_data)
            else:
                api_metrics = {
                    "total_requests": 0,
                    "average_response_time_ms": 0,
                    "cache_hit_ratio_percent": 0,
                    "error_rate_percent": 0,
                }

            # Calculate additional metrics
            current_time = datetime.now()
            hour_ago = current_time - timedelta(hours=1)

            # Get request count for last hour
            recent_requests = 0
            for i in range(60):  # Check last 60 minutes
                minute_key = f"api_performance:{(current_time - timedelta(minutes=i)).strftime('%Y%m%d_%H%M')}"
                minute_data = self.redis_client.get(minute_key)
                if minute_data:
                    minute_metrics = json.loads(minute_data)
                    recent_requests += minute_metrics.get("total_requests", 0)

            api_metrics.update(
                {
                    "requests_last_hour": recent_requests,
                    "timestamp": current_time.isoformat(),
                }
            )

            return api_metrics

        except Exception as e:
            logger.error(f"Failed to collect API metrics: {e}")
            return {}

    async def collect_database_metrics(self) -> dict[str, Any]:
        """Collect database performance metrics"""
        try:
            # Get database metrics from Redis
            db_metrics_data = self.redis_client.get("database_performance:latest")
            if db_metrics_data:
                db_metrics = json.loads(db_metrics_data)
            else:
                db_metrics = {
                    "active_connections": 0,
                    "cache_hit_ratio": 0,
                    "database_size": "0 MB",
                    "slow_queries_count": 0,
                }

            db_metrics.update(
                {
                    "timestamp": datetime.now().isoformat(),
                }
            )

            return db_metrics

        except Exception as e:
            logger.error(f"Failed to collect database metrics: {e}")
            return {}

    async def check_alerts(self) -> list[dict[str, Any]]:
        """Check for performance alerts and thresholds"""
        try:
            alerts = []
            current_time = datetime.now()

            # Get latest metrics
            system_metrics = await self.collect_system_metrics()
            api_metrics = await self.collect_api_metrics()
            db_metrics = await self.collect_database_metrics()

            # Check CPU usage
            if (
                system_metrics.get("cpu", {}).get("percent", 0)
                > self.thresholds["cpu_usage_percent"]
            ):
                alerts.append(
                    {
                        "type": "cpu_usage",
                        "severity": "warning",
                        "message": f"High CPU usage: {system_metrics['cpu']['percent']}%",
                        "timestamp": current_time.isoformat(),
                    }
                )

            # Check memory usage
            if (
                system_metrics.get("memory", {}).get("percent", 0)
                > self.thresholds["memory_usage_percent"]
            ):
                alerts.append(
                    {
                        "type": "memory_usage",
                        "severity": "warning",
                        "message": f"High memory usage: {system_metrics['memory']['percent']}%",
                        "timestamp": current_time.isoformat(),
                    }
                )

            # Check API response time
            if (
                api_metrics.get("average_response_time_ms", 0)
                > self.thresholds["api_response_time_ms"]
            ):
                alerts.append(
                    {
                        "type": "api_response_time",
                        "severity": "warning",
                        "message": f"Slow API response time: {api_metrics['average_response_time_ms']}ms",
                        "timestamp": current_time.isoformat(),
                    }
                )

            # Check cache hit ratio
            if (
                api_metrics.get("cache_hit_ratio_percent", 0)
                < self.thresholds["cache_hit_rate_percent"]
            ):
                alerts.append(
                    {
                        "type": "cache_hit_ratio",
                        "severity": "info",
                        "message": f"Low cache hit ratio: {api_metrics['cache_hit_ratio_percent']}%",
                        "timestamp": current_time.isoformat(),
                    }
                )

            # Store alerts
            if alerts:
                self.redis_client.setex(
                    f"alerts:{current_time.strftime('%Y%m%d_%H%M%S')}",
                    3600,
                    json.dumps(alerts),
                )
                self.alerts.extend(alerts)

            return alerts

        except Exception as e:
            logger.error(f"Failed to check alerts: {e}")
            return []

    async def generate_performance_report(self) -> dict[str, Any]:
        """Generate comprehensive performance report"""
        try:
            # Collect all metrics
            system_metrics = await self.collect_system_metrics()
            api_metrics = await self.collect_api_metrics()
            db_metrics = await self.collect_database_metrics()
            recent_alerts = await self.check_alerts()

            # Calculate performance scores
            performance_score = self._calculate_performance_score(
                system_metrics, api_metrics, db_metrics
            )

            # Generate recommendations
            recommendations = self._generate_recommendations(
                system_metrics, api_metrics, db_metrics, recent_alerts
            )

            report = {
                "timestamp": datetime.now().isoformat(),
                "performance_score": performance_score,
                "system_metrics": system_metrics,
                "api_metrics": api_metrics,
                "database_metrics": db_metrics,
                "recent_alerts": recent_alerts,
                "recommendations": recommendations,
                "overall_status": "healthy"
                if performance_score > 80
                else "needs_attention",
            }

            # Store report
            self.redis_client.setex(
                f"performance_report:{datetime.now().strftime('%Y%m%d_%H%M')}",
                3600,
                json.dumps(report),
            )

            return report

        except Exception as e:
            logger.error(f"Failed to generate performance report: {e}")
            return {"error": str(e)}

    def _calculate_performance_score(
        self, system_metrics: dict, api_metrics: dict, db_metrics: dict
    ) -> int:
        """Calculate overall performance score (0-100)"""
        try:
            score = 100

            # CPU usage penalty
            cpu_percent = system_metrics.get("cpu", {}).get("percent", 0)
            if cpu_percent > 80:
                score -= 20
            elif cpu_percent > 60:
                score -= 10

            # Memory usage penalty
            memory_percent = system_metrics.get("memory", {}).get("percent", 0)
            if memory_percent > 80:
                score -= 20
            elif memory_percent > 60:
                score -= 10

            # API response time penalty
            api_response_time = api_metrics.get("average_response_time_ms", 0)
            if api_response_time > 1000:
                score -= 20
            elif api_response_time > 500:
                score -= 10

            # Cache hit ratio bonus/penalty
            cache_hit_ratio = api_metrics.get("cache_hit_ratio_percent", 0)
            if cache_hit_ratio > 90:
                score += 5
            elif cache_hit_ratio < 50:
                score -= 15

            return max(0, min(100, score))

        except Exception as e:
            logger.error(f"Failed to calculate performance score: {e}")
            return 50

    def _generate_recommendations(
        self, system_metrics: dict, api_metrics: dict, db_metrics: dict, alerts: list
    ) -> list[str]:
        """Generate performance optimization recommendations"""
        recommendations = []

        try:
            # CPU recommendations
            cpu_percent = system_metrics.get("cpu", {}).get("percent", 0)
            if cpu_percent > 80:
                recommendations.append(
                    "Consider scaling up CPU resources or optimizing CPU-intensive operations"
                )
            elif cpu_percent > 60:
                recommendations.append(
                    "Monitor CPU usage and consider optimization for high-load periods"
                )

            # Memory recommendations
            memory_percent = system_metrics.get("memory", {}).get("percent", 0)
            if memory_percent > 80:
                recommendations.append(
                    "Increase memory allocation or optimize memory usage"
                )
            elif memory_percent > 60:
                recommendations.append(
                    "Monitor memory usage and consider memory optimization"
                )

            # API recommendations
            api_response_time = api_metrics.get("average_response_time_ms", 0)
            if api_response_time > 1000:
                recommendations.append(
                    "Optimize API endpoints and consider caching strategies"
                )
            elif api_response_time > 500:
                recommendations.append(
                    "Review API performance and implement response caching"
                )

            # Cache recommendations
            cache_hit_ratio = api_metrics.get("cache_hit_ratio_percent", 0)
            if cache_hit_ratio < 70:
                recommendations.append(
                    "Improve cache hit ratio by adjusting TTL values and cache strategies"
                )

            # Database recommendations
            if db_metrics.get("slow_queries_count", 0) > 5:
                recommendations.append(
                    "Optimize database queries and consider adding indexes"
                )

            # General recommendations
            if not recommendations:
                recommendations.append(
                    "System performance is optimal - continue monitoring"
                )

            return recommendations

        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return ["Monitor system performance and generate recommendations"]

    async def get_optimization_report(self) -> dict[str, Any]:
        """Generate comprehensive optimization report"""
        try:
            performance_report = await self.generate_performance_report()

            report = {
                "optimization_status": "completed",
                "performance_report": performance_report,
                "monitoring_configured": True,
                "alert_thresholds": self.thresholds,
                "recommendations": [
                    "Continue monitoring system performance",
                    "Set up automated alerting for critical thresholds",
                    "Regular performance reviews and optimization",
                    "Implement performance testing in CI/CD pipeline",
                    "Consider load testing for capacity planning",
                ],
                "timestamp": datetime.now().isoformat(),
            }

            return report

        except Exception as e:
            logger.error(f"Failed to generate optimization report: {e}")
            return {"error": str(e)}
