# Security Hardening Guide

## Overview

This guide provides comprehensive security hardening strategies for the PaiiD platform, covering infrastructure security, application security, data protection, and compliance requirements. It follows industry best practices and security frameworks.

## Security Framework

### Defense in Depth Strategy
```
┌─────────────────────────────────────────────────────────────┐
│                    Security Layers                         │
├─────────────────────────────────────────────────────────────┤
│ 1. Network Security (Firewalls, VPN, DDoS Protection)     │
│ 2. Application Security (Authentication, Authorization)    │
│ 3. Data Security (Encryption, Backup, Access Control)      │
│ 4. Infrastructure Security (OS Hardening, Updates)        │
│ 5. Monitoring & Incident Response (Logging, Alerts)       │
└─────────────────────────────────────────────────────────────┘
```

### Security Principles
- **Least Privilege**: Users and systems have minimum required access
- **Defense in Depth**: Multiple security layers
- **Fail Secure**: System fails to secure state
- **Separation of Duties**: Critical functions split across users
- **Continuous Monitoring**: Real-time security monitoring

## Infrastructure Security

### 1. Network Security

#### Firewall Configuration
```bash
# UFW Firewall Rules
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow essential services
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow internal services (restrict to localhost)
sudo ufw allow from 127.0.0.1 to any port 8000
sudo ufw allow from 127.0.0.1 to any port 3000
sudo ufw allow from 127.0.0.1 to any port 5432
sudo ufw allow from 127.0.0.1 to any port 6379

# Enable firewall
sudo ufw enable
```

#### Network Segmentation
```yaml
# Docker network segmentation
version: '3.8'

networks:
  frontend:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/24
  backend:
    driver: bridge
    ipam:
      config:
        - subnet: 172.21.0.0/24
  database:
    driver: bridge
    ipam:
      config:
        - subnet: 172.22.0.0/24

services:
  frontend:
    networks:
      - frontend
      - backend
  
  backend:
    networks:
      - backend
      - database
  
  postgres:
    networks:
      - database
```

#### DDoS Protection
```nginx
# Nginx DDoS protection
http {
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=general:10m rate=1r/s;
    
    # Connection limiting
    limit_conn_zone $binary_remote_addr zone=conn_limit_per_ip:10m;
    limit_conn_zone $server_name zone=conn_limit_per_server:10m;
    
    server {
        # Apply rate limiting
        limit_req zone=general burst=20 nodelay;
        limit_conn conn_limit_per_ip 10;
        limit_conn conn_limit_per_server 1000;
        
        # Login endpoint with stricter limits
        location /api/auth/login {
            limit_req zone=login burst=3 nodelay;
            proxy_pass http://backend;
        }
        
        # API endpoints
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend;
        }
    }
}
```

### 2. Server Hardening

#### Operating System Hardening
```bash
#!/bin/bash
# os_hardening.sh

# Disable unnecessary services
sudo systemctl disable bluetooth
sudo systemctl disable cups
sudo systemctl disable avahi-daemon

# Remove unnecessary packages
sudo apt remove --purge -y telnet rsh-client rsh-redone-client
sudo apt remove --purge -y nis yp-tools
sudo apt remove --purge -y tcpd tcpdump

# Configure kernel parameters
echo "net.ipv4.conf.all.send_redirects = 0" >> /etc/sysctl.conf
echo "net.ipv4.conf.default.send_redirects = 0" >> /etc/sysctl.conf
echo "net.ipv4.conf.all.accept_redirects = 0" >> /etc/sysctl.conf
echo "net.ipv4.conf.default.accept_redirects = 0" >> /etc/sysctl.conf
echo "net.ipv4.conf.all.accept_source_route = 0" >> /etc/sysctl.conf
echo "net.ipv4.conf.default.accept_source_route = 0" >> /etc/sysctl.conf
echo "net.ipv4.conf.all.log_martians = 1" >> /etc/sysctl.conf
echo "net.ipv4.conf.default.log_martians = 1" >> /etc/sysctl.conf
echo "net.ipv4.icmp_echo_ignore_broadcasts = 1" >> /etc/sysctl.conf
echo "net.ipv4.icmp_ignore_bogus_error_responses = 1" >> /etc/sysctl.conf
echo "net.ipv4.tcp_syncookies = 1" >> /etc/sysctl.conf

# Apply changes
sudo sysctl -p
```

