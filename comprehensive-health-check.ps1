# 🏥 Comprehensive PowerShell Health Check
# Advanced diagnostic and health monitoring for PowerShell environments
# Created: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

param(
    [switch]$Detailed,
    [switch]$Export,
    [string]$OutputFile = "powershell-health-report-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
)

$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"

# Color functions
function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Write-Success { param([string]$Message) Write-ColorOutput "✅ $Message" "Green" }
function Write-Error { param([string]$Message) Write-ColorOutput "❌ $Message" "Red" }
function Write-Warning { param([string]$Message) Write-ColorOutput "⚠️ $Message" "Yellow" }
function Write-Info { param([string]$Message) Write-ColorOutput "ℹ️ $Message" "Cyan" }

Write-ColorOutput "`n╔══════════════════════════════════════════════════════════════╗" "Cyan"
Write-ColorOutput "║              🏥 Comprehensive PowerShell Health Check        ║" "Cyan"
Write-ColorOutput "╚══════════════════════════════════════════════════════════════╝" "Cyan"
Write-ColorOutput ""

# Initialize health report
$healthReport = @{
    Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    SystemInfo = @{}
    PowerShellCore = @{}
    WindowsPowerShell = @{}
    Environment = @{}
    Security = @{}
    Performance = @{}
    Issues = @()
    Recommendations = @()
    OverallHealth = "Unknown"
}

# ============================================
# SYSTEM INFORMATION
# ============================================
Write-Info "🔍 Gathering System Information"

try {
    $osInfo = Get-WmiObject -Class Win32_OperatingSystem
    $healthReport.SystemInfo = @{
        OSName = $osInfo.Caption
        OSVersion = $osInfo.Version
        Architecture = $osInfo.OSArchitecture
        TotalMemory = [Math]::Round($osInfo.TotalVisibleMemorySize / 1MB, 2)
        FreeMemory = [Math]::Round($osInfo.FreePhysicalMemory / 1MB, 2)
        ComputerName = $env:COMPUTERNAME
        Username = $env:USERNAME
    }
    Write-Success "System information gathered"
} catch {
    Write-Error "Failed to gather system information: $($_.Exception.Message)"
    $healthReport.Issues += "Could not gather system information"
}

# ============================================
# POWERSHELL CORE HEALTH
# ============================================
Write-Info "`n🔍 Checking PowerShell Core Health"

$pwshHealth = @{
    Installed = $false
    Version = $null
    Path = $null
    ExecutionPolicy = $null
    Modules = @()
    Performance = @{}
    Issues = @()
}

# Check if PowerShell Core is installed
try {
    $pwshVersion = & pwsh -Version 2>$null
    if ($pwshVersion) {
        $pwshHealth.Installed = $true
        $pwshHealth.Version = $pwshVersion
        $pwshHealth.Path = (Get-Command pwsh -ErrorAction SilentlyContinue).Source
        Write-Success "PowerShell Core found: $pwshVersion"
    } else {
        $pwshHealth.Issues += "PowerShell Core not found or not accessible"
        Write-Error "PowerShell Core not found"
    }
} catch {
    $pwshHealth.Issues += "PowerShell Core command failed: $($_.Exception.Message)"
    Write-Error "PowerShell Core command failed: $($_.Exception.Message)"
}

# Check PowerShell Core execution policy
if ($pwshHealth.Installed) {
    try {
        $pwshPolicy = & pwsh -Command "Get-ExecutionPolicy" 2>$null
        $pwshHealth.ExecutionPolicy = $pwshPolicy
        Write-Info "PowerShell Core execution policy: $pwshPolicy"
    } catch {
        $pwshHealth.Issues += "Could not determine PowerShell Core execution policy"
        Write-Warning "Could not determine PowerShell Core execution policy"
    }
}

# Check PowerShell Core modules
if ($pwshHealth.Installed) {
    try {
        $pwshModules = & pwsh -Command "Get-Module -ListAvailable | Select-Object Name, Version | ConvertTo-Json" 2>$null | ConvertFrom-Json
        $pwshHealth.Modules = $pwshModules
        Write-Info "PowerShell Core modules found: $($pwshModules.Count)"
    } catch {
        $pwshHealth.Issues += "Could not enumerate PowerShell Core modules"
        Write-Warning "Could not enumerate PowerShell Core modules"
    }
}

