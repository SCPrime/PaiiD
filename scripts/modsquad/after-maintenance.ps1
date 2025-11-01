param(
    [Parameter(Mandatory = $true)]
    [string]$Window,

    [string]$Status = "complete",

    [string]$MetricsJson = "",

    [string]$DetailsJson = "",

    [switch]$Verify
)

$repoRoot = (Resolve-Path "$PSScriptRoot/../..").Path
Set-Location $repoRoot

$python = if ($env:PYTHON) { $env:PYTHON } else { "python" }
$module = "modsquad.extensions.runner"
$cmd = @("-m", $module, "after-maintenance", "--window", $Window, "--status", $Status)

if ($MetricsJson) {
    $metricsPath = Resolve-Path $MetricsJson -ErrorAction Stop
    $cmd += @("--metrics-json", $metricsPath.Path)
}

if ($DetailsJson) {
    $detailsPath = Resolve-Path $DetailsJson -ErrorAction Stop
    $cmd += @("--details-json", $detailsPath.Path)
}

if ($Verify) {
    $cmd += "--verify"
}

& $python @cmd
if ($LASTEXITCODE -ne 0) {
    throw "MOD SQUAD extension runner failed with exit code $LASTEXITCODE"
}

