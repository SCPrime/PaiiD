#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RENDER MOD - Render Environment Variable Validator
Prevents production deployment failures by validating all required environment variables.

Usage:
    python scripts/render_mod.py                    # Check current environment
    python scripts/render_mod.py --check-backend    # Backend validation only
    python scripts/render_mod.py --check-frontend   # Frontend validation only
    python scripts/render_mod.py --strict           # Fail on warnings
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Fix Windows console encoding
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
except ImportError:
    # Fallback to basic printing if rich not available
    class Console:
        def print(self, *args, **kwargs):
            print(*args)

    console = Console()
else:
    console = Console()


# Required environment variables for each service
REQUIRED_BACKEND_VARS = {
    "API_TOKEN": {
        "description": "Backend API authentication token",
        "example": "rnd_bDRqi1TvLvd3rC78yvUSgDraH2Kl",
        "severity": "CRITICAL"
    },
    "TRADIER_API_KEY": {
        "description": "Tradier API key for live market data",
        "example": "xxxxxxxxxxxxxxxxxxxxx",
        "severity": "CRITICAL"
    },
    "TRADIER_ACCOUNT_ID": {
        "description": "Tradier account ID",
        "example": "VA12345678",
        "severity": "CRITICAL"
    },
    "ALPACA_PAPER_API_KEY": {
        "description": "Alpaca Paper Trading API key",
        "example": "PKxxxxxxxxxxxxxxxxxxxx",
        "severity": "CRITICAL"
    },
    "ALPACA_PAPER_SECRET_KEY": {
        "description": "Alpaca Paper Trading secret key",
        "example": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "severity": "CRITICAL"
    },
    "ANTHROPIC_API_KEY": {
        "description": "Claude AI API key for recommendations",
        "example": "sk-ant-xxxxxxxxxxxxxxxxxxxxx",
        "severity": "HIGH"
    },
    "ALLOW_ORIGIN": {
        "description": "CORS allowed origin (frontend URL)",
        "example": "https://paiid-frontend.onrender.com",
        "severity": "HIGH",
        "optional": True
    },
    "DATABASE_URL": {
        "description": "PostgreSQL database connection string",
        "example": "postgresql://user:pass@host:5432/db",
        "severity": "MEDIUM",
        "optional": True
    }
}

REQUIRED_FRONTEND_VARS = {
    "NEXT_PUBLIC_API_TOKEN": {
        "description": "Backend API token (must match backend API_TOKEN)",
        "example": "rnd_bDRqi1TvLvd3rC78yvUSgDraH2Kl",
        "severity": "CRITICAL"
    },
    "NEXT_PUBLIC_BACKEND_API_BASE_URL": {
        "description": "Backend API base URL",
        "example": "https://paiid-backend.onrender.com",
        "severity": "CRITICAL"
    },
    "NEXT_PUBLIC_ANTHROPIC_API_KEY": {
        "description": "Claude AI API key for frontend chat",
        "example": "sk-ant-xxxxxxxxxxxxxxxxxxxxx",
        "severity": "HIGH",
        "optional": True
    }
}


