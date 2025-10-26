# Process Management Documentation

## Overview

This document describes the process lifecycle management system implemented to prevent zombie processes in the PaiiD application. The system includes process spawning, tracking, cleanup, and zombie detection across all components.

## Architecture

### Process Management Components

1. **PowerShell ProcessManager.ps1** - Windows process lifecycle management
2. **Bash process-manager.sh** - Unix/Linux process management  
3. **Python zombie-detector.py** - Cross-platform zombie detection
4. **PowerShell zombie-killer.ps1** - Windows-specific zombie cleanup
5. **Enhanced cleanup scripts** - Port and process cleanup

### Process Lifecycle Patterns

#### 1. Process Spawning
- All processes must be spawned with proper PID tracking
- Use ProcessManager.ps1 for Windows processes
- Use process-manager.sh for Unix processes
- Never use `Start-Process` without PID tracking
- Never use `execSync` without timeout and error handling

#### 2. Process Tracking
- All spawned processes must be registered with PID files
- PID files stored in `backend/.run/` and `frontend/.run/`
- Process objects stored in memory for graceful shutdown
- Regular cleanup of orphaned PID files

#### 3. Process Termination
- Graceful shutdown first (SIGTERM/CloseMainWindow)
- Timeout-based escalation to force kill (SIGKILL)
- Process tree termination for child processes
- Cleanup of PID files and process objects

## Implementation Details

### Windows Process Management

#### ProcessManager.ps1 Functions

```powershell
# Start a managed process
$pid = Start-ManagedProcess -Name "backend-dev" -Command "uvicorn app.main:app" -WorkingDirectory "backend"

# Stop a managed process
Stop-ManagedProcess -Name "backend-dev" -Timeout 10

# Check process status
Get-ManagedProcessStatus -Name "backend-dev"

# Clean up orphaned processes
Clear-OrphanedPids

# Clear a port
Clear-Port -Port 8001 -MaxRetries 3
```

#### Key Features
- Direct process spawning (not Job objects)
- Process object tracking for graceful shutdown
- Environment variable management
- Port conflict detection and resolution
- Orphaned process cleanup

### Unix Process Management

#### process-manager.sh Functions

```bash
# Start a process
start_process "backend-server" "uvicorn app.main:app --host 0.0.0.0 --port 8001"

# Stop a process
stop_process "backend-server" 10

# Check status
status_process "backend-server"

# Clean up orphans
cleanup_orphans

# Clear port
cleanup_port 8001 3
```

#### Key Features
- PID file management
- Signal handling (SIGTERM → SIGKILL)
- Process tree termination
- Zombie process detection
- Port-based cleanup

### Zombie Detection

#### Python zombie-detector.py

```python
# Run zombie detection
python scripts/zombie-detector.py

# Detects:
# - Actual zombie processes (state 'Z')
# - Orphaned processes (no parent)
# - Port conflicts
# - Hung processes (high CPU)
```

#### PowerShell zombie-killer.ps1

```powershell
# Safe mode cleanup
.\scripts\zombie-killer.ps1 -SafeMode

# Force cleanup
.\scripts\zombie-killer.ps1 -Force

# Custom patterns
.\scripts\zombie-killer.ps1 -Patterns @("uvicorn", "npm.*dev")
```

## Process Spawning Guidelines

### ✅ Correct Patterns

#### PowerShell (Windows)
```powershell
# Use ProcessManager
$pid = Start-ManagedProcess -Name "backend" -Command "uvicorn app.main:app" -WorkingDirectory "backend"
```

#### Bash (Unix)
```bash
# Use process-manager.sh
start_process "backend" "uvicorn app.main:app --host 0.0.0.0 --port 8001"
```

#### Python
```python
# Use timeout and error handling
try:
    result = subprocess.run(
        ["git", "diff", "--name-only"],
        capture_output=True,
        text=True,
        timeout=30,
        check=True,
    )
except subprocess.TimeoutExpired:
    print("Command timed out")
except subprocess.CalledProcessError as e:
    print(f"Command failed: {e}")
```

#### TypeScript/JavaScript
```typescript
// Use async spawn with PID tracking
const { spawn } = require('child_process');
const process = spawn('uvicorn', ['app.main:app'], { stdio: 'inherit' });
// Store PID for cleanup
```

### ❌ Incorrect Patterns

#### PowerShell
```powershell
# DON'T: Start-Process without tracking
Start-Process powershell -ArgumentList "-Command", "uvicorn app.main:app"

# DON'T: Start-Job without PID tracking
Start-Job -ScriptBlock { uvicorn app.main:app }
```

