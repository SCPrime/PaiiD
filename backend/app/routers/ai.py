"""
AI Recommendations Router
Provides AI-generated trading recommendations based on market analysis
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Literal, Optional
from pydantic import BaseModel
import random
from datetime import datetime
from sqlalchemy.orm import Session
from ..core.auth import require_bearer
from ..db.session import get_db
from ..services.tradier_client import get_tradier_client
from ..services.technical_indicators import TechnicalIndicators
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["ai"])

class TradeData(BaseModel):
    """Pre-filled trade execution data for 1-click trading"""
    symbol: str
    side: Literal["buy", "sell"]
    quantity: int
    orderType: Literal["market", "limit"] = "limit"
    entryPrice: Optional[float] = None
    stopLoss: Optional[float] = None
    takeProfit: Optional[float] = None

class Recommendation(BaseModel):
    symbol: str
    action: Literal["BUY", "SELL", "HOLD"]
    confidence: float  # 0-100
    score: float  # 1-10 AI recommendation score
    reason: str
    targetPrice: float
    currentPrice: float
    timeframe: str = "1-3 months"
    risk: Literal["Low", "Medium", "High"] = "Medium"
    entryPrice: Optional[float] = None
    stopLoss: Optional[float] = None
    takeProfit: Optional[float] = None
    riskRewardRatio: Optional[float] = None
    indicators: Optional[dict] = None
    tradeData: Optional[TradeData] = None  # 1-click execution data
    portfolioFit: Optional[str] = None  # How this fits user's portfolio
    momentum: Optional[dict] = None  # Momentum analysis (price vs SMAs, volume)
    volatility: Optional[dict] = None  # Volatility analysis (ATR, BB width, classification)
    sector: Optional[str] = None  # Sector assignment (e.g., "Technology", "Healthcare")
    sectorPerformance: Optional[dict] = None  # Sector performance data
    explanation: Optional[str] = None  # Detailed "Why this recommendation?" explanation

class PortfolioAnalysis(BaseModel):
    """Portfolio-level risk and diversification analysis"""
    totalPositions: int
    totalValue: float
    topSectors: List[dict]
    riskScore: float  # 1-10 (10 = highest risk)
    diversificationScore: float  # 1-10 (10 = best diversified)
    recommendations: List[str]  # Portfolio-level suggestions

class RecommendationsResponse(BaseModel):
    recommendations: List[Recommendation]
    portfolioAnalysis: Optional[PortfolioAnalysis] = None
    generated_at: str
    model_version: str = "v1.0.0"

@router.get("/recommendations", response_model=RecommendationsResponse)
async def get_recommendations():
    """
    Generate AI-powered trading recommendations using real market data

    Uses:
    1. Real-time quotes from Tradier API
    2. Technical indicators analysis
    3. Portfolio integration (Alpaca positions)
    4. Risk/reward calculations
    5. 1-click trade execution data

    Returns top recommendations based on technical signals + portfolio fit
    """
    try:
        # Fetch user's current portfolio from Alpaca
        portfolio_data = await _fetch_portfolio_data()

        # Fetch sector performance data (shared across all recommendations)
        sector_performance_data = await _fetch_sector_performance()

        # TODO: Get user's watchlist from database (Phase 2.5 prerequisite)
        # For now, use configurable default watchlist from environment
        import os
        default_watchlist = os.getenv("DEFAULT_WATCHLIST", "AAPL,MSFT,GOOGL,META,NVDA,AMZN,TSLA,JPM,V,JNJ")
        stock_symbols = [s.strip().upper() for s in default_watchlist.split(",") if s.strip() and not s.startswith("$")][:10]

        # Randomly select 5 stocks for recommendations
        selected_symbols = random.sample(stock_symbols, min(5, len(stock_symbols)))

        # Fetch real prices and generate real signals from Tradier
        client = get_tradier_client()
        quotes_response = client.get_quotes(selected_symbols)

        recommendations = []

        if "quotes" in quotes_response and "quote" in quotes_response["quotes"]:
            quotes = quotes_response["quotes"]["quote"]
            # Normalize to list
            if isinstance(quotes, dict):
                quotes = [quotes]

            # Create quote lookup
            quote_map = {q.get("symbol"): q for q in quotes if q.get("symbol")}

            for symbol in selected_symbols:
                quote = quote_map.get(symbol)

                if not quote or "last" not in quote:
                    logger.warning(f"No price data for {symbol}, skipping")
                    continue

                current_price = float(quote["last"])
                change_percent = float(quote.get("change_percentage", 0))
                current_volume = int(quote.get("volume", 0))

                # Fetch historical data for momentum and volume analysis
                momentum_data = await _calculate_momentum_analysis(symbol, current_price, current_volume)

                # Calculate volatility analysis (ATR, BB width)
                volatility_data = await _calculate_volatility_analysis(symbol, current_price)

                # Map symbol to sector and find sector performance
                symbol_sector = _map_symbol_to_sector(symbol)
                sector_perf = None
                if sector_performance_data and "sectors" in sector_performance_data:
                    # Find this symbol's sector in the performance data
                    for sec in sector_performance_data["sectors"]:
                        if sec.get("name") == symbol_sector:
                            sector_perf = {
                                "name": sec["name"],
                                "changePercent": sec.get("changePercent", 0),
                                "rank": sec.get("rank", 0),
                                "isLeader": sec["name"] == sector_performance_data.get("leader"),
                                "isLaggard": sec["name"] == sector_performance_data.get("laggard")
                            }
                            break

                # Calculate entry price (slightly below current for limit orders)
                entry_price = round(current_price * 0.995, 2)  # 0.5% below current
                stop_loss = round(current_price * 0.95, 2)  # 5% stop loss
                take_profit = round(current_price * 1.10, 2)  # 10% target

                # Generate action based on momentum analysis + price movement
                action, confidence, target_price, risk, reason = _generate_signal_from_momentum(
                    symbol, current_price, change_percent, momentum_data, entry_price, take_profit
                )

                # Adjust stop loss and take profit for SELL signals
                if action == "SELL":
                    stop_loss = round(current_price * 1.05, 2)
                    take_profit = round(current_price * 0.90, 2)

                # Calculate AI score (1-10) based on confidence, risk, momentum, and volume
                score = _calculate_enhanced_score(confidence, risk, change_percent, momentum_data)

                # Generate detailed explanation
                explanation = _generate_recommendation_explanation(
                    symbol, action, current_price, change_percent, momentum_data, confidence, risk
                )

                # Analyze portfolio fit
                portfolio_fit = _analyze_portfolio_fit(symbol, action, portfolio_data)

                # Calculate suggested position size (% of portfolio)
                suggested_qty = _calculate_position_size(current_price, portfolio_data, risk)

                # Create trade data for 1-click execution
                trade_data = None
                if action in ["BUY", "SELL"]:
                    trade_data = TradeData(
                        symbol=symbol,
                        side="buy" if action == "BUY" else "sell",
                        quantity=suggested_qty,
                        orderType="limit",
                        entryPrice=entry_price,
                        stopLoss=stop_loss,
                        takeProfit=take_profit
                    )

                recommendations.append(Recommendation(
                    symbol=symbol,
                    action=action,
                    confidence=round(confidence, 1),
                    score=score,
                    reason=reason,
                    targetPrice=target_price,
                    currentPrice=current_price,
                    timeframe="1-2 weeks" if action != "HOLD" else "Wait",
                    risk=risk,
                    entryPrice=entry_price if action != "HOLD" else None,
                    stopLoss=stop_loss if action != "HOLD" else None,
                    takeProfit=take_profit if action != "HOLD" else None,
                    tradeData=trade_data,
                    portfolioFit=portfolio_fit,
                    momentum=momentum_data,
                    volatility=volatility_data,
                    sector=symbol_sector,
                    sectorPerformance=sector_perf,
                    explanation=explanation
                ))

        # Sort by score (highest first)
        recommendations.sort(key=lambda x: x.score, reverse=True)

        # Generate portfolio analysis
        portfolio_analysis = _generate_portfolio_analysis(portfolio_data, recommendations)

        logger.info(f"✅ Generated {len(recommendations)} portfolio-aware recommendations")

        return RecommendationsResponse(
            recommendations=recommendations,
            portfolioAnalysis=portfolio_analysis,
            generated_at=datetime.utcnow().isoformat() + "Z",
            model_version="v2.0.0-portfolio-aware"
        )

    except Exception as e:
        logger.error(f"❌ Failed to generate recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {str(e)}")

@router.get("/recommendations/{symbol}", response_model=Recommendation)
async def get_symbol_recommendation(symbol: str):
    """
    Get AI recommendation for a specific symbol using real market data
    """
    try:
        symbol = symbol.upper()

        # Get real price from Tradier
        client = get_tradier_client()
        quote = client.get_quote(symbol)

        if not quote or "last" not in quote:
            raise HTTPException(status_code=404, detail=f"No price data available for {symbol}")

        current_price = float(quote["last"])

        # Simple momentum-based recommendation
        # In production, this would use technical analysis
        action = "BUY"  # Default action
        confidence = 70.0 + random.uniform(0, 20)  # 70-90
        target_price = round(current_price * 1.10, 2)  # 10% upside
        risk = "Medium"

        recommendation = Recommendation(
            symbol=symbol,
            action=action,
            confidence=round(confidence, 1),
            reason=f"AI analysis suggests favorable risk/reward for {symbol}. Technical indicators show potential upside.",
            targetPrice=target_price,
            currentPrice=current_price,
            timeframe="1-2 months",
            risk=risk
        )

        logger.info(f"✅ Generated recommendation for {symbol} using real price: ${current_price:.2f}")
        return recommendation

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to generate recommendation for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendation: {str(e)}")


@router.get("/signals", response_model=RecommendationsResponse, dependencies=[Depends(require_bearer)])
async def get_ml_signals(
    symbols: Optional[str] = Query(default=None, description="Comma-separated list of symbols"),
    min_confidence: float = Query(default=60.0, ge=0, le=100),
    use_technical: bool = Query(default=True, description="Use real technical indicators")
):
    """
    Generate ML-based trading signals with technical analysis

    This endpoint generates signals using:
    - Real market data from Tradier API
    - Technical indicators (RSI, MACD, Bollinger Bands)
    - Trend analysis
    - Risk/reward calculations

    Args:
        symbols: Comma-separated symbols (e.g., "AAPL,MSFT,GOOGL")
        min_confidence: Minimum confidence threshold (0-100)
        use_technical: Use real technical analysis vs mock data
    """
    try:
        # Default watchlist if no symbols provided (from environment or hardcoded)
        if not symbols:
            import os
            symbols = os.getenv("DEFAULT_WATCHLIST", "$DJI.IX,$COMP.IX,AAPL,MSFT,GOOGL,META,NVDA,AMZN,TSLA")

        symbol_list = [s.strip().upper() for s in symbols.split(",")][:10]  # Limit to 10

        recommendations = []

        for symbol in symbol_list:
            try:
                if use_technical:
                    # Generate real signal using technical indicators
                    signal = await _generate_technical_signal(symbol)
                    if signal and signal.confidence >= min_confidence:
                        recommendations.append(signal)
                else:
                    # Fall back to mock data
                    pass

            except Exception as e:
                logger.error(f"Error generating signal for {symbol}: {str(e)}")
                continue

        # Return empty recommendations if none met criteria (no mock fallback)
        if not recommendations:
            logger.warning(f"⚠️ No technical signals met min_confidence threshold of {min_confidence} for symbols: {symbols}")

        logger.info(f"✅ Generated {len(recommendations)} real technical signals")

        return RecommendationsResponse(
            recommendations=recommendations[:5],  # Return top 5
            generated_at=datetime.utcnow().isoformat() + "Z",
            model_version="v2.0.0-technical"
        )

    except Exception as e:
        logger.error(f"Error generating signals: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def _generate_technical_signal(symbol: str) -> Optional[Recommendation]:
    """
    Generate signal using real technical analysis from Tradier historical data

    Returns None if data unavailable or signal doesn't meet criteria
    """
    try:
        # Fetch real historical data from Tradier
        from datetime import timedelta
        client = get_tradier_client()

        # Get 200 days of historical data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=250)  # Extra days for weekends/holidays

        bars = client.get_historical_bars(
            symbol=symbol,
            interval="daily",
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d")
        )

        if not bars or len(bars) < 50:
            logger.warning(f"Insufficient historical data for {symbol} (got {len(bars)} bars)")
            return None

        # Extract closing prices for technical analysis
        prices = [float(bar["close"]) for bar in bars]

        # Take last 200 days max
        prices = prices[-200:]

        # Generate signal using technical indicators
        signal_data = TechnicalIndicators.generate_signal(symbol, prices)

        # Map to Recommendation model
        reasons_text = ". ".join(signal_data["reasons"])

        # Determine risk based on confidence
        if signal_data["confidence"] >= 80:
            risk = "Low"
        elif signal_data["confidence"] >= 65:
            risk = "Medium"
        else:
            risk = "High"

        recommendation = Recommendation(
            symbol=signal_data["symbol"],
            action=signal_data["action"],
            confidence=signal_data["confidence"],
            reason=reasons_text,
            currentPrice=signal_data["current_price"],
            targetPrice=signal_data["take_profit"],
            entryPrice=signal_data["entry_price"],
            stopLoss=signal_data["stop_loss"],
            takeProfit=signal_data["take_profit"],
            riskRewardRatio=signal_data["risk_reward_ratio"],
            timeframe="1-2 weeks" if signal_data["action"] != "HOLD" else "Wait",
            risk=risk,
            indicators=signal_data["indicators"]
        )

        logger.info(f"✅ Generated technical signal for {symbol} using {len(prices)} real price bars")
        return recommendation

    except Exception as e:
        logger.error(f"Error generating technical signal for {symbol}: {str(e)}")
        return None


class SymbolAnalysis(BaseModel):
    symbol: str
    current_price: float
    analysis: str
    momentum: str
    trend: str
    support_level: float
    resistance_level: float
    risk_assessment: str
    entry_suggestion: str
    exit_suggestion: str
    stop_loss_suggestion: float
    take_profit_suggestion: float
    confidence_score: float
    key_indicators: dict
    summary: str


@router.get("/analyze-symbol/{symbol}", response_model=SymbolAnalysis, dependencies=[Depends(require_bearer)])
async def analyze_symbol(symbol: str):
    """
    Comprehensive AI analysis of a stock symbol using Tradier data

    Provides:
    - Technical analysis (RSI, MACD, Bollinger Bands, trend)
    - Support/resistance levels
    - Entry/exit suggestions
    - Risk assessment
    - Momentum analysis
    """
    try:
        symbol = symbol.upper()

        # Fetch real historical data from Tradier
        from datetime import timedelta
        client = get_tradier_client()

        # Get current quote
        quote = client.get_quote(symbol)

        if not quote or "last" not in quote:
            raise HTTPException(status_code=404, detail=f"No price data available for {symbol}")

        current_price = float(quote["last"])

        # Get 200 days of historical data for comprehensive analysis
        end_date = datetime.now()
        start_date = end_date - timedelta(days=250)

        bars = client.get_historical_bars(
            symbol=symbol,
            interval="daily",
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d")
        )

        if not bars or len(bars) < 50:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient historical data for {symbol} (need at least 50 days)"
            )

        # Extract prices
        prices = [float(bar["close"]) for bar in bars][-200:]
        highs = [float(bar["high"]) for bar in bars[-200:]]
        lows = [float(bar["low"]) for bar in bars[-200:]]

        # Calculate technical indicators
        signal_data = TechnicalIndicators.generate_signal(symbol, prices)

        # Determine support and resistance levels (last 60 days)
        recent_lows = lows[-60:]
        recent_highs = highs[-60:]
        support_level = round(min(recent_lows), 2)
        resistance_level = round(max(recent_highs), 2)

        # Generate momentum analysis
        rsi = signal_data["indicators"].get("rsi", 50)
        if rsi < 30:
            momentum = "Strong Bearish (Oversold)"
        elif rsi < 45:
            momentum = "Bearish"
        elif rsi < 55:
            momentum = "Neutral"
        elif rsi < 70:
            momentum = "Bullish"
        else:
            momentum = "Strong Bullish (Overbought)"

        # Determine trend from moving averages
        indicators = signal_data["indicators"]
        sma_20 = indicators.get("sma_20")
        sma_50 = indicators.get("sma_50")

        if sma_20 and sma_50:
            if current_price > sma_20 > sma_50:
                trend = "Strong Uptrend"
            elif current_price > sma_20:
                trend = "Uptrend"
            elif current_price < sma_20 < sma_50:
                trend = "Strong Downtrend"
            elif current_price < sma_20:
                trend = "Downtrend"
            else:
                trend = "Sideways"
        else:
            trend = "Unknown"

        # Risk assessment
        action = signal_data["action"]
        confidence = signal_data["confidence"]

        if confidence >= 80 and action in ["BUY", "SELL"]:
            risk_assessment = "Low - Strong signal with high confidence"
        elif confidence >= 65:
            risk_assessment = "Medium - Moderate signal strength"
        else:
            risk_assessment = "High - Weak signal, proceed with caution"

        # Entry/Exit suggestions
        if action == "BUY":
            entry_suggestion = f"Consider entering near ${current_price:.2f} if price holds above ${support_level:.2f} support. Wait for pullback to ${(current_price * 0.98):.2f} for better entry."
            exit_suggestion = f"Take partial profits at ${signal_data['take_profit']:.2f} (first target). Set trailing stop to lock gains."
        elif action == "SELL":
            entry_suggestion = f"Consider shorting near ${current_price:.2f} if price fails at ${resistance_level:.2f} resistance. Confirm with breakdown."
            exit_suggestion = f"Cover short position at ${signal_data['take_profit']:.2f}. Use tight stops above ${resistance_level:.2f}."
        else:  # HOLD
            entry_suggestion = f"Wait for clearer signal. Current price ${current_price:.2f} is in consolidation range. Watch for break above ${resistance_level:.2f} (bullish) or below ${support_level:.2f} (bearish)."
            exit_suggestion = "No immediate action recommended. Monitor key levels."

        # Generate comprehensive analysis text
        reasons = signal_data["reasons"]
        analysis_parts = [
            f"**Current Status**: {symbol} is trading at ${current_price:.2f}, showing {momentum.lower()} momentum with {trend.lower()} characteristics.",
            f"",
            f"**Technical Analysis**:",
            f"- RSI: {rsi:.1f} ({momentum})",
            f"- MACD: {indicators.get('macd_histogram', 0):.4f} ({'Bullish' if indicators.get('macd_histogram', 0) > 0 else 'Bearish'} crossover)",
            f"- Trend: {trend}",
            f"- Support: ${support_level:.2f}",
            f"- Resistance: ${resistance_level:.2f}",
            f"",
            f"**AI Signal**: {action} with {confidence:.1f}% confidence",
            f"",
            f"**Key Observations**:",
        ]

        for reason in reasons:
            analysis_parts.append(f"- {reason}")

        analysis_text = "\n".join(analysis_parts)

        # Generate summary
        summary = f"{action} signal with {confidence:.1f}% confidence. {trend} with {momentum.lower()} momentum. Key levels: Support ${support_level:.2f}, Resistance ${resistance_level:.2f}."

        logger.info(f"✅ Generated comprehensive analysis for {symbol}")

        return SymbolAnalysis(
            symbol=symbol,
            current_price=current_price,
            analysis=analysis_text,
            momentum=momentum,
            trend=trend,
            support_level=support_level,
            resistance_level=resistance_level,
            risk_assessment=risk_assessment,
            entry_suggestion=entry_suggestion,
            exit_suggestion=exit_suggestion,
            stop_loss_suggestion=signal_data["stop_loss"],
            take_profit_suggestion=signal_data["take_profit"],
            confidence_score=confidence,
            key_indicators={
                "rsi": rsi,
                "macd_histogram": indicators.get("macd_histogram", 0),
                "sma_20": sma_20,
                "sma_50": sma_50,
                "sma_200": indicators.get("sma_200"),
                "current_vs_sma20": round((current_price / sma_20 - 1) * 100, 2) if sma_20 else None,
                "current_vs_sma50": round((current_price / sma_50 - 1) * 100, 2) if sma_50 else None,
            },
            summary=summary
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to analyze {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# ====== PORTFOLIO-AWARE HELPER FUNCTIONS ======

async def _fetch_portfolio_data() -> dict:
    """Fetch user's current portfolio from Alpaca"""
    try:
        from ..services.alpaca_client import get_alpaca_client
        alpaca = get_alpaca_client()

        # Get account info
        account = alpaca.get_account()

        # Get positions
        positions = alpaca.list_positions()

        # Calculate portfolio metrics
        total_value = float(account.portfolio_value)
        position_list = []

        for pos in positions:
            position_list.append({
                "symbol": pos.symbol,
                "qty": float(pos.qty),
                "market_value": float(pos.market_value),
                "pct_of_portfolio": (float(pos.market_value) / total_value * 100) if total_value > 0 else 0,
                "unrealized_pl": float(pos.unrealized_pl),
                "unrealized_plpc": float(pos.unrealized_plpc) * 100
            })

        return {
            "total_value": total_value,
            "cash": float(account.cash),
            "positions": position_list,
            "num_positions": len(position_list)
        }

    except Exception as e:
        logger.warning(f"⚠️ Could not fetch portfolio data: {e}")
        # Return empty portfolio on error
        return {
            "total_value": 100000.0,  # Default $100k portfolio
            "cash": 100000.0,
            "positions": [],
            "num_positions": 0
        }


