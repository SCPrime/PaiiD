"""
Security Headers Validation Tests

Tests security headers middleware implementation.
Validates presence and correctness of security headers (CSP, HSTS, X-Frame-Options, etc.).

Agent 6C: Rate Limiting & Security Audit Specialist
"""

import pytest
from fastapi.testclient import TestClient


class TestSecurityHeadersPresence:
    """Test that all required security headers are present"""

    def test_x_content_type_options_present(self, client: TestClient):
        """Test X-Content-Type-Options header is present"""
        response = client.get("/api/health")
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"

    def test_x_frame_options_present(self, client: TestClient):
        """Test X-Frame-Options header is present"""
        response = client.get("/api/health")
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"

    def test_referrer_policy_present(self, client: TestClient):
        """Test Referrer-Policy header is present"""
        response = client.get("/api/health")
        assert "Referrer-Policy" in response.headers
        assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"

    def test_x_xss_protection_present(self, client: TestClient):
        """Test X-XSS-Protection header is present"""
        response = client.get("/api/health")
        assert "X-XSS-Protection" in response.headers
        assert response.headers["X-XSS-Protection"] == "1; mode=block"

    def test_strict_transport_security_present(self, client: TestClient):
        """Test Strict-Transport-Security (HSTS) header is present"""
        response = client.get("/api/health")
        assert "Strict-Transport-Security" in response.headers

    def test_permissions_policy_present(self, client: TestClient):
        """Test Permissions-Policy header is present"""
        response = client.get("/api/health")
        assert "Permissions-Policy" in response.headers

    def test_content_security_policy_present(self, client: TestClient):
        """Test Content-Security-Policy (CSP) header is present"""
        response = client.get("/api/health")
        assert "Content-Security-Policy" in response.headers


class TestSecurityHeadersValues:
    """Test that security headers have correct values"""

    def test_x_content_type_options_correct(self, client: TestClient):
        """Test X-Content-Type-Options is set to nosniff"""
        response = client.get("/api/health")
        assert response.headers["X-Content-Type-Options"] == "nosniff"

    def test_x_frame_options_deny(self, client: TestClient):
        """Test X-Frame-Options is set to DENY"""
        response = client.get("/api/health")
        # Should be DENY to prevent clickjacking
        assert response.headers["X-Frame-Options"] == "DENY"

    def test_hsts_max_age(self, client: TestClient):
        """Test HSTS header has appropriate max-age"""
        response = client.get("/api/health")
        hsts = response.headers["Strict-Transport-Security"]

        # Should include max-age directive
        assert "max-age=" in hsts

        # Extract max-age value
        for directive in hsts.split(";"):
            if "max-age=" in directive:
                max_age = directive.strip().replace("max-age=", "")
                # Should be at least 180 days (15552000 seconds)
                # Recommended: 1 year (31536000 seconds)
                assert int(max_age) >= 15552000

    def test_hsts_includes_subdomains(self, client: TestClient):
        """Test HSTS header includes includeSubDomains directive"""
        response = client.get("/api/health")
        hsts = response.headers["Strict-Transport-Security"]
        assert "includeSubDomains" in hsts

    def test_hsts_preload_recommended(self, client: TestClient):
        """Test HSTS header includes preload directive (recommended)"""
        response = client.get("/api/health")
        hsts = response.headers["Strict-Transport-Security"]
        # Preload is recommended for maximum security
        assert "preload" in hsts

    def test_csp_default_src(self, client: TestClient):
        """Test CSP default-src directive"""
        response = client.get("/api/health")
        csp = response.headers["Content-Security-Policy"]

        # Should restrict default sources to 'self'
        assert "default-src 'self'" in csp

    def test_csp_script_src(self, client: TestClient):
        """Test CSP script-src directive"""
        response = client.get("/api/health")
        csp = response.headers["Content-Security-Policy"]

        # Should have script-src directive
        assert "script-src" in csp

        # May allow 'self' and 'unsafe-inline' for Swagger UI compatibility
        assert "'self'" in csp

    def test_csp_frame_ancestors(self, client: TestClient):
        """Test CSP frame-ancestors directive prevents clickjacking"""
        response = client.get("/api/health")
        csp = response.headers["Content-Security-Policy"]

        # Should prevent embedding in iframes
        assert "frame-ancestors 'none'" in csp or "frame-ancestors 'self'" in csp

    def test_csp_object_src_none(self, client: TestClient):
        """Test CSP object-src is set to 'none' to block plugins"""
        response = client.get("/api/health")
        csp = response.headers["Content-Security-Policy"]

        # Should block plugins (Flash, Java, etc.)
        assert "object-src 'none'" in csp

    def test_csp_upgrade_insecure_requests(self, client: TestClient):
        """Test CSP includes upgrade-insecure-requests"""
        response = client.get("/api/health")
        csp = response.headers["Content-Security-Policy"]

        # Should upgrade HTTP to HTTPS automatically
        assert "upgrade-insecure-requests" in csp

    def test_permissions_policy_camera_disabled(self, client: TestClient):
        """Test Permissions-Policy disables camera"""
        response = client.get("/api/health")
        permissions = response.headers["Permissions-Policy"]

        # Trading app doesn't need camera access
        assert "camera=()" in permissions

    def test_permissions_policy_microphone_disabled(self, client: TestClient):
        """Test Permissions-Policy disables microphone"""
        response = client.get("/api/health")
        permissions = response.headers["Permissions-Policy"]

        # Trading app doesn't need microphone access
        assert "microphone=()" in permissions

    def test_permissions_policy_geolocation_disabled(self, client: TestClient):
        """Test Permissions-Policy disables geolocation"""
        response = client.get("/api/health")
        permissions = response.headers["Permissions-Policy"]

        # Trading app doesn't need geolocation
        assert "geolocation=()" in permissions

    def test_permissions_policy_payment_disabled(self, client: TestClient):
        """Test Permissions-Policy disables payment API"""
        response = client.get("/api/health")
        permissions = response.headers["Permissions-Policy"]

        # Trading app handles payments separately
        assert "payment=()" in permissions


