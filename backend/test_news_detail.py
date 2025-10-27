"""Test news endpoint in detail"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

from app.services.news.news_aggregator import NewsAggregator
import json

news_agg = NewsAggregator()
articles = news_agg.get_company_news("SPY", days_back=7)

print(f"Retrieved {len(articles)} articles\n")
print("=" * 60)

# Check first 3 articles
for i, article in enumerate(articles[:3], 1):
    print(f"\nArticle {i}:")
    print(f"  Keys: {list(article.keys())}")
    print(f"  Title: {article.get('title', 'N/A')[:50]}...")
    print(f"  published_at: {article.get('published_at')}")
    print(f"  published_date: {article.get('published_date')}")
    print(f"  provider: {article.get('provider')}")
    print()

# Pretty print first article
if articles:
    print("\n" + "=" * 60)
    print("First article (full):")
    print(json.dumps(articles[0], indent=2, default=str))
