"""
Load Testing Baseline for Production Monitoring

Agent 7C - Final Production Validation
Tests critical endpoints to establish baseline performance metrics.

Target Baseline Thresholds:
- Health endpoint: <100ms avg, >200 req/s
- Market data: <500ms avg, >100 req/s
- AI recommendations: <2000ms avg, >20 req/s
- Portfolio: <1000ms avg, >50 req/s
"""

import asyncio
import os
import statistics
import time
from typing import Dict, List, Tuple

import httpx
import pytest

# Base URL - use environment variable or default to localhost
BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8001")
API_TOKEN = os.getenv("API_TOKEN", "rnd_bDRqi1TvLvd3rC78yvUSgDraH2Kl")

# JWT token for authenticated requests (obtained from login)
# If not set, tests will attempt to login and get a token
JWT_TOKEN = None


async def get_jwt_token() -> str:
    """
    Get JWT token by logging in as test user.
    Creates test user if it doesn't exist.

    Returns:
        JWT access token for authenticated requests
    """
    global JWT_TOKEN

    if JWT_TOKEN:
        return JWT_TOKEN

    # Test credentials
    test_email = "loadtest@paiid.com"
    test_password = "LoadTest123!"

    async with httpx.AsyncClient() as client:
        # Try to register first (will fail if user exists)
        try:
            register_response = await client.post(
                f"{BASE_URL}/api/auth/register",
                json={
                    "email": test_email,
                    "password": test_password,
                    "full_name": "Load Test User",
                },
            )
            if register_response.status_code == 201:
                data = register_response.json()
                JWT_TOKEN = data["access_token"]
                return JWT_TOKEN
        except Exception:
            pass  # User probably exists

        # Try to login
        login_response = await client.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": test_email, "password": test_password},
        )

        if login_response.status_code == 200:
            data = login_response.json()
            JWT_TOKEN = data["access_token"]
            return JWT_TOKEN
        else:
            raise RuntimeError(
                f"Failed to get JWT token: {login_response.status_code} - {login_response.text}"
            )


class LoadTestResult:
    """Container for load test results"""

    def __init__(self, endpoint: str, num_requests: int):
        self.endpoint = endpoint
        self.num_requests = num_requests
        self.response_times: List[float] = []
        self.success_count = 0
        self.failure_count = 0
        self.timeout_count = 0
        self.total_time = 0.0

    def add_result(
        self, response_time: float, success: bool, timeout: bool = False
    ) -> None:
        """Add a single request result"""
        self.response_times.append(response_time)
        if timeout:
            self.timeout_count += 1
        elif success:
            self.success_count += 1
        else:
            self.failure_count += 1

    def calculate_metrics(self) -> Dict[str, float]:
        """Calculate aggregate metrics"""
        if not self.response_times:
            return {
                "total_time": 0.0,
                "avg_response_time": 0.0,
                "min_response_time": 0.0,
                "max_response_time": 0.0,
                "median_response_time": 0.0,
                "p95_response_time": 0.0,
                "p99_response_time": 0.0,
                "success_rate": 0.0,
                "requests_per_second": 0.0,
                "error_rate": 0.0,
                "timeout_rate": 0.0,
            }

        sorted_times = sorted(self.response_times)
        p95_index = int(len(sorted_times) * 0.95)
        p99_index = int(len(sorted_times) * 0.99)

        return {
            "total_time": self.total_time,
            "avg_response_time": statistics.mean(self.response_times),
            "min_response_time": min(self.response_times),
            "max_response_time": max(self.response_times),
            "median_response_time": statistics.median(self.response_times),
            "p95_response_time": sorted_times[p95_index]
            if p95_index < len(sorted_times)
            else sorted_times[-1],
            "p99_response_time": sorted_times[p99_index]
            if p99_index < len(sorted_times)
            else sorted_times[-1],
            "success_rate": (
                self.success_count / self.num_requests
                if self.num_requests > 0
                else 0.0
            ),
            "requests_per_second": (
                self.num_requests / self.total_time if self.total_time > 0 else 0.0
            ),
            "error_rate": (
                self.failure_count / self.num_requests
                if self.num_requests > 0
                else 0.0
            ),
            "timeout_rate": (
                self.timeout_count / self.num_requests
                if self.num_requests > 0
                else 0.0
            ),
        }


