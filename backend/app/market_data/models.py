"""SQLAlchemy models for market data persistence."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, UniqueConstraint

from app.db.session import Base


class IntradayBar(Base):
    """Aggregated intraday bar data generated from streaming trades."""

    __tablename__ = "intraday_bars"
    __table_args__ = (
        UniqueConstraint("symbol", "interval", "timestamp", name="uq_intraday_bars_symbol_interval_timestamp"),
    )

    id = Column(Integer, primary_key=True)
    symbol = Column(String(32), index=True, nullable=False)
    interval = Column(String(16), index=True, nullable=False, default="1min")
    timestamp = Column(DateTime, index=True, nullable=False, default=datetime.utcnow)

    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False, default=0)

    def update_from_trade(self, price: float, size: float | None = None) -> None:
        """Update OHLCV values using a new trade print."""

        if price > self.high:
            self.high = price
        if price < self.low:
            self.low = price

        self.close = price
        if self.open == 0:
            self.open = price

        if size:
            self.volume += size

    def apply_summary(
        self,
        *,
        open_: float | None = None,
        high: float | None = None,
        low: float | None = None,
        close: float | None = None,
        volume: float | None = None,
    ) -> None:
        """Apply summary statistics to the bar."""

        if open_ is not None:
            self.open = open_
        if high is not None:
            self.high = max(self.high, high) if self.high else high
        if low is not None:
            self.low = min(self.low, low) if self.low else low
        if close is not None:
            self.close = close
        if volume is not None:
            self.volume = max(self.volume, volume)
