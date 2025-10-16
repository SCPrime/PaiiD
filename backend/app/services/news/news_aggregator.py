from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from difflib import SequenceMatcher
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
import logging

from .finnhub_provider import FinnhubProvider
from .alpha_vantage_provider import AlphaVantageProvider
from .polygon_provider import PolygonProvider
from .base_provider import NewsArticle

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """
    Circuit breaker pattern to prevent hammering failed providers.

    States:
    - CLOSED: Normal operation, allows requests
    - OPEN: Provider is failing, blocks requests for cooldown period
    - HALF_OPEN: Testing if provider recovered
    """

    def __init__(self, failure_threshold: int = 3, cooldown_seconds: int = 60):
        """
        Initialize circuit breaker

        Args:
            failure_threshold: Number of consecutive failures before opening circuit
            cooldown_seconds: How long to wait before testing provider again
        """
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN

    def record_success(self):
        """Record successful call - reset circuit"""
        self.failure_count = 0
        self.state = 'CLOSED'
        self.last_failure_time = None

    def record_failure(self):
        """Record failed call - increment counter and potentially open circuit"""
        # If we're in HALF_OPEN, reset count to allow gradual recovery
        if self.state == 'HALF_OPEN':
            self.failure_count = 1  # Gradual recovery: start with 1 failure instead of keeping full count
            logger.info(f"[Circuit Breaker] HALF_OPEN test failed - resetting to 1 failure for gradual recovery")
        else:
            self.failure_count += 1

        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
            logger.warning(
                f"[Circuit Breaker] OPENED after {self.failure_count} failures. "
                f"Cooldown: {self.cooldown_seconds}s"
            )

    def is_available(self) -> bool:
        """Check if requests should be allowed"""
        if self.state == 'CLOSED':
            return True

        if self.state == 'OPEN':
            # Check if cooldown period has elapsed
            if self.last_failure_time:
                elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                if elapsed >= self.cooldown_seconds:
                    # Move to HALF_OPEN to test provider
                    self.state = 'HALF_OPEN'
                    logger.info(f"[Circuit Breaker] HALF_OPEN - testing provider")
                    return True
            return False

        # HALF_OPEN state - allow one test request
        return True

    def get_state(self) -> Dict[str, Any]:
        """Get circuit breaker status"""
        return {
            'state': self.state,
            'failure_count': self.failure_count,
            'last_failure': self.last_failure_time.isoformat() if self.last_failure_time else None
        }


