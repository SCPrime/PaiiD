import os
import requests
import sys


"""
Test script for the new /api/ai/analyze-positions endpoint
"""

# Backend URL
BASE_URL = "http://127.0.0.1:8001"

# API token from environment variable
API_TOKEN = os.getenv("API_TOKEN")
if not API_TOKEN:
    print("ERROR: API_TOKEN environment variable not set")
    print("Please set API_TOKEN in your .env file or export it")
    sys.exit(1)

headers = {"Authorization": f"Bearer {API_TOKEN}", "Content-Type": "application/json"}

def test_analyze_positions():
    """Test the analyze-positions endpoint"""
    print("\n" + "=" * 80)
    print("Testing POST /api/ai/analyze-positions")
    print("=" * 80)

    # Request body
    request_body = {
        "include_technicals": True,
        "include_sentiment": False,
        "timeframe": "1-2 weeks",
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/ai/analyze-positions", headers=headers, json=request_body, timeout=30
        )

        print(f"\nStatus Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("\n[SUCCESS] Response received:")
            print("\nPortfolio Summary:")
            print(f"  - Total Positions: {data['portfolio_summary']['total_positions']}")
            print(f"  - Total Value: ${data['portfolio_summary']['total_value']:,.2f}")
            print(f"  - Total P/L: ${data['portfolio_summary'].get('total_unrealized_pl', 0):,.2f}")
            print(f"  - Risk Score: {data['overall_risk_score']}/10")
            print(f"  - Diversification Score: {data['diversification_score']}/10")

            print("\nPortfolio Recommendations:")
            for rec in data["portfolio_recommendations"]:
                print(f"  - {rec}")

            print(f"\nIndividual Positions ({len(data['positions'])}):")
            for pos in data["positions"][:3]:  # Show first 3
                print(f"\n  {pos['symbol']}:")
                print(f"    Qty: {pos['quantity']}, Current: ${pos['current_price']:.2f}")
                print(f"    P/L: {pos['unrealized_pl_percent']:+.1f}%")
                print(
                    f"    Recommendation: {pos['recommendation']} ({pos['recommendation_confidence']:.0f}% confidence)"
                )
                print(f"    Trend: {pos['trend']}, Momentum: {pos['momentum']}")
                print(f"    Outlook: {pos['short_term_outlook'][:80]}...")

            if len(data["positions"]) > 3:
                print(f"\n  ... and {len(data['positions']) - 3} more positions")

            print("\n[OK] Test PASSED")
            return True

        else:
            print(f"\n[ERROR] Status {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"\n[ERROR] EXCEPTION: {e!s}")
        return False

def test_endpoint_exists():
    """Test that the endpoint is registered"""
    print("\n" + "=" * 80)
    print("Testing endpoint registration")
    print("=" * 80)

    try:
        # FastAPI automatically generates /docs
        response = requests.get(f"{BASE_URL}/docs")

        if response.status_code == 200:
            print("\n[OK] Backend is running and serving docs")
            print(f"   Docs URL: {BASE_URL}/docs")
            return True
        else:
            print(f"\n[WARN] Backend may not be fully ready (status {response.status_code})")
            return False

    except Exception as e:
        print(f"\n[ERROR] Cannot connect to backend: {e!s}")
        return False

if __name__ == "__main__":
    print("\n[TEST] Testing ActivePositions AI Analysis Endpoint")
    print(f"Backend: {BASE_URL}")

    # Test 1: Check backend is running
    if not test_endpoint_exists():
        print("\n[ERROR] Backend is not running on port 8001")
        print("   Start with: cd backend && python -m uvicorn app.main:app --reload --port 8001")
        exit(1)

    # Test 2: Test the analyze-positions endpoint
    success = test_analyze_positions()

    print("\n" + "=" * 80)
    if success:
        print("[SUCCESS] All tests PASSED!")
    else:
        print("[ERROR] Some tests FAILED - check output above")
    print("=" * 80 + "\n")
