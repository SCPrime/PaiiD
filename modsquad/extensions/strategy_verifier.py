"""Strategy verification harness for MOD SQUAD."""

from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from .utils import CONFIG_PATH, dump_jsonl, load_extension_config

ARTIFACT_DIR = CONFIG_PATH.parent.parent / "logs" / "run-history" / "strategy_verifier"


def run() -> None:
    """Execute verification commands sequentially."""

    config = load_extension_config()
    settings = config.get("strategy_verifier")
    if not settings.get("enabled", False):
        return

    commands: List[Dict[str, Any]] = settings.get("commands", [])
    results: List[Dict[str, Any]] = []

    for command in commands:
        run_cmd = command.get("run")
        name = command.get("name", run_cmd)
        if not run_cmd:
            continue
        completed = subprocess.run(run_cmd, shell=True, capture_output=True, text=True)
        artifact = record_artifact(name, completed.stdout, completed.stderr)
        results.append(
            {
                "name": name,
                "command": run_cmd,
                "returncode": completed.returncode,
                "artifact": artifact,
            }
        )

    dump_jsonl(
        ARTIFACT_DIR / "strategy_verifier.jsonl",
        {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "results": results,
        },
    )


def record_artifact(name: str, stdout: str, stderr: str) -> str:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    file_path = ARTIFACT_DIR / f"{name}-{timestamp}.log"
    with file_path.open("w", encoding="utf-8") as fh:
        fh.write(stdout)
        if stderr:
            fh.write("\n=== stderr ===\n")
            fh.write(stderr)
    prune_artifacts()
    return str(file_path)


def prune_artifacts() -> None:
    config = load_extension_config()
    keep = int(config.get("strategy_verifier").get("artifacts", {}).get("keep", 10))
    files = sorted(ARTIFACT_DIR.glob("*.log"))
    for excess in files[:-keep]:
        excess.unlink(missing_ok=True)


def cli() -> None:
    run()

