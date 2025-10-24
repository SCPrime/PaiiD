#!/usr/bin/env bash
set -euo pipefail

SKIP_RENDER=false
SKIP_VERCEL=false
SKIP_CHECKS=false

for arg in "$@"; do
  case "$arg" in
    --skip-render) SKIP_RENDER=true ;;
    --skip-vercel) SKIP_VERCEL=true ;;
    --skip-checks) SKIP_CHECKS=true ;;
    *) echo "Unknown flag: $arg" >&2; exit 1 ;;
  esac
done

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

function log() {
  printf '%s %s\n' "[$(date '+%Y-%m-%dT%H:%M:%S%z')]" "$*"
}

function require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    log "❌ Required command '$1' not found"
    exit 1
  fi
}

if [[ ! -f .env ]]; then
  log "❌ .env file not found in repository root"
  exit 1
fi

if [[ "$SKIP_CHECKS" == "false" ]]; then
  require_command git
  require_command python
  require_command curl
  if [[ "$SKIP_VERCEL" == "false" ]]; then
    require_command vercel
  fi
  log "🔍 Running pre-launch validator"
  (cd backend && python -m app.core.prelaunch)
fi

# shellcheck disable=SC1091
set -a
source .env
set +a

BACKEND_URL=${NEXT_PUBLIC_BACKEND_API_BASE_URL:-${NEXT_PUBLIC_API_BASE_URL:-""}}
FRONTEND_URL=${ALLOW_ORIGIN:-""}

log "🚀 Deploying PaiiD platform"
log "   Branch: $(git branch --show-current)"

log "📤 Pushing latest commits"
git push origin "$(git branch --show-current)"

if [[ "$SKIP_RENDER" == "false" ]]; then
  log "🛠  Deploying backend to Render (manual trigger required)"
  log "   Ensure Render service uses start command: bash start.sh"
  log "   Required env vars: API_TOKEN, TRADIER_API_KEY, SENTRY_DSN, ENVIRONMENT=production"
fi

if [[ "$SKIP_VERCEL" == "false" ]]; then
  log "🎨 Deploying frontend to Vercel"
  pushd frontend >/dev/null
  npm install --silent
  npm run build
  vercel --prod --yes
  popd >/dev/null
fi

if [[ -n "$BACKEND_URL" ]]; then
  log "🧪 Smoke test: backend health"
  if command -v jq >/dev/null 2>&1; then
    curl --fail --silent --show-error "$BACKEND_URL/api/health" | jq '.'
  else
    curl --fail --silent --show-error "$BACKEND_URL/api/health" >/dev/null
    log "⚠️ jq not installed; showing raw response suppressed"
  fi
fi

if [[ -n "$FRONTEND_URL" ]]; then
  log "🧪 Smoke test: frontend"
  curl --fail --silent --show-error "$FRONTEND_URL" >/dev/null && log "Frontend reachable"
fi

log "✅ Deployment workflow complete"
