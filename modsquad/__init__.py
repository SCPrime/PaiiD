"""
MOD SQUAD - Meta Orchestration & Development System for Quality & Utility Automation Dashboards

🎯 ELITE SPECIALTY SQUADS - Permanent Deployment Configuration

ALPHA SQUAD   - Core Infrastructure & Security (<1% risk, always active)
BRAVO SQUAD   - Quality Validation & Testing (<3% risk, on-demand)
CHARLIE SQUAD - Security & Dependency Management (<2% risk, scheduled)
DELTA SQUAD   - Change Detection & Monitoring (<1% risk, continuous)
ECHO SQUAD    - Aggregation & Reporting (<1% risk, post-execution)
FOXTROT SQUAD - Orchestration & Coordination (<2% risk, meta-coordination)
SUN TZU SQUAD - Strategic Batch Planning (<2% risk, on-demand) - The Art of Parallel Warfare
ARMANI SQUAD  - Integration Weaving (<3% risk, on-demand) - Haute Couture Code Integration

Universal preloaded work environment with 190+ modules available.
"""

from .universal_loader import (
    REGISTRY,
    UniversalModuleRegistry,
    get_registry,
    load_all,
)

# Import all extensions for direct access
from . import extensions

# Import elite squads
from . import squads

# Expose registry globally
modules = REGISTRY

# Auto-activate ALPHA SQUAD (always-on services)
squads.alpha.activate()


def list_all_modules():
    """List all available modules."""
    return REGISTRY.list_all()


def get_module(name: str):
    """Get a specific module by name."""
    return REGISTRY.get(name)


def deploy_full_stack(skip_slow=False):
    """Deploy all squads for full stack validation."""
    return squads.foxtrot.orchestrate_all(skip_slow=skip_slow)


def pre_deploy_check():
    """Run pre-deployment validation (BRAVO + CHARLIE)."""
    return squads.foxtrot.pre_deploy_check()


def squad_status():
    """Get status of all squads."""
    return squads.status_all()


__version__ = "2.2.0"
__all__ = [
    "extensions",
    "modules",
    "squads",
    "REGISTRY",
    "UniversalModuleRegistry",
    "get_registry",
    "load_all",
    "list_all_modules",
    "get_module",
    "deploy_full_stack",
    "pre_deploy_check",
    "squad_status",
]