class NewsAggregator:
    def __init__(self):
        self.providers = []
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}

        # Try to initialize each provider (fail gracefully if API key missing)
        try:
            provider = FinnhubProvider()
            self.providers.append(provider)
            self.circuit_breakers[provider.get_provider_name()] = CircuitBreaker(
                failure_threshold=3,
                cooldown_seconds=30  # Tuned: 60s→30s for faster recovery
            )
            logger.info("[OK] Finnhub provider initialized")
        except Exception as e:
            logger.warning(f"[WARNING] Finnhub provider skipped: {e}")

        try:
            provider = AlphaVantageProvider()
            self.providers.append(provider)
            self.circuit_breakers[provider.get_provider_name()] = CircuitBreaker(
                failure_threshold=3,
                cooldown_seconds=30  # Tuned: 60s→30s for faster recovery
            )
            logger.info("[OK] Alpha Vantage provider initialized")
        except Exception as e:
            logger.warning(f"[WARNING] Alpha Vantage provider skipped: {e}")

        try:
            provider = PolygonProvider()
            self.providers.append(provider)
            self.circuit_breakers[provider.get_provider_name()] = CircuitBreaker(
                failure_threshold=3,
                cooldown_seconds=30  # Tuned: 60s→30s for faster recovery
            )
            logger.info("[OK] Polygon provider initialized")
        except Exception as e:
            logger.warning(f"[WARNING] Polygon provider skipped: {e}")

        if not self.providers:
            raise ValueError("No news providers available - check API keys!")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def _call_provider_with_retry(
        self,
        provider,
        method_name: str,
        *args,
        **kwargs
    ) -> List[NewsArticle]:
        """
        Call provider method with retry logic and circuit breaker

        Args:
            provider: News provider instance
            method_name: Method to call ('get_company_news' or 'get_market_news')
            *args, **kwargs: Arguments to pass to provider method

        Returns:
            List of NewsArticle objects

        Raises:
            Exception: If all retries fail or circuit breaker is open
        """
        provider_name = provider.get_provider_name()
        breaker = self.circuit_breakers.get(provider_name)

        # Check circuit breaker
        if breaker and not breaker.is_available():
            logger.warning(
                f"[Circuit Breaker] {provider_name} circuit is OPEN - skipping"
            )
            return []

        try:
            # Call provider method
            method = getattr(provider, method_name)
            articles = method(*args, **kwargs)

            # Success - reset circuit breaker
            if breaker:
                breaker.record_success()

            logger.info(f"[OK] {provider_name}: {len(articles)} articles")
            return articles

        except Exception as e:
            # Record failure in circuit breaker
            if breaker:
                breaker.record_failure()

            logger.error(
                f"[ERROR] {provider_name} failed: {e} "
                f"(Circuit: {breaker.state if breaker else 'N/A'})"
            )

            # Re-raise for retry logic (if retryable exception)
            if isinstance(e, (ConnectionError, TimeoutError)):
                raise
            # For non-retryable errors, return empty list
            return []

    def get_company_news(self, symbol: str, days_back: int = 7) -> List[Dict[str, Any]]:
        """
        Aggregate news from all providers for a specific company.

        Uses retry logic with exponential backoff and circuit breaker pattern
        to ensure high availability even when individual providers fail.

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            days_back: How many days of historical news to fetch

        Returns:
            List of deduplicated and aggregated news articles
        """
        all_articles = []

        # Try each provider with retry logic and circuit breaker
        for provider in self.providers:
            articles = self._call_provider_with_retry(
                provider,
                'get_company_news',
                symbol,
                days_back
            )
            all_articles.extend(articles)

        # If no articles found from any provider, return empty list
        if not all_articles:
            logger.warning(f"[NEWS] No articles found for {symbol} from any provider")
            return []

        # Deduplicate
        deduplicated = self._deduplicate(all_articles)

        # Aggregate sentiment
        aggregated = self._aggregate_sentiment(deduplicated)

        # Sort by date
        aggregated.sort(key=lambda x: x.published_at, reverse=True)

        logger.info(
            f"[NEWS] {symbol}: {len(all_articles)} articles -> {len(aggregated)} unique "
            f"(providers: {len([p for p in self.providers if self.circuit_breakers.get(p.get_provider_name(), CircuitBreaker()).state != 'OPEN'])} active)"
        )

        return [article.to_dict() for article in aggregated]

    def get_market_news(self, category: str = 'general', limit: int = 50) -> List[Dict[str, Any]]:
        """
        Aggregate market news from all providers.

        Uses retry logic with exponential backoff and circuit breaker pattern
        to ensure high availability even when individual providers fail.

        Args:
            category: News category (e.g., 'general', 'forex', 'crypto')
            limit: Maximum number of articles to return

        Returns:
            List of deduplicated, aggregated, and prioritized news articles
        """
        all_articles = []

        # Try each provider with retry logic and circuit breaker
        for provider in self.providers:
            articles = self._call_provider_with_retry(
                provider,
                'get_market_news',
                category
            )
            all_articles.extend(articles)

        # If no articles found from any provider, return empty list
        if not all_articles:
            logger.warning(f"[NEWS] No market news found from any provider")
            return []

        # Deduplicate
        deduplicated = self._deduplicate(all_articles)

        # Aggregate sentiment
        aggregated = self._aggregate_sentiment(deduplicated)

        # Prioritize
        aggregated = self._prioritize(aggregated)

        active_providers = len([
            p for p in self.providers
            if self.circuit_breakers.get(p.get_provider_name(), CircuitBreaker()).state != 'OPEN'
        ])

        logger.info(
            f"[NEWS] Market: {len(all_articles)} articles -> {len(aggregated)} unique "
            f"(providers: {active_providers}/{len(self.providers)} active)"
        )

        return [article.to_dict() for article in aggregated[:limit]]

    def _deduplicate(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """Remove duplicate articles based on title similarity"""
        if not articles:
            return []

        groups = []
        used = set()

        for i, article in enumerate(articles):
            if i in used:
                continue

            group = [article]
            used.add(i)

            for j, other in enumerate(articles[i+1:], start=i+1):
                if j in used:
                    continue

                similarity = SequenceMatcher(None, article.title.lower(), other.title.lower()).ratio()

                if similarity > 0.85:
                    group.append(other)
                    used.add(j)

            groups.append(group)

        deduplicated = []
        for group in groups:
            best = max(group, key=lambda x: (
                abs(x.sentiment_score),
                len(x.summary),
                x.published_at
            ))
            deduplicated.append(best)

        return deduplicated

    def _aggregate_sentiment(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """Average sentiment scores from multiple sources"""
        url_groups = defaultdict(list)
        for article in articles:
            url_groups[article.url].append(article)

        aggregated = []
        for url, group in url_groups.items():
            if len(group) == 1:
                aggregated.append(group[0])
            else:
                avg_score = sum(a.sentiment_score for a in group) / len(group)
                best = max(group, key=lambda x: len(x.summary))
                best.sentiment_score = avg_score
                best.sentiment = self._score_to_label(avg_score)
                best.provider = ', '.join(set(a.provider for a in group))
                aggregated.append(best)

        return aggregated

    def _score_to_label(self, score: float) -> str:
        if score > 0.2:
            return 'bullish'
        elif score < -0.2:
            return 'bearish'
        else:
            return 'neutral'

    def _prioritize(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """Sort by importance"""
        def priority_score(article: NewsArticle) -> float:
            score = 0.0

            try:
                age_hours = (datetime.now() - datetime.fromisoformat(article.published_at.replace('Z', '+00:00'))).total_seconds() / 3600
                score += max(0, 100 - age_hours)
            except:
                pass

            score += abs(article.sentiment_score) * 50

            if ',' in article.provider:
                score += 30

            score += min(len(article.summary) / 10, 20)

            return score

        articles.sort(key=priority_score, reverse=True)
        return articles

    def get_provider_health(self) -> Dict[str, Any]:
        """
        Get health status of all news providers for observability

        Returns:
            Dictionary with provider health information including circuit breaker states
        """
        health_status = {
            'total_providers': len(self.providers),
            'providers': []
        }

        for provider in self.providers:
            provider_name = provider.get_provider_name()
            breaker = self.circuit_breakers.get(provider_name)

            provider_info = {
                'name': provider_name,
                'status': 'healthy' if (breaker and breaker.state == 'CLOSED') else 'degraded' if (breaker and breaker.state == 'HALF_OPEN') else 'down',
                'circuit_breaker': breaker.get_state() if breaker else None
            }

            health_status['providers'].append(provider_info)

        # Calculate overall health
        active_count = sum(1 for p in health_status['providers'] if p['status'] == 'healthy')
        degraded_count = sum(1 for p in health_status['providers'] if p['status'] == 'degraded')
        down_count = sum(1 for p in health_status['providers'] if p['status'] == 'down')

        health_status['summary'] = {
            'active': active_count,
            'degraded': degraded_count,
            'down': down_count,
            'health_percentage': (active_count / len(self.providers) * 100) if self.providers else 0
        }

        return health_status
