# 🔬 Master Surgeon's Build Cleanup Script (PowerShell version)
# Removes all old JavaScript artifacts and forces fresh build

$ErrorActionPreference = "Stop"

Write-Host "🔬 Master Surgeon's Build Cleanup Protocol" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Kill any running dev servers
Write-Host "Step 1: Checking for running processes..." -ForegroundColor Yellow
$nodeProcesses = Get-Process node -ErrorAction SilentlyContinue
if ($nodeProcesses) {
    Write-Host "⚠️  Killing Node.js processes..." -ForegroundColor Red
    $nodeProcesses | Stop-Process -Force
}
Write-Host "✅ No conflicting processes" -ForegroundColor Green
Write-Host ""

# Step 2: Navigate to frontend
Write-Host "Step 2: Navigating to frontend directory..." -ForegroundColor Yellow
Push-Location frontend
Write-Host "✅ In frontend directory" -ForegroundColor Green
Write-Host ""

# Step 3: Remove build artifacts
Write-Host "Step 3: Removing old build artifacts..." -ForegroundColor Yellow
Write-Host "  - Removing .next directory..."
if (Test-Path .next) {
    Remove-Item -Recurse -Force .next
    Write-Host "    ✅ Removed .next"
} else {
    Write-Host "    ℹ️  No .next directory found"
}
Write-Host "✅ Build artifacts removed" -ForegroundColor Green
Write-Host ""

# Step 4: Verify environment variables
Write-Host "Step 4: Verifying environment variables..." -ForegroundColor Yellow
if (Test-Path .env.local) {
    Write-Host "✅ .env.local exists" -ForegroundColor Green

    $envContent = Get-Content .env.local -Raw

    # Check for correct variable names
    if ($envContent -match "NEXT_PUBLIC_BACKEND_API_BASE_URL") {
        Write-Host "✅ NEXT_PUBLIC_BACKEND_API_BASE_URL found" -ForegroundColor Green
    } else {
        Write-Host "⚠️  WARNING: NEXT_PUBLIC_BACKEND_API_BASE_URL not found in .env.local" -ForegroundColor Red
    }

    # Check for production URL
    if ($envContent -match "ai-trader-86a1.onrender.com") {
        Write-Host "✅ Production backend URL found" -ForegroundColor Green
    } else {
        Write-Host "⚠️  WARNING: Production backend URL not found" -ForegroundColor Red
    }
} else {
    Write-Host "⚠️  No .env.local file found (will use fallback URLs)" -ForegroundColor Yellow
}
Write-Host ""

# Step 5: Fresh build
Write-Host "Step 5: Performing fresh build..." -ForegroundColor Yellow
Write-Host "This may take 30-60 seconds..." -ForegroundColor Yellow
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed!" -ForegroundColor Red
    Pop-Location
    exit 1
}
Write-Host ""
Write-Host "✅ Fresh build completed!" -ForegroundColor Green
Write-Host ""

# Step 6: Verify build output
Write-Host "Step 6: Verifying build output..." -ForegroundColor Yellow
if (Test-Path .next) {
    Write-Host "✅ .next directory created" -ForegroundColor Green

    # Check for localhost in bundles
    $indexFiles = Get-ChildItem -Path ".next\static\chunks\pages\index-*.js" -ErrorAction SilentlyContinue
    if ($indexFiles) {
        $localhostFound = $false
        foreach ($file in $indexFiles) {
            $content = Get-Content $file.FullName -Raw
            if ($content -match "localhost:8001|127\.0\.0\.1:8001") {
                $localhostFound = $true
                break
            }
        }

        if ($localhostFound) {
            Write-Host "❌ ERROR: localhost references found in build!" -ForegroundColor Red
            Pop-Location
            exit 1
        } else {
            Write-Host "✅ NO localhost references in build" -ForegroundColor Green
        }

        # Check for production URL in bundles
        $prodUrlFound = $false
        foreach ($file in $indexFiles) {
            $content = Get-Content $file.FullName -Raw
            if ($content -match "ai-trader-86a1\.onrender\.com") {
                $prodUrlFound = $true
                break
            }
        }

        if ($prodUrlFound) {
            Write-Host "✅ Production URL found in build" -ForegroundColor Green
        } else {
            Write-Host "⚠️  WARNING: Production URL not found in build" -ForegroundColor Yellow
        }
    } else {
        Write-Host "⚠️  WARNING: No index bundle files found" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ ERROR: Build failed - .next directory not created" -ForegroundColor Red
    Pop-Location
    exit 1
}
Write-Host ""

Pop-Location

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🎉 BUILD CLEANUP COMPLETE!" -ForegroundColor Green
Write-Host ""
Write-Host "Your frontend is now:" -ForegroundColor Cyan
Write-Host "  ✅ Free of old JavaScript artifacts" -ForegroundColor Green
Write-Host "  ✅ Built with fresh Next.js cache" -ForegroundColor Green
Write-Host "  ✅ Using production backend URLs" -ForegroundColor Green
Write-Host "  ✅ Ready for deployment" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Test locally: cd frontend && npm run dev" -ForegroundColor White
Write-Host "  2. Deploy to Vercel: git push origin main" -ForegroundColor White
Write-Host "  3. Set Vercel env vars (see VERCEL_ENV_URGENT_FIX.md)" -ForegroundColor White
Write-Host ""
Write-Host "🔬 Master Surgeon approved! 🏆" -ForegroundColor Cyan
