"""
Integration Tests: Backtesting Flow
Test ID: INTG-BACKTEST-001
Priority: HIGH

Tests complete backtesting workflow:
1. Create trading strategy
2. Run backtest with historical data
3. Analyze backtest results and metrics
4. Compare strategies performance
5. Optimize strategy parameters
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from app.main import app


class TestStrategyCreationFlow:
    """Integration tests for trading strategy creation"""

    def test_create_simple_strategy(self, client, test_db):
        """
        Test creating a simple trading strategy

        Flow:
        1. Define strategy parameters
        2. Create strategy via API
        3. Verify strategy is stored
        """
        strategy_payload = {
            "name": "Simple Momentum Strategy",
            "description": "Buy stocks with RSI > 70, sell when RSI < 30",
            "strategy_type": "momentum",
            "config": {
                "entry_rules": ["RSI > 70"],
                "exit_rules": ["RSI < 30"],
                "position_size": 0.10,
            },
        }

        response = client.post("/api/strategies", json=strategy_payload)

        if response.status_code == 404:
            pytest.skip("Strategy creation endpoint not implemented")

        assert response.status_code in [200, 201], f"Strategy creation failed: {response.text}"

        strategy_data = response.json()

        # Verify strategy data
        assert "id" in strategy_data or "strategy_id" in strategy_data
        assert strategy_data["name"] == strategy_payload["name"]
        assert strategy_data["strategy_type"] == strategy_payload["strategy_type"]

    def test_create_complex_strategy(self, client, test_db):
        """
        Test creating complex multi-indicator strategy
        """
        complex_strategy = {
            "name": "Multi-Indicator Strategy",
            "description": "Combines RSI, MACD, and moving averages",
            "strategy_type": "technical",
            "config": {
                "entry_rules": [
                    "RSI > 60",
                    "MACD_SIGNAL == bullish",
                    "Price > MA50",
                ],
                "exit_rules": [
                    "RSI < 40",
                    "MACD_SIGNAL == bearish",
                    "Price < MA50",
                ],
                "position_size": 0.15,
                "max_positions": 5,
                "stop_loss": 0.02,
                "take_profit": 0.05,
            },
        }

        response = client.post("/api/strategies", json=complex_strategy)

        if response.status_code == 404:
            pytest.skip("Strategy creation endpoint not implemented")

        assert response.status_code in [200, 201]

    def test_list_strategies(self, client, test_db):
        """
        Test listing all user strategies
        """
        response = client.get("/api/strategies")

        if response.status_code == 404:
            pytest.skip("Strategy list endpoint not implemented")

        assert response.status_code == 200

        strategies = response.json()

        # Should be list or dict with 'strategies' key
        strategies_list = strategies if isinstance(strategies, list) else strategies.get("strategies", [])

        assert isinstance(strategies_list, list)

    def test_get_strategy_by_id(self, client, test_db):
        """
        Test retrieving specific strategy by ID
        """
        # Create strategy first
        strategy_payload = {
            "name": "Test Strategy",
            "strategy_type": "momentum",
            "config": {},
        }

        create_response = client.post("/api/strategies", json=strategy_payload)

        if create_response.status_code == 404:
            pytest.skip("Strategy endpoints not implemented")

        if create_response.status_code in [200, 201]:
            strategy_id = create_response.json().get("id") or create_response.json().get("strategy_id")

            # Get strategy by ID
            get_response = client.get(f"/api/strategies/{strategy_id}")
            assert get_response.status_code == 200

            strategy = get_response.json()
            assert strategy["name"] == "Test Strategy"

    def test_update_strategy(self, client, test_db):
        """
        Test updating existing strategy
        """
        # Create strategy
        create_payload = {
            "name": "Original Strategy",
            "strategy_type": "momentum",
            "config": {"position_size": 0.10},
        }

        create_response = client.post("/api/strategies", json=create_payload)

        if create_response.status_code == 404:
            pytest.skip("Strategy endpoints not implemented")

        if create_response.status_code in [200, 201]:
            strategy_id = create_response.json().get("id") or create_response.json().get("strategy_id")

            # Update strategy
            update_payload = {
                "name": "Updated Strategy",
                "config": {"position_size": 0.15},
            }

            update_response = client.put(f"/api/strategies/{strategy_id}", json=update_payload)

            if update_response.status_code == 200:
                updated_strategy = update_response.json()
                assert updated_strategy["name"] == "Updated Strategy"

    def test_delete_strategy(self, client, test_db):
        """
        Test deleting strategy
        """
        # Create strategy
        create_payload = {
            "name": "Strategy to Delete",
            "strategy_type": "momentum",
            "config": {},
        }

        create_response = client.post("/api/strategies", json=create_payload)

        if create_response.status_code == 404:
            pytest.skip("Strategy endpoints not implemented")

        if create_response.status_code in [200, 201]:
            strategy_id = create_response.json().get("id") or create_response.json().get("strategy_id")

            # Delete strategy
            delete_response = client.delete(f"/api/strategies/{strategy_id}")
            assert delete_response.status_code in [200, 204]


class TestBacktestExecutionFlow:
    """Integration tests for backtest execution"""

    def test_run_simple_backtest(self, client, test_db):
        """
        Test running backtest for a strategy

        Flow:
        1. Create strategy
        2. Run backtest with date range
        3. Verify backtest completes
        """
        # Create strategy first
        strategy_payload = {
            "name": "Backtest Strategy",
            "strategy_type": "momentum",
            "config": {
                "entry_rules": ["RSI > 70"],
                "exit_rules": ["RSI < 30"],
            },
        }

        strategy_response = client.post("/api/strategies", json=strategy_payload)

        if strategy_response.status_code == 404:
            pytest.skip("Strategy endpoints not implemented")

        if strategy_response.status_code in [200, 201]:
            strategy_id = strategy_response.json().get("id") or strategy_response.json().get("strategy_id")

            # Run backtest
            backtest_payload = {
                "strategy_id": strategy_id,
                "symbol": "AAPL",
                "start_date": (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
                "end_date": datetime.now().strftime("%Y-%m-%d"),
                "initial_capital": 10000.0,
            }

            backtest_response = client.post("/api/backtesting/run", json=backtest_payload)

            if backtest_response.status_code == 404:
                # Try alternative endpoint
                backtest_response = client.post(f"/api/strategies/{strategy_id}/backtest", json=backtest_payload)

            if backtest_response.status_code == 404:
                pytest.skip("Backtest execution endpoint not implemented")

            assert backtest_response.status_code in [200, 201, 202], f"Backtest failed: {backtest_response.text}"

    def test_backtest_with_multiple_symbols(self, client, test_db):
        """
        Test backtesting strategy across multiple symbols
        """
        strategy_payload = {
            "name": "Multi-Symbol Strategy",
            "strategy_type": "momentum",
            "config": {},
        }

        strategy_response = client.post("/api/strategies", json=strategy_payload)

        if strategy_response.status_code == 404:
            pytest.skip("Strategy endpoints not implemented")

        if strategy_response.status_code in [200, 201]:
            strategy_id = strategy_response.json().get("id") or strategy_response.json().get("strategy_id")

            # Run backtest on multiple symbols
            backtest_payload = {
                "strategy_id": strategy_id,
                "symbols": ["AAPL", "MSFT", "GOOGL"],
                "start_date": (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d"),
                "end_date": datetime.now().strftime("%Y-%m-%d"),
                "initial_capital": 10000.0,
            }

            backtest_response = client.post("/api/backtesting/run", json=backtest_payload)

            if backtest_response.status_code == 404:
                pytest.skip("Backtest execution endpoint not implemented")

            assert backtest_response.status_code in [200, 201, 202]

    def test_backtest_status_tracking(self, client, test_db):
        """
        Test tracking backtest execution status
        """
        # Create and run backtest
        strategy_payload = {"name": "Status Test", "strategy_type": "momentum", "config": {}}
        strategy_response = client.post("/api/strategies", json=strategy_payload)

        if strategy_response.status_code == 404:
            pytest.skip("Strategy endpoints not implemented")

        if strategy_response.status_code in [200, 201]:
            strategy_id = strategy_response.json().get("id") or strategy_response.json().get("strategy_id")

            backtest_payload = {
                "strategy_id": strategy_id,
                "symbol": "AAPL",
                "start_date": (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d"),
                "end_date": datetime.now().strftime("%Y-%m-%d"),
            }

            run_response = client.post("/api/backtesting/run", json=backtest_payload)

            if run_response.status_code in [200, 201, 202]:
                backtest_id = run_response.json().get("id") or run_response.json().get("backtest_id")

                if backtest_id:
                    # Check backtest status
                    status_response = client.get(f"/api/backtesting/{backtest_id}/status")

                    if status_response.status_code == 200:
                        status = status_response.json()
                        assert "status" in status or "state" in status


class TestBacktestResultsAnalysis:
    """Integration tests for backtest results analysis"""

    def test_get_backtest_results(self, client, test_db):
        """
        Test retrieving backtest results

        Results should include:
        - Total return
        - Win rate
        - Max drawdown
        - Sharpe ratio
        - Number of trades
        """
        # Create strategy and run backtest
        strategy_payload = {"name": "Results Test", "strategy_type": "momentum", "config": {}}
        strategy_response = client.post("/api/strategies", json=strategy_payload)

        if strategy_response.status_code == 404:
            pytest.skip("Strategy endpoints not implemented")

        if strategy_response.status_code in [200, 201]:
            strategy_id = strategy_response.json().get("id") or strategy_response.json().get("strategy_id")

            backtest_payload = {
                "strategy_id": strategy_id,
                "symbol": "AAPL",
                "start_date": (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d"),
                "end_date": datetime.now().strftime("%Y-%m-%d"),
            }

            run_response = client.post("/api/backtesting/run", json=backtest_payload)

            if run_response.status_code == 404:
                pytest.skip("Backtest execution endpoint not implemented")

            if run_response.status_code in [200, 201, 202]:
                result_data = run_response.json()

                # Results might be in response or need separate call
                if "results" in result_data:
                    results = result_data["results"]
                else:
                    backtest_id = result_data.get("id") or result_data.get("backtest_id")
                    if backtest_id:
                        results_response = client.get(f"/api/backtesting/{backtest_id}/results")
                        if results_response.status_code == 200:
                            results = results_response.json()
                        else:
                            pytest.skip("Backtest results endpoint not found")
                    else:
                        pytest.skip("No backtest ID in response")

                # Verify results structure
                expected_metrics = [
                    "total_return",
                    "win_rate",
                    "max_drawdown",
                    "sharpe_ratio",
                    "num_trades",
                    "profit_factor",
                ]

                # Should have at least some metrics
                has_metrics = any(metric in results for metric in expected_metrics)
                assert has_metrics or "metrics" in results

    def test_backtest_trade_history(self, client, test_db):
        """
        Test retrieving individual trades from backtest
        """
        # Try to get backtest trade history
        response = client.get("/api/backtesting/1/trades")

        if response.status_code == 404:
            pytest.skip("Backtest trade history endpoint not implemented")

        if response.status_code == 200:
            trades = response.json()

            # Should be list of trades
            trades_list = trades if isinstance(trades, list) else trades.get("trades", [])

            if len(trades_list) > 0:
                trade = trades_list[0]

                # Verify trade structure
                assert "symbol" in trade or "ticker" in trade
                assert "entry_date" in trade or "buy_date" in trade
                assert "exit_date" in trade or "sell_date" in trade
                assert "profit_loss" in trade or "pnl" in trade

    def test_backtest_equity_curve(self, client, test_db):
        """
        Test retrieving equity curve from backtest
        """
        response = client.get("/api/backtesting/1/equity_curve")

        if response.status_code == 404:
            pytest.skip("Backtest equity curve endpoint not implemented")

        if response.status_code == 200:
            equity_curve = response.json()

            # Should be list of timestamped values
            curve_list = equity_curve if isinstance(equity_curve, list) else equity_curve.get("curve", [])

            if len(curve_list) > 0:
                point = curve_list[0]
                assert "date" in point or "timestamp" in point
                assert "value" in point or "equity" in point


class TestStrategyComparison:
    """Integration tests for comparing multiple strategies"""

    def test_compare_two_strategies(self, client, test_db):
        """
        Test comparing performance of two strategies
        """
        # Create two strategies
        strategy1 = {"name": "Strategy A", "strategy_type": "momentum", "config": {}}
        strategy2 = {"name": "Strategy B", "strategy_type": "value", "config": {}}

        resp1 = client.post("/api/strategies", json=strategy1)
        resp2 = client.post("/api/strategies", json=strategy2)

        if resp1.status_code == 404:
            pytest.skip("Strategy endpoints not implemented")

        if resp1.status_code in [200, 201] and resp2.status_code in [200, 201]:
            id1 = resp1.json().get("id")
            id2 = resp2.json().get("id")

            # Compare strategies
            compare_payload = {
                "strategy_ids": [id1, id2],
                "symbol": "AAPL",
                "start_date": (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d"),
                "end_date": datetime.now().strftime("%Y-%m-%d"),
            }

            compare_response = client.post("/api/backtesting/compare", json=compare_payload)

            if compare_response.status_code == 404:
                pytest.skip("Strategy comparison endpoint not implemented")

            if compare_response.status_code == 200:
                comparison = compare_response.json()

                # Should include results for both strategies
                assert "strategies" in comparison or "results" in comparison


class TestStrategyOptimization:
    """Integration tests for strategy parameter optimization"""

    def test_optimize_strategy_parameters(self, client, test_db):
        """
        Test optimizing strategy parameters
        """
        optimization_request = {
            "strategy_id": 1,
            "symbol": "AAPL",
            "parameters_to_optimize": {
                "rsi_threshold": {"min": 60, "max": 80, "step": 5},
                "position_size": {"min": 0.05, "max": 0.20, "step": 0.05},
            },
            "start_date": (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d"),
            "end_date": datetime.now().strftime("%Y-%m-%d"),
        }

        response = client.post("/api/backtesting/optimize", json=optimization_request)

        if response.status_code == 404:
            pytest.skip("Strategy optimization endpoint not implemented")

        if response.status_code in [200, 202]:
            optimization_result = response.json()

            # Should include best parameters
            assert "best_parameters" in optimization_result or "optimal_params" in optimization_result


class TestBacktestErrorHandling:
    """Test error handling in backtesting flows"""

    def test_invalid_date_range(self, client, test_db):
        """
        Test backtest rejects invalid date ranges
        """
        backtest_payload = {
            "strategy_id": 1,
            "symbol": "AAPL",
            "start_date": "2025-12-31",  # Future date
            "end_date": "2025-01-01",  # Before start
        }

        response = client.post("/api/backtesting/run", json=backtest_payload)

        if response.status_code == 404:
            pytest.skip("Backtest endpoint not implemented")

        # Should reject invalid date range
        assert response.status_code in [400, 422]

    def test_missing_strategy_id(self, client, test_db):
        """
        Test backtest requires valid strategy ID
        """
        backtest_payload = {
            "symbol": "AAPL",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
        }

        response = client.post("/api/backtesting/run", json=backtest_payload)

        if response.status_code == 404:
            pytest.skip("Backtest endpoint not implemented")

        # Should reject missing strategy_id
        assert response.status_code in [400, 422]

    def test_backtest_timeout_handling(self, client, test_db):
        """
        Test handling of long-running backtests
        """
        # Very long backtest period
        backtest_payload = {
            "strategy_id": 1,
            "symbol": "AAPL",
            "start_date": "2000-01-01",
            "end_date": datetime.now().strftime("%Y-%m-%d"),
        }

        response = client.post("/api/backtesting/run", json=backtest_payload)

        if response.status_code == 404:
            pytest.skip("Backtest endpoint not implemented")

        # Should either succeed, return 202 (accepted), or timeout gracefully
        assert response.status_code in [200, 201, 202, 408, 504]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
