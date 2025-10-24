# PaiiD Internal PyPI Mirror

This directory contains an internal Python package mirror for `pip-audit` and its dependencies. The mirror enables offline installation and reduces dependency on external PyPI, making it ideal for environments behind corporate proxies or with restricted internet access.

## 📋 Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Setup Instructions](#setup-instructions)
  - [1. Populate the Mirror](#1-populate-the-mirror)
  - [2. Configure Pip](#2-configure-pip)
  - [3. Test the Setup](#3-test-the-setup)
- [Usage](#usage)
  - [Local Development](#local-development)
  - [CI/CD Integration](#cicd-integration)
  - [Production Deployment](#production-deployment)
- [Mirror Structure](#mirror-structure)
- [Troubleshooting](#troubleshooting)
- [Maintenance](#maintenance)

## Overview

The internal mirror provides:

- **Offline Installation**: Install `pip-audit` without external internet access
- **Proxy Support**: Pre-downloaded packages bypass proxy restrictions
- **Version Control**: Pin specific package versions for reproducibility
- **Security**: Host packages on internal infrastructure
- **Performance**: Faster installations from local/internal network

### Supported Package Index Formats

This mirror uses the [PEP 503 Simple Repository API](https://peps.python.org/pep-0503/) format, compatible with:

- **Artifactory** (JFrog)
- **Nexus Repository** (Sonatype)
- **devpi** (PyPI server)
- **Simple HTTP server** (for testing)

## Quick Start

```bash
# 1. Populate the mirror (run once)
cd backend/pypi-mirror
chmod +x scripts/download-packages.sh
./scripts/download-packages.sh

# 2. Start local mirror server (for testing)
python scripts/serve-mirror.py

# 3. In another terminal, activate mirror and install
source backend/pypi-mirror/activate-mirror.sh
pip install pip-audit

# 4. Verify installation
pip-audit --version
```

## Setup Instructions

### 1. Populate the Mirror

Download `pip-audit` and all its dependencies:

```bash
cd backend/pypi-mirror
chmod +x scripts/download-packages.sh
./scripts/download-packages.sh
```

This script:
- Downloads `pip-audit` and all transitive dependencies
- Organizes packages into the Simple Repository API structure
- Generates index.html files for each package
- Creates a root index for package discovery

**Output structure:**
```
simple/
├── index.html                    # Root package index
├── pip-audit/
│   ├── index.html               # pip-audit package index
│   └── pip_audit-2.6.0-py3-none-any.whl
├── packaging/
│   ├── index.html
│   └── packaging-23.0-py3-none-any.whl
└── [other dependencies...]/
```

### 2. Configure Pip

Choose one of the following methods:

#### Option A: Environment Variables (Recommended for CI/CD)

```bash
# Source the activation script
source backend/pypi-mirror/activate-mirror.sh

# Or export manually
export PIP_INDEX_URL="http://localhost:8080/"
export PIP_TRUSTED_HOST="localhost"
export PIP_EXTRA_INDEX_URL="https://pypi.org/simple"  # Optional fallback
```

#### Option B: Pip Configuration File

**Per-user configuration:**
```bash
# Linux/macOS
mkdir -p ~/.config/pip
cp backend/pypi-mirror/pip.conf ~/.config/pip/pip.conf

# Windows (PowerShell)
New-Item -Path "$env:APPDATA\pip" -ItemType Directory -Force
Copy-Item backend\pypi-mirror\pip.conf "$env:APPDATA\pip\pip.ini"
```

**Global configuration (requires sudo):**
```bash
# Linux/macOS
sudo cp backend/pypi-mirror/pip.conf /etc/pip.conf

# Windows (PowerShell as Administrator)
Copy-Item backend\pypi-mirror\pip.conf "C:\ProgramData\pip\pip.ini"
```

#### Option C: Command-line Arguments

```bash
# Install from mirror only
pip install --index-url http://localhost:8080/ pip-audit

# Install with fallback to PyPI
pip install \
    --index-url http://localhost:8080/ \
    --extra-index-url https://pypi.org/simple \
    pip-audit
```

### 3. Test the Setup

```bash
# Start local mirror server (in one terminal)
cd backend/pypi-mirror
python scripts/serve-mirror.py

# Test installation (in another terminal)
source backend/pypi-mirror/activate-mirror.sh
pip install pip-audit

# Verify
pip-audit --version
pip-audit --help
```

## Usage

### Local Development

**Start the mirror server:**
```bash
cd backend/pypi-mirror
python scripts/serve-mirror.py --port 8080 --host 127.0.0.1
```

**Install pip-audit:**
```bash
source backend/pypi-mirror/activate-mirror.sh
pip install pip-audit
```

**Run security audit:**
```bash
cd backend
pip-audit -r requirements.txt
```

### CI/CD Integration

#### GitHub Actions Example

```yaml
# .github/workflows/security-audit.yml
name: Security Audit

on: [push, pull_request]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Configure pip to use internal mirror
        run: |
          source backend/pypi-mirror/activate-mirror.sh
          # Override with production mirror URL if needed
          export PIP_INDEX_URL="${{ secrets.INTERNAL_PYPI_MIRROR }}"

      - name: Install pip-audit from mirror
        run: pip install pip-audit

      - name: Run security audit
        run: |
          cd backend
          pip-audit -r requirements.txt
```

#### GitLab CI Example

```yaml
# .gitlab-ci.yml
security-audit:
  stage: test
  image: python:3.11
  before_script:
    - source backend/pypi-mirror/activate-mirror.sh
    # Override with production mirror URL
    - export PIP_INDEX_URL="${INTERNAL_PYPI_MIRROR}"
  script:
    - pip install pip-audit
    - cd backend && pip-audit -r requirements.txt
```

### Production Deployment

For production, replace the local HTTP server with a proper package index:

#### Artifactory (JFrog)

```bash
# Configure in activate-mirror.sh or environment
export PIP_INDEX_URL="https://artifactory.company.com/artifactory/api/pypi/pypi-local/simple"
export PIP_TRUSTED_HOST="artifactory.company.com"

# If authentication required
export PIP_USERNAME="your-username"
export PIP_PASSWORD="${ARTIFACTORY_TOKEN}"
```

#### Nexus Repository

```bash
export PIP_INDEX_URL="https://nexus.company.com/repository/pypi-internal/simple"
export PIP_TRUSTED_HOST="nexus.company.com"
```

#### devpi

```bash
export PIP_INDEX_URL="https://devpi.company.com/root/pypi/+simple/"
```

#### Upload packages to production mirror:

**Artifactory:**
```bash
# Upload using curl
for package in simple/pip-audit/*.whl; do
  curl -u username:token \
    -X PUT \
    "https://artifactory.company.com/artifactory/pypi-local/$(basename $package)" \
    -T "$package"
done
```

**Nexus:**
```bash
# Upload using twine
pip install twine
twine upload --repository-url https://nexus.company.com/repository/pypi-internal/ simple/pip-audit/*
```

## Mirror Structure

```
backend/pypi-mirror/
├── README.md                     # This file
├── pip.conf                      # Pip configuration template
├── activate-mirror.sh            # Environment setup script
├── requirements-audit.txt        # pip-audit requirements file
│
├── scripts/
│   ├── download-packages.sh     # Download packages from PyPI
│   └── serve-mirror.py          # Local HTTP server for testing
│
└── simple/                       # Simple Repository API structure
    ├── index.html               # Root package index
    ├── pip-audit/
    │   ├── index.html
    │   └── pip_audit-*.whl
    ├── packaging/
    │   ├── index.html
    │   └── packaging-*.whl
    └── [dependencies...]/
```

## Troubleshooting

### Package Not Found

**Error:** `Could not find a version that satisfies the requirement pip-audit`

**Solutions:**
1. Verify mirror is running: `curl http://localhost:8080/`
2. Check package exists: `ls backend/pypi-mirror/simple/pip-audit/`
3. Regenerate index: `./scripts/download-packages.sh`
4. Verify PIP_INDEX_URL: `echo $PIP_INDEX_URL`

### SSL/Certificate Errors

**Error:** `SSL: CERTIFICATE_VERIFY_FAILED`

**Solutions:**
1. Add to trusted hosts: `export PIP_TRUSTED_HOST="localhost"`
2. Or use proper SSL certificate for production mirror
3. Update pip.conf with trusted-host setting

### Proxy Issues

**Error:** `ProxyError` or `Connection refused`

**Solutions:**
1. Configure proxy in activate-mirror.sh:
   ```bash
   export PIP_PROXY="http://proxy.company.com:8080"
   export HTTP_PROXY="http://proxy.company.com:8080"
   export HTTPS_PROXY="http://proxy.company.com:8080"
   ```
2. Add proxy credentials if required:
   ```bash
   export PIP_PROXY="http://username:password@proxy.company.com:8080"
   ```

### Mirror Server Already Running

**Error:** `OSError: [Errno 48] Address already in use`

**Solutions:**
1. Use different port: `python serve-mirror.py --port 8081`
2. Stop existing server: `pkill -f serve-mirror.py`
3. Find process: `lsof -i :8080` and kill it

## Maintenance

### Updating Packages

To update `pip-audit` or dependencies:

```bash
# 1. Remove old packages
rm -rf backend/pypi-mirror/simple/*

# 2. Download latest versions
cd backend/pypi-mirror
./scripts/download-packages.sh

# 3. Test updated packages
python scripts/serve-mirror.py &
pip install --upgrade --force-reinstall pip-audit
pip-audit --version

# 4. Upload to production mirror if using one
```

### Adding New Packages

To add additional packages to the mirror:

```bash
# Edit download-packages.sh and add package name to pip download command
# Example: Add both pip-audit and safety
pip download \
    --dest "$TEMP_DIR" \
    --no-cache-dir \
    pip-audit safety

# Then run the script
./scripts/download-packages.sh
```

### Mirror Size Management

Monitor and manage mirror size:

```bash
# Check total size
du -sh backend/pypi-mirror/simple/

# List packages by size
du -sh backend/pypi-mirror/simple/*/ | sort -h

# Remove unused packages
rm -rf backend/pypi-mirror/simple/unused-package/

# Regenerate root index
cd backend/pypi-mirror
./scripts/download-packages.sh  # This will rebuild indices
```

## Security Considerations

1. **Package Integrity**: Verify checksums of downloaded packages
2. **Access Control**: Restrict mirror access to authorized users/systems
3. **Regular Updates**: Keep packages updated to include security patches
4. **Audit Logs**: Monitor who accesses/downloads packages
5. **HTTPS**: Use SSL/TLS for production mirrors
6. **Authentication**: Require credentials for package downloads

## References

- [PEP 503 - Simple Repository API](https://peps.python.org/pep-0503/)
- [pip Configuration](https://pip.pypa.io/en/stable/topics/configuration/)
- [pip-audit Documentation](https://github.com/pypa/pip-audit)
- [Artifactory PyPI Repositories](https://jfrog.com/help/r/jfrog-artifactory-documentation/pypi-repositories)
- [Nexus PyPI Repositories](https://help.sonatype.com/repomanager3/nexus-repository-administration/formats/pypi-repositories)

## Support

For questions or issues with the internal mirror:

1. Check this README and troubleshooting section
2. Review logs from serve-mirror.py
3. Test with `pip install -vvv pip-audit` for verbose output
4. Open an issue in the repository with error details

---

**Last Updated:** 2025-10-24
**Maintained by:** PaiiD Development Team