# Performance test for PowerShell Core
if ($pwshHealth.Installed) {
    try {
        $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
        & pwsh -Command "Get-Date" 2>$null | Out-Null
        $stopwatch.Stop()
        $pwshHealth.Performance.StartupTime = $stopwatch.ElapsedMilliseconds
        Write-Info "PowerShell Core startup time: $($stopwatch.ElapsedMilliseconds)ms"
    } catch {
        $pwshHealth.Issues += "PowerShell Core performance test failed"
        Write-Warning "PowerShell Core performance test failed"
    }
}

$healthReport.PowerShellCore = $pwshHealth

# ============================================
# WINDOWS POWERSHELL HEALTH
# ============================================
Write-Info "`n🔍 Checking Windows PowerShell Health"

$psHealth = @{
    Version = $null
    ExecutionPolicy = $null
    Modules = @()
    Performance = @{}
    Issues = @()
}

# Windows PowerShell version
try {
    $psVersion = $PSVersionTable.PSVersion
    $psHealth.Version = $psVersion.ToString()
    Write-Success "Windows PowerShell version: $psVersion"
} catch {
    $psHealth.Issues += "Could not determine Windows PowerShell version"
    Write-Error "Could not determine Windows PowerShell version"
}

# Windows PowerShell execution policy
try {
    $psPolicy = Get-ExecutionPolicy
    $psHealth.ExecutionPolicy = $psPolicy
    Write-Info "Windows PowerShell execution policy: $psPolicy"
} catch {
    $psHealth.Issues += "Could not determine Windows PowerShell execution policy"
    Write-Warning "Could not determine Windows PowerShell execution policy"
}

# Windows PowerShell modules
try {
    $psModules = Get-Module -ListAvailable | Select-Object Name, Version
    $psHealth.Modules = $psModules
    Write-Info "Windows PowerShell modules found: $($psModules.Count)"
} catch {
    $psHealth.Issues += "Could not enumerate Windows PowerShell modules"
    Write-Warning "Could not enumerate Windows PowerShell modules"
}

# Performance test for Windows PowerShell
try {
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    Get-Date | Out-Null
    $stopwatch.Stop()
    $psHealth.Performance.StartupTime = $stopwatch.ElapsedMilliseconds
    Write-Info "Windows PowerShell startup time: $($stopwatch.ElapsedMilliseconds)ms"
} catch {
    $psHealth.Issues += "Windows PowerShell performance test failed"
    Write-Warning "Windows PowerShell performance test failed"
}

$healthReport.WindowsPowerShell = $psHealth

# ============================================
# ENVIRONMENT HEALTH
# ============================================
Write-Info "`n🔍 Checking Environment Health"

$envHealth = @{
    PATH = @{}
    EnvironmentVariables = @{}
    PowerShellPaths = @()
    Issues = @()
}

# Check PATH environment variable
try {
    $pathEntries = $env:PATH -split ';' | Where-Object { $_ -ne '' }
    $envHealth.PATH.TotalEntries = $pathEntries.Count
    $envHealth.PATH.Entries = $pathEntries
    
    $powershellPaths = $pathEntries | Where-Object { $_ -like "*PowerShell*" }
    $envHealth.PowerShellPaths = $powershellPaths
    
    if ($powershellPaths) {
        Write-Success "PowerShell paths found in PATH: $($powershellPaths.Count)"
    } else {
        $envHealth.Issues += "No PowerShell paths found in PATH environment variable"
        Write-Warning "No PowerShell paths found in PATH environment variable"
    }
} catch {
    $envHealth.Issues += "Could not check PATH environment variable"
    Write-Error "Could not check PATH environment variable"
}

# Check important environment variables
$importantVars = @('PSModulePath', 'PSExecutionPolicyPreference', 'PSDefaultParameterValues')
foreach ($var in $importantVars) {
    try {
        $value = [Environment]::GetEnvironmentVariable($var)
        $envHealth.EnvironmentVariables[$var] = $value
        if ($value) {
            Write-Info "$var = $value"
        } else {
            Write-Warning "$var is not set"
        }
    } catch {
        $envHealth.Issues += "Could not check environment variable: $var"
        Write-Warning "Could not check environment variable: $var"
    }
}

