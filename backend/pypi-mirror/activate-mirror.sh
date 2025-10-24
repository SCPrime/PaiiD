#!/bin/bash
# PaiiD Internal PyPI Mirror Activation Script
#
# This script configures pip to use the internal package mirror.
# Source this file in your shell or CI environment:
#
#   source backend/pypi-mirror/activate-mirror.sh
#
# Or for CI/CD, run with eval:
#
#   eval "$(bash backend/pypi-mirror/activate-mirror.sh)"

# Configuration - Update these values for your environment
# ============================================================

# Mirror URL - REPLACE with your actual internal mirror URL
# Examples:
#   - Local testing: http://localhost:8080/
#   - Artifactory: https://artifactory.company.com/artifactory/api/pypi/pypi-local/simple
#   - Nexus: https://nexus.company.com/repository/pypi-internal/simple
#   - devpi: https://devpi.company.com/root/pypi/+simple/
MIRROR_URL="${PIP_MIRROR_URL:-http://localhost:8080/}"

# Trusted host (for mirrors without SSL)
# Remove or leave empty if your mirror has valid SSL certificates
MIRROR_HOST="${PIP_MIRROR_HOST:-localhost}"

# Proxy settings (if required)
# Uncomment and configure if behind a corporate proxy
# PROXY_URL="${HTTP_PROXY:-}"

# Fallback to PyPI (set to "true" to enable, "false" to disable)
# If "true", pip will fall back to PyPI if package not found in mirror
# If "false", pip will ONLY use the internal mirror
ALLOW_FALLBACK="${PIP_ALLOW_FALLBACK:-true}"

# ============================================================

# Export pip configuration via environment variables
export PIP_INDEX_URL="$MIRROR_URL"

if [ -n "$MIRROR_HOST" ]; then
    export PIP_TRUSTED_HOST="$MIRROR_HOST"
fi

if [ "$ALLOW_FALLBACK" = "true" ]; then
    export PIP_EXTRA_INDEX_URL="https://pypi.org/simple"
fi

# Proxy configuration
if [ -n "$PROXY_URL" ]; then
    export PIP_PROXY="$PROXY_URL"
    export HTTP_PROXY="$PROXY_URL"
    export HTTPS_PROXY="$PROXY_URL"
fi

# Additional pip settings
export PIP_DISABLE_PIP_VERSION_CHECK=1
export PIP_PREFER_BINARY=1

# Print configuration
echo "=========================================="
echo "🔧 PaiiD PyPI Mirror Configuration"
echo "=========================================="
echo "Index URL:     $PIP_INDEX_URL"
if [ -n "$PIP_TRUSTED_HOST" ]; then
    echo "Trusted Host:  $PIP_TRUSTED_HOST"
fi
if [ -n "$PIP_EXTRA_INDEX_URL" ]; then
    echo "Fallback:      $PIP_EXTRA_INDEX_URL"
fi
if [ -n "$PIP_PROXY" ]; then
    echo "Proxy:         $PIP_PROXY"
fi
echo "=========================================="
echo ""
echo "✅ Pip is now configured to use the internal mirror"
echo ""
echo "Test installation:"
echo "  pip install pip-audit"
echo ""
echo "To deactivate, unset the environment variables:"
echo "  unset PIP_INDEX_URL PIP_TRUSTED_HOST PIP_EXTRA_INDEX_URL PIP_PROXY"
echo "=========================================="
