param(
    [int[]]$Ports = @(3000, 8001),
    [string]$BackendHealthUrl = "http://localhost:8001/api/health/detailed",
    [string]$FrontendUrl = "http://localhost:3000",
    [string]$LogDirectory = "monitoring/logs"
)

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

if (-not (Test-Path $LogDirectory)) {
    New-Item -ItemType Directory -Force -Path $LogDirectory | Out-Null
}

$logPath = Join-Path $LogDirectory "health-monitor.log"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $entry = "[$timestamp] [$Level] $Message"
    Add-Content -Path $logPath -Value $entry
}

function Test-Port {
    param([int]$Port)
    try {
        $result = Test-NetConnection -ComputerName "localhost" -Port $Port -WarningAction SilentlyContinue
        if ($result.TcpTestSucceeded) {
            Write-Log "Port $Port reachable (PID: $($result.PingReplyDetails.Address))"
        }
        else {
            Write-Log "Port $Port unreachable" "WARN"
        }
    }
    catch {
        Write-Log "Failed to test port $Port - $_" "ERROR"
    }
}

foreach ($port in $Ports) {
    Test-Port -Port $port
}

try {
    $response = Invoke-WebRequest -Uri $BackendHealthUrl -TimeoutSec 5
    Write-Log "Backend health: $($response.StatusCode)"
}
catch {
    Write-Log "Backend health endpoint failed - $_" "ERROR"
}

try {
    $response = Invoke-WebRequest -Uri $FrontendUrl -TimeoutSec 5
    Write-Log "Frontend response: $($response.StatusCode)"
}
catch {
    Write-Log "Frontend check failed - $_" "ERROR"
}

Write-Log "Health monitor run complete"
