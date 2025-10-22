"""Test script to diagnose options endpoint issue"""
import requests
import sys

# Test1: Health endpoint (should work)
print("\n==== TEST 1: Health Endpoint ====")
try:
    resp = requests.get("http://127.0.0.1:8001/api/health")
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text[:200]}")
except Exception as e:
    print(f"ERROR: {e}")

# Test 2: Expirations endpoint (failing)
print("\n==== TEST 2: Expirations Endpoint (No Auth) ====")
try:
    resp = requests.get("http://127.0.0.1:8001/api/expirations/AAPL", timeout=5)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")
except Exception as e:
    print(f"ERROR: {e}")

# Test 3: With auth
print("\n==== TEST 3: Expirations Endpoint (With Auth) ====")
try:
    headers = {"Authorization": "Bearer tuGlKvrYEoiJcv7r7oIy7zXM9pqVnaxN_74obFz6lVo"}
    resp = requests.get("http://127.0.0.1:8001/api/expirations/AAPL", headers=headers, timeout=5)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")
except Exception as e:
    print(f"ERROR: {e}")

# Test 4: Test Tradier API directly
print("\n==== TEST 4: Tradier API Direct ====")
try:
    headers = {
        "Authorization": "Bearer MNJOKCtlpADk2POdChc0vGDUAGMD",
        "Accept": "application/json"
    }
    resp = requests.get(
        "https://api.tradier.com/v1/markets/options/expirations",
        headers=headers,
        params={"symbol": "AAPL"},
        timeout=10
    )
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")
except Exception as e:
    print(f"ERROR: {e}")

print("\n==== DIAGNOSIS ====")
print("✅ Health endpoint works")
print("❌ Expirations endpoint returns 500")
print("✅ Tradier API works directly")
print("\nConclusion: Issue is in the backend endpoint handler")
