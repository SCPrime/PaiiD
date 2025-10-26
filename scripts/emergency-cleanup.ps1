# Emergency Zombie Process Killer
# Nuclear option for stubborn processes that won't die
# Version: 1.0.0

param(
    [Parameter(Mandatory=$false)]
    [int]$Port = 8001,

    [Parameter(Mandatory=$false)]
    [switch]$Force = $false,

    [Parameter(Mandatory=$false)]
    [switch]$KillAllPython = $false,

    [Parameter(Mandatory=$false)]
    [switch]$WhatIf = $false
)

$ErrorActionPreference = "Continue"

# Import ProcessManager module if available
$ProcessManagerPath = Join-Path $PSScriptRoot "ProcessManager.ps1"
if (Test-Path $ProcessManagerPath) {
    Import-Module $ProcessManagerPath -Force -ErrorAction SilentlyContinue
}

Write-Host "======================================" -ForegroundColor Red
Write-Host "EMERGENCY ZOMBIE PROCESS KILLER" -ForegroundColor Red
Write-Host "======================================" -ForegroundColor Red
Write-Host ""
Write-Host "Target Port: $Port" -ForegroundColor Yellow
Write-Host "Force Mode: $Force" -ForegroundColor $(if ($Force) { "Red" } else { "Green" })
Write-Host "Kill All Python: $KillAllPython" -ForegroundColor $(if ($KillAllPython) { "Red" } else { "Green" })
Write-Host "What-If Mode: $WhatIf" -ForegroundColor $(if ($WhatIf) { "Yellow" } else { "Green" })
Write-Host ""

if ($WhatIf) {
    Write-Host "Running in WHAT-IF mode - no processes will be killed" -ForegroundColor Cyan
    Write-Host ""
}

# Function to log with timestamp
function Write-EmergencyLog {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Level) {
        "ERROR" { "Red" }
        "WARN"  { "Yellow" }
        "SUCCESS" { "Green" }
        default { "White" }
    }

    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $color
}

# Phase 1: Kill processes on specific port
function Kill-ProcessesOnPort {
    param([int]$TargetPort)

    Write-EmergencyLog "Phase 1: Killing processes on port $TargetPort" "WARN"

    # Get all PIDs on the port
    $connections = Get-NetTCPConnection -LocalPort $TargetPort -ErrorAction SilentlyContinue

    if (-not $connections) {
        Write-EmergencyLog "No processes found on port $TargetPort" "SUCCESS"
        return $true
    }

    $pids = $connections | ForEach-Object { $_.OwningProcess } | Select-Object -Unique
    $pidCount = $pids.Count
    $pidList = $pids -join ', '
    Write-EmergencyLog "Found $pidCount unique PID(s) on port $TargetPort`: $pidList" "WARN"

    foreach ($processId in $pids) {
        try {
            $process = Get-Process -Id $processId -ErrorAction SilentlyContinue

            if ($process) {
                $processName = $process.ProcessName
                $commandLine = (Get-CimInstance Win32_Process -Filter "ProcessId = $processId").CommandLine

                Write-EmergencyLog "Targeting PID $processId ($processName)" "WARN"
                Write-EmergencyLog "  Command: $commandLine" "INFO"

                if (-not $WhatIf) {
                    # Try graceful close first
                    Write-EmergencyLog "  Attempting graceful close..." "INFO"
                    $process.CloseMainWindow() | Out-Null
                    Start-Sleep -Seconds 2

                    # Check if still running
                    if (Get-Process -Id $processId -ErrorAction SilentlyContinue) {
                        Write-EmergencyLog "  Escalating to taskkill /F..." "WARN"
                        taskkill /F /PID $processId /T 2>&1 | Out-Null

                        Start-Sleep -Seconds 1

                        # Final check
                        if (Get-Process -Id $processId -ErrorAction SilentlyContinue) {
                            Write-EmergencyLog "  FAILED to kill PID $processId (stubborn zombie)" "ERROR"
                        } else {
                            Write-EmergencyLog "  Successfully killed PID $processId" "SUCCESS"
                        }
                    } else {
                        Write-EmergencyLog "  Gracefully closed PID $processId" "SUCCESS"
                    }
                }
            }
        }
        catch {
            Write-EmergencyLog "  Error processing PID $processId : $_" "ERROR"
        }
    }

    # Wait for sockets to release
    Write-EmergencyLog "Waiting 5 seconds for sockets to release..." "INFO"
    Start-Sleep -Seconds 5

    # Verify port is free
    $stillInUse = Get-NetTCPConnection -LocalPort $TargetPort -ErrorAction SilentlyContinue
    if ($stillInUse) {
        Write-EmergencyLog "Port $TargetPort is STILL in use after cleanup!" "ERROR"
        return $false
    } else {
        Write-EmergencyLog "Port $TargetPort is now FREE" "SUCCESS"
        return $true
    }
}

