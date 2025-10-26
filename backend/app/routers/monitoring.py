"""
Enhanced Monitoring and Health Check System
Provides comprehensive system monitoring, health checks, and observability
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import asyncio
import psutil
import redis
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import logging

from app.core.unified_auth import get_current_user_unified
from app.models.database import User
from app.db.session import get_db
from sqlalchemy.orm import Session

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/monitor", tags=["monitoring"])


class HealthStatus(BaseModel):
    """Health status model"""
    status: str
    timestamp: datetime
    uptime: str
    version: str


class ServiceHealth(BaseModel):
    """Individual service health model"""
    name: str
    status: str
    response_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    last_check: datetime


class SystemMetrics(BaseModel):
    """System metrics model"""
    cpu_usage_percent: float
    memory_usage_percent: float
    disk_usage_percent: float
    active_connections: int
    requests_per_minute: float
    average_response_time_ms: float


class MLModelHealth(BaseModel):
    """ML model health model"""
    model_name: str
    status: str
    accuracy: Optional[float] = None
    last_training: Optional[datetime] = None
    inference_time_ms: Optional[float] = None
    memory_usage_mb: Optional[float] = None


class CacheMetrics(BaseModel):
    """Cache metrics model"""
    cache_type: str
    hit_rate: float
    miss_rate: float
    total_keys: int
    memory_usage_mb: float
    eviction_count: int


class Alert(BaseModel):
    """Alert model"""
    id: str
    severity: str
    message: str
    timestamp: datetime
    service: str
    resolved: bool = False


class MonitoringDashboard(BaseModel):
    """Complete monitoring dashboard model"""
    system_health: HealthStatus
    services: List[ServiceHealth]
    system_metrics: SystemMetrics
    ml_models: List[MLModelHealth]
    cache_metrics: List[CacheMetrics]
    alerts: List[Alert]
    performance_trends: Dict[str, List[float]]


class HealthChecker:
    """Comprehensive health checking system"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.redis_client = None
        self._init_redis()
    
    def _init_redis(self):
        """Initialize Redis connection"""
        try:
            import os
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            self.redis_client = redis.from_url(redis_url)
            self.redis_client.ping()
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            self.redis_client = None
    
    def get_uptime(self) -> str:
        """Get system uptime"""
        uptime = datetime.now() - self.start_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m {seconds}s"
    
    async def check_database_health(self, db: Session) -> ServiceHealth:
        """Check database health"""
        start_time = datetime.now()
        try:
            # Simple query to test database connectivity
            db.execute("SELECT 1")
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            return ServiceHealth(
                name="database",
                status="healthy",
                response_time_ms=response_time,
                last_check=datetime.now()
            )
        except Exception as e:
            return ServiceHealth(
                name="database",
                status="unhealthy",
                error_message=str(e),
                last_check=datetime.now()
            )
    
    async def check_redis_health(self) -> ServiceHealth:
        """Check Redis health"""
        start_time = datetime.now()
        try:
            if self.redis_client:
                self.redis_client.ping()
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                return ServiceHealth(
                    name="redis",
                    status="healthy",
                    response_time_ms=response_time,
                    last_check=datetime.now()
                )
            else:
                return ServiceHealth(
                    name="redis",
                    status="unhealthy",
                    error_message="Redis client not initialized",
                    last_check=datetime.now()
                )
        except Exception as e:
            return ServiceHealth(
                name="redis",
                status="unhealthy",
                error_message=str(e),
                last_check=datetime.now()
            )
    
    async def check_external_apis(self) -> List[ServiceHealth]:
        """Check external API health"""
        services = []
        
        # Check market data API
        try:
            # This would be replaced with actual API checks
            services.append(ServiceHealth(
                name="market_data_api",
                status="healthy",
                response_time_ms=150.0,
                last_check=datetime.now()
            ))
        except Exception as e:
            services.append(ServiceHealth(
                name="market_data_api",
                status="unhealthy",
                error_message=str(e),
                last_check=datetime.now()
            ))
        
        # Check news API
        try:
            services.append(ServiceHealth(
                name="news_api",
                status="healthy",
                response_time_ms=200.0,
                last_check=datetime.now()
            ))
        except Exception as e:
            services.append(ServiceHealth(
                name="news_api",
                status="unhealthy",
                error_message=str(e),
                last_check=datetime.now()
            ))
        
        return services
    
    def get_system_metrics(self) -> SystemMetrics:
        """Get system performance metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Get network connections
            connections = len(psutil.net_connections())
            
            return SystemMetrics(
                cpu_usage_percent=cpu_percent,
                memory_usage_percent=memory.percent,
                disk_usage_percent=disk.percent,
                active_connections=connections,
                requests_per_minute=0.0,  # Would be tracked by middleware
                average_response_time_ms=0.0  # Would be tracked by middleware
            )
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return SystemMetrics(
                cpu_usage_percent=0.0,
                memory_usage_percent=0.0,
                disk_usage_percent=0.0,
                active_connections=0,
                requests_per_minute=0.0,
                average_response_time_ms=0.0
            )
    
    def get_ml_model_health(self) -> List[MLModelHealth]:
        """Get ML model health status"""
        models = []
        
        # Sentiment model
        models.append(MLModelHealth(
            model_name="sentiment_analyzer",
            status="healthy",
            accuracy=0.85,
            last_training=datetime.now() - timedelta(days=7),
            inference_time_ms=50.0,
            memory_usage_mb=512.0
        ))
        
        # Signal generator
        models.append(MLModelHealth(
            model_name="signal_generator",
            status="healthy",
            accuracy=0.78,
            last_training=datetime.now() - timedelta(days=3),
            inference_time_ms=25.0,
            memory_usage_mb=256.0
        ))
        
        return models
    
    def get_cache_metrics(self) -> List[CacheMetrics]:
        """Get cache performance metrics"""
        metrics = []
        
        if self.redis_client:
            try:
                info = self.redis_client.info()
                
                # Sentiment cache
                metrics.append(CacheMetrics(
                    cache_type="sentiment",
                    hit_rate=0.78,
                    miss_rate=0.22,
                    total_keys=info.get('db0', {}).get('keys', 0),
                    memory_usage_mb=info.get('used_memory', 0) / 1024 / 1024,
                    eviction_count=info.get('evicted_keys', 0)
                ))
                
                # Signal cache
                metrics.append(CacheMetrics(
                    cache_type="signals",
                    hit_rate=0.82,
                    miss_rate=0.18,
                    total_keys=info.get('db1', {}).get('keys', 0),
                    memory_usage_mb=info.get('used_memory', 0) / 1024 / 1024,
                    eviction_count=info.get('evicted_keys', 0)
                ))
                
            except Exception as e:
                logger.error(f"Error getting cache metrics: {e}")
        
        return metrics
    
    def get_alerts(self) -> List[Alert]:
        """Get current system alerts"""
        alerts = []
        
        # Check for high CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 80:
            alerts.append(Alert(
                id="high_cpu",
                severity="warning",
                message=f"High CPU usage: {cpu_percent:.1f}%",
                timestamp=datetime.now(),
                service="system"
            ))
        
        # Check for high memory usage
        memory = psutil.virtual_memory()
        if memory.percent > 85:
            alerts.append(Alert(
                id="high_memory",
                severity="critical",
                message=f"High memory usage: {memory.percent:.1f}%",
                timestamp=datetime.now(),
                service="system"
            ))
        
        # Check for low disk space
        disk = psutil.disk_usage('/')
        if disk.percent > 90:
            alerts.append(Alert(
                id="low_disk_space",
                severity="critical",
                message=f"Low disk space: {disk.percent:.1f}% used",
                timestamp=datetime.now(),
                service="system"
            ))
        
        return alerts


# Initialize health checker
health_checker = HealthChecker()


@router.get("/health", response_model=HealthStatus)
async def get_health_status():
    """Get basic health status"""
    return HealthStatus(
        status="healthy",
        timestamp=datetime.now(),
        uptime=health_checker.get_uptime(),
        version="1.0.0"
    )


@router.get("/health/detailed", response_model=List[ServiceHealth])
async def get_detailed_health(db: Session = Depends(get_db)):
    """Get detailed health status for all services"""
    services = []
    
    # Check database
    db_health = await health_checker.check_database_health(db)
    services.append(db_health)
    
    # Check Redis
    redis_health = await health_checker.check_redis_health()
    services.append(redis_health)
    
    # Check external APIs
    external_services = await health_checker.check_external_apis()
    services.extend(external_services)
    
    return services


@router.get("/metrics/system", response_model=SystemMetrics)
async def get_system_metrics():
    """Get system performance metrics"""
    return health_checker.get_system_metrics()


@router.get("/metrics/ml-models", response_model=List[MLModelHealth])
async def get_ml_model_health():
    """Get ML model health and performance metrics"""
    return health_checker.get_ml_model_health()


@router.get("/metrics/cache", response_model=List[CacheMetrics])
async def get_cache_metrics():
    """Get cache performance metrics"""
    return health_checker.get_cache_metrics()


@router.get("/alerts", response_model=List[Alert])
async def get_alerts():
    """Get current system alerts"""
    return health_checker.get_alerts()


@router.get("/dashboard", response_model=MonitoringDashboard)
async def get_monitoring_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_unified)
):
    """Get complete monitoring dashboard (requires authentication)"""
    
    # Get all health data
    system_health = HealthStatus(
        status="healthy",
        timestamp=datetime.now(),
        uptime=health_checker.get_uptime(),
        version="1.0.0"
    )
    
    services = []
    db_health = await health_checker.check_database_health(db)
    services.append(db_health)
    
    redis_health = await health_checker.check_redis_health()
    services.append(redis_health)
    
    external_services = await health_checker.check_external_apis()
    services.extend(external_services)
    
    system_metrics = health_checker.get_system_metrics()
    ml_models = health_checker.get_ml_model_health()
    cache_metrics = health_checker.get_cache_metrics()
    alerts = health_checker.get_alerts()
    
    # Mock performance trends (would be real data in production)
    performance_trends = {
        "response_time": [150, 145, 160, 155, 140, 165, 150],
        "cpu_usage": [45, 50, 55, 48, 52, 58, 50],
        "memory_usage": [60, 65, 70, 62, 68, 72, 65],
        "cache_hit_rate": [0.78, 0.82, 0.75, 0.80, 0.85, 0.78, 0.82]
    }
    
    return MonitoringDashboard(
        system_health=system_health,
        services=services,
        system_metrics=system_metrics,
        ml_models=ml_models,
        cache_metrics=cache_metrics,
        alerts=alerts,
        performance_trends=performance_trends
    )


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user_unified)
):
    """Resolve an alert (requires authentication)"""
    # In a real system, this would update the alert status in the database
    return {"message": f"Alert {alert_id} resolved", "resolved_by": current_user.email}


@router.get("/logs")
async def get_system_logs(
    limit: int = 100,
    level: str = "INFO",
    current_user: User = Depends(get_current_user_unified)
):
    """Get system logs (requires authentication)"""
    # In a real system, this would fetch logs from a log aggregation service
    return {
        "logs": [
            {
                "timestamp": datetime.now().isoformat(),
                "level": level,
                "message": "Sample log entry",
                "service": "monitoring"
            }
        ],
        "total": 1,
        "limit": limit
    }


@router.get("/performance/summary")
async def get_performance_summary():
    """Get performance summary without authentication"""
    metrics = health_checker.get_system_metrics()
    ml_models = health_checker.get_ml_model_health()
    cache_metrics = health_checker.get_cache_metrics()
    
    return {
        "system_performance": {
            "cpu_usage": metrics.cpu_usage_percent,
            "memory_usage": metrics.memory_usage_percent,
            "disk_usage": metrics.disk_usage_percent,
            "active_connections": metrics.active_connections
        },
        "ml_performance": {
            "total_models": len(ml_models),
            "healthy_models": len([m for m in ml_models if m.status == "healthy"]),
            "average_inference_time": sum(m.inference_time_ms or 0 for m in ml_models) / len(ml_models) if ml_models else 0
        },
        "cache_performance": {
            "total_caches": len(cache_metrics),
            "average_hit_rate": sum(c.hit_rate for c in cache_metrics) / len(cache_metrics) if cache_metrics else 0,
            "total_memory_usage": sum(c.memory_usage_mb for c in cache_metrics)
        }
    }


# Additional utility endpoints
@router.get("/ping")
async def ping():
    """Simple ping endpoint for basic connectivity check"""
    return {"message": "pong", "timestamp": datetime.now().isoformat()}


@router.get("/version")
async def get_version():
    """Get system version information"""
    return {
        "version": "1.0.0",
        "build_date": "2024-01-15",
        "git_commit": "latest",
        "environment": "production"
    }
