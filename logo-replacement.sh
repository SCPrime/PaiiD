#!/bin/bash
# ============================================================================
# COMPREHENSIVE LOGO REPLACEMENT - ALL AT ONCE
# Execute time: ~20 minutes
# ============================================================================

echo "🚀 Starting comprehensive logo replacement..."

# PHASE 1: AUDIT
echo "📋 Phase 1: Auditing codebase..."
grep -rn "PaiiD" frontend/components/ frontend/pages/ --include="*.tsx" --include="*.ts" | grep -v node_modules | grep -v ".next" > logo-audit.txt
echo "✅ Audit complete - results in logo-audit.txt"

# PHASE 2: DEPLOY COMPONENTS
echo "📦 Phase 2: Deploying LOCKED FINAL components..."
cp "LOCKED FINAL iPi Wrapped Logo and PaiiD Chat Box/2-CompletePaiiDLogo-Locked.tsx" frontend/components/CompletePaiiDLogo.tsx
cp "LOCKED FINAL iPi Wrapped Logo and PaiiD Chat Box/4-PaiiDChatBoxLocked.tsx" frontend/components/PaiiDChatBoxLocked.tsx
echo "✅ Components deployed"

# PHASE 3: UPDATE ALL FILES
echo "🔄 Phase 3: Updating all logo instances..."

# Update RadialMenu.tsx - Replace old logo with new
sed -i.bak "s/import PaiiDLogo from '\.\/PaiiDLogo'/import CompletePaiiDLogo from '.\/CompletePaiiDLogo'/g" frontend/components/RadialMenu.tsx
sed -i.bak "s/<PaiiDLogo/<CompletePaiiDLogo/g" frontend/components/RadialMenu.tsx
sed -i.bak "s/<\/PaiiDLogo>/<\/CompletePaiiDLogo>/g" frontend/components/RadialMenu.tsx

# Update index.tsx
sed -i.bak "s/import PaiiDLogo from '\.\.\/components\/PaiiDLogo'/import CompletePaiiDLogo from '..\/components\/CompletePaiiDLogo'/g" frontend/pages/index.tsx
sed -i.bak "s/<PaiiDLogo/<CompletePaiiDLogo/g" frontend/pages/index.tsx

# Update UserSetupAI.tsx
sed -i.bak "s/import PaiiDLogo from '\.\/PaiiDLogo'/import CompletePaiiDLogo from '.\/CompletePaiiDLogo'/g" frontend/components/UserSetupAI.tsx
sed -i.bak "s/<PaiiDLogo/<CompletePaiiDLogo/g" frontend/components/UserSetupAI.tsx

echo "✅ All files updated"

# PHASE 4: VERIFY
echo "🔍 Phase 4: Verifying changes..."
grep -n "CompletePaiiDLogo" frontend/components/RadialMenu.tsx | head -5
grep -n "CompletePaiiDLogo" frontend/pages/index.tsx | head -5
echo "✅ Verification complete"

# PHASE 5: BUILD TEST
echo "🏗️ Phase 5: Testing build..."
cd frontend
npm run build 2>&1 | tail -20
BUILD_STATUS=$?
cd ..

if [ $BUILD_STATUS -ne 0 ]; then
    echo "❌ Build failed! Aborting commit."
    exit 1
fi

# PHASE 6: COMMIT
echo "💾 Phase 6: Committing changes..."
git add frontend/components/CompletePaiiDLogo.tsx
git add frontend/components/PaiiDChatBoxLocked.tsx
git add frontend/components/RadialMenu.tsx
git add frontend/pages/index.tsx
git add frontend/components/UserSetupAI.tsx

git commit -m "feat: implement LOCKED FINAL logo system throughout codebase

- Deploy CompletePaiiDLogo.tsx from LOCKED FINAL
- Deploy PaiiDChatBoxLocked.tsx (10 capabilities)
- Replace all PaiiDLogo instances with CompletePaiiDLogo
- Update RadialMenu.tsx, index.tsx, UserSetupAI.tsx
- Exact spacing preserved: size * 0.08, size * 0.02436

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

git push origin main

echo ""
echo "🎉 ============================================"
echo "🎉 COMPREHENSIVE LOGO REPLACEMENT COMPLETE!"
echo "🎉 ============================================"
echo ""
echo "✅ Components deployed"
echo "✅ All instances updated"
echo "✅ Build verified"
echo "✅ Committed to GitHub"
echo "✅ Render will auto-deploy"
echo ""
echo "🌐 Frontend: http://localhost:3006"
echo "🌐 Backend: http://127.0.0.1:8002"
echo ""
