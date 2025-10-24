# 🔧 PowerShell Core Deployment Repair Script
# Comprehensive repair and verification for PowerShell Core installation
# Created: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

param(
    [switch]$Force,
    [switch]$Verbose,
    [string]$LogFile = "powershell-repair-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"
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

# Logging function
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    Add-Content -Path $LogFile -Value $logEntry -Encoding UTF8
    if ($Verbose) { Write-Host $logEntry }
}

Write-ColorOutput "`n╔══════════════════════════════════════════════════════════════╗" "Cyan"
Write-ColorOutput "║           🔧 PowerShell Core Deployment Repair              ║" "Cyan"
Write-ColorOutput "╚══════════════════════════════════════════════════════════════╝" "Cyan"
Write-ColorOutput ""

Write-Log "Starting PowerShell Core repair process"

# ============================================
# PHASE 1: DIAGNOSTIC ASSESSMENT
# ============================================
Write-Info "🔍 PHASE 1: Diagnostic Assessment"
Write-Log "Starting diagnostic assessment"

$diagnostics = @{
    PowerShellCoreInstalled = $false
    PowerShellCoreVersion = $null
    PowerShellCorePath = $null
    WindowsPowerShellVersion = $null
    ExecutionPolicy = $null
    EnvironmentPath = $null
    Issues = @()
}

# Check PowerShell Core installation
try {
    $pwshVersion = & pwsh -Version 2>$null
    if ($pwshVersion) {
        $diagnostics.PowerShellCoreInstalled = $true
        $diagnostics.PowerShellCoreVersion = $pwshVersion
        $diagnostics.PowerShellCorePath = (Get-Command pwsh -ErrorAction SilentlyContinue).Source
        Write-Success "PowerShell Core is installed: $pwshVersion"
        Write-Log "PowerShell Core found: $pwshVersion at $($diagnostics.PowerShellCorePath)"
    }
} catch {
    $diagnostics.Issues += "PowerShell Core not found or not accessible"
    Write-Error "PowerShell Core not found or not accessible"
    Write-Log "PowerShell Core not found: $($_.Exception.Message)"
}

# Check Windows PowerShell
try {
    $psVersion = $PSVersionTable.PSVersion
    $diagnostics.WindowsPowerShellVersion = $psVersion.ToString()
    Write-Info "Windows PowerShell version: $psVersion"
    Write-Log "Windows PowerShell version: $psVersion"
} catch {
    Write-Warning "Could not determine Windows PowerShell version"
}

# Check execution policy
try {
    $executionPolicy = Get-ExecutionPolicy
    $diagnostics.ExecutionPolicy = $executionPolicy
    Write-Info "Current execution policy: $executionPolicy"
    Write-Log "Execution policy: $executionPolicy"
} catch {
    $diagnostics.Issues += "Could not determine execution policy"
    Write-Warning "Could not determine execution policy"
}

# Check PATH environment
try {
    $pathEnv = $env:PATH -split ';' | Where-Object { $_ -like "*PowerShell*" }
    $diagnostics.EnvironmentPath = $pathEnv
    if ($pathEnv) {
        Write-Info "PowerShell paths in PATH: $($pathEnv -join ', ')"
        Write-Log "PowerShell paths found in PATH: $($pathEnv -join ', ')"
    } else {
        $diagnostics.Issues += "No PowerShell paths found in PATH environment variable"
        Write-Warning "No PowerShell paths found in PATH environment variable"
    }
} catch {
    $diagnostics.Issues += "Could not check PATH environment variable"
    Write-Warning "Could not check PATH environment variable"
}

# ============================================
# PHASE 2: ISSUE IDENTIFICATION
# ============================================
Write-Info "`n🔍 PHASE 2: Issue Identification"

$criticalIssues = @()
$warnings = @()

# Analyze diagnostic results
if (-not $diagnostics.PowerShellCoreInstalled) {
    $criticalIssues += "PowerShell Core is not installed or not accessible"
}

if ($diagnostics.ExecutionPolicy -eq "Restricted") {
    $criticalIssues += "Execution policy is set to Restricted, which may prevent script execution"
}

if (-not $diagnostics.EnvironmentPath) {
    $warnings += "PowerShell may not be in system PATH"
}

