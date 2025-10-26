# ML System Architecture Documentation

## Overview

The PaiiD ML System is a comprehensive machine learning platform designed for financial market analysis, sentiment analysis, and automated trading signal generation. The system combines multiple ML models, real-time data processing, and intelligent caching to provide actionable insights for traders.

## System Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   ML Services   │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (Python)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Auth     │    │   Database      │    │   Redis Cache   │
│   (JWT/API)     │    │   (PostgreSQL)  │    │   (Sentiment)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   External APIs │    │   Data Pipeline  │    │   ML Models     │
│   (News/Market) │    │   (Real-time)   │    │   (Sentiment)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Core Components

### 1. ML Data Pipeline (`MLDataPipeline`)

**Purpose**: Orchestrates data collection, processing, and model inference

**Key Features**:
- Real-time market data ingestion
- News sentiment analysis
- Technical indicator calculation
- Model prediction orchestration

**Architecture**:
```python
class MLDataPipeline:
    def __init__(self):
        self.market_data_client = MarketDataClient()
        self.news_client = NewsClient()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.signal_generator = SignalGenerator()
        self.cache_manager = CacheManager()
    
    async def get_sentiment_analysis(self, symbol: str, lookback_days: int):
        # 1. Check cache
        # 2. Fetch market data
        # 3. Fetch news data
        # 4. Run sentiment analysis
        # 5. Cache results
        # 6. Return analysis
```

### 2. Sentiment Analyzer (`SentimentAnalyzer`)

**Purpose**: Analyzes news sentiment using multiple ML models

**Models Supported**:
- **VADER**: Rule-based sentiment analysis
- **FinBERT**: Financial domain-specific BERT model
- **Custom BERT**: Fine-tuned on financial news
- **Ensemble**: Combines multiple models for robust predictions

**Architecture**:
```python
class SentimentAnalyzer:
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
        self.finbert = AutoModel.from_pretrained('yiyanghkust/finbert-tone')
        self.custom_bert = AutoModel.from_pretrained('custom-financial-bert')
        self.ensemble_weights = [0.3, 0.4, 0.3]
    
    def analyze_sentiment(self, text: str) -> SentimentResult:
        # 1. Preprocess text
        # 2. Run VADER analysis
        # 3. Run FinBERT analysis
        # 4. Run Custom BERT analysis
        # 5. Ensemble predictions
        # 6. Return confidence-weighted result
```

### 3. Signal Generator (`SignalGenerator`)

**Purpose**: Generates trading signals based on sentiment and technical analysis

**Signal Types**:
- **BUY**: Strong positive sentiment + bullish technicals
- **SELL**: Strong negative sentiment + bearish technicals
- **HOLD**: Neutral sentiment or conflicting signals
- **STRONG_BUY/STRONG_SELL**: High confidence signals

**Architecture**:
```python
class SignalGenerator:
    def __init__(self):
        self.technical_analyzer = TechnicalAnalyzer()
        self.risk_manager = RiskManager()
        self.signal_validator = SignalValidator()
    
    def generate_signals(self, symbol: str, sentiment: SentimentResult) -> List[Signal]:
        # 1. Get technical indicators
        # 2. Calculate signal strength
        # 3. Apply risk management rules
        # 4. Validate signal quality
        # 5. Return actionable signals
```

### 4. Cache Manager (`CacheManager`)

**Purpose**: Intelligent caching for performance optimization

**Cache Strategies**:
- **Sentiment Cache**: 15-minute TTL for sentiment analysis
- **Signal Cache**: 5-minute TTL for trading signals
- **News Cache**: 30-minute TTL for news data
- **Market Data Cache**: 1-minute TTL for price data

**Architecture**:
```python
class CacheManager:
    def __init__(self):
        self.redis_client = redis.Redis()
        self.cache_configs = {
            'sentiment': {'ttl': 900, 'prefix': 'sentiment:'},
            'signals': {'ttl': 300, 'prefix': 'signals:'},
            'news': {'ttl': 1800, 'prefix': 'news:'},
            'market': {'ttl': 60, 'prefix': 'market:'}
        }
    
    async def get_cached_result(self, key: str, cache_type: str):
        # 1. Check cache validity
        # 2. Return cached data if valid
        # 3. Return None if expired/missing
    
    async def cache_result(self, key: str, data: Any, cache_type: str):
        # 1. Serialize data
        # 2. Set TTL
        # 3. Store in Redis
```

