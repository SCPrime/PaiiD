#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SPEC_DIR="$REPO_ROOT/infrastructure"

if ! command -v render >/dev/null 2>&1; then
  echo "The Render CLI (render) must be installed and on your PATH." >&2
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "jq is required to inspect the Render API responses." >&2
  exit 1
fi

if [[ ! -d "$SPEC_DIR" ]]; then
  echo "No infrastructure specs found at $SPEC_DIR" >&2
  exit 1
fi

# Ensure we have the latest origin/main reference
git fetch origin main --quiet
main_commit="$(git rev-parse origin/main)"

echo "Expected commit: $main_commit"

status=0

extract_commit() {
  jq -r '
    [
      .. | objects
         | to_entries[]
         | select(.key | test("commit"; "i"))
         | .value
         | if type == "object" then (.id // .sha // .hash // .commitId // .commit // empty) else . end
         | select(type == "string" and test("^[0-9a-f]{7,40}$"))
    ][0] // empty
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

  echo "Checking latest deployment commit for $service"
  latest_commit="$(render services get "$service" --json | extract_commit)"

  if [[ -z "$latest_commit" ]]; then
    echo "Unable to determine the deployed commit for $service" >&2
    status=1
    continue
  fi

  echo " - Latest deployed commit: $latest_commit"
  if [[ "$latest_commit" != "$main_commit" ]]; then
    echo "Deployment commit mismatch for $service" >&2
    status=1
  else
    echo " - Matches origin/main"
  fi
done

exit $status