# Phase 2: Kill orphaned uvicorn processes and PowerShell zombies
function Kill-OrphanedUvicornProcesses {
    Write-EmergencyLog "Phase 2: Killing orphaned uvicorn processes and PowerShell zombies" "WARN"

    # Kill orphaned uvicorn processes
    $uvicornProcesses = Get-CimInstance Win32_Process | Where-Object {
        $_.CommandLine -like "*uvicorn*" -and $_.Name -eq "python.exe"
    }

    if ($uvicornProcesses) {
        Write-EmergencyLog "Found $($uvicornProcesses.Count) uvicorn process(es)" "WARN"

        foreach ($proc in $uvicornProcesses) {
            $processId = $proc.ProcessId
            $commandLine = $proc.CommandLine

            Write-EmergencyLog "Orphaned uvicorn PID $processId" "WARN"
            Write-EmergencyLog "  Command: $commandLine" "INFO"

            if (-not $WhatIf) {
                try {
                    Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
                    Write-EmergencyLog "  Killed PID $processId" "SUCCESS"
                }
                catch {
                    Write-EmergencyLog "  Failed to kill PID $processId : $_" "ERROR"
                }
            }
        }
    } else {
        Write-EmergencyLog "No orphaned uvicorn processes found" "SUCCESS"
    }

    # Kill orphaned PowerShell processes running our commands
    Write-EmergencyLog "Checking for orphaned PowerShell processes..." "INFO"
    
    $powershellProcesses = Get-CimInstance Win32_Process | Where-Object {
        $_.Name -eq "powershell.exe" -and (
            $_.CommandLine -like "*uvicorn*" -or
            $_.CommandLine -like "*npm*dev*" -or
            $_.CommandLine -like "*next*dev*" -or
            $_.CommandLine -like "*paiid*"
        )
    }

    if ($powershellProcesses) {
        Write-EmergencyLog "Found $($powershellProcesses.Count) orphaned PowerShell process(es)" "WARN"

        foreach ($proc in $powershellProcesses) {
            $processId = $proc.ProcessId
            $commandLine = $proc.CommandLine

            Write-EmergencyLog "Orphaned PowerShell PID $processId" "WARN"
            Write-EmergencyLog "  Command: $commandLine" "INFO"

            if (-not $WhatIf) {
                try {
                    Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
                    Write-EmergencyLog "  Killed PID $processId" "SUCCESS"
                }
                catch {
                    Write-EmergencyLog "  Failed to kill PID $processId : $_" "ERROR"
                }
            }
        }
    } else {
        Write-EmergencyLog "No orphaned PowerShell processes found" "SUCCESS"
    }
}

