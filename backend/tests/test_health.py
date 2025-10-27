"""
Comprehensive Health Monitor Tests

Tests the health monitoring service with mocked external clients
to verify healthy, degraded, and failure scenarios.
"""

from unittest.mock import Mock, patch

from app.services.health_monitor import HealthMonitor


class TestHealthMonitor:
    """Test suite for HealthMonitor class"""

    def setup_method(self):
        """Set up test fixtures before each test method"""
        self.health_monitor = HealthMonitor()

    def test_health_monitor_initialization(self):
        """Test health monitor initializes correctly"""
        assert self.health_monitor.start_time is not None
        assert self.health_monitor.request_count == 0
        assert self.health_monitor.error_count == 0
        assert self.health_monitor.response_times == []
        assert self.health_monitor.cache_hits == 0
        assert self.health_monitor.cache_misses == 0

    def test_record_request_success(self):
        """Test recording successful requests"""
        self.health_monitor.record_request(0.5, is_error=False)

        assert self.health_monitor.request_count == 1
        assert self.health_monitor.error_count == 0
        assert self.health_monitor.response_times == [0.5]

    def test_record_request_error(self):
        """Test recording failed requests"""
        self.health_monitor.record_request(2.0, is_error=True)

        assert self.health_monitor.request_count == 1
        assert self.health_monitor.error_count == 1
        assert self.health_monitor.response_times == [2.0]

    def test_record_cache_hit(self):
        """Test recording cache hits"""
        self.health_monitor.record_cache_hit()
        assert self.health_monitor.cache_hits == 1

    def test_record_cache_miss(self):
        """Test recording cache misses"""
        self.health_monitor.record_cache_miss()
        assert self.health_monitor.cache_misses == 1

    def test_response_times_limit(self):
        """Test response times are limited to 1000 entries"""
        # Add 1001 response times
        for i in range(1001):
            self.health_monitor.record_request(0.1)

        assert len(self.health_monitor.response_times) == 1000
        assert self.health_monitor.response_times[0] == 0.1  # First entry
        assert self.health_monitor.response_times[-1] == 0.1  # Last entry

    @patch("app.services.health_monitor.get_tradier_client")
    @patch("app.services.health_monitor.get_alpaca_client")
    def test_check_dependencies_healthy(self, mock_alpaca_client, mock_tradier_client):
        """Test dependency check when all services are healthy"""
        # Mock successful Tradier client
        mock_tradier = Mock()
        mock_tradier.get_market_clock.return_value = {"clock": {"state": "open"}}
        mock_tradier_client.return_value = mock_tradier

        # Mock successful Alpaca client
        mock_alpaca = Mock()
        mock_alpaca.get_account.return_value = {"account_number": "TEST123"}
        mock_alpaca_client.return_value = mock_alpaca

        dependencies = self.health_monitor._check_dependencies()

        assert dependencies["tradier"]["status"] == "up"
        assert "response_time_ms" in dependencies["tradier"]
        assert dependencies["alpaca"]["status"] == "up"
        assert "response_time_ms" in dependencies["alpaca"]

    @patch("app.services.health_monitor.get_tradier_client")
    @patch("app.services.health_monitor.get_alpaca_client")
    def test_check_dependencies_tradier_down(
        self, mock_alpaca_client, mock_tradier_client
    ):
        """Test dependency check when Tradier is down"""
        # Mock failing Tradier client
        mock_tradier_client.side_effect = Exception("Tradier API unavailable")

        # Mock successful Alpaca client
        mock_alpaca = Mock()
        mock_alpaca.get_account.return_value = {"account_number": "TEST123"}
        mock_alpaca_client.return_value = mock_alpaca

        dependencies = self.health_monitor._check_dependencies()

        assert dependencies["tradier"]["status"] == "down"
        assert "error" in dependencies["tradier"]
        assert dependencies["alpaca"]["status"] == "up"

    @patch("app.services.health_monitor.get_tradier_client")
    @patch("app.services.health_monitor.get_alpaca_client")
    def test_check_dependencies_alpaca_down(
        self, mock_alpaca_client, mock_tradier_client
    ):
        """Test dependency check when Alpaca is down"""
        # Mock successful Tradier client
        mock_tradier = Mock()
        mock_tradier.get_market_clock.return_value = {"clock": {"state": "open"}}
        mock_tradier_client.return_value = mock_tradier

        # Mock failing Alpaca client
        mock_alpaca_client.side_effect = Exception("Alpaca API unavailable")

        dependencies = self.health_monitor._check_dependencies()

        assert dependencies["tradier"]["status"] == "up"
        assert dependencies["alpaca"]["status"] == "down"
        assert "error" in dependencies["alpaca"]

    @patch("app.services.health_monitor.get_tradier_client")
    @patch("app.services.health_monitor.get_alpaca_client")
    def test_check_dependencies_both_down(
        self, mock_alpaca_client, mock_tradier_client
    ):
        """Test dependency check when both services are down"""
        # Mock both clients failing
        mock_tradier_client.side_effect = Exception("Tradier API unavailable")
        mock_alpaca_client.side_effect = Exception("Alpaca API unavailable")

        dependencies = self.health_monitor._check_dependencies()

        assert dependencies["tradier"]["status"] == "down"
        assert dependencies["alpaca"]["status"] == "down"
        assert "error" in dependencies["tradier"]
        assert "error" in dependencies["alpaca"]

    @patch("app.services.health_monitor.get_tradier_client")
    @patch("app.services.health_monitor.get_alpaca_client")
    def test_check_api_configuration_healthy(
        self, mock_alpaca_client, mock_tradier_client
    ):
        """Test API configuration check when all keys are configured"""
        # Mock Tradier client with configured keys
        mock_tradier = Mock()
        mock_tradier.api_key = "test-tradier-key"
        mock_tradier.account_id = "test-account-id"
        mock_tradier.base_url = "https://api.tradier.com/v1"
        mock_tradier_client.return_value = mock_tradier

        # Mock Alpaca client with configured keys
        mock_alpaca = Mock()
        mock_alpaca.api_key = "test-alpaca-key"
        mock_alpaca.secret_key = "test-alpaca-secret"
        mock_alpaca_client.return_value = mock_alpaca

        config = self.health_monitor._check_api_configuration()

        assert config["tradier"]["api_key_configured"] is True
        assert config["tradier"]["account_id_configured"] is True
        assert config["alpaca"]["api_key_configured"] is True
        assert config["alpaca"]["secret_key_configured"] is True

    @patch("app.services.health_monitor.get_tradier_client")
    @patch("app.services.health_monitor.get_alpaca_client")
    def test_check_api_configuration_missing_keys(
        self, mock_alpaca_client, mock_tradier_client
    ):
        """Test API configuration check when keys are missing"""
        # Mock Tradier client with missing keys
        mock_tradier_client.side_effect = ValueError(
            "TRADIER_API_KEY and TRADIER_ACCOUNT_ID must be set in .env"
        )

        # Mock Alpaca client with missing keys
        mock_alpaca_client.side_effect = ValueError(
            "ALPACA_PAPER_API_KEY and ALPACA_PAPER_SECRET_KEY must be set in .env"
        )

        config = self.health_monitor._check_api_configuration()

        assert config["tradier"]["api_key_configured"] is False
        assert config["tradier"]["account_id_configured"] is False
        assert "error" in config["tradier"]
        assert config["alpaca"]["api_key_configured"] is False
        assert config["alpaca"]["secret_key_configured"] is False
        assert "error" in config["alpaca"]

    @patch("app.services.health_monitor.get_tradier_client")
    @patch("app.services.health_monitor.get_alpaca_client")
    @patch("psutil.cpu_percent")
    @patch("psutil.virtual_memory")
    @patch("psutil.disk_usage")
    def test_get_system_health_healthy(
        self, mock_disk, mock_memory, mock_cpu, mock_alpaca_client, mock_tradier_client
    ):
        """Test system health when all systems are healthy"""
        # Mock system metrics
        mock_cpu.return_value = 50.0
        mock_memory.return_value = Mock(
            percent=70.0, used=1024 * 1024 * 1024, total=2 * 1024 * 1024 * 1024
        )
        mock_disk.return_value = Mock(percent=60.0, free=100 * 1024 * 1024 * 1024)

        # Mock successful clients
        mock_tradier = Mock()
        mock_tradier.get_market_clock.return_value = {"clock": {"state": "open"}}
        mock_tradier_client.return_value = mock_tradier

        mock_alpaca = Mock()
        mock_alpaca.get_account.return_value = {"account_number": "TEST123"}
        mock_alpaca_client.return_value = mock_alpaca

        health = self.health_monitor.get_system_health()

        assert health["status"] == "healthy"
        assert "timestamp" in health
        assert "uptime_seconds" in health
        assert "system" in health
        assert "application" in health
        assert "dependencies" in health
        assert "configuration" in health

    @patch("app.services.health_monitor.get_tradier_client")
    @patch("app.services.health_monitor.get_alpaca_client")
    @patch("psutil.cpu_percent")
    @patch("psutil.virtual_memory")
    @patch("psutil.disk_usage")
    def test_get_system_health_degraded_cpu(
        self, mock_disk, mock_memory, mock_cpu, mock_alpaca_client, mock_tradier_client
    ):
        """Test system health when CPU is degraded"""
        # Mock degraded CPU
        mock_cpu.return_value = 85.0  # Above 80% threshold
        mock_memory.return_value = Mock(
            percent=70.0, used=1024 * 1024 * 1024, total=2 * 1024 * 1024 * 1024
        )
        mock_disk.return_value = Mock(percent=60.0, free=100 * 1024 * 1024 * 1024)

        # Mock successful clients
        mock_tradier = Mock()
        mock_tradier.get_market_clock.return_value = {"clock": {"state": "open"}}
        mock_tradier_client.return_value = mock_tradier

        mock_alpaca = Mock()
        mock_alpaca.get_account.return_value = {"account_number": "TEST123"}
        mock_alpaca_client.return_value = mock_alpaca

        health = self.health_monitor.get_system_health()

        assert health["status"] == "degraded"

    @patch("app.services.health_monitor.get_tradier_client")
    @patch("app.services.health_monitor.get_alpaca_client")
    @patch("psutil.cpu_percent")
    @patch("psutil.virtual_memory")
    @patch("psutil.disk_usage")
    def test_get_system_health_degraded_memory(
        self, mock_disk, mock_memory, mock_cpu, mock_alpaca_client, mock_tradier_client
    ):
        """Test system health when memory is degraded"""
        # Mock degraded memory
        mock_cpu.return_value = 50.0
        mock_memory.return_value = Mock(
            percent=90.0, used=1024 * 1024 * 1024, total=2 * 1024 * 1024 * 1024
        )  # Above 85% threshold
        mock_disk.return_value = Mock(percent=60.0, free=100 * 1024 * 1024 * 1024)

        # Mock successful clients
        mock_tradier = Mock()
        mock_tradier.get_market_clock.return_value = {"clock": {"state": "open"}}
        mock_tradier_client.return_value = mock_tradier

        mock_alpaca = Mock()
        mock_alpaca.get_account.return_value = {"account_number": "TEST123"}
        mock_alpaca_client.return_value = mock_alpaca

        health = self.health_monitor.get_system_health()

        assert health["status"] == "degraded"

    def test_error_rate_calculation(self):
        """Test error rate calculation"""
        # Record some requests with errors
        self.health_monitor.record_request(0.5, is_error=False)
        self.health_monitor.record_request(1.0, is_error=True)
        self.health_monitor.record_request(0.8, is_error=False)
        self.health_monitor.record_request(2.0, is_error=True)

        health = self.health_monitor.get_system_health()

        assert health["application"]["total_requests"] == 4
        assert health["application"]["total_errors"] == 2
        assert health["application"]["error_rate_percent"] == 50.0

    def test_cache_hit_rate_calculation(self):
        """Test cache hit rate calculation"""
        # Record some cache hits and misses
        self.health_monitor.record_cache_hit()
        self.health_monitor.record_cache_hit()
        self.health_monitor.record_cache_miss()

        health = self.health_monitor.get_system_health()

        assert health["application"]["cache_hits"] == 2
        assert health["application"]["cache_misses"] == 1
        assert health["application"]["cache_hit_rate_percent"] == 66.67  # 2/3 * 100

    def test_average_response_time_calculation(self):
        """Test average response time calculation"""
        # Record some response times
        self.health_monitor.record_request(0.5)
        self.health_monitor.record_request(1.0)
        self.health_monitor.record_request(1.5)

        health = self.health_monitor.get_system_health()

        expected_avg = (0.5 + 1.0 + 1.5) / 3
        assert health["application"]["avg_response_time_ms"] == expected_avg * 1000

    def test_requests_per_minute_calculation(self):
        """Test requests per minute calculation"""
        # Record some requests
        self.health_monitor.record_request(0.5)
        self.health_monitor.record_request(1.0)

        health = self.health_monitor.get_system_health()

        # Should have some requests per minute (exact value depends on test execution time)
        assert health["application"]["requests_per_minute"] >= 0