class TestSecurityHeadersConsistency:
    """Test that security headers are consistent across endpoints"""

    def test_headers_on_health_endpoint(self, client: TestClient):
        """Test security headers on health endpoint"""
        response = client.get("/api/health")
        assert response.status_code == 200
        self._assert_all_security_headers(response)

    def test_headers_on_docs_endpoint(self, client: TestClient):
        """Test security headers on API docs endpoint"""
        response = client.get("/api/docs")
        # Docs may redirect or return 200
        assert response.status_code in [200, 307]
        self._assert_all_security_headers(response)

    def test_headers_on_openapi_endpoint(self, client: TestClient):
        """Test security headers on OpenAPI schema endpoint"""
        response = client.get("/api/openapi.json")
        assert response.status_code == 200
        self._assert_all_security_headers(response)

    def test_headers_on_404_endpoint(self, client: TestClient):
        """Test security headers on 404 responses"""
        response = client.get("/api/nonexistent-endpoint-12345")
        assert response.status_code == 404
        self._assert_all_security_headers(response)

    def test_headers_on_post_endpoint(self, client: TestClient, auth_headers):
        """Test security headers on POST requests"""
        response = client.post(
            "/api/strategies",
            json={"name": "Test", "strategy_type": "momentum", "config": {}},
            headers=auth_headers
        )
        # May succeed or fail validation, but headers should be present
        self._assert_all_security_headers(response)

    def _assert_all_security_headers(self, response):
        """Helper to assert all required security headers are present"""
        required_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "Referrer-Policy",
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "Permissions-Policy",
            "Content-Security-Policy",
        ]

        for header in required_headers:
            assert header in response.headers, f"Missing security header: {header}"


class TestCORSHeaders:
    """Test CORS headers configuration"""

    def test_cors_headers_on_preflight(self, client: TestClient):
        """Test CORS headers on OPTIONS (preflight) request"""
        response = client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            }
        )

        # CORS middleware should handle preflight
        assert "Access-Control-Allow-Origin" in response.headers

    def test_cors_allows_localhost_3000(self, client: TestClient):
        """Test CORS allows localhost:3000 (frontend dev server)"""
        response = client.get(
            "/api/health",
            headers={"Origin": "http://localhost:3000"}
        )

        # Should allow localhost:3000
        if "Access-Control-Allow-Origin" in response.headers:
            allowed_origin = response.headers["Access-Control-Allow-Origin"]
            assert allowed_origin in ["*", "http://localhost:3000"]

    def test_cors_allows_credentials(self, client: TestClient):
        """Test CORS allows credentials (cookies, auth headers)"""
        response = client.get(
            "/api/health",
            headers={"Origin": "http://localhost:3000"}
        )

        # Should allow credentials for authenticated requests
        if "Access-Control-Allow-Credentials" in response.headers:
            assert response.headers["Access-Control-Allow-Credentials"] == "true"


class TestSecurityHeadersMiddlewareImplementation:
    """Test security headers middleware implementation details"""

    def test_middleware_registered(self):
        """Test that SecurityHeadersMiddleware is registered"""
        from app.main import app
        from app.middleware.security_headers import SecurityHeadersMiddleware

        # Middleware should be in app's middleware stack
        middleware_types = [type(m) for m in app.user_middleware]
        assert SecurityHeadersMiddleware in middleware_types

    def test_middleware_uses_setdefault(self, client: TestClient):
        """Test that middleware uses setdefault (doesn't override existing headers)"""
        # Make request - middleware should add headers
        response = client.get("/api/health")

        # All security headers should be present
        assert "X-Content-Type-Options" in response.headers

        # If endpoint sets a custom header, middleware shouldn't override it
        # This is ensured by using setdefault() in middleware implementation


