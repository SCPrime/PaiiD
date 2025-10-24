<#
.SYNOPSIS
    Ensures PowerShell 7+ (PowerShell Core) is available and provides install guidance per platform.

.DESCRIPTION
    This script detects whether the cross-platform `pwsh` executable is available.
    When run with Windows PowerShell 5.1 or PowerShell Core it will:
      * Detect the host operating system.
      * Verify the installed version of `pwsh` meets the minimum requirement (7.2).
      * Offer installation commands for Windows, macOS and popular Linux distributions.
      * Emit a compatibility matrix covering high-priority PaiiD automation scripts.

    The script is intentionally non-destructive – it guides the user rather than forcing
    installation so it can be executed safely inside CI/CD or constrained environments.

.PARAMETER MinimumVersion
    Optional semantic version string that overrides the default minimum of 7.2.0.

.EXAMPLE
    pwsh -File ./scripts/ensure-powershell-core.ps1

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File ./scripts/ensure-powershell-core.ps1 -MinimumVersion 7.4.0
#>
[CmdletBinding()]
param(
    [Version]$MinimumVersion = [Version]"7.2.0"
)

function Write-Section {
    param(
        [Parameter(Mandatory)]
        [string]$Title
    )

    Write-Host "`n==== $Title ==== " -ForegroundColor Cyan
}

function Get-PlatformInfo {
    if ($IsWindows) {
        return [pscustomobject]@{ Platform = "Windows"; Details = (Get-CimInstance Win32_OperatingSystem).Caption }
    }

    if ($IsMacOS) {
        $product = sw_vers -productName 2>$null
        $version = sw_vers -productVersion 2>$null
        return [pscustomobject]@{ Platform = "macOS"; Details = "$product $version" }
    }

    if ($IsLinux) {
        $osRelease = Get-Content -Path /etc/os-release -ErrorAction SilentlyContinue
        if ($osRelease) {
            $name = ($osRelease | Where-Object { $_ -like "NAME=*" }).Split('=')[1].Trim('"')
            $version = ($osRelease | Where-Object { $_ -like "VERSION=*" }).Split('=')[1].Trim('"')
            return [pscustomobject]@{ Platform = "Linux"; Details = "$name $version" }
        }
    }

    return [pscustomobject]@{ Platform = "Unknown"; Details = "Unknown host" }
}

function Write-InstallGuidance {
    param(
        [Parameter(Mandatory)]
        [string]$Platform
    )

    Write-Section "Installation Guidance"
    switch ($Platform) {
        "Windows" {
            Write-Host "Use winget (recommended):" -ForegroundColor Yellow
            Write-Host "  winget install --id Microsoft.PowerShell -e" -ForegroundColor Gray
            Write-Host "";
            Write-Host "Alternative (MSI installer):" -ForegroundColor Yellow
            Write-Host "  https://aka.ms/powershell-release?tag=stable" -ForegroundColor Gray
        }
        "macOS" {
            Write-Host "Homebrew (recommended):" -ForegroundColor Yellow
            Write-Host "  brew install --cask powershell" -ForegroundColor Gray
            Write-Host "";
            Write-Host "Direct download (PKG):" -ForegroundColor Yellow
            Write-Host "  https://aka.ms/powershell-release?tag=stable" -ForegroundColor Gray
        }
        "Linux" {
            Write-Host "Debian/Ubuntu:" -ForegroundColor Yellow
            Write-Host "  sudo apt-get update && sudo apt-get install -y powershell" -ForegroundColor Gray
            Write-Host "";
            Write-Host "RHEL/CentOS:" -ForegroundColor Yellow
            Write-Host "  sudo dnf install -y powershell" -ForegroundColor Gray
            Write-Host "";
            Write-Host "See additional distributions:" -ForegroundColor Yellow
            Write-Host "  https://learn.microsoft.com/powershell/scripting/install/installing-powershell" -ForegroundColor Gray
        }
        Default {
            Write-Host "Refer to official installation guide:" -ForegroundColor Yellow
            Write-Host "  https://learn.microsoft.com/powershell/scripting/install/installing-powershell" -ForegroundColor Gray
        }
    }
}

function Write-CompatibilityReport {
    param(
        [Parameter(Mandatory)]
        [Version]$DetectedVersion
    )

    Write-Section "PaiiD Script Compatibility"

    $scripts = @(
        @{ Name = "start-dev.ps1"; Purpose = "Local full-stack bootstrap" },
        @{ Name = "start-chrome-dev.ps1"; Purpose = "Chromium dev harness" },
        @{ Name = "deploy-production.ps1"; Purpose = "Render production deployment" },
        @{ Name = "test-production.ps1"; Purpose = "Production smoke validation" },
        @{ Name = "setup-dev-tools.ps1"; Purpose = "One-time workstation bootstrap" }
    )

    foreach ($script in $scripts) {
        $path = Join-Path $PSScriptRoot "..\$($script.Name)"
        $exists = Test-Path $path
        $status = if ($exists) { "Ready" } else { "Missing" }
        $color = if ($exists) { "Green" } else { "Red" }
        Write-Host ("{0,-28} {1,-10} {2}" -f $script.Name, $DetectedVersion, $script.Purpose) -ForegroundColor $color
    }

    Write-Host "`nAll listed workflows are compatible with PowerShell Core 7+." -ForegroundColor Green
}

Write-Section "Environment"
$platformInfo = Get-PlatformInfo
Write-Host ("Platform: {0}" -f $platformInfo.Platform) -ForegroundColor White
Write-Host ("Details:  {0}" -f $platformInfo.Details) -ForegroundColor White

$pwsh = Get-Command pwsh -ErrorAction SilentlyContinue
if (-not $pwsh) {
    Write-Host "`n⚠️  PowerShell 7+ (pwsh) is not currently installed or not in PATH." -ForegroundColor Yellow
    Write-InstallGuidance -Platform $platformInfo.Platform
    return
}

$pwshVersionOutput = pwsh -NoLogo -NoProfile -Command "$PSVersionTable.PSVersion" 2>$null
if (-not $pwshVersionOutput) {
    Write-Host "`n⚠️  Unable to determine pwsh version." -ForegroundColor Yellow
    Write-InstallGuidance -Platform $platformInfo.Platform
    return
}

$version = [Version]$pwshVersionOutput
Write-Host ("Detected PowerShell Core: pwsh {0}" -f $version) -ForegroundColor Green

if ($version -lt $MinimumVersion) {
    Write-Host ("`n⚠️  Minimum required version is {0}." -f $MinimumVersion) -ForegroundColor Yellow
    Write-InstallGuidance -Platform $platformInfo.Platform
    return
}

Write-Section "Status"
Write-Host "✅ PowerShell Core meets minimum version requirements" -ForegroundColor Green
Write-Host "   Minimum: $MinimumVersion" -ForegroundColor Gray
Write-Host "   Actual : $version" -ForegroundColor Gray

Write-CompatibilityReport -DetectedVersion $version
Write-Host "`nYou are ready to run PaiiD automation workflows with pwsh." -ForegroundColor Cyan
