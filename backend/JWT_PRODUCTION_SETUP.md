# JWT Production Setup for Render

## Issue Fixed
Added `email-validator>=2.0.0` to `requirements.txt` to fix the authentication router deployment failure.

## Required Environment Variable

The authentication system requires a secure JWT secret key for production. Add this to your Render backend environment variables:

### Environment Variable to Add

**Variable Name**: `JWT_SECRET_KEY`

**Variable Value** (generated secure key):
```
B4JiaGcf5ypQ9agSWbhzUtI3_koWkU6QrjQyTaOlt9CzQy70H82omFJaY5-dmLDULjsF8YLKIK4s0pDArQM54Q
```

## How to Add in Render Dashboard

1. Go to your **paiid-backend** service in Render
2. Navigate to **Environment** tab
3. Click **Add Environment Variable**
4. Set:
   - **Key**: `JWT_SECRET_KEY`
   - **Value**: `B4JiaGcf5ypQ9agSWbhzUtI3_koWkU6QrjQyTaOlt9CzQy70H82omFJaY5-dmLDULjsF8YLKIK4s0pDArQM54Q`
5. Click **Save Changes**
6. Render will automatically redeploy

## Security Notes

- **NEVER commit this key to git**
- This key is used to sign JWT tokens (access + refresh tokens)
- If compromised, all existing tokens become invalid and users must re-authenticate
- Key rotation: Generate a new key and update Render environment variable (will invalidate all sessions)

## JWT Configuration (Current Settings)

The following JWT settings are configured in `backend/app/core/config.py`:

- **Algorithm**: HS256
- **Access Token Expiry**: 15 minutes
- **Refresh Token Expiry**: 7 days
- **Secret Key**: From `JWT_SECRET_KEY` env var (defaults to dev key if not set)

## Testing

After adding the environment variable and deploying:

1. **Test registration**:
   ```bash
   curl -X POST https://paiid-backend.onrender.com/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "Test1234"}'
   ```

2. **Test login**:
   ```bash
   curl -X POST https://paiid-backend.onrender.com/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "Test1234"}'
   ```

3. **Test protected endpoint**:
   ```bash
   curl https://paiid-backend.onrender.com/api/auth/me \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
   ```

## Deployment Fix Summary

**Problem**: Backend failing with `ModuleNotFoundError: No module named 'email_validator'`

**Solution**: Added `email-validator>=2.0.0` to `requirements.txt`

**Result**: Backend will now deploy successfully with full authentication support.