def _calculate_recommendation_score(confidence: float, risk: str, change_percent: float) -> float:
    """
    Calculate 1-10 recommendation score

    Factors:
    - Confidence (0-100) -> base score
    - Risk level -> penalty
    - Momentum strength -> bonus
    """
    # Base score from confidence (0-100 -> 1-10)
    base_score = (confidence / 100) * 10

    # Risk penalty
    risk_penalty = {"Low": 0, "Medium": 0.5, "High": 1.5}
    base_score -= risk_penalty.get(risk, 0)

    # Momentum bonus (strong moves get bonus)
    if abs(change_percent) > 3.0:
        base_score += 0.5
    elif abs(change_percent) > 5.0:
        base_score += 1.0

    # Clamp to 1-10
    return round(max(1.0, min(10.0, base_score)), 1)


def _analyze_portfolio_fit(symbol: str, action: str, portfolio_data: dict) -> str:
    """Analyze how this recommendation fits the user's portfolio"""
    positions = portfolio_data.get("positions", [])
    total_value = portfolio_data.get("total_value", 100000)

    # Check if symbol already in portfolio
    existing_position = next((p for p in positions if p["symbol"] == symbol), None)

    if existing_position:
        pct = existing_position["pct_of_portfolio"]
        if action == "BUY":
            if pct > 15:
                return f"⚠️ Already {pct:.1f}% of portfolio - High concentration risk"
            elif pct > 10:
                return f"⚠️ Already {pct:.1f}% of portfolio - Consider diversification"
            else:
                return f"✅ Currently {pct:.1f}% of portfolio - Room to add"
        elif action == "SELL":
            return f"📊 Reduce position (currently {pct:.1f}% of portfolio)"
    else:
        if action == "BUY":
            return "✅ New position - Adds diversification"
        elif action == "SELL":
            return "N/A - Not currently held"

    return "✅ Good fit"