if ($diagnostics.Issues.Count -gt 0) {
    $criticalIssues += $diagnostics.Issues
}

# Report findings
if ($criticalIssues.Count -gt 0) {
    Write-Error "Critical issues found:"
    foreach ($issue in $criticalIssues) {
        Write-Error "  • $issue"
        Write-Log "CRITICAL: $issue"
    }
} else {
    Write-Success "No critical issues found"
    Write-Log "No critical issues found"
}

if ($warnings.Count -gt 0) {
    Write-Warning "Warnings:"
    foreach ($warning in $warnings) {
        Write-Warning "  • $warning"
        Write-Log "WARNING: $warning"
    }
}

# ============================================
# PHASE 3: REPAIR ACTIONS
# ============================================
Write-Info "`n🔧 PHASE 3: Repair Actions"

$repairActions = @()

# Fix execution policy if needed
if ($diagnostics.ExecutionPolicy -eq "Restricted") {
    Write-Info "Setting execution policy to RemoteSigned for current user"
    try {
        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
        Write-Success "Execution policy updated to RemoteSigned"
        Write-Log "Execution policy updated to RemoteSigned"
        $repairActions += "Updated execution policy to RemoteSigned"
    } catch {
        Write-Error "Failed to update execution policy: $($_.Exception.Message)"
        Write-Log "ERROR: Failed to update execution policy: $($_.Exception.Message)"
    }
}

