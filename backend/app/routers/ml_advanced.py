"""
Advanced ML API Endpoints
Enhanced ML features for PaiiD trading platform
"""

import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime, timedelta

from ..core.unified_auth import get_current_user_unified
from ..models.database import User
from ..ml.advanced_patterns import AdvancedPatternDetector, PatternSignal, PatternType
from ..ml.regime_detection import AdvancedRegimeDetector, RegimeAnalysis, MarketRegime
from ..services.market_data import MarketDataService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ml/advanced", tags=["ml-advanced"])

# Initialize ML services
pattern_detector = AdvancedPatternDetector()
regime_detector = AdvancedRegimeDetector()
market_data_service = MarketDataService()


class PatternDetectionRequest(BaseModel):
    """Request model for pattern detection"""
    symbol: str = Field(..., description="Stock symbol to analyze")
    timeframe: str = Field(default="1d", description="Timeframe for analysis")
    lookback_days: int = Field(default=90, description="Number of days to look back")
    min_confidence: float = Field(default=0.6, description="Minimum confidence threshold")


class PatternDetectionResponse(BaseModel):
    """Response model for pattern detection"""
    symbol: str
    patterns: List[Dict[str, Any]]
    total_patterns: int
    analysis_timestamp: datetime
    timeframe: str
    confidence_summary: Dict[str, int]


class RegimeDetectionRequest(BaseModel):
    """Request model for regime detection"""
    symbol: str = Field(..., description="Stock symbol to analyze")
    timeframe: str = Field(default="1d", description="Timeframe for analysis")
    lookback_days: int = Field(default=252, description="Number of days to look back")
    include_market_data: bool = Field(default=True, description="Include market-wide data")


class RegimeDetectionResponse(BaseModel):
    """Response model for regime detection"""
    symbol: str
    current_regime: str
    confidence: float
    regime_strength: str
    trend_direction: str
    volatility_level: str
    momentum_score: float
    regime_duration: int
    regime_probabilities: Dict[str, float]
    key_indicators: Dict[str, float]
    trading_implications: List[str]
    risk_level: str
    recommended_strategies: List[str]
    analysis_timestamp: datetime


class MLInsightsRequest(BaseModel):
    """Request model for comprehensive ML insights"""
    symbol: str = Field(..., description="Stock symbol to analyze")
    analysis_type: str = Field(default="comprehensive", description="Type of analysis")
    include_patterns: bool = Field(default=True, description="Include pattern detection")
    include_regime: bool = Field(default=True, description="Include regime detection")
    include_sentiment: bool = Field(default=True, description="Include sentiment analysis")


class MLInsightsResponse(BaseModel):
    """Response model for comprehensive ML insights"""
    symbol: str
    analysis_timestamp: datetime
    patterns: Optional[Dict[str, Any]] = None
    regime: Optional[Dict[str, Any]] = None
    sentiment: Optional[Dict[str, Any]] = None
    overall_score: float
    trading_recommendation: str
    risk_assessment: str
    key_insights: List[str]


