# Deployment & Operations Guide

## Overview

This guide provides comprehensive instructions for deploying, operating, and maintaining the PaiiD platform across different environments. It covers everything from initial setup to production deployment, monitoring, and disaster recovery.

## Environment Architecture

### Development Environment
```
Developer Machine → Local Services → Test Database → Mock APIs
```

### Staging Environment
```
Staging Server → Staging Services → Staging Database → Sandbox APIs
```

### Production Environment
```
Load Balancer → Production Servers → Production Database → Live APIs
```

## Prerequisites

### System Requirements

#### Minimum Requirements
- **CPU**: 4 cores, 2.4GHz
- **RAM**: 8GB
- **Storage**: 100GB SSD
- **Network**: 100Mbps

#### Recommended Requirements
- **CPU**: 8 cores, 3.0GHz
- **RAM**: 32GB
- **Storage**: 500GB NVMe SSD
- **Network**: 1Gbps

### Software Dependencies

#### Required Software
- **Python**: 3.11+
- **Node.js**: 18+
- **PostgreSQL**: 14+
- **Redis**: 6+
- **Docker**: 20+
- **Docker Compose**: 2+

#### Optional Software
- **Nginx**: 1.20+ (for reverse proxy)
- **Certbot**: For SSL certificates
- **Prometheus**: For monitoring
- **Grafana**: For dashboards

## Development Setup

### 1. Clone Repository
```bash
git clone https://github.com/paiid/paiid.git
cd paiid
```

### 2. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

#### Required Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/paiid_dev

# Redis
REDIS_URL=redis://localhost:6379

# API Keys
TRADIER_API_KEY=your_tradier_key
ALPACA_API_KEY=your_alpaca_key
NEWS_API_KEY=your_news_key

# JWT
JWT_SECRET_KEY=your_jwt_secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Sentry
SENTRY_DSN=your_sentry_dsn
```

### 3. Database Setup
```bash
# Start PostgreSQL
sudo systemctl start postgresql

# Create database
createdb paiid_dev

# Run migrations
cd backend
alembic upgrade head

# Seed database
python scripts/seed_database.py
```

### 4. Start Services
```bash
# Start Redis
sudo systemctl start redis

# Start backend
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start frontend (in new terminal)
cd frontend
npm install
npm run dev
```

### 5. Verify Setup
```bash
# Test backend
curl http://localhost:8000/api/health

# Test frontend
curl http://localhost:3000
```

## Docker Deployment

### 1. Docker Compose Setup
```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: paiid
      POSTGRES_USER: paiid
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://paiid:secure_password@postgres:5432/paiid
      - REDIS_URL=redis://redis:6379
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
    command: npm run dev

volumes:
  postgres_data:
  redis_data:
```

### 2. Build and Deploy
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### 3. Production Docker Setup
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend

  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      - DATABASE_URL=postgresql://paiid:${DB_PASSWORD}@postgres:5432/paiid
      - REDIS_URL=redis://redis:6379
      - ENVIRONMENT=production
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    depends_on:
      - backend
    restart: unless-stopped

  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: paiid
      POSTGRES_USER: paiid
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:6-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped
```

## Production Deployment

### 1. Server Preparation

#### Ubuntu/Debian Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3.11 python3.11-pip python3.11-venv
sudo apt install -y postgresql-14 postgresql-client-14
sudo apt install -y redis-server
sudo apt install -y nginx certbot python3-certbot-nginx
sudo apt install -y git curl wget

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

#### CentOS/RHEL Setup
```bash
# Update system
sudo yum update -y

# Install EPEL repository
sudo yum install -y epel-release

# Install required packages
sudo yum install -y python311 python311-pip python311-venv
sudo yum install -y postgresql14-server postgresql14
sudo yum install -y redis
sudo yum install -y nginx certbot python3-certbot-nginx
sudo yum install -y git curl wget

# Install Node.js
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs

# Install Docker
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

### 2. Database Setup

#### PostgreSQL Configuration
```bash
# Initialize database
sudo postgresql-setup --initdb

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql
CREATE DATABASE paiid;
CREATE USER paiid WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE paiid TO paiid;
\q
```

#### Database Optimization
```bash
# Edit PostgreSQL configuration
sudo nano /var/lib/pgsql/data/postgresql.conf

# Optimize for production
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### 3. Application Deployment

#### Backend Deployment
```bash
# Create application directory
sudo mkdir -p /opt/paiid
sudo chown $USER:$USER /opt/paiid
cd /opt/paiid

# Clone repository
git clone https://github.com/paiid/paiid.git .

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Create systemd service
sudo nano /etc/systemd/system/paiid-backend.service
```

