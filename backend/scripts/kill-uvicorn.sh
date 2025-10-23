#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=_uvicorn_port_utils.sh
. "$SCRIPT_DIR/_uvicorn_port_utils.sh"

print_usage() {
  cat <<USAGE
Usage: $(basename "$0") [--quiet]

Terminates uvicorn processes that are bound to the development backend ports
(8001 and 8002). The script attempts a graceful shutdown (SIGTERM) before
falling back to SIGKILL if the process does not exit.

Options:
  -q, --quiet   Only print messages when a process is terminated.
  -h, --help    Show this help message.
USAGE
}

QUIET=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    -q|--quiet)
      QUIET=1
      ;;
    -h|--help)
      print_usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      print_usage >&2
      exit 1
      ;;
  esac
  shift
done

if ! has_port_inspector; then
  if [ "$QUIET" -eq 0 ]; then
    echo "⚠️  No supported network inspection utilities (lsof/ss/netstat) found."
    echo "    Skipping uvicorn cleanup."
  fi
  exit 0
fi

PORTS="8001 8002"
HANDLED=""
KILLED=0

for port in $PORTS; do
  pids_raw=$(list_uvicorn_pids "$port" || true)
  pids_clean=$(printf "%s\n" "$pids_raw" | tr ' ' '\n' | awk '/^[0-9]+$/')

  if [ -z "$pids_clean" ]; then
    if [ "$QUIET" -eq 0 ]; then
      echo "No uvicorn processes detected on port $port."
    fi
    continue
  fi

  for pid in $pids_clean; do
    case " $HANDLED " in
      *" $pid "*)
        continue
        ;;
    esac

    cmd=$(command_for_pid "$pid")
    if [ "$QUIET" -eq 0 ]; then
      if [ -n "$cmd" ]; then
        echo "Terminating uvicorn process $pid ($cmd)..."
      else
        echo "Terminating uvicorn process $pid..."
      fi
    fi

    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
      sleep 1
      if kill -0 "$pid" 2>/dev/null; then
        if [ "$QUIET" -eq 0 ]; then
          echo "Process $pid did not exit after SIGTERM; sending SIGKILL." >&2
        fi
        kill -9 "$pid" 2>/dev/null || true
      fi
    fi

    if kill -0 "$pid" 2>/dev/null; then
      if [ "$QUIET" -eq 0 ]; then
        echo "❌ Failed to terminate process $pid." >&2
      fi
    else
      if [ "$QUIET" -eq 0 ]; then
        echo "✅ Process $pid terminated."
      fi
      KILLED=1
    fi

    HANDLED="$HANDLED $pid"
  done
done

if [ "$KILLED" -eq 0 ] && [ "$QUIET" -eq 0 ]; then
  echo "No uvicorn processes required termination."
elif [ "$KILLED" -eq 1 ] && [ "$QUIET" -eq 0 ]; then
  echo "Cleanup complete."
fi