class TestHealthMonitorIntegration:
    """Integration tests for health monitor with FastAPI"""

    def test_health_endpoint_basic(self, client):
        """Test basic health endpoint returns 200"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "time" in data

    def test_health_endpoint_detailed_requires_auth(self, client_no_auth):
        """Test detailed health endpoint requires authentication"""
        response = client_no_auth.get("/api/health/detailed")
        assert response.status_code == 401  # Unauthorized

    def test_health_endpoint_detailed_with_auth(self, client, auth_headers):
        """Test detailed health endpoint with authentication"""
        response = client.get("/api/health/detailed", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "system" in data
        assert "application" in data
        assert "dependencies" in data
        assert "configuration" in data

    def test_readiness_endpoint_healthy(self, client):
        """Test readiness endpoint when system is healthy"""
        with patch(
            "app.services.health_monitor.HealthMonitor.get_system_health"
        ) as mock_health:
            mock_health.return_value = {"status": "healthy"}
            response = client.get("/api/health/ready")
            assert response.status_code == 200
            data = response.json()
            assert data["ready"] is True

    def test_readiness_endpoint_degraded(self, client):
        """Test readiness endpoint when system is degraded"""
        with patch(
            "app.services.health_monitor.HealthMonitor.get_system_health"
        ) as mock_health:
            mock_health.return_value = {"status": "degraded"}
            response = client.get("/api/health/ready")
            assert response.status_code == 503
            data = response.json()
            assert data["detail"]["ready"] is False

    def test_liveness_endpoint(self, client):
        """Test liveness endpoint always returns alive"""
        response = client.get("/api/health/liveness")
        assert response.status_code == 200
        data = response.json()
        assert data["alive"] is True
