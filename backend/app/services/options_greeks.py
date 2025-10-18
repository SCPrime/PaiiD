"""
Options Greeks Calculation Service

Implements Black-Scholes-Merton model for calculating option Greeks:
- Delta: Rate of change of option price with respect to underlying price
- Gamma: Rate of change of delta with respect to underlying price
- Theta: Rate of change of option price with respect to time (time decay)
- Vega: Rate of change of option price with respect to volatility
- Rho: Rate of change of option price with respect to interest rate

Uses scipy for numerical calculations and supports both call and put options.
"""

import math
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from scipy.stats import norm


@dataclass
class OptionsGreeks:
    """Container for all calculated Greeks"""

    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float
    # Derived metrics
    theoretical_price: float
    intrinsic_value: float
    extrinsic_value: float
    probability_itm: float  # Probability of finishing in-the-money


class GreeksCalculator:
    """
    Black-Scholes-Merton Greeks calculator

    Assumptions:
    - European-style options (exercise only at expiration)
    - Continuous compounding
    - No dividends (can be extended for dividend-paying stocks)
    - Constant volatility and risk-free rate
    """

    def __init__(self, risk_free_rate: float = 0.05):
        """
        Initialize calculator with risk-free interest rate

        Args:
            risk_free_rate: Annual risk-free rate (default 5% = 0.05)
        """
        self.risk_free_rate = risk_free_rate

    def calculate_greeks(
        self,
        spot_price: float,
        strike_price: float,
        time_to_expiry: float,  # in years
        volatility: float,  # implied volatility (annualized)
        option_type: Literal["call", "put"],
        dividend_yield: float = 0.0,
    ) -> OptionsGreeks:
        """
        Calculate all Greeks for an option

        Args:
            spot_price: Current price of underlying asset
            strike_price: Strike price of the option
            time_to_expiry: Time to expiration in years (e.g., 30 days = 30/365)
            volatility: Implied volatility (e.g., 0.25 = 25% IV)
            option_type: "call" or "put"
            dividend_yield: Annual dividend yield (default 0)

        Returns:
            OptionsGreeks object with all calculated values
        """
        # Handle edge case: at expiration
        if time_to_expiry <= 0:
            return self._calculate_at_expiration(spot_price, strike_price, option_type)

        # Calculate d1 and d2 (Black-Scholes parameters)
        d1 = self._calculate_d1(
            spot_price, strike_price, time_to_expiry, volatility, dividend_yield
        )
        d2 = d1 - volatility * math.sqrt(time_to_expiry)

        # Calculate theoretical price
        theo_price = self._calculate_theoretical_price(
            spot_price, strike_price, time_to_expiry, d1, d2, option_type, dividend_yield
        )

        # Calculate Greeks
        delta = self._calculate_delta(d1, option_type, dividend_yield, time_to_expiry)
        gamma = self._calculate_gamma(spot_price, d1, volatility, time_to_expiry, dividend_yield)
        theta = self._calculate_theta(
            spot_price,
            strike_price,
            time_to_expiry,
            d1,
            d2,
            volatility,
            option_type,
            dividend_yield,
        )
        vega = self._calculate_vega(spot_price, d1, time_to_expiry, dividend_yield)
        rho = self._calculate_rho(strike_price, time_to_expiry, d2, option_type)

        # Calculate intrinsic and extrinsic value
        intrinsic = (
            max(0, spot_price - strike_price)
            if option_type == "call"
            else max(0, strike_price - spot_price)
        )
        extrinsic = theo_price - intrinsic

        # Probability of finishing ITM
        prob_itm = norm.cdf(d2) if option_type == "call" else norm.cdf(-d2)

        return OptionsGreeks(
            delta=delta,
            gamma=gamma,
            theta=theta,
            vega=vega,
            rho=rho,
            theoretical_price=theo_price,
            intrinsic_value=intrinsic,
            extrinsic_value=extrinsic,
            probability_itm=prob_itm,
        )

    def _calculate_d1(
        self,
        spot_price: float,
        strike_price: float,
        time_to_expiry: float,
        volatility: float,
        dividend_yield: float,
    ) -> float:
        """Calculate d1 parameter for Black-Scholes"""
        numerator = (
            math.log(spot_price / strike_price)
            + (self.risk_free_rate - dividend_yield + 0.5 * volatility**2) * time_to_expiry
        )
        denominator = volatility * math.sqrt(time_to_expiry)
        return numerator / denominator

    def _calculate_theoretical_price(
        self,
        spot_price: float,
        strike_price: float,
        time_to_expiry: float,
        d1: float,
        d2: float,
        option_type: Literal["call", "put"],
        dividend_yield: float,
    ) -> float:
        """Calculate theoretical option price using Black-Scholes"""
        discount_factor = math.exp(-self.risk_free_rate * time_to_expiry)
        dividend_discount = math.exp(-dividend_yield * time_to_expiry)

        if option_type == "call":
            price = spot_price * dividend_discount * norm.cdf(
                d1
            ) - strike_price * discount_factor * norm.cdf(d2)
        else:  # put
            price = strike_price * discount_factor * norm.cdf(
                -d2
            ) - spot_price * dividend_discount * norm.cdf(-d1)

        return price

    def _calculate_delta(
        self,
        d1: float,
        option_type: Literal["call", "put"],
        dividend_yield: float,
        time_to_expiry: float,
    ) -> float:
        """Calculate Delta (∂V/∂S)"""
        dividend_discount = math.exp(-dividend_yield * time_to_expiry)

        if option_type == "call":
            return dividend_discount * norm.cdf(d1)
        else:  # put
            return dividend_discount * (norm.cdf(d1) - 1)

    def _calculate_gamma(
        self,
        spot_price: float,
        d1: float,
        volatility: float,
        time_to_expiry: float,
        dividend_yield: float,
    ) -> float:
        """Calculate Gamma (∂²V/∂S²) - same for calls and puts"""
        dividend_discount = math.exp(-dividend_yield * time_to_expiry)
        numerator = dividend_discount * norm.pdf(d1)
        denominator = spot_price * volatility * math.sqrt(time_to_expiry)
        return numerator / denominator

    def _calculate_theta(
        self,
        spot_price: float,
        strike_price: float,
        time_to_expiry: float,
        d1: float,
        d2: float,
        volatility: float,
        option_type: Literal["call", "put"],
        dividend_yield: float,
    ) -> float:
        """Calculate Theta (∂V/∂t) - time decay per day"""
        discount_factor = math.exp(-self.risk_free_rate * time_to_expiry)
        dividend_discount = math.exp(-dividend_yield * time_to_expiry)

        # First term (volatility component)
        first_term = -(spot_price * dividend_discount * norm.pdf(d1) * volatility) / (
            2 * math.sqrt(time_to_expiry)
        )

        if option_type == "call":
            # Second term (interest rate component for calls)
            second_term = -self.risk_free_rate * strike_price * discount_factor * norm.cdf(d2)
            # Third term (dividend component)
            third_term = dividend_yield * spot_price * dividend_discount * norm.cdf(d1)
            theta = first_term + second_term + third_term
        else:  # put
            # Second term (interest rate component for puts)
            second_term = self.risk_free_rate * strike_price * discount_factor * norm.cdf(-d2)
            # Third term (dividend component)
            third_term = -dividend_yield * spot_price * dividend_discount * norm.cdf(-d1)
            theta = first_term + second_term + third_term

        # Convert to per-day theta (divide by 365)
        return theta / 365

    def _calculate_vega(
        self, spot_price: float, d1: float, time_to_expiry: float, dividend_yield: float
    ) -> float:
        """Calculate Vega (∂V/∂σ) - sensitivity to volatility"""
        dividend_discount = math.exp(-dividend_yield * time_to_expiry)
        vega = spot_price * dividend_discount * norm.pdf(d1) * math.sqrt(time_to_expiry)
        # Return vega per 1% change in volatility (divide by 100)
        return vega / 100

    def _calculate_rho(
        self,
        strike_price: float,
        time_to_expiry: float,
        d2: float,
        option_type: Literal["call", "put"],
    ) -> float:
        """Calculate Rho (∂V/∂r) - sensitivity to interest rate"""
        discount_factor = math.exp(-self.risk_free_rate * time_to_expiry)

        if option_type == "call":
            rho = strike_price * time_to_expiry * discount_factor * norm.cdf(d2)
        else:  # put
            rho = -strike_price * time_to_expiry * discount_factor * norm.cdf(-d2)

        # Return rho per 1% change in interest rate (divide by 100)
        return rho / 100

    def _calculate_at_expiration(
        self, spot_price: float, strike_price: float, option_type: Literal["call", "put"]
    ) -> OptionsGreeks:
        """Handle special case: option at expiration"""
        if option_type == "call":
            intrinsic = max(0, spot_price - strike_price)
            delta = 1.0 if spot_price > strike_price else 0.0
        else:  # put
            intrinsic = max(0, strike_price - spot_price)
            delta = -1.0 if spot_price < strike_price else 0.0

        return OptionsGreeks(
            delta=delta,
            gamma=0.0,  # No gamma at expiration
            theta=0.0,  # No time decay left
            vega=0.0,  # No volatility sensitivity
            rho=0.0,  # No interest rate sensitivity
            theoretical_price=intrinsic,
            intrinsic_value=intrinsic,
            extrinsic_value=0.0,
            probability_itm=1.0 if intrinsic > 0 else 0.0,
        )


