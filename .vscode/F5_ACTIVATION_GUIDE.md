# 🎮 F5 Debugging Activation Guide for PaiiD

## ✅ Prerequisites Installed
- ✅ Chrome Debugger: `msjsdiag.debugger-for-chrome`
- ✅ Edge DevTools: `ms-edgedevtools.vscode-edge-devtools`
- ✅ Python Debugger: `ms-python.debugpy`
- ✅ Launch config: `.vscode/launch.json` created

---

## 🎯 How to Activate F5 Debugging

### Method 1: Using the Debug Panel (RECOMMENDED for first time)

1. **Open Debug Panel**:
   - Click the 🐛 icon in the left sidebar (looks like a bug with a play button)
   - OR press `Ctrl+Shift+D`

2. **You should see**:
   ```
   RUN AND DEBUG
   ┌─────────────────────────────────────┐
   │ 🌐 Launch Chrome - Local Dev    ▼ │ ← Dropdown
   └─────────────────────────────────────┘

   ▶  [Green Play Button]
   ```

3. **Select a configuration** from the dropdown:
   - `🌐 Launch Chrome - Local Dev` - Opens Chrome to localhost:3000
   - `🔷 Launch Edge - Local Dev` - Opens Edge to localhost:3000
   - `🐍 Python: Backend (Uvicorn)` - Starts backend server
   - `🎯 Full Stack Debug` - Starts BOTH backend + frontend

4. **Click the green play button** OR **press F5**

---

### Method 2: Using F5 Directly

1. **Make sure a file is open** (any .tsx, .py, .ts file)
2. **Press F5**
3. **If prompted**, select a debug configuration from the list
4. **Browser/terminal should launch**

---

## 🧪 Test Right Now

### Test 1: Python Backend Debugging

1. Open any Python file (e.g., `backend/app/main.py`)
2. Press `Ctrl+Shift+D` to open Debug panel
3. Select `🐍 Python: Backend (Uvicorn)` from dropdown
4. Press F5

**Expected Result**:
```
Terminal opens showing:
INFO:     Uvicorn running on http://127.0.0.1:8001
INFO:     Application startup complete
```

### Test 2: Chrome Browser Debugging

**IMPORTANT**: Frontend must be running first!

1. In terminal: `cd frontend && npm run dev`
2. Wait for "Ready on http://localhost:3000"
3. Press `Ctrl+Shift+D`
4. Select `🌐 Launch Chrome - Local Dev`
5. Press F5

**Expected Result**:
- New Chrome window opens
- Navigates to localhost:3000
- PaiiD dashboard loads
- Debug toolbar appears in VS Code:
  ```
  ⏸ Continue | ⏭ Step Over | ⏬ Step Into | ⏫ Step Out | 🔄 Restart | ⏹ Stop
  ```

---

## 🔍 Troubleshooting

### Problem: "F5 does nothing"

**Solution 1**: Open the Debug panel first
```
Ctrl+Shift+D → Select configuration → Press F5
```

**Solution 2**: Make sure you're in the correct workspace
```
File → Open Folder → Navigate to C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD
```

**Solution 3**: Reload VS Code window
```
Ctrl+Shift+P → Type "Reload Window" → Press Enter
```

---

### Problem: "Cannot connect to runtime process"

**For Chrome/Edge debugging**:
- **Cause**: Frontend dev server not running
- **Fix**:
  ```bash
  cd frontend
  npm run dev
  # Wait for "Ready on http://localhost:3000"
  # THEN press F5
  ```

**For Python debugging**:
- **Cause**: Port 8001 already in use
- **Fix**:
  ```bash
  # Kill existing process
  taskkill /F /IM python.exe
  # Then press F5 again
  ```

---

### Problem: "No configurations" in dropdown

**Fix**: Verify launch.json exists
```bash
cat .vscode/launch.json
```

If missing, the file is at: `.vscode/launch.json` (already created)

---

## 🎨 Visual Indicators That F5 Worked

### When debugging is ACTIVE, you'll see:

1. **Debug Toolbar** (floating at top of VS Code):
   ```
   ⏸️ ⏭️ ⏬ ⏫ 🔄 ⏹️
   ```

2. **Debug Console** tab (bottom panel):
   ```
   DEBUG CONSOLE  |  PROBLEMS  |  OUTPUT  |  TERMINAL
   ^^^^^^^^^^^^^^^^ (becomes active)
   ```

3. **Variables panel** (left sidebar shows):
   ```
   VARIABLES
   ├─ Local
   ├─ Global
   └─ Closure
   ```

4. **Call Stack** (left sidebar shows):
   ```
   CALL STACK
   └─ main.py:42
   ```

5. **Browser/Terminal launches** (you'll see the window open)

---

## 🚀 Quick Start Commands

### Start Full Stack Debugging (Recommended):

1. Press `Ctrl+Shift+D`
2. Select `🎯 Full Stack Debug (Chrome + Backend)`
3. Press F5

**This starts**:
- Backend on http://localhost:8001
- Frontend dev server (if not running, start it first)
- Chrome browser with debugging enabled

---

## 📸 Screenshot Locations (What to Look For)

### Debug Panel Location:
```
VS Code Window
├─ Left Sidebar
│  ├─ 📁 Explorer
│  ├─ 🔍 Search
│  ├─ 🌿 Source Control
│  ├─ 🐛 Run and Debug  ← CLICK HERE
│  └─ 🧩 Extensions
```

### Debug Toolbar Location:
```
┌─────────────────────────────────────────────┐
│ File Edit Selection View ...                │
├─────────────────────────────────────────────┤
│  ⏸️ ⏭️ ⏬ ⏫ 🔄 ⏹️   ← Floating toolbar here
│                                              │
│  [Your code editor]                          │
└─────────────────────────────────────────────┘
```

---

## 🎯 Current Available Configurations

You have 6 debug configurations + 2 compound configs:

### Single Configurations:
1. `🌐 Launch Chrome - Local Dev` - Debug frontend in Chrome
2. `🔷 Launch Edge - Local Dev` - Debug frontend in Edge
3. `🔗 Attach to Chrome (Port 9222)` - Attach to running Chrome
4. `🚀 Debug Production (Render)` - Debug production site
5. `🐍 Python: Backend (Uvicorn)` - Debug backend API
6. `🧪 Python: Run Tests` - Debug pytest tests

### Compound Configurations (Start Multiple):
7. `🎯 Full Stack Debug (Chrome + Backend)` - Both at once!
8. `🎯 Full Stack Debug (Edge + Backend)` - Both with Edge!

---

## 💡 Pro Tips

### Set Breakpoints:
1. Open any .ts/.tsx/.py file
2. Click in the **gutter** (left of line numbers)
3. Red dot appears = breakpoint set
4. Press F5 - code will pause at that line!

### View Console Output:
- `Ctrl+Shift+Y` - Opens Debug Console
- Shows all console.log() and print() statements
- Shows network requests (with Console Ninja extension)

### Hot Reload While Debugging:
- Edit code while debugging
- Changes auto-reload (frontend with Next.js, backend with --reload)
- No need to restart F5!

---

## ✅ Success Checklist

After pressing F5, verify you see:

- [ ] Debug toolbar appeared at top
- [ ] Debug Console tab is active (bottom panel)
- [ ] Variables panel shows on left sidebar
- [ ] Browser window opened (for Chrome/Edge configs)
- [ ] OR Terminal opened (for Python configs)
- [ ] Status bar (bottom) says "Debugging" or shows a debug indicator

If you see ALL of these → **F5 is working!** 🎉

---

## 🆘 Still Not Working?

**Share a screenshot of**:
1. Your VS Code window with Debug panel open
2. What happens when you press F5
3. Any error messages in the Output panel

**Then I can help troubleshoot specifically!**

---

**Created**: 2025-10-25
**Last Updated**: 2025-10-25
**Status**: Ready to test F5 debugging