$healthReport.Environment = $envHealth

# ============================================
# SECURITY HEALTH
# ============================================
Write-Info "`n🔍 Checking Security Health"

$securityHealth = @{
    ExecutionPolicies = @{}
    ScriptSigning = @{}
    Antivirus = @{}
    Issues = @()
}

# Check execution policies for both PowerShell versions
$executionPolicies = @{
    "CurrentUser" = Get-ExecutionPolicy -Scope CurrentUser
    "LocalMachine" = Get-ExecutionPolicy -Scope LocalMachine
    "Process" = Get-ExecutionPolicy -Scope Process
}

$securityHealth.ExecutionPolicies = $executionPolicies

foreach ($scope in $executionPolicies.Keys) {
    $policy = $executionPolicies[$scope]
    Write-Info "Execution policy ($scope): $policy"
    
    if ($policy -eq "Restricted") {
        $securityHealth.Issues += "Execution policy is Restricted for $scope"
        Write-Warning "Execution policy is Restricted for $scope"
    }
}

# Check for script signing
try {
    $signingCert = Get-ChildItem -Path Cert:\CurrentUser\My -CodeSigningCert -ErrorAction SilentlyContinue
    $securityHealth.ScriptSigning.Certificates = $signingCert.Count
    if ($signingCert) {
        Write-Info "Code signing certificates found: $($signingCert.Count)"
    } else {
        Write-Info "No code signing certificates found"
    }
} catch {
    $securityHealth.Issues += "Could not check code signing certificates"
    Write-Warning "Could not check code signing certificates"
}

$healthReport.Security = $securityHealth

# ============================================
# PERFORMANCE HEALTH
# ============================================
Write-Info "`n🔍 Checking Performance Health"

$perfHealth = @{
    MemoryUsage = @{}
    CPUUsage = @{}
    DiskSpace = @{}
    NetworkConnectivity = @{}
    Issues = @()
}

# Memory usage
try {
    $memory = Get-WmiObject -Class Win32_OperatingSystem
    $totalMemory = [Math]::Round($memory.TotalVisibleMemorySize / 1MB, 2)
    $freeMemory = [Math]::Round($memory.FreePhysicalMemory / 1MB, 2)
    $usedMemory = $totalMemory - $freeMemory
    $memoryPercent = [Math]::Round(($usedMemory / $totalMemory) * 100, 2)
    
    $perfHealth.MemoryUsage = @{
        Total = $totalMemory
        Free = $freeMemory
        Used = $usedMemory
        PercentUsed = $memoryPercent
    }
    
    Write-Info "Memory usage: $usedMemory GB / $totalMemory GB ($memoryPercent%)"
    
    if ($memoryPercent -gt 90) {
        $perfHealth.Issues += "High memory usage: $memoryPercent%"
        Write-Warning "High memory usage: $memoryPercent%"
    }
} catch {
    $perfHealth.Issues += "Could not check memory usage"
    Write-Warning "Could not check memory usage"
}

# Disk space
try {
    $drives = Get-WmiObject -Class Win32_LogicalDisk | Where-Object { $_.DriveType -eq 3 }
    $diskInfo = @()
    foreach ($drive in $drives) {
        $totalSpace = [Math]::Round($drive.Size / 1GB, 2)
        $freeSpace = [Math]::Round($drive.FreeSpace / 1GB, 2)
        $usedSpace = $totalSpace - $freeSpace
        $percentUsed = [Math]::Round(($usedSpace / $totalSpace) * 100, 2)
        
        $diskInfo += @{
            Drive = $drive.DeviceID
            Total = $totalSpace
            Free = $freeSpace
            Used = $usedSpace
            PercentUsed = $percentUsed
        }
        
        if ($percentUsed -gt 90) {
            $perfHealth.Issues += "High disk usage on $($drive.DeviceID): $percentUsed%"
            Write-Warning "High disk usage on $($drive.DeviceID): $percentUsed%"
        }
    }
    $perfHealth.DiskSpace = $diskInfo
} catch {
    $perfHealth.Issues += "Could not check disk space"
    Write-Warning "Could not check disk space"
}

