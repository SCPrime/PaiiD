# Production Deployment Checklist

This guide walks you through deploying the internal PyPI mirror to production, step-by-step. No advanced coding experience required!

## 🎯 Goal

Move from local testing to a production-ready internal PyPI mirror that your CI/CD and developers can use.

## 📋 Pre-Deployment Checklist

### ✅ Prerequisites

- [ ] Local mirror tested successfully (run `./scripts/verify-mirror.sh`)
- [ ] pip-audit working from local mirror
- [ ] Security audit completed on backend dependencies
- [ ] Access to one of the following:
  - Corporate Artifactory instance
  - Corporate Nexus Repository instance
  - devpi server
  - OR ability to set up a simple HTTP server

### ✅ Decisions Needed

- [ ] **Mirror Platform Choice**
  - [ ] Option A: Artifactory (Recommended for enterprises)
  - [ ] Option B: Nexus Repository (Good alternative)
  - [ ] Option C: devpi (Lightweight Python-specific)
  - [ ] Option D: Simple HTTP Server (Basic, requires less setup)

- [ ] **Access & Permissions**
  - [ ] URL for production mirror (e.g., `https://pypi.company.com`)
  - [ ] Authentication credentials (if required)
  - [ ] Network access from CI/CD servers
  - [ ] SSL/TLS certificate (recommended)

## 🚀 Deployment Methods

Choose the method that matches your infrastructure:

---

### Method A: Artifactory (JFrog)

**Best for:** Enterprises with existing Artifactory

#### Step 1: Create Repository

1. Log into Artifactory web UI
2. Admin → Repositories → Create Repository
3. Select "PyPI" type
4. Repository Key: `pypi-internal` (or your preference)
5. Click "Create"

#### Step 2: Upload Packages

```bash
# From your local machine
cd backend/pypi-mirror/simple

# Upload each package (requires Artifactory API key)
for package_dir in */; do
    package_name=$(basename "$package_dir")
    for file in "$package_dir"/*.whl "$package_dir"/*.tar.gz; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            curl -u USERNAME:API_KEY \
                -X PUT \
                "https://artifactory.company.com/artifactory/pypi-internal/$filename" \
                -T "$file"
            echo "✅ Uploaded: $filename"
        fi
    done
done
```

#### Step 3: Configure Index

Artifactory automatically generates PyPI indices. Verify at:
```
https://artifactory.company.com/artifactory/api/pypi/pypi-internal/simple
```

#### Step 4: Update CI/CD

In your CI/CD environment variables:
```bash
PIP_INDEX_URL=https://artifactory.company.com/artifactory/api/pypi/pypi-internal/simple
PIP_USERNAME=ci-user
PIP_PASSWORD=<artifactory-token>
```

---

### Method B: Nexus Repository

**Best for:** Teams using Nexus Repository Manager

#### Step 1: Create Repository

1. Log into Nexus web UI
2. Server Configuration → Repositories → Create Repository
3. Select "pypi (hosted)"
4. Name: `pypi-internal`
5. Deployment Policy: "Allow redeploy"
6. Click "Create"

#### Step 2: Upload Packages

```bash
# Install twine if not already installed
pip install twine

# Configure twine with Nexus credentials
cat > ~/.pypirc <<EOF
[distutils]
index-servers = nexus

[nexus]
repository = https://nexus.company.com/repository/pypi-internal/
username = <your-username>
password = <your-password>
EOF

# Upload packages
cd backend/pypi-mirror/simple
for package_dir in */; do
    for file in "$package_dir"/*.whl "$package_dir"/*.tar.gz; do
        if [ -f "$file" ]; then
            twine upload --repository nexus "$file"
            echo "✅ Uploaded: $(basename "$file")"
        fi
    done
done
```

#### Step 3: Configure CI/CD

```bash
PIP_INDEX_URL=https://nexus.company.com/repository/pypi-internal/simple
PIP_TRUSTED_HOST=nexus.company.com
```

---

### Method C: devpi (Lightweight)

**Best for:** Small teams, Python-specific mirror

#### Step 1: Install devpi-server

```bash
# On your mirror server
pip install devpi-server devpi-client

# Initialize server
devpi-init

# Start server
devpi-server --start --host 0.0.0.0 --port 3141
```

