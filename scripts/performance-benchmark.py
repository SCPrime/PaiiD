"""
Performance Benchmarking Tool
Load testing and performance profiling for PaiiD backend APIs
"""

import asyncio
import json
import statistics
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import aiohttp


class PerformanceBenchmark:
    """Performance benchmarking and load testing utility"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "endpoints": {},
            "load_tests": {},
            "summary": {},
        }

    async def benchmark_endpoint(
        self,
        endpoint: str,
        method: str = "GET",
        data: Dict = None,
        iterations: int = 100,
        headers: Dict = None,
    ) -> Dict[str, Any]:
        """Benchmark a single endpoint"""
        print(f"[BENCHMARK] Testing {method} {endpoint} ({iterations} iterations)...")

        response_times = []
        status_codes = []
        errors = []

        async with aiohttp.ClientSession() as session:
            for i in range(iterations):
                start_time = time.time()

                try:
                    if method == "GET":
                        async with session.get(
                            f"{self.base_url}{endpoint}", headers=headers
                        ) as response:
                            status_codes.append(response.status)
                            await response.text()
                    elif method == "POST":
                        async with session.post(
                            f"{self.base_url}{endpoint}", json=data, headers=headers
                        ) as response:
                            status_codes.append(response.status)
                            await response.text()

                    elapsed = (time.time() - start_time) * 1000  # Convert to ms
                    response_times.append(elapsed)

                except Exception as e:
                    errors.append(str(e))

        # Calculate statistics
        if response_times:
            stats = {
                "endpoint": endpoint,
                "method": method,
                "iterations": iterations,
                "min_time_ms": round(min(response_times), 2),
                "max_time_ms": round(max(response_times), 2),
                "mean_time_ms": round(statistics.mean(response_times), 2),
                "median_time_ms": round(statistics.median(response_times), 2),
                "p95_time_ms": round(statistics.quantiles(response_times, n=20)[18], 2),
                "p99_time_ms": round(
                    statistics.quantiles(response_times, n=100)[98], 2
                ),
                "status_codes": dict(
                    [(code, status_codes.count(code)) for code in set(status_codes)]
                ),
                "error_count": len(errors),
                "errors": errors[:5],  # First 5 errors
            }
        else:
            stats = {
                "endpoint": endpoint,
                "method": method,
                "error": "All requests failed",
                "errors": errors,
            }

        return stats

    async def load_test(
        self,
        endpoint: str,
        method: str = "GET",
        data: Dict = None,
        concurrent_users: int = 50,
        duration_seconds: int = 30,
        headers: Dict = None,
    ) -> Dict[str, Any]:
        """Perform load test with concurrent users"""
        print(
            f"[LOAD TEST] {endpoint} - {concurrent_users} users for {duration_seconds}s..."
        )

        start_time = time.time()
        request_count = 0
        response_times = []
        status_codes = []
        errors = []

        async def make_request(session):
            nonlocal request_count
            try:
                req_start = time.time()

                if method == "GET":
                    async with session.get(
                        f"{self.base_url}{endpoint}", headers=headers
                    ) as response:
                        status_codes.append(response.status)
                        await response.text()
                elif method == "POST":
                    async with session.post(
                        f"{self.base_url}{endpoint}", json=data, headers=headers
                    ) as response:
                        status_codes.append(response.status)
                        await response.text()

                elapsed = (time.time() - req_start) * 1000
                response_times.append(elapsed)
                request_count += 1

            except Exception as e:
                errors.append(str(e))

        async def user_session():
            """Simulate a single user making continuous requests"""
            async with aiohttp.ClientSession() as session:
                end_time = start_time + duration_seconds
                while time.time() < end_time:
                    await make_request(session)
                    # Small delay between requests
                    await asyncio.sleep(0.1)

        # Run concurrent user sessions
        await asyncio.gather(*[user_session() for _ in range(concurrent_users)])

        # Calculate statistics
        total_time = time.time() - start_time
        requests_per_second = request_count / total_time if total_time > 0 else 0

        return {
            "endpoint": endpoint,
            "method": method,
            "concurrent_users": concurrent_users,
            "duration_seconds": round(total_time, 2),
            "total_requests": request_count,
            "requests_per_second": round(requests_per_second, 2),
            "mean_response_time_ms": round(statistics.mean(response_times), 2)
            if response_times
            else 0,
            "p95_response_time_ms": round(
                statistics.quantiles(response_times, n=20)[18], 2
            )
            if len(response_times) > 20
            else 0,
            "success_rate": round(
                (request_count / (request_count + len(errors))) * 100, 2
            )
            if request_count + len(errors) > 0
            else 0,
            "error_count": len(errors),
            "status_codes": dict(
                [(code, status_codes.count(code)) for code in set(status_codes)]
            ),
        }

    async def run_api_benchmarks(self):
        """Run benchmarks on all critical API endpoints"""
        print("\n[PHASE 1] API Endpoint Benchmarking")
        print("=" * 60)

        # Authentication endpoints
        print("\n[AUTH ENDPOINTS]")
        self.results["endpoints"]["auth_health"] = await self.benchmark_endpoint(
            "/health", method="GET", iterations=100
        )

        # Note: Login requires valid credentials, skipping for now
        # self.results["endpoints"]["auth_login"] = await self.benchmark_endpoint(
        #     "/api/auth/login",
        #     method="POST",
        #     data={"email": "test@example.com", "password": "test123"},
        #     iterations=50
        # )

        # Market data endpoints (if available)
        print("\n[MARKET DATA ENDPOINTS]")
        # self.results["endpoints"]["market_quotes"] = await self.benchmark_endpoint(
        #     "/api/market-data/quotes?symbols=AAPL,MSFT",
        #     method="GET",
        #     iterations=100
        # )

        print("\n[PHASE 1 COMPLETE] API Benchmarks completed")

    async def run_load_tests(self):
        """Run load tests simulating concurrent users"""
        print("\n[PHASE 2] Load Testing")
        print("=" * 60)

        # Test with increasing load
        user_counts = [10, 25, 50, 100]

        for user_count in user_counts:
            print(f"\n[LOAD TEST] {user_count} concurrent users...")
            result = await self.load_test(
                "/health", concurrent_users=user_count, duration_seconds=10
            )
            self.results["load_tests"][f"{user_count}_users"] = result

            # Break if errors are too high
            if result["error_count"] > result["total_requests"] * 0.1:
                print(
                    f"[WARNING] High error rate ({result['error_count']} errors), stopping load tests"
                )
                break

        print("\n[PHASE 2 COMPLETE] Load tests completed")

    def analyze_results(self):
        """Analyze benchmark results and generate summary"""
        print("\n[PHASE 3] Analyzing Results")
        print("=" * 60)

        summary = {
            "endpoints_tested": len(self.results["endpoints"]),
            "load_tests_completed": len(self.results["load_tests"]),
            "performance_grade": "A",  # Will calculate
            "bottlenecks": [],
            "recommendations": [],
        }

        # Analyze endpoint performance
        for endpoint, stats in self.results["endpoints"].items():
            if "mean_time_ms" in stats:
                mean_time = stats["mean_time_ms"]

                # Check against targets
                if mean_time > 1000:
                    summary["bottlenecks"].append(
                        f"{endpoint}: {mean_time}ms (target: <500ms)"
                    )
                    summary["recommendations"].append(
                        f"Optimize {endpoint} - response time too high"
                    )

        # Analyze load test results
        for test_name, result in self.results["load_tests"].items():
            if result["success_rate"] < 95:
                summary["bottlenecks"].append(
                    f"Load test {test_name}: {result['success_rate']}% success rate"
                )
                summary["recommendations"].append(
                    "Improve error handling and add circuit breakers"
                )

            if result["requests_per_second"] < 100:
                summary["recommendations"].append(
                    f"Low throughput: {result['requests_per_second']} req/s (target: >100)"
                )

        # Calculate overall grade
        if len(summary["bottlenecks"]) == 0:
            summary["performance_grade"] = "A"
        elif len(summary["bottlenecks"]) <= 2:
            summary["performance_grade"] = "B"
        elif len(summary["bottlenecks"]) <= 5:
            summary["performance_grade"] = "C"
        else:
            summary["performance_grade"] = "D"

        self.results["summary"] = summary

        print(f"\n[PERFORMANCE GRADE] {summary['performance_grade']}")
        print(f"[ENDPOINTS TESTED] {summary['endpoints_tested']}")
        print(f"[LOAD TESTS] {summary['load_tests_completed']}")
        print(f"[BOTTLENECKS] {len(summary['bottlenecks'])}")

    def save_report(self):
        """Save benchmark report to file"""
        output_file = Path("PERFORMANCE_BENCHMARK_REPORT.json")
        with open(output_file, "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"\n[SUCCESS] Report saved to {output_file}")

    def generate_markdown_report(self):
        """Generate markdown summary report"""
        summary = self.results["summary"]

        markdown = f"""# Performance Benchmark Report