#### SSH Hardening
```bash
# SSH configuration
sudo nano /etc/ssh/sshd_config

# Security settings
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2
LoginGraceTime 60
AllowUsers paiid
Protocol 2
X11Forwarding no
PermitEmptyPasswords no
ChallengeResponseAuthentication no
UsePAM yes
```

#### File System Security
```bash
# Set proper file permissions
sudo chmod 700 /opt/paiid
sudo chmod 600 /opt/paiid/.env
sudo chmod 600 /opt/paiid/backend/.env
sudo chmod 600 /opt/paiid/frontend/.env.local

# Set ownership
sudo chown -R paiid:paiid /opt/paiid

# Enable audit logging
sudo apt install auditd
sudo systemctl enable auditd
sudo systemctl start auditd

# Configure audit rules
sudo nano /etc/audit/rules.d/paiid.rules
```

#### Audit Rules
```bash
# /etc/audit/rules.d/paiid.rules
# Monitor file access
-w /opt/paiid/.env -p wa -k paiid_config
-w /opt/paiid/backend/.env -p wa -k paiid_backend_config
-w /opt/paiid/frontend/.env.local -p wa -k paiid_frontend_config

# Monitor system calls
-a always,exit -F arch=b64 -S execve -k paiid_exec
-a always,exit -F arch=b32 -S execve -k paiid_exec

# Monitor network connections
-a always,exit -F arch=b64 -S socket -k paiid_network
-a always,exit -F arch=b32 -S socket -k paiid_network
```

## Application Security

### 1. Authentication Security

#### Password Security
```python
# Password policy implementation
import re
from passlib.context import CryptContext

class PasswordPolicy:
    def __init__(self):
        self.min_length = 12
        self.require_uppercase = True
        self.require_lowercase = True
        self.require_numbers = True
        self.require_special = True
        self.forbidden_patterns = [
            r'password', r'123456', r'qwerty', r'admin'
        ]
    
    def validate_password(self, password: str) -> tuple[bool, str]:
        """Validate password against policy"""
        errors = []
        
        if len(password) < self.min_length:
            errors.append(f"Password must be at least {self.min_length} characters")
        
        if self.require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("Password must contain uppercase letters")
        
        if self.require_lowercase and not re.search(r'[a-z]', password):
            errors.append("Password must contain lowercase letters")
        
        if self.require_numbers and not re.search(r'\d', password):
            errors.append("Password must contain numbers")
        
        if self.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain special characters")
        
        for pattern in self.forbidden_patterns:
            if re.search(pattern, password, re.IGNORECASE):
                errors.append("Password contains forbidden patterns")
        
        return len(errors) == 0, "; ".join(errors)

# Password hashing with secure parameters
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256", "bcrypt"],
    deprecated="auto",
    pbkdf2_sha256__default_rounds=290000,
    pbkdf2_sha256__min_rounds=100000,
    bcrypt__default_rounds=12,
    bcrypt__min_rounds=10,
    bcrypt__max_rounds=15
)
```

#### Multi-Factor Authentication
```python
# MFA implementation
import pyotp
import qrcode
from io import BytesIO
import base64

class MFAManager:
    def __init__(self):
        self.issuer_name = "PaiiD"
    
    def generate_secret(self, user_email: str) -> str:
        """Generate MFA secret for user"""
        return pyotp.random_base32()
    
    def generate_qr_code(self, user_email: str, secret: str) -> str:
        """Generate QR code for MFA setup"""
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user_email,
            issuer_name=self.issuer_name
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode()
    
    def verify_token(self, secret: str, token: str) -> bool:
        """Verify MFA token"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)
```