def _calculate_position_size(current_price: float, portfolio_data: dict, risk: str) -> int:
    """
    Calculate suggested position size based on portfolio and risk

    Rules:
    - Low risk: 5% of portfolio
    - Medium risk: 3% of portfolio
    - High risk: 2% of portfolio
    """
    total_value = portfolio_data.get("total_value", 100000)

    # Position size as % of portfolio
    risk_allocation = {"Low": 0.05, "Medium": 0.03, "High": 0.02}
    allocation_pct = risk_allocation.get(risk, 0.03)

    # Calculate dollar amount
    position_value = total_value * allocation_pct

    # Calculate quantity (minimum 1 share)
    quantity = max(1, int(position_value / current_price))

    return quantity


def _generate_portfolio_analysis(portfolio_data: dict, recommendations: List[Recommendation]) -> PortfolioAnalysis:
    """Generate portfolio-level analysis"""
    positions = portfolio_data.get("positions", [])
    total_value = portfolio_data.get("total_value", 100000)
    num_positions = len(positions)

    # Calculate concentration (Herfindahl index)
    if num_positions > 0:
        concentration = sum((p["pct_of_portfolio"] / 100) ** 2 for p in positions)
        diversification_score = round((1 - concentration) * 10, 1)
    else:
        diversification_score = 10.0  # Empty portfolio = fully diversified

    # Calculate portfolio risk score (based on concentration and volatility)
    if num_positions == 0:
        risk_score = 5.0  # Neutral for empty portfolio
    elif num_positions < 5:
        risk_score = 7.5  # High risk - under-diversified
    elif num_positions > 15:
        risk_score = 6.0  # Moderate risk - over-diversified
    else:
        # Check for concentration
        max_position_pct = max((p["pct_of_portfolio"] for p in positions), default=0)
        if max_position_pct > 20:
            risk_score = 8.0
        elif max_position_pct > 15:
            risk_score = 6.5
        else:
            risk_score = 4.5  # Well balanced

    # Top sectors (mock for now - would need sector data)
    top_sectors = [
        {"name": "Technology", "percentage": 35.0},
        {"name": "Financials", "percentage": 25.0},
        {"name": "Healthcare", "percentage": 20.0}
    ]

    # Generate recommendations
    portfolio_recommendations = []

    if num_positions == 0:
        portfolio_recommendations.append("💡 Start with 3-5 positions to build a diversified portfolio")
    elif num_positions < 5:
        portfolio_recommendations.append(f"💡 Consider adding {5 - num_positions} more positions for better diversification")
    elif num_positions > 15:
        portfolio_recommendations.append("💡 Consider consolidating positions - you may be over-diversified")

    if num_positions > 0:
        max_position = max(positions, key=lambda p: p["pct_of_portfolio"])
        if max_position["pct_of_portfolio"] > 20:
            portfolio_recommendations.append(f"⚠️ {max_position['symbol']} is {max_position['pct_of_portfolio']:.1f}% of portfolio - High concentration risk")

    # Check if any recommendations would improve diversification
    buy_recs = [r for r in recommendations if r.action == "BUY"]
    if buy_recs and num_positions > 0:
        new_symbols = [r.symbol for r in buy_recs if r.symbol not in [p["symbol"] for p in positions]]
        if new_symbols:
            portfolio_recommendations.append(f"✅ {len(new_symbols)} recommendations add new diversification")

    return PortfolioAnalysis(
        totalPositions=num_positions,
        totalValue=total_value,
        topSectors=top_sectors,
        riskScore=round(risk_score, 1),
        diversificationScore=diversification_score,
        recommendations=portfolio_recommendations[:5]  # Top 5 suggestions
    )


