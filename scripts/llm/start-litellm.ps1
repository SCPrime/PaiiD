Param(
  [string]$Port = "4000"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Ensure-LiteLLM {
  try {
    if (Get-Command litellm -ErrorAction SilentlyContinue) { return }
  } catch {}
  Write-Host "Installing litellm[proxy]..." -ForegroundColor Cyan
  python -m pip install --upgrade pip | Out-Null
  python -m pip install "litellm[proxy]" | Out-Null
}

function Ensure-Config {
  $cfg = Join-Path $PSScriptRoot 'litellm.config.yaml'
  $example = Join-Path $PSScriptRoot 'litellm.config.example.yaml'
  if (-not (Test-Path $cfg)) {
    if (Test-Path $example) {
      Copy-Item $example $cfg -Force
      Write-Host "Created $cfg from example." -ForegroundColor Green
    } else {
      throw "Missing example config at $example"
    }
  }
}

# Main
Ensure-LiteLLM
Ensure-Config

$cfgPath = Join-Path $PSScriptRoot 'litellm.config.yaml'
Write-Host "Starting LiteLLM proxy on port $Port using $cfgPath" -ForegroundColor Cyan
Start-Process -FilePath "litellm" -ArgumentList @("--config", $cfgPath, "--port", $Port) -WindowStyle Hidden
Start-Sleep -Seconds 2

Write-Host "LiteLLM running at http://127.0.0.1:$Port/v1" -ForegroundColor Green
