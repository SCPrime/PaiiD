# 🚀 Frontend Deployment Guide - Render

**Deploy your PaiiD frontend in under 10 minutes!**

---

## 🎯 **QUICK DEPLOY (AUTOMATIC)**

### **Step 1: Push to GitHub** ✅ (We'll do this)

```bash
git add .
git commit -m "🚀 feat: Frontend deployment configuration"
git push origin main
```

### **Step 2: Create Render Web Service** (5 minutes)

1. **Go to Render Dashboard**:
   ```
   https://dashboard.render.com
   ```

2. **Click "New +" → "Web Service"**

3. **Connect Your GitHub Repo**:
   - Search for: `PaiiD`
   - Click "Connect"

4. **Configure Service**:
   ```
   Name: paiid-frontend
   Region: Oregon (US West) - same as backend
   Branch: main
   Root Directory: frontend
   Runtime: Node
   Build Command: npm install && npm run build
   Start Command: npm start
   ```

5. **Select Plan**:
   - **Free Tier** (great for testing!)
   - Or **Starter ($7/mo)** for always-on

6. **Add Environment Variables**:
   Click "Advanced" → Add these:
   ```
   NEXT_PUBLIC_API_URL=https://paiid-backend.onrender.com
   NEXT_PUBLIC_WS_URL=wss://paiid-backend.onrender.com
   NODE_ENV=production
   NEXT_TELEMETRY_DISABLED=1
   ```

7. **Click "Create Web Service"**

8. **Wait 3-5 minutes** for build & deployment ⏱️

9. **Done!** Your app will be live at:
   ```
   https://paiid-frontend.onrender.com
   ```

---

## 🎉 **WHAT YOU'LL GET:**

### **Your Live Trading Platform:**
```
Frontend: https://paiid-frontend.onrender.com
Backend:  https://paiid-backend.onrender.com

Features Live:
├─ ✅ User Authentication (JWT)
├─ ✅ Trading Dashboard
├─ ✅ Options Chain Viewer
├─ ✅ ML Trade Signals
├─ ✅ Portfolio Management
├─ ✅ News & Sentiment Analysis
├─ ✅ Backtesting Engine
├─ ✅ Real-time Market Data
├─ ✅ GitHub Monitor Dashboard
└─ ✅ Settings & Configuration
```

---

## 🔍 **VERIFICATION CHECKLIST:**

After deployment, test these:

### **1. Homepage Loads** ✅
```
Visit: https://paiid-frontend.onrender.com
Expect: PaiiD logo and login page
```

### **2. API Connection** ✅
```
Open browser console (F12)
Look for: "Connected to backend API"
No CORS errors
```

### **3. Authentication** ✅
```
Try login/signup
Token stored in localStorage
Redirects to dashboard
```

### **4. Core Features** ✅
```
Dashboard displays
Charts render
Data loads from backend
No JavaScript errors
```

### **5. Real-time Updates** ✅
```
WebSocket connects
Live price updates
Trade signals refresh
```

---

## 🚨 **TROUBLESHOOTING:**

### **Problem 1: Build Fails**

**Error**: `MODULE_NOT_FOUND`

**Solution**:
```bash
# In frontend directory:
rm -rf node_modules package-lock.json
npm install
npm run build

# If works locally, push to GitHub
git add package-lock.json
git commit -m "fix: Update dependencies"
git push
```

---

### **Problem 2: Can't Connect to Backend**

**Error**: `CORS policy` or `Network Error`

**Solution**:
1. Check backend CORS settings in `backend/app/main.py`
2. Verify `NEXT_PUBLIC_API_URL` matches backend URL exactly
3. Ensure backend is running (check Render dashboard)

**Backend CORS should include**:
```python
allow_origins=[
    "https://paiid-frontend.onrender.com",
    "http://localhost:3000",  # local dev
]
```

---

### **Problem 3: WebSocket Won't Connect**

**Error**: `WebSocket connection failed`

**Solution**:
1. Use `wss://` (not `ws://`) for production
2. Check `NEXT_PUBLIC_WS_URL` is correct
3. Verify backend WebSocket endpoint is running

---

### **Problem 4: Environment Variables Not Working**

**Symptom**: Frontend uses localhost instead of production API

