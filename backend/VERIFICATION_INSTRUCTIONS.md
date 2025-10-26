# JWT Auth Fix - Verification Instructions

## Prerequisites
1. Backend server running on port 8001
2. API token from `.env` file
3. HTTP client (curl, Thunder Client, or Postman)

## API Token
From `api-tests.http` or `.env`:
```
tuGlKvrYEoiJcv7r7oIy7zXM9pqVnaxN_74obFz6lVo
```

## Test Cases

### Test 1: API Token Authentication
**Request:**
```http
GET http://127.0.0.1:8001/api/health
Authorization: Bearer tuGlKvrYEoiJcv7r7oIy7zXM9pqVnaxN_74obFz6lVo
```

**Expected Behavior:**
- Status: 200 OK
- Backend logs should show:
  ```
  INFO: Auth request - header preview: Bearer tuGlKvrYEo...
  INFO: Extracted token: tuGlKvrYEo... (first 10 chars)
  INFO: Token matches API_TOKEN - using API_TOKEN auth mode
  INFO: Auth mode detected: api_token
  INFO: Using API token authentication
  INFO: API token auth successful - returning user: mvp_user
  ```

### Test 2: Invalid API Token
**Request:**
```http
GET http://127.0.0.1:8001/api/health
Authorization: Bearer invalid_token_123
```

**Expected Behavior:**
- Status: 401 Unauthorized
- Error message should be clear about invalid token
- Backend logs should show:
  ```
  INFO: Token doesn't match API_TOKEN - assuming JWT auth mode
  INFO: Auth mode detected: jwt
  INFO: Using JWT authentication
  ERROR: JWT validation error: Invalid token format (JWT tokens must have header.payload.signature structure)
  ```

### Test 3: Valid JWT Token (if you have one)
**Request:**
```http
GET http://127.0.0.1:8001/api/health
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Expected Behavior:**
- Status: 200 OK or 401 based on JWT validity
- Backend logs should show JWT decoding process

## Verification Checklist
- [ ] API token authentication works (Test 1)
- [ ] Logs show correct auth mode detection
- [ ] No "Not enough segments" error appears
- [ ] Error messages are clear and helpful
- [ ] MVP user is returned for API token
- [ ] JWT validation still works (if tested)

## Backend Logs to Look For
1. ✅ "Token matches API_TOKEN - using API_TOKEN auth mode"
2. ✅ "Using API token authentication"
3. ✅ "API token auth successful - returning user: mvp_user"
4. ❌ "Attempting JWT decode for token: tuGlKvrYEo..." (should NOT appear for API tokens)
5. ❌ "Not enough segments" (should NOT appear)

## Troubleshooting
If you see "Not enough segments" error:
1. Check if auth mode detection is working (look for "Token matches API_TOKEN" in logs)
2. Verify that API token matches exactly (no extra spaces, correct case)
3. Ensure backend has the latest `unified_auth.py` with enhanced logging

If JWT decode is attempted for API tokens:
1. Check that API token path has early return (line 135 in unified_auth.py)
2. Verify auth_mode == AuthMode.API_TOKEN comparison is working
3. Look for any middleware that might be modifying the authorization header
