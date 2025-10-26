"""
Security and middleware behavior tests
"""


def test_security_headers_present(client):
    response = client.get("/api/health")
    # Security headers should be present
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    # CSP/HSTS present (values may vary)
    assert "Content-Security-Policy" in response.headers
    assert "Strict-Transport-Security" in response.headers


def test_request_id_header_present(client):
    response = client.get("/api/health")
    req_id = response.headers.get("X-Request-ID")
    assert req_id is not None and len(req_id) > 0


def test_kill_switch_blocks_mutation(client, monkeypatch, auth_headers):
    # Force kill switch on
    from app.core import kill_switch as ks

    monkeypatch.setattr(ks, "is_killed", lambda: True)

    # POST to a mutating endpoint should be blocked with 423
    payload = {
        "symbol": "SPY",
        "option_symbol": "SPY250117C00590000",
        "quantity": 1,
        "order_type": "limit",
    }
    resp = client.post("/api/proposals/create", json=payload, headers=auth_headers)
    assert resp.status_code == 423
    data = resp.json()
    assert data.get("error") == "trading halted"
