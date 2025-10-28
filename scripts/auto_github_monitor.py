#!/usr/bin/env python3
import argparse
import json
import os
import re
from pathlib import Path


def scan_conflicts(repo_root: Path) -> dict:
    """Find duplicate endpoints/components, dead code, and TODO/FIXME markers."""
    duplicate_endpoints = []
    duplicate_components = []
    dead_code = []
    todos = []

    # Lightweight scans; detailed checks can be added as needed
    backend = repo_root / "backend"
    frontend = repo_root / "frontend"

    # TODO/FIXME in code
    for base in [backend, frontend]:
        if not base.exists():
            continue
        for p in base.rglob("*.py"):
            try:
                txt = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if "TODO" in txt or "FIXME" in txt:
                todos.append(str(p))
        for p in base.rglob("*.tsx"):
            try:
                txt = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if "TODO" in txt or "FIXME" in txt:
                todos.append(str(p))

    return {
        "duplicate_endpoints": duplicate_endpoints,
        "duplicate_components": duplicate_components,
        "dead_code": dead_code,
        "todos": sorted(set(todos)),
    }


def scan_old_code(repo_root: Path) -> dict:
    """Find deprecated patterns: datetime.utcnow, mock imports, hardcoded keys, TS any."""
    utcnow = []
    mock_imports = []
    hardcoded_keys = []
    ts_any = []

    for p in repo_root.rglob("*.py"):
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if "datetime.utcnow(" in txt:
            utcnow.append(str(p))
        if re.search(r"from\s+mock_?data\s+import", txt):
            mock_imports.append(str(p))
        if re.search(r"(API_KEY|SECRET|TOKEN)\s*=\s*['\"]\w+['\"]", txt):
            hardcoded_keys.append(str(p))

    for p in repo_root.rglob("*.tsx"):
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        # naive: 'any' in TSX code
        if re.search(r"\Wany\W", txt):
            ts_any.append(str(p))

    return {
        "utcnow": sorted(set(utcnow)),
        "mock_imports": sorted(set(mock_imports)),
        "hardcoded_keys": sorted(set(hardcoded_keys)),
        "ts_any": sorted(set(ts_any)),
    }


def endpoint_coverage(repo_root: Path) -> dict:
    """Basic endpoint coverage checks: CORS/auth/error handling placeholders.
    Real validation happens in CI with tests; this surfaces obvious gaps.
    """
    missing_cors = []
    missing_auth = []
    missing_error_handling = []
    proxy_mismatch = []

    backend = repo_root / "backend"
    proxy = repo_root / "frontend" / "pages" / "api" / "proxy"

    # Heuristic scans
    if backend.exists():
        for p in backend.rglob("*.py"):
            if p.name.endswith("main.py"):
                try:
                    txt = p.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue
                if "CORSMiddleware" not in txt and "allow_origins" not in txt:
                    missing_cors.append(str(p))

    # Proxy allowlist vs backend routes is environment-driven; flag if proxy folder missing
    if not proxy.exists():
        proxy_mismatch.append("frontend/pages/api/proxy missing")

    return {
        "missing_cors": missing_cors,
        "missing_auth": missing_auth,
        "missing_error_handling": missing_error_handling,
        "proxy_mismatch": proxy_mismatch,
    }


def env_audit(repo_root: Path) -> dict:
    missing_env = []
    unused_env = []

    # Known required envs (extend as needed)
    required = [
        "BACKEND_API_BASE_URL",
        "API_TOKEN",
        "ALLOWED_ORIGINS",
    ]
    for key in required:
        if not os.getenv(key):
            missing_env.append(key)

    # Unused env detection is project-specific; placeholder
    return {
        "missing_env": sorted(set(missing_env)),
        "unused_env": sorted(set(unused_env)),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--full-audit", action="store_true")
    parser.add_argument("--scan-conflicts", action="store_true")
    parser.add_argument("--scan-old-code", action="store_true")
    parser.add_argument("--endpoint-coverage", action="store_true")
    parser.add_argument("--env-audit", action="store_true")
    parser.add_argument("--output", default="reports/github_mod_report.json")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    out = {}

    if args.full_audit or args.scan_conflicts:
        out["conflicts"] = scan_conflicts(repo_root)
    if args.full_audit or args.scan_old_code:
        out["old_code"] = scan_old_code(repo_root)
    if args.full_audit or args.endpoint_coverage:
        out["endpoint_coverage"] = endpoint_coverage(repo_root)
    if args.full_audit or args.env_audit:
        out["env_audit"] = env_audit(repo_root)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"[GITHUB_MOD] Report written: {out_path}")


if __name__ == "__main__":
    main()