#### Systemd Service Configuration
```ini
[Unit]
Description=PaiiD Backend API
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=paiid
Group=paiid
WorkingDirectory=/opt/paiid/backend
Environment=PATH=/opt/paiid/venv/bin
ExecStart=/opt/paiid/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Frontend Deployment
```bash
# Build frontend
cd frontend
npm install
npm run build

# Create systemd service
sudo nano /etc/systemd/system/paiid-frontend.service
```

#### Frontend Systemd Service
```ini
[Unit]
Description=PaiiD Frontend
After=network.target paiid-backend.service

[Service]
Type=exec
User=paiid
Group=paiid
WorkingDirectory=/opt/paiid/frontend
ExecStart=/usr/bin/npm run start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 4. Nginx Configuration

#### Reverse Proxy Setup
```nginx
# /etc/nginx/sites-available/paiid
server {
    listen 80;
    server_name paiid.com www.paiid.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name paiid.com www.paiid.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/paiid.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/paiid.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

    # API Backend
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Rate limiting
        limit_req zone=api burst=20 nodelay;
    }

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /static/ {
        alias /opt/paiid/frontend/out/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}

# Rate limiting
http {
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
}
```

#### Enable Site
```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/paiid /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 5. SSL Certificate Setup
```bash
# Install SSL certificate
sudo certbot --nginx -d paiid.com -d www.paiid.com

# Test automatic renewal
sudo certbot renew --dry-run

# Set up automatic renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Monitoring and Logging

### 1. Application Monitoring

#### Prometheus Setup
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'paiid-backend'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'paiid-frontend'
    static_configs:
      - targets: ['localhost:3000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'postgres'
    static_configs:
      - targets: ['localhost:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:9121']
```

#### Grafana Dashboard
```json
{
  "dashboard": {
    "title": "PaiiD Platform Dashboard",
    "panels": [
      {
        "title": "API Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
          }
        ]
      },
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])"
          }
        ]
      }
    ]
  }
}
```

### 2. Log Management

#### Log Rotation
```bash
# Configure logrotate
sudo nano /etc/logrotate.d/paiid

# Log rotation configuration
/opt/paiid/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 paiid paiid
    postrotate
        systemctl reload paiid-backend
    endscript
}
```

#### Centralized Logging
```yaml
# docker-compose.logging.yml
version: '3.8'

services:
  elasticsearch:
    image: elasticsearch:7.17.0
    environment:
      - discovery.type=single-node
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"

  logstash:
    image: logstash:7.17.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    ports:
      - "5044:5044"
    depends_on:
      - elasticsearch

  kibana:
    image: kibana:7.17.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch

volumes:
  elasticsearch_data:
```

## Backup and Recovery

### 1. Database Backup

#### Automated Backup Script
```bash
#!/bin/bash
# backup_database.sh

BACKUP_DIR="/opt/paiid/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="paiid_backup_$DATE.sql"

# Create backup directory
mkdir -p $BACKUP_DIR

# Create database backup
pg_dump -h localhost -U paiid paiid > $BACKUP_DIR/$BACKUP_FILE

# Compress backup
gzip $BACKUP_DIR/$BACKUP_FILE

# Upload to S3 (optional)
aws s3 cp $BACKUP_DIR/$BACKUP_FILE.gz s3://paiid-backups/

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE.gz"
```

#### Backup Schedule
```bash
# Add to crontab
sudo crontab -e

# Daily backup at 2 AM
0 2 * * * /opt/paiid/scripts/backup_database.sh

# Weekly full backup
0 2 * * 0 /opt/paiid/scripts/full_backup.sh
```

### 2. Application Backup

#### Configuration Backup
```bash
#!/bin/bash
# backup_config.sh

BACKUP_DIR="/opt/paiid/backups/config"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup configuration files
tar -czf $BACKUP_DIR/config_$DATE.tar.gz \
    /opt/paiid/.env \
    /etc/nginx/sites-available/paiid \
    /etc/systemd/system/paiid-*.service \
    /opt/paiid/backend/alembic/versions/

echo "Configuration backup completed: config_$DATE.tar.gz"
```

### 3. Disaster Recovery

#### Recovery Procedures
```bash
#!/bin/bash
# disaster_recovery.sh

# 1. Restore database
pg_restore -h localhost -U paiid -d paiid /opt/paiid/backups/latest_backup.sql

# 2. Restore configuration
tar -xzf /opt/paiid/backups/config/latest_config.tar.gz -C /

# 3. Restart services
systemctl restart paiid-backend
systemctl restart paiid-frontend
systemctl restart nginx