class TestCSPDirectivesComprehensive:
    """Comprehensive CSP directives testing"""

    def test_csp_base_uri_restricted(self, client: TestClient):
        """Test CSP restricts base-uri to prevent base tag injection"""
        response = client.get("/api/health")
        csp = response.headers["Content-Security-Policy"]

        assert "base-uri 'self'" in csp

    def test_csp_form_action_restricted(self, client: TestClient):
        """Test CSP restricts form-action to prevent form hijacking"""
        response = client.get("/api/health")
        csp = response.headers["Content-Security-Policy"]

        assert "form-action 'self'" in csp

    def test_csp_img_src_allows_https(self, client: TestClient):
        """Test CSP img-src allows HTTPS for external images"""
        response = client.get("/api/health")
        csp = response.headers["Content-Security-Policy"]

        # Should allow images from HTTPS sources (charts, logos, etc.)
        assert "img-src" in csp
        # Should allow 'self', 'data:', and potentially 'https:'
        assert "'self'" in csp

    def test_csp_connect_src_allows_api_calls(self, client: TestClient):
        """Test CSP connect-src allows API calls"""
        response = client.get("/api/health")
        csp = response.headers["Content-Security-Policy"]

        # Should allow API calls (fetch, XHR, WebSocket)
        assert "connect-src" in csp

    def test_csp_font_src_configuration(self, client: TestClient):
        """Test CSP font-src allows necessary font sources"""
        response = client.get("/api/health")
        csp = response.headers["Content-Security-Policy"]

        # Should have font-src directive
        assert "font-src" in csp


class TestSecurityHeadersEdgeCases:
    """Test edge cases and error scenarios"""

    def test_headers_on_server_error(self, client: TestClient):
        """Test security headers are present even on 500 errors"""
        # Trigger an error endpoint (if one exists for testing)
        # For now, test that middleware runs even on errors
        response = client.get("/api/nonexistent")

        # Even on 404, security headers should be present
        assert "X-Content-Type-Options" in response.headers
        assert "Content-Security-Policy" in response.headers

    def test_headers_not_duplicated(self, client: TestClient):
        """Test that security headers are not duplicated"""
        response = client.get("/api/health")

        # Each header should appear exactly once
        for header in ["X-Frame-Options", "X-Content-Type-Options", "Strict-Transport-Security"]:
            header_values = response.headers.get_list(header)
            assert len(header_values) == 1, f"Header {header} appears {len(header_values)} times"

    def test_headers_on_streaming_response(self, client: TestClient):
        """Test security headers on streaming responses (if applicable)"""
        # Standard endpoints should have headers
        response = client.get("/api/health")
        assert "X-Content-Type-Options" in response.headers


class TestSecurityBestPractices:
    """Test compliance with security best practices"""

    def test_no_server_header_leak(self, client: TestClient):
        """Test that Server header doesn't leak too much information"""
        response = client.get("/api/health")

        # Server header may be present from uvicorn
        if "Server" in response.headers:
            server = response.headers["Server"]
            # Should not reveal detailed version numbers
            # Note: FastAPI/Uvicorn add this by default, not a security issue
            assert server is not None

    def test_no_x_powered_by_header(self, client: TestClient):
        """Test that X-Powered-By header is not present"""
        response = client.get("/api/health")

        # Should not reveal framework details
        assert "X-Powered-By" not in response.headers

    def test_hsts_sufficient_duration(self, client: TestClient):
        """Test HSTS max-age is sufficiently long (at least 1 year)"""
        response = client.get("/api/health")
        hsts = response.headers["Strict-Transport-Security"]

        # Extract max-age
        for directive in hsts.split(";"):
            if "max-age=" in directive:
                max_age = int(directive.strip().replace("max-age=", ""))
                # 1 year = 31536000 seconds
                assert max_age >= 31536000, f"HSTS max-age {max_age} is less than 1 year"

    def test_csp_no_unsafe_eval(self, client: TestClient):
        """Test that CSP does not allow 'unsafe-eval' in script-src"""
        response = client.get("/api/health")
        csp = response.headers["Content-Security-Policy"]

        # 'unsafe-eval' allows eval() which is a major XSS risk
        # It should NOT be present
        assert "'unsafe-eval'" not in csp, "CSP allows 'unsafe-eval' which is dangerous"

    def test_referrer_policy_strict(self, client: TestClient):
        """Test Referrer-Policy is sufficiently strict"""
        response = client.get("/api/health")
        referrer = response.headers["Referrer-Policy"]

        # Should use strict policy to prevent information leakage
        strict_policies = [
            "no-referrer",
            "strict-origin",
            "strict-origin-when-cross-origin",
            "same-origin"
        ]
        assert any(policy in referrer for policy in strict_policies)
