from dataclasses import dataclass
from typing import Any

"""
Strategy Templates Service
Pre-built trading strategy templates with risk classifications
"""


@dataclass
class StrategyTemplate:
    """Template for a trading strategy"""

    id: str
    name: str
    description: str
    strategy_type: str  # trend_following, mean_reversion, momentum, volatility_breakout
    risk_level: str  # Conservative, Moderate, Aggressive
    config: dict[str, Any]  # Strategy configuration (matches StrategyRules format)
    expected_win_rate: float  # 0-100 percentage
    avg_return_percent: float  # Average return per trade
    max_drawdown_percent: float  # Maximum historical drawdown
    recommended_for: list[str]  # Market conditions this strategy works best in

# Pre-built strategy templates
STRATEGY_TEMPLATES = [
    StrategyTemplate(
        id="trend-following-macd",
        name="Trend Following (MACD Crossover)",
        description="Follow strong trends using MACD crossover signals and moving averages. Best for trending markets with clear direction.",
        strategy_type="trend_following",
        risk_level="Moderate",
        config={
            "entry_rules": [
                {
                    "indicator": "MACD",
                    "condition": "histogram_positive",
                    "description": "MACD histogram turns positive (bullish crossover)",
                },
                {
                    "indicator": "PRICE",
                    "condition": "above_sma_50",
                    "description": "Price above 50-day moving average",
                },
            ],
            "exit_rules": [
                {
                    "type": "take_profit",
                    "value": 8.0,
                    "description": "Take profit at +8%",
                },
                {"type": "stop_loss", "value": 3.0, "description": "Stop loss at -3%"},
                {
                    "type": "trailing_stop",
                    "value": 2.0,
                    "description": "Trailing stop at -2% from peak",
                },
            ],
            "position_size_percent": 10.0,  # 10% of portfolio per trade
            "max_positions": 5,
            "rsi_period": 14,
            "macd_fast": 12,
            "macd_slow": 26,
            "macd_signal": 9,
        },
        expected_win_rate=55.0,
        avg_return_percent=5.2,
        max_drawdown_percent=12.0,
        recommended_for=["Trending markets", "Tech stocks", "Growth stocks"],
    ),
    StrategyTemplate(
        id="mean-reversion-bb-rsi",
        name="Mean Reversion (Bollinger Bands + RSI)",
        description="Buy oversold stocks and sell overbought stocks using RSI and Bollinger Bands. Works best in ranging markets.",
        strategy_type="mean_reversion",
        risk_level="Conservative",
        config={
            "entry_rules": [
                {
                    "indicator": "RSI",
                    "operator": "<",
                    "value": 30,
                    "description": "RSI oversold below 30",
                },
                {
                    "indicator": "PRICE",
                    "condition": "below_bb_lower",
                    "description": "Price touches lower Bollinger Band",
                },
            ],
            "exit_rules": [
                {
                    "type": "take_profit",
                    "value": 5.0,
                    "description": "Take profit at +5%",
                },
                {
                    "type": "stop_loss",
                    "value": 2.5,
                    "description": "Stop loss at -2.5%",
                },
                {
                    "indicator": "RSI",
                    "operator": ">",
                    "value": 70,
                    "description": "Exit when RSI overbought above 70",
                },
            ],
            "position_size_percent": 8.0,  # 8% of portfolio per trade
            "max_positions": 4,
            "rsi_period": 14,
            "bb_period": 20,
            "bb_std_dev": 2.0,
        },
        expected_win_rate=62.0,
        avg_return_percent=3.8,
        max_drawdown_percent=8.5,
        recommended_for=[
            "Ranging markets",
            "Blue chip stocks",
            "Low volatility periods",
        ],
    ),
    StrategyTemplate(
        id="momentum-breakout",
        name="Momentum Breakout (Volume + Price)",
        description="Catch explosive moves with volume surge and price breakouts. High risk, high reward strategy for aggressive traders.",
        strategy_type="momentum",
        risk_level="Aggressive",
        config={
            "entry_rules": [
                {
                    "indicator": "VOLUME",
                    "condition": "above_avg_volume",
                    "multiplier": 2.0,
                    "description": "Volume 2x above 20-day average",
                },
                {
                    "indicator": "PRICE",
                    "condition": "breakout_resistance",
                    "lookback_days": 20,
                    "description": "Price breaks above 20-day high",
                },
                {
                    "indicator": "RSI",
                    "operator": ">",
                    "value": 60,
                    "description": "RSI above 60 (strong momentum)",
                },
            ],
            "exit_rules": [
                {
                    "type": "take_profit",
                    "value": 12.0,
                    "description": "Take profit at +12%",
                },
                {"type": "stop_loss", "value": 5.0, "description": "Stop loss at -5%"},
                {
                    "indicator": "VOLUME",
                    "condition": "below_avg_volume",
                    "description": "Exit when volume drops below average",
                },
            ],
            "position_size_percent": 15.0,  # 15% of portfolio per trade
            "max_positions": 6,
            "rsi_period": 14,
            "volume_period": 20,
        },
        expected_win_rate=48.0,
        avg_return_percent=8.5,
        max_drawdown_percent=18.0,
        recommended_for=[
            "High volatility markets",
            "Small cap stocks",
            "Momentum stocks",
        ],
    ),
    StrategyTemplate(
        id="volatility-breakout-atr",
        name="Volatility Breakout (ATR Squeeze)",
        description="Trade volatility expansions after quiet periods. Identifies low volatility followed by explosive moves.",
        strategy_type="volatility_breakout",
        risk_level="Moderate",
        config={
            "entry_rules": [
                {
                    "indicator": "BB_WIDTH",
                    "operator": "<",
                    "value": 3.0,
                    "description": "Bollinger Band width below 3% (squeeze)",
                },
                {
                    "indicator": "PRICE",
                    "condition": "breakout_bb",
                    "description": "Price breaks above upper Bollinger Band",
                },
                {
                    "indicator": "ATR",
                    "condition": "rising",
                    "lookback_days": 5,
                    "description": "ATR rising over last 5 days",
                },
            ],
            "exit_rules": [
                {
                    "type": "take_profit",
                    "value": 10.0,
                    "description": "Take profit at +10%",
                },
                {"type": "stop_loss", "value": 4.0, "description": "Stop loss at -4%"},
                {
                    "indicator": "BB_WIDTH",
                    "operator": ">",
                    "value": 6.0,
                    "description": "Exit when BB width exceeds 6% (expansion complete)",
                },
            ],
            "position_size_percent": 12.0,  # 12% of portfolio per trade
            "max_positions": 5,
            "atr_period": 14,
            "bb_period": 20,
            "bb_std_dev": 2.0,
        },
        expected_win_rate=58.0,
        avg_return_percent=6.3,
        max_drawdown_percent=14.0,
        recommended_for=[
            "Volatility expansion periods",
            "Post-earnings plays",
            "Breakout stocks",
        ],
    ),
]

