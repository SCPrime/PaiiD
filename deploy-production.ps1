# 🚀 PaiiD Production Deployment Script
# Batch 5D: Deploy to Production

Write-Host "🚀 Starting PaiiD Production Deployment..." -ForegroundColor Green

# Step 1: Verify we're on main branch
Write-Host "📋 Step 1: Verifying branch..." -ForegroundColor Yellow
$currentBranch = git branch --show-current
if ($currentBranch -ne "main") {
    Write-Host "❌ Not on main branch. Current: $currentBranch" -ForegroundColor Red
    Write-Host "Please switch to main branch first: git checkout main" -ForegroundColor Red
    exit 1
}
Write-Host "✅ On main branch: $currentBranch" -ForegroundColor Green

# Step 2: Pull latest changes
Write-Host "📥 Step 2: Pulling latest changes..." -ForegroundColor Yellow
git pull origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to pull latest changes" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Latest changes pulled" -ForegroundColor Green

# Step 3: Check for uncommitted changes
Write-Host "🔍 Step 3: Checking for uncommitted changes..." -ForegroundColor Yellow
$status = git status --porcelain
if ($status) {
    Write-Host "❌ Uncommitted changes detected:" -ForegroundColor Red
    Write-Host $status -ForegroundColor Red
    Write-Host "Please commit or stash changes before deploying" -ForegroundColor Red
    exit 1
}
Write-Host "✅ No uncommitted changes" -ForegroundColor Green

# Step 4: Verify backend requirements
Write-Host "🐍 Step 4: Verifying backend requirements..." -ForegroundColor Yellow
if (Test-Path "backend/requirements.txt") {
    Write-Host "✅ Backend requirements.txt found" -ForegroundColor Green
} else {
    Write-Host "❌ Backend requirements.txt not found" -ForegroundColor Red
    exit 1
}

# Step 5: Verify frontend configuration
Write-Host "⚛️ Step 5: Verifying frontend configuration..." -ForegroundColor Yellow
if (Test-Path "frontend/package.json") {
    Write-Host "✅ Frontend package.json found" -ForegroundColor Green
} else {
    Write-Host "❌ Frontend package.json not found" -ForegroundColor Red
    exit 1
}

if (Test-Path "frontend/Dockerfile") {
    Write-Host "✅ Frontend Dockerfile found" -ForegroundColor Green
} else {
    Write-Host "❌ Frontend Dockerfile not found" -ForegroundColor Red
    exit 1
}

# Step 6: Verify render.yaml
Write-Host "📋 Step 6: Verifying render.yaml..." -ForegroundColor Yellow
if (Test-Path "render.yaml") {
    Write-Host "✅ render.yaml found" -ForegroundColor Green
} else {
    Write-Host "❌ render.yaml not found" -ForegroundColor Red
    exit 1
}

# Step 7: Display deployment instructions
Write-Host "`n🚀 DEPLOYMENT READY!" -ForegroundColor Green
Write-Host "`n📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Go to https://render.com" -ForegroundColor White
Write-Host "2. Create new Web Service" -ForegroundColor White
Write-Host "3. Connect GitHub repository: SCPrime/PaiiD" -ForegroundColor White
Write-Host "4. Select branch: main" -ForegroundColor White
Write-Host "5. For Backend: Root directory = backend" -ForegroundColor White
Write-Host "6. For Frontend: Root directory = frontend, Runtime = Docker" -ForegroundColor White
Write-Host "`n📖 See PRODUCTION_DEPLOYMENT_GUIDE.md for detailed instructions" -ForegroundColor Cyan

# Step 8: Tag release
Write-Host "`n🏷️ Step 8: Tagging release..." -ForegroundColor Yellow
$tagName = "v1.0.0"
$tagMessage = "Production launch - Options trading platform"

git tag -a $tagName -m $tagMessage
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Tag $tagName created" -ForegroundColor Green
    git push origin $tagName
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Tag $tagName pushed to remote" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Failed to push tag to remote" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️ Failed to create tag" -ForegroundColor Yellow
}

Write-Host "`n🎉 DEPLOYMENT PREPARATION COMPLETE!" -ForegroundColor Green
Write-Host "Ready for production deployment to Render!" -ForegroundColor Green
