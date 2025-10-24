#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIRS=("backend/.run" "frontend/.run")

status=0

for dir in "${RUN_DIRS[@]}"; do
  abs="${ROOT_DIR}/${dir}"
  [[ -d "$abs" ]] || continue

  for pid_file in "$abs"/*.pid; do
    [[ -e "$pid_file" ]] || continue
    pid=$(tr -d '[:space:]' < "$pid_file" || true)
    name=$(basename "$pid_file")

    if [[ -z "$pid" || ! "$pid" =~ ^[0-9]+$ ]]; then
      echo "[VALIDATION] Invalid PID in $pid_file"
      status=1
      continue
    fi

    if ! ps -p "$pid" >/dev/null 2>&1; then
      echo "[VALIDATION] Stale PID file detected: $pid_file (PID $pid)"
      status=1
    else
      echo "[VALIDATION] $name is running (PID $pid)"
    fi
  done
done

exit $status