#### Session Security
```python
# Secure session management
from datetime import datetime, timedelta
import secrets

class SecureSessionManager:
    def __init__(self):
        self.session_timeout = timedelta(hours=1)
        self.max_concurrent_sessions = 3
    
    def create_session(self, user_id: str, ip_address: str, user_agent: str) -> str:
        """Create secure session"""
        session_id = secrets.token_urlsafe(32)
        
        session_data = {
            "user_id": user_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "is_active": True
        }
        
        # Store in Redis with expiration
        redis_client.setex(
            f"session:{session_id}",
            int(self.session_timeout.total_seconds()),
            json.dumps(session_data)
        )
        
        return session_id
    
    def validate_session(self, session_id: str, ip_address: str, user_agent: str) -> bool:
        """Validate session security"""
        session_data = redis_client.get(f"session:{session_id}")
        
        if not session_data:
            return False
        
        session = json.loads(session_data)
        
        # Check IP address
        if session["ip_address"] != ip_address:
            self.invalidate_session(session_id)
            return False
        
        # Check user agent
        if session["user_agent"] != user_agent:
            self.invalidate_session(session_id)
            return False
        
        # Check session timeout
        last_activity = datetime.fromisoformat(session["last_activity"])
        if datetime.utcnow() - last_activity > self.session_timeout:
            self.invalidate_session(session_id)
            return False
        
        # Update last activity
        session["last_activity"] = datetime.utcnow().isoformat()
        redis_client.setex(
            f"session:{session_id}",
            int(self.session_timeout.total_seconds()),
            json.dumps(session)
        )
        
        return True
```

### 2. Authorization Security

#### Role-Based Access Control (RBAC)
```python
# RBAC implementation
from enum import Enum
from typing import List, Set

class Permission(Enum):
    READ_PORTFOLIO = "read:portfolio"
    WRITE_PORTFOLIO = "write:portfolio"
    READ_ORDERS = "read:orders"
    WRITE_ORDERS = "write:orders"
    READ_ANALYTICS = "read:analytics"
    ADMIN_USERS = "admin:users"
    ADMIN_SYSTEM = "admin:system"

class Role(Enum):
    TRADER = "trader"
    ANALYST = "analyst"
    ADMIN = "admin"
    READONLY = "readonly"

class RBACManager:
    def __init__(self):
        self.role_permissions = {
            Role.TRADER: {
                Permission.READ_PORTFOLIO,
                Permission.WRITE_PORTFOLIO,
                Permission.READ_ORDERS,
                Permission.WRITE_ORDERS,
                Permission.READ_ANALYTICS
            },
            Role.ANALYST: {
                Permission.READ_PORTFOLIO,
                Permission.READ_ORDERS,
                Permission.READ_ANALYTICS
            },
            Role.ADMIN: set(Permission),
            Role.READONLY: {
                Permission.READ_PORTFOLIO,
                Permission.READ_ORDERS,
                Permission.READ_ANALYTICS
            }
        }
    
    def has_permission(self, user_role: Role, permission: Permission) -> bool:
        """Check if user role has permission"""
        return permission in self.role_permissions.get(user_role, set())
    
    def get_user_permissions(self, user_role: Role) -> Set[Permission]:
        """Get all permissions for user role"""
        return self.role_permissions.get(user_role, set())

# Permission decorator
def require_permission(permission: Permission):
    def decorator(func):
        def wrapper(*args, **kwargs):
            user = get_current_user()
            if not rbac_manager.has_permission(user.role, permission):
                raise HTTPException(
                    status_code=403,
                    detail="Insufficient permissions"
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

#### API Rate Limiting
```python
# Advanced rate limiting
from collections import defaultdict
import time
from typing import Dict, Tuple

