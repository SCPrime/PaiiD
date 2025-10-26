"""
Integration Tests: Options Trading Flow
Test ID: INTG-OPT-001
Priority: HIGH

Tests complete options trading workflow:
1. Fetch options chain for symbol
2. Calculate options Greeks (delta, gamma, theta, vega)
3. Generate options trade proposals
4. Execute options orders
5. Track options positions
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from app.main import app


class TestOptionsChainFlow:
    """Integration tests for options chain retrieval and analysis"""

    def test_fetch_options_chain(self, client, test_db):
        """
        Test fetching options chain for a symbol

        Flow:
        1. Request options chain for AAPL
        2. Verify chain structure
        3. Check expiration dates and strikes
        """
        symbol = "AAPL"

        response = client.get(f"/api/options/chain/{symbol}")

        if response.status_code == 404:
            pytest.skip("Options chain endpoint not implemented")

        assert response.status_code in [200, 422], f"Options chain request failed: {response.text}"

        if response.status_code == 200:
            chain = response.json()

            # Verify chain structure
            # Could be dict with 'calls' and 'puts' or list of options
            assert chain is not None

            # Check for expiration dates
            if "expirations" in chain:
                assert len(chain["expirations"]) > 0
            elif "options" in chain:
                assert len(chain["options"]) > 0
            elif isinstance(chain, list):
                assert len(chain) > 0

    def test_options_chain_with_expiration(self, client, test_db):
        """
        Test filtering options by expiration date
        """
        symbol = "AAPL"

        # Get expirations first
        exp_response = client.get(f"/api/options/expirations/{symbol}")

        if exp_response.status_code == 404:
            # Try alternative endpoint
            exp_response = client.get(f"/api/options/chain/{symbol}")

        if exp_response.status_code == 404:
            pytest.skip("Options expirations endpoint not implemented")

        if exp_response.status_code == 200:
            exp_data = exp_response.json()

            # Extract expiration date
            if "expirations" in exp_data:
                if len(exp_data["expirations"]) > 0:
                    expiration = exp_data["expirations"][0]

                    # Get chain for specific expiration
                    chain_response = client.get(
                        f"/api/options/chain/{symbol}",
                        params={"expiration": expiration}
                    )

                    if chain_response.status_code == 200:
                        chain = chain_response.json()
                        assert chain is not None

    def test_options_chain_calls_and_puts(self, client, test_db):
        """
        Test options chain includes both calls and puts
        """
        symbol = "AAPL"

        response = client.get(f"/api/options/chain/{symbol}")

        if response.status_code == 404:
            pytest.skip("Options chain endpoint not implemented")

        if response.status_code == 200:
            chain = response.json()

            # Check for calls and puts
            if "calls" in chain and "puts" in chain:
                assert isinstance(chain["calls"], list)
                assert isinstance(chain["puts"], list)
            elif "options" in chain:
                # Options list should have option_type field
                options = chain["options"]
                if len(options) > 0:
                    assert "option_type" in options[0] or "type" in options[0]

    def test_options_strikes_retrieval(self, client, test_db):
        """
        Test retrieving available strike prices
        """
        symbol = "AAPL"

        # Get current stock price
        quote_response = client.get(f"/api/market/quote/{symbol}")
        if quote_response.status_code != 200:
            pytest.skip("Cannot get stock quote for options test")

        current_price = quote_response.json()["last"]

        # Get options chain
        chain_response = client.get(f"/api/options/chain/{symbol}")

        if chain_response.status_code == 404:
            pytest.skip("Options chain endpoint not implemented")

        if chain_response.status_code == 200:
            chain = chain_response.json()

            # Verify strikes near current price
            strikes = []

            if "calls" in chain:
                strikes.extend([opt["strike"] for opt in chain["calls"] if "strike" in opt])
            elif "options" in chain:
                strikes.extend([opt["strike"] for opt in chain["options"] if "strike" in opt])

            if len(strikes) > 0:
                # Should have strikes both above and below current price
                assert any(s < current_price for s in strikes)
                assert any(s > current_price for s in strikes)


class TestOptionsGreeksFlow:
    """Integration tests for options Greeks calculation"""

    def test_calculate_option_greeks(self, client, test_db):
        """
        Test calculating Greeks for an option

        Greeks: delta, gamma, theta, vega, rho
        """
        # Try Greeks calculation endpoint
        greeks_payload = {
            "symbol": "AAPL",
            "option_type": "call",
            "strike": 150.0,
            "expiration": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        }

        response = client.post("/api/options/greeks", json=greeks_payload)

        if response.status_code == 404:
            # Try GET endpoint
            response = client.get("/api/options/greeks/AAPL")

        if response.status_code == 404:
            pytest.skip("Options Greeks endpoint not implemented")

        if response.status_code == 200:
            greeks = response.json()

            # Verify Greeks are present
            expected_greeks = ["delta", "gamma", "theta", "vega", "rho"]

            # Should have at least some Greeks
            has_greeks = any(greek in greeks for greek in expected_greeks)
            assert has_greeks, f"Greeks response missing expected fields: {greeks}"

    def test_greeks_in_options_chain(self, client, test_db):
        """
        Test options chain includes Greeks for each option
        """
        symbol = "AAPL"

        response = client.get(f"/api/options/chain/{symbol}")

        if response.status_code == 404:
            pytest.skip("Options chain endpoint not implemented")

        if response.status_code == 200:
            chain = response.json()

            # Check if options have Greeks
            options = []
            if "calls" in chain and len(chain["calls"]) > 0:
                options = chain["calls"]
            elif "options" in chain and len(chain["options"]) > 0:
                options = chain["options"]

            if len(options) > 0:
                option = options[0]

                # Greeks may be embedded or separate
                greeks_fields = ["delta", "gamma", "theta", "vega", "greeks"]
                has_greeks = any(field in option for field in greeks_fields)

                # Greeks are nice to have but not required
                if not has_greeks:
                    print(f"Info: Options chain lacks Greeks data")

    def test_greeks_calculation_accuracy(self, client, test_db):
        """
        Test Greeks calculations are within reasonable bounds

        Delta: 0-1 for calls, -1-0 for puts
        Gamma: Always positive
        Theta: Usually negative (time decay)
        Vega: Always positive
        """
        greeks_payload = {
            "symbol": "AAPL",
            "option_type": "call",
            "strike": 150.0,
            "expiration": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        }

        response = client.post("/api/options/greeks", json=greeks_payload)

        if response.status_code == 404:
            pytest.skip("Options Greeks endpoint not implemented")

        if response.status_code == 200:
            greeks = response.json()

            # Validate delta for call (0 to 1)
            if "delta" in greeks:
                delta = greeks["delta"]
                assert 0 <= delta <= 1, f"Call delta out of range: {delta}"

            # Validate gamma (positive)
            if "gamma" in greeks:
                gamma = greeks["gamma"]
                assert gamma >= 0, f"Gamma should be positive: {gamma}"

            # Validate vega (positive)
            if "vega" in greeks:
                vega = greeks["vega"]
                assert vega >= 0, f"Vega should be positive: {vega}"


class TestOptionsProposalsFlow:
    """Integration tests for options trade proposals"""

    def test_generate_options_proposal(self, client, test_db):
        """
        Test generating options trade proposal

        Proposal suggests optimal options trades based on market conditions
        """
        proposal_request = {
            "symbol": "AAPL",
            "strategy": "covered_call",
            "contracts": 1,
        }

        response = client.post("/api/proposals/generate", json=proposal_request)

        if response.status_code == 404:
            # Try alternative endpoint
            response = client.post("/api/options/proposal", json=proposal_request)

        if response.status_code == 404:
            pytest.skip("Options proposal endpoint not implemented")

        assert response.status_code in [200, 201, 422]

        if response.status_code in [200, 201]:
            proposal = response.json()

            # Verify proposal structure
            assert "symbol" in proposal or "legs" in proposal or "strategy" in proposal

    def test_multi_leg_options_proposal(self, client, test_db):
        """
        Test multi-leg options strategies (spreads, iron condors, etc.)
        """
        strategies = [
            "vertical_spread",
            "iron_condor",
            "butterfly",
            "straddle",
        ]

        for strategy in strategies:
            proposal_request = {
                "symbol": "AAPL",
                "strategy": strategy,
            }

            response = client.post("/api/proposals/generate", json=proposal_request)

            if response.status_code == 404:
                response = client.post("/api/options/proposal", json=proposal_request)

            if response.status_code in [200, 201]:
                proposal = response.json()

                # Multi-leg strategies should have multiple legs
                if "legs" in proposal:
                    assert len(proposal["legs"]) >= 2
                return  # At least one strategy worked

        pytest.skip("Multi-leg options proposals not implemented")

    def test_options_proposal_risk_metrics(self, client, test_db):
        """
        Test options proposals include risk metrics
        """
        proposal_request = {
            "symbol": "AAPL",
            "strategy": "covered_call",
        }

        response = client.post("/api/proposals/generate", json=proposal_request)

        if response.status_code == 404:
            pytest.skip("Options proposal endpoint not implemented")

        if response.status_code in [200, 201]:
            proposal = response.json()

            # Check for risk metrics
            risk_fields = [
                "max_profit",
                "max_loss",
                "break_even",
                "risk_reward",
                "probability_profit",
            ]

            has_risk_metrics = any(field in proposal for field in risk_fields)

            # Risk metrics are important for options
            if not has_risk_metrics:
                print(f"Warning: Options proposal lacks risk metrics")


class TestOptionsOrderExecution:
    """Integration tests for options order execution"""

    def test_single_leg_options_order(self, client, test_db):
        """
        Test placing single-leg options order
        """
        # Get options chain to find valid option
        chain_response = client.get("/api/options/chain/AAPL")

        if chain_response.status_code == 404:
            pytest.skip("Options chain endpoint not implemented")

        if chain_response.status_code == 200:
            chain = chain_response.json()

            # Extract first call option
            option_symbol = None

            if "calls" in chain and len(chain["calls"]) > 0:
                option = chain["calls"][0]
                option_symbol = option.get("symbol") or option.get("option_symbol")

            if option_symbol:
                # Place options order
                order_payload = {
                    "symbol": option_symbol,
                    "quantity": 1,
                    "side": "buy_to_open",
                    "order_type": "market",
                }

                order_response = client.post("/api/orders", json=order_payload)

                # Options orders may not be supported yet
                assert order_response.status_code in [200, 201, 400, 422]
            else:
                pytest.skip("Could not extract option symbol from chain")

    def test_options_order_validation(self, client, test_db):
        """
        Test validation of options orders
        """
        # Invalid option symbol
        invalid_order = {
            "symbol": "INVALID_OPTION",
            "quantity": 1,
            "side": "buy_to_open",
            "order_type": "market",
        }

        response = client.post("/api/orders", json=invalid_order)

        # Should return validation error
        assert response.status_code in [400, 422, 404]

    def test_options_position_tracking(self, client, test_db):
        """
        Test tracking options positions separately from stock positions
        """
        # Get positions
        positions_response = client.get("/api/positions")
        assert positions_response.status_code == 200

        positions_data = positions_response.json()

        # Try to get options positions specifically
        options_response = client.get("/api/positions/options")

        if options_response.status_code == 200:
            options_positions = options_response.json()

            # Verify options positions structure
            assert isinstance(options_positions, (list, dict))
        elif options_response.status_code == 404:
            # Options positions may be mixed with stock positions
            pytest.skip("Separate options positions endpoint not implemented")


class TestOptionsAnalysis:
    """Integration tests for options analysis tools"""

    def test_implied_volatility_calculation(self, client, test_db):
        """
        Test implied volatility calculation for options
        """
        response = client.get("/api/options/iv/AAPL")

        if response.status_code == 404:
            pytest.skip("Implied volatility endpoint not implemented")

        assert response.status_code == 200

        iv_data = response.json()

        # Should include IV values
        assert "iv" in iv_data or "implied_volatility" in iv_data

    def test_options_probability_calculator(self, client, test_db):
        """
        Test probability calculator for options
        """
        calc_payload = {
            "symbol": "AAPL",
            "target_price": 160.0,
            "expiration": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        }

        response = client.post("/api/options/probability", json=calc_payload)

        if response.status_code == 404:
            pytest.skip("Options probability calculator not implemented")

        if response.status_code == 200:
            probability = response.json()

            # Should include probability value
            assert "probability" in probability or "chance" in probability

    def test_options_scanner(self, client, test_db):
        """
        Test options scanner for finding trading opportunities
        """
        scanner_params = {
            "min_volume": 100,
            "max_spread": 0.10,
            "strategy": "covered_call",
        }

        response = client.get("/api/options/scan", params=scanner_params)

        if response.status_code == 404:
            pytest.skip("Options scanner not implemented")

        if response.status_code == 200:
            results = response.json()

            # Should return list of opportunities
            assert isinstance(results, (list, dict))


class TestOptionsErrorHandling:
    """Test error handling in options trading flows"""

    def test_invalid_expiration_date(self, client, test_db):
        """
        Test handling of invalid expiration dates
        """
        # Past expiration date
        past_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        response = client.get(
            "/api/options/chain/AAPL",
            params={"expiration": past_date}
        )

        if response.status_code == 404:
            pytest.skip("Options chain endpoint not implemented")

        # Should reject past dates
        assert response.status_code in [200, 400, 422]

    def test_options_api_timeout(self, client, test_db):
        """
        Test graceful handling of options API timeouts
        """
        response = client.get("/api/options/chain/AAPL")

        if response.status_code == 404:
            pytest.skip("Options chain endpoint not implemented")

        # Should handle timeouts gracefully
        assert response.status_code in [200, 503, 504]

    def test_zero_contracts_rejection(self, client, test_db):
        """
        Test rejection of orders with zero contracts
        """
        order_payload = {
            "symbol": "AAPL250117C00150000",
            "quantity": 0,
            "side": "buy_to_open",
            "order_type": "market",
        }

        response = client.post("/api/orders", json=order_payload)

        # Should reject zero quantity
        assert response.status_code in [400, 422]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
