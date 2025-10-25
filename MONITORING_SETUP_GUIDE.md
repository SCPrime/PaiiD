# Monitoring & Observability Setup Guide
**Project**: PaiiD  
**Date**: October 24, 2025  
**Status**: READY FOR IMPLEMENTATION

---

## Overview

Comprehensive monitoring strategy covering error tracking, performance monitoring, logging, and alerting.

---

## 1. Error Tracking (Sentry)

### Installation

```bash
# Frontend
cd frontend
npm install @sentry/nextjs

# Backend
cd backend
pip install sentry-sdk[fastapi]
```

### Frontend Configuration

```typescript
// sentry.client.config.ts
import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 1.0,
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
});
```

### Backend Configuration

```python
# backend/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    environment=os.getenv("ENVIRONMENT", "production"),
    traces_sample_rate=1.0,
    integrations=[FastApiIntegration()],
)
```

---

## 2. Performance Monitoring

### Frontend (Web Vitals)

```typescript
// lib/monitoring.ts
export function reportWebVitals(metric: NextWebVitalsMetric) {
  // Send to analytics
  if (window.gtag) {
    window.gtag('event', metric.name, {
      value: Math.round(metric.value),
      metric_id: metric.id,
      metric_label: metric.label,
    });
  }
  
  // Send to custom endpoint
  fetch('/api/analytics/web-vitals', {
    method: 'POST',
    body: JSON.stringify(metric),
  });
}
```

### Backend (Custom Metrics)

```python
# backend/middleware/monitoring.py
from prometheus_client import Counter, Histogram
import time

request_count = Counter('http_requests_total', 'Total HTTP requests')
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')

@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    request_count.inc()
    request_duration.observe(duration)
    
    return response
```

---

## 3. Logging

### Structured Logging

```typescript
// lib/logger.ts
export const logger = {
  info: (message: string, meta?: Record<string, any>) => {
    console.log(JSON.stringify({
      level: 'info',
      message,
      timestamp: new Date().toISOString(),
      ...meta,
    }));
  },
  
  error: (message: string, error?: Error, meta?: Record<string, any>) => {
    console.error(JSON.stringify({
      level: 'error',
      message,
      error: error?.message,
      stack: error?.stack,
      timestamp: new Date().toISOString(),
      ...meta,
    }));
  },
};
```

---

## 4. Health Checks

```typescript
// pages/api/health.ts
export default async function handler(req, res) {
  const health = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    checks: {
      database: await checkDatabase(),
      redis: await checkRedis(),
      external_apis: await checkExternalAPIs(),
    },
  };
  
  const isHealthy = Object.values(health.checks).every(c => c.status === 'ok');
  
  res.status(isHealthy ? 200 : 503).json(health);
}
```

---

## 5. Alerting Rules

### Critical Alerts
- Error rate > 5% for 5 minutes
- API response time p95 > 1000ms for 10 minutes
- Health check failures > 3 consecutive
- Database connection pool exhausted

### Warning Alerts
- Error rate > 2% for 10 minutes
- API response time p95 > 500ms for 15 minutes
- Memory usage > 80%
- Disk usage > 85%

---

## 6. Dashboards

### Key Metrics to Monitor

1. **User Activity**
   - Active users (real-time)
   - Sign-ups (daily)
   - Login success rate

2. **Application Performance**
   - API response times (p50, p95, p99)
   - Frontend page load times
   - Error rates by endpoint

3. **Infrastructure**
   - CPU usage
   - Memory usage
   - Database connections
   - Redis hit rate

4. **Business Metrics**
   - Trades executed (daily)
   - Portfolio value (aggregate)
   - Active positions

---

## Status

**Documentation**: ✅ COMPLETE  
**Implementation**: 📋 PENDING  
**Testing**: ⚠️ NOT STARTED

---

**Owner**: DevOps Team  
**Next Steps**: Install Sentry, configure alerts