class AdvancedRateLimiter:
    def __init__(self):
        self.limits = {
            "login": (5, 300),      # 5 attempts per 5 minutes
            "api": (100, 3600),    # 100 requests per hour
            "portfolio": (60, 3600), # 60 requests per hour
            "orders": (20, 3600),   # 20 requests per hour
        }
        self.attempts = defaultdict(list)
    
    def is_allowed(self, key: str, limit_type: str) -> Tuple[bool, Dict]:
        """Check if request is allowed"""
        if limit_type not in self.limits:
            return True, {}
        
        max_requests, window_seconds = self.limits[limit_type]
        now = time.time()
        
        # Clean old attempts
        self.attempts[key] = [
            attempt_time for attempt_time in self.attempts[key]
            if now - attempt_time < window_seconds
        ]
        
        # Check if limit exceeded
        if len(self.attempts[key]) >= max_requests:
            return False, {
                "limit_exceeded": True,
                "retry_after": int(window_seconds - (now - self.attempts[key][0])),
                "limit": max_requests,
                "window": window_seconds
            }
        
        # Record attempt
        self.attempts[key].append(now)
        
        return True, {
            "remaining": max_requests - len(self.attempts[key]),
            "reset_time": int(now + window_seconds)
        }
```

### 3. Input Validation and Sanitization

#### Input Validation
```python
# Comprehensive input validation
from pydantic import BaseModel, validator, Field
import re
from typing import Optional

class SecureOrderRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10)
    side: str = Field(..., regex="^(buy|sell)$")
    quantity: int = Field(..., gt=0, le=10000)
    order_type: str = Field(..., regex="^(market|limit|stop)$")
    price: Optional[float] = Field(None, gt=0)
    
    @validator('symbol')
    def validate_symbol(cls, v):
        if not re.match(r'^[A-Z]{1,5}$', v):
            raise ValueError('Invalid symbol format')
        return v.upper()
    
    @validator('price')
    def validate_price(cls, v, values):
        if values.get('order_type') in ['limit', 'stop'] and v is None:
            raise ValueError('Price required for limit/stop orders')
        return v

class SecureUserRegistration(BaseModel):
    email: str = Field(..., regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    password: str = Field(..., min_length=12, max_length=128)
    name: str = Field(..., min_length=2, max_length=100)
    risk_tolerance: str = Field(..., regex="^(conservative|moderate|aggressive)$")
    
    @validator('password')
    def validate_password_strength(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase letters')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase letters')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain numbers')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain special characters')
        return v
```

#### SQL Injection Prevention
```python
# SQL injection prevention
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

