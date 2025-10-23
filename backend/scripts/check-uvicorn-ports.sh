#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=_uvicorn_port_utils.sh
. "$SCRIPT_DIR/_uvicorn_port_utils.sh"

if ! has_port_inspector; then
  echo "⚠️  Skipping uvicorn port check: no supported inspection tools found (lsof/ss/netstat)."
  exit 0
fi

PORTS="8001 8002"
STATUS=0

for port in $PORTS; do
  pids_raw=$(list_uvicorn_pids "$port" || true)
  pids_clean=$(printf "%s\n" "$pids_raw" | tr ' ' '\n' | awk '/^[0-9]+$/')

  if [ -z "$pids_clean" ]; then
    echo "✅ No uvicorn processes detected on port $port."
    continue
  fi

  count=$(printf "%s\n" "$pids_clean" | wc -l | tr -d ' ')

  if [ "$count" -gt 1 ]; then
    echo "❌ Detected $count uvicorn processes listening on port $port:"
    for pid in $pids_clean; do
      cmd=$(command_for_pid "$pid")
      if [ -n "$cmd" ]; then
        echo "   - PID $pid :: $cmd"
      else
        echo "   - PID $pid"
      fi
    done
    STATUS=1
  else
    pid=$(printf "%s\n" "$pids_clean" | head -n 1)
    cmd=$(command_for_pid "$pid")
    if [ -n "$cmd" ]; then
      echo "✅ Port $port has a single uvicorn process (PID $pid :: $cmd)."
    else
      echo "✅ Port $port has a single uvicorn process (PID $pid)."
    fi
  fi
done

exit $STATUS
