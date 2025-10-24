# Pre-launch Validation Guide

**Purpose**: Comprehensive validation system to prevent deployment issues and ensure production readiness.

**Components**: Port availability, Python version, dependencies, environment variables, external services.

---

## 🎯 Overview

The pre-launch validation system runs comprehensive checks before application startup to prevent common deployment issues:

- **Port conflicts** (zombie processes)
- **Missing dependencies** (import errors)
- **Environment misconfiguration** (missing secrets)
- **External service connectivity** (API availability)
- **Python version compatibility** (3.10+ required)

---

## 🚀 Quick Start

### Run Validation

```bash
# Basic validation (warnings only)
python -m app.core.prelaunch

# Strict validation (fails on warnings)
python -m app.core.prelaunch --strict

# Check-only mode (no modifications)
python -m app.core.prelaunch --check-only
```

### Integration Points

```bash
# Backend startup (automatic)
cd backend && bash start.sh

# Manual validation
python -m app.core.prelaunch --strict

# CI/CD integration
python -m app.core.prelaunch --strict && bash start.sh
```

---

## 🔍 Validation Checks

### 1. Port Availability Check

**Purpose**: Prevents zombie process conflicts that cause 500 errors.

**What it checks**:
- Target port (default: 8001) is available
- No existing processes listening on port
- Socket binding test successful

**Implementation**:
```python
def validate_port_availability(self) -> ValidationResult:
    port = int(os.getenv('PORT', '8001'))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('127.0.0.1', port))
        sock.close()
        return ValidationResult(success=True, message=f"Port {port} available")
    except OSError:
        return ValidationResult(success=False, message=f"Port {port} in use")
```

**Common Issues**:
- Zombie uvicorn processes
- Port already bound
- Socket handle not released

**Resolution**:
```bash
# Kill zombie processes
bash backend/scripts/cleanup.sh 8001

# Or manually
powershell -Command "Get-Process python | Stop-Process -Force"
```

### 2. Python Version Validation

**Purpose**: Ensures Python 3.10+ compatibility.

**What it checks**:
- Python version >= 3.10
- sys.version_info compatibility
- Version string parsing

**Implementation**:
```python
def validate_python_version(self) -> ValidationResult:
    major, minor = sys.version_info[:2]
    if (major, minor) >= (3, 10):
        return ValidationResult(success=True, message=f"Python {major}.{minor} OK")
    else:
        return ValidationResult(success=False, message=f"Python 3.10+ required, found {major}.{minor}")
```

**Common Issues**:
- Python 3.9 or earlier
- Virtual environment issues
- PATH configuration

**Resolution**:
```bash
# Check Python version
python --version

# Upgrade Python (if needed)
# Install Python 3.10+ from python.org
```

### 3. Critical Dependencies Check

**Purpose**: Catches import errors before startup.

**What it checks**:
- fastapi, uvicorn, cachetools, anthropic, psutil
- sentry_sdk, redis, sqlalchemy
- Import success for each package

**Implementation**:
```python
def validate_critical_dependencies(self) -> ValidationResult:
    critical_packages = ['fastapi', 'uvicorn', 'cachetools', 'anthropic', 'psutil']
    missing = []
    for package in critical_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if not missing:
        return ValidationResult(success=True, message="All dependencies available")
    else:
        return ValidationResult(success=False, message=f"Missing: {', '.join(missing)}")
```

**Common Issues**:
- Missing pip packages
- Virtual environment not activated
- Version conflicts

**Resolution**:
```bash
# Install missing packages
pip install fastapi uvicorn cachetools anthropic psutil sentry-sdk redis sqlalchemy

# Or install from requirements
pip install -r backend/requirements.txt
```

### 4. Required Secrets Validation

**Purpose**: Ensures all required environment variables are configured.

**What it checks**:
- API_TOKEN (required)
- ALPACA_PAPER_API_KEY (required)
- ALPACA_PAPER_SECRET_KEY (required)
- TRADIER_API_KEY (required)
- SENTRY_DSN (required for production)

**Implementation**:
```python
def validate_required_secrets(self) -> ValidationResult:
    required_vars = ['API_TOKEN', 'ALPACA_PAPER_API_KEY', 'ALPACA_PAPER_SECRET_KEY', 'TRADIER_API_KEY', 'SENTRY_DSN']
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if not missing:
        return ValidationResult(success=True, message="All required secrets configured")
    else:
        return ValidationResult(success=False, message=f"Missing: {', '.join(missing)}")
```

**Common Issues**:
- Missing .env file
- Environment variables not set
- Typos in variable names