class SecureDatabaseManager:
    def __init__(self, db_session):
        self.db = db_session
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Secure user lookup"""
        try:
            # Use parameterized queries
            result = self.db.execute(
                text("SELECT * FROM users WHERE email = :email"),
                {"email": email}
            )
            return result.fetchone()
        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            return None
    
    def search_stocks(self, search_term: str) -> List[Stock]:
        """Secure stock search with input validation"""
        # Validate input
        if not re.match(r'^[A-Za-z0-9\s]{1,50}$', search_term):
            raise ValueError("Invalid search term")
        
        try:
            # Use parameterized query with LIKE
            result = self.db.execute(
                text("SELECT * FROM stocks WHERE symbol ILIKE :search OR name ILIKE :search LIMIT 50"),
                {"search": f"%{search_term}%"}
            )
            return result.fetchall()
        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            return []
```

## Data Security

### 1. Encryption

#### Data at Rest Encryption
```python
# Database encryption
from cryptography.fernet import Fernet
import os

class DataEncryption:
    def __init__(self):
        self.key = os.getenv('ENCRYPTION_KEY', Fernet.generate_key())
        self.cipher = Fernet(self.key)
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()

# Database field encryption
class EncryptedString:
    def __init__(self, value: str = None):
        self.encryption = DataEncryption()
        self._value = value
    
    def __str__(self):
        return self.encryption.decrypt_sensitive_data(self._value) if self._value else ""
    
    def __set__(self, value: str):
        self._value = self.encryption.encrypt_sensitive_data(value) if value else None
```

#### Data in Transit Encryption
```python
# HTTPS enforcement
from fastapi import Request, HTTPException

class HTTPSEnforcer:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, request: Request, call_next):
        # Check if request is over HTTPS
        if request.headers.get("x-forwarded-proto") != "https":
            if not request.url.hostname == "localhost":
                raise HTTPException(
                    status_code=400,
                    detail="HTTPS required"
                )
        
        response = await call_next(request)
        
        # Add security headers
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        return response
```

### 2. Data Privacy

#### Personal Data Protection
```python
# GDPR compliance
from datetime import datetime, timedelta
from typing import Dict, Any

class DataPrivacyManager:
    def __init__(self):
        self.data_retention_period = timedelta(days=365)
        self.anonymization_fields = ['email', 'name', 'phone']
    
    def anonymize_user_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize user data for GDPR compliance"""
        anonymized = user_data.copy()
        
        for field in self.anonymization_fields:
            if field in anonymized:
                anonymized[field] = self._hash_field(anonymized[field])
        
        return anonymized
    
    def _hash_field(self, value: str) -> str:
        """Hash field value for anonymization"""
        import hashlib
        return hashlib.sha256(value.encode()).hexdigest()[:8]
    
    def get_user_data_export(self, user_id: str) -> Dict[str, Any]:
        """Export user data for GDPR data portability"""
        user_data = self._get_user_data(user_id)
        return {
            "personal_data": user_data,
            "export_date": datetime.utcnow().isoformat(),
            "data_categories": ["profile", "transactions", "preferences"]
        }
    
    def delete_user_data(self, user_id: str) -> bool:
        """Delete user data for GDPR right to be forgotten"""
        try:
            # Anonymize instead of delete for audit purposes
            user_data = self._get_user_data(user_id)
            anonymized_data = self.anonymize_user_data(user_data)
            
            # Store anonymized data
            self._store_anonymized_data(user_id, anonymized_data)
            
            # Delete original data
            self._delete_original_data(user_id)
            
            return True
        except Exception as e:
            logger.error(f"Error deleting user data: {e}")
            return False
```

### 3. Backup Security

#### Encrypted Backups
```bash
#!/bin/bash
# secure_backup.sh

BACKUP_DIR="/opt/paiid/backups"
ENCRYPTION_KEY="/opt/paiid/keys/backup.key"
DATE=$(date +%Y%m%d_%H%M%S)

# Create encrypted backup
pg_dump -h localhost -U paiid paiid | \
gpg --symmetric --cipher-algo AES256 --passphrase-file $ENCRYPTION_KEY | \
gzip > $BACKUP_DIR/paiid_backup_$DATE.sql.gz.gpg

# Verify backup integrity
gpg --verify $BACKUP_DIR/paiid_backup_$DATE.sql.gz.gpg

# Upload to secure storage
aws s3 cp $BACKUP_DIR/paiid_backup_$DATE.sql.gz.gpg \
    s3://paiid-secure-backups/ \
    --server-side-encryption AES256

# Clean local backup after upload
rm $BACKUP_DIR/paiid_backup_$DATE.sql.gz.gpg
```

## Monitoring and Incident Response

### 1. Security Monitoring

#### Security Event Logging
```python
# Security event logging
import logging
from datetime import datetime
from typing import Dict, Any