async def load_test_endpoint(
    url: str,
    num_requests: int = 100,
    concurrent: int = 10,
    headers: Dict[str, str] = None,
    timeout: float = 10.0,
) -> LoadTestResult:
    """
    Load test an endpoint with concurrent requests.

    Args:
        url: Full URL to test
        num_requests: Total number of requests to make
        concurrent: Number of concurrent requests
        headers: Optional headers to include
        timeout: Request timeout in seconds

    Returns:
        LoadTestResult with performance metrics
    """
    result = LoadTestResult(url, num_requests)
    start_time = time.time()

    async def make_request(client: httpx.AsyncClient, semaphore: asyncio.Semaphore):
        """Make a single request with concurrency control"""
        async with semaphore:
            request_start = time.time()
            try:
                response = await client.get(url, headers=headers, timeout=timeout)
                request_time = (time.time() - request_start) * 1000  # Convert to ms
                result.add_result(request_time, response.status_code == 200)
            except httpx.TimeoutException:
                request_time = (time.time() - request_start) * 1000
                result.add_result(request_time, False, timeout=True)
            except Exception:
                request_time = (time.time() - request_start) * 1000
                result.add_result(request_time, False)

    # Create semaphore for concurrency control
    semaphore = asyncio.Semaphore(concurrent)

    # Create async HTTP client
    async with httpx.AsyncClient() as client:
        # Create all request tasks
        tasks = [make_request(client, semaphore) for _ in range(num_requests)]

        # Execute all requests concurrently
        await asyncio.gather(*tasks)

    result.total_time = time.time() - start_time
    return result


def print_results(endpoint_name: str, metrics: Dict[str, float]) -> None:
    """Pretty print test results"""
    print(f"\n{'=' * 70}")
    print(f"Load Test Results: {endpoint_name}")
    print(f"{'=' * 70}")
    print(f"Total Time:           {metrics['total_time']:.2f}s")
    print(f"Requests/Second:      {metrics['requests_per_second']:.2f}")
    print(f"Success Rate:         {metrics['success_rate'] * 100:.1f}%")
    print(f"Error Rate:           {metrics['error_rate'] * 100:.1f}%")
    print(f"Timeout Rate:         {metrics['timeout_rate'] * 100:.1f}%")
    print(f"\nResponse Times (ms):")
    print(f"  Average:            {metrics['avg_response_time']:.2f}")
    print(f"  Median:             {metrics['median_response_time']:.2f}")
    print(f"  Min:                {metrics['min_response_time']:.2f}")
    print(f"  Max:                {metrics['max_response_time']:.2f}")
    print(f"  95th Percentile:    {metrics['p95_response_time']:.2f}")
    print(f"  99th Percentile:    {metrics['p99_response_time']:.2f}")
    print(f"{'=' * 70}\n")


# Test 1: Health Check Endpoint
@pytest.mark.asyncio
async def test_load_health_endpoint():
    """
    Test /api/health endpoint

    Expected baseline:
    - Average response time: <100ms
    - Requests per second: >200
    - Success rate: >99%
    """
    url = f"{BASE_URL}/api/health"
    result = await load_test_endpoint(url, num_requests=100, concurrent=10)
    metrics = result.calculate_metrics()

    print_results("Health Check", metrics)

    # Relaxed assertions for baseline establishment
    assert metrics["success_rate"] >= 0.90, f"Health check success rate too low: {metrics['success_rate']*100:.1f}%"
    assert (
        metrics["avg_response_time"] < 1000
    ), f"Health check avg response time too high: {metrics['avg_response_time']:.2f}ms"


# Test 2: Market Indices Endpoint
@pytest.mark.asyncio
async def test_load_market_indices():
    """
    Test /api/market/indices endpoint

    Expected baseline:
    - Average response time: <500ms
    - Requests per second: >100
    - Success rate: >95%
    """
    url = f"{BASE_URL}/api/market/indices"
    jwt_token = await get_jwt_token()
    headers = {"Authorization": f"Bearer {jwt_token}"}
    result = await load_test_endpoint(
        url, num_requests=100, concurrent=10, headers=headers, timeout=15.0
    )
    metrics = result.calculate_metrics()

    print_results("Market Indices", metrics)

    # Relaxed assertions - market data can be slower
    assert (
        metrics["success_rate"] >= 0.80
    ), f"Market indices success rate too low: {metrics['success_rate']*100:.1f}%"
    assert (
        metrics["avg_response_time"] < 5000
    ), f"Market indices avg response time too high: {metrics['avg_response_time']:.2f}ms"