@router.post("/patterns/detect", response_model=PatternDetectionResponse)
async def detect_patterns(
    request: PatternDetectionRequest,
    current_user: User = Depends(get_current_user_unified)
):
    """
    Detect advanced chart patterns using ML algorithms
    
    This endpoint uses sophisticated pattern recognition algorithms to identify:
    - Reversal patterns (Head & Shoulders, Double Top/Bottom, etc.)
    - Continuation patterns (Triangles, Flags, Pennants)
    - Candlestick patterns (Hammer, Doji, Engulfing, etc.)
    - Volume patterns (Volume spikes, divergences)
    - Support/Resistance breaks
    """
    try:
        logger.info(f"Pattern detection requested for {request.symbol}")
        
        # Get market data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=request.lookback_days)
        
        # Fetch OHLCV data
        ohlcv_data = await market_data_service.get_historical_data(
            symbol=request.symbol,
            start_date=start_date,
            end_date=end_date,
            timeframe=request.timeframe
        )
        
        if ohlcv_data.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No data available for symbol {request.symbol}"
            )
        
        # Get volume data
        volume_data = ohlcv_data.get('volume')
        
        # Detect patterns
        patterns = pattern_detector.detect_patterns(ohlcv_data, volume_data)
        
        # Filter by confidence
        filtered_patterns = [
            p for p in patterns 
            if p.confidence >= request.min_confidence
        ]
        
        # Convert to response format
        pattern_dicts = []
        for pattern in filtered_patterns:
            pattern_dicts.append({
                "pattern_type": pattern.pattern_type.value,
                "confidence": pattern.confidence,
                "strength": pattern.strength,
                "direction": pattern.direction,
                "target_price": pattern.target_price,
                "stop_loss": pattern.stop_loss,
                "risk_reward_ratio": pattern.risk_reward_ratio,
                "timeframe": pattern.timeframe,
                "volume_confirmation": pattern.volume_confirmation,
                "trend_alignment": pattern.trend_alignment,
                "key_levels": pattern.key_levels,
                "description": pattern.description,
                "trading_suggestion": pattern.trading_suggestion
            })
        
        # Calculate confidence summary
        confidence_summary = {
            "very_strong": len([p for p in filtered_patterns if p.confidence >= 0.8]),
            "strong": len([p for p in filtered_patterns if 0.7 <= p.confidence < 0.8]),
            "moderate": len([p for p in filtered_patterns if 0.6 <= p.confidence < 0.7]),
            "weak": len([p for p in filtered_patterns if p.confidence < 0.6])
        }
        
        return PatternDetectionResponse(
            symbol=request.symbol,
            patterns=pattern_dicts,
            total_patterns=len(filtered_patterns),
            analysis_timestamp=datetime.now(),
            timeframe=request.timeframe,
            confidence_summary=confidence_summary
        )
        
    except Exception as e:
        logger.error(f"Error in pattern detection: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Pattern detection failed: {str(e)}"
        )


@router.post("/regime/detect", response_model=RegimeDetectionResponse)
async def detect_regime(
    request: RegimeDetectionRequest,
    current_user: User = Depends(get_current_user_unified)
):
    """
    Detect market regime using advanced ML algorithms
    
    This endpoint analyzes market conditions to determine:
    - Current market regime (trending, ranging, high volatility, etc.)
    - Regime confidence and strength
    - Trend direction and momentum
    - Volatility characteristics
    - Trading implications and recommendations
    """
    try:
        logger.info(f"Regime detection requested for {request.symbol}")
        
        # Get market data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=request.lookback_days)
        
        # Fetch OHLCV data
        ohlcv_data = await market_data_service.get_historical_data(
            symbol=request.symbol,
            start_date=start_date,
            end_date=end_date,
            timeframe=request.timeframe
        )
        
        if ohlcv_data.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No data available for symbol {request.symbol}"
            )
        
        # Get volume data
        volume_data = ohlcv_data.get('volume')
        
        # Get additional market data if requested
        market_data = None
        if request.include_market_data:
            # This would fetch VIX, sector data, etc.
            market_data = await market_data_service.get_market_indicators()
        
        # Detect regime
        regime_analysis = regime_detector.detect_regime(
            ohlcv_data, volume_data, market_data
        )
        
        # Convert regime probabilities to string keys
        regime_probs = {
            regime.value: prob 
            for regime, prob in regime_analysis.regime_probability.items()
        }
        
        return RegimeDetectionResponse(
            symbol=request.symbol,
            current_regime=regime_analysis.current_regime.value,
            confidence=regime_analysis.confidence,
            regime_strength=regime_analysis.regime_strength,
            trend_direction=regime_analysis.trend_direction,
            volatility_level=regime_analysis.volatility_level,
            momentum_score=regime_analysis.momentum_score,
            regime_duration=regime_analysis.regime_duration,
            regime_probabilities=regime_probs,
            key_indicators=regime_analysis.key_indicators,
            trading_implications=regime_analysis.trading_implications,
            risk_level=regime_analysis.risk_level,
            recommended_strategies=regime_analysis.recommended_strategies,
            analysis_timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error in regime detection: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Regime detection failed: {str(e)}"
        )