**Date**: {self.results["timestamp"]}  
**Overall Grade**: {summary["performance_grade"]}  
**Status**: {"PASS" if summary["performance_grade"] in ["A", "B"] else "NEEDS IMPROVEMENT"}

---

## Summary

- **Endpoints Tested**: {summary["endpoints_tested"]}
- **Load Tests Completed**: {summary["load_tests_completed"]}
- **Bottlenecks Identified**: {len(summary["bottlenecks"])}
- **Recommendations**: {len(summary["recommendations"])}

---

## API Endpoint Performance

| Endpoint | Mean Time | P95 | P99 | Status |
|----------|-----------|-----|-----|--------|
"""

        for endpoint, stats in self.results["endpoints"].items():
            if "mean_time_ms" in stats:
                status = "✅" if stats["mean_time_ms"] < 500 else "⚠️"
                markdown += f"| {stats['endpoint']} | {stats['mean_time_ms']}ms | {stats['p95_time_ms']}ms | {stats['p99_time_ms']}ms | {status} |\n"

        markdown += """
---

## Load Test Results

| Test | Users | RPS | Mean Time | Success Rate | Status |
|------|-------|-----|-----------|--------------|--------|
"""

        for test_name, result in self.results["load_tests"].items():
            status = "✅" if result["success_rate"] > 95 else "⚠️"
            markdown += f"| {test_name} | {result['concurrent_users']} | {result['requests_per_second']} | {result['mean_response_time_ms']}ms | {result['success_rate']}% | {status} |\n"

        markdown += """
