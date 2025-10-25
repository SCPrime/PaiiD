from backend.optimization.api_optimizer import APIOptimizer
from backend.optimization.cache_manager import CacheManager
from backend.optimization.database_optimizer import DatabaseOptimizer
from backend.optimization.performance_monitor import PerformanceMonitor
from backend.optimization.security_hardener import SecurityHardener
from datetime import datetime
from typing import Any
import logging

"""
Optimization Orchestrator
Coordinates all backend optimization processes for maximum performance
"""

logger = logging.getLogger(__name__)

class OptimizationOrchestrator:
    """Orchestrates all backend optimization processes"""

    def __init__(self):
        self.database_optimizer = DatabaseOptimizer()
        self.api_optimizer = APIOptimizer()
        self.cache_manager = CacheManager()
        self.performance_monitor = PerformanceMonitor()
        self.security_hardener = SecurityHardener()

        self.optimization_status = {
            "database": False,
            "api": False,
            "cache": False,
            "monitoring": False,
            "security": False,
        }

    async def run_full_optimization(self) -> dict[str, Any]:
        """Run comprehensive backend optimization"""
        try:
            logger.info("Starting comprehensive backend optimization...")

            optimization_results = {
                "timestamp": datetime.now().isoformat(),
                "status": "in_progress",
                "results": {},
                "errors": [],
            }

            # Phase 1: Database Optimization
            logger.info("Phase 1: Database Optimization")
            try:
                await self.database_optimizer.initialize_connection_pool()
                await self.database_optimizer.create_performance_indexes()
                await self.database_optimizer.optimize_database_settings()
                await self.database_optimizer.optimize_queries()
                await self.database_optimizer.setup_query_caching()
                await self.database_optimizer.cleanup_old_data()

                db_report = await self.database_optimizer.get_optimization_report()
                optimization_results["results"]["database"] = db_report
                self.optimization_status["database"] = True
                logger.info("Database optimization completed successfully")

            except Exception as e:
                error_msg = f"Database optimization failed: {e}"
                logger.error(error_msg)
                optimization_results["errors"].append(error_msg)

            # Phase 2: API Optimization
            logger.info("Phase 2: API Optimization")
            try:
                await self.api_optimizer.setup_response_caching()
                await self.api_optimizer.optimize_response_compression()
                await self.api_optimizer.setup_rate_limiting()
                await self.api_optimizer.optimize_database_queries()
                await self.api_optimizer.setup_response_headers()

                api_report = await self.api_optimizer.get_optimization_report()
                optimization_results["results"]["api"] = api_report
                self.optimization_status["api"] = True
                logger.info("API optimization completed successfully")

            except Exception as e:
                error_msg = f"API optimization failed: {e}"
                logger.error(error_msg)
                optimization_results["errors"].append(error_msg)

            # Phase 3: Cache Optimization
            logger.info("Phase 3: Cache Optimization")
            try:
                await self.cache_manager.setup_cache_strategies()
                await self.cache_manager.setup_distributed_caching()
                await self.cache_manager.setup_cache_warming()
                await self.cache_manager.optimize_cache_memory()

                cache_report = await self.cache_manager.get_optimization_report()
                optimization_results["results"]["cache"] = cache_report
                self.optimization_status["cache"] = True
                logger.info("Cache optimization completed successfully")

            except Exception as e:
                error_msg = f"Cache optimization failed: {e}"
                logger.error(error_msg)
                optimization_results["errors"].append(error_msg)

            # Phase 4: Performance Monitoring
            logger.info("Phase 4: Performance Monitoring Setup")
            try:
                await self.performance_monitor.setup_monitoring()

                monitoring_report = (
                    await self.performance_monitor.get_optimization_report()
                )
                optimization_results["results"]["monitoring"] = monitoring_report
                self.optimization_status["monitoring"] = True
                logger.info("Performance monitoring setup completed successfully")

            except Exception as e:
                error_msg = f"Performance monitoring setup failed: {e}"
                logger.error(error_msg)
                optimization_results["errors"].append(error_msg)

            # Phase 5: Security Hardening
            logger.info("Phase 5: Security Hardening")
            try:
                await self.security_hardener.setup_security_policies()
                await self.security_hardener.setup_session_security()

                security_report = await self.security_hardener.get_optimization_report()
                optimization_results["results"]["security"] = security_report
                self.optimization_status["security"] = True
                logger.info("Security hardening completed successfully")

            except Exception as e:
                error_msg = f"Security hardening failed: {e}"
                logger.error(error_msg)
                optimization_results["errors"].append(error_msg)

            # Generate final optimization report
            optimization_results["status"] = "completed"
            optimization_results["success_rate"] = self._calculate_success_rate()
            optimization_results["overall_status"] = self._get_overall_status()

            logger.info(
                f"Backend optimization completed with {optimization_results['success_rate']}% success rate"
            )

            return optimization_results

        except Exception as e:
            logger.error(f"Full optimization failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _calculate_success_rate(self) -> float:
        """Calculate optimization success rate"""
        total_phases = len(self.optimization_status)
        successful_phases = sum(
            1 for status in self.optimization_status.values() if status
        )
        return round((successful_phases / total_phases) * 100, 2)

    def _get_overall_status(self) -> str:
        """Get overall optimization status"""
        success_rate = self._calculate_success_rate()

        if success_rate >= 90:
            return "excellent"
        elif success_rate >= 75:
            return "good"
        elif success_rate >= 50:
            return "partial"
        else:
            return "poor"

    async def run_quick_optimization(self) -> dict[str, Any]:
        """Run quick optimization for critical performance issues"""
        try:
            logger.info("Starting quick backend optimization...")

            quick_results = {
                "timestamp": datetime.now().isoformat(),
                "status": "in_progress",
                "optimizations": [],
            }

            # Quick database optimizations
            try:
                await self.database_optimizer.cleanup_old_data()
                quick_results["optimizations"].append("Database cleanup completed")
            except Exception as e:
                logger.error(f"Quick database optimization failed: {e}")

            # Quick cache optimizations
            try:
                await self.cache_manager.cleanup_expired_cache()
                quick_results["optimizations"].append("Cache cleanup completed")
            except Exception as e:
                logger.error(f"Quick cache optimization failed: {e}")

            # Quick performance monitoring
            try:
                performance_data = (
                    await self.performance_monitor.collect_system_metrics()
                )
                quick_results["optimizations"].append("Performance metrics collected")
            except Exception as e:
                logger.error(f"Quick performance monitoring failed: {e}")

            quick_results["status"] = "completed"
            logger.info("Quick optimization completed successfully")

            return quick_results

        except Exception as e:
            logger.error(f"Quick optimization failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def run_specific_optimization(self, optimization_type: str) -> dict[str, Any]:
        """Run specific optimization type"""
        try:
            logger.info(f"Running {optimization_type} optimization...")

            if optimization_type == "database":
                return await self._optimize_database()
            elif optimization_type == "api":
                return await self._optimize_api()
            elif optimization_type == "cache":
                return await self._optimize_cache()
            elif optimization_type == "monitoring":
                return await self._optimize_monitoring()
            elif optimization_type == "security":
                return await self._optimize_security()
            else:
                return {
                    "status": "failed",
                    "error": f"Unknown optimization type: {optimization_type}",
                }

        except Exception as e:
            logger.error(f"{optimization_type} optimization failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def _optimize_database(self) -> dict[str, Any]:
        """Optimize database specifically"""
        try:
            await self.database_optimizer.initialize_connection_pool()
            await self.database_optimizer.create_performance_indexes()
            await self.database_optimizer.optimize_database_settings()
            await self.database_optimizer.optimize_queries()

            report = await self.database_optimizer.get_optimization_report()
            return {
                "status": "completed",
                "type": "database",
                "report": report,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def _optimize_api(self) -> dict[str, Any]:
        """Optimize API specifically"""
        try:
            await self.api_optimizer.setup_response_caching()
            await self.api_optimizer.optimize_response_compression()
            await self.api_optimizer.setup_rate_limiting()
            await self.api_optimizer.optimize_database_queries()

            report = await self.api_optimizer.get_optimization_report()
            return {
                "status": "completed",
                "type": "api",
                "report": report,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def _optimize_cache(self) -> dict[str, Any]:
        """Optimize cache specifically"""
        try:
            await self.cache_manager.setup_cache_strategies()
            await self.cache_manager.setup_distributed_caching()
            await self.cache_manager.optimize_cache_memory()

            report = await self.cache_manager.get_optimization_report()
            return {
                "status": "completed",
                "type": "cache",
                "report": report,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def _optimize_monitoring(self) -> dict[str, Any]:
        """Optimize monitoring specifically"""
        try:
            await self.performance_monitor.setup_monitoring()

            report = await self.performance_monitor.get_optimization_report()
            return {
                "status": "completed",
                "type": "monitoring",
                "report": report,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def _optimize_security(self) -> dict[str, Any]:
        """Optimize security specifically"""
        try:
            await self.security_hardener.setup_security_policies()
            await self.security_hardener.setup_session_security()

            report = await self.security_hardener.get_optimization_report()
            return {
                "status": "completed",
                "type": "security",
                "report": report,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def get_optimization_status(self) -> dict[str, Any]:
        """Get current optimization status"""
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "optimization_status": self.optimization_status.copy(),
                "success_rate": self._calculate_success_rate(),
                "overall_status": self._get_overall_status(),
                "next_recommended_optimization": self._get_next_recommendation(),
            }
        except Exception as e:
            logger.error(f"Failed to get optimization status: {e}")
            return {"error": str(e)}

    def _get_next_recommendation(self) -> str:
        """Get next recommended optimization"""
        if not self.optimization_status["database"]:
            return "database"
        elif not self.optimization_status["api"]:
            return "api"
        elif not self.optimization_status["cache"]:
            return "cache"
        elif not self.optimization_status["monitoring"]:
            return "monitoring"
        elif not self.optimization_status["security"]:
            return "security"
        else:
            return "maintenance"

    async def cleanup_optimization_resources(self):
        """Cleanup optimization resources"""
        try:
            # Close database connections
            await self.database_optimizer.close_connections()

            logger.info("Optimization resources cleaned up successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to cleanup optimization resources: {e}")
            return False