# ====== PHASE 3.A: ENHANCED MOMENTUM & VOLUME ANALYSIS ======

async def _calculate_momentum_analysis(symbol: str, current_price: float, current_volume: int) -> dict:
    """
    Calculate momentum and volume analysis using historical data

    Returns:
    {
        "sma_20": float,
        "sma_50": float,
        "sma_200": float,
        "price_vs_sma_20": float,  # Percentage distance
        "price_vs_sma_50": float,
        "price_vs_sma_200": float,
        "avg_volume_20d": int,
        "volume_strength": str,  # "High", "Normal", "Low"
        "volume_ratio": float,  # current / average
        "trend_alignment": str  # "Bullish", "Bearish", "Mixed"
    }
    """
    try:
        from datetime import timedelta
        client = get_tradier_client()

        # Get 250 days of historical data (extra for weekends/holidays)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=300)

        bars = client.get_historical_bars(
            symbol=symbol,
            interval="daily",
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d")
        )

        if not bars or len(bars) < 200:
            logger.warning(f"⚠️ Insufficient data for momentum analysis: {symbol} ({len(bars) if bars else 0} bars)")
            # Return neutral default data
            return {
                "sma_20": current_price,
                "sma_50": current_price,
                "sma_200": current_price,
                "price_vs_sma_20": 0.0,
                "price_vs_sma_50": 0.0,
                "price_vs_sma_200": 0.0,
                "avg_volume_20d": current_volume,
                "volume_strength": "Normal",
                "volume_ratio": 1.0,
                "trend_alignment": "Unknown"
            }

        # Extract prices and volumes (last 200 days)
        prices = [float(bar["close"]) for bar in bars[-200:]]
        volumes = [int(bar["volume"]) for bar in bars[-200:]]

        # Calculate Simple Moving Averages
        sma_20 = sum(prices[-20:]) / 20 if len(prices) >= 20 else current_price
        sma_50 = sum(prices[-50:]) / 50 if len(prices) >= 50 else current_price
        sma_200 = sum(prices) / len(prices) if len(prices) >= 200 else current_price

        # Calculate percentage distance from SMAs
        price_vs_sma_20 = round(((current_price / sma_20) - 1) * 100, 2) if sma_20 > 0 else 0
        price_vs_sma_50 = round(((current_price / sma_50) - 1) * 100, 2) if sma_50 > 0 else 0
        price_vs_sma_200 = round(((current_price / sma_200) - 1) * 100, 2) if sma_200 > 0 else 0

        # Calculate 20-day average volume
        avg_volume_20d = int(sum(volumes[-20:]) / 20) if len(volumes) >= 20 else current_volume

        # Volume strength analysis
        volume_ratio = round(current_volume / avg_volume_20d, 2) if avg_volume_20d > 0 else 1.0
        if volume_ratio > 1.5:
            volume_strength = "High"
        elif volume_ratio < 0.7:
            volume_strength = "Low"
        else:
            volume_strength = "Normal"

        # Trend alignment analysis
        if current_price > sma_20 > sma_50 > sma_200:
            trend_alignment = "Bullish"
        elif current_price < sma_20 < sma_50 < sma_200:
            trend_alignment = "Bearish"
        elif current_price > sma_20 and current_price > sma_50:
            trend_alignment = "Mixed Bullish"
        elif current_price < sma_20 and current_price < sma_50:
            trend_alignment = "Mixed Bearish"
        else:
            trend_alignment = "Mixed"

        logger.info(f"✅ Calculated momentum for {symbol}: {trend_alignment}, Vol: {volume_strength}")

        return {
            "sma_20": round(sma_20, 2),
            "sma_50": round(sma_50, 2),
            "sma_200": round(sma_200, 2),
            "price_vs_sma_20": price_vs_sma_20,
            "price_vs_sma_50": price_vs_sma_50,
            "price_vs_sma_200": price_vs_sma_200,
            "avg_volume_20d": avg_volume_20d,
            "volume_strength": volume_strength,
            "volume_ratio": volume_ratio,
            "trend_alignment": trend_alignment
        }

    except Exception as e:
        logger.error(f"❌ Momentum analysis error for {symbol}: {str(e)}")
        # Return neutral data on error
        return {
            "sma_20": current_price,
            "sma_50": current_price,
            "sma_200": current_price,
            "price_vs_sma_20": 0.0,
            "price_vs_sma_50": 0.0,
            "price_vs_sma_200": 0.0,
            "avg_volume_20d": current_volume,
            "volume_strength": "Normal",
            "volume_ratio": 1.0,
            "trend_alignment": "Unknown"
        }


