from datetime import datetime, timedelta

from app.db.session import Base, SessionLocal, engine
from app.market_data.persistence import IntradayBarRepository


def setup_module(_module):
    Base.metadata.create_all(bind=engine)


def teardown_module(_module):
    Base.metadata.drop_all(bind=engine)


def test_record_trade_and_fetch_bars():
    repository = IntradayBarRepository(session_factory=SessionLocal)
    now = datetime.utcnow().replace(second=0, microsecond=0)

    repository.record_trade(symbol="AAPL", price=100.0, size=10, timestamp=now)
    repository.record_trade(symbol="AAPL", price=101.0, size=5, timestamp=now + timedelta(seconds=10))

    bars = repository.get_intraday_bars("AAPL")
    assert len(bars) == 1
    bar = bars[0]
    assert bar.open == 100.0
    assert bar.high == 101.0
    assert bar.low == 100.0
    assert bar.close == 101.0
    assert bar.volume == 15


def test_apply_summary_creates_new_interval():
    repository = IntradayBarRepository(session_factory=SessionLocal)
    now = datetime.utcnow().replace(second=0, microsecond=0)

    repository.apply_summary(
        symbol="MSFT",
        interval="session",
        timestamp=now,
        open_=300.0,
        high=305.0,
        low=299.0,
        close=304.0,
        volume=1200,
    )

    bars = repository.get_intraday_bars("MSFT", interval="session")
    assert len(bars) == 1
    summary = bars[0]
    assert summary.open == 300.0
    assert summary.close == 304.0
    assert summary.volume == 1200
