# PaiiD Frontend Development Guide

## Onboarding Bypass System

The PaiiD application has a user onboarding flow (UserSetupAI) that must be completed before accessing the main RadialMenu interface. To streamline development, multiple bypass mechanisms are available.

### Automatic Development Bypass

**Status:** ENABLED by default in development mode

When running `npm run dev`, the onboarding screen is automatically bypassed based on `process.env.NODE_ENV === 'development'`. You'll see:

- Orange banner at the top: "🔧 DEVELOPMENT MODE | Onboarding Bypass Active"
- Immediate access to RadialMenu with CompletePaiiDLogo visible
- No localStorage manipulation required

**Location:** `pages/index.tsx:29` (ENABLE_DEV_BYPASS flag)

### Manual Keyboard Shortcut

**Shortcut:** `Ctrl+Shift+A` (Windows/Linux) or `Cmd+Shift+A` (Mac)

Activates admin bypass anytime, setting:

- `localStorage['user-setup-complete'] = 'true'`
- `localStorage['admin-bypass'] = 'true'`
- `localStorage['bypass-timestamp'] = <current ISO timestamp>`

**Location:** `pages/index.tsx:49-75` (keyboard event handler)

### Manual LocalStorage Method

If you need to manually control the bypass:

```javascript
// Browser Console (F12)

// Bypass onboarding
localStorage.setItem("user-setup-complete", "true");
location.reload();

// Reset to onboarding (for testing)
localStorage.clear();
location.reload();
```

## LocalStorage Flags

The application uses these localStorage keys:

| Key                   | Values             | Purpose                      |
| --------------------- | ------------------ | ---------------------------- |
| `user-setup-complete` | `'true'` \| `null` | Controls onboarding gate     |
| `admin-bypass`        | `'true'` \| `null` | Indicates manual bypass used |
| `bypass-timestamp`    | ISO timestamp      | When bypass was activated    |
| `trading-preferences` | JSON object        | User's trading preferences   |
| `watchlist`           | JSON array         | User's stock watchlist       |

## Logo System

### Current Logo Component

**Component:** `CompletePaiiDLogo.tsx`
**Used In:**

- `RadialMenu.tsx` (main navigation)
- `UserSetupAI.tsx` (onboarding header - size 60)
- `UserSetup.tsx` (manual form header - size 60)
- `index.tsx` (imported but not directly rendered)

**Old Logo:** `PaiiDLogo.tsx` was **deleted** - no longer exists

### Logo Visibility

**Problem:** "Logo not showing despite successful deployment"

**Root Cause:** If you see the onboarding screen (UserSetupAI) instead of RadialMenu:

- The new logo IS deployed correctly
- UserSetupAI shows CompletePaiiDLogo at size 60
- RadialMenu (with larger logo) never renders due to onboarding gate
- Use bypass methods above to see RadialMenu

**Verification:**

1. Check for dev banner (orange bar) → bypass is working
2. No banner → Enable dev bypass (Ctrl+Shift+A)
3. See RadialMenu → CompletePaiiDLogo is visible

## Troubleshooting

### "Old logo still showing"

1. **Clear Next.js cache:**

   ```bash
   cd frontend
   rm -rf .next
   npm run dev
   ```

2. **Clear browser cache:**

   ```javascript
   // Browser Console
   location.reload(true); // Hard reload
   ```

3. **Verify component imports:**
   ```bash
   grep -r "CompletePaiiDLogo" components/ pages/
   # Should show: RadialMenu.tsx, UserSetupAI.tsx, UserSetup.tsx, index.tsx
   ```

### "Can't access RadialMenu"

**Symptom:** Stuck on UserSetupAI screen

**Solution:**

1. Check dev banner is visible (should auto-bypass in dev mode)
2. If no banner, press `Ctrl+Shift+A`
3. If still stuck, run: `localStorage.setItem('user-setup-complete', 'true'); location.reload();`

### "Logo appears but looks wrong"

Check which component is rendering:

```javascript
// Browser Console
// Open React DevTools → Components
// Search for "CompletePaiiDLogo"
// Verify it's mounted under RadialMenu (not UserSetupAI)
```

## Production vs Development Behavior

| Environment                     | Onboarding             | Logo Visibility                                     | Banner                  |
| ------------------------------- | ---------------------- | --------------------------------------------------- | ----------------------- |
| **Development** (`npm run dev`) | Bypassed automatically | RadialMenu logo visible immediately                 | Orange dev banner shown |
| **Production** (`npm start`)    | Required first time    | UserSetupAI logo → RadialMenu logo after completion | No banner               |

## Testing Onboarding Flow

To test the actual onboarding experience in development:

```javascript
// Browser Console
localStorage.clear();
location.reload();
// Complete the onboarding wizard manually
```

After completing onboarding, `user-setup-complete` will be set to `'true'` and you'll see RadialMenu.

## Environment Variables

**Development Detection:**

```typescript
const ENABLE_DEV_BYPASS = process.env.NODE_ENV === "development";
```

**Values:**

- `npm run dev` → `NODE_ENV='development'` → Bypass active
- `npm run build && npm start` → `NODE_ENV='production'` → Normal flow

## Quick Reference

## Corporate npm registry & security audits

The frontend uses a self-hosted npm-compatible registry for dependency installs and audit reports. This registry proxies the public advisory API so that `npm audit` can run entirely inside the corporate network.

### One-time setup

1. Make sure you can reach the internal registry (Verdaccio, Nexus, etc.) from the corporate VPN. The local developer sandbox exposes it at `http://127.0.0.1:4873/`.
2. Populate `frontend/.npmrc` with the registry details:
   ```ini
   registry=http://127.0.0.1:4873/
   audit=true
   audit-level=moderate
   audit-registry=http://127.0.0.1:4873/-/npm/v1/security
   always-auth=true
   //127.0.0.1:4873/:_authToken=<paste your corporate token>
   ```
   Replace the token with the credential issued by the platform team. The `.npmrc` file is committed so every audit invocation inherits these defaults.
3. If you prefer storing credentials outside source control, delete the `_authToken` line from `.npmrc` and set it locally with:
   ```bash
   npm config set //127.0.0.1:4873/:_authToken "<token>" --location=project --prefix frontend
   ```

### Running security audits

1. Start the internal registry or ensure the corporate proxy is reachable.
2. Execute the audit from the repository root:
   ```bash
   npm audit --prefix frontend
   ```
   The command uses the registry and advisory proxy from `.npmrc` and reports vulnerabilities without leaving the network perimeter.
3. Capture the report output in tickets or status updates as required by the security review process.

**Immediate RadialMenu Access:**

```bash
npm run dev  # Auto-bypass in development
```

**Test Onboarding Flow:**

```javascript
localStorage.clear();
location.reload(); // Reset
```

**Manual Bypass:**

```javascript
localStorage.setItem("user-setup-complete", "true");
location.reload();
// OR press Ctrl+Shift+A
```

**Verify Logo Component:**

```bash
ls -lh components/CompletePaiiDLogo.tsx  # Should exist (18KB)
ls -lh components/PaiiDLogo.tsx 2>/dev/null  # Should NOT exist (deleted)
```

## Files Modified (October 2025 Logo Fix)

- `pages/index.tsx` - Added ENABLE_DEV_BYPASS flag and dev banner
- `components/UserSetup.tsx` - Updated to use CompletePaiiDLogo
- `components/UserSetupAI.tsx` - Already using CompletePaiiDLogo
- `components/RadialMenu.tsx` - Already using CompletePaiiDLogo
- `components/PaiiDLogo.tsx` - DELETED (old logo removed)
- `components/CompletePaiiDLogo.tsx` - NEW logo component (18KB)

## Support

If the new logo still doesn't appear after following this guide:

1. Verify `process.env.NODE_ENV === 'development'` in console
2. Check React DevTools for CompletePaiiDLogo in component tree
3. Verify dev server restarted after code changes
4. Clear all caches (browser + .next folder)
5. Check console for TypeScript/React errors