# Add PowerShell to PATH if missing
if (-not $diagnostics.EnvironmentPath) {
    Write-Info "Adding PowerShell to PATH environment variable"
    try {
        $pwshPath = "C:\Program Files\PowerShell\7"
        if (Test-Path $pwshPath) {
            $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
            if ($currentPath -notlike "*$pwshPath*") {
                [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$pwshPath", "User")
                Write-Success "Added PowerShell to user PATH"
                Write-Log "Added PowerShell to user PATH: $pwshPath"
                $repairActions += "Added PowerShell to PATH environment variable"
            }
        } else {
            Write-Warning "PowerShell installation directory not found at expected location"
            Write-Log "WARNING: PowerShell installation directory not found at $pwshPath"
        }
    } catch {
        Write-Error "Failed to update PATH: $($_.Exception.Message)"
        Write-Log "ERROR: Failed to update PATH: $($_.Exception.Message)"
    }
}

# ============================================
# PHASE 4: VERIFICATION
# ============================================
Write-Info "`n✅ PHASE 4: Verification"

$verificationTests = @()

# Test 1: PowerShell Core version check
Write-Info "Testing PowerShell Core version command..."
try {
    $versionTest = & pwsh -Version 2>$null
    if ($versionTest) {
        Write-Success "PowerShell Core version test passed: $versionTest"
        Write-Log "VERIFICATION: PowerShell Core version test passed: $versionTest"
        $verificationTests += "PowerShell Core version command works"
    } else {
        Write-Error "PowerShell Core version test failed"
        Write-Log "VERIFICATION FAILED: PowerShell Core version test failed"
    }
} catch {
    Write-Error "PowerShell Core version test failed with error: $($_.Exception.Message)"
    Write-Log "VERIFICATION FAILED: PowerShell Core version test failed: $($_.Exception.Message)"
}

# Test 2: PowerShell Core execution
Write-Info "Testing PowerShell Core script execution..."
try {
    $testScript = 'Write-Output "PowerShell Core test successful"'
    $testResult = & pwsh -Command $testScript 2>$null
    if ($testResult -eq "PowerShell Core test successful") {
        Write-Success "PowerShell Core script execution test passed"
        Write-Log "VERIFICATION: PowerShell Core script execution test passed"
        $verificationTests += "PowerShell Core script execution works"
    } else {
        Write-Error "PowerShell Core script execution test failed"
        Write-Log "VERIFICATION FAILED: PowerShell Core script execution test failed"
    }
} catch {
    Write-Error "PowerShell Core script execution test failed: $($_.Exception.Message)"
    Write-Log "VERIFICATION FAILED: PowerShell Core script execution test failed: $($_.Exception.Message)"
}

# Test 3: PowerShell Core module loading
Write-Info "Testing PowerShell Core module capabilities..."
try {
    $moduleTest = & pwsh -Command "Get-Module -ListAvailable | Select-Object -First 1 | Format-Table -AutoSize" 2>$null
    if ($moduleTest) {
        Write-Success "PowerShell Core module test passed"
        Write-Log "VERIFICATION: PowerShell Core module test passed"
        $verificationTests += "PowerShell Core module loading works"
    } else {
        Write-Warning "PowerShell Core module test had no output"
        Write-Log "VERIFICATION WARNING: PowerShell Core module test had no output"
    }
} catch {
    Write-Warning "PowerShell Core module test failed: $($_.Exception.Message)"
    Write-Log "VERIFICATION WARNING: PowerShell Core module test failed: $($_.Exception.Message)"
}

# ============================================
# PHASE 5: FINAL REPORT
# ============================================
Write-Info "`n📊 PHASE 5: Final Report"

Write-ColorOutput "`n╔══════════════════════════════════════════════════════════════╗" "Cyan"
Write-ColorOutput "║                    📊 REPAIR SUMMARY                        ║" "Cyan"
Write-ColorOutput "╚══════════════════════════════════════════════════════════════╝" "Cyan"

# System Status
Write-Info "System Status:"
Write-Info "  PowerShell Core Installed: $($diagnostics.PowerShellCoreInstalled)"
if ($diagnostics.PowerShellCoreVersion) {
    Write-Info "  PowerShell Core Version: $($diagnostics.PowerShellCoreVersion)"
}
if ($diagnostics.PowerShellCorePath) {
    Write-Info "  PowerShell Core Path: $($diagnostics.PowerShellCorePath)"
}
Write-Info "  Windows PowerShell Version: $($diagnostics.WindowsPowerShellVersion)"
Write-Info "  Execution Policy: $($diagnostics.ExecutionPolicy)"

# Issues Found
if ($criticalIssues.Count -gt 0) {
    Write-Error "Critical Issues Found: $($criticalIssues.Count)"
    foreach ($issue in $criticalIssues) {
        Write-Error "  • $issue"
    }
} else {
    Write-Success "No critical issues found"
}

if ($warnings.Count -gt 0) {
    Write-Warning "Warnings: $($warnings.Count)"
    foreach ($warning in $warnings) {
        Write-Warning "  • $warning"
    }
}

# Repair Actions Taken
if ($repairActions.Count -gt 0) {
    Write-Info "Repair Actions Taken:"
    foreach ($action in $repairActions) {
        Write-Success "  ✓ $action"
    }
} else {
    Write-Info "No repair actions were necessary"
}

# Verification Results
Write-Info "Verification Tests Passed: $($verificationTests.Count)"
foreach ($test in $verificationTests) {
    Write-Success "  ✓ $test"
}

# Overall Status
$overallStatus = if ($criticalIssues.Count -eq 0 -and $verificationTests.Count -gt 0) {
    "HEALTHY"
} elseif ($criticalIssues.Count -eq 0) {
    "PARTIALLY_HEALTHY"
} else {
    "NEEDS_ATTENTION"
}

Write-ColorOutput "`nOverall Status: $overallStatus" $(switch ($overallStatus) {
    "HEALTHY" { "Green" }
    "PARTIALLY_HEALTHY" { "Yellow" }
    default { "Red" }
})

# Recommendations
Write-Info "`nRecommendations:"
if ($overallStatus -eq "HEALTHY") {
    Write-Success "  • PowerShell Core is working correctly"
    Write-Success "  • No further action required"
} elseif ($overallStatus -eq "PARTIALLY_HEALTHY") {
    Write-Warning "  • PowerShell Core is installed but may have minor issues"
    Write-Warning "  • Consider restarting your terminal/IDE"
} else {
    Write-Error "  • PowerShell Core installation needs attention"
    Write-Error "  • Consider reinstalling PowerShell Core"
    Write-Error "  • Check system permissions and antivirus software"
}

Write-Log "Repair process completed. Overall status: $overallStatus"
Write-Info "`nLog file saved to: $LogFile"

# Exit with appropriate code
$exitCode = switch ($overallStatus) {
    "HEALTHY" { 0 }
    "PARTIALLY_HEALTHY" { 1 }
    default { 2 }
}

Write-ColorOutput "`nRepair script completed with exit code: $exitCode" "Cyan"
exit $exitCode
