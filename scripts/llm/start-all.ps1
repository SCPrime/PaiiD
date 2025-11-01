Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$here = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "Starting Ollama..." -ForegroundColor Cyan
& (Join-Path $here 'start-ollama.ps1')

Write-Host "Starting LiteLLM proxy..." -ForegroundColor Cyan
& (Join-Path $here 'start-litellm.ps1') -Port 4000

Write-Host "Ready. Configure Cursor to http://127.0.0.1:4000/v1" -ForegroundColor Green
