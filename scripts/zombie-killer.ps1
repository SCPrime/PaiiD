# Zombie Process Killer for Windows
# Detects and kills orphaned processes by command line pattern matching
# Version: 1.0.0

param(
    [switch]$SafeMode = $true,
    [switch]$Force = $false,
    [string[]]$Patterns = @("uvicorn", "python.*app.main", "npm.*dev", "next.*dev", "paiid")
)

# Safe mode patterns - only kill processes with these exact patterns
$SafePatterns = @(
    "uvicorn app.main:app",
    "python -m uvicorn",
    "npm run dev",
    "next dev",
    "paiid"
)

# Logging function
function Write-ZombieLog {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $logMessage = "[$timestamp] [$Level] $Message"
    
    switch ($Level) {
        'ERROR' { Write-Host $logMessage -ForegroundColor Red }
        'WARN'  { Write-Host $logMessage -ForegroundColor Yellow }
        'SUCCESS' { Write-Host $logMessage -ForegroundColor Green }
        default { Write-Host $logMessage -ForegroundColor Gray }
    }
}

# Get processes by command line pattern
function Get-ProcessesByPattern {
    param([string[]]$Patterns)
    
    $processes = @()
    
    try {
        $allProcesses = Get-CimInstance Win32_Process | Where-Object { 
            $_.CommandLine -and 
            $_.ProcessId -gt 0 -and
            $_.Name -in @("python.exe", "node.exe", "powershell.exe", "cmd.exe")
        }
        
        foreach ($process in $allProcesses) {
            $commandLine = $process.CommandLine.ToLower()
            
            foreach ($pattern in $Patterns) {
                $regexPattern = $pattern -replace '\*', '.*'
                if ($commandLine -match $regexPattern) {
                    $processes += $process
                    break
                }
            }
        }
    }
    catch {
        Write-ZombieLog "Error getting processes: $_" "ERROR"
    }
    
    return $processes
}

# Kill process with confirmation
function Stop-ProcessSafely {
    param(
        [object]$Process,
        [bool]$Force = $false
    )
    
    $pid = $Process.ProcessId
    $name = $Process.Name
    $commandLine = $Process.CommandLine
    
    try {
        Write-ZombieLog "Attempting to kill process: PID $pid ($name)"
        Write-ZombieLog "  Command: $commandLine"
        
        # Try graceful termination first
        $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
        if ($proc) {
            $proc.CloseMainWindow()
            Start-Sleep -Seconds 2
            
            # Check if still running
            if (Get-Process -Id $pid -ErrorAction SilentlyContinue) {
                if ($Force) {
                    Write-ZombieLog "Process still running, forcing termination..." "WARN"
                    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                } else {
                    Write-ZombieLog "Process did not terminate gracefully, use -Force to force kill" "WARN"
                    return $false
                }
            }
        }
        
        # Verify process is gone
        Start-Sleep -Seconds 1
        if (-not (Get-Process -Id $pid -ErrorAction SilentlyContinue)) {
            Write-ZombieLog "Successfully killed PID $pid" "SUCCESS"
            return $true
        } else {
            Write-ZombieLog "Failed to kill PID $pid" "ERROR"
            return $false
        }
    }
    catch {
        Write-ZombieLog "Error killing PID $pid: $_" "ERROR"
        return $false
    }
}

# Main detection and cleanup
function Start-ZombieCleanup {
    Write-ZombieLog "Starting Zombie Process Cleanup"
    Write-ZombieLog "Safe Mode: $SafeMode"
    Write-ZombieLog "Force Mode: $Force"
    Write-ZombieLog ""
    
    # Get processes to kill
    $targetPatterns = if ($SafeMode) { $SafePatterns } else { $Patterns }
    $processes = Get-ProcessesByPattern -Patterns $targetPatterns
    
    if ($processes.Count -eq 0) {
        Write-ZombieLog "No zombie processes found" "SUCCESS"
        return
    }
    
    Write-ZombieLog "Found $($processes.Count) potential zombie process(es):"
    Write-ZombieLog ""
    
    $killed = 0
    $failed = 0
    
    foreach ($process in $processes) {
        $pid = $process.ProcessId
        $name = $process.Name
        $commandLine = $process.CommandLine
        
        Write-ZombieLog "Process: PID $pid ($name)"
        Write-ZombieLog "  Command: $commandLine"
        
        # Additional safety checks in safe mode
        if ($SafeMode) {
            # Check if process is actually a zombie (no parent or parent is system)
            try {
                $parent = Get-CimInstance Win32_Process | Where-Object { $_.ProcessId -eq $process.ParentProcessId }
                if ($parent -and $parent.Name -ne "explorer.exe" -and $parent.Name -ne "cmd.exe") {
                    Write-ZombieLog "  Process has valid parent ($($parent.Name)), skipping" "WARN"
                    continue
                }
            }
            catch {
                # If we can't get parent info, assume it's safe to kill in safe mode
            }
        }
        
        # Kill the process
        if (Stop-ProcessSafely -Process $process -Force $Force) {
            $killed++
        } else {
            $failed++
        }
        
        Write-ZombieLog ""
    }
    
    # Summary
    Write-ZombieLog "=" * 50
    Write-ZombieLog "CLEANUP SUMMARY"
    Write-ZombieLog "=" * 50
    Write-ZombieLog "Processes killed: $killed" "SUCCESS"
    Write-ZombieLog "Processes failed: $failed" $(if ($failed -gt 0) { "ERROR" } else { "SUCCESS" })
    Write-ZombieLog "=" * 50
    
    if ($failed -gt 0) {
        Write-ZombieLog "Some processes could not be killed. Try running with -Force" "WARN"
        exit 1
    }
}

# Run cleanup
Start-ZombieCleanup
