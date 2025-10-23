param(
    [switch]$Quiet
)

$ports = @(8001, 8002)
$terminated = @()
$inspected = @()

foreach ($port in $ports) {
    try {
        $connections = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction Stop
    } catch {
        continue
    }

    foreach ($connection in $connections) {
        $pid = $connection.OwningProcess
        if ($inspected -contains $pid) {
            continue
        }

        $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
        if (-not $process) {
            continue
        }

        $commandLine = $null
        try {
            $commandLine = (Get-CimInstance Win32_Process -Filter "ProcessId = $pid").CommandLine
        } catch {
            $commandLine = $null
        }

        $matchesUvicorn = $false
        if ($commandLine -and $commandLine -match "uvicorn") {
            $matchesUvicorn = $true
        } elseif ($process.Path -and $process.Path -match "uvicorn") {
            $matchesUvicorn = $true
        } elseif ($process.ProcessName -match "uvicorn") {
            $matchesUvicorn = $true
        }

        if (-not $matchesUvicorn) {
            continue
        }

        if (-not $Quiet) {
            $details = if ($commandLine) { $commandLine } else { $process.Path }
            Write-Host "Terminating uvicorn process $pid on port $($connection.LocalAddress):$($connection.LocalPort)" -ForegroundColor Yellow
            if ($details) {
                Write-Host "  Command: $details" -ForegroundColor DarkGray
            }
        }

        try {
            Stop-Process -Id $pid -ErrorAction SilentlyContinue
            Start-Sleep -Milliseconds 750
            if (Get-Process -Id $pid -ErrorAction SilentlyContinue) {
                Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
            }
            if (-not $Quiet) {
                Write-Host "  ✅ Process $pid terminated" -ForegroundColor Green
            }
            $terminated += $pid
        } catch {
            if (-not $Quiet) {
                Write-Host "  ❌ Failed to terminate process $pid: $($_.Exception.Message)" -ForegroundColor Red
            }
        }

        $inspected += $pid
    }
}

if (-not $Quiet -and $terminated.Count -eq 0) {
    Write-Host "No uvicorn processes found on ports 8001 or 8002." -ForegroundColor DarkGray
}
