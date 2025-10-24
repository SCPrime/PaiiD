#!/usr/bin/env python3
"""
Phase 1 Options Trading - End-to-End Verification Test
Tests backend endpoints and validates Greeks data
"""

import requests
import json
import sys

# Configuration
BACKEND_URL = "http://localhost:8001"
TOKEN = "tuGlKvrYEoiJcv7r7oIy7zXM9pqVnaxN_74obFz6lVo"
TEST_SYMBOL = "SPY"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_endpoint(name, url, expected_keys=None):
    """Test a single endpoint"""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"URL: {url}")
    print(f"{'='*60}")

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code != 200:
            print(f"❌ FAILED: {response.text}")
            return False

        data = response.json()
        print(f"Response Type: {type(data)}")

        if isinstance(data, dict):
            print(f"Keys: {list(data.keys())}")
            if expected_keys:
                missing = [k for k in expected_keys if k not in data]
                if missing:
                    print(f"❌ MISSING KEYS: {missing}")
                    return False
        elif isinstance(data, list):
            print(f"Items: {len(data)}")
            if data and isinstance(data[0], dict):
                print(f"First Item Keys: {list(data[0].keys())}")

        print("✅ PASSED")
        return True

    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False

def test_greeks_presence(chain_data):
    """Verify Greeks are present in options data"""
    print(f"\n{'='*60}")
    print("TEST: Greeks Validation")
    print(f"{'='*60}")

    greeks = ["delta", "gamma", "theta", "vega", "rho"]

    if not chain_data.get("calls"):
        print("❌ No calls found")
        return False

    sample_call = chain_data["calls"][0]
    print(f"Sample Call: {sample_call['symbol']}")
    print(f"Strike: ${sample_call['strike_price']}")

    missing_greeks = []
    for greek in greeks:
        value = sample_call.get(greek)
        if value is None:
            missing_greeks.append(greek)
        else:
            print(f"  {greek.capitalize()}: {value:.4f}")

    if missing_greeks:
        print(f"❌ MISSING GREEKS: {missing_greeks}")
        return False

    print("✅ All Greeks present")
    return True

def main():
    """Run all tests"""
    print(f"\n{'#'*60}")
    print("PHASE 1 OPTIONS TRADING - VERIFICATION TEST")
    print(f"{'#'*60}")

    results = []

    # Test 1: Health Check
    results.append(test_endpoint(
        "Backend Health Check",
        f"{BACKEND_URL}/api/health"
    ))

    # Test 2: Expirations Endpoint
    results.append(test_endpoint(
        f"Expirations for {TEST_SYMBOL}",
        f"{BACKEND_URL}/api/options/expirations/{TEST_SYMBOL}",
        expected_keys=None  # Returns list
    ))

    # Test 3: Options Chain Endpoint
    expirations_response = requests.get(
        f"{BACKEND_URL}/api/options/expirations/{TEST_SYMBOL}",
        headers=HEADERS
    )
    expirations = expirations_response.json()

    if expirations:
        test_expiration = expirations[0]["date"]
        chain_response = requests.get(
            f"{BACKEND_URL}/api/options/chain/{TEST_SYMBOL}?expiration={test_expiration}",
            headers=HEADERS
        )

        if chain_response.status_code == 200:
            chain_data = chain_response.json()

            results.append(test_endpoint(
                f"Options Chain for {TEST_SYMBOL} {test_expiration}",
                f"{BACKEND_URL}/api/options/chain/{TEST_SYMBOL}?expiration={test_expiration}",
                expected_keys=["symbol", "expiration_date", "calls", "puts", "total_contracts"]
            ))

            # Test 4: Greeks Validation
            results.append(test_greeks_presence(chain_data))

            # Print Summary Stats
            print(f"\n{'='*60}")
            print("SUMMARY STATISTICS")
            print(f"{'='*60}")
            print(f"Symbol: {chain_data['symbol']}")
            print(f"Expiration: {chain_data['expiration_date']}")
            print(f"Total Contracts: {chain_data['total_contracts']}")
            print(f"Calls: {len(chain_data['calls'])}")
            print(f"Puts: {len(chain_data['puts'])}")
        else:
            results.append(False)

    # Final Results
    print(f"\n{'#'*60}")
    print("FINAL RESULTS")
    print(f"{'#'*60}")

    passed = sum(results)
    total = len(results)

    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")

    if all(results):
        print("\n🎉 ALL TESTS PASSED - PHASE 1 COMPLETE")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED - REVIEW REQUIRED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