#### Bash
```bash
# DON'T: Background process without tracking
uvicorn app.main:app &

# DON'T: No signal handling
uvicorn app.main:app
```

#### Python
```python
# DON'T: No timeout
subprocess.run(["git", "diff"], capture_output=True)

# DON'T: No error handling
subprocess.run(["git", "diff"], capture_output=True)
```

#### TypeScript/JavaScript
```typescript
// DON'T: execSync without timeout
execSync(`lsof -ti:${port} | xargs kill -9`, { stdio: "ignore" });

// DON'T: No PID tracking
execSync(`uvicorn app.main:app`, { stdio: "ignore" });
```

## Cleanup Procedures

### Automatic Cleanup

1. **Process Exit Handlers** - Cleanup on script exit
2. **Signal Handlers** - SIGINT/SIGTERM handling
3. **Orphaned PID Cleanup** - Regular cleanup of stale PID files
4. **Port Cleanup** - Clear ports before starting new processes

### Manual Cleanup

#### Emergency Cleanup
```powershell
# Windows emergency cleanup
.\scripts\emergency-cleanup.ps1

# Unix emergency cleanup
bash backend/scripts/cleanup.sh 8001
```

#### Development Environment
```powershell
# Stop all development processes
.\scripts\stop-dev.ps1

# Stop with force cleanup
.\scripts\stop-dev.ps1 -Force
```

#### Zombie Detection
```bash
# Run zombie detection
python scripts/zombie-detector.py

# Windows zombie cleanup
.\scripts\zombie-killer.ps1 -SafeMode
```

## Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the port
netstat -ano | findstr :8001
lsof -i:8001

# Kill processes on port
.\scripts\stop-dev.ps1 -Force
```

#### 2. Zombie Processes
```bash
# Detect zombies
python scripts/zombie-detector.py

# Clean zombies
.\scripts\zombie-killer.ps1 -Force
```

#### 3. Orphaned PID Files
```bash
# Clean orphaned PIDs
Clear-OrphanedPids  # PowerShell
cleanup_orphans     # Bash
```

#### 4. Hung Processes
```bash
# Check for hung processes
python scripts/zombie-detector.py

# Force kill hung processes
.\scripts\zombie-killer.ps1 -Force
```

### Debugging Commands

#### Check Process Status
```powershell
# PowerShell
Get-ManagedProcessStatus -Name "backend-dev"

# Bash
status_process "backend-server"
```

#### Check Port Usage
```bash
# Windows
netstat -ano | findstr :8001

# Unix
lsof -i:8001
```

#### Check PID Files
```bash
# List PID files
ls backend/.run/*.pid
ls frontend/.run/*.pid

# Check PID file contents
cat backend/.run/backend-server.pid
```

## Integration with CI/CD

### Pre-commit Hooks
```bash
# Add to .git/hooks/pre-commit
python scripts/zombie-detector.py
if [ $? -ne 0 ]; then
    echo "Zombie processes detected, aborting commit"
    exit 1
fi
```

### GitHub Actions
```yaml
- name: Check for zombie processes
  run: python scripts/zombie-detector.py
```

## Best Practices

### 1. Always Use Process Managers
- Never spawn processes directly
- Always register PIDs
- Always implement cleanup handlers

### 2. Implement Timeouts
- All subprocess calls must have timeouts
- Graceful shutdown with timeout escalation
- Force kill after timeout

### 3. Handle Signals Properly
- SIGINT/SIGTERM → graceful shutdown
- SIGKILL → force kill
- Forward signals to child processes

### 4. Clean Up Resources
- Remove PID files on exit
- Close file handles
- Clean up process objects

### 5. Monitor for Zombies
- Regular zombie detection
- Automated cleanup
- Alert on zombie detection

## File Locations

### Process Management Scripts
- `scripts/ProcessManager.ps1` - Windows process manager
- `backend/scripts/process-manager.sh` - Unix process manager
- `scripts/zombie-detector.py` - Zombie detection
- `scripts/zombie-killer.ps1` - Windows zombie cleanup
- `scripts/stop-dev.ps1` - Development environment stop
- `scripts/stop-all.ps1` - Stop all managed processes

### PID Files
- `backend/.run/` - Backend process PID files
- `frontend/.run/` - Frontend process PID files

### Logs
- `backend/.logs/` - Process management logs
- `scripts/zombie-detection-results.json` - Zombie detection results

## Conclusion

This process management system provides comprehensive zombie process prevention through proper process lifecycle management, automated cleanup, and zombie detection. Following these patterns ensures reliable process management across all components of the PaiiD application.
