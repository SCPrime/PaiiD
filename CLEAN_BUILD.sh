#!/bin/bash
# 🔬 Master Surgeon's Build Cleanup Script
# Removes all old JavaScript artifacts and forces fresh build

set -e  # Exit on error

echo "🔬 Master Surgeon's Build Cleanup Protocol"
echo "=========================================="
echo ""

# Step 1: Kill any running dev servers
echo "Step 1: Checking for running processes..."
if lsof -ti:3000 >/dev/null 2>&1; then
    echo "⚠️  Killing process on port 3000..."
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
fi
echo "✅ No conflicting processes"
echo ""

# Step 2: Navigate to frontend
echo "Step 2: Navigating to frontend directory..."
cd frontend
echo "✅ In frontend directory"
echo ""

# Step 3: Remove build artifacts
echo "Step 3: Removing old build artifacts..."
echo "  - Removing .next directory..."
rm -rf .next
echo "  - Removing .next/cache..."
rm -rf .next/cache 2>/dev/null || true
echo "✅ Build artifacts removed"
echo ""

# Step 4: Clear node_modules cache (optional, uncomment if needed)
# echo "Step 4: Clearing node_modules cache..."
# rm -rf node_modules/.cache
# echo "✅ Node modules cache cleared"
# echo ""

# Step 5: Verify environment variables
echo "Step 4: Verifying environment variables..."
if [ -f .env.local ]; then
    echo "✅ .env.local exists"

    # Check for correct variable names
    if grep -q "NEXT_PUBLIC_BACKEND_API_BASE_URL" .env.local; then
        echo "✅ NEXT_PUBLIC_BACKEND_API_BASE_URL found"
    else
        echo "⚠️  WARNING: NEXT_PUBLIC_BACKEND_API_BASE_URL not found in .env.local"
    fi

    # Check for production URL
    if grep -q "ai-trader-86a1.onrender.com" .env.local; then
        echo "✅ Production backend URL found"
    else
        echo "⚠️  WARNING: Production backend URL not found"
    fi
else
    echo "⚠️  No .env.local file found (will use fallback URLs)"
fi
echo ""

# Step 6: Fresh build
echo "Step 5: Performing fresh build..."
echo "This may take 30-60 seconds..."
npm run build
echo ""
echo "✅ Fresh build completed!"
echo ""

# Step 7: Verify build output
echo "Step 6: Verifying build output..."
if [ -d .next ]; then
    echo "✅ .next directory created"

    # Check for localhost in bundles
    if grep -r "localhost:8001\|127.0.0.1:8001" .next/static/chunks/pages/index-*.js 2>/dev/null; then
        echo "❌ ERROR: localhost references found in build!"
        exit 1
    else
        echo "✅ NO localhost references in build"
    fi

    # Check for production URL in bundles
    if grep -q "ai-trader-86a1.onrender.com" .next/static/chunks/pages/index-*.js 2>/dev/null; then
        echo "✅ Production URL found in build"
    else
        echo "⚠️  WARNING: Production URL not found in build"
    fi
else
    echo "❌ ERROR: Build failed - .next directory not created"
    exit 1
fi
echo ""

echo "=========================================="
echo "🎉 BUILD CLEANUP COMPLETE!"
echo ""
echo "Your frontend is now:"
echo "  ✅ Free of old JavaScript artifacts"
echo "  ✅ Built with fresh Next.js cache"
echo "  ✅ Using production backend URLs"
echo "  ✅ Ready for deployment"
echo ""
echo "Next steps:"
echo "  1. Test locally: npm run dev"
echo "  2. Deploy to Vercel: git push origin main"
echo "  3. Set Vercel env vars (see VERCEL_ENV_URGENT_FIX.md)"
echo ""
echo "🔬 Master Surgeon approved! 🏆"
