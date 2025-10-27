# Security Monitoring Guide
**Last Updated:** October 27, 2025
**Owner:** Security Team
**Scope:** PaiiD Trading Platform Security Monitoring & Incident Response

---

## Table of Contents
1. [Overview](#overview)
2. [Key Security Metrics](#key-security-metrics)
3. [Alert Thresholds](#alert-thresholds)
4. [Monitoring Tools Integration](#monitoring-tools-integration)
5. [Security Dashboards](#security-dashboards)
6. [Incident Response](#incident-response)
7. [Log Analysis](#log-analysis)
8. [Automated Detection Rules](#automated-detection-rules)

---

## Overview

This guide provides comprehensive security monitoring practices for the PaiiD trading platform. It covers key metrics, alerting thresholds, incident response procedures, and monitoring tool configurations.

### Security Objectives
1. **Detection:** Identify security incidents within minutes
2. **Response:** Contain threats within 15 minutes of detection
3. **Recovery:** Restore normal operations within 1 hour
4. **Prevention:** Learn from incidents to prevent recurrence

### Monitoring Principles
- **Defense in Depth:** Multiple layers of monitoring
- **Real-time Alerting:** Immediate notification of critical events
- **Automated Response:** Auto-block malicious IPs
- **Audit Trail:** Complete logging for forensic analysis

---

## Key Security Metrics

### 1. Authentication Metrics

#### Failed Login Attempts
**Metric:** `auth.login.failed`
**Description:** Count of failed authentication attempts per IP/user

**Normal Behavior:**
- 0-2 failures per user per hour (typos)
- 0-5 failures per IP per hour (shared networks)

**Suspicious Patterns:**
- 5+ failures per user in 5 minutes (credential stuffing)
- 10+ failures per IP in 1 minute (brute force)
- 100+ failures from different IPs (distributed attack)

**Dashboard Query (Sentry):**
```sql
SELECT count(*) as failures,
       client_ip,
       user_email,
       time_bucket('1 minute') as time_window
FROM security_events
WHERE event_type = 'auth.login.failed'
GROUP BY client_ip, user_email, time_window
HAVING count(*) > 5
ORDER BY failures DESC
```

**Alert Rule:**
```python
if failed_logins_per_ip > 10 in 1_minute:
    severity = "HIGH"
    action = "block_ip_15_minutes"
    notify = ["security-team", "pagerduty"]
```

#### Unusual Login Patterns
**Metric:** `auth.login.unusual`
**Indicators:**
- Login from new geolocation
- Login from new device/browser
- Login outside normal hours (for user)
- Impossible travel (two locations too far apart in time)

**Example Detection:**
```python
# Detect impossible travel
last_login_location = get_last_login_location(user_id)
current_login_location = get_current_location(ip_address)
time_diff = current_time - last_login_time
distance = calculate_distance(last_location, current_location)
max_speed = distance / time_diff

if max_speed > 800:  # km/h (faster than commercial flight)
    alert("Impossible travel detected", severity="MEDIUM")
```

#### Session Anomalies
**Metrics:**
- `auth.session.hijack_attempt` - Concurrent sessions from different IPs
- `auth.session.expired_reuse` - Attempt to use expired token
- `auth.token.tampering` - Invalid JWT signature

**Alert Thresholds:**
- 1+ concurrent session from different countries → HIGH
- 5+ expired token reuse attempts → MEDIUM
- 1+ token tampering attempt → CRITICAL

---

### 2. Rate Limiting Metrics

#### Rate Limit Violations
**Metric:** `rate_limit.exceeded`
**Description:** Count of 429 (Too Many Requests) responses per IP

**Normal Behavior:**
- 0-1 violations per user per hour (accidental)

**Suspicious Patterns:**
- 10+ violations per IP in 1 hour (API abuse)
- 100+ violations from single IP (DoS attempt)
- Coordinated violations from multiple IPs (DDoS)

**Dashboard Query:**
```python
# Monitor rate limit violations by endpoint
SELECT endpoint,
       client_ip,
       count(*) as violations,
       avg(requests_per_minute) as avg_rpm
FROM rate_limit_events
WHERE status_code = 429
GROUP BY endpoint, client_ip
HAVING count(*) > 10
```

**Auto-Response:**
```python
if rate_limit_violations_per_ip > 20 in 1_hour:
    action = "block_ip_24_hours"
    log_to_threat_intel(ip_address, "rate_limit_abuse")
    notify = ["security-team"]
```

#### Endpoint-Specific Monitoring
**High-Value Endpoints:**
- `/api/auth/login` - Authentication attempts
- `/api/orders` - Trade execution
- `/api/portfolio` - Account information
- `/api/settings` - Configuration changes

**Alert on:**
- 100+ requests to `/api/auth/login` from single IP → Brute force
- 50+ requests to `/api/orders` in 1 minute → Trading bot abuse
- 200+ requests to `/api/portfolio` → Data scraping

---

### 3. CSRF Validation Metrics

#### CSRF Token Failures
**Metric:** `csrf.validation.failed`
**Description:** Count of requests with missing/invalid CSRF tokens

**Normal Behavior:**
- 0-2 failures per user per day (browser refresh, expired token)

**Suspicious Patterns:**
- 5+ failures from same IP (CSRF attack attempt)
- Missing CSRF token on state-changing endpoints (automated attack)
- Invalid CSRF token signature (token tampering)

**Detection Logic:**
```python
# CSRF validation failure analysis
if csrf_failure and request.method in ["POST", "PUT", "DELETE", "PATCH"]:
    if "Referer" not in request.headers:
        severity = "HIGH"  # No referer = likely automated
    elif not is_valid_referer(request.headers["Referer"]):
        severity = "CRITICAL"  # Cross-origin = active attack
    else:
        severity = "MEDIUM"  # May be expired token
```

**Alert Rule:**
```python
if csrf_failures_per_ip > 5 in 10_minutes:
    severity = "HIGH"
    action = "require_recaptcha"
    notify = ["security-team"]
```

---

### 4. API Security Metrics

#### SQL Injection Attempts
**Metric:** `attack.sql_injection`
**Indicators:**
- Requests with SQL keywords: `SELECT`, `UNION`, `DROP`, `INSERT`
- Encoded SQL: `%27` (single quote), `%3B` (semicolon)
- Boolean-based blind SQLi: `OR 1=1`, `AND 1=2`

**Detection Patterns:**
```python
SQL_INJECTION_PATTERNS = [
    r"(\bunion\b.*\bselect\b)",
    r"(\bor\b.*\b=\b)",
    r"(\'|%27)(\s)*(or|and)(\s)*(\d+|[a-z]+)(\s)*=",
    r"(;|\||&)(\s)*(drop|delete|truncate)",
]

for pattern in SQL_INJECTION_PATTERNS:
    if re.search(pattern, request.query_string, re.IGNORECASE):
        log_security_event("sql_injection_attempt", severity="CRITICAL")
        block_request()
```

#### XSS (Cross-Site Scripting) Attempts
**Metric:** `attack.xss`
**Indicators:**
- Script tags: `<script>`, `</script>`
- Event handlers: `onerror=`, `onload=`
- JavaScript URLs: `javascript:`, `data:text/html`

**Detection:**
```python
XSS_PATTERNS = [
    r"<script[^>]*>.*?</script>",
    r"on\w+\s*=",
    r"javascript:",
    r"<iframe",
]

for pattern in XSS_PATTERNS:
    if re.search(pattern, request.body, re.IGNORECASE):
        log_security_event("xss_attempt", severity="HIGH")
        sanitize_and_reject()
```

#### Path Traversal Attempts
**Metric:** `attack.path_traversal`
**Indicators:**
- `../` sequences
- Encoded: `%2e%2e%2f`, `..%2f`, `%2e%2e/`
- Absolute paths: `/etc/passwd`, `C:\Windows\System32`

---

### 5. Application Security Metrics

#### Startup Validation Failures
**Metric:** `startup.validation.failed`
**Critical Events:**
- Missing required secrets (API keys, JWT secret)
- Database connection failure
- External API connectivity issues

**Alert Rule:**
```python
if startup_validation_failed:
    severity = "CRITICAL"
    action = "block_all_traffic"  # Don't serve if not properly configured
    notify = ["oncall-engineer", "pagerduty"]
    escalate_after = 5_minutes
```

#### Security Header Violations
**Metric:** `security_headers.violation`
**Monitored Headers:**
- Missing CSP header
- Missing HSTS header
- Missing X-Frame-Options
- Weak CSP directives (unsafe-eval, unsafe-inline without nonce)

**Detection:**
```python
def validate_security_headers(response):
    required_headers = [
        "Content-Security-Policy",
        "Strict-Transport-Security",
        "X-Frame-Options",
        "X-Content-Type-Options",
    ]

    for header in required_headers:
        if header not in response.headers:
            log_security_event(f"missing_{header.lower()}", severity="MEDIUM")
```

---

## Alert Thresholds

### Severity Levels

#### CRITICAL (Immediate Notification)
**Response Time:** Immediate (PagerDuty)
**Escalation:** 5 minutes if not acknowledged

**Examples:**
- SQL injection attempt detected
- Token tampering detected
- Startup validation failure (production)
- 1000+ failed login attempts (DDoS)
- Cross-origin CSRF attack

**Notification Channels:**
- PagerDuty (on-call engineer)
- Slack #security-critical
- Email to security-team@paiid.com
- SMS to CTO

**Auto-Response:**
- Block source IP immediately
- Enable rate limiting (strict mode)
- Capture full request/response for forensics
- Create incident ticket

---

#### HIGH (Within 15 minutes)
**Response Time:** 15 minutes
**Escalation:** 30 minutes if not resolved

**Examples:**
- 10+ failed login attempts from single IP
- 20+ rate limit violations in 1 hour
- Missing security header on production endpoint
- Unusual login pattern (new country)
- 5+ CSRF validation failures

**Notification Channels:**
- Slack #security-alerts
- Email to security-team@paiid.com

**Auto-Response:**
- Throttle source IP (reduce rate limits)
- Require CAPTCHA for authentication
- Log detailed event data
- Create warning ticket

---

#### MEDIUM (Within 1 hour)
**Response Time:** 1 hour
**Escalation:** 4 hours if not resolved

**Examples:**
- 5+ failed login attempts from single user
- Dependency vulnerability detected (medium severity)
- Expired JWT token reuse attempt
- Suspicious user-agent string
- Rate limit violation (single occurrence)

**Notification Channels:**
- Slack #security-alerts (batched every 15 min)
- Daily email digest

**Auto-Response:**
- Log event for analysis
- Monitor for pattern escalation
- Create informational ticket

---

#### LOW (Daily Digest)
**Response Time:** Daily review
**Escalation:** Weekly review if recurring

**Examples:**
- 1-2 failed login attempts (typos)
- Dependency vulnerability (low severity)
- Deprecated API usage
- Slow endpoint performance

**Notification Channels:**
- Daily email digest
- Weekly security report

**Auto-Response:**
- Aggregate statistics
- Trend analysis

---

## Monitoring Tools Integration

### 1. Sentry (Error Tracking) ✅ Implemented

**Configuration:**
```python
# backend/app/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    environment=settings.SENTRY_ENVIRONMENT,
    traces_sample_rate=0.1,  # 10% performance monitoring
    profiles_sample_rate=0.1,
    send_default_pii=False,  # Don't send PII
    before_send=redact_sensitive_data,
)
```

**Security Events to Track:**
```python
# Log security events to Sentry
sentry_sdk.capture_message(
    "Failed login attempt",
    level="warning",
    extras={
        "ip_address": client_ip,
        "user_email": email,
        "failure_reason": "invalid_password",
        "attempt_count": attempt_count,
    }
)
```

**Custom Security Tags:**
```python
# Tag events for filtering
sentry_sdk.set_tag("security_event", "auth_failure")
sentry_sdk.set_tag("threat_level", "medium")
sentry_sdk.set_context("request", {
    "ip": request.client.host,
    "method": request.method,
    "endpoint": request.url.path,
})
```

**Alert Rules in Sentry:**
1. Failed logins > 10/minute → Notify #security-alerts
2. CSRF validation failures > 5/hour → Notify security-team
3. SQL injection pattern detected → PagerDuty
4. Rate limit exceeded > 100/hour → Notify #security-alerts

---

### 2. DataDog (Recommended for Production)

**Installation:**
```bash
# Install DataDog agent
pip install ddtrace

# Backend instrumentation
ddtrace-run uvicorn app.main:app --host 0.0.0.0 --port 8001
```

**Custom Metrics:**
```python
from datadog import statsd

# Track authentication metrics
statsd.increment('auth.login.failed', tags=[
    f'ip:{client_ip}',
    f'endpoint:{endpoint}',
])

# Track rate limiting
statsd.histogram('rate_limit.requests_per_minute', rpm, tags=[
    f'endpoint:{endpoint}',
    f'user_id:{user_id}',
])

# Track security events
statsd.event(
    "SQL Injection Attempt",
    f"Detected SQL injection from {client_ip}",
    alert_type="error",
    tags=['security', 'critical'],
)
```

**Dashboard Widgets:**
- Failed login attempts by IP (time series)
- Rate limit violations by endpoint (heatmap)
- CSRF failures (single value with threshold)
- Top attacked endpoints (top list)

---

### 3. ELK Stack (Log Aggregation)

**Architecture:**
```
Application → Filebeat → Logstash → Elasticsearch → Kibana
```

**Filebeat Configuration:**
```yaml
# filebeat.yml
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/paiid/security.log
    fields:
      log_type: security
      environment: production

output.logstash:
  hosts: ["logstash:5044"]
```

**Logstash Parsing:**
```ruby
# logstash.conf
filter {
  if [log_type] == "security" {
    grok {
      match => {
        "message" => "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:level} %{DATA:event_type} ip=%{IP:client_ip} user=%{DATA:user_email}"
      }
    }

    # Enrich with GeoIP data
    geoip {
      source => "client_ip"
      target => "geoip"
    }
  }
}
```

**Kibana Dashboards:**
1. **Authentication Monitor:**
   - Failed logins by country (map)
   - Failed logins over time (line chart)
   - Top attacking IPs (table)

2. **Rate Limiting Monitor:**
   - Rate limit violations by endpoint (bar chart)
   - Requests per minute (gauge)
   - Top rate-limited IPs (table)

3. **Security Events:**
   - Event types over time (area chart)
   - Severity distribution (pie chart)
   - Recent critical events (table)

---

### 4. CloudWatch (AWS Hosted)

**For AWS Deployments:**
```python
# Send custom metrics to CloudWatch
import boto3

cloudwatch = boto3.client('cloudwatch')

cloudwatch.put_metric_data(
    Namespace='PaiiD/Security',
    MetricData=[
        {
            'MetricName': 'FailedLogins',
            'Value': failed_login_count,
            'Unit': 'Count',
            'Timestamp': datetime.utcnow(),
            'Dimensions': [
                {'Name': 'Environment', 'Value': 'production'},
                {'Name': 'Endpoint', 'Value': '/api/auth/login'},
            ]
        }
    ]
)
```

**CloudWatch Alarms:**
```yaml
# cloudformation template
Resources:
  FailedLoginAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: HighFailedLogins
      MetricName: FailedLogins
      Namespace: PaiiD/Security
      Statistic: Sum
      Period: 300  # 5 minutes
      EvaluationPeriods: 1
      Threshold: 50
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref SecuritySNSTopic
```

---

## Security Dashboards

### Dashboard 1: Authentication Overview

**Purpose:** Monitor authentication security in real-time

**Widgets:**

1. **Failed Login Attempts (Last Hour)**
   - Type: Single Value
   - Query: `count(*) WHERE event_type='auth.login.failed' AND timestamp > now() - 1h`
   - Threshold: >50 = RED, >20 = YELLOW, <20 = GREEN

2. **Failed Logins by IP (Top 10)**
   - Type: Table
   - Columns: IP Address, Country, Attempt Count, Last Attempt
   - Query: `SELECT client_ip, geoip.country, count(*) as attempts, max(timestamp) FROM auth_events WHERE event_type='auth.login.failed' GROUP BY client_ip ORDER BY attempts DESC LIMIT 10`

3. **Login Success vs Failure Rate**
   - Type: Time Series (Line Chart)
   - Metrics:
     - Success rate (%)
     - Failure count
   - Time Range: Last 24 hours, 5-minute granularity

4. **Geographic Distribution of Failed Logins**
   - Type: World Map
   - Color Scale: 0 attempts = Green, 100+ = Red
   - Query: `SELECT geoip.country, count(*) FROM auth_events WHERE event_type='auth.login.failed' GROUP BY geoip.country`

5. **Unusual Login Alerts**
   - Type: Event List
   - Filters: New device, New location, Impossible travel
   - Query: `SELECT timestamp, user_email, event_details WHERE event_type IN ('auth.unusual_device', 'auth.unusual_location', 'auth.impossible_travel') ORDER BY timestamp DESC LIMIT 20`

---

### Dashboard 2: Rate Limiting & API Abuse

**Purpose:** Monitor API usage and detect abuse patterns

**Widgets:**

1. **Rate Limit Violations (Last Hour)**
   - Type: Single Value with Sparkline
   - Query: `count(*) WHERE status_code=429 AND timestamp > now() - 1h`
   - Threshold: >100 = RED

2. **Violations by Endpoint**
   - Type: Horizontal Bar Chart
   - Query: `SELECT endpoint, count(*) as violations FROM rate_limit_events WHERE status_code=429 GROUP BY endpoint ORDER BY violations DESC`

3. **Requests Per Minute (RPM) by Endpoint**
   - Type: Time Series (Multi-line)
   - Lines: One per high-traffic endpoint
   - Annotations: Rate limit threshold line

4. **Top Rate-Limited IPs**
   - Type: Table
   - Columns: IP, Country, Endpoint, Violation Count, Status (Blocked/Throttled)
   - Query: `SELECT client_ip, endpoint, count(*) as violations, is_blocked FROM rate_limit_events WHERE status_code=429 GROUP BY client_ip, endpoint ORDER BY violations DESC LIMIT 20`

5. **Rate Limit Effectiveness**
   - Type: Gauge
   - Metric: % of requests blocked before backend processing
   - Formula: `(blocked_at_middleware / total_requests) * 100`

---

### Dashboard 3: Security Events & Threats

**Purpose:** Real-time threat detection and incident tracking

**Widgets:**

1. **Critical Security Events (Last 24h)**
   - Type: Event List (Critical Priority)
   - Events: SQL injection, XSS, CSRF attacks, Token tampering
   - Query: `SELECT * FROM security_events WHERE severity='CRITICAL' AND timestamp > now() - 24h ORDER BY timestamp DESC`

2. **Security Event Severity Distribution**
   - Type: Donut Chart
   - Segments: Critical, High, Medium, Low
   - Query: `SELECT severity, count(*) FROM security_events GROUP BY severity`

3. **Attack Vector Timeline**
   - Type: Time Series (Stacked Area)
   - Layers: SQL Injection, XSS, CSRF, Path Traversal, Other
   - Query: `SELECT attack_type, count(*) FROM security_events GROUP BY attack_type, time_bucket('5 minutes')`

4. **Blocked IPs (Currently Active)**
   - Type: Table
   - Columns: IP, Reason, Block Duration, Expires At
   - Query: `SELECT ip_address, block_reason, block_duration, expires_at FROM ip_blocklist WHERE is_active=true ORDER BY expires_at`

5. **Incident Response Status**
   - Type: Status Board
   - Metrics:
     - Open Incidents: `count(*) WHERE status='open'`
     - Mean Time to Detect: `avg(detect_time - event_time)`
     - Mean Time to Respond: `avg(response_time - detect_time)`
     - Mean Time to Resolve: `avg(resolve_time - detect_time)`

---

### Dashboard 4: Compliance & Audit

**Purpose:** Security compliance and audit trail

**Widgets:**

1. **Security Header Compliance**
   - Type: Status Grid
   - Headers: CSP, HSTS, X-Frame-Options, X-Content-Type-Options
   - Status: Compliant (Green), Missing (Red), Weak (Yellow)

2. **Dependency Vulnerability Count**
   - Type: Single Value with Trend
   - Breakdown: Critical, High, Medium, Low
   - Source: Latest pip-audit / npm audit

3. **Failed Startup Validations**
   - Type: Event List
   - Query: `SELECT timestamp, validation_type, error_message FROM startup_events WHERE status='failed' ORDER BY timestamp DESC LIMIT 10`

4. **Audit Log Activity**
   - Type: Time Series
   - Events: User created, Role changed, Secret rotated, Config modified
   - Query: `SELECT audit_event_type, count(*) FROM audit_log GROUP BY audit_event_type, time_bucket('1 hour')`

---

## Incident Response

### Detection → Investigation → Containment → Recovery

---

### Phase 1: Detection

**Automated Detection:**
1. Real-time alerts trigger from monitoring tools
2. Security events logged to SIEM (Sentry, DataDog, ELK)
3. Anomaly detection algorithms flag unusual patterns
4. On-call engineer receives notification (PagerDuty, Slack)

**Manual Detection:**
5. User reports suspicious activity
6. Routine security audit finds anomaly
7. Third-party security researcher reports vulnerability

**Initial Triage:**
- Acknowledge alert within 5 minutes (SLA)
- Assess severity (CRITICAL, HIGH, MEDIUM, LOW)
- Determine if it's a false positive
- Create incident ticket (Jira, Linear, GitHub Issues)

---

### Phase 2: Investigation

**Gather Evidence:**
1. **Log Analysis:**
   ```bash
   # Search security logs
   grep "sql_injection" /var/log/paiid/security.log | tail -100

   # Check access logs for suspicious IPs
   grep "192.168.1.100" /var/log/nginx/access.log
   ```

2. **Database Queries:**
   ```sql
   -- Find all requests from suspicious IP
   SELECT * FROM security_events
   WHERE client_ip = '192.168.1.100'
   ORDER BY timestamp DESC
   LIMIT 100;

   -- Find all failed login attempts in last hour
   SELECT user_email, client_ip, count(*) as attempts
   FROM auth_events
   WHERE event_type = 'auth.login.failed'
   AND timestamp > now() - INTERVAL '1 hour'
   GROUP BY user_email, client_ip
   HAVING count(*) > 5;
   ```

3. **External Threat Intelligence:**
   ```bash
   # Check IP reputation
   curl https://api.abuseipdb.com/api/v2/check?ipAddress=192.168.1.100 \
     -H "Key: YOUR_API_KEY"

   # Check VirusTotal
   curl https://www.virustotal.com/vtapi/v2/ip-address/report?ip=192.168.1.100 \
     -H "x-apikey: YOUR_API_KEY"
   ```

**Determine Scope:**
- How many users affected?
- What data was accessed?
- How long has the attack been ongoing?
- Are there other compromised systems?

**Root Cause Analysis:**
- Which vulnerability was exploited?
- How did the attacker gain access?
- What was the attack vector?

---

### Phase 3: Containment

**Immediate Actions (Within 15 minutes):**

1. **Block Malicious IP:**
   ```python
   # Add IP to blocklist
   from app.core.security import block_ip

   block_ip(
       ip_address="192.168.1.100",
       reason="SQL injection attempt",
       duration_hours=24,
       severity="CRITICAL"
   )
   ```

2. **Invalidate Compromised Sessions:**
   ```python
   # Revoke all sessions for compromised user
   from app.core.auth import revoke_all_sessions

   revoke_all_sessions(user_id=123)
   ```

3. **Enable Enhanced Monitoring:**
   ```python
   # Increase logging verbosity
   import logging
   logging.getLogger('app.security').setLevel(logging.DEBUG)

   # Enable request/response logging
   app.middleware.add(FullRequestResponseLogger)
   ```

4. **Notify Stakeholders:**
   - Security team
   - Affected users (if data breach)
   - Legal/compliance team (if GDPR/regulatory impact)

**Eradication (Within 1 hour):**

5. **Patch Vulnerability:**
   - Deploy emergency security patch
   - Update dependencies with known vulnerabilities
   - Apply security hardening measures

6. **Remove Backdoors:**
   - Check for unauthorized users/API keys
   - Review recent code changes
   - Scan for web shells or malicious files

---

### Phase 4: Recovery

**Restore Normal Operations:**

1. **Verify Security Posture:**
   ```bash
   # Run security audit
   python scripts/security_audit.py

   # Verify all patches applied
   pip-audit
   npm audit
   ```

2. **Gradual Service Restoration:**
   - Remove IP blocks (if false positive confirmed)
   - Re-enable affected features
   - Monitor closely for 24 hours

3. **Communication:**
   - Notify users that incident is resolved
   - Publish post-mortem (public or internal)
   - Update security documentation

**Post-Incident Review (Within 1 week):**

4. **Document Lessons Learned:**
   - What went well?
   - What could be improved?
   - Were detection/response times adequate?
   - Do monitoring rules need tuning?

5. **Implement Preventive Measures:**
   - Add new detection rules
   - Update security policies
   - Conduct security training
   - Schedule follow-up audits

---

### Escalation Procedures

**Level 1: On-Call Engineer**
- Receives initial alert
- Performs triage and investigation
- Contains threat if straightforward

**Level 2: Security Team Lead**
- Escalated if incident is CRITICAL or unresolved after 30 minutes
- Coordinates response across teams
- Makes containment decisions

**Level 3: CTO / CISO**
- Escalated if data breach, legal implications, or major outage
- Handles external communications
- Approves emergency response procedures

**Level 4: Executive Leadership**
- Escalated for company-wide impact
- Public disclosure decisions
- Regulatory reporting

---

## Log Analysis

### Security Log Format

**Standard Security Event Log:**
```json
{
  "timestamp": "2025-10-27T14:32:15.123Z",
  "event_id": "evt_abc123",
  "event_type": "auth.login.failed",
  "severity": "MEDIUM",
  "client_ip": "192.168.1.100",
  "user_email": "user@example.com",
  "user_agent": "Mozilla/5.0...",
  "endpoint": "/api/auth/login",
  "method": "POST",
  "status_code": 401,
  "failure_reason": "invalid_password",
  "geolocation": {
    "country": "US",
    "region": "CA",
    "city": "San Francisco",
    "latitude": 37.7749,
    "longitude": -122.4194
  },
  "request_id": "req_xyz789",
  "session_id": "sess_def456"
}
```

### Log Analysis Queries

**Find Brute Force Attacks:**
```bash
# Grep for high-frequency failed logins
grep "auth.login.failed" security.log | \
  awk '{print $4}' | \  # Extract IP
  sort | uniq -c | \    # Count occurrences
  sort -rn | \          # Sort by count
  head -20              # Top 20
```

**SQL Injection Attempts:**
```bash
# Search for SQL injection patterns
grep -E "(union|select|drop|insert|delete).*from" access.log -i | \
  awk '{print $1, $7}' | \  # IP and URL
  sort | uniq -c
```

**CSRF Attack Detection:**
```bash
# Find POST requests with missing/invalid CSRF tokens
grep "csrf.validation.failed" security.log | \
  jq -r '[.timestamp, .client_ip, .endpoint] | @csv'
```

**Geographic Anomalies:**
```bash
# Find users logging in from multiple countries
grep "auth.login.success" security.log | \
  jq -r '[.user_email, .geolocation.country] | @csv' | \
  sort | uniq -c | \
  awk '$1 > 1 {print}'  # Users with >1 country
```

---

## Automated Detection Rules

### Rule 1: Brute Force Detection

```python
# Pseudocode for brute force detection
class BruteForceDetector:
    def __init__(self):
        self.failure_counts = {}  # ip -> count
        self.threshold = 10
        self.window = 300  # 5 minutes

    def check_login_attempt(self, ip, success):
        if success:
            self.failure_counts[ip] = 0
            return

        # Increment failure count
        if ip not in self.failure_counts:
            self.failure_counts[ip] = 0
        self.failure_counts[ip] += 1

        # Check threshold
        if self.failure_counts[ip] >= self.threshold:
            self.trigger_alert(ip, "brute_force")
            self.block_ip(ip, duration_minutes=15)
```

### Rule 2: Anomaly Detection (Machine Learning)

```python
# Use Isolation Forest for anomaly detection
from sklearn.ensemble import IsolationForest

class AnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(contamination=0.01)  # 1% anomaly rate

    def train(self, normal_traffic_features):
        """
        Features: [requests_per_minute, unique_endpoints, avg_response_time,
                   failed_auth_rate, geographic_distance, ...]
        """
        self.model.fit(normal_traffic_features)

    def detect(self, current_traffic_features):
        prediction = self.model.predict([current_traffic_features])
        if prediction == -1:  # Anomaly detected
            self.trigger_alert("traffic_anomaly", features=current_traffic_features)
```

### Rule 3: Credential Stuffing Detection

```python
# Detect credential stuffing attacks
class CredentialStuffingDetector:
    def __init__(self):
        self.recent_usernames = set()
        self.threshold = 50  # 50+ different usernames from 1 IP
        self.window = 600  # 10 minutes

    def check_login(self, ip, username):
        # Track unique usernames per IP
        key = f"{ip}:{time.time() // self.window}"
        if key not in self.recent_usernames:
            self.recent_usernames[key] = set()

        self.recent_usernames[key].add(username)

        # Check threshold
        if len(self.recent_usernames[key]) >= self.threshold:
            self.trigger_alert(ip, "credential_stuffing")
            self.block_ip(ip, duration_hours=24)
```

---

## Maintenance & Review

### Daily Tasks
- [ ] Review overnight security alerts
- [ ] Check failed login report
- [ ] Verify backup completion
- [ ] Monitor rate limit violations

### Weekly Tasks
- [ ] Run dependency security audit (`pip-audit`, `npm audit`)
- [ ] Review and triage medium-severity alerts
- [ ] Analyze security dashboard trends
- [ ] Update IP blocklist (remove expired)

### Monthly Tasks
- [ ] Comprehensive security log review
- [ ] Update detection rules based on trends
- [ ] Review and update this documentation
- [ ] Security metrics report to leadership

### Quarterly Tasks
- [ ] Full security audit (internal or external)
- [ ] Penetration testing
- [ ] Review and update incident response procedures
- [ ] Security team training

---

## Contact Information

**Security Team:**
- Email: security-team@paiid.com
- Slack: #security-alerts
- PagerDuty: security-oncall

**On-Call Schedule:**
- Primary: security-team@pagerduty.com
- Escalation: cto@paiid.com

**External Resources:**
- Incident Response Partner: [External Security Firm]
- Bug Bounty Program: security@paiid.com
- Vulnerability Disclosure: https://paiid.com/security/disclosure

---

## Appendix A: Common Security Queries

```sql
-- Failed logins in last 24 hours
SELECT client_ip, user_email, count(*) as attempts
FROM security_events
WHERE event_type = 'auth.login.failed'
AND timestamp > now() - INTERVAL '24 hours'
GROUP BY client_ip, user_email
ORDER BY attempts DESC;

-- Rate limit violations by endpoint
SELECT endpoint, count(*) as violations
FROM rate_limit_events
WHERE status_code = 429
GROUP BY endpoint
ORDER BY violations DESC;

-- CSRF failures by IP
SELECT client_ip, count(*) as failures
FROM security_events
WHERE event_type = 'csrf.validation.failed'
GROUP BY client_ip
ORDER BY failures DESC;

-- Unusual login locations
SELECT user_id,
       COUNT(DISTINCT geolocation.country) as countries,
       array_agg(DISTINCT geolocation.country) as country_list
FROM auth_events
WHERE event_type = 'auth.login.success'
GROUP BY user_id
HAVING COUNT(DISTINCT geolocation.country) > 2;
```

---

**Last Updated:** October 27, 2025
**Next Review:** November 27, 2025
**Document Owner:** Security Team Lead