$healthReport.Performance = $perfHealth

# ============================================
# OVERALL HEALTH ASSESSMENT
# ============================================
Write-Info "`n🔍 Assessing Overall Health"

$totalIssues = 0
$criticalIssues = 0
$warnings = 0

# Count issues from all health checks
$allHealthChecks = @($healthReport.PowerShellCore, $healthReport.WindowsPowerShell, $healthReport.Environment, $healthReport.Security, $healthReport.Performance)

foreach ($check in $allHealthChecks) {
    if ($check.Issues) {
        $totalIssues += $check.Issues.Count
        foreach ($issue in $check.Issues) {
            if ($issue -like "*Critical*" -or $issue -like "*Failed*" -or $issue -like "*not found*") {
                $criticalIssues++
            } else {
                $warnings++
            }
        }
    }
}

# Determine overall health
if ($criticalIssues -eq 0 -and $warnings -le 2) {
    $healthReport.OverallHealth = "HEALTHY"
    $healthColor = "Green"
} elseif ($criticalIssues -eq 0 -and $warnings -le 5) {
    $healthReport.OverallHealth = "WARNING"
    $healthColor = "Yellow"
} else {
    $healthReport.OverallHealth = "CRITICAL"
    $healthColor = "Red"
}

# Generate recommendations
$recommendations = @()

if ($healthReport.PowerShellCore.Issues.Count -gt 0) {
    $recommendations += "Install or repair PowerShell Core installation"
}

if ($healthReport.Security.ExecutionPolicies.Values -contains "Restricted") {
    $recommendations += "Consider updating execution policy to allow script execution"
}

if ($healthReport.Environment.PowerShellPaths.Count -eq 0) {
    $recommendations += "Add PowerShell to system PATH environment variable"
}

if ($healthReport.Performance.MemoryUsage.PercentUsed -gt 90) {
    $recommendations += "Consider freeing up system memory"
}

if ($healthReport.Performance.DiskSpace | Where-Object { $_.PercentUsed -gt 90 }) {
    $recommendations += "Consider freeing up disk space"
}

$healthReport.Recommendations = $recommendations

# ============================================
# FINAL REPORT
# ============================================
Write-ColorOutput "`n╔══════════════════════════════════════════════════════════════╗" "Cyan"
Write-ColorOutput "║                    📊 HEALTH REPORT                          ║" "Cyan"
Write-ColorOutput "╚══════════════════════════════════════════════════════════════╝" "Cyan"

Write-ColorOutput "`nOverall Health: $($healthReport.OverallHealth)" $healthColor
Write-Info "Total Issues: $totalIssues (Critical: $criticalIssues, Warnings: $warnings)"

if ($healthReport.PowerShellCore.Installed) {
    Write-Success "PowerShell Core: Installed ($($healthReport.PowerShellCore.Version))"
} else {
    Write-Error "PowerShell Core: Not installed or not accessible"
}

Write-Info "Windows PowerShell: $($healthReport.WindowsPowerShell.Version)"
Write-Info "System: $($healthReport.SystemInfo.OSName) $($healthReport.SystemInfo.OSVersion)"

if ($recommendations.Count -gt 0) {
    Write-Info "`nRecommendations:"
    foreach ($rec in $recommendations) {
        Write-Warning "  • $rec"
    }
}

# Export report if requested
if ($Export) {
    try {
        $healthReport | ConvertTo-Json -Depth 10 | Out-File -FilePath $OutputFile -Encoding UTF8
        Write-Success "Health report exported to: $OutputFile"
    } catch {
        Write-Error "Failed to export health report: $($_.Exception.Message)"
    }
}

# Detailed report if requested
if ($Detailed) {
    Write-Info "`nDetailed Health Report:"
    $healthReport | ConvertTo-Json -Depth 10 | Write-Host
}

Write-ColorOutput "`nHealth check completed." "Cyan"

# Exit with appropriate code
$exitCode = switch ($healthReport.OverallHealth) {
    "HEALTHY" { 0 }
    "WARNING" { 1 }
    default { 2 }
}

exit $exitCode
