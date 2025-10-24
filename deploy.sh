#!/usr/bin/env bash
set -euo pipefail

SKIP_RENDER=false
SKIP_VERCEL=false
SKIP_CHECKS=false

usage() {
  cat <<USAGE
Usage: $(basename "$0") [--skip-render] [--skip-vercel] [--skip-checks]

Mirrors deploy.ps1 using POSIX shell so that macOS/Linux environments can
trigger the same workflow without PowerShell.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-render)
      SKIP_RENDER=true
      ;;
    --skip-vercel)
      SKIP_VERCEL=true
      ;;
    --skip-checks)
      SKIP_CHECKS=true
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
  shift
done

if [[ ! -f .env ]]; then
  echo "❌ .env file not found" >&2
  exit 1
fi

declare -A ENV_VARS
while IFS='=' read -r key value; do
  [[ -z "$key" ]] && continue
  value=${value%$'\r'}
  ENV_VARS["$key"]="$value"
done < <(grep -v '^#' .env)

BACKEND_URL=${ENV_VARS[NEXT_PUBLIC_API_BASE_URL]:-}
API_TOKEN=${ENV_VARS[API_TOKEN]:-}
VERCEL_URL=${ENV_VARS[ALLOW_ORIGIN]:-}

if [[ "$SKIP_CHECKS" == false ]]; then
  echo "✓ Pre-flight checks..."
  echo "  Checking branch hold points..."
  if ! python scripts/check_hold_points.py; then
    echo "  ❌ Branch hold point validation failed" >&2
    exit 1
  fi

  if ! git diff --quiet; then
    echo "⚠️  Uncommitted changes detected"
    git status -sb
    read -r -p "Continue anyway? (y/N) " response
    if [[ "$response" != "y" ]]; then
      exit 0
    fi
  fi

  CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
  echo "  Branch: $CURRENT_BRANCH"

  for cli in curl gh vercel; do
    if ! command -v "$cli" >/dev/null 2>&1; then
      echo "  ❌ Required CLI '$cli' not found" >&2
      exit 1
    fi
    echo "  ✓ $cli CLI found"
  done
fi

echo "\n📤 Pushing to GitHub..."
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if ! git push origin "$CURRENT_BRANCH"; then
  echo "❌ Git push failed" >&2
  exit 1
fi

echo "✓ Pushed to GitHub"

if [[ "$SKIP_RENDER" == false ]]; then
  echo "\n🔧 Deploying Backend to Render..."
  echo "   URL: ${BACKEND_URL:-<not-set>}"
  python infra/render/validate.py --service backend
  echo "   Manual steps:" 
  echo "     1. Visit https://dashboard.render.com"
  echo "     2. Trigger 'Deploy latest commit' on the backend service"
fi

if [[ "$SKIP_VERCEL" == false ]]; then
  echo "\n🎨 Deploying Frontend to Vercel..."
  echo "   URL: ${VERCEL_URL:-<not-set>}"
  (cd frontend && vercel --prod --yes)
fi

declare -a CHECKS=(
  "Backend Health|${BACKEND_URL%/}/api/health|healthy"
  "Frontend Proxy Health|${VERCEL_URL%/}/api/proxy/api/health|healthy"
)

echo "\n🧪 Running Smoke Tests..."
for check in "${CHECKS[@]}"; do
  IFS='|' read -r name url expected <<<"$check"
  [[ -z "$url" ]] && continue
  if response=$(curl -fsSL "$url"); then
    if [[ "$response" == *"$expected"* ]]; then
      echo "  ✓ $name"
    else
      echo "  ⚠️  $name responded but missing expected token ($expected)"
    fi
  else
    echo "  ❌ $name failed at $url"
  fi
  sleep 1
done

echo "\n✅ Deployment helper complete"