**Resolution**:
```bash
# Check .env file exists
ls -la backend/.env

# Verify environment variables
echo $API_TOKEN
echo $SENTRY_DSN

# Set missing variables
export API_TOKEN="your-token"
export SENTRY_DSN="your-sentry-dsn"
```

### 5. Optional Secrets Check

**Purpose**: Reports on optional environment variables.

**What it checks**:
- ANTHROPIC_API_KEY
- DATABASE_URL
- REDIS_URL
- SENTRY_ENVIRONMENT
- LOG_LEVEL

**Implementation**:
```python
def validate_optional_secrets(self) -> ValidationResult:
    optional_vars = ['ANTHROPIC_API_KEY', 'DATABASE_URL', 'REDIS_URL', 'SENTRY_ENVIRONMENT', 'LOG_LEVEL']
    configured = [var for var in optional_vars if os.getenv(var)]
    
    return ValidationResult(
        success=True,
        message=f"{len(configured)}/{len(optional_vars)} optional secrets configured",
        details={"configured": configured, "missing": [var for var in optional_vars if not os.getenv(var)]}
    )
```

### 6. External Services Check

**Purpose**: Tests connectivity to external APIs.

**What it checks**:
- Tradier API reachability
- Alpaca API reachability
- Response times
- Error handling

**Implementation**:
```python
async def validate_external_services(self) -> ValidationResult:
    services = {
        'Tradier API': 'https://api.tradier.com/v1',
        'Alpaca API': 'https://paper-api.alpaca.markets'
    }
    
    results = {}
    async with httpx.AsyncClient(timeout=5.0) as client:
        for name, url in services.items():
            try:
                response = await client.get(f"{url}/health", follow_redirects=True)
                results[name] = {"status": "reachable", "status_code": response.status_code}
            except Exception as e:
                results[name] = {"status": "unreachable", "error": str(e)}
    
    reachable = sum(1 for r in results.values() if r["status"] == "reachable")
    return ValidationResult(success=True, message=f"{reachable}/{len(services)} services reachable")
```

**Common Issues**:
- Network connectivity
- API service down
- Firewall blocking
- DNS resolution

**Resolution**:
```bash
# Test connectivity
curl -I https://api.tradier.com/v1
curl -I https://paper-api.alpaca.markets

# Check network
ping google.com
nslookup api.tradier.com
```

---

## 🛠️ Troubleshooting

### Common Error Messages

#### "Port 8001 is in use - run cleanup first"

**Cause**: Zombie processes occupying the port.

**Solution**:
```bash
# Run cleanup script
bash backend/scripts/cleanup.sh 8001

# Or manually kill processes
powershell -Command "Get-Process python | Stop-Process -Force"

# Verify port is free
netstat -ano | findstr ":8001"
```

#### "Python 3.10+ required, found 3.9.x"

**Cause**: Python version too old.

**Solution**:
```bash
# Check current version
python --version

# Install Python 3.10+ from python.org
# Or use pyenv/conda to manage versions
```

#### "Missing critical dependencies: fastapi, uvicorn"

**Cause**: Packages not installed.

**Solution**:
```bash
# Install from requirements
pip install -r backend/requirements.txt

# Or install individually
pip install fastapi uvicorn cachetools anthropic psutil
```

#### "Missing required secrets: SENTRY_DSN"

**Cause**: Environment variables not set.

**Solution**:
```bash
# Check .env file
cat backend/.env

# Set missing variables
export SENTRY_DSN="https://your-dsn@sentry.io/project-id"
export API_TOKEN="your-secure-token"

# Or add to .env file
echo "SENTRY_DSN=https://your-dsn@sentry.io/project-id" >> backend/.env
```

#### "Only 1/2 external services reachable"

**Cause**: Network connectivity issues.

**Solution**:
```bash
# Test individual services
curl -I https://api.tradier.com/v1
curl -I https://paper-api.alpaca.markets

# Check network connectivity
ping google.com
```

### Debug Mode

Enable detailed logging:

```bash
# Set log level
export LOG_LEVEL=DEBUG

# Run validation with debug output
python -m app.core.prelaunch --strict
```

### Manual Validation

If automated validation fails, run manual checks:

```bash
# 1. Check port availability
netstat -ano | findstr ":8001"

# 2. Check Python version
python --version

# 3. Check dependencies
python -c "import fastapi, uvicorn, cachetools, anthropic, psutil"

# 4. Check environment variables
echo $API_TOKEN
echo $SENTRY_DSN

# 5. Test external services
curl -I https://api.tradier.com/v1
```

---

## 🔧 Configuration

### Environment Variables

