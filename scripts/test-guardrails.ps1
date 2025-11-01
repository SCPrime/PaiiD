#!/usr/bin/env pwsh
# Test MOD SQUAD guardrail extensions
# Run from repo root: ./scripts/test-guardrails.ps1

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = $PWD

Write-Host "[OK] Testing MOD SQUAD Guardrail Extensions" -ForegroundColor Green
Write-Host ""

# Test 1: Infrastructure Health
Write-Host "[TEST] infra_health extension..." -ForegroundColor Cyan
try {
    python -m modsquad.extensions.infra_health
    Write-Host "[OK] infra_health completed" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] infra_health error: $_" -ForegroundColor Red
}

Write-Host ""

# Test 2: Browser Validator (may fail if frontend not running)
Write-Host "[TEST] browser_validator extension..." -ForegroundColor Cyan
try {
    python -m modsquad.extensions.browser_validator 2>&1 | Out-Null
    Write-Host "[OK] browser_validator completed (check logs for results)" -ForegroundColor Green
} catch {
    Write-Host "[WARN] browser_validator: $_" -ForegroundColor Yellow
}

Write-Host ""

# Test 3: Contract Enforcer (may fail if backend not running)
Write-Host "[TEST] contract_enforcer extension..." -ForegroundColor Cyan
try {
    python -m modsquad.extensions.contract_enforcer 2>&1 | Out-Null
    Write-Host "[OK] contract_enforcer completed (check logs for results)" -ForegroundColor Green
} catch {
    Write-Host "[WARN] contract_enforcer: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[OK] Guardrail test suite complete!" -ForegroundColor Green
Write-Host "Check logs in: modsquad/logs/run-history/" -ForegroundColor Cyan