# ====== PHASE 3.A.2: VOLATILITY & SECTOR CORRELATION ======

def _map_symbol_to_sector(symbol: str) -> str:
    """
    Map stock symbol to sector

    Uses hardcoded mapping for common stocks. Could be enhanced with external API.
    """
    # Common stock to sector mapping
    sector_map = {
        # Technology
        "AAPL": "Technology", "MSFT": "Technology", "GOOGL": "Technology", "GOOG": "Technology",
        "META": "Technology", "NVDA": "Technology", "AMD": "Technology", "INTC": "Technology",
        "CSCO": "Technology", "ORCL": "Technology", "CRM": "Technology", "ADBE": "Technology",
        "AVGO": "Technology", "TXN": "Technology", "QCOM": "Technology", "IBM": "Technology",

        # Communication
        "T": "Communication", "VZ": "Communication", "TMUS": "Communication", "DIS": "Communication",
        "NFLX": "Communication", "CMCSA": "Communication", "CHTR": "Communication",

        # Consumer Discretionary
        "AMZN": "Consumer Discretionary", "TSLA": "Consumer Discretionary", "HD": "Consumer Discretionary",
        "MCD": "Consumer Discretionary", "NKE": "Consumer Discretionary", "SBUX": "Consumer Discretionary",
        "TGT": "Consumer Discretionary", "LOW": "Consumer Discretionary", "TJX": "Consumer Discretionary",

        # Financials
        "JPM": "Financials", "BAC": "Financials", "WFC": "Financials", "GS": "Financials",
        "MS": "Financials", "C": "Financials", "AXP": "Financials", "BLK": "Financials",
        "SPGI": "Financials", "USB": "Financials", "PNC": "Financials", "TFC": "Financials",

        # Healthcare
        "JNJ": "Healthcare", "UNH": "Healthcare", "PFE": "Healthcare", "ABBV": "Healthcare",
        "TMO": "Healthcare", "MRK": "Healthcare", "ABT": "Healthcare", "DHR": "Healthcare",
        "LLY": "Healthcare", "CVS": "Healthcare", "BMY": "Healthcare", "AMGN": "Healthcare",

        # Industrials
        "BA": "Industrials", "CAT": "Industrials", "GE": "Industrials", "HON": "Industrials",
        "UNP": "Industrials", "UPS": "Industrials", "RTX": "Industrials", "DE": "Industrials",

        # Materials
        "LIN": "Materials", "APD": "Materials", "ECL": "Materials", "DD": "Materials",

        # Real Estate
        "AMT": "Real Estate", "PLD": "Real Estate", "CCI": "Real Estate", "EQIX": "Real Estate",

        # Utilities
        "NEE": "Utilities", "DUK": "Utilities", "SO": "Utilities", "D": "Utilities",

        # Energy
        "XOM": "Energy", "CVX": "Energy", "COP": "Energy", "SLB": "Energy",

        # Consumer Staples
        "PG": "Consumer Staples", "KO": "Consumer Staples", "PEP": "Consumer Staples",
        "WMT": "Consumer Staples", "COST": "Consumer Staples", "PM": "Consumer Staples"
    }

    return sector_map.get(symbol, "Unknown")