def get_all_templates() -> list[StrategyTemplate]:
    """Get all available strategy templates"""
    return STRATEGY_TEMPLATES

def get_template_by_id(template_id: str) -> StrategyTemplate:
    """Get a specific template by ID"""
    for template in STRATEGY_TEMPLATES:
        if template.id == template_id:
            return template
    raise ValueError(f"Template not found: {template_id}")

def filter_templates_by_risk(risk_tolerance: int) -> list[StrategyTemplate]:
    """
    Filter templates by user's risk tolerance

    Args:
        risk_tolerance: 0-100 (0=ultra-conservative, 100=ultra-aggressive)

    Returns:
        List of templates appropriate for user's risk level
    """
    if risk_tolerance <= 33:
        # Conservative users: Only Conservative templates
        allowed_levels = ["Conservative"]
    elif risk_tolerance <= 66:
        # Moderate users: Conservative + Moderate templates
        allowed_levels = ["Conservative", "Moderate"]
    else:
        # Aggressive users: All templates
        allowed_levels = ["Conservative", "Moderate", "Aggressive"]

    return [t for t in STRATEGY_TEMPLATES if t.risk_level in allowed_levels]

def customize_template_for_risk(template: StrategyTemplate, risk_tolerance: int) -> dict[str, Any]:
    """
    Customize template parameters based on user's risk tolerance

    Adjusts position sizing and stop losses to match user's risk profile.

    Args:
        template: The base template
        risk_tolerance: User's risk tolerance (0-100)

    Returns:
        Customized config dictionary
    """
    config = template.config.copy()

    # Adjust position sizing based on risk tolerance
    base_position_size = config.get("position_size_percent", 10.0)

    if risk_tolerance <= 33:
        # Conservative: Reduce position size by 40%
        config["position_size_percent"] = round(base_position_size * 0.6, 1)
        # Tighten stop losses by 20%
        for rule in config.get("exit_rules", []):
            if rule.get("type") == "stop_loss":
                rule["value"] = round(rule["value"] * 0.8, 1)
    elif risk_tolerance <= 66:
        # Moderate: Keep original position size
        config["position_size_percent"] = base_position_size
    else:
        # Aggressive: Increase position size by 30%
        config["position_size_percent"] = min(20.0, round(base_position_size * 1.3, 1))
        # Widen stop losses by 20% (let winners run)
        for rule in config.get("exit_rules", []):
            if rule.get("type") == "stop_loss":
                rule["value"] = round(rule["value"] * 1.2, 1)

    return config

