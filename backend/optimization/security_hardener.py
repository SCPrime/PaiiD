from datetime import datetime
from typing import Any
import hashlib
import json
import logging
import re
import redis
import secrets

"""
Security Hardener
Implements comprehensive security hardening and input validation for maximum protection
"""



logger = logging.getLogger(__name__)

class SecurityHardener:
    """Comprehensive security hardening and protection"""

    def __init__(self):
        self.redis_client = redis.Redis(
            host="localhost", port=6379, db=9, decode_responses=True
        )
        self.security_policies = {
            "password_policy": {
                "min_length": 12,
                "require_uppercase": True,
                "require_lowercase": True,
                "require_numbers": True,
                "require_special_chars": True,
                "max_age_days": 90,
                "history_count": 5,
            },
            "session_policy": {
                "timeout_minutes": 30,
                "max_concurrent_sessions": 3,
                "require_https": True,
                "secure_cookies": True,
            },
            "rate_limiting": {
                "login_attempts": 5,
                "api_requests_per_minute": 60,
                "password_reset_attempts": 3,
                "block_duration_minutes": 15,
            },
            "input_validation": {
                "max_string_length": 1000,
                "sql_injection_protection": True,
                "xss_protection": True,
                "file_upload_restrictions": True,
            },
        }
        self.security_events = []
        self.blocked_ips = set()

    async def setup_security_policies(self):
        """Setup comprehensive security policies"""
        try:
            for policy_name, policy_config in self.security_policies.items():
                self.redis_client.setex(
                    f"security_policy:{policy_name}",
                    3600,  # 1 hour
                    json.dumps(policy_config),
                )

            logger.info("Security policies configured successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to setup security policies: {e}")
            return False

    async def validate_password_strength(self, password: str) -> dict[str, Any]:
        """Validate password against security policy"""
        try:
            policy = self.security_policies["password_policy"]
            validation_result = {
                "is_valid": True,
                "score": 0,
                "violations": [],
                "recommendations": [],
            }

            # Length check
            if len(password) < policy["min_length"]:
                validation_result["violations"].append(
                    f"Password must be at least {policy['min_length']} characters"
                )
                validation_result["is_valid"] = False
            else:
                validation_result["score"] += 20

            # Character type checks
            if policy["require_uppercase"] and not re.search(r"[A-Z]", password):
                validation_result["violations"].append(
                    "Password must contain uppercase letters"
                )
                validation_result["is_valid"] = False
            else:
                validation_result["score"] += 20

            if policy["require_lowercase"] and not re.search(r"[a-z]", password):
                validation_result["violations"].append(
                    "Password must contain lowercase letters"
                )
                validation_result["is_valid"] = False
            else:
                validation_result["score"] += 20

            if policy["require_numbers"] and not re.search(r"[0-9]", password):
                validation_result["violations"].append("Password must contain numbers")
                validation_result["is_valid"] = False
            else:
                validation_result["score"] += 20

            if policy["require_special_chars"] and not re.search(
                r'[!@#$%^&*(),.?":{}|<>]', password
            ):
                validation_result["violations"].append(
                    "Password must contain special characters"
                )
                validation_result["is_valid"] = False
            else:
                validation_result["score"] += 20

            # Common password check
            common_passwords = ["password", "123456", "qwerty", "admin", "letmein"]
            if password.lower() in common_passwords:
                validation_result["violations"].append("Password is too common")
                validation_result["is_valid"] = False

            # Generate recommendations
            if not validation_result["is_valid"]:
                validation_result["recommendations"] = [
                    "Use a mix of uppercase and lowercase letters",
                    "Include numbers and special characters",
                    "Avoid common words and patterns",
                    "Make it at least 12 characters long",
                ]

            return validation_result

        except Exception as e:
            logger.error(f"Failed to validate password: {e}")
            return {"is_valid": False, "error": str(e)}

    async def validate_input(
        self, input_data: str, input_type: str = "general"
    ) -> dict[str, Any]:
        """Validate and sanitize input data"""
        try:
            validation_result = {
                "is_valid": True,
                "sanitized_data": input_data,
                "violations": [],
                "security_risks": [],
            }

            policy = self.security_policies["input_validation"]

            # Length validation
            if len(input_data) > policy["max_string_length"]:
                validation_result["violations"].append(
                    f"Input exceeds maximum length of {policy['max_string_length']}"
                )
                validation_result["is_valid"] = False

            # SQL injection protection
            if policy["sql_injection_protection"]:
                sql_patterns = [
                    r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
                    r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
                    r"(\b(OR|AND)\s+'.*'\s*=\s*'.*')",
                    r"(--|\#|\/\*|\*\/)",
                ]

                for pattern in sql_patterns:
                    if re.search(pattern, input_data, re.IGNORECASE):
                        validation_result["security_risks"].append(
                            "Potential SQL injection detected"
                        )
                        validation_result["is_valid"] = False
                        break

            # XSS protection
            if policy["xss_protection"]:
                xss_patterns = [
                    r"<script[^>]*>.*?</script>",
                    r"javascript:",
                    r"on\w+\s*=",
                    r"<iframe[^>]*>",
                    r"<object[^>]*>",
                    r"<embed[^>]*>",
                ]

                for pattern in xss_patterns:
                    if re.search(pattern, input_data, re.IGNORECASE):
                        validation_result["security_risks"].append(
                            "Potential XSS attack detected"
                        )
                        validation_result["is_valid"] = False
                        break

            # Sanitize data if valid
            if validation_result["is_valid"]:
                # Basic HTML entity encoding
                sanitized = input_data.replace("<", "&lt;").replace(">", "&gt;")
                sanitized = sanitized.replace('"', "&quot;").replace("'", "&#x27;")
                sanitized = sanitized.replace("&", "&amp;")
                validation_result["sanitized_data"] = sanitized

            return validation_result

        except Exception as e:
            logger.error(f"Failed to validate input: {e}")
            return {"is_valid": False, "error": str(e)}

    async def check_rate_limits(self, client_ip: str, action: str) -> dict[str, Any]:
        """Check rate limits for security actions"""
        try:
            policy = self.security_policies["rate_limiting"]
            current_time = datetime.now()

            # Get rate limit config for action
            rate_limit_key = f"rate_limit:{action}:{client_ip}"
            attempts = self.redis_client.get(rate_limit_key)

            if attempts is None:
                attempts = 0
            else:
                attempts = int(attempts)

            # Check if blocked
            if client_ip in self.blocked_ips:
                return {
                    "allowed": False,
                    "reason": "IP address is blocked",
                    "retry_after": None,
                }

            # Check rate limits
            max_attempts = policy.get(f"{action}_attempts", 5)
            if attempts >= max_attempts:
                # Block IP temporarily
                self.blocked_ips.add(client_ip)
                self.redis_client.setex(
                    f"blocked_ip:{client_ip}",
                    policy["block_duration_minutes"] * 60,
                    "blocked",
                )

                return {
                    "allowed": False,
                    "reason": f"Rate limit exceeded for {action}",
                    "retry_after": policy["block_duration_minutes"] * 60,
                }

            # Increment attempt count
            self.redis_client.setex(rate_limit_key, 3600, attempts + 1)

            return {
                "allowed": True,
                "attempts_remaining": max_attempts - attempts - 1,
            }

        except Exception as e:
            logger.error(f"Failed to check rate limits: {e}")
            return {"allowed": True, "error": str(e)}

    async def generate_secure_token(self, length: int = 32) -> str:
        """Generate cryptographically secure token"""
        try:
            return secrets.token_urlsafe(length)
        except Exception as e:
            logger.error(f"Failed to generate secure token: {e}")
            return ""

    async def hash_password(self, password: str) -> str:
        """Hash password with secure algorithm"""
        try:
            # Generate random salt
            salt = secrets.token_hex(16)

            # Hash password with salt
            password_hash = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                salt.encode("utf-8"),
                100000,  # 100,000 iterations
            )

            # Combine salt and hash
            return f"{salt}:{password_hash.hex()}"

        except Exception as e:
            logger.error(f"Failed to hash password: {e}")
            return ""

    async def verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash"""
        try:
            if ":" not in stored_hash:
                return False

            salt, hash_part = stored_hash.split(":", 1)

            # Hash the provided password with the stored salt
            password_hash = hashlib.pbkdf2_hmac(
                "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
            )

            return password_hash.hex() == hash_part

        except Exception as e:
            logger.error(f"Failed to verify password: {e}")
            return False

    async def setup_session_security(self):
        """Setup secure session management"""
        try:
            session_config = {
                "session_timeout": self.security_policies["session_policy"][
                    "timeout_minutes"
                ]
                * 60,
                "max_sessions": self.security_policies["session_policy"][
                    "max_concurrent_sessions"
                ],
                "secure_cookies": self.security_policies["session_policy"][
                    "secure_cookies"
                ],
                "http_only": True,
                "same_site": "strict",
            }

            self.redis_client.setex(
                "session_security_config", 3600, json.dumps(session_config)
            )

            logger.info("Session security configured successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to setup session security: {e}")
            return False

    async def log_security_event(self, event_type: str, details: dict[str, Any]):
        """Log security events for monitoring and analysis"""
        try:
            security_event = {
                "event_type": event_type,
                "timestamp": datetime.now().isoformat(),
                "details": details,
                "severity": self._get_event_severity(event_type),
            }

            # Store in Redis
            self.redis_client.lpush("security_events", json.dumps(security_event))

            # Keep only last 1000 events
            self.redis_client.ltrim("security_events", 0, 999)

            # Store in security events list
            self.security_events.append(security_event)

            logger.info(f"Security event logged: {event_type}")
            return True

        except Exception as e:
            logger.error(f"Failed to log security event: {e}")
            return False

    def _get_event_severity(self, event_type: str) -> str:
        """Determine security event severity"""
        high_severity_events = [
            "sql_injection_attempt",
            "xss_attempt",
            "brute_force_attack",
            "unauthorized_access",
            "data_breach_attempt",
        ]

        medium_severity_events = [
            "rate_limit_exceeded",
            "invalid_credentials",
            "suspicious_activity",
        ]

        if event_type in high_severity_events:
            return "high"
        elif event_type in medium_severity_events:
            return "medium"
        else:
            return "low"

    async def scan_for_vulnerabilities(self) -> dict[str, Any]:
        """Scan system for potential security vulnerabilities"""
        try:
            vulnerabilities = []

            # Check for weak passwords in system
            weak_password_count = await self._check_weak_passwords()
            if weak_password_count > 0:
                vulnerabilities.append(
                    {
                        "type": "weak_passwords",
                        "severity": "high",
                        "count": weak_password_count,
                        "description": "Users with weak passwords detected",
                    }
                )

            # Check for expired sessions
            expired_sessions = await self._check_expired_sessions()
            if expired_sessions > 0:
                vulnerabilities.append(
                    {
                        "type": "expired_sessions",
                        "severity": "medium",
                        "count": expired_sessions,
                        "description": "Expired sessions not properly cleaned up",
                    }
                )

            # Check for blocked IPs that should be unblocked
            blocked_ips_count = len(self.blocked_ips)
            if blocked_ips_count > 100:  # Arbitrary threshold
                vulnerabilities.append(
                    {
                        "type": "excessive_blocked_ips",
                        "severity": "low",
                        "count": blocked_ips_count,
                        "description": "Large number of blocked IP addresses",
                    }
                )

            scan_result = {
                "timestamp": datetime.now().isoformat(),
                "vulnerabilities_found": len(vulnerabilities),
                "vulnerabilities": vulnerabilities,
                "scan_status": "completed",
            }

            return scan_result

        except Exception as e:
            logger.error(f"Failed to scan for vulnerabilities: {e}")
            return {"error": str(e)}

    async def _check_weak_passwords(self) -> int:
        """Check for users with weak passwords"""
        # This would typically query the database
        # For now, return a mock count
        return 0

    async def _check_expired_sessions(self) -> int:
        """Check for expired sessions that need cleanup"""
        # This would typically query the session store
        # For now, return a mock count
        return 0

    async def get_security_report(self) -> dict[str, Any]:
        """Generate comprehensive security report"""
        try:
            # Get recent security events
            recent_events = self.redis_client.lrange("security_events", 0, 99)
            events_data = [json.loads(event) for event in recent_events]

            # Get vulnerability scan results
            vulnerability_scan = await self.scan_for_vulnerabilities()

            # Calculate security metrics
            high_severity_events = len(
                [e for e in events_data if e.get("severity") == "high"]
            )
            medium_severity_events = len(
                [e for e in events_data if e.get("severity") == "medium"]
            )
            low_severity_events = len(
                [e for e in events_data if e.get("severity") == "low"]
            )

            security_report = {
                "timestamp": datetime.now().isoformat(),
                "security_policies_configured": len(self.security_policies),
                "recent_security_events": {
                    "total": len(events_data),
                    "high_severity": high_severity_events,
                    "medium_severity": medium_severity_events,
                    "low_severity": low_severity_events,
                },
                "vulnerability_scan": vulnerability_scan,
                "blocked_ips_count": len(self.blocked_ips),
                "security_score": self._calculate_security_score(
                    events_data, vulnerability_scan
                ),
                "recommendations": [
                    "Regular security audits and penetration testing",
                    "Implement automated security monitoring",
                    "Keep security policies up to date",
                    "Train users on security best practices",
                    "Implement multi-factor authentication",
                ],
            }

            return security_report

        except Exception as e:
            logger.error(f"Failed to generate security report: {e}")
            return {"error": str(e)}

    def _calculate_security_score(
        self, events: list[dict], vulnerabilities: dict
    ) -> int:
        """Calculate overall security score (0-100)"""
        try:
            score = 100

            # Deduct points for high severity events
            high_severity_count = len(
                [e for e in events if e.get("severity") == "high"]
            )
            score -= high_severity_count * 10

            # Deduct points for vulnerabilities
            vulnerabilities_count = vulnerabilities.get("vulnerabilities_found", 0)
            score -= vulnerabilities_count * 5

            # Ensure score doesn't go below 0
            return max(0, score)

        except Exception as e:
            logger.error(f"Failed to calculate security score: {e}")
            return 50

    async def get_optimization_report(self) -> dict[str, Any]:
        """Generate comprehensive security optimization report"""
        try:
            security_report = await self.get_security_report()

            report = {
                "optimization_status": "completed",
                "security_report": security_report,
                "policies_configured": len(self.security_policies),
                "security_hardening": "enabled",
                "input_validation": "enabled",
                "rate_limiting": "enabled",
                "password_policy": "enabled",
                "session_security": "enabled",
                "recommendations": [
                    "Regular security audits and updates",
                    "Implement automated security monitoring",
                    "Conduct penetration testing",
                    "Keep security policies current",
                    "Train users on security awareness",
                ],
                "timestamp": datetime.now().isoformat(),
            }

            return report

        except Exception as e:
            logger.error(f"Failed to generate optimization report: {e}")
            return {"error": str(e)}
