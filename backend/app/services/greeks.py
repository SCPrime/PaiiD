"""
Adapter around options_greeks to provide the existing interface used across the app.

Keeps the same class name and method signatures expected by callers while delegating
to the production implementation in options_greeks.
"""

from .options_greeks import GreeksCalculator as _BSCalculator


class GreeksCalculator:
    def __init__(self, risk_free_rate: float = 0.05):
        self._impl = _BSCalculator(risk_free_rate=risk_free_rate)

    def calculate_greeks(
        self,
        option_type: str,
        underlying_price: float,
        strike_price: float,
        days_to_expiry: int,
        implied_volatility: float,
    ) -> dict[str, float]:
        """Return minimal greeks dict matching existing callers."""
        time_to_expiry = max(0.0, days_to_expiry / 365.0)
        greeks = self._impl.calculate_greeks(
            spot_price=underlying_price,
            strike_price=strike_price,
            time_to_expiry=time_to_expiry,
            volatility=implied_volatility,
            option_type=option_type,
        )

        return {
            "delta": float(greeks.delta),
            "gamma": float(greeks.gamma),
            "theta": float(greeks.theta),
            "vega": float(greeks.vega),
        }

    # Convenience helpers (not currently used by callers)
    def calculate_delta(
        self,
        option_type: str,
        underlying_price: float,
        strike_price: float,
        days_to_expiry: int,
        implied_volatility: float,
    ) -> float:
        return self.calculate_greeks(
            option_type,
            underlying_price,
            strike_price,
            days_to_expiry,
            implied_volatility,
        )["delta"]

    def calculate_gamma(
        self,
        underlying_price: float,
        strike_price: float,
        days_to_expiry: int,
        implied_volatility: float,
    ) -> float:
        return self.calculate_greeks(
            "call",
            underlying_price,
            strike_price,
            days_to_expiry,
            implied_volatility,
        )["gamma"]

    def calculate_theta(
        self,
        option_type: str,
        underlying_price: float,
        strike_price: float,
        days_to_expiry: int,
        implied_volatility: float,
    ) -> float:
        return self.calculate_greeks(
            option_type,
            underlying_price,
            strike_price,
            days_to_expiry,
            implied_volatility,
        )["theta"]

    def calculate_vega(
        self,
        underlying_price: float,
        strike_price: float,
        days_to_expiry: int,
        implied_volatility: float,
    ) -> float:
        return self.calculate_greeks(
            "call",
            underlying_price,
            strike_price,
            days_to_expiry,
            implied_volatility,
        )["vega"]


# Global instance retained for compatibility
greeks_calculator = GreeksCalculator(risk_free_rate=0.05)