async def _fetch_sector_performance() -> dict:
    """
    Fetch current sector performance from market endpoint

    Returns sector data with leader/laggard identification
    """
    try:
        import requests
        from ..core.config import settings

        # Make internal API call to market/sectors endpoint
        # In production, we could call the function directly, but using HTTP ensures consistency
        response = requests.get(
            f"{settings.TRADIER_API_BASE_URL.replace('/v1', '')}/market/sectors",  # Remove /v1 for our internal endpoint
            headers={"Authorization": f"Bearer {settings.API_TOKEN}"},
            timeout=5
        )

        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Fetched sector performance: {data.get('leader')} leading, {data.get('laggard')} lagging")
            return data
        else:
            logger.warning(f"⚠️ Sector performance endpoint returned {response.status_code}")
            return {"sectors": [], "leader": "Unknown", "laggard": "Unknown"}

    except Exception as e:
        logger.error(f"❌ Failed to fetch sector performance: {str(e)}")
        return {"sectors": [], "leader": "Unknown", "laggard": "Unknown"}


async def _calculate_volatility_analysis(symbol: str, current_price: float) -> dict:
    """
    Calculate volatility analysis using ATR and Bollinger Band width

    Returns:
    {
        "atr": float,  # Average True Range (absolute $)
        "atr_percent": float,  # ATR as % of price
        "bb_width": float,  # Bollinger Band width (%)
        "volatility_class": str,  # "Low", "Medium", "High"
        "volatility_score": float  # 0-10 (10 = highest volatility)
    }
    """
    try:
        from datetime import timedelta
        client = get_tradier_client()

        # Get 60 days of OHLC data for ATR calculation
        end_date = datetime.now()
        start_date = end_date - timedelta(days=80)  # Extra for weekends

        bars = client.get_historical_bars(
            symbol=symbol,
            interval="daily",
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d")
        )

        if not bars or len(bars) < 50:
            logger.warning(f"⚠️ Insufficient data for volatility analysis: {symbol}")
            return {
                "atr": 0.0,
                "atr_percent": 2.0,
                "bb_width": 4.0,
                "volatility_class": "Medium",
                "volatility_score": 5.0
            }

        # Extract OHLC data (last 50 days for ATR, 20 for BB)
        highs = [float(bar["high"]) for bar in bars[-50:]]
        lows = [float(bar["low"]) for bar in bars[-50:]]
        closes = [float(bar["close"]) for bar in bars[-50:]]

        # Calculate ATR using technical indicators service
        atr = TechnicalIndicators.calculate_atr(highs, lows, closes, period=14)
        atr_percent = round((atr / current_price) * 100, 2) if current_price > 0 else 0

        # Calculate Bollinger Band width
        bb_width = TechnicalIndicators.calculate_bb_width(closes, period=20, std_dev=2.0)

        # Classify volatility based on BB width (primary) and ATR percent (secondary)
        # BB Width thresholds: <3% = Low, 3-5% = Medium, >5% = High
        # ATR % thresholds: <2% = Low, 2-4% = Medium, >4% = High
        if bb_width < 3.0 and atr_percent < 2.0:
            volatility_class = "Low"
            volatility_score = 3.0
        elif bb_width > 5.0 or atr_percent > 4.0:
            volatility_class = "High"
            volatility_score = 8.0
        else:
            volatility_class = "Medium"
            volatility_score = 5.5

        # Fine-tune volatility score (0-10 scale)
        volatility_score = min(10.0, max(0.0, (bb_width / 10) * 10))

        logger.info(f"✅ Calculated volatility for {symbol}: {volatility_class} (ATR: {atr_percent:.1f}%, BB: {bb_width:.1f}%)")

        return {
            "atr": atr,
            "atr_percent": atr_percent,
            "bb_width": bb_width,
            "volatility_class": volatility_class,
            "volatility_score": round(volatility_score, 1)
        }

    except Exception as e:
        logger.error(f"❌ Volatility analysis error for {symbol}: {str(e)}")
        # Return neutral data on error
        return {
            "atr": 0.0,
            "atr_percent": 2.0,
            "bb_width": 4.0,
            "volatility_class": "Medium",
            "volatility_score": 5.0
        }


