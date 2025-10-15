# SonarCloud Setup Guide

This guide walks you through setting up SonarCloud for continuous code quality scanning on the PaiiD project.

## What is SonarCloud?

SonarCloud is a cloud-based code quality and security service that automatically analyzes your code on every commit and pull request. It provides:

- **Code Quality Analysis**: Detects bugs, code smells, and maintainability issues
- **Security Vulnerability Detection**: Identifies security hotspots and vulnerabilities
- **Test Coverage Tracking**: Monitors code coverage from Jest (frontend) and pytest (backend)
- **Technical Debt Monitoring**: Tracks complexity and technical debt over time
- **Quality Gates**: Enforces quality standards before merging code

## Prerequisites

- GitHub account with access to the SCPrime/PaiiD repository
- Admin access to add GitHub Secrets

## Step 1: Create SonarCloud Account

1. Go to **https://sonarcloud.io**
2. Click **"Log in"** and select **"Log in with GitHub"**
3. Authorize SonarCloud to access your GitHub account
4. Follow the setup wizard

## Step 2: Create Organization

1. After logging in, click **"+"** (Create new organization)
2. Choose **"Import an organization from GitHub"**
3. Select your GitHub username or organization: **`SCPrime`**
4. Set organization key: **`scprime`** (lowercase)
5. Choose plan: **"Free Plan"** (sufficient for open-source/private projects)
6. Click **"Continue"**

## Step 3: Import Repository

1. SonarCloud will show your GitHub repositories
2. Find **`PaiiD`** in the list
3. Click **"Set Up"** next to it
4. Choose **"With GitHub Actions"** as the analysis method
5. SonarCloud will detect the monorepo structure

## Step 4: Create Projects for Monorepo

Since PaiiD is a monorepo with frontend and backend, you need two separate projects:

### Frontend Project:
1. Click **"Create new project manually"**
2. Project key: **`SCPrime_PaiiD:frontend`**
3. Project name: **`PaiiD Frontend`**
4. Click **"Set up"**

### Backend Project:
1. Click **"Create new project manually"**
2. Project key: **`SCPrime_PaiiD:backend`**
3. Project name: **`PaiiD Backend`**
4. Click **"Set up"**

## Step 5: Generate SONAR_TOKEN

1. Go to **My Account** (top-right corner) → **Security**
2. Under **"Tokens"**, enter token name: **`PaiiD-GitHub-Actions`**
3. Set token type: **"User Token"** (or "Project Analysis Token" if available)
4. Click **"Generate"**
5. **COPY THE TOKEN IMMEDIATELY** - it won't be shown again!
   - Format: `sqp_1234567890abcdef1234567890abcdef12345678`

## Step 6: Add Token to GitHub Secrets

1. Go to **GitHub repository**: https://github.com/SCPrime/PaiiD
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Name: **`SONAR_TOKEN`**
5. Value: Paste the token from Step 5
6. Click **"Add secret"**

## Step 7: Verify Configuration Files

The following files have been created and should be committed:

```
ai-Trader/
├── sonar-project.properties          # Root monorepo config
├── frontend/
│   └── sonar-project.properties      # Frontend-specific config
├── backend/
│   └── sonar-project.properties      # Backend-specific config
└── .github/
    └── workflows/
        └── ci.yml                    # Updated with SonarCloud jobs
```

## Step 8: Push and Test

1. Commit the SonarCloud configuration:
   ```bash
   git add sonar-project.properties frontend/sonar-project.properties backend/sonar-project.properties .github/workflows/ci.yml SONARCLOUD_SETUP.md
   git commit -m "feat(ci): configure SonarCloud for code quality scanning"
   git push origin main
   ```

2. Monitor the GitHub Actions workflow:
   - Go to **Actions** tab in GitHub
   - Watch the CI workflow run
   - Verify `sonar-frontend` and `sonar-backend` jobs succeed

3. Check SonarCloud Dashboard:
   - Go to https://sonarcloud.io/organizations/scprime/projects
   - You should see both projects with analysis results

## Understanding SonarCloud Reports

### Quality Gate Status
- ✅ **Passed**: Code meets quality standards
- ❌ **Failed**: Code has issues that need fixing

### Key Metrics
- **Bugs**: Critical issues that can cause runtime errors
- **Vulnerabilities**: Security issues
- **Code Smells**: Maintainability issues
- **Coverage**: Percentage of code tested
- **Duplications**: Percentage of duplicated code
- **Technical Debt**: Estimated time to fix all issues

### Viewing Issues
1. Click on a project in SonarCloud
2. Go to **"Issues"** tab
3. Filter by:
   - **Type**: Bug, Vulnerability, Code Smell
   - **Severity**: Blocker, Critical, Major, Minor, Info
   - **Status**: Open, Confirmed, Resolved, Reopened

## Quality Gate Configuration

Default quality gate requires:
- **Coverage**: ≥ 80% on new code
- **Duplications**: ≤ 3% on new code
- **Maintainability Rating**: A on new code
- **Reliability Rating**: A on new code
- **Security Rating**: A on new code

You can customize these in SonarCloud → Project Settings → Quality Gate.

## Troubleshooting

### "Could not find a default branch to fall back to"
- Ensure your repository has at least one commit on `main` branch
- Push initial commit before running SonarCloud analysis

### "No analysis found for this project"
- Verify `SONAR_TOKEN` is correctly set in GitHub Secrets
- Check GitHub Actions logs for errors in `sonar-frontend` or `sonar-backend` jobs

### "Coverage report not found"
- Ensure tests run successfully before SonarCloud scan
- Check that coverage files are uploaded as artifacts:
  - Frontend: `frontend/coverage/lcov.info`
  - Backend: `backend/coverage.xml`

### "Shallow clone detected"
- Fixed by `fetch-depth: 0` in GitHub Actions checkout
- This ensures SonarCloud can access full git history for blame information

## Integration with Pull Requests

SonarCloud will automatically:
1. ✅ Analyze every pull request
2. 💬 Comment on PRs with issues found
3. 🚦 Set PR status check (passed/failed)
4. 📊 Show quality gate status in PR checks

## Continuous Monitoring

SonarCloud dashboard provides:
- **Project Homepage**: Overview of current status
- **Issues Breakdown**: Track bugs, vulnerabilities, code smells
- **Activity**: Recent analysis history
- **Measures**: Detailed metrics over time

Access at: **https://sonarcloud.io/organizations/scprime/projects**

## Best Practices

1. **Fix Critical Issues First**: Address bugs and vulnerabilities before code smells
2. **Monitor New Code**: Focus on improving new/changed code quality
3. **Review Security Hotspots**: Manually verify flagged security-sensitive code
4. **Improve Test Coverage**: Add tests to increase coverage percentage
5. **Reduce Technical Debt**: Regularly refactor to keep debt manageable

## Support

- **SonarCloud Docs**: https://docs.sonarcloud.io
- **Community Forum**: https://community.sonarsource.com
- **GitHub Actions Integration**: https://docs.sonarcloud.io/advanced-setup/ci-based-analysis/github-actions-for-sonarcloud/

---

**Status**: Configuration files created, ready for GitHub Secret setup
**Next Steps**: Complete Steps 1-6, then push configuration to trigger first analysis
