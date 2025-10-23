#!/bin/bash
# monitor-production.sh - Continuous monitoring script

BACKEND_URL="${BACKEND_URL:-https://paiid-backend.onrender.com}"
ALERT_THRESHOLD_MS=1000
ERROR_THRESHOLD_PERCENT=5

echo "🔍 Production Monitoring Started"
echo "Monitoring: $BACKEND_URL"

while true; do
    # Fetch health metrics
    HEALTH=$(curl -s "$BACKEND_URL/api/health/detailed" -H "Authorization: Bearer $API_TOKEN")
    
    # Parse metrics
    ERROR_RATE=$(echo "$HEALTH" | jq -r '.application.error_rate_percent')
    RESPONSE_TIME=$(echo "$HEALTH" | jq -r '.application.avg_response_time_ms')
    CPU=$(echo "$HEALTH" | jq -r '.system.cpu_percent')
    MEMORY=$(echo "$HEALTH" | jq -r '.system.memory_percent')
    STATUS=$(echo "$HEALTH" | jq -r '.status')
    
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Log metrics
    echo "[$TIMESTAMP] Status: $STATUS | CPU: ${CPU}% | Memory: ${MEMORY}% | Errors: ${ERROR_RATE}% | Response: ${RESPONSE_TIME}ms"
    
    # Check thresholds
    if (( $(echo "$ERROR_RATE > $ERROR_THRESHOLD_PERCENT" | bc -l) )); then
        echo "⚠️  HIGH ERROR RATE: ${ERROR_RATE}%"
        # Send alert (implement Slack/email notification)
    fi
    
    if (( $(echo "$RESPONSE_TIME > $ALERT_THRESHOLD_MS" | bc -l) )); then
        echo "⚠️  SLOW RESPONSE TIME: ${RESPONSE_TIME}ms"
    fi
    
    if [ "$STATUS" != "healthy" ]; then
        echo "🚨 SYSTEM DEGRADED: $STATUS"
    fi
    
    # Wait before next check
    sleep 60
done