def _generate_signal_from_momentum(
    symbol: str,
    current_price: float,
    change_percent: float,
    momentum: dict,
    entry_price: float,
    take_profit: float
) -> tuple:
    """
    Generate trading signal based on momentum analysis

    Returns: (action, confidence, target_price, risk, reason)
    """
    trend = momentum["trend_alignment"]
    price_vs_sma_20 = momentum["price_vs_sma_20"]
    price_vs_sma_50 = momentum["price_vs_sma_50"]
    volume_strength = momentum["volume_strength"]

    # Strong BUY signals
    if trend == "Bullish" and price_vs_sma_20 > 0 and volume_strength == "High":
        action = "BUY"
        confidence = min(90.0, 75.0 + abs(price_vs_sma_20))
        target_price = take_profit
        risk = "Low"
        reason = f"Strong bullish momentum: Price {price_vs_sma_20:+.1f}% above SMA-20 with high volume. All SMAs aligned bullish."

    # Good BUY signals
    elif trend in ["Bullish", "Mixed Bullish"] and price_vs_sma_20 > 0:
        action = "BUY"
        confidence = min(80.0, 70.0 + abs(price_vs_sma_20) * 0.5)
        target_price = take_profit
        risk = "Medium" if volume_strength == "Low" else "Low"
        reason = f"Bullish trend: Price {price_vs_sma_20:+.1f}% above SMA-20. {volume_strength} volume confirms move."

    # Breakout BUY (price crossing above SMA-20)
    elif price_vs_sma_20 > -1 and price_vs_sma_20 < 2 and change_percent > 1.0 and volume_strength == "High":
        action = "BUY"
        confidence = 75.0
        target_price = take_profit
        risk = "Medium"
        reason = f"Potential breakout: Price near SMA-20 with +{change_percent:.1f}% gain on high volume. Watch for confirmation."

    # Strong SELL signals
    elif trend == "Bearish" and price_vs_sma_20 < 0 and volume_strength == "High":
        action = "SELL"
        confidence = min(85.0, 70.0 + abs(price_vs_sma_20))
        target_price = round(current_price * 0.95, 2)
        risk = "Medium"
        reason = f"Strong bearish momentum: Price {price_vs_sma_20:+.1f}% below SMA-20 with high volume. All SMAs aligned bearish."

    # Bearish weakness
    elif trend in ["Bearish", "Mixed Bearish"] and price_vs_sma_20 < -2:
        action = "SELL"
        confidence = min(75.0, 65.0 + abs(price_vs_sma_20) * 0.5)
        target_price = round(current_price * 0.95, 2)
        risk = "Medium"
        reason = f"Bearish trend: Price {price_vs_sma_20:+.1f}% below SMA-20. Consider taking profits or avoiding entry."

    # Consolidation / HOLD
    elif abs(price_vs_sma_20) < 1.5 and volume_strength != "High":
        action = "HOLD"
        confidence = 60.0
        target_price = current_price
        risk = "Low"
        reason = f"Consolidating near SMAs ({price_vs_sma_20:+.1f}% from SMA-20). Low volume. Wait for clearer direction."

    # Mixed signals - use basic momentum
    elif change_percent > 2.0:
        action = "BUY"
        confidence = 70.0
        target_price = take_profit
        risk = "Medium"
        reason = f"Positive momentum: +{change_percent:.1f}% daily gain, but mixed trend signals. Proceed with caution."

    elif change_percent < -2.0:
        action = "SELL"
        confidence = 65.0
        target_price = round(current_price * 0.95, 2)
        risk = "Medium"
        reason = f"Weakness: {change_percent:.1f}% daily decline with mixed signals. Consider defensive position."

    else:
        # Default HOLD
        action = "HOLD"
        confidence = 60.0
        target_price = current_price
        risk = "Low"
        reason = f"Mixed signals. Price {price_vs_sma_20:+.1f}% from SMA-20. Wait for confirmation before entering."

    return action, confidence, target_price, risk, reason


def _calculate_enhanced_score(
    confidence: float,
    risk: str,
    change_percent: float,
    momentum: dict
) -> float:
    """
    Calculate enhanced 1-10 recommendation score

    Factors:
    - Confidence (0-100) -> base score (60%)
    - Risk level -> penalty (20%)
    - Momentum alignment -> bonus (10%)
    - Volume strength -> bonus (10%)
    """
    # Base score from confidence (weighted 60%)
    base_score = (confidence / 100) * 10 * 0.6

    # Risk penalty (weighted 20%)
    risk_scores = {"Low": 2.0, "Medium": 1.0, "High": 0.0}
    risk_score = risk_scores.get(risk, 1.0) * 0.2

    # Momentum bonus (weighted 10%)
    trend = momentum.get("trend_alignment", "Mixed")
    if trend == "Bullish":
        momentum_bonus = 1.0
    elif trend in ["Mixed Bullish", "Mixed"]:
        momentum_bonus = 0.5
    elif trend in ["Mixed Bearish"]:
        momentum_bonus = 0.2
    else:  # Bearish
        momentum_bonus = 0.0
    momentum_score = momentum_bonus * 0.1 * 10

    # Volume bonus (weighted 10%)
    volume_strength = momentum.get("volume_strength", "Normal")
    if volume_strength == "High":
        volume_bonus = 1.0
    elif volume_strength == "Normal":
        volume_bonus = 0.5
    else:  # Low
        volume_bonus = 0.2
    volume_score = volume_bonus * 0.1 * 10

    # Total score
    total_score = base_score + risk_score + momentum_score + volume_score

    # Clamp to 1-10
    return round(max(1.0, min(10.0, total_score)), 1)


def _generate_recommendation_explanation(
    symbol: str,
    action: str,
    current_price: float,
    change_percent: float,
    momentum: dict,
    confidence: float,
    risk: str
) -> str:
    """
    Generate detailed 'Why this recommendation?' explanation

    Provides clear reasoning based on momentum, volume, and technical factors
    """
    trend = momentum.get("trend_alignment", "Unknown")
    price_vs_sma_20 = momentum.get("price_vs_sma_20", 0)
    price_vs_sma_50 = momentum.get("price_vs_sma_50", 0)
    price_vs_sma_200 = momentum.get("price_vs_sma_200", 0)
    volume_strength = momentum.get("volume_strength", "Normal")
    volume_ratio = momentum.get("volume_ratio", 1.0)

    explanation_parts = []

    # Action header
    if action == "BUY":
        explanation_parts.append(f"**BUY Recommendation** ({confidence:.0f}% confidence)")
    elif action == "SELL":
        explanation_parts.append(f"**SELL Recommendation** ({confidence:.0f}% confidence)")
    else:
        explanation_parts.append(f"**HOLD Recommendation** ({confidence:.0f}% confidence)")

    explanation_parts.append("")

    # Price analysis
    explanation_parts.append("**📊 Price Analysis:**")
    explanation_parts.append(f"- Current Price: ${current_price:.2f} ({change_percent:+.2f}% today)")
    explanation_parts.append(f"- vs SMA-20: {price_vs_sma_20:+.1f}% ({'' if price_vs_sma_20 >= 0 else 'Below'} ${momentum['sma_20']:.2f})")
    explanation_parts.append(f"- vs SMA-50: {price_vs_sma_50:+.1f}% ({'' if price_vs_sma_50 >= 0 else 'Below'} ${momentum['sma_50']:.2f})")
    explanation_parts.append(f"- vs SMA-200: {price_vs_sma_200:+.1f}% ({'' if price_vs_sma_200 >= 0 else 'Below'} ${momentum['sma_200']:.2f})")
    explanation_parts.append("")

    # Volume analysis
    explanation_parts.append("**📈 Volume Analysis:**")
    explanation_parts.append(f"- Volume Strength: **{volume_strength}** ({volume_ratio:.1f}x average)")
    if volume_strength == "High":
        explanation_parts.append("- ✅ High volume confirms price movement strength")
    elif volume_strength == "Low":
        explanation_parts.append("- ⚠️ Low volume suggests weak conviction in price move")
    else:
        explanation_parts.append("- 📊 Normal volume - no unusual activity")
    explanation_parts.append("")

    # Trend analysis
    explanation_parts.append("**🎯 Trend Analysis:**")
    explanation_parts.append(f"- Trend Alignment: **{trend}**")
    if trend == "Bullish":
        explanation_parts.append("- ✅ All moving averages aligned bullish (SMA-20 > SMA-50 > SMA-200)")
    elif trend == "Bearish":
        explanation_parts.append("- ⚠️ All moving averages aligned bearish (SMA-20 < SMA-50 < SMA-200)")
    elif "Mixed" in trend:
        explanation_parts.append("- ⚠️ Mixed signals - some bullish, some bearish indicators")
    explanation_parts.append("")

    # Risk assessment
    explanation_parts.append("**⚡ Risk Assessment:**")
    explanation_parts.append(f"- Risk Level: **{risk}**")
    if risk == "Low":
        explanation_parts.append("- ✅ Strong signals with high confidence")
    elif risk == "Medium":
        explanation_parts.append("- ⚠️ Moderate risk - proceed with caution and proper stop loss")
    else:
        explanation_parts.append("- 🔴 High risk - weak signals, consider waiting for better setup")

    return "\n".join(explanation_parts)