#### Step 2: Create Index and Upload

```bash
# Configure devpi client
devpi use http://localhost:3141
devpi login root --password ''
devpi index -c root/pypi-internal bases=root/pypi

# Upload packages
cd backend/pypi-mirror/simple
devpi use root/pypi-internal
devpi upload --from-dir .
```

#### Step 3: Configure CI/CD

```bash
PIP_INDEX_URL=http://devpi.company.com:3141/root/pypi-internal/+simple/
```

---

### Method D: Simple HTTP Server (Basic)

**Best for:** Quick setup, no enterprise infrastructure

#### Step 1: Set Up Web Server

**Option D1: Using Python**
```bash
# On your mirror server
cd backend/pypi-mirror/simple
python3 -m http.server 8080
```

**Option D2: Using nginx**
```nginx
# /etc/nginx/sites-available/pypi-mirror
server {
    listen 80;
    server_name pypi.company.com;

    root /path/to/backend/pypi-mirror/simple;

    location / {
        autoindex on;
        try_files $uri $uri/ =404;
    }
}
```

#### Step 2: Configure CI/CD

```bash
PIP_INDEX_URL=http://pypi.company.com/
PIP_TRUSTED_HOST=pypi.company.com
```

---

## 🔧 CI/CD Integration

### GitHub Actions

Update `.github/workflows/security-audit.yml`:

```yaml
env:
  PIP_INDEX_URL: ${{ secrets.INTERNAL_PYPI_MIRROR }}
  PIP_USERNAME: ${{ secrets.PYPI_USERNAME }}  # if auth required
  PIP_PASSWORD: ${{ secrets.PYPI_PASSWORD }}  # if auth required
```

Add secrets in GitHub:
1. Repository → Settings → Secrets → Actions
2. New repository secret:
   - Name: `INTERNAL_PYPI_MIRROR`
   - Value: `https://artifactory.company.com/artifactory/api/pypi/pypi-internal/simple`

### GitLab CI

Update `.gitlab-ci.yml`:

```yaml
variables:
  PIP_INDEX_URL: ${INTERNAL_PYPI_MIRROR}
  PIP_USERNAME: ${PYPI_USERNAME}
  PIP_PASSWORD: ${PYPI_PASSWORD}
```

Add variables in GitLab:
1. Project → Settings → CI/CD → Variables
2. Add variable:
   - Key: `INTERNAL_PYPI_MIRROR`
   - Value: `https://nexus.company.com/repository/pypi-internal/simple`
   - Protected: ✅
   - Masked: ✅

---

## 👨‍💻 Developer Setup

### For Your Team

Share this with developers:

```bash
# One-time setup
cd backend/pypi-mirror
source activate-mirror.sh

# Or add to ~/.bashrc or ~/.zshrc:
export PIP_INDEX_URL="https://pypi.company.com/simple"
export PIP_TRUSTED_HOST="pypi.company.com"

# Then install packages normally
pip install pip-audit
```

### For Windows Developers

Create `setup-mirror.bat`:
```batch
@echo off
set PIP_INDEX_URL=https://pypi.company.com/simple
set PIP_TRUSTED_HOST=pypi.company.com
echo ✅ Mirror configured for this session
```

---

## 🧪 Testing Production Mirror

### Step 1: Test from CI/CD Environment

```bash
# SSH into CI/CD runner or agent
export PIP_INDEX_URL="https://pypi.company.com/simple"
pip install pip-audit
pip-audit --version
```

Expected output:
```
pip-audit 2.9.0
```

### Step 2: Run Full Audit

```bash
cd /path/to/PaiiD/backend
pip-audit -r requirements.txt
```

### Step 3: Verify Package Source

```bash
pip install -vvv pip-audit 2>&1 | grep "Looking in indexes"
```

Should show your mirror URL.

---

## 📊 Monitoring & Maintenance

### Daily Checks

- [ ] Monitor mirror server logs for errors
- [ ] Check disk space (mirrors grow over time)
- [ ] Verify CI/CD jobs can access mirror

### Weekly Tasks

- [ ] Update packages in mirror (run `download-packages.sh`)
- [ ] Review any new security vulnerabilities
- [ ] Check for package download failures

