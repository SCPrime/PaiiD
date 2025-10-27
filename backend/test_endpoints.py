"""Test script for debugging endpoint failures"""
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

# Test imports first
print("=" * 60)
print("TESTING ENDPOINT DEPENDENCIES")
print("=" * 60)

# Test 1: Account endpoint
print("\n1. Testing Tradier Account Endpoint...")
try:
    from app.services.tradier_client import get_tradier_client
    client = get_tradier_client()
    print(f"[OK] Tradier client initialized")
    print(f"   Account ID: {client.account_id}")

    # Try get_account
    account_data = client.get_account()
    print(f"[OK] Account data retrieved")
    print(f"   Portfolio Value: ${account_data.get('portfolio_value', 0):,.2f}")
    print(f"   Buying Power: ${account_data.get('buying_power', 0):,.2f}")
except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Market quote endpoint
print("\n2. Testing Market Quote Endpoint...")
try:
    from app.services.tradier_client import get_tradier_client
    client = get_tradier_client()

    quotes = client.get_quotes(["AAPL", "SPY", "TSLA"])
    print(f"[OK] Quotes retrieved: {quotes}")

    # Parse response
    if "quotes" in quotes:
        quote_data = quotes["quotes"].get("quote", [])
        if isinstance(quote_data, list):
            print(f"   Retrieved {len(quote_data)} quotes")
            for q in quote_data:
                symbol = q.get("symbol", "?")
                last = q.get("last", 0)
                print(f"   {symbol}: ${last}")
        elif isinstance(quote_data, dict):
            symbol = quote_data.get("symbol", "?")
            last = quote_data.get("last", 0)
            print(f"   {symbol}: ${last}")
    else:
        print(f"   Raw response keys: {quotes.keys()}")

except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# Test 3: News endpoint
print("\n3. Testing News Endpoint...")
try:
    from datetime import datetime, timezone

    # Test datetime operations
    current_time = datetime.now(timezone.utc)
    print(f"[OK] Current time (UTC): {current_time}")

    # Try importing news aggregator
    try:
        from app.services.news.news_aggregator import NewsAggregator
        news_agg = NewsAggregator()
        print(f"[OK] News aggregator initialized")

        # Try getting news
        articles = news_agg.get_company_news("SPY", days_back=7)
        print(f"[OK] Retrieved {len(articles)} articles")

        # Check for datetime issues
        for article in articles[:3]:
            pub_date = article.get("published_date")
            print(f"   Article date: {pub_date} (type: {type(pub_date)})")

    except Exception as e2:
        print(f"[WARNING] News aggregator error: {e2}")
        import traceback
        traceback.print_exc()

except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)