def get_template_compatibility_score(
    template: StrategyTemplate,
    risk_tolerance: int,
    market_volatility: str,
    portfolio_size: float,
) -> float:
    """
    Calculate compatibility score for template recommendation

    Args:
        template: Strategy template
        risk_tolerance: User's risk tolerance (0-100)
        market_volatility: Current market volatility ("Low", "Medium", "High")
        portfolio_size: User's portfolio value

    Returns:
        Compatibility score (0-100)
    """
    score = 50.0  # Base score

    # Risk compatibility (max +30 points)
    if risk_tolerance <= 33 and template.risk_level == "Conservative":
        score += 30
    elif 34 <= risk_tolerance <= 66 and template.risk_level == "Moderate":
        score += 30
    elif risk_tolerance > 66 and template.risk_level == "Aggressive":
        score += 30
    elif risk_tolerance <= 33 and template.risk_level == "Moderate":
        score += 15  # Partial match
    elif 34 <= risk_tolerance <= 66 and template.risk_level == "Conservative":
        score += 20
    elif risk_tolerance > 66 and template.risk_level == "Moderate":
        score += 20

    # Market condition compatibility (max +20 points)
    if market_volatility == "High":
        if template.strategy_type in ["momentum", "volatility_breakout"]:
            score += 20
        elif template.strategy_type == "mean_reversion":
            score -= 10  # Mean reversion struggles in high volatility
    elif market_volatility == "Low":
        if template.strategy_type == "mean_reversion":
            score += 20
        elif template.strategy_type in ["momentum", "volatility_breakout"]:
            score -= 10
    else:  # Medium volatility
        if template.strategy_type == "trend_following":
            score += 15
        else:
            score += 10

    # Portfolio size compatibility (max +10 points)
    # Smaller portfolios should use fewer positions
    max_positions = template.config.get("max_positions", 5)
    if portfolio_size < 10000:
        if max_positions <= 3:
            score += 10
        elif max_positions > 5:
            score -= 5
    elif portfolio_size < 50000:
        if max_positions <= 5:
            score += 10
    else:  # Large portfolio
        score += 10  # Can handle any number of positions

    return min(100.0, max(0.0, score))

def get_all_strategy_templates() -> list[StrategyTemplate]:
    """
    Get all available strategy templates

    Returns:
        List of all strategy templates
    """
    return STRATEGY_TEMPLATES