# Phase 3: Kill ALL Python processes (nuclear option)
function Kill-AllPythonProcesses {
    if (-not $KillAllPython) {
        return
    }

    Write-EmergencyLog "Phase 3: NUCLEAR - Killing ALL Python processes" "ERROR"
    Write-Host ""
    Write-Host "WARNING: This will kill ALL python.exe processes on your system!" -ForegroundColor Red

    if (-not $Force) {
        Write-Host "Use -Force to confirm this action" -ForegroundColor Yellow
        return
    }

    if ($WhatIf) {
        Write-Host "Would kill all Python processes (What-If mode)" -ForegroundColor Yellow
        return
    }

    Write-Host "Proceeding in 3 seconds... (Ctrl+C to abort)" -ForegroundColor Red
    Start-Sleep -Seconds 3

    $pythonProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue

    if (-not $pythonProcesses) {
        Write-EmergencyLog "No Python processes found" "SUCCESS"
        return
    }

    Write-EmergencyLog "Found $($pythonProcesses.Count) Python process(es)" "WARN"

    foreach ($proc in $pythonProcesses) {
        try {
            $processId = $proc.Id
            Write-EmergencyLog "Killing Python PID $processId" "WARN"
            Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
            Write-EmergencyLog "  Killed PID $processId" "SUCCESS"
        }
        catch {
            Write-EmergencyLog "  Failed to kill PID $processId : $_" "ERROR"
        }
    }
}

# Phase 4: Clean up TIME_WAIT sockets
function Clear-TimeWaitSockets {
    param([int]$TargetPort)

    Write-EmergencyLog "Phase 4: Checking for TIME_WAIT sockets on port $TargetPort" "INFO"

    $timeWaitConnections = Get-NetTCPConnection -LocalPort $TargetPort -State TimeWait -ErrorAction SilentlyContinue

    if (-not $timeWaitConnections) {
        Write-EmergencyLog "No TIME_WAIT sockets on port $TargetPort" "SUCCESS"
        return
    }

    Write-EmergencyLog "Found $($timeWaitConnections.Count) TIME_WAIT socket(s)" "WARN"
    Write-EmergencyLog "These will expire automatically in 30-120 seconds" "INFO"

    if ($Force) {
        Write-EmergencyLog "Attempting to clear TIME_WAIT sockets (requires admin)..." "WARN"

        if (-not $WhatIf) {
            try {
                # This requires admin privileges
                netsh int ipv4 set dynamicport tcp start=49152 num=16384 | Out-Null
                Write-EmergencyLog "Reset dynamic port range - TIME_WAIT sockets may clear faster" "SUCCESS"
            }
            catch {
                Write-EmergencyLog "Failed to reset port range (may need admin rights): $_" "ERROR"
            }
        }
    }
}

# Phase 5: Clean up Job Objects and PowerShell Jobs
function Clear-JobObjects {
    Write-EmergencyLog "Phase 5: Cleaning up Job Objects and PowerShell Jobs" "INFO"

    # Get all PowerShell jobs
    $jobs = Get-Job -ErrorAction SilentlyContinue
    
    if ($jobs) {
        Write-EmergencyLog "Found $($jobs.Count) PowerShell job(s)" "WARN"
        
        foreach ($job in $jobs) {
            $jobId = $job.Id
            $jobName = $job.Name
            $jobState = $job.State
            
            Write-EmergencyLog "Job $jobId ($jobName): $jobState" "INFO"
            
            if (-not $WhatIf) {
                try {
                    Remove-Job -Id $jobId -Force -ErrorAction SilentlyContinue
                    Write-EmergencyLog "  Removed job $jobId" "SUCCESS"
                }
                catch {
                    Write-EmergencyLog "  Failed to remove job $jobId : $_" "ERROR"
                }
            }
        }
    } else {
        Write-EmergencyLog "No PowerShell jobs found" "SUCCESS"
    }

    # Check for orphaned Job Objects using WMI
    try {
        $jobObjects = Get-CimInstance Win32_Job -ErrorAction SilentlyContinue
        
        if ($jobObjects) {
            Write-EmergencyLog "Found $($jobObjects.Count) Job Object(s)" "WARN"
            
            foreach ($job in $jobObjects) {
                $jobName = $job.Name
                $jobProcesses = $job.Processes
                
                Write-EmergencyLog "Job Object: $jobName (Processes: $jobProcesses)" "INFO"
                
                if (-not $WhatIf) {
                    try {
                        $job.Terminate()
                        Write-EmergencyLog "  Terminated Job Object: $jobName" "SUCCESS"
                    }
                    catch {
                        Write-EmergencyLog "  Failed to terminate Job Object $jobName : $_" "ERROR"
                    }
                }
            }
        } else {
            Write-EmergencyLog "No Job Objects found" "SUCCESS"
        }
    }
    catch {
        Write-EmergencyLog "Could not query Job Objects: $_" "WARN"
    }
}