**Required**:
- `API_TOKEN` - Backend authentication token
- `ALPACA_PAPER_API_KEY` - Alpaca paper trading API key
- `ALPACA_PAPER_SECRET_KEY` - Alpaca paper trading secret
- `TRADIER_API_KEY` - Tradier market data API key
- `SENTRY_DSN` - Sentry error tracking DSN

**Optional**:
- `ANTHROPIC_API_KEY` - Anthropic AI API key
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `SENTRY_ENVIRONMENT` - Sentry environment (default: development)
- `LOG_LEVEL` - Logging level (default: INFO)
- `USE_TEST_FIXTURES` - Enable test fixtures (default: false)

### Validation Modes

**Basic Mode** (`python -m app.core.prelaunch`):
- Runs all checks
- Warnings don't block startup
- Suitable for development

**Strict Mode** (`python -m app.core.prelaunch --strict`):
- Runs all checks
- Warnings block startup
- Required for production

**Check-only Mode** (`python -m app.core.prelaunch --check-only`):
- Runs validation without side effects
- Suitable for CI/CD
- Doesn't modify system state

---

## 📊 Integration Points

### Backend Startup

```bash
# backend/start.sh
#!/bin/bash
set -e

# Step 0: Process cleanup
bash scripts/cleanup.sh $PORT

# Step 1: Pre-launch validation
python -m app.core.prelaunch --strict

# Step 2: Database migrations
alembic upgrade head

# Step 3: Start server
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### CI/CD Pipeline

```yaml
# .github/workflows/ci.yml
- name: Pre-launch Validation
  run: |
    cd backend
    python -m app.core.prelaunch --strict
```

### Docker Integration

```dockerfile
# Dockerfile
COPY requirements.txt .
RUN pip install -r requirements.txt

# Run validation before starting
RUN python -m app.core.prelaunch --check-only

CMD ["python", "-m", "app.core.prelaunch", "--strict", "&&", "uvicorn", "app.main:app"]
```

### Render Deployment

```yaml
# render.yaml
buildCommand: pip install -r requirements.txt && python -m app.core.prelaunch --check-only
startCommand: bash start.sh
```

---

## 📈 Monitoring

### Validation Metrics

Track validation success rates:

```python
# Telemetry events
{"event": "prelaunch_validation_start", "timestamp": "2025-10-23T20:00:00Z"}
{"event": "prelaunch_validation_complete", "timestamp": "2025-10-23T20:00:01Z", "success": true}
{"event": "port_conflict_detected", "timestamp": "2025-10-23T20:00:02Z", "port": 8001}
```

### Log Analysis

Monitor validation logs:

```bash
# Check validation results
grep "prelaunch_validation" backend/logs/app.log

# Monitor port conflicts
grep "port_conflict" backend/logs/app.log

# Track dependency issues
grep "missing_dependencies" backend/logs/app.log
```

### Alerting

Set up alerts for validation failures:

- Port conflicts → Immediate alert
- Missing dependencies → High priority
- External service failures → Medium priority
- Optional secrets missing → Low priority

---

## 🚀 Best Practices

### Development

1. **Run validation before commits**
   ```bash
   python -m app.core.prelaunch --strict
   ```

2. **Use check-only mode in CI**
   ```bash
   python -m app.core.prelaunch --check-only
   ```

3. **Monitor validation logs**
   ```bash
   tail -f backend/logs/app.log | grep prelaunch
   ```

### Production

1. **Always use strict mode**
   ```bash
   python -m app.core.prelaunch --strict
   ```

2. **Set up monitoring**
   - Track validation success rates
   - Alert on failures
   - Monitor port conflicts

3. **Regular maintenance**
   - Clean up zombie processes
   - Update dependencies
   - Verify external services

### Troubleshooting

1. **Start with port cleanup**
   ```bash
   bash backend/scripts/cleanup.sh 8001
   ```

2. **Check environment variables**
   ```bash
   env | grep -E "(API_TOKEN|SENTRY_DSN|TRADIER)"
   ```

3. **Verify dependencies**
   ```bash
   pip list | grep -E "(fastapi|uvicorn|sentry)"
   ```

4. **Test external connectivity**
   ```bash
   curl -I https://api.tradier.com/v1
   ```

---

## 📚 References

- [Backend Configuration Guide](../backend/RENDER_ENV_TEMPLATE.txt)
- [Deployment Scripts](../DEPLOYMENT_SCRIPTS_README.md)
- [Options Endpoint Bug Report](../BUG_REPORT_OPTIONS_500.md)
- [QE Acceptance Checklist](../QE_ACCEPTANCE_CHECKLIST.md)

---

**Last Updated**: October 23, 2025  
**Version**: 1.0.0  
**Maintainer**: Dr. Cursor Claude
