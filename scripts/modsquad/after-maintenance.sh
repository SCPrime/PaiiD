#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: after-maintenance.sh --window <id> [--status <status>] [--metrics-json file] [--details-json file] [--verify]

Runs the MOD SQUAD extension suite (notifier, metrics streamer, secrets watchdog, optional strategy verifier)
after a maintenance batch completes.
EOF
}

WINDOW=""
STATUS="complete"
METRICS=""
DETAILS=""
VERIFY=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --window)
      WINDOW="$2"; shift 2 ;;
    --status)
      STATUS="$2"; shift 2 ;;
    --metrics-json)
      METRICS="$2"; shift 2 ;;
    --details-json)
      DETAILS="$2"; shift 2 ;;
    --verify)
      VERIFY=1; shift ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1 ;;
  esac
done

if [[ -z "$WINDOW" ]]; then
  echo "--window is required" >&2
  usage
  exit 1
fi

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"

PYTHON_BIN="${PYTHON:-python}"

CMD=("$PYTHON_BIN" "-m" "modsquad.extensions.runner" "after-maintenance" "--window" "$WINDOW" "--status" "$STATUS")

if [[ -n "$METRICS" ]]; then
  CMD+=("--metrics-json" "$(realpath "$METRICS")")
fi

if [[ -n "$DETAILS" ]]; then
  CMD+=("--details-json" "$(realpath "$DETAILS")")
fi

if [[ $VERIFY -eq 1 ]]; then
  CMD+=("--verify")
fi

"${CMD[@]}"