@router.post("/insights/comprehensive", response_model=MLInsightsResponse)
async def get_comprehensive_insights(
    request: MLInsightsRequest,
    current_user: User = Depends(get_current_user_unified)
):
    """
    Get comprehensive ML insights combining multiple analyses
    
    This endpoint provides a complete ML-powered analysis including:
    - Pattern detection results
    - Market regime analysis
    - Sentiment analysis
    - Overall trading recommendation
    - Risk assessment
    - Key insights and actionable recommendations
    """
    try:
        logger.info(f"Comprehensive ML insights requested for {request.symbol}")
        
        # Get market data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        # Fetch OHLCV data
        ohlcv_data = await market_data_service.get_historical_data(
            symbol=request.symbol,
            start_date=start_date,
            end_date=end_date,
            timeframe="1d"
        )
        
        if ohlcv_data.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No data available for symbol {request.symbol}"
            )
        
        # Initialize results
        patterns_result = None
        regime_result = None
        sentiment_result = None
        
        # Pattern detection
        if request.include_patterns:
            try:
                volume_data = ohlcv_data.get('volume')
                patterns = pattern_detector.detect_patterns(ohlcv_data, volume_data)
                
                # Get top 3 patterns by confidence
                top_patterns = sorted(patterns, key=lambda x: x.confidence, reverse=True)[:3]
                
                patterns_result = {
                    "total_patterns": len(patterns),
                    "top_patterns": [
                        {
                            "pattern_type": p.pattern_type.value,
                            "confidence": p.confidence,
                            "direction": p.direction,
                            "trading_suggestion": p.trading_suggestion
                        }
                        for p in top_patterns
                    ],
                    "confidence_distribution": {
                        "very_strong": len([p for p in patterns if p.confidence >= 0.8]),
                        "strong": len([p for p in patterns if 0.7 <= p.confidence < 0.8]),
                        "moderate": len([p for p in patterns if 0.6 <= p.confidence < 0.7])
                    }
                }
            except Exception as e:
                logger.warning(f"Pattern detection failed: {e}")
        
        # Regime detection
        if request.include_regime:
            try:
                volume_data = ohlcv_data.get('volume')
                regime_analysis = regime_detector.detect_regime(ohlcv_data, volume_data)
                
                regime_result = {
                    "current_regime": regime_analysis.current_regime.value,
                    "confidence": regime_analysis.confidence,
                    "trend_direction": regime_analysis.trend_direction,
                    "volatility_level": regime_analysis.volatility_level,
                    "risk_level": regime_analysis.risk_level,
                    "recommended_strategies": regime_analysis.recommended_strategies,
                    "trading_implications": regime_analysis.trading_implications
                }
            except Exception as e:
                logger.warning(f"Regime detection failed: {e}")
        
        # Sentiment analysis (placeholder)
        if request.include_sentiment:
            try:
                # This would integrate with news sentiment analysis
                sentiment_result = {
                    "overall_sentiment": "neutral",
                    "sentiment_score": 0.0,
                    "news_sentiment": "neutral",
                    "social_sentiment": "neutral",
                    "analyst_sentiment": "neutral"
                }
            except Exception as e:
                logger.warning(f"Sentiment analysis failed: {e}")
        
        # Calculate overall score
        overall_score = 0.5  # Default neutral score
        
        if patterns_result:
            pattern_confidence = sum(p["confidence"] for p in patterns_result["top_patterns"]) / len(patterns_result["top_patterns"]) if patterns_result["top_patterns"] else 0.5
            overall_score = (overall_score + pattern_confidence) / 2
        
        if regime_result:
            regime_confidence = regime_result["confidence"]
            overall_score = (overall_score + regime_confidence) / 2
        
        # Generate trading recommendation
        trading_recommendation = "HOLD"
        if overall_score > 0.7:
            trading_recommendation = "BUY"
        elif overall_score < 0.3:
            trading_recommendation = "SELL"
        
        # Generate risk assessment
        risk_assessment = "MEDIUM"
        if regime_result:
            if regime_result["risk_level"] == "extreme":
                risk_assessment = "HIGH"
            elif regime_result["risk_level"] == "low":
                risk_assessment = "LOW"
        
        # Generate key insights
        key_insights = []
        
        if patterns_result and patterns_result["top_patterns"]:
            top_pattern = patterns_result["top_patterns"][0]
            key_insights.append(f"Strong {top_pattern['pattern_type']} pattern detected with {top_pattern['confidence']:.1%} confidence")
        
        if regime_result:
            key_insights.append(f"Market in {regime_result['current_regime']} regime with {regime_result['trend_direction']} trend")
            key_insights.extend(regime_result["trading_implications"][:2])
        
        if sentiment_result:
            key_insights.append(f"Overall sentiment: {sentiment_result['overall_sentiment']}")
        
        return MLInsightsResponse(
            symbol=request.symbol,
            analysis_timestamp=datetime.now(),
            patterns=patterns_result,
            regime=regime_result,
            sentiment=sentiment_result,
            overall_score=overall_score,
            trading_recommendation=trading_recommendation,
            risk_assessment=risk_assessment,
            key_insights=key_insights
        )
        
    except Exception as e:
        logger.error(f"Error in comprehensive ML insights: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Comprehensive analysis failed: {str(e)}"
        )


