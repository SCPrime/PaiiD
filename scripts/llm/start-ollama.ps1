Param(
  [switch]$SkipInstall
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Ensure-OllamaInstalled {
  if ($SkipInstall) { return }
  try {
    if (Get-Command ollama -ErrorAction SilentlyContinue) { return }
  } catch {}
  Write-Host "Installing Ollama via winget..." -ForegroundColor Cyan
  winget install -e --id Ollama.Ollama -h --accept-package-agreements --accept-source-agreements | Out-Null
}

function Start-OllamaServer {
  try {
    $ping = Invoke-RestMethod -Method Get -Uri 'http://127.0.0.1:11434/api/tags' -TimeoutSec 2
    Write-Host "Ollama already running." -ForegroundColor Green
    return
  } catch {}
  Write-Host "Starting ollama serve..." -ForegroundColor Cyan
  Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden
  Start-Sleep -Seconds 3
}

function Ensure-Model($name) {
  try {
    $out = ollama list | Select-String -SimpleMatch $name
    if ($out) { Write-Host "Model '$name' present." -ForegroundColor Green; return }
  } catch {}
  Write-Host "Pulling model '$name'..." -ForegroundColor Cyan
  ollama pull $name
}

# Main
Ensure-OllamaInstalled
Start-OllamaServer
Ensure-Model "deepseek-coder"
Ensure-Model "deepseek-r1"

Write-Host "Done. Ollama at http://127.0.0.1:11434" -ForegroundColor Green