### Monthly Tasks

- [ ] Audit mirror access logs
- [ ] Review and rotate credentials
- [ ] Update documentation as needed
- [ ] Prune old package versions (optional)

---

## 🆘 Troubleshooting Production Issues

### Issue: "Could not find a version that satisfies the requirement pip-audit"

**Solution:**
```bash
# Verify mirror is accessible
curl -f https://pypi.company.com/simple/pip-audit/

# Check if package exists
ls backend/pypi-mirror/simple/pip-audit/

# Re-upload if missing
# (follow Method A/B/C/D upload steps)
```

### Issue: "SSL: CERTIFICATE_VERIFY_FAILED"

**Solution:**
```bash
# Option 1: Fix certificate
# Contact IT to install proper SSL certificate

# Option 2: Temporary workaround (not recommended for production)
export PIP_TRUSTED_HOST="pypi.company.com"
```

### Issue: "403 Forbidden" in CI/CD

**Solution:**
```bash
# Verify credentials are set
echo $PIP_USERNAME
echo $PIP_INDEX_URL

# Check if secrets/variables are properly configured
# GitHub: Repository Settings → Secrets
# GitLab: Project Settings → CI/CD → Variables
```

### Issue: Slow package downloads

**Solution:**
```bash
# Check mirror server resources
top
df -h

# Consider using a CDN or load balancer
# Contact DevOps for infrastructure optimization
```

---

## 🔒 Security Best Practices

### Authentication

- [ ] Use authentication for production mirrors (Artifactory/Nexus)
- [ ] Rotate credentials every 90 days
- [ ] Use tokens instead of passwords where possible
- [ ] Limit access to authorized users/systems only

### SSL/TLS

- [ ] Use HTTPS for all production mirrors
- [ ] Install valid SSL certificates (not self-signed)
- [ ] Keep certificates up to date (renew before expiry)

### Network Security

- [ ] Restrict mirror access to internal network only
- [ ] Use firewall rules to limit access
- [ ] Enable audit logging for all package downloads
- [ ] Monitor for unusual access patterns

### Package Integrity

- [ ] Verify checksums after uploading packages
- [ ] Use signed packages where available
- [ ] Regularly scan mirror for vulnerabilities
- [ ] Keep packages updated with security patches

---

## 📞 Getting Help

### Internal Resources

- **Mirror Documentation:** `backend/pypi-mirror/README.md`
- **Setup Summary:** `backend/pypi-mirror/SETUP_SUMMARY.md`
- **This Checklist:** `backend/pypi-mirror/PRODUCTION_DEPLOYMENT.md`

### External Resources

- **Artifactory PyPI:** https://jfrog.com/help/r/jfrog-artifactory-documentation/pypi-repositories
- **Nexus PyPI:** https://help.sonatype.com/repomanager3/nexus-repository-administration/formats/pypi-repositories
- **devpi:** https://devpi.net/docs/devpi/devpi/stable/+doc/index.html
- **pip Configuration:** https://pip.pypa.io/en/stable/topics/configuration/

### Support Contacts

- **DevOps Team:** [Your contact info]
- **Security Team:** [Your contact info]
- **Project Maintainer:** [Your contact info]

---

## ✅ Post-Deployment Checklist

After completing deployment:

- [ ] Production mirror is accessible from CI/CD
- [ ] pip-audit installs successfully from mirror
- [ ] Security audit runs successfully in CI/CD
- [ ] Developers can use mirror from their workstations
- [ ] Documentation updated with production URL
- [ ] Team trained on using the mirror
- [ ] Monitoring and alerting configured
- [ ] Backup and disaster recovery plan in place
- [ ] Security team notified of new infrastructure

---

## 🎉 Success Criteria

You've successfully deployed to production when:

✅ CI/CD can install pip-audit from internal mirror
✅ Security audits run automatically on every commit
✅ No external PyPI calls during package installation
✅ Developers can use mirror from their local machines
✅ Mirror is monitored and maintained regularly
✅ Documentation is up to date and accessible

---

**Last Updated:** 2025-10-24
**Maintained By:** PaiiD Development Team

**Questions?** Open an issue or contact the DevOps team.