## Data Flow Architecture

### 1. Real-time Data Ingestion

```
External APIs → Data Pipeline → Preprocessing → Feature Extraction → Model Input
     │              │              │              │              │
     ▼              ▼              ▼              ▼              ▼
News API      Market Data    Text Cleaning    Sentiment      ML Models
Market API    Validation     Tokenization    Features       Inference
```

### 2. Model Inference Pipeline

```
Input Data → Preprocessing → Model Selection → Inference → Post-processing → Output
     │            │              │              │              │            │
     ▼            ▼              ▼              ▼              ▼            ▼
Raw Text    Text Cleaning   Model Router    Prediction    Confidence    Signals
Market Data Normalization   Ensemble        Aggregation   Scoring       Results
```

### 3. Caching Strategy

```
Request → Cache Check → Cache Hit? → Return Cached Data
    │           │           │
    ▼           ▼           ▼
Process    Cache Miss   Generate New Data
Request    Generate     Cache Result
           New Data     Return Data
```

## ML Models Architecture

### 1. Sentiment Analysis Models

#### VADER Sentiment Analyzer
- **Type**: Rule-based
- **Use Case**: Quick sentiment scoring
- **Pros**: Fast, no training required
- **Cons**: Limited financial domain knowledge

#### FinBERT Model
- **Type**: Transformer-based
- **Use Case**: Financial text sentiment
- **Pros**: Domain-specific, high accuracy
- **Cons**: Slower inference, requires GPU

#### Custom BERT Model
- **Type**: Fine-tuned transformer
- **Use Case**: Custom financial sentiment
- **Pros**: Optimized for specific use case
- **Cons**: Requires training data and maintenance

#### Ensemble Model
- **Type**: Weighted combination
- **Use Case**: Robust predictions
- **Pros**: Reduces individual model bias
- **Cons**: More complex to tune

### 2. Technical Analysis Models

#### RSI Calculator
- **Purpose**: Momentum analysis
- **Range**: 0-100
- **Signals**: Overbought (>70), Oversold (<30)

#### MACD Calculator
- **Purpose**: Trend analysis
- **Components**: MACD line, Signal line, Histogram
- **Signals**: Crossovers, Divergences

#### Bollinger Bands
- **Purpose**: Volatility analysis
- **Components**: Upper, Middle, Lower bands
- **Signals**: Price position relative to bands

### 3. Signal Generation Models

#### Rule-based Engine
- **Purpose**: Basic signal generation
- **Logic**: If-else rules based on indicators
- **Pros**: Interpretable, fast
- **Cons**: Limited complexity

#### ML-based Engine
- **Purpose**: Advanced signal generation
- **Models**: Random Forest, XGBoost, Neural Networks
- **Pros**: Complex patterns, adaptive
- **Cons**: Black box, requires training

## Performance Optimization

### 1. Caching Strategy

```python
# Cache hierarchy
L1 Cache (Memory) → L2 Cache (Redis) → L3 Cache (Database) → External API
     │                   │                   │                   │
     ▼                   ▼                   ▼                   ▼
Fastest Access    Fast Access        Medium Access        Slowest Access
< 1ms             < 10ms            < 100ms             > 1000ms
```

### 2. Parallel Processing

```python
# Concurrent data fetching
async def fetch_all_data(symbol: str):
    tasks = [
        fetch_market_data(symbol),
        fetch_news_data(symbol),
        fetch_technical_indicators(symbol)
    ]
    results = await asyncio.gather(*tasks)
    return results
```

### 3. Model Optimization

- **Model Quantization**: Reduce model size
- **Batch Processing**: Process multiple requests together
- **GPU Acceleration**: Use CUDA for transformer models
- **Model Caching**: Keep models in memory

## Monitoring and Observability

### 1. Health Checks

```python
class MLHealthChecker:
    def check_model_health(self):
        return {
            'sentiment_model': self.check_sentiment_model(),
            'signal_model': self.check_signal_model(),
            'cache_status': self.check_cache_status(),
            'data_sources': self.check_data_sources()
        }
```