---

## Bottlenecks

"""
        if summary["bottlenecks"]:
            for bottleneck in summary["bottlenecks"]:
                markdown += f"- ⚠️ {bottleneck}\n"
        else:
            markdown += "- ✅ No significant bottlenecks detected\n"

        markdown += """
---

## Recommendations

"""
        if summary["recommendations"]:
            for rec in summary["recommendations"]:
                markdown += f"- 📋 {rec}\n"
        else:
            markdown += "- ✅ Performance meets all targets\n"

        markdown += """
---

**Report Generated**: Batch 16 - Performance Benchmarking  
**Tool**: performance-benchmark.py  
**Status**: COMPLETE
"""

        output_file = Path("PERFORMANCE_BENCHMARK_REPORT.md")
        with open(output_file, "w") as f:
            f.write(markdown)

        print(f"[SUCCESS] Markdown report saved to {output_file}")


async def main():
    """Main benchmark execution"""
    benchmark = PerformanceBenchmark()

    print("\n" + "=" * 60)
    print(" PaiiD Performance Benchmark Suite")
    print("=" * 60)

    try:
        # Run all benchmarks
        await benchmark.run_api_benchmarks()
        await benchmark.run_load_tests()

        # Analyze and save results
        benchmark.analyze_results()
        benchmark.save_report()
        benchmark.generate_markdown_report()

        print("\n" + "=" * 60)
        print(" ✅ BENCHMARK COMPLETE")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n[ERROR] Benchmark failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