class SecurityLogger:
    def __init__(self):
        self.logger = logging.getLogger('security')
        self.logger.setLevel(logging.INFO)
        
        # Create security log file
        handler = logging.FileHandler('/var/log/paiid/security.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_auth_attempt(self, email: str, ip_address: str, success: bool):
        """Log authentication attempts"""
        self.logger.info(
            f"AUTH_ATTEMPT - Email: {email}, IP: {ip_address}, Success: {success}"
        )
    
    def log_permission_denied(self, user_id: str, resource: str, action: str):
        """Log permission denied events"""
        self.logger.warning(
            f"PERMISSION_DENIED - User: {user_id}, Resource: {resource}, Action: {action}"
        )
    
    def log_suspicious_activity(self, user_id: str, activity: str, details: Dict[str, Any]):
        """Log suspicious activities"""
        self.logger.error(
            f"SUSPICIOUS_ACTIVITY - User: {user_id}, Activity: {activity}, Details: {details}"
        )
    
    def log_data_access(self, user_id: str, data_type: str, action: str):
        """Log data access events"""
        self.logger.info(
            f"DATA_ACCESS - User: {user_id}, Data: {data_type}, Action: {action}"
        )
```

#### Intrusion Detection
```python
# Intrusion detection system
from collections import defaultdict
import time
from typing import List, Dict

class IntrusionDetectionSystem:
    def __init__(self):
        self.failed_logins = defaultdict(list)
        self.suspicious_patterns = [
            "sql_injection",
            "xss_attempt",
            "path_traversal",
            "command_injection"
        ]
        self.thresholds = {
            "failed_logins": 5,
            "suspicious_requests": 3,
            "rate_limit_violations": 10
        }
    
    def analyze_request(self, request_data: Dict[str, Any]) -> bool:
        """Analyze request for suspicious patterns"""
        is_suspicious = False
        
        # Check for SQL injection patterns
        if self._detect_sql_injection(request_data):
            self._log_suspicious_activity("sql_injection", request_data)
            is_suspicious = True
        
        # Check for XSS patterns
        if self._detect_xss(request_data):
            self._log_suspicious_activity("xss_attempt", request_data)
            is_suspicious = True
        
        # Check for path traversal
        if self._detect_path_traversal(request_data):
            self._log_suspicious_activity("path_traversal", request_data)
            is_suspicious = True
        
        return is_suspicious
    
    def _detect_sql_injection(self, request_data: Dict[str, Any]) -> bool:
        """Detect SQL injection attempts"""
        sql_patterns = [
            r"union\s+select",
            r"drop\s+table",
            r"delete\s+from",
            r"insert\s+into",
            r"update\s+set",
            r"'\s*or\s*'1'\s*=\s*'1",
            r"'\s*or\s*1\s*=\s*1"
        ]
        
        for key, value in request_data.items():
            if isinstance(value, str):
                for pattern in sql_patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        return True
        
        return False
    
    def _detect_xss(self, request_data: Dict[str, Any]) -> bool:
        """Detect XSS attempts"""
        xss_patterns = [
            r"<script[^>]*>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>"
        ]
        
        for key, value in request_data.items():
            if isinstance(value, str):
                for pattern in xss_patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        return True
        
        return False
    
    def _detect_path_traversal(self, request_data: Dict[str, Any]) -> bool:
        """Detect path traversal attempts"""
        traversal_patterns = [
            r"\.\./",
            r"\.\.\\",
            r"\.\.%2f",
            r"\.\.%5c",
            r"%2e%2e%2f",
            r"%2e%2e%5c"
        ]
        
        for key, value in request_data.items():
            if isinstance(value, str):
                for pattern in traversal_patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        return True
        
        return False
```

### 2. Incident Response

#### Automated Response
```python
# Automated incident response
class IncidentResponseSystem:
    def __init__(self):
        self.response_actions = {
            "brute_force": self._handle_brute_force,
            "suspicious_activity": self._handle_suspicious_activity,
            "data_breach": self._handle_data_breach,
            "ddos_attack": self._handle_ddos_attack
        }
    
    def handle_incident(self, incident_type: str, details: Dict[str, Any]):
        """Handle security incident"""
        if incident_type in self.response_actions:
            self.response_actions[incident_type](details)
        else:
            self._handle_unknown_incident(incident_type, details)
    
    def _handle_brute_force(self, details: Dict[str, Any]):
        """Handle brute force attacks"""
        ip_address = details.get("ip_address")
        
        # Block IP address
        self._block_ip_address(ip_address)
        
        # Send alert
        self._send_security_alert("Brute Force Attack", details)
        
        # Log incident
        self._log_incident("brute_force", details)
    
    def _handle_suspicious_activity(self, details: Dict[str, Any]):
        """Handle suspicious activities"""
        user_id = details.get("user_id")
        
        # Temporarily suspend user
        self._suspend_user(user_id, duration=3600)  # 1 hour
        
        # Send alert
        self._send_security_alert("Suspicious Activity", details)
        
        # Log incident
        self._log_incident("suspicious_activity", details)
    
    def _handle_data_breach(self, details: Dict[str, Any]):
        """Handle data breach incidents"""
        # Immediate response
        self._isolate_affected_systems(details)
        
        # Notify authorities (if required)
        self._notify_authorities(details)
        
        # Notify affected users
        self._notify_affected_users(details)
        
        # Log incident
        self._log_incident("data_breach", details)
    
    def _handle_ddos_attack(self, details: Dict[str, Any]):
        """Handle DDoS attacks"""
        # Activate DDoS protection
        self._activate_ddos_protection()
        
        # Scale up resources
        self._scale_up_resources()
        
        # Send alert
        self._send_security_alert("DDoS Attack", details)
        
        # Log incident
        self._log_incident("ddos_attack", details)
```

## Compliance and Auditing

### 1. Security Auditing

#### Audit Trail
```python
# Comprehensive audit trail
class AuditTrail:
    def __init__(self):
        self.audit_logger = logging.getLogger('audit')
        self.audit_logger.setLevel(logging.INFO)
        
        # Create audit log file
        handler = logging.FileHandler('/var/log/paiid/audit.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.audit_logger.addHandler(handler)
    
    def log_user_action(self, user_id: str, action: str, resource: str, details: Dict[str, Any]):
        """Log user actions"""
        self.audit_logger.info(
            f"USER_ACTION - User: {user_id}, Action: {action}, Resource: {resource}, Details: {details}"
        )
    
    def log_system_event(self, event_type: str, details: Dict[str, Any]):
        """Log system events"""
        self.audit_logger.info(
            f"SYSTEM_EVENT - Type: {event_type}, Details: {details}"
        )
    
    def log_data_access(self, user_id: str, data_type: str, action: str, record_id: str):
        """Log data access"""
        self.audit_logger.info(
            f"DATA_ACCESS - User: {user_id}, Data: {data_type}, Action: {action}, Record: {record_id}"
        )
    
    def log_configuration_change(self, user_id: str, config_item: str, old_value: Any, new_value: Any):
        """Log configuration changes"""
        self.audit_logger.info(
            f"CONFIG_CHANGE - User: {user_id}, Item: {config_item}, Old: {old_value}, New: {new_value}"
        )
```

### 2. Compliance Reporting

#### Compliance Reports
```python
# Compliance reporting
class ComplianceReporter:
    def __init__(self):
        self.audit_trail = AuditTrail()
    
    def generate_security_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate security compliance report"""
        return {
            "report_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "security_events": self._get_security_events(start_date, end_date),
            "user_activities": self._get_user_activities(start_date, end_date),
            "data_access_logs": self._get_data_access_logs(start_date, end_date),
            "compliance_status": self._check_compliance_status(),
            "recommendations": self._generate_recommendations()
        }
    
    def generate_gdpr_report(self, user_id: str) -> Dict[str, Any]:
        """Generate GDPR compliance report"""
        return {
            "user_id": user_id,
            "data_categories": self._get_user_data_categories(user_id),
            "processing_purposes": self._get_processing_purposes(user_id),
            "data_retention": self._get_data_retention_info(user_id),
            "third_party_sharing": self._get_third_party_sharing(user_id),
            "user_rights": self._get_user_rights_status(user_id)
        }
```

## Security Testing

### 1. Automated Security Testing

#### Security Test Suite
```python
# Security test suite
import pytest
from fastapi.testclient import TestClient

class SecurityTestSuite:
    def __init__(self, client: TestClient):
        self.client = client
    
    def test_sql_injection_protection(self):
        """Test SQL injection protection"""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "'; INSERT INTO users VALUES ('hacker', 'password'); --"
        ]
        
        for malicious_input in malicious_inputs:
            response = self.client.post(
                "/api/auth/login",
                json={"email": malicious_input, "password": "test"}
            )
            assert response.status_code in [400, 401]
    
    def test_xss_protection(self):
        """Test XSS protection"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>"
        ]
        
        for payload in xss_payloads:
            response = self.client.post(
                "/api/users",
                json={"name": payload, "email": "test@example.com"}
            )
            assert payload not in response.text
    
    def test_authentication_bypass(self):
        """Test authentication bypass attempts"""
        # Test without token
        response = self.client.get("/api/portfolio")
        assert response.status_code == 401
        
        # Test with invalid token
        response = self.client.get(
            "/api/portfolio",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
    
    def test_rate_limiting(self):
        """Test rate limiting"""
        # Make multiple requests quickly
        for _ in range(10):
            response = self.client.post(
                "/api/auth/login",
                json={"email": "test@example.com", "password": "wrong"}
            )
        
        # Should be rate limited
        response = self.client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "wrong"}
        )
        assert response.status_code == 429