# Phase 6: Clean up PID files
function Clear-OrphanedPidFiles {
    Write-EmergencyLog "Phase 6: Cleaning up orphaned PID files" "INFO"

    $projectRoot = Split-Path $PSScriptRoot -Parent
    $pidDirs = @(
        Join-Path $projectRoot "backend\.run",
        Join-Path $projectRoot "frontend\.run"
    )

    $totalCleaned = 0

    foreach ($pidDir in $pidDirs) {
        if (-not (Test-Path $pidDir)) {
            Write-EmergencyLog "PID directory not found: $pidDir" "INFO"
            continue
        }

        $pidFiles = Get-ChildItem -Path $pidDir -Filter "*.pid" -ErrorAction SilentlyContinue

        if (-not $pidFiles) {
            Write-EmergencyLog "No PID files found in $pidDir" "SUCCESS"
            continue
        }

        Write-EmergencyLog "Found $($pidFiles.Count) PID file(s) in $pidDir" "INFO"

        foreach ($pidFile in $pidFiles) {
            $processId = Get-Content $pidFile.FullName -Raw -ErrorAction SilentlyContinue

            if ($processId) {
                $processId = $processId.Trim()
                $processExists = Get-Process -Id $processId -ErrorAction SilentlyContinue

                if (-not $processExists) {
                    Write-EmergencyLog "Orphaned PID file: $($pidFile.Name) (PID $processId no longer running)" "WARN"

                    if (-not $WhatIf) {
                        Remove-Item $pidFile.FullName -Force
                        Write-EmergencyLog "  Removed $($pidFile.Name)" "SUCCESS"
                        $totalCleaned++
                    }
                } else {
                    Write-EmergencyLog "Active PID file: $($pidFile.Name) (PID $processId is running)" "INFO"
                }
            }
        }
    }

    if ($totalCleaned -gt 0) {
        Write-EmergencyLog "Cleaned up $totalCleaned orphaned PID file(s)" "SUCCESS"
    }
}

# Main execution
function Main {
    Write-EmergencyLog "Starting emergency cleanup..." "WARN"
    Write-Host ""

    # Phase 1: Kill processes on port
    $portCleared = Kill-ProcessesOnPort -TargetPort $Port

    # Phase 2: Kill orphaned uvicorn
    Kill-OrphanedUvicornProcesses

    # Phase 3: Nuclear option (if enabled)
    Kill-AllPythonProcesses

    # Phase 4: TIME_WAIT cleanup
    Clear-TimeWaitSockets -TargetPort $Port

    # Phase 5: Job Object cleanup
    Clear-JobObjects

    # Phase 6: PID file cleanup
    Clear-OrphanedPidFiles

    Write-Host ""
    Write-Host "======================================" -ForegroundColor $(if ($portCleared) { "Green" } else { "Red" })

    if ($portCleared) {
        Write-EmergencyLog "EMERGENCY CLEANUP SUCCESSFUL" "SUCCESS"
        Write-Host "Port $Port is now free and ready for use" -ForegroundColor Green
    } else {
        Write-EmergencyLog "EMERGENCY CLEANUP INCOMPLETE" "ERROR"
        Write-Host "Port $Port is still occupied - consider these options:" -ForegroundColor Red
        Write-Host "  1. Run with -Force flag for more aggressive cleanup" -ForegroundColor Yellow
        Write-Host "  2. Run with -KillAllPython -Force to kill all Python processes" -ForegroundColor Yellow
        Write-Host "  3. Restart Windows to release all socket handles" -ForegroundColor Yellow
        Write-Host "  4. Use alternate port: `$env:PORT=8002; npm run dev" -ForegroundColor Yellow
    }

    Write-Host "======================================" -ForegroundColor $(if ($portCleared) { "Green" } else { "Red" })
    Write-Host ""

    # Exit code
    if ($portCleared) {
        exit 0
    } else {
        exit 1
    }
}

# Run main
Main