### 2. Performance Metrics

- **Response Time**: Average inference time
- **Cache Hit Rate**: Percentage of cache hits
- **Model Accuracy**: Prediction accuracy metrics
- **Throughput**: Requests per second
- **Error Rate**: Failed requests percentage

### 3. Alerting System

```python
class MLAlerting:
    def check_alerts(self):
        alerts = []
        
        # Performance alerts
        if self.avg_response_time > 200:
            alerts.append('High response time')
        
        # Accuracy alerts
        if self.model_accuracy < 0.8:
            alerts.append('Low model accuracy')
        
        # Cache alerts
        if self.cache_hit_rate < 0.7:
            alerts.append('Low cache hit rate')
        
        return alerts
```

## Security Architecture

### 1. Data Security

- **Encryption**: All data encrypted in transit and at rest
- **Access Control**: Role-based access to ML models
- **Audit Logging**: All ML operations logged
- **Data Privacy**: No PII in ML models

### 2. Model Security

- **Model Validation**: Input validation for all models
- **Adversarial Protection**: Protection against adversarial attacks
- **Model Versioning**: Secure model deployment pipeline
- **Access Logging**: Track model usage and access

### 3. API Security

- **Rate Limiting**: Prevent abuse of ML endpoints
- **Authentication**: JWT and API token authentication
- **Input Sanitization**: Prevent injection attacks
- **Output Validation**: Validate model outputs

## Deployment Architecture

### 1. Development Environment

```
Developer → Local ML Models → Test Database → Mock External APIs
```

### 2. Staging Environment

```
Staging API → Staging ML Models → Staging Database → Sandbox APIs
```

### 3. Production Environment

```
Production API → Production ML Models → Production Database → Live APIs
```

## Scalability Considerations

### 1. Horizontal Scaling

- **Load Balancing**: Distribute requests across multiple ML servers
- **Model Replication**: Deploy multiple model instances
- **Cache Clustering**: Redis cluster for high availability
- **Database Sharding**: Partition data by symbol or time

### 2. Vertical Scaling

- **GPU Acceleration**: Use GPUs for transformer models
- **Memory Optimization**: Optimize model memory usage
- **CPU Optimization**: Use multi-core processing
- **Storage Optimization**: Use SSD for faster I/O

### 3. Auto-scaling

```python
class MLAutoScaler:
    def scale_based_on_load(self):
        current_load = self.get_current_load()
        
        if current_load > 0.8:
            self.scale_up()
        elif current_load < 0.3:
            self.scale_down()
```

## Future Enhancements

### 1. Advanced ML Features

- **Real-time Learning**: Online model updates
- **Multi-modal Analysis**: Combine text, images, and market data
- **Reinforcement Learning**: Learn from trading outcomes
- **Federated Learning**: Distributed model training

### 2. Performance Improvements

- **Edge Computing**: Deploy models closer to users
- **Model Compression**: Reduce model size without accuracy loss
- **Streaming Processing**: Real-time data processing
- **Predictive Caching**: Pre-compute likely requests

### 3. Integration Enhancements

- **WebSocket Support**: Real-time updates
- **GraphQL API**: Flexible data querying
- **Microservices**: Decompose into smaller services
- **Event-driven Architecture**: Asynchronous processing

## Troubleshooting Guide

### Common Issues

1. **High Response Times**
   - Check cache hit rates
   - Monitor model inference times
   - Verify external API response times

2. **Low Accuracy**
   - Check model performance metrics
   - Verify data quality
   - Review model training data

3. **Cache Issues**
   - Check Redis connectivity
   - Verify cache TTL settings
   - Monitor memory usage

4. **Model Errors**
   - Check model loading status
   - Verify input data format
   - Review error logs

### Debug Tools

```python
# Enable debug mode
export DEBUG_ML_SYSTEM=true
export LOG_LEVEL=DEBUG

# Check system health
python -m app.ml.health_check

# Test model inference
python -m app.ml.test_models

# Monitor performance
python -m app.ml.performance_monitor
```

---

*Last Updated: January 15, 2024*
*Version: 1.0.0*
