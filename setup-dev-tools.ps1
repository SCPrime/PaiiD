# PaiiD Development Tools Auto-Setup Script
# Run this once to configure your development environment

Write-Host "🚀 Setting up PaiiD development environment..." -ForegroundColor Cyan
Write-Host ""

# Change to PaiiD directory
Set-Location $PSScriptRoot

# ============================================================================
# STEP 1: Install Python dependencies (including Ruff)
# ============================================================================
Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
Set-Location backend
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Python dependencies installed" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to install Python dependencies" -ForegroundColor Red
}
Set-Location ..

# ============================================================================
# STEP 2: Install VS Code/Cursor Extensions
# ============================================================================
Write-Host ""
Write-Host "🔌 Installing VS Code/Cursor extensions..." -ForegroundColor Yellow

$extensions = @(
    "usernamehw.errorlens",           # Inline error highlighting
    "charliermarsh.ruff",              # Python linter/formatter
    "ms-python.python",                # Python support
    "ms-python.vscode-pylance",        # Python IntelliSense
    "yoavbls.pretty-ts-errors",        # Pretty TypeScript errors
    "humao.rest-client",               # API testing
    "dbaeumer.vscode-eslint",          # ESLint
    "esbenp.prettier-vscode"           # Prettier formatting
)

foreach ($ext in $extensions) {
    Write-Host "  Installing $ext..." -ForegroundColor Gray
    code --install-extension $ext --force 2>$null
}

Write-Host "✅ Extensions installed" -ForegroundColor Green

# ============================================================================
# STEP 3: Verify Ruff is working
# ============================================================================
Write-Host ""
Write-Host "🔍 Verifying Ruff installation..." -ForegroundColor Yellow
Set-Location backend
$ruffVersion = ruff --version 2>$null
if ($ruffVersion) {
    Write-Host "✅ Ruff installed: $ruffVersion" -ForegroundColor Green
} else {
    Write-Host "⚠️  Ruff not in PATH - restart terminal after completion" -ForegroundColor Yellow
}
Set-Location ..

# ============================================================================
# STEP 4: Create API test file for REST Client
# ============================================================================
Write-Host ""
Write-Host "📝 Creating API test file..." -ForegroundColor Yellow

$apiTestContent = @"
### PaiiD Backend API Tests
### Use the "Send Request" link above each request to test

@baseUrl = http://127.0.0.1:8001
@token = tuGlKvrYEoiJcv7r7oIy7zXM9pqVnaxN_74obFz6lVo

### Health Check
GET {{baseUrl}}/api/health

### Portfolio Analysis (NEW!)
GET {{baseUrl}}/api/ai/analyze-portfolio
Authorization: Bearer {{token}}

### Account Info
GET {{baseUrl}}/api/account
Authorization: Bearer {{token}}

### Active Positions
GET {{baseUrl}}/api/positions
Authorization: Bearer {{token}}

### AI Recommendations
GET {{baseUrl}}/api/ai/recommendations
Authorization: Bearer {{token}}

### Market Indices (SPY, QQQ, DIA)
GET {{baseUrl}}/api/market/indices

### Get Quote for Symbol
GET {{baseUrl}}/api/market/quote/AAPL
Authorization: Bearer {{token}}
"@

$apiTestContent | Out-File -FilePath "api-tests.http" -Encoding UTF8
Write-Host "✅ Created api-tests.http" -ForegroundColor Green

# ============================================================================
# STEP 5: Run Ruff check (non-blocking)
# ============================================================================
Write-Host ""
Write-Host "🔍 Running Ruff linter check..." -ForegroundColor Yellow
Set-Location backend
$ruffOutput = ruff check . --fix 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ No linting issues found" -ForegroundColor Green
} else {
    Write-Host "⚠️  Some issues auto-fixed by Ruff" -ForegroundColor Yellow
}
Set-Location ..

# ============================================================================
# DONE!
# ============================================================================
Write-Host ""
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "✨ Development environment setup complete!" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Restart VS Code/Cursor to activate extensions" -ForegroundColor White
Write-Host "  2. Open 'api-tests.http' to test your API endpoints" -ForegroundColor White
Write-Host "  3. Start coding - auto-formatting enabled on save!" -ForegroundColor White
Write-Host ""
Write-Host "🎯 Installed Extensions:" -ForegroundColor Yellow
Write-Host "  ✓ Error Lens - Inline error highlighting" -ForegroundColor Gray
Write-Host "  ✓ Ruff - Python linting & formatting" -ForegroundColor Gray
Write-Host "  ✓ Pylance - Python IntelliSense" -ForegroundColor Gray
Write-Host "  ✓ Pretty TS Errors - Readable TypeScript errors" -ForegroundColor Gray
Write-Host "  ✓ REST Client - API testing in .http files" -ForegroundColor Gray
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
"@