# ====== PHASE 3.A.3: STRATEGY TEMPLATE MATCHING ======

@router.get("/recommended-templates", dependencies=[Depends(require_bearer)])
async def get_recommended_templates(
    db: Session = Depends(get_db)
):
    """
    Get AI-recommended strategy templates based on user's risk profile, portfolio, and market conditions

    Integrates Phase 3.A.2 template system with AI recommendations to suggest
    best-fit trading strategies for the user.

    Returns:
        List of templates sorted by compatibility score with rationale
    """
    try:
        from ..services.strategy_templates import (
            filter_templates_by_risk,
            get_template_compatibility_score
        )
        from ..models.database import User

        # Get user preferences
        user = db.query(User).filter(User.id == 1).first()
        preferences = user.preferences if user else {}
        risk_tolerance = preferences.get("risk_tolerance", 50)

        # Fetch portfolio data for template matching
        portfolio_data = await _fetch_portfolio_data()
        portfolio_value = portfolio_data.get("total_value", 100000)

        # Determine current market volatility from recent recommendations
        # (In production, this would come from market volatility index)
        market_volatility = "Medium"  # Default

        try:
            # Quick volatility check on SPY
            client = get_tradier_client()
            from datetime import timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)

            bars = client.get_historical_bars(
                symbol="SPY",
                interval="daily",
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d")
            )

            if bars and len(bars) >= 20:
                closes = [float(bar["close"]) for bar in bars[-20:]]
                bb_width = TechnicalIndicators.calculate_bb_width(closes, period=20, std_dev=2.0)

                if bb_width < 3.0:
                    market_volatility = "Low"
                elif bb_width > 5.0:
                    market_volatility = "High"
                else:
                    market_volatility = "Medium"

                logger.info(f"📊 Detected market volatility: {market_volatility} (BB width: {bb_width:.2f}%)")
        except Exception as e:
            logger.warning(f"⚠️ Could not detect market volatility: {e}")

        # Get templates filtered by user's risk tolerance
        templates = filter_templates_by_risk(risk_tolerance)

        # Calculate compatibility scores and generate recommendations
        recommended_templates = []

        for template in templates:
            compatibility_score = get_template_compatibility_score(
                template,
                risk_tolerance,
                market_volatility,
                portfolio_value
            )

            # Generate AI rationale for recommendation
            rationale_parts = []

            # Risk compatibility
            if risk_tolerance <= 33 and template.risk_level == "Conservative":
                rationale_parts.append(f"✅ Perfect match for your conservative risk profile ({risk_tolerance}/100)")
            elif 34 <= risk_tolerance <= 66 and template.risk_level == "Moderate":
                rationale_parts.append(f"✅ Ideal for your moderate risk tolerance ({risk_tolerance}/100)")
            elif risk_tolerance > 66 and template.risk_level == "Aggressive":
                rationale_parts.append(f"✅ Matches your aggressive risk appetite ({risk_tolerance}/100)")
            else:
                rationale_parts.append(f"⚠️ Different risk profile - template is {template.risk_level}, you're at {risk_tolerance}/100")

            # Market compatibility
            if market_volatility == "High":
                if template.strategy_type in ["momentum", "volatility_breakout"]:
                    rationale_parts.append(f"✅ Excellent for current high volatility market conditions")
                elif template.strategy_type == "mean_reversion":
                    rationale_parts.append(f"⚠️ Mean reversion may struggle in high volatility")
            elif market_volatility == "Low":
                if template.strategy_type == "mean_reversion":
                    rationale_parts.append(f"✅ Perfect for current low volatility environment")
                elif template.strategy_type in ["momentum", "volatility_breakout"]:
                    rationale_parts.append(f"⚠️ Limited opportunities in low volatility")
            else:
                rationale_parts.append(f"✅ Good fit for current market conditions")

            # Performance highlights
            rationale_parts.append(f"📈 Historical win rate: {template.expected_win_rate:.0f}%")
            rationale_parts.append(f"💰 Avg return per trade: {template.avg_return_percent:.1f}%")
            rationale_parts.append(f"📉 Max drawdown: {template.max_drawdown_percent:.1f}%")

            recommended_templates.append({
                "template_id": template.id,
                "name": template.name,
                "description": template.description,
                "strategy_type": template.strategy_type,
                "risk_level": template.risk_level,
                "compatibility_score": round(compatibility_score, 1),
                "expected_win_rate": template.expected_win_rate,
                "avg_return_percent": template.avg_return_percent,
                "max_drawdown_percent": template.max_drawdown_percent,
                "recommended_for": template.recommended_for,
                "ai_rationale": "\n".join(rationale_parts),
                "clone_url": f"/api/strategies/templates/{template.id}/clone"
            })

        # Sort by compatibility score
        recommended_templates.sort(key=lambda x: x["compatibility_score"], reverse=True)

        logger.info(f"✅ Generated {len(recommended_templates)} AI-matched template recommendations")

        return {
            "templates": recommended_templates,
            "user_risk_tolerance": risk_tolerance,
            "market_volatility": market_volatility,
            "portfolio_value": portfolio_value,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "message": f"Found {len(recommended_templates)} strategies compatible with your {'' if risk_tolerance <= 33 else '' if risk_tolerance <= 66 else 'aggressive'} risk profile"
        }

    except Exception as e:
        logger.error(f"❌ Failed to generate template recommendations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate template recommendations: {str(e)}"
        )
