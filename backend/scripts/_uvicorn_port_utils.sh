#!/usr/bin/env bash

# Shared helpers for inspecting uvicorn processes bound to specific ports.
# These functions are intentionally POSIX-friendly so that they can be sourced
# by other scripts that run under both macOS and Linux environments.

has_port_inspector() {
  if command -v lsof >/dev/null 2>&1; then
    return 0
  fi
  if command -v ss >/dev/null 2>&1; then
    return 0
  fi
  if command -v netstat >/dev/null 2>&1; then
    return 0
  fi
  return 1
}

collect_listeners() {
  local port="$1"
  local results=""
  local tool_output=""
  local parsed=""

  if command -v lsof >/dev/null 2>&1; then
    tool_output=$(lsof -t -iTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)
    if [ -n "$tool_output" ]; then
      results="$results $(echo "$tool_output" | tr '\n' ' ')"
    fi
  fi

  if command -v ss >/dev/null 2>&1; then
    tool_output=$(ss -ltnp 2>/dev/null | awk -v port=":$port" '$4 ~ port' | grep -o 'pid=[0-9]*' | sed 's/pid=//' || true)
    if [ -n "$tool_output" ]; then
      results="$results $(echo "$tool_output" | tr '\n' ' ')"
    fi
  fi

  if command -v netstat >/dev/null 2>&1; then
    tool_output=$(netstat -nlp 2>/dev/null || true)
    if [ -n "$tool_output" ]; then
      parsed=$(printf "%s\n" "$tool_output" | awk -v port=":$port" '$4 ~ port && $6 == "LISTEN" {split($7,a,"/"); if (a[1] ~ /^[0-9]+$/) print a[1]}' || true)
      if [ -n "$parsed" ]; then
        results="$results $(echo "$parsed" | tr '\n' ' ')"
      fi
    fi
  fi

  echo "$results"
}

list_uvicorn_pids() {
  local port="$1"
  local candidates=""
  candidates=$(collect_listeners "$port")
  if [ -z "$candidates" ]; then
    return 0
  fi

  echo "$candidates" | tr ' ' '\n' | awk '/^[0-9]+$/' | sort -u | while read -r pid; do
    if [ -z "$pid" ]; then
      continue
    fi
    cmd=$(ps -p "$pid" -o command= 2>/dev/null || true)
    case "$cmd" in
      *uvicorn*)
        echo "$pid"
        ;;
    esac
  done
}

command_for_pid() {
  local pid="$1"
  ps -p "$pid" -o command= 2>/dev/null || true
}
