"""MOD SQUAD extension suite - Universal preloaded extensions for all projects."""

from .utils import ExtensionConfig, load_extension_config

# Core extensions (pre-existing)
from . import maintenance_notifier
from . import metrics_streamer
from . import secrets_watchdog
from . import strategy_verifier

# Validation extensions
from . import browser_validator
from . import contract_enforcer
from . import integration_validator
from . import bundle_analyzer
from . import runtime_error_monitor
from . import visual_regression_advanced

# Infrastructure & health
from . import infra_health
from . import dependency_tracker
from . import subprocess_manager
from . import circuit_breaker
from . import test_orchestrator

# Scheduling & orchestration
from . import guardrail_scheduler
from . import accessibility_scheduler
from . import data_latency_tracker

# Reporting & analysis
from . import component_diff_reporter
from . import security_patch_advisor
from . import docs_sync
from . import review_aggregator
from . import quality_inspector

# Testing & simulation
from . import persona_simulator

# Coordination
from . import stream_coordinator

# SUN TZU Squad - Strategic Batch Planning
from . import elite_strategist
from . import task_graph_analyzer
from . import risk_profiler
from . import batch_optimizer
from . import intersection_mapper

# ARMANI Squad - Integration Weaving
from . import elite_weaver
from . import interface_predictor
from . import glue_code_generator
from . import conflict_resolver
from . import intersection_executor

__all__ = [
    # Utilities
    "ExtensionConfig",
    "load_extension_config",

    # Core extensions
    "maintenance_notifier",
    "metrics_streamer",
    "secrets_watchdog",
    "strategy_verifier",

    # Validation extensions
    "browser_validator",
    "contract_enforcer",
    "integration_validator",
    "bundle_analyzer",
    "runtime_error_monitor",
    "visual_regression_advanced",

    # Infrastructure & health
    "infra_health",
    "dependency_tracker",
    "subprocess_manager",
    "circuit_breaker",
    "test_orchestrator",

    # Scheduling & orchestration
    "guardrail_scheduler",
    "accessibility_scheduler",
    "data_latency_tracker",

    # Reporting & analysis
    "component_diff_reporter",
    "security_patch_advisor",
    "docs_sync",
    "review_aggregator",
    "quality_inspector",

    # Testing & simulation
    "persona_simulator",

    # Coordination
    "stream_coordinator",

    # SUN TZU Squad - Strategic Batch Planning
    "elite_strategist",
    "task_graph_analyzer",
    "risk_profiler",
    "batch_optimizer",
    "intersection_mapper",

    # ARMANI Squad - Integration Weaving
    "elite_weaver",
    "interface_predictor",
    "glue_code_generator",
    "conflict_resolver",
    "intersection_executor",
]

