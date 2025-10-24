# PowerShell Core Utilities

This directory contains cross-platform helper scripts for maintaining the PowerShell-based
workflow that drives PaiiD automation.

## ensure-powershell-core.ps1

Verifies that PowerShell 7+ (`pwsh`) is installed, meets the minimum supported version and
summarises compatibility with the high-priority `.ps1` automation entrypoints.

```powershell
# From the repository root
echo "Checking PowerShell Core availability"
pwsh -File ./scripts/ensure-powershell-core.ps1

# Run from Windows PowerShell when pwsh is not yet available
powershell -ExecutionPolicy Bypass -File ./scripts/ensure-powershell-core.ps1
```

The script is non-destructive: if `pwsh` is missing it prints platform-specific commands for
winget, Homebrew, or the appropriate Linux package manager instead of attempting privileged
installs automatically.

### Why this matters

All first-class PaiiD scripts (deployment, smoke tests, workstation setup and local bootstrap)
are now validated to launch under PowerShell Core. Verifying the runtime up front prevents
issues when running workflows with `pwsh` on Windows, macOS or Linux.

### Compatibility report

Every run emits a compatibility table that highlights key `.ps1` automation entrypoints and the
installed PowerShell version, making it easy to capture the output in deployment checklists or
runbooks.
