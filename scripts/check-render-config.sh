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

if [[ ! -d "$SPEC_DIR" ]]; then
  echo "No infrastructure specs found at $SPEC_DIR" >&2
  exit 1
fi

status=0

normalize_for_spec() {
  local spec_file="$1"
  jq --argjson spec "$(jq '.' "$spec_file")" '
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
    ($spec | keys_unsorted) as $keys |
    reduce $keys[] as $k ({}; . + {($k): lookup($k)})
  '
}

for spec in "$SPEC_DIR"/*.json; do
  [[ -e "$spec" ]] || continue
  service="$(jq -r '.service // empty' "$spec")"
  if [[ -z "$service" ]]; then
    echo "Spec $spec is missing the required 'service' property." >&2
    status=1
    continue
  fi

  echo "Checking Render configuration drift for $service"
  tmp_file="$(mktemp)"
  render services get "$service" --json >"$tmp_file"

  if ! diff -u <(jq -S '.' "$spec") <(normalize_for_spec "$spec" <"$tmp_file" | jq -S '.'); then
    echo "Configuration drift detected for $service" >&2
    status=1
  else
    echo "No drift detected for $service"
  fi

  rm -f "$tmp_file"
done

exit $status
