"""Test script to debug auth_mode detection"""
import os
import sys


sys.path.insert(0, ".")

from app.core.config import get_settings


settings = get_settings()

# Test token from environment variable
test_token = os.getenv("API_TOKEN")
if not test_token:
    print("ERROR: API_TOKEN environment variable not set")
    print("Please set API_TOKEN in your .env file or export it")
    sys.exit(1)

authorization = f"Bearer {test_token}"

print("=" * 60)
print("AUTH MODE DETECTION TEST")
print("=" * 60)
print(f"Authorization header: {authorization[:30]}...")
print(f"settings.API_TOKEN: {settings.API_TOKEN[:20] if settings.API_TOKEN else 'MISSING'}...")
print()

# Extract token
token = authorization.split(" ", 1)[1] if authorization.startswith("Bearer ") else None
print(f"Extracted token: {token[:20] if token else 'NONE'}...")
print(f"Expected token:  {settings.API_TOKEN[:20] if settings.API_TOKEN else 'MISSING'}...")
print()

# Test comparison
if token == settings.API_TOKEN:
    print("[OK] TOKEN MATCH - Should use API_TOKEN auth mode")
else:
    print("[ERROR] TOKEN MISMATCH - Will use JWT auth mode (THIS IS THE BUG!)")
    print()
    print("Debug info:")
    print(f"  Token length: {len(token) if token else 0}")
    print(f"  Expected length: {len(settings.API_TOKEN) if settings.API_TOKEN else 0}")
    print(f"  Tokens equal: {token == settings.API_TOKEN}")
    print(f"  Token type: {type(token)}")
    print(f"  Expected type: {type(settings.API_TOKEN)}")

print("=" * 60)