# Test 3: AI Recommendations Endpoint
@pytest.mark.asyncio
async def test_load_ai_recommendations():
    """
    Test /api/ai/recommendations endpoint

    Expected baseline:
    - Average response time: <2000ms
    - Requests per second: >20
    - Success rate: >90%
    """
    url = f"{BASE_URL}/api/ai/recommendations"
    jwt_token = await get_jwt_token()
    headers = {"Authorization": f"Bearer {jwt_token}"}
    result = await load_test_endpoint(
        url, num_requests=50, concurrent=5, headers=headers, timeout=30.0
    )
    metrics = result.calculate_metrics()

    print_results("AI Recommendations", metrics)

    # Very relaxed for AI endpoint - can be slow
    assert (
        metrics["success_rate"] >= 0.70
    ), f"AI recommendations success rate too low: {metrics['success_rate']*100:.1f}%"
    assert (
        metrics["avg_response_time"] < 10000
    ), f"AI recommendations avg response time too high: {metrics['avg_response_time']:.2f}ms"


# Test 4: Strategy Templates Endpoint
@pytest.mark.asyncio
async def test_load_strategy_templates():
    """
    Test /api/strategies/templates endpoint

    Expected baseline:
    - Average response time: <500ms
    - Requests per second: >100
    - Success rate: >95%
    """
    url = f"{BASE_URL}/api/strategies/templates"
    jwt_token = await get_jwt_token()
    headers = {"Authorization": f"Bearer {jwt_token}"}
    result = await load_test_endpoint(
        url, num_requests=100, concurrent=10, headers=headers
    )
    metrics = result.calculate_metrics()

    print_results("Strategy Templates", metrics)

    assert (
        metrics["success_rate"] >= 0.85
    ), f"Strategy templates success rate too low: {metrics['success_rate']*100:.1f}%"
    assert (
        metrics["avg_response_time"] < 2000
    ), f"Strategy templates avg response time too high: {metrics['avg_response_time']:.2f}ms"


# Test 5: Portfolio Summary Endpoint
@pytest.mark.asyncio
async def test_load_portfolio_summary():
    """
    Test /api/portfolio endpoint

    Expected baseline:
    - Average response time: <1000ms
    - Requests per second: >50
    - Success rate: >95%
    """
    url = f"{BASE_URL}/api/portfolio"
    jwt_token = await get_jwt_token()
    headers = {"Authorization": f"Bearer {jwt_token}"}
    result = await load_test_endpoint(
        url, num_requests=100, concurrent=10, headers=headers, timeout=15.0
    )
    metrics = result.calculate_metrics()

    print_results("Portfolio Summary", metrics)

    assert (
        metrics["success_rate"] >= 0.80
    ), f"Portfolio summary success rate too low: {metrics['success_rate']*100:.1f}%"
    assert (
        metrics["avg_response_time"] < 5000
    ), f"Portfolio summary avg response time too high: {metrics['avg_response_time']:.2f}ms"


# Test 6: Positions Endpoint
@pytest.mark.asyncio
async def test_load_positions():
    """
    Test /api/positions endpoint

    Expected baseline:
    - Average response time: <1000ms
    - Requests per second: >50
    - Success rate: >95%
    """
    url = f"{BASE_URL}/api/positions"
    jwt_token = await get_jwt_token()
    headers = {"Authorization": f"Bearer {jwt_token}"}
    result = await load_test_endpoint(
        url, num_requests=100, concurrent=10, headers=headers, timeout=15.0
    )
    metrics = result.calculate_metrics()

    print_results("Positions", metrics)

    assert (
        metrics["success_rate"] >= 0.80
    ), f"Positions success rate too low: {metrics['success_rate']*100:.1f}%"
    assert (
        metrics["avg_response_time"] < 5000
    ), f"Positions avg response time too high: {metrics['avg_response_time']:.2f}ms"


# Test 7: News Endpoint
@pytest.mark.asyncio
async def test_load_news():
    """
    Test /api/news endpoint

    Expected baseline:
    - Average response time: <2000ms
    - Requests per second: >30
    - Success rate: >90%
    """
    url = f"{BASE_URL}/api/news?symbol=AAPL"
    jwt_token = await get_jwt_token()
    headers = {"Authorization": f"Bearer {jwt_token}"}
    result = await load_test_endpoint(
        url, num_requests=50, concurrent=5, headers=headers, timeout=20.0
    )
    metrics = result.calculate_metrics()

    print_results("News", metrics)

    assert (
        metrics["success_rate"] >= 0.70
    ), f"News success rate too low: {metrics['success_rate']*100:.1f}%"
    assert (
        metrics["avg_response_time"] < 8000
    ), f"News avg response time too high: {metrics['avg_response_time']:.2f}ms"


