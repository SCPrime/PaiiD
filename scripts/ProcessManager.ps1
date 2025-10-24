# PowerShell Process Manager Module
# Windows-native process lifecycle management with Job Objects
# Version: 1.0.0

$script:ProcessManagerConfig = @{
    PidDir = Join-Path $PSScriptRoot "..backend.run"
    LogDir = Join-Path $PSScriptRoot "..backend.logs"
    DefaultTimeout = 10
}

# Ensure directories exist
function Initialize-ProcessManager {
    if (-not (Test-Path $script:ProcessManagerConfig.PidDir)) {
        New-Item -ItemType Directory -Path $script:ProcessManagerConfig.PidDir -Force | Out-Null
    }
    if (-not (Test-Path $script:ProcessManagerConfig.LogDir)) {
        New-Item -ItemType Directory -Path $script:ProcessManagerConfig.LogDir -Force | Out-Null
    }
}

# Logging functions
function Write-ProcessLog {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Message,

        [Parameter(Mandatory=$false)]
        [ValidateSet('INFO', 'WARN', 'ERROR')]
        [string]$Level = 'INFO'
    )

    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $logMessage = "[$timestamp] [$Level] $Message"
    $logFile = Join-Path $script:ProcessManagerConfig.LogDir "process-manager.log"

    Add-Content -Path $logFile -Value $logMessage

    switch ($Level) {
        'ERROR' { Write-Host $logMessage -ForegroundColor Red }
        'WARN'  { Write-Host $logMessage -ForegroundColor Yellow }
        default { Write-Host $logMessage -ForegroundColor Gray }
    }
}

# PID file management
function Get-PidFilePath {
    param([string]$Name)
    return Join-Path $script:ProcessManagerConfig.PidDir "$Name.pid"
}

function Get-RegisteredPid {
    param([string]$Name)

    $pidFile = Get-PidFilePath -Name $Name
    if (Test-Path $pidFile) {
        $pid = Get-Content $pidFile -Raw
        return [int]$pid.Trim()
    }
    return $null
}

function Register-ProcessPid {
    param(
        [int]$Pid,
        [string]$Name
    )

    $pidFile = Get-PidFilePath -Name $Name
    Set-Content -Path $pidFile -Value $Pid
    Write-ProcessLog "Registered PID $Pid for process '$Name' in $pidFile"
}

function Unregister-ProcessPid {
    param([string]$Name)

    $pidFile = Get-PidFilePath -Name $Name
    if (Test-Path $pidFile) {
        Remove-Item $pidFile -Force
        Write-ProcessLog "Unregistered process '$Name'"
    }
}

# Process status
function Test-ProcessRunning {
    param([int]$Pid)

    if ($Pid -le 0) { return $false }

    try {
        $process = Get-Process -Id $Pid -ErrorAction SilentlyContinue
        return $null -ne $process
    }
    catch {
        return $false
    }
}

# Port management
function Test-PortInUse {
    param([int]$Port)

    $connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    return $null -ne $connections
}

function Get-ProcessOnPort {
    param([int]$Port)

    $connection = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($connection) {
        return $connection.OwningProcess
    }
    return $null
}

function Get-AllProcessesOnPort {
    param([int]$Port)

    $connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    return $connections | ForEach-Object { $_.OwningProcess } | Select-Object -Unique
}

# Process termination
function Stop-ProcessSafely {
    param(
        [int]$Pid,
        [int]$Timeout = 10
    )

    if (-not (Test-ProcessRunning -Pid $Pid)) {
        Write-ProcessLog "Process $Pid is not running"
        return $true
    }

    try {
        Write-ProcessLog "Attempting graceful shutdown of PID $Pid"
        $process = Get-Process -Id $Pid -ErrorAction SilentlyContinue

        if ($process) {
            # Try graceful close first
            $process.CloseMainWindow() | Out-Null
            $exited = $process.WaitForExit($Timeout * 1000)

            if ($exited) {
                Write-ProcessLog "Process $Pid terminated gracefully"
                return $true
            }

            # Escalate to Kill
            Write-ProcessLog "Process $Pid did not exit gracefully, forcing termination" -Level WARN
            Stop-Process -Id $Pid -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 1

            if (-not (Test-ProcessRunning -Pid $Pid)) {
                Write-ProcessLog "Process $Pid forcefully terminated"
                return $true
            }
        }
    }
    catch {
        Write-ProcessLog "Error stopping process $Pid: $_" -Level ERROR
    }

    return -not (Test-ProcessRunning -Pid $Pid)
}

# Process tree termination
function Stop-ProcessTree {
    param(
        [int]$Pid,
        [int]$Timeout = 10
    )

    if (-not (Test-ProcessRunning -Pid $Pid)) {
        return $true
    }

    Write-ProcessLog "Stopping process tree for PID $Pid"

    # Get child processes
    $children = Get-CimInstance Win32_Process | Where-Object { $_.ParentProcessId -eq $Pid }

    # Stop children first
    foreach ($child in $children) {
        Stop-ProcessTree -Pid $child.ProcessId -Timeout $Timeout
    }

    # Stop parent
    return Stop-ProcessSafely -Pid $Pid -Timeout $Timeout
}

