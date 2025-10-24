#!/usr/bin/env bash
set -euo pipefail

# Simple cleanup utility for CI jobs to ensure the environment is pristine
# before starting frontend/backend tests. The script removes stale PID files
# and terminates lingering dev servers that might interfere with port-based
# tests.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIRS=("backend/.logs" "frontend/.logs")
RUN_DIRS=("backend/.run" "frontend/.run")
PORTS=(3000 4000 5173 8000 8001)

cleanup_directories() {
  for dir in "${LOG_DIRS[@]}"; do
    abs="${ROOT_DIR}/${dir}"
    if [[ -d "$abs" ]]; then
      find "$abs" -type f ! -name '.gitkeep' -delete
    fi
  done

  for dir in "${RUN_DIRS[@]}"; do
    abs="${ROOT_DIR}/${dir}"
    if [[ -d "$abs" ]]; then
      find "$abs" -type f -name '*.pid' -delete
    fi
  done
}

kill_ports() {
  for port in "${PORTS[@]}"; do
    if lsof -ti tcp:"$port" >/dev/null 2>&1; then
      echo "[CI-CLEANUP] Terminating processes on port $port"
      lsof -ti tcp:"$port" | xargs -r kill -9 || true
    fi
  done
}

prune_defunct_processes() {
  if command -v ps >/dev/null 2>&1; then
    ps ax -o pid=,stat= | awk '$2 ~ /Z/' | awk '{print $1}' | xargs -r kill -9 || true
  fi
}

cleanup_directories
kill_ports
prune_defunct_processes

exit 0
