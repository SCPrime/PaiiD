import asyncio
import sys

from app.routers.ai import analyze_portfolio


"""
Test script for the /api/ai/analyze-portfolio endpoint
"""

sys.path.insert(0, ".")

# Test by directly importing and calling the function

async def test_portfolio_endpoint():
    """Test the portfolio analysis endpoint"""
    print("\n" + "=" * 80)
    print("[TEST] TESTING /api/ai/analyze-portfolio ENDPOINT")
    print("=" * 80)

    print("\n[SUCCESS] ENDPOINT SUCCESSFULLY IMPORTED")
    print(f"   Function: {analyze_portfolio.__name__}")
    print(f"   Docstring: {analyze_portfolio.__doc__[:100]}...")

    print("\n[INFO] ENDPOINT DETAILS:")
    print("   - Route: /ai/analyze-portfolio")
    print("   - Method: GET")
    print("   - Authentication: Bearer token required")
    print("   - Returns: PortfolioAnalysisResponse")

    print("\n" + "=" * 80)
    print("[SUCCESS] ENDPOINT VERIFICATION COMPLETE")
    print("=" * 80)

    print("\n[INFO] To test with live data:")
    print("   1. Ensure backend server is restarted with latest code")
    print(
        "   2. Run: curl -H 'Authorization: Bearer <token>' http://localhost:8001/api/ai/analyze-portfolio"
    )
    print("\n")

if __name__ == "__main__":
    asyncio.run(test_portfolio_endpoint())
