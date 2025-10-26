# JWT Authentication Implementation - Complete Guide

**Date**: 2025-10-25
**Status**: IMPLEMENTED - Ready for Testing
**Impact**: BREAKING CHANGE - Users must now login to access PaiiD

---

## What Changed

### The Problem

Your backend was updated to use proper JWT authentication with user accounts, but the frontend was still using the old simple API token system. This incompatibility prevented all API calls from working.

**Symptoms**:
- ❌ All endpoints returning "Invalid token: Not enough segments"
- ❌ Unable to test Tradier API fixes
- ❌ Frontend and backend authentication mismatch

### The Solution

Implemented complete JWT authentication on the frontend to match the backend's authentication system.

---

## Files Created

###1. `frontend/lib/auth.ts` - Authentication Utilities

**Purpose**: Central auth management for JWT tokens

**Key Functions**:
- `login(email, password)` - Authenticate user and store tokens
- `register(userData)` - Create new user account
- `logout()` - Clear tokens and end session
- `refreshAccessToken()` - Automatically refresh expired tokens
- `getAuthHeaders()` - Get headers for authenticated API requests
- `authenticatedFetch(endpoint, options)` - Make authenticated API calls
- `isAuthenticated()` - Check if user is logged in

**Token Storage**:
- Access token: 15-minute expiry
- Refresh token: 7-day expiry
- Stored in localStorage

### 2. `frontend/components/LoginForm.tsx` - Login UI

**Purpose**: Beautiful login/register form

**Features**:
- Tab interface (Login / Register)
- Email + password authentication
- Password strength requirements (8+ chars, 1 uppercase, 1 digit)
- Optional full name and invite code for registration
- Error handling with user-friendly messages
- Glassmorphism dark theme matching PaiiD design

---

## Changes to Existing Files

### 1. `frontend/pages/index.tsx`

**Added**:
```typescript
import LoginForm from "../components/LoginForm";
import { isAuthenticated } from "../lib/auth";

// New state
const [isLoggedIn, setIsLoggedIn] = useState(false);

// Check authentication on mount
useEffect(() => {
  const authStatus = isAuthenticated();
  setIsLoggedIn(authStatus);
}, []);

// Show login form if not authenticated
if (!isLoggedIn) {
  return <LoginForm onLoginSuccess={() => {
    setIsLoggedIn(true);
    initializeSession();
  }} />;
}
```

**Result**: Users must login before accessing the dashboard

### 2. `frontend/pages/api/proxy/[...path].ts`

**Changed**:
```typescript
// OLD: Always used hardcoded API_TOKEN
authorization: `Bearer ${API_TOKEN}`,

// NEW: Forwards JWT token from client
const clientAuth = req.headers.authorization as string;
authorization: clientAuth || `Bearer ${API_TOKEN}`,
```

**Result**: API proxy now forwards user's JWT token to backend

---

## How to Use (For Users)

### First Time Setup

1. **Navigate to PaiiD**: https://paiid-frontend.onrender.com
2. **You'll see the login screen** (new!)
3. **Click "Register" tab**
4. **Fill in the form**:
   - Email: your@email.com
   - Password: Must be 8+ characters, 1 uppercase, 1 digit
   - Full Name: (optional)
   - Invite Code: (optional - for beta testers)
5. **Click "Create Account"**
6. **You're automatically logged in!**

### Returning Users

1. Navigate to Pa iiD
2. Login screen appears
3. Enter your email and password
4. Click "Login"
5. Access granted!

### Logout

Currently, you need to manually clear localStorage:
1. Open browser DevTools (F12)
2. Go to Application tab → LocalStorage
3. Delete `paiid_access_token` and `paiid_refresh_token`

**(TODO: Add logout button to Settings page)**

---

## How It Works (Technical)

### Authentication Flow

```
┌─────────────┐
│   User      │
│  Visits App │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ Check if            │
│ JWT token exists    │
│ in localStorage     │
└──────┬──────────────┘
       │
       ▼
  ┌────────────┐
  │ Token      │───Yes──►┌──────────────┐
  │ exists?    │         │ Show         │
  └────┬───────┘         │ Dashboard    │
       │                 └──────────────┘
       No
       │
       ▼
┌──────────────────┐
│ Show Login Form  │
└────────┬─────────┘
         │
         ▼
┌──────────────────────┐
│ User enters email +  │
│ password             │
└────────┬─────────────┘
         │
         ▼
┌─────────────────────────┐
│ POST /api/auth/login    │
│ (via backend)           │
└────────┬────────────────┘
         │
         ▼
┌──────────────────────────┐
│ Backend validates        │
│ credentials, returns     │
│ access_token +           │
│ refresh_token            │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│ Store tokens in          │
│ localStorage             │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│ Show Dashboard           │
└──────────────────────────┘
```

### API Request Flow

```
┌─────────────────────┐
│ Component makes     │
│ API call            │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────────┐
│ Use authenticatedFetch() │
│ from lib/auth.ts         │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│ Check if token expired  │
└──────┬──────────────────┘
       │
   ┌───┴───┐
   │       │
Expired  Valid
   │       │
   ▼       ▼
┌──────┐ ┌────────────────┐
│Refresh│ │ Add Authorization│
│Token  │ │ header with JWT │
└───┬───┘ └───────┬────────┘
    │             │
    └─────┬───────┘
          ▼
┌──────────────────────┐
│ Send request to      │
│ /api/proxy/[...path] │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Proxy forwards JWT   │
│ to backend           │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Backend validates    │
│ JWT and processes    │
│ request              │
└──────────────────────┘
```

