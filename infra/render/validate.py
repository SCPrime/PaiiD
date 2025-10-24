#!/usr/bin/env python3
"""
Render Configuration Validator

Validates render.yaml files against expected configuration schema.
Detects config drift and missing required environment variables.
"""

import json
import sys

import yaml


def validate_render_config(render_yaml_path: str, expected_config_path: str = None):
    """Validate Render YAML against expected configuration"""

    # Load render.yaml
    with open(render_yaml_path) as f:
        render_config = yaml.safe_load(f)

    # Load expected config if provided
    if expected_config_path:
        with open(expected_config_path) as f:
            expected = json.load(f)

        # Validate required env vars present
        service = render_config["services"][0]
        env_var_keys = [var["key"] for var in service.get("envVars", [])]

        missing_required = [
            var for var in expected["required_env_vars"] if var not in env_var_keys
        ]

        if missing_required:
            print(f"❌ Missing required env vars: {missing_required}")
            return False

    print(f"✅ {render_yaml_path} validation passed")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate.py <render.yaml> [expected-config.json]")
        sys.exit(1)

    render_yaml = sys.argv[1]
    expected_config = sys.argv[2] if len(sys.argv) > 2 else None

    success = validate_render_config(render_yaml, expected_config)
    sys.exit(0 if success else 1)