# Port cleanup with retry
function Clear-Port {
    param(
        [int]$Port,
        [int]$MaxRetries = 3
    )

    Write-ProcessLog "Cleaning up port $Port (max $MaxRetries retries)"

    for ($retry = 0; $retry -lt $MaxRetries; $retry++) {
        if (-not (Test-PortInUse -Port $Port)) {
            Write-ProcessLog "Port $Port is free"
            return $true
        }

        $pids = Get-AllProcessesOnPort -Port $Port
        if ($pids.Count -eq 0) {
            Write-ProcessLog "Port $Port is in use but no PIDs found" -Level WARN
            Start-Sleep -Seconds 2
            continue
        }

        Write-ProcessLog "Port $Port is used by PIDs: $($pids -join ', ') (attempt $($retry + 1)/$MaxRetries)"

        foreach ($pid in $pids) {
            try {
                Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
            }
            catch {
                Write-ProcessLog "Failed to kill PID $pid: $_" -Level WARN
            }
        }

        Start-Sleep -Seconds 2
    }

    if (Test-PortInUse -Port $Port) {
        Write-ProcessLog "Failed to free port $Port after $MaxRetries attempts" -Level ERROR
        return $false
    }

    Write-ProcessLog "Port $Port successfully freed"
    return $true
}

# Orphan cleanup
function Clear-OrphanedPids {
    Write-ProcessLog "Scanning for orphaned PID files..."

    $cleaned = 0
    $pidFiles = Get-ChildItem -Path $script:ProcessManagerConfig.PidDir -Filter "*.pid" -ErrorAction SilentlyContinue

    foreach ($pidFile in $pidFiles) {
        $name = $pidFile.BaseName
        $pid = Get-RegisteredPid -Name $name

        if ($null -eq $pid) {
            Write-ProcessLog "Empty PID file: $($pidFile.Name)" -Level WARN
            Remove-Item $pidFile.FullName -Force
            $cleaned++
            continue
        }

        if (-not (Test-ProcessRunning -Pid $pid)) {
            Write-ProcessLog "Orphaned PID file detected: $name (PID: $pid)" -Level WARN
            Remove-Item $pidFile.FullName -Force
            $cleaned++
        }
    }

    Write-ProcessLog "Cleaned up $cleaned orphaned PID file(s)"
    return $cleaned
}

# Start process with Job Object
function Start-ManagedProcess {
    param(
        [string]$Name,
        [string]$Command,
        [string]$WorkingDirectory = (Get-Location).Path,
        [hashtable]$Environment = @{}
    )

    Initialize-ProcessManager

    # Check if already running
    $existingPid = Get-RegisteredPid -Name $Name
    if ($existingPid -and (Test-ProcessRunning -Pid $existingPid)) {
        Write-ProcessLog "Process '$Name' is already running (PID: $existingPid)" -Level ERROR
        return $false
    }

    # Clean up stale PID
    Unregister-ProcessPid -Name $Name

    Write-ProcessLog "Starting process: $Name"
    Write-ProcessLog "Command: $Command"

    try {
        # Create Job Object for grouped termination
        $job = Start-Job -ScriptBlock {
            param($cmd, $wd, $env)
            Set-Location $wd
            foreach ($key in $env.Keys) {
                [System.Environment]::SetEnvironmentVariable($key, $env[$key])
            }
            Invoke-Expression $cmd
        } -ArgumentList $Command, $WorkingDirectory, $Environment

        # Get the actual process PID (not the Job PID)
        Start-Sleep -Milliseconds 500
        $process = Get-Process -Id $job.ChildJobs[0].ProcessId -ErrorAction SilentlyContinue

        if ($process) {
            $pid = $process.Id
            Register-ProcessPid -Pid $pid -Name $Name
            Write-ProcessLog "Process '$Name' started successfully (PID: $pid)"
            return $pid
        }
        else {
            Write-ProcessLog "Process '$Name' failed to start" -Level ERROR
            Remove-Job $job -Force
            return $false
        }
    }
    catch {
        Write-ProcessLog "Error starting process '$Name': $_" -Level ERROR
        return $false
    }
}

# Stop managed process
function Stop-ManagedProcess {
    param(
        [string]$Name,
        [int]$Timeout = 10
    )

    $pid = Get-RegisteredPid -Name $Name

    if ($null -eq $pid) {
        Write-ProcessLog "No PID found for process '$Name'" -Level WARN
        Unregister-ProcessPid -Name $Name
        return $true
    }

    Write-ProcessLog "Stopping process: $Name (PID: $pid)"

    if (Stop-ProcessTree -Pid $pid -Timeout $Timeout) {
        Unregister-ProcessPid -Name $Name
        Write-ProcessLog "Process '$Name' stopped successfully"
        return $true
    }
    else {
        Write-ProcessLog "Failed to stop process '$Name'" -Level ERROR
        return $false
    }
}

# Get process status
function Get-ManagedProcessStatus {
    param([string]$Name)

    $pid = Get-RegisteredPid -Name $Name

    if ($null -eq $pid) {
        return @{
            Name = $Name
            Status = "Not registered"
            Pid = $null
        }
    }

    if (Test-ProcessRunning -Pid $pid) {
        $process = Get-Process -Id $pid
        return @{
            Name = $Name
            Status = "Running"
            Pid = $pid
            StartTime = $process.StartTime
            Memory = $process.WorkingSet64
        }
    }
    else {
        return @{
            Name = $Name
            Status = "Dead (stale PID)"
            Pid = $pid
        }
    }
}

# Export functions
Export-ModuleMember -Function `
    Initialize-ProcessManager,
    Write-ProcessLog,
    Get-RegisteredPid,
    Register-ProcessPid,
    Unregister-ProcessPid,
    Test-ProcessRunning,
    Test-PortInUse,
    Get-ProcessOnPort,
    Get-AllProcessesOnPort,
    Stop-ProcessSafely,
    Stop-ProcessTree,
    Clear-Port,
    Clear-OrphanedPids,
    Start-ManagedProcess,
    Stop-ManagedProcess,
    Get-ManagedProcessStatus