@router.get("/patterns/types")
async def get_pattern_types(
    current_user: User = Depends(get_current_user_unified)
):
    """Get list of available pattern types for detection"""
    return {
        "pattern_types": [
            {
                "type": pattern_type.value,
                "category": "reversal" if "top" in pattern_type.value or "bottom" in pattern_type.value or "shoulder" in pattern_type.value else
                          "continuation" if "triangle" in pattern_type.value or "flag" in pattern_type.value or "pennant" in pattern_type.value else
                          "candlestick" if pattern_type.value in ["hammer", "doji", "engulfing", "morning_star", "evening_star"] else
                          "volume" if "volume" in pattern_type.value else
                          "support_resistance",
                "description": f"Detects {pattern_type.value.replace('_', ' ').title()} patterns"
            }
            for pattern_type in PatternType
        ]
    }


@router.get("/regime/types")
async def get_regime_types(
    current_user: User = Depends(get_current_user_unified)
):
    """Get list of available market regime types"""
    return {
        "regime_types": [
            {
                "type": regime.value,
                "description": f"Market in {regime.value.replace('_', ' ').title()} state",
                "characteristics": {
                    "trending_bull": "Strong upward trend with bullish momentum",
                    "trending_bear": "Strong downward trend with bearish momentum",
                    "ranging": "Sideways movement within support and resistance",
                    "high_volatility": "Increased price volatility and uncertainty",
                    "low_volatility": "Reduced price movement and consolidation",
                    "breakout": "Price breaking through key levels",
                    "reversal": "Trend reversal patterns emerging",
                    "accumulation": "Institutional buying and accumulation",
                    "distribution": "Institutional selling and distribution"
                }.get(regime.value, "Market regime characteristics")
            }
            for regime in MarketRegime
        ]
    }


@router.get("/health")
async def ml_health_check():
    """Health check for ML services"""
    try:
        # Test pattern detector
        pattern_status = "healthy"
        try:
            # Simple test with dummy data
            import pandas as pd
            import numpy as np
            test_data = pd.DataFrame({
                'open': np.random.randn(100).cumsum() + 100,
                'high': np.random.randn(100).cumsum() + 102,
                'low': np.random.randn(100).cumsum() + 98,
                'close': np.random.randn(100).cumsum() + 100,
                'volume': np.random.randint(1000, 10000, 100)
            })
            pattern_detector.detect_patterns(test_data)
        except Exception as e:
            pattern_status = f"unhealthy: {str(e)}"
        
        # Test regime detector
        regime_status = "healthy"
        try:
            test_data = pd.DataFrame({
                'open': np.random.randn(100).cumsum() + 100,
                'high': np.random.randn(100).cumsum() + 102,
                'low': np.random.randn(100).cumsum() + 98,
                'close': np.random.randn(100).cumsum() + 100,
                'volume': np.random.randint(1000, 10000, 100)
            })
            regime_detector.detect_regime(test_data)
        except Exception as e:
            regime_status = f"unhealthy: {str(e)}"
        
        return {
            "status": "healthy" if pattern_status == "healthy" and regime_status == "healthy" else "degraded",
            "services": {
                "pattern_detector": pattern_status,
                "regime_detector": regime_status
            },
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now()
        }