# 4. Verify services
curl -f http://localhost:8000/api/health || exit 1
curl -f http://localhost:3000 || exit 1

echo "Disaster recovery completed successfully"
```

## Security Hardening

### 1. System Security

#### Firewall Configuration
```bash
# Configure UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH
sudo ufw allow ssh

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow application ports (internal only)
sudo ufw allow from 127.0.0.1 to any port 8000
sudo ufw allow from 127.0.0.1 to any port 3000

# Enable firewall
sudo ufw enable
```

#### SSH Hardening
```bash
# Edit SSH configuration
sudo nano /etc/ssh/sshd_config

# Security settings
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2

# Restart SSH
sudo systemctl restart sshd
```

### 2. Application Security

#### Environment Security
```bash
# Secure environment file
sudo chmod 600 /opt/paiid/.env
sudo chown paiid:paiid /opt/paiid/.env

# Remove sensitive data from logs
echo "SENSITIVE_DATA=***" >> /opt/paiid/.env
```

#### Database Security
```sql
-- Create read-only user
CREATE USER paiid_readonly WITH PASSWORD 'readonly_password';
GRANT CONNECT ON DATABASE paiid TO paiid_readonly;
GRANT USAGE ON SCHEMA public TO paiid_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO paiid_readonly;

-- Enable SSL
ALTER SYSTEM SET ssl = on;
ALTER SYSTEM SET ssl_cert_file = '/var/lib/pgsql/data/server.crt';
ALTER SYSTEM SET ssl_key_file = '/var/lib/pgsql/data/server.key';
```

## Maintenance Procedures

### 1. Regular Maintenance

#### System Updates
```bash
#!/bin/bash
# system_update.sh

# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Python packages
cd /opt/paiid/backend
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Update Node.js packages
cd /opt/paiid/frontend
npm update

# Restart services
sudo systemctl restart paiid-backend
sudo systemctl restart paiid-frontend
```

#### Database Maintenance
```sql
-- Analyze tables for better performance
ANALYZE;

-- Vacuum database
VACUUM ANALYZE;

-- Reindex if needed
REINDEX DATABASE paiid;
```

### 2. Performance Monitoring

#### Health Checks
```bash
#!/bin/bash
# health_check.sh

# Check backend health
if ! curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "Backend health check failed"
    systemctl restart paiid-backend
fi

# Check frontend health
if ! curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "Frontend health check failed"
    systemctl restart paiid-frontend
fi

# Check database connection
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "Database connection failed"
    systemctl restart postgresql
fi

# Check Redis connection
if ! redis-cli ping > /dev/null 2>&1; then
    echo "Redis connection failed"
    systemctl restart redis
fi
```

## Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check service status
sudo systemctl status paiid-backend

# Check logs
sudo journalctl -u paiid-backend -f

# Check configuration
sudo systemctl daemon-reload
```

#### Database Connection Issues
```bash
# Test database connection
psql -h localhost -U paiid -d paiid

# Check PostgreSQL status
sudo systemctl status postgresql

# Check logs
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

#### High Memory Usage
```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head

# Check for memory leaks
sudo dmesg | grep -i "out of memory"
```

### Performance Issues

#### Slow API Responses
```bash
# Check API response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/health

# Check database performance
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"

# Check slow queries
sudo tail -f /var/log/postgresql/postgresql-14-main.log | grep "slow query"
```

#### High CPU Usage
```bash
# Check CPU usage
top -p $(pgrep -f "uvicorn")

# Profile application
python -m cProfile -o profile.stats /opt/paiid/backend/app/main.py
```

## Scaling

### Horizontal Scaling

#### Load Balancer Setup
```nginx
# nginx load balancer configuration
upstream paiid_backend {
    server 192.168.1.10:8000;
    server 192.168.1.11:8000;
    server 192.168.1.12:8000;
}

server {
    location /api/ {
        proxy_pass http://paiid_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### Database Scaling
```bash
# Set up read replicas
# Master: 192.168.1.10:5432
# Replica: 192.168.1.11:5432

# Configure streaming replication
# On master
sudo -u postgres psql -c "CREATE USER replicator REPLICATION;"

# On replica
pg_basebackup -h 192.168.1.10 -D /var/lib/postgresql/14/main -U replicator -v -P -W
```

### Vertical Scaling

#### Resource Monitoring
```bash
# Monitor resource usage
htop
iotop
nethogs

# Check disk I/O
iostat -x 1

# Check network usage
iftop
```

---

*Last Updated: January 15, 2024*
*Version: 1.0.0*