```

### 2. Penetration Testing

#### Penetration Testing Checklist
```bash
# Penetration testing checklist
#!/bin/bash

echo "Starting PaiiD Security Penetration Test"

# 1. Network Security Tests
echo "Testing network security..."
nmap -sS -O target_ip
nmap -sV -p 1-65535 target_ip

# 2. Web Application Tests
echo "Testing web application security..."
nikto -h https://paiid.com
sqlmap -u "https://paiid.com/api/auth/login" --data="email=test&password=test"

# 3. SSL/TLS Tests
echo "Testing SSL/TLS configuration..."
sslscan paiid.com
testssl.sh paiid.com

# 4. Authentication Tests
echo "Testing authentication security..."
hydra -l admin -P passwords.txt paiid.com http-post-form "/api/auth/login:email=^USER^&password=^PASS^:Invalid credentials"

# 5. Authorization Tests
echo "Testing authorization bypass..."
# Test privilege escalation
# Test horizontal privilege escalation
# Test vertical privilege escalation

echo "Penetration test completed"
```

## Security Checklist

### Infrastructure Security
- [ ] Firewall configured and enabled
- [ ] SSH hardened with key-based authentication
- [ ] Unnecessary services disabled
- [ ] System updates applied
- [ ] File permissions set correctly
- [ ] Audit logging enabled
- [ ] Network segmentation implemented
- [ ] DDoS protection configured

### Application Security
- [ ] Input validation implemented
- [ ] Output encoding applied
- [ ] Authentication secured with MFA
- [ ] Authorization properly implemented
- [ ] Session management secure
- [ ] Rate limiting configured
- [ ] Security headers implemented
- [ ] Error handling secure

### Data Security
- [ ] Data encrypted at rest
- [ ] Data encrypted in transit
- [ ] Backup encryption implemented
- [ ] Data retention policies enforced
- [ ] Privacy controls implemented
- [ ] Data access logging enabled
- [ ] Secure data disposal procedures

### Monitoring and Response
- [ ] Security monitoring implemented
- [ ] Incident response plan documented
- [ ] Security alerts configured
- [ ] Log analysis automated
- [ ] Threat detection enabled
- [ ] Response procedures tested
- [ ] Security team trained
- [ ] Regular security reviews scheduled

---

*Last Updated: January 15, 2024*
*Version: 1.0.0*
