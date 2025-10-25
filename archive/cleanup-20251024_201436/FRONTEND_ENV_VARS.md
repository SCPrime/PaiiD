# 🌐 Frontend Environment Variables Configuration

**For Render Deployment**

---

## 📋 **REQUIRED ENVIRONMENT VARIABLES:**

### **Production (Render):**

```bash
# API Configuration
NEXT_PUBLIC_API_URL=https://paiid-backend.onrender.com
NEXT_PUBLIC_WS_URL=wss://paiid-backend.onrender.com

# Build Configuration
NODE_ENV=production
NEXT_TELEMETRY_DISABLED=1

# Optional: Sentry Error Tracking
NEXT_PUBLIC_SENTRY_DSN=your_sentry_dsn_here
```

### **Local Development:**

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_WS_URL=ws://localhost:8001

# Build Configuration
NODE_ENV=development
NEXT_TELEMETRY_DISABLED=1
```

---

## 🚀 **HOW TO SET IN RENDER:**

1. Go to: https://dashboard.render.com
2. Click your frontend service (after creating it)
3. Go to "Environment" tab
4. Add each variable above
5. Click "Save Changes"
6. Render will auto-redeploy

---

## ✅ **VERIFICATION:**

After deployment, your frontend should:
- Connect to backend API at `paiid-backend.onrender.com`
- Display data from backend
- Handle authentication properly
- Show real-time updates via WebSocket

---

## 🔧 **TROUBLESHOOTING:**

**Problem**: Frontend can't connect to backend  
**Solution**: Check CORS settings in backend, verify API URL is correct

**Problem**: WebSocket not connecting  
**Solution**: Ensure `wss://` (not `ws://`) for production

**Problem**: Build fails  
**Solution**: Check that all dependencies are in `package.json`

