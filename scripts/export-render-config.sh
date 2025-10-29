#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SPEC_DIR="$REPO_ROOT/infrastructure"

if ! command -v render >/dev/null 2>&1; then
  echo "The Render CLI (render) must be installed and on your PATH." >&2
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "jq is required to normalize the Render API responses." >&2
  exit 1
fi

mkdir -p "$SPEC_DIR"

render_normalize() {
  local keys_json="$1"
  jq --argjson keys "$keys_json" '
    def present:
      select(. != null and ((. | type) != "string" or . != ""));
    def findAny($keys):
      reduce $keys[] as $k (null;
        if . != null then .
        else ([.. | objects | select(has($k)) | .[$k]] | map(present) | first?)
        end
      );
    def lookup($key):
      if $key == "service" then findAny(["name", "serviceName"])
      elif $key == "branch" then findAny(["branch", "repoBranch"])
      elif $key == "rootDir" then findAny(["rootDir", "repoRootDir"])
      elif $key == "buildCommand" then findAny(["buildCommand"])
      elif $key == "startCommand" then findAny(["startCommand"])
      elif $key == "dockerfilePath" then findAny(["dockerfilePath"])
      elif $key == "dockerCommand" then findAny(["dockerCommand", "startCommand"])
      elif $key == "autoDeploy" then findAny(["autoDeploy", "autoDeployEnabled"])
      else findAny([$key])
      end;
    reduce $keys[] as $k ({}; . + {($k): lookup($k)})
      | with_entries(select(.value != null))
  '
}

export_service() {
  local service="$1"
  local target="$2"
  local default_keys_json="$3"

  local keys_json="$default_keys_json"
  if [[ -f "$target" ]]; then
    keys_json="$(jq -c 'keys_unsorted' "$target")"
  fi

  echo "Exporting $service configuration to $target"
  render services get "$service" --json \
    | render_normalize "$keys_json" \
    | jq -S '.' >"$target"
}

# Defaults for first-run exports
backend_keys='["service","autoDeploy","branch","rootDir","buildCommand","startCommand"]'
frontend_keys='["service","autoDeploy","branch","rootDir","dockerfilePath","dockerCommand"]'

export_service "paiid-backend" "$SPEC_DIR/paiid-backend.json" "$backend_keys"
export_service "paiid-frontend" "$SPEC_DIR/paiid-frontend.json" "$frontend_keys"
