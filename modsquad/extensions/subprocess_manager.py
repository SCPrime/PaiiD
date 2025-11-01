"""
Centralized subprocess management for MOD SQUAD extensions.
Reduces risk through standardized execution, timeouts, and error handling.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


@dataclass
class CommandResult:
    """Standardized command execution result."""
    success: bool
    returncode: int
    stdout: str
    stderr: str
    command: str
    skipped: bool = False
    skip_reason: Optional[str] = None


def check_binary_exists(binary: str) -> bool:
    """Check if a binary/command exists in PATH."""
    return shutil.which(binary) is not None


def run_command(
    command: Union[str, List[str]],
    timeout: int = 120,
    cwd: Optional[Path] = None,
    required_binary: Optional[str] = None,
    check_binary: bool = True,
    env: Optional[Dict[str, str]] = None,
) -> CommandResult:
    """
    Execute command with safety checks and standardized error handling.

    Args:
        command: Command to execute (string or list)
        timeout: Maximum execution time in seconds
        cwd: Working directory for command
        required_binary: Binary that must exist (auto-detected if command is list)
        check_binary: Whether to check binary existence before running
        env: Environment variables to add/override

    Returns:
        CommandResult with execution details
    """
    # Auto-detect binary from command
    if required_binary is None and isinstance(command, list):
        required_binary = command[0]

    # Preflight check: verify binary exists
    if check_binary and required_binary:
        if not check_binary_exists(required_binary):
            return CommandResult(
                success=False,
                returncode=-1,
                stdout="",
                stderr=f"{required_binary} not installed",
                command=str(command),
                skipped=True,
                skip_reason=f"{required_binary} not found in PATH"
            )

    # Prepare environment
    run_env = os.environ.copy()
    if env:
        run_env.update(env)

    # Prepare subprocess kwargs
    run_kwargs: Dict[str, Any] = {
        "capture_output": True,
        "text": True,
        "timeout": timeout,
        "env": run_env,
    }

    if cwd:
        run_kwargs["cwd"] = str(cwd)

    # Handle shell mode for string commands
    if isinstance(command, str):
        run_kwargs["shell"] = True
        cmd_str = command
    else:
        cmd_str = " ".join(command)

    # Execute command
    try:
        completed = subprocess.run(command, **run_kwargs)
        return CommandResult(
            success=completed.returncode == 0,
            returncode=completed.returncode,
            stdout=completed.stdout[:5000],  # Limit output size
            stderr=completed.stderr[:500],
            command=cmd_str,
        )
    except subprocess.TimeoutExpired:
        return CommandResult(
            success=False,
            returncode=-2,
            stdout="",
            stderr=f"Command timed out after {timeout}s",
            command=cmd_str,
        )
    except FileNotFoundError as e:
        return CommandResult(
            success=False,
            returncode=-3,
            stdout="",
            stderr=f"Command not found: {e}",
            command=cmd_str,
            skipped=True,
            skip_reason="Binary not found"
        )
    except Exception as e:
        return CommandResult(
            success=False,
            returncode=-4,
            stdout="",
            stderr=f"Unexpected error: {str(e)}",
            command=cmd_str,
        )


def run_npm_command(
    args: List[str],
    timeout: int = 120,
    cwd: Optional[Path] = None,
) -> CommandResult:
    """Execute npm command with automatic binary detection."""
    npm_binary = "npm.cmd" if os.name == "nt" else "npm"
    return run_command(
        [npm_binary] + args,
        timeout=timeout,
        cwd=cwd,
        required_binary="npm"
    )


def run_npx_command(
    args: List[str],
    timeout: int = 120,
    cwd: Optional[Path] = None,
) -> CommandResult:
    """Execute npx command with automatic binary detection."""
    npx_binary = "npx.cmd" if os.name == "nt" else "npx"
    return run_command(
        [npx_binary] + args,
        timeout=timeout,
        cwd=cwd,
        required_binary="npx"
    )


def run_python_command(
    args: List[str],
    timeout: int = 120,
    cwd: Optional[Path] = None,
) -> CommandResult:
    """Execute Python command."""
    return run_command(
        ["python"] + args,
        timeout=timeout,
        cwd=cwd,
        required_binary="python"
    )


def run_git_command(
    args: List[str],
    timeout: int = 30,
    cwd: Optional[Path] = None,
) -> CommandResult:
    """Execute git command."""
    return run_command(
        ["git"] + args,
        timeout=timeout,
        cwd=cwd,
        required_binary="git"
    )


def run_docker_compose_command(
    args: List[str],
    compose_file: Optional[Path] = None,
    timeout: int = 60,
    cwd: Optional[Path] = None,
) -> CommandResult:
    """Execute docker compose command."""
    cmd = ["docker", "compose"]

    if compose_file:
        cmd.extend(["-f", str(compose_file)])

    cmd.extend(args)

    return run_command(
        cmd,
        timeout=timeout,
        cwd=cwd,
        required_binary="docker"
    )


__all__ = [
    "CommandResult",
    "check_binary_exists",
    "run_command",
    "run_npm_command",
    "run_npx_command",
    "run_python_command",
    "run_git_command",
    "run_docker_compose_command",
]
