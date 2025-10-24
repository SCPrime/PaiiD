"""Persistence helpers for market data."""

from __future__ import annotations

from datetime import datetime
from typing import Callable, Iterable, Sequence

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import SessionLocal

from .models import IntradayBar


class IntradayBarRepository:
    """Repository for storing and retrieving intraday bars."""

    def __init__(self, session_factory: Callable[[], Session] = SessionLocal):
        self._session_factory = session_factory

    def _session(self) -> Session:
        return self._session_factory()

    def record_trade(
        self,
        *,
        symbol: str,
        price: float | None,
        size: float | None,
        timestamp: datetime,
        interval: str = "1min",
    ) -> None:
        """Insert or update the bar that matches the trade timestamp."""

        if price is None:
            return

        normalized = symbol.upper()
        bucket = timestamp.replace(second=0, microsecond=0)
        session = self._session()
        try:
            bar = (
                session.query(IntradayBar)
                .filter_by(symbol=normalized, interval=interval, timestamp=bucket)
                .one_or_none()
            )

            if bar is None:
                bar = IntradayBar(
                    symbol=normalized,
                    interval=interval,
                    timestamp=bucket,
                    open=price,
                    high=price,
                    low=price,
                    close=price,
                    volume=size or 0,
                )
                session.add(bar)
            else:
                bar.update_from_trade(price, size)

            session.commit()
        except IntegrityError:
            session.rollback()
        finally:
            session.close()

    def apply_summary(
        self,
        *,
        symbol: str,
        interval: str,
        timestamp: datetime,
        open_: float | None = None,
        high: float | None = None,
        low: float | None = None,
        close: float | None = None,
        volume: float | None = None,
    ) -> None:
        """Persist summary information for an interval bucket."""

        normalized = symbol.upper()
        bucket = timestamp.replace(second=0, microsecond=0)
        session = self._session()
        try:
            bar = (
                session.query(IntradayBar)
                .filter_by(symbol=normalized, interval=interval, timestamp=bucket)
                .one_or_none()
            )

            if bar is None:
                bar = IntradayBar(
                    symbol=normalized,
                    interval=interval,
                    timestamp=bucket,
                    open=open_ or 0,
                    high=high or open_ or 0,
                    low=low or open_ or 0,
                    close=close or open_ or 0,
                    volume=volume or 0,
                )
                session.add(bar)
            else:
                bar.apply_summary(
                    open_=open_,
                    high=high,
                    low=low,
                    close=close,
                    volume=volume,
                )

            session.commit()
        except IntegrityError:
            session.rollback()
        finally:
            session.close()

    def get_intraday_bars(
        self,
        symbol: str,
        *,
        interval: str = "1min",
        limit: int = 100,
    ) -> Sequence[IntradayBar]:
        """Return most recent bars for the requested symbol."""

        session = self._session()
        try:
            query = (
                session.query(IntradayBar)
                .filter_by(symbol=symbol.upper(), interval=interval)
                .order_by(IntradayBar.timestamp.desc())
                .limit(limit)
            )
            return list(reversed(query.all()))
        finally:
            session.close()

    def bulk_insert(self, bars: Iterable[IntradayBar]) -> None:
        """Persist a collection of bars (used for backfilling tests)."""

        session = self._session()
        try:
            session.bulk_save_objects(list(bars))
            session.commit()
        finally:
            session.close()
