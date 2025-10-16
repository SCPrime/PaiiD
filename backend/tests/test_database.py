"""
Database Model Tests

Tests for SQLAlchemy models: User, Strategy, Trade, Performance, EquitySnapshot
"""

from datetime import datetime

import pytest

from app.models.database import EquitySnapshot, Performance, Strategy, Trade, User

# Test password hash (matches TEST_PASSWORD_HASH from conftest.py)
# Pre-computed bcrypt hash for "TestPassword123!"
TEST_PASSWORD_HASH = "$2b$12$LQ3JzqjX7Y8ZHnVc9r5MHOfWw8L4vQy8QWxK0X1y0HdTYJKRQ6qKK"


class TestUserModel:
    """Test User model CRUD operations and relationships"""

    def test_create_user(self, test_db):
        """Test creating a new user"""
        user = User(
            email="user@example.com",
            password_hash=TEST_PASSWORD_HASH,
            alpaca_account_id="ACCOUNT123",
            preferences={"risk_tolerance": "moderate", "position_size": 0.02},
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        assert user.id is not None
        assert user.email == "user@example.com"
        assert user.alpaca_account_id == "ACCOUNT123"
        assert user.preferences["risk_tolerance"] == "moderate"
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_user_without_email(self, test_db):
        """Test creating user with minimal required fields"""
        user = User(email="minimal@example.com", password_hash=TEST_PASSWORD_HASH, preferences={})
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        assert user.id is not None
        assert user.email == "minimal@example.com"

    def test_user_unique_email(self, test_db):
        """Test email uniqueness constraint"""
        user1 = User(email="same@example.com", password_hash=TEST_PASSWORD_HASH, preferences={})
        test_db.add(user1)
        test_db.commit()

        user2 = User(email="same@example.com", password_hash=TEST_PASSWORD_HASH, preferences={})
        test_db.add(user2)

        with pytest.raises(Exception):  # IntegrityError
            test_db.commit()

    def test_user_strategies_relationship(self, test_db, sample_user):
        """Test User → Strategy relationship"""
        strategy = Strategy(
            user_id=sample_user.id,
            name="Test Strategy",
            description="Test",
            strategy_type="momentum",
            config={},
        )
        test_db.add(strategy)
        test_db.commit()

        # Refresh to load relationships
        test_db.refresh(sample_user)

        assert len(sample_user.strategies) == 1
        assert sample_user.strategies[0].name == "Test Strategy"

    def test_user_cascade_delete(self, test_db, sample_user, sample_strategy):
        """Test cascade delete (deleting user deletes strategies)"""
        user_id = sample_user.id
        strategy_id = sample_strategy.id

        test_db.delete(sample_user)
        test_db.commit()

        # Strategy should be deleted too
        assert test_db.query(Strategy).filter_by(id=strategy_id).first() is None


class TestStrategyModel:
    """Test Strategy model CRUD operations"""

    def test_create_strategy(self, test_db, sample_user):
        """Test creating a new strategy"""
        strategy = Strategy(
            user_id=sample_user.id,
            name="Mean Reversion",
            description="Buy oversold stocks",
            strategy_type="mean_reversion",
            config={"entry_rules": ["RSI < 30"], "exit_rules": ["RSI > 70"], "lookback_period": 14},
            is_active=True,
            is_autopilot=False,
        )
        test_db.add(strategy)
        test_db.commit()
        test_db.refresh(strategy)

        assert strategy.id is not None
        assert strategy.name == "Mean Reversion"
        assert strategy.strategy_type == "mean_reversion"
        assert strategy.config["lookback_period"] == 14
        assert strategy.is_active is True
        assert strategy.created_at is not None

    def test_strategy_without_user(self, test_db):
        """Test creating strategy without user (nullable foreign key)"""
        strategy = Strategy(
            name="System Strategy",
            description="Built-in strategy",
            strategy_type="trend_following",
            config={},
        )
        test_db.add(strategy)
        test_db.commit()
        test_db.refresh(strategy)

        assert strategy.user_id is None

    def test_update_strategy_performance(self, test_db, sample_strategy):
        """Test updating strategy performance metrics"""
        sample_strategy.total_trades = 25
        sample_strategy.win_rate = 0.68
        sample_strategy.sharpe_ratio = 1.45
        sample_strategy.max_drawdown = -0.08

        test_db.commit()
        test_db.refresh(sample_strategy)

        assert sample_strategy.total_trades == 25
        assert sample_strategy.win_rate == 0.68
        assert sample_strategy.sharpe_ratio == 1.45

    def test_strategy_last_backtest_timestamp(self, test_db, sample_strategy):
        """Test updating last backtest timestamp"""
        now = datetime.utcnow()
        sample_strategy.last_backtest_at = now

        test_db.commit()
        test_db.refresh(sample_strategy)

        assert sample_strategy.last_backtest_at == now


class TestTradeModel:
    """Test Trade model CRUD operations"""

    def test_create_trade(self, test_db, sample_user, sample_strategy):
        """Test creating a new trade"""
        trade = Trade(
            user_id=sample_user.id,
            strategy_id=sample_strategy.id,
            symbol="TSLA",
            side="buy",
            quantity=5,
            price=245.30,
            order_type="limit",
            limit_price=245.00,
            status="pending",
        )
        test_db.add(trade)
        test_db.commit()
        test_db.refresh(trade)

        assert trade.id is not None
        assert trade.symbol == "TSLA"
        assert trade.side == "buy"
        assert trade.quantity == 5
        assert trade.limit_price == 245.00
        assert trade.status == "pending"

    def test_trade_fill_execution(self, test_db, sample_trade):
        """Test updating trade to filled status"""
        sample_trade.status = "filled"
        sample_trade.filled_quantity = 10
        sample_trade.filled_avg_price = 150.55
        sample_trade.filled_at = datetime.utcnow()

        test_db.commit()
        test_db.refresh(sample_trade)

        assert sample_trade.status == "filled"
        assert sample_trade.filled_quantity == 10
        assert sample_trade.filled_at is not None

    def test_trade_pnl_calculation(self, test_db, sample_trade):
        """Test P&L tracking"""
        sample_trade.pnl = 50.00  # $5/share profit on 10 shares
        sample_trade.pnl_percent = 3.32

        test_db.commit()
        test_db.refresh(sample_trade)

        assert sample_trade.pnl == 50.00
        assert sample_trade.pnl_percent == 3.32

    def test_trade_broker_order_id_unique(self, test_db, sample_user):
        """Test broker order ID uniqueness"""
        trade1 = Trade(
            user_id=sample_user.id,
            symbol="AAPL",
            side="buy",
            quantity=1,
            price=150,
            order_type="market",
            broker_order_id="ORDER123",
            status="filled",
        )
        test_db.add(trade1)
        test_db.commit()

        trade2 = Trade(
            user_id=sample_user.id,
            symbol="MSFT",
            side="buy",
            quantity=1,
            price=380,
            order_type="market",
            broker_order_id="ORDER123",  # Duplicate
            status="filled",
        )
        test_db.add(trade2)

        with pytest.raises(Exception):  # IntegrityError
            test_db.commit()


class TestPerformanceModel:
    """Test Performance model for daily snapshots"""

    def test_create_performance_snapshot(self, test_db, sample_user):
        """Test creating daily performance record"""
        perf = Performance(
            user_id=sample_user.id,
            date=datetime.utcnow(),
            portfolio_value=110000.00,
            cash=20000.00,
            positions_value=90000.00,
            num_positions=5,
            total_pnl=10000.00,
            total_pnl_percent=10.00,
            day_pnl=500.00,
            day_pnl_percent=0.45,
            sharpe_ratio=1.25,
            max_drawdown=-2500.00,
            max_drawdown_percent=-2.27,
            total_trades=50,
            winning_trades=35,
            losing_trades=15,
            win_rate=0.70,
        )
        test_db.add(perf)
        test_db.commit()
        test_db.refresh(perf)

        assert perf.id is not None
        assert perf.portfolio_value == 110000.00
        assert perf.total_pnl_percent == 10.00
        assert perf.win_rate == 0.70

    def test_performance_risk_metrics(self, test_db, sample_user):
        """Test risk metrics fields"""
        perf = Performance(
            user_id=sample_user.id,
            date=datetime.utcnow(),
            portfolio_value=100000.00,
            cash=50000.00,
            positions_value=50000.00,
            num_positions=3,
            total_pnl=0,
            total_pnl_percent=0,
            day_pnl=0,
            day_pnl_percent=0,
            sharpe_ratio=1.45,
            volatility=0.15,
            max_drawdown=-5000.00,
            max_drawdown_percent=-5.00,
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
        )
        test_db.add(perf)
        test_db.commit()
        test_db.refresh(perf)

        assert perf.sharpe_ratio == 1.45
        assert perf.volatility == 0.15
        assert perf.max_drawdown_percent == -5.00


class TestEquitySnapshotModel:
    """Test EquitySnapshot model for intraday tracking"""

    def test_create_equity_snapshot(self, test_db, sample_user):
        """Test creating intraday equity snapshot"""
        snapshot = EquitySnapshot(
            user_id=sample_user.id,
            timestamp=datetime.utcnow(),
            equity=105000.00,
            cash=25000.00,
            positions_value=80000.00,
            num_positions=4,
            extra_data={
                "largest_position": "AAPL",
                "largest_position_value": 30000.00,
                "sector_breakdown": {"Technology": 0.60, "Healthcare": 0.25, "Finance": 0.15},
            },
        )
        test_db.add(snapshot)
        test_db.commit()
        test_db.refresh(snapshot)

        assert snapshot.id is not None
        assert snapshot.equity == 105000.00
        assert snapshot.extra_data["largest_position"] == "AAPL"
        assert snapshot.extra_data["sector_breakdown"]["Technology"] == 0.60

    def test_multiple_snapshots_per_day(self, test_db, sample_user):
        """Test creating multiple snapshots (for charting)"""
        base_time = datetime.utcnow()

        for i in range(5):
            snapshot = EquitySnapshot(
                user_id=sample_user.id,
                timestamp=base_time,
                equity=100000.00 + (i * 100),  # Simulated growth
                cash=50000.00,
                positions_value=50000.00 + (i * 100),
                num_positions=3,
                extra_data={},
            )
            test_db.add(snapshot)

        test_db.commit()

        # Query all snapshots
        snapshots = test_db.query(EquitySnapshot).filter_by(user_id=sample_user.id).all()
        assert len(snapshots) == 5
        assert snapshots[0].equity == 100000.00
        assert snapshots[4].equity == 100400.00


class TestModelRelationships:
    """Test relationships between models"""

    def test_strategy_to_user_relationship(self, test_db, sample_strategy):
        """Test Strategy → User relationship"""
        assert sample_strategy.user is not None
        assert sample_strategy.user.email == "test@example.com"

    def test_trade_to_strategy_relationship(self, test_db, sample_trade):
        """Test Trade → Strategy relationship"""
        # Note: Trade model doesn't have back_populates to Strategy
        # So we can only test the foreign key exists
        assert sample_trade.strategy_id is not None

    def test_trade_set_null_on_strategy_delete(self, test_db, sample_trade, sample_strategy):
        """Test ON DELETE SET NULL for strategy_id"""
        strategy_id = sample_strategy.id
        trade_id = sample_trade.id

        # Delete strategy
        test_db.delete(sample_strategy)
        test_db.commit()

        # Trade should still exist with NULL strategy_id
        trade = test_db.query(Trade).filter_by(id=trade_id).first()
        assert trade is not None
        assert trade.strategy_id is None  # SET NULL


class TestModelConstraints:
    """Test model constraints and validation"""

    def test_user_email_unique_constraint(self, test_db):
        """Test unique constraint on email"""
        user1 = User(email="unique@example.com", password_hash=TEST_PASSWORD_HASH, preferences={})
        test_db.add(user1)
        test_db.commit()

        user2 = User(email="unique@example.com", password_hash=TEST_PASSWORD_HASH, preferences={})
        test_db.add(user2)

        with pytest.raises(Exception):
            test_db.commit()

    def test_strategy_name_not_null(self, test_db):
        """Test strategy name is required"""
        strategy = Strategy(name=None, strategy_type="custom", config={})  # NULL not allowed
        test_db.add(strategy)

        with pytest.raises(Exception):
            test_db.commit()

    def test_trade_symbol_not_null(self, test_db, sample_user):
        """Test trade symbol is required"""
        trade = Trade(
            user_id=sample_user.id,
            symbol=None,  # NULL not allowed
            side="buy",
            quantity=1,
            price=100,
            order_type="market",
            status="pending",
        )
        test_db.add(trade)

        with pytest.raises(Exception):
            test_db.commit()