### Token Refresh Strategy

- **Access Token**: Expires in 15 minutes
- **Refresh Token**: Expires in 7 days
- **Auto-refresh**: Tokens are automatically refreshed 1 minute before expiry
- **Graceful handling**: If refresh fails, user is prompted to login again

---

## Testing the New System

### Test Scenario 1: New User Registration

```bash
# 1. Navigate to frontend (Render should redeploy automatically)
# 2. You'll see the login form
# 3. Click "Register"
# 4. Enter:
#    - Email: test@example.com
#    - Password: Test1234
#    - Full Name: Test User
# 5. Click "Create Account"
# 6. Should see dashboard immediately
```

### Test Scenario 2: Login with Existing User

```bash
# Assuming you already registered above:
# 1. Clear localStorage (logout)
# 2. Refresh page
# 3. Login form appears
# 4. Enter:
#    - Email: test@example.com
#    - Password: Test1234
# 5. Click "Login"
# 6. Should see dashboard
```

### Test Scenario 3: API Calls Work

```bash
# After logging in:
# 1. Click "Morning Routine" wedge
# 2. Component should load WITHOUT errors
# 3. Check DevTools Network tab:
#    - Request to /api/proxy/api/account
#    - Should have Authorization header with JWT
#    - Should return 200 (if Tradier key is correct)
```

---

## Backend Requirements

For this to work, the backend must have:

1. ✅ **User table** in database (already exists)
2. ✅ **Auth endpoints** registered:
   - POST `/api/auth/register`
   - POST `/api/auth/login`
   - POST `/api/auth/refresh`
   - POST `/api/auth/logout`
3. ✅ **JWT utilities** (in `backend/app/core/jwt.py`)
4. ✅ **get_current_user** dependency on protected endpoints

**All backend requirements are already met!**

---

## Environment Variables

### Frontend (Render)

Already configured, no changes needed:
```
NEXT_PUBLIC_BACKEND_API_BASE_URL=https://paiid-backend.onrender.com
```

### Backend (Render)

Already configured:
```
JWT_SECRET_KEY=[auto-generated]
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
DATABASE_URL=[postgres connection]
TRADIER_API_KEY=fbvCD3YvHQCfIiU0TLH0FYj71Oni
```

---

## Migration Path

### For Existing Users (if any)

If you had test users before, they should still work. Just use their email/password to login.

### Creating First User

**Option A - Via UI (Recommended)**:
1. Visit frontend
2. Click "Register"
3. Create account

**Option B - Via Database**:
```sql
-- If you need to create a user directly in the database:
INSERT INTO users (email, password_hash, full_name, role, is_active)
VALUES (
  'admin@paiid.com',
  '$2b$12$[bcrypt_hash_here]',  -- Use bcrypt to hash a password
  'Admin User',
  'owner',
  true
);
```

---

## Troubleshooting

### Issue: "Invalid token: Not enough segments"

**Cause**: Old API token being used instead of JWT

**Fix**: Clear localStorage and login again

### Issue: "Session expired. Please login again."

**Cause**: Refresh token expired (after 7 days)

**Fix**: Normal - just login again

### Issue: Login button does nothing

**Check**:
1. Browser console for errors
2. Network tab - is `/api/auth/login` request succeeding?
3. Backend logs - is the auth endpoint working?

### Issue: Can't register - password requirements

**Requirements**:
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 digit

Example valid passwords:
- `Password1`
- `MyPass123`
- `SecureP4ss`

---

## Next Steps

### Immediate (For Testing)

1. **Wait for Render to redeploy** frontend (~3-5 minutes)
2. **Create a test account** on the deployed frontend
3. **Test login/logout** flow
4. **Verify API calls work** by clicking through wedges

### Short-term Improvements

1. **Add logout button** to Settings page
2. **Add "Forgot Password"** flow
3. **Add email verification** for new accounts
4. **Add "Remember Me"** checkbox
5. **Show user profile** in header

### Long-term Features

1. **Multi-user support** - different users, different portfolios
2. **Role-based permissions** - owner, beta tester, etc.
3. **Session management** - view active sessions
4. **2FA (Two-Factor Auth)** - extra security
5. **Social login** - Google, GitHub, etc.

---

## Security Notes

### What's Secure

✅ Passwords hashed with bcrypt
✅ JWT tokens with expiration
✅ Automatic token refresh
✅ HTTPS in production
✅ CORS protection
✅ No API keys in frontend code

### What to Improve

⚠️ Add rate limiting on login endpoint
⚠️ Add account lockout after failed attempts
⚠️ Add email verification
⚠️ Add password reset flow
⚠️ Add session invalidation on password change

---

## Summary

**What we accomplished**:
1. ✅ Created complete JWT auth system for frontend
2. ✅ Built beautiful login/register UI
3. ✅ Updated dashboard to require authentication
4. ✅ Modified API proxy to forward JWT tokens
5. ✅ Committed and pushed all changes

**Current status**:
- Frontend deploying to Render (auto-deploy from main branch)
- Backend already has JWT auth configured
- Tradier API key updated on backend
- Ready for end-to-end testing

**To test Tradier integration**:
1. Wait for frontend deployment
2. Register/login
3. Click through wedges
4. Verify live data loads without errors

**Expected result**: All wedges should now work with live data from Tradier API!

---

**Implementation Date**: 2025-10-25
**Implemented By**: Claude Code
**Commits**:
- `242b722` - Fixed websocket import error
- `a6b29ba` - Implemented JWT authentication system

**Status**: 🚀 DEPLOYED - Waiting for Render redeploy