class RenderMod:
    """Environment variable validation system for Render deployments"""

    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "backend": {"missing": [], "present": [], "warnings": []},
            "frontend": {"missing": [], "present": [], "warnings": []},
            "issues": []
        }

    def check_env_var(self, var_name: str, config: Dict) -> Tuple[bool, Optional[str]]:
        """
        Check if environment variable exists and validate its value.
        Returns (is_valid, warning_message)
        """
        value = os.getenv(var_name)

        if not value:
            return False, None

        # Basic validation checks
        warnings = []

        # Check for placeholder values
        if value.lower() in ["your-key", "xxxxx", "changeme", "todo", "null", "undefined"]:
            warnings.append(f"Looks like a placeholder value")

        # Check for minimum length (most API keys are >20 chars)
        if config.get("severity") == "CRITICAL" and len(value) < 10:
            warnings.append(f"Suspiciously short value ({len(value)} chars)")

        # Check for matching tokens between frontend/backend
        if var_name == "NEXT_PUBLIC_API_TOKEN":
            backend_token = os.getenv("API_TOKEN")
            if backend_token and value != backend_token:
                warnings.append("Does not match backend API_TOKEN")

        return True, warnings[0] if warnings else None

    def validate_backend(self) -> bool:
        """Validate backend environment variables"""
        console.print("\n[bold cyan]🔧 BACKEND ENVIRONMENT VALIDATION[/bold cyan]\n")

        all_valid = True

        for var_name, config in REQUIRED_BACKEND_VARS.items():
            is_present, warning = self.check_env_var(var_name, config)

            if not is_present:
                if not config.get("optional"):
                    self.results["backend"]["missing"].append({
                        "name": var_name,
                        "severity": config["severity"],
                        "description": config["description"]
                    })
                    severity_icon = "🔴" if config["severity"] == "CRITICAL" else "🟡"
                    console.print(f"{severity_icon} MISSING: [red]{var_name}[/red]")
                    console.print(f"   {config['description']}")
                    console.print(f"   Example: [dim]{config['example']}[/dim]\n")

                    if config["severity"] == "CRITICAL":
                        all_valid = False
                else:
                    console.print(f"ℹ️  OPTIONAL: [yellow]{var_name}[/yellow] not set")
            else:
                self.results["backend"]["present"].append(var_name)

                if warning:
                    self.results["backend"]["warnings"].append({
                        "name": var_name,
                        "warning": warning
                    })
                    console.print(f"⚠️  WARNING: [yellow]{var_name}[/yellow]: {warning}")

                    if self.strict_mode:
                        all_valid = False
                else:
                    console.print(f"✅ PRESENT: [green]{var_name}[/green]")

        return all_valid

    def validate_frontend(self) -> bool:
        """Validate frontend environment variables"""
        console.print("\n[bold cyan]🎨 FRONTEND ENVIRONMENT VALIDATION[/bold cyan]\n")

        all_valid = True

        for var_name, config in REQUIRED_FRONTEND_VARS.items():
            is_present, warning = self.check_env_var(var_name, config)

            if not is_present:
                if not config.get("optional"):
                    self.results["frontend"]["missing"].append({
                        "name": var_name,
                        "severity": config["severity"],
                        "description": config["description"]
                    })
                    severity_icon = "🔴" if config["severity"] == "CRITICAL" else "🟡"
                    console.print(f"{severity_icon} MISSING: [red]{var_name}[/red]")
                    console.print(f"   {config['description']}")
                    console.print(f"   Example: [dim]{config['example']}[/dim]\n")

                    if config["severity"] == "CRITICAL":
                        all_valid = False
                else:
                    console.print(f"ℹ️  OPTIONAL: [yellow]{var_name}[/yellow] not set")
            else:
                self.results["frontend"]["present"].append(var_name)

                if warning:
                    self.results["frontend"]["warnings"].append({
                        "name": var_name,
                        "warning": warning
                    })
                    console.print(f"⚠️  WARNING: [yellow]{var_name}[/yellow]: {warning}")

                    if self.strict_mode:
                        all_valid = False
                else:
                    console.print(f"✅ PRESENT: [green]{var_name}[/green]")

        return all_valid

    def check_render_specific(self):
        """Check for Render-specific environment variables"""
        console.print("\n[bold cyan]☁️  RENDER PLATFORM CHECK[/bold cyan]\n")

        render_vars = {
            "RENDER": "Indicates running on Render platform",
            "RENDER_SERVICE_NAME": "Service name in Render",
            "RENDER_EXTERNAL_URL": "Public URL of the service",
            "PORT": "Port assigned by Render"
        }

        found_render_vars = []
        for var_name, description in render_vars.items():
            if os.getenv(var_name):
                found_render_vars.append(var_name)
                console.print(f"✅ {var_name}: {os.getenv(var_name)}")

        if not found_render_vars:
            console.print("ℹ️  Not running on Render platform (local development)")
        else:
            console.print(f"\n[green]Running on Render: {os.getenv('RENDER_SERVICE_NAME', 'Unknown')}[/green]")

    def generate_report(self) -> int:
        """Generate final report and return exit code"""
        console.print("\n[bold cyan]📊 RENDER MOD - FINAL REPORT[/bold cyan]\n")

        # Count issues
        backend_missing = len([m for m in self.results["backend"]["missing"] if m["severity"] == "CRITICAL"])
        frontend_missing = len([m for m in self.results["frontend"]["missing"] if m["severity"] == "CRITICAL"])

        total_warnings = len(self.results["backend"]["warnings"]) + len(self.results["frontend"]["warnings"])

        # Summary table
        try:
            table = Table(title="Environment Status", show_header=True)
            table.add_column("Service", style="cyan")
            table.add_column("Present", style="green")
            table.add_column("Missing (Critical)", style="red")
            table.add_column("Warnings", style="yellow")

            table.add_row(
                "Backend",
                str(len(self.results["backend"]["present"])),
                str(backend_missing),
                str(len(self.results["backend"]["warnings"]))
            )

            table.add_row(
                "Frontend",
                str(len(self.results["frontend"]["present"])),
                str(frontend_missing),
                str(len(self.results["frontend"]["warnings"]))
            )

            console.print(table)
        except:
            # Fallback if rich not available
            console.print(f"\nBackend: {len(self.results['backend']['present'])} present, {backend_missing} missing")
            console.print(f"Frontend: {len(self.results['frontend']['present'])} present, {frontend_missing} missing")

        # Render deployment instructions
        if backend_missing > 0 or frontend_missing > 0:
            console.print("\n[bold red]⚠️  DEPLOYMENT BLOCKED[/bold red]")
            console.print("\n[yellow]To fix missing variables in Render:[/yellow]")
            console.print("1. Go to: https://dashboard.render.com")
            console.print("2. Select your service (backend or frontend)")
            console.print("3. Navigate to 'Environment' tab")
            console.print("4. Click 'Add Environment Variable'")
            console.print("5. Add each missing variable listed above")
            console.print("6. Click 'Save Changes' to trigger redeploy\n")

        # Exit code logic
        if backend_missing > 0 or frontend_missing > 0:
            console.print("[red]❌ RENDER MOD: FAILED - Missing critical variables[/red]")
            return 1
        elif self.strict_mode and total_warnings > 0:
            console.print("[yellow]⚠️  RENDER MOD: WARNING - Issues found (strict mode)[/yellow]")
            return 1
        else:
            console.print("[green]✅ RENDER MOD: PASSED - All required variables present[/green]")
            return 0


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="RENDER MOD - Environment variable validator for Render deployments"
    )
    parser.add_argument("--check-backend", action="store_true", help="Validate backend only")
    parser.add_argument("--check-frontend", action="store_true", help="Validate frontend only")
    parser.add_argument("--strict", action="store_true", help="Fail on warnings")
    parser.add_argument("--env-file", type=str, help="Load variables from .env file")

    args = parser.parse_args()

    # Load from .env file if specified
    if args.env_file:
        env_path = Path(args.env_file)
        if env_path.exists():
            console.print(f"[cyan]Loading environment from: {env_path}[/cyan]")
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ[key.strip()] = value.strip()
        else:
            console.print(f"[red]Error: .env file not found: {env_path}[/red]")
            return 1

    # Run validation
    mod = RenderMod(strict_mode=args.strict)

    console.print("\n[bold cyan]🚀 RENDER MOD - Environment Variable Validator[/bold cyan]")
    console.print(f"[dim]Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]")

    backend_valid = True
    frontend_valid = True

    if not args.check_frontend:
        backend_valid = mod.validate_backend()

    if not args.check_backend:
        frontend_valid = mod.validate_frontend()

    # Check Render-specific vars
    mod.check_render_specific()

    # Generate report
    exit_code = mod.generate_report()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
