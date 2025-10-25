# Check Cursor Extensions and Development Environment
# This script helps verify your Cursor setup and extensions

Write-Host "🔍 Checking Cursor Extensions and Development Environment..." -ForegroundColor Cyan
Write-Host ""

# Check if Cursor is installed
$cursorPath = Get-Command cursor -ErrorAction SilentlyContinue
if ($cursorPath) {
    Write-Host "✅ Cursor CLI found at: $($cursorPath.Source)" -ForegroundColor Green
} else {
    Write-Host "❌ Cursor CLI not found. Please install Cursor or add it to PATH" -ForegroundColor Red
}

# Check for common development extensions
Write-Host ""
Write-Host "📦 Checking for recommended extensions..." -ForegroundColor Yellow

$recommendedExtensions = @(
    "ms-vscode.vscode-typescript-next",
    "bradlc.vscode-tailwindcss", 
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-eslint",
    "ms-vscode.vscode-json",
    "ms-vscode.vscode-python",
    "ms-vscode.vscode-git",
    "GitHub.copilot",
    "GitHub.copilot-chat",
    "ms-vscode.vscode-github-actions"
)

foreach ($extension in $recommendedExtensions) {
    $extensionPath = "$env:USERPROFILE\.cursor\extensions\$extension*"
    if (Test-Path $extensionPath) {
        Write-Host "✅ $extension" -ForegroundColor Green
    } else {
        Write-Host "❌ $extension (not installed)" -ForegroundColor Red
    }
}

# Check Node.js and npm
Write-Host ""
Write-Host "🟢 Checking Node.js environment..." -ForegroundColor Yellow

$nodeVersion = node --version 2>$null
if ($nodeVersion) {
    Write-Host "✅ Node.js: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Node.js not found" -ForegroundColor Red
}

$npmVersion = npm --version 2>$null
if ($npmVersion) {
    Write-Host "✅ npm: $npmVersion" -ForegroundColor Green
} else {
    Write-Host "❌ npm not found" -ForegroundColor Red
}

# Check Python
Write-Host ""
Write-Host "🐍 Checking Python environment..." -ForegroundColor Yellow

$pythonVersion = python --version 2>$null
if ($pythonVersion) {
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Python not found" -ForegroundColor Red
}

# Check Git
Write-Host ""
Write-Host "📝 Checking Git..." -ForegroundColor Yellow

$gitVersion = git --version 2>$null
if ($gitVersion) {
    Write-Host "✅ Git: $gitVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Git not found" -ForegroundColor Red
}

# Check project dependencies
Write-Host ""
Write-Host "📦 Checking project dependencies..." -ForegroundColor Yellow

if (Test-Path "package.json") {
    Write-Host "✅ package.json found" -ForegroundColor Green
    
    if (Test-Path "node_modules") {
        Write-Host "✅ node_modules directory exists" -ForegroundColor Green
    } else {
        Write-Host "❌ node_modules not found. Run 'npm install'" -ForegroundColor Red
    }
} else {
    Write-Host "❌ package.json not found" -ForegroundColor Red
}

if (Test-Path "requirements.txt") {
    Write-Host "✅ requirements.txt found" -ForegroundColor Green
} else {
    Write-Host "❌ requirements.txt not found" -ForegroundColor Red
}

# Check GitHub Actions
Write-Host ""
Write-Host "🔧 Checking GitHub Actions..." -ForegroundColor Yellow

if (Test-Path ".github/workflows") {
    $workflowFiles = Get-ChildItem ".github/workflows" -Filter "*.yml" -ErrorAction SilentlyContinue
    if ($workflowFiles) {
        Write-Host "✅ Found $($workflowFiles.Count) workflow files:" -ForegroundColor Green
        foreach ($file in $workflowFiles) {
            Write-Host "   - $($file.Name)" -ForegroundColor Cyan
        }
    } else {
        Write-Host "❌ No workflow files found" -ForegroundColor Red
    }
} else {
    Write-Host "❌ .github/workflows directory not found" -ForegroundColor Red
}

# Check environment variables
Write-Host ""
Write-Host "🔐 Checking environment variables..." -ForegroundColor Yellow

$envVars = @("NEXT_PUBLIC_BACKEND_API_BASE_URL", "NEXT_PUBLIC_WS_URL", "NODE_ENV")
foreach ($var in $envVars) {
    if ([Environment]::GetEnvironmentVariable($var)) {
        Write-Host "✅ $var is set" -ForegroundColor Green
    } else {
        Write-Host "❌ $var is not set" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "🎯 Summary:" -ForegroundColor Cyan
Write-Host "   - Use Ctrl+Shift+P to open Command Palette" -ForegroundColor White
Write-Host "   - Use Ctrl+K for AI chat" -ForegroundColor White
Write-Host "   - Use Ctrl+Shift+A for admin bypass" -ForegroundColor White
Write-Host "   - Check Extensions tab in Cursor for missing extensions" -ForegroundColor White
Write-Host "   - GitHub Actions Monitor is now available in the radial menu!" -ForegroundColor Green

Write-Host ""
Write-Host "🚀 Ready to develop! Your GitHub Actions Monitor is set up." -ForegroundColor Green
