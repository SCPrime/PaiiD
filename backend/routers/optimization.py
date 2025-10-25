from backend.optimization.optimization_orchestrator import OptimizationOrchestrator
from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from fastapi.responses import JSONResponse
import logging

"""
Optimization Router
API endpoints for backend optimization and performance monitoring
"""

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/optimization", tags=["optimization"])

# Global orchestrator instance
orchestrator = OptimizationOrchestrator()

@router.post("/run-full")
async def run_full_optimization(background_tasks: BackgroundTasks):
    """
    Run comprehensive backend optimization
    """
    try:
        logger.info("Starting full backend optimization...")

        # Run optimization in background
        result = await orchestrator.run_full_optimization()

        return JSONResponse(
            status_code=200,
            content={
                "message": "Backend optimization completed",
                "result": result,
            },
        )

    except Exception as e:
        logger.error(f"Full optimization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/run-quick")
async def run_quick_optimization():
    """
    Run quick optimization for critical performance issues
    """
    try:
        logger.info("Starting quick backend optimization...")

        result = await orchestrator.run_quick_optimization()

        return JSONResponse(
            status_code=200,
            content={
                "message": "Quick optimization completed",
                "result": result,
            },
        )

    except Exception as e:
        logger.error(f"Quick optimization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/run-specific")
async def run_specific_optimization(
    optimization_type: str = Query(..., description="Type of optimization to run"),
):
    """
    Run specific optimization type
    """
    try:
        valid_types = ["database", "api", "cache", "monitoring", "security"]
        if optimization_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid optimization type. Must be one of: {valid_types}",
            )

        logger.info(f"Starting {optimization_type} optimization...")

        result = await orchestrator.run_specific_optimization(optimization_type)

        return JSONResponse(
            status_code=200,
            content={
                "message": f"{optimization_type.title()} optimization completed",
                "result": result,
            },
        )

    except Exception as e:
        logger.error(f"{optimization_type} optimization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_optimization_status():
    """
    Get current optimization status
    """
    try:
        status = await orchestrator.get_optimization_status()

        return JSONResponse(status_code=200, content=status)

    except Exception as e:
        logger.error(f"Failed to get optimization status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/database/performance")
async def get_database_performance():
    """
    Get database performance metrics
    """
    try:
        db_stats = await orchestrator.database_optimizer.get_database_stats()
        slow_queries = await orchestrator.database_optimizer.analyze_slow_queries()

        return JSONResponse(
            status_code=200,
            content={
                "database_stats": db_stats,
                "slow_queries": slow_queries,
            },
        )

    except Exception as e:
        logger.error(f"Failed to get database performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/performance")
async def get_api_performance():
    """
    Get API performance metrics
    """
    try:
        api_metrics = await orchestrator.api_optimizer.monitor_api_performance()

        return JSONResponse(status_code=200, content=api_metrics)

    except Exception as e:
        logger.error(f"Failed to get API performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cache/stats")
async def get_cache_stats():
    """
    Get cache performance statistics
    """
    try:
        cache_stats = await orchestrator.cache_manager.get_cache_stats()

        return JSONResponse(status_code=200, content=cache_stats)

    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monitoring/report")
async def get_performance_report():
    """
    Get comprehensive performance report
    """
    try:
        performance_report = (
            await orchestrator.performance_monitor.generate_performance_report()
        )

        return JSONResponse(status_code=200, content=performance_report)

    except Exception as e:
        logger.error(f"Failed to get performance report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/security/report")
async def get_security_report():
    """
    Get security hardening report
    """
    try:
        security_report = await orchestrator.security_hardener.get_security_report()

        return JSONResponse(status_code=200, content=security_report)

    except Exception as e:
        logger.error(f"Failed to get security report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cache/warm")
async def warm_cache(strategy: str = Query(..., description="Cache warming strategy")):
    """
    Warm cache for specific strategy
    """
    try:
        result = await orchestrator.cache_manager.warm_cache(strategy)

        return JSONResponse(
            status_code=200,
            content={
                "message": f"Cache warming completed for strategy: {strategy}",
                "result": result,
            },
        )

    except Exception as e:
        logger.error(f"Cache warming failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cache/invalidate")
async def invalidate_cache(
    pattern: str = Query(..., description="Cache invalidation pattern"),
):
    """
    Invalidate cache entries matching pattern
    """
    try:
        invalidated_count = await orchestrator.cache_manager.invalidate_by_pattern(
            pattern
        )

        return JSONResponse(
            status_code=200,
            content={
                "message": "Cache invalidation completed",
                "invalidated_count": invalidated_count,
                "pattern": pattern,
            },
        )

    except Exception as e:
        logger.error(f"Cache invalidation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/database/cleanup")
async def cleanup_database():
    """
    Cleanup old database data
    """
    try:
        result = await orchestrator.database_optimizer.cleanup_old_data()

        return JSONResponse(
            status_code=200,
            content={
                "message": "Database cleanup completed",
                "success": result,
            },
        )

    except Exception as e:
        logger.error(f"Database cleanup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/security/scan")
async def scan_security_vulnerabilities():
    """
    Scan for security vulnerabilities
    """
    try:
        scan_result = await orchestrator.security_hardener.scan_for_vulnerabilities()

        return JSONResponse(
            status_code=200,
            content={
                "message": "Security vulnerability scan completed",
                "result": scan_result,
            },
        )

    except Exception as e:
        logger.error(f"Security scan failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def optimization_health_check():
    """
    Health check for optimization services
    """
    try:
        health_status = {
            "database_optimizer": orchestrator.database_optimizer is not None,
            "api_optimizer": orchestrator.api_optimizer is not None,
            "cache_manager": orchestrator.cache_manager is not None,
            "performance_monitor": orchestrator.performance_monitor is not None,
            "security_hardener": orchestrator.security_hardener is not None,
            "overall_status": "healthy",
        }

        return JSONResponse(status_code=200, content=health_status)

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=500, content={"overall_status": "unhealthy", "error": str(e)}
        )