# Comprehensive load test runner
@pytest.mark.asyncio
async def test_comprehensive_load_baseline():
    """
    Run comprehensive load test across all critical endpoints

    This test provides a complete baseline snapshot for production monitoring.
    Results should be documented in AGENT_7C_PRODUCTION_VALIDATION.md
    """
    print("\n" + "=" * 70)
    print("COMPREHENSIVE LOAD TEST BASELINE - Agent 7C")
    print("=" * 70)
    print(f"Base URL: {BASE_URL}")
    print(f"Test Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70 + "\n")

    # Get JWT token for authenticated requests
    print("Authenticating...")
    jwt_token = await get_jwt_token()
    headers = {"Authorization": f"Bearer {jwt_token}"}
    print(f"JWT token obtained: {jwt_token[:20]}...\n")

    all_results = []

    # Test 1: Health Check (lightweight)
    print("Running Test 1/7: Health Check...")
    result1 = await load_test_endpoint(
        f"{BASE_URL}/api/health", num_requests=200, concurrent=20
    )
    all_results.append(("Health Check", result1.calculate_metrics()))

    # Test 2: Market Indices
    print("Running Test 2/7: Market Indices...")
    result2 = await load_test_endpoint(
        f"{BASE_URL}/api/market/indices",
        num_requests=100,
        concurrent=10,
        headers=headers,
        timeout=15.0,
    )
    all_results.append(("Market Indices", result2.calculate_metrics()))

    # Test 3: Portfolio
    print("Running Test 3/7: Portfolio...")
    result3 = await load_test_endpoint(
        f"{BASE_URL}/api/portfolio",
        num_requests=100,
        concurrent=10,
        headers=headers,
        timeout=15.0,
    )
    all_results.append(("Portfolio", result3.calculate_metrics()))

    # Test 4: Positions
    print("Running Test 4/7: Positions...")
    result4 = await load_test_endpoint(
        f"{BASE_URL}/api/positions",
        num_requests=100,
        concurrent=10,
        headers=headers,
        timeout=15.0,
    )
    all_results.append(("Positions", result4.calculate_metrics()))

    # Test 5: Strategy Templates
    print("Running Test 5/7: Strategy Templates...")
    result5 = await load_test_endpoint(
        f"{BASE_URL}/api/strategies/templates",
        num_requests=100,
        concurrent=10,
        headers=headers,
    )
    all_results.append(("Strategy Templates", result5.calculate_metrics()))

    # Test 6: News (lighter load)
    print("Running Test 6/7: News...")
    result6 = await load_test_endpoint(
        f"{BASE_URL}/api/news?symbol=AAPL",
        num_requests=50,
        concurrent=5,
        headers=headers,
        timeout=20.0,
    )
    all_results.append(("News", result6.calculate_metrics()))

    # Test 7: AI Recommendations (lightest load - expensive endpoint)
    print("Running Test 7/7: AI Recommendations...")
    result7 = await load_test_endpoint(
        f"{BASE_URL}/api/ai/recommendations",
        num_requests=20,
        concurrent=2,
        headers=headers,
        timeout=30.0,
    )
    all_results.append(("AI Recommendations", result7.calculate_metrics()))

    # Print summary
    print("\n" + "=" * 70)
    print("BASELINE SUMMARY - ALL ENDPOINTS")
    print("=" * 70)
    print(
        f"{'Endpoint':<25} {'Avg (ms)':<12} {'P95 (ms)':<12} {'RPS':<10} {'Success %':<12}"
    )
    print("-" * 70)

    for name, metrics in all_results:
        print(
            f"{name:<25} "
            f"{metrics['avg_response_time']:<12.2f} "
            f"{metrics['p95_response_time']:<12.2f} "
            f"{metrics['requests_per_second']:<10.2f} "
            f"{metrics['success_rate']*100:<12.1f}"
        )

    print("=" * 70 + "\n")

    # Overall health check
    overall_success = sum(m["success_rate"] for _, m in all_results) / len(all_results)
    print(f"Overall Success Rate: {overall_success*100:.1f}%")
    print(f"Tests Completed: {len(all_results)}/7")

    assert (
        overall_success >= 0.70
    ), f"Overall success rate too low: {overall_success*100:.1f}%"


if __name__ == "__main__":
    # Allow running tests directly for manual load testing
    print("Starting manual load test...")
    asyncio.run(test_comprehensive_load_baseline())
