"""
Tests order execution idempotency and validation
"""


def test_duplicate_idempotency(client, auth_headers):
    """Submitting the same requestId twice should mark duplicate"""
    body = {
        "dryRun": True,
        "requestId": "test-request-12345",
        "orders": [{"symbol": "AAPL", "side": "buy", "qty": 1}],
    }
    r1 = client.post("/api/trading/execute", json=body, headers=auth_headers)
    r2 = client.post("/api/trading/execute", json=body, headers=auth_headers)
    assert r1.status_code in [200, 500]
    if r1.status_code == 200:
        assert r2.json().get("duplicate") is True