def days_to_expiry_in_years(expiry_date: datetime) -> float:
    """
    Convert expiration date to time in years

    Args:
        expiry_date: Option expiration date (datetime object)

    Returns:
        Time to expiry in years (e.g., 30 days = 0.0822 years)
    """
    now = datetime.now()
    days_remaining = (expiry_date - now).total_seconds() / 86400
    return max(0, days_remaining / 365.0)


# Singleton calculator instance
_calculator = GreeksCalculator()


def calculate_option_greeks(
    spot_price: float,
    strike_price: float,
    expiry_date: datetime,
    volatility: float,
    option_type: Literal["call", "put"],
    dividend_yield: float = 0.0,
) -> OptionsGreeks:
    """
    Convenience function to calculate Greeks with date-based expiry

    Example:
        greeks = calculate_option_greeks(
            spot_price=150.0,
            strike_price=155.0,
            expiry_date=datetime(2025, 12, 20),
            volatility=0.30,  # 30% IV
            option_type="call"
        )
        print(f"Delta: {greeks.delta:.4f}")
        print(f"Theta: {greeks.theta:.4f} per day")
    """
    time_to_expiry = days_to_expiry_in_years(expiry_date)
    return _calculator.calculate_greeks(
        spot_price=spot_price,
        strike_price=strike_price,
        time_to_expiry=time_to_expiry,
        volatility=volatility,
        option_type=option_type,
        dividend_yield=dividend_yield,
    )