**Solution**:
1. In Render dashboard → your frontend service
2. Go to "Environment" tab
3. Re-add all environment variables
4. Must start with `NEXT_PUBLIC_` to be accessible in browser
5. Click "Save Changes" (triggers redeploy)

---

### **Problem 5: Free Tier Sleeping**

**Symptom**: First load takes 30+ seconds

**This is NORMAL for free tier!**
- Free tier sleeps after 15 min inactivity
- First request wakes it up (30 sec delay)
- Subsequent requests are fast

**Solutions**:
- **Free**: Live with it (it's free!)
- **Paid ($7/mo)**: Upgrade to Starter plan (always-on)
- **Workaround**: Use UptimeRobot to ping every 10 min

---

## ⚙️ **RENDER CONFIGURATION FILES:**

### **Already Created for You:**

1. **`frontend/server.js`** ✅
   - Custom Next.js production server
   - Handles graceful shutdown
   - Environment variable logging

2. **`frontend/next.config.js`** ✅
   - Standalone output for Docker
   - Security headers configured
   - CSP with production API URLs
   - Image optimization

3. **`frontend/package.json`** ✅
   - Build scripts configured
   - All dependencies listed
   - Node 20+ required

---

## 🔄 **AUTO-DEPLOY SETUP:**

Once connected to GitHub, Render auto-deploys when you:

```bash
# Make changes
git add .
git commit -m "feat: New feature"
git push origin main

# Render detects push → Builds → Deploys (3-5 min)
```

**Watch deployment**:
```
https://dashboard.render.com → Your Service → Logs
```

---

## 🎯 **CUSTOM DOMAIN (OPTIONAL):**

Want `app.paiid.com` instead of `paiid-frontend.onrender.com`?

1. **In Render Dashboard**:
   - Go to your frontend service
   - Click "Settings"
   - Scroll to "Custom Domain"
   - Add: `app.paiid.com`

2. **In Your Domain Provider (GoDaddy, Namecheap, etc.)**:
   - Add CNAME record:
     ```
     Type:  CNAME
     Name:  app (or @)
     Value: paiid-frontend.onrender.com
     ```

3. **Wait 5-60 minutes** for DNS propagation

4. **Done!** SSL certificate auto-generated

---

## 💰 **COST BREAKDOWN:**

### **Free Tier**:
```
Cost: $0/month
Limits:
├─ Sleeps after 15 min inactivity
├─ 750 hours/month (enough for personal use)
├─ Shared resources
└─ Good for: Testing, personal projects
```

### **Starter Plan**:
```
Cost: $7/month
Benefits:
├─ Always-on (no sleeping)
├─ Dedicated resources
├─ Faster performance
├─ Custom domains included
└─ Good for: Production, real users
```

---

## 🏆 **SUCCESS CRITERIA:**

You'll know it worked when:

✅ **Frontend URL loads** (no 404)  
✅ **Login page appears** (with logo)  
✅ **Backend API connects** (no CORS errors)  
✅ **Authentication works** (can login)  
✅ **Dashboard displays** (with data)  
✅ **Charts render** (TradingView, Recharts)  
✅ **Real-time updates** (WebSocket connected)  
✅ **No console errors** (clean F12 console)  

---

## 🚀 **NEXT STEPS AFTER DEPLOYMENT:**

1. **Test Full User Journey**:
   - Sign up → Login → View Dashboard → Place Trade

2. **Share Your Live App**:
   - Add to portfolio
   - Share on LinkedIn
   - Demo for investors/employers

3. **Monitor Performance**:
   - Check Render logs
   - Watch Sentry for errors
   - Monitor GitHub Actions

4. **Iterate & Improve**:
   - Fix any bugs found
   - Add new features
   - Optimize performance

---

## 📞 **NEED HELP?**

**Render Docs**: https://render.com/docs/web-services  
**Next.js Deployment**: https://nextjs.org/docs/deployment  
**Our Backend API**: https://paiid-backend.onrender.com/docs  

---

## 🎉 **YOU'RE ABOUT TO BE LIVE!**

Once you complete Step 2 above, your full trading platform will be:

**PUBLIC** → Anyone can visit  
**FUNCTIONAL** → All features working  
**IMPRESSIVE** → Portfolio-worthy  
**FAST** → Optimized & cached  
**SECURE** → JWT auth, HTTPS, CSP headers  

**LET'S MAKE IT HAPPEN!** 🚀🔥💪

