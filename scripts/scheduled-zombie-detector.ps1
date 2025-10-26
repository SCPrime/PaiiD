# Scheduled Zombie Process Detector
# Runs as a scheduled task to detect and report zombie processes
# Version: 1.0.0

param(
    [switch]$AutoCleanup = $false,
    [string]$LogFile = "zombie-detection.log"
)

# Configuration
$ProjectRoot = Split-Path $PSScriptRoot -Parent
$LogPath = Join-Path $ProjectRoot "backend\.logs"
$LogFile = Join-Path $LogPath $LogFile

# Ensure log directory exists
if (-not (Test-Path $LogPath)) {
    New-Item -ItemType Directory -Path $LogPath -Force | Out-Null
}

# Logging function
function Write-ZombieLog {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $logMessage = "[$timestamp] [$Level] $Message"
    
    # Write to console
    switch ($Level) {
        'ERROR' { Write-Host $logMessage -ForegroundColor Red }
        'WARN'  { Write-Host $logMessage -ForegroundColor Yellow }
        'SUCCESS' { Write-Host $logMessage -ForegroundColor Green }
        default { Write-Host $logMessage -ForegroundColor Gray }
    }
    
    # Write to log file
    Add-Content -Path $LogFile -Value $logMessage
}

# Import ProcessManager if available
$ProcessManagerPath = Join-Path $PSScriptRoot "ProcessManager.ps1"
if (Test-Path $ProcessManagerPath) {
    try {
        Import-Module $ProcessManagerPath -Force -ErrorAction SilentlyContinue
    }
    catch {
        Write-ZombieLog "Could not import ProcessManager: $_" "WARN"
    }
}

Write-ZombieLog "Starting scheduled zombie detection scan"

# Check for zombie processes on common ports
$CommonPorts = @(3000, 8001, 8002, 5432)
$ZombieCount = 0
$ZombieDetails = @()

foreach ($Port in $CommonPorts) {
    try {
        $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        
        if ($connections) {
            foreach ($connection in $connections) {
                $pid = $connection.OwningProcess
                $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
                
                if (-not $process) {
                    $ZombieCount++
                    $ZombieDetails += "Port $Port: Zombie PID $pid (process not found)"
                    Write-ZombieLog "Zombie detected on port $Port: PID $pid" "WARN"
                }
            }
        }
    }
    catch {
        Write-ZombieLog "Error checking port $Port: $_" "ERROR"
    }
}

# Check for orphaned uvicorn processes
try {
    $uvicornProcesses = Get-CimInstance Win32_Process | Where-Object {
        $_.CommandLine -like "*uvicorn*" -and $_.Name -eq "python.exe"
    }
    
    foreach ($proc in $uvicornProcesses) {
        $pid = $proc.ProcessId
        $commandLine = $proc.CommandLine
        
        # Check if process is actually running
        $runningProcess = Get-Process -Id $pid -ErrorAction SilentlyContinue
        if (-not $runningProcess) {
            $ZombieCount++
            $ZombieDetails += "Uvicorn: Zombie PID $pid - $commandLine"
            Write-ZombieLog "Orphaned uvicorn process: PID $pid" "WARN"
        }
    }
}
catch {
    Write-ZombieLog "Error checking uvicorn processes: $_" "ERROR"
}

# Check for orphaned Node.js processes
try {
    $nodeProcesses = Get-CimInstance Win32_Process | Where-Object {
        $_.Name -eq "node.exe" -and (
            $_.CommandLine -like "*next*dev*" -or
            $_.CommandLine -like "*npm*dev*"
        )
    }
    
    foreach ($proc in $nodeProcesses) {
        $pid = $proc.ProcessId
        $commandLine = $proc.CommandLine
        
        # Check if process is actually running
        $runningProcess = Get-Process -Id $pid -ErrorAction SilentlyContinue
        if (-not $runningProcess) {
            $ZombieCount++
            $ZombieDetails += "Node.js: Zombie PID $pid - $commandLine"
            Write-ZombieLog "Orphaned Node.js process: PID $pid" "WARN"
        }
    }
}
catch {
    Write-ZombieLog "Error checking Node.js processes: $_" "ERROR"
}

# Summary
if ($ZombieCount -eq 0) {
    Write-ZombieLog "No zombie processes detected" "SUCCESS"
    exit 0
} else {
    Write-ZombieLog "Detected $ZombieCount zombie process(es):" "WARN"
    foreach ($detail in $ZombieDetails) {
        Write-ZombieLog "  $detail" "WARN"
    }
    
    # Auto-cleanup if requested
    if ($AutoCleanup) {
        Write-ZombieLog "Running automatic cleanup..." "WARN"
        
        $zombieKillerPath = Join-Path $PSScriptRoot "zombie-killer.ps1"
        if (Test-Path $zombieKillerPath) {
            try {
                & $zombieKillerPath -Force
                Write-ZombieLog "Automatic cleanup completed" "SUCCESS"
            }
            catch {
                Write-ZombieLog "Automatic cleanup failed: $_" "ERROR"
            }
        } else {
            Write-ZombieLog "Zombie killer not found at $zombieKillerPath" "ERROR"
        }
    }
    
    exit 1
}
