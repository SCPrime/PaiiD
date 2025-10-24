# File Naming Conventions
**Established**: October 24, 2025  
**Purpose**: Prevent future redundancy and maintain clean codebase organization

---

## Overview

This document establishes naming conventions for the PaiiD project to prevent accumulation of redundant files and maintain clear organization. These conventions should be followed for all new files and applied when refactoring existing files.

---

## Core Principles

1. **Clarity**: File names should clearly indicate purpose and content
2. **Consistency**: Use standardized patterns across the project
3. **Avoidance**: Prevent creation of redundant or duplicate files
4. **Organization**: Group related files logically
5. **Maintenance**: Enable easy identification of outdated content

---

## File Naming Standards

### Active Files (Current/Active)

#### Documentation Files
**Pattern**: `[TOPIC]_[TYPE].md`

**Examples**:
- `API_DOCUMENTATION.md` - API reference
- `DEPLOYMENT_GUIDE.md` - Deployment instructions
- `ARCHITECTURE_OVERVIEW.md` - System architecture
- `CONTRIBUTING.md` - Contribution guidelines
- `README.md` - Project overview (special case)

**Status Indicators** (AVOID):
- ❌ `*_COMPLETE.md` - Use `*_STATUS.md` instead
- ❌ `*_FINAL.md` - Use `*_CURRENT.md` instead
- ❌ `*_DONE.md` - Use `*_ACTIVE.md` instead

#### Code Files
**Pattern**: `[purpose].[extension]`

**Examples**:
- `deploy.ps1` - Deployment script
- `health-check.sh` - Health monitoring
- `cleanup.py` - Cleanup utility
- `migrate.sql` - Database migration

#### Configuration Files
**Pattern**: `[service].[extension]`

**Examples**:
- `docker-compose.yml`
- `package.json`
- `tsconfig.json`
- `render.yaml`

### Archived Files (Historical/Completed)

#### Pattern: `[TOPIC]_[STATUS]_[DATE].md`

**Examples**:
- `DEPLOYMENT_COMPLETE_2025-10-24.md`
- `AUDIT_FINISHED_2025-10-13.md`
- `MIGRATION_DONE_2025-09-15.md`

#### Archive Directory Structure
```
archive/
├── cleanup-2025-10-24/          # Batch cleanup archives
├── reports-2025-10/             # Monthly report archives
├── deprecated-2025-09/          # Deprecated feature archives
└── completed-tasks/              # Task completion archives
```

### Status Reports

#### Active Status Files
**Pattern**: `[COMPONENT]_STATUS.md`

**Examples**:
- `API_STATUS.md` - Current API status
- `DEPLOYMENT_STATUS.md` - Current deployment status
- `SYSTEM_STATUS.md` - Overall system status

#### Historical Status Files
**Pattern**: `[COMPONENT]_STATUS_[DATE].md`

**Examples**:
- `API_STATUS_2025-10-24.md` - API status on specific date
- `DEPLOYMENT_STATUS_2025-10-23.md` - Deployment status on specific date

### Test and Report Files

#### Test Reports
**Pattern**: `test-[type]-[timestamp].md`

**Examples**:
- `test-deployment-20251024-143022.md`
- `test-api-20251024-091500.md`
- `test-integration-20251024-160000.md`

#### Health Reports
**Pattern**: `health-[component]-[timestamp].md`

**Examples**:
- `health-system-20251024-143022.md`
- `health-database-20251024-091500.md`

#### Audit Reports
**Pattern**: `audit-[scope]-[date].md`

**Examples**:
- `audit-security-2025-10-24.md`
- `audit-performance-2025-10-23.md`
- `audit-code-quality-2025-10-22.md`

---

## Directory Organization

### Root Directory
**Keep minimal and organized**:
- `README.md` - Project overview
- `CONTRIBUTING.md` - Contribution guidelines
- `LICENSE` - License information
- `package.json` - Node.js dependencies
- `docker-compose.yml` - Container orchestration
- `render.yaml` - Deployment configuration

### Documentation Directory Structure
```
docs/
├── setup/                       # Installation and setup guides
├── api/                         # API documentation
├── operations/                  # Operations and deployment
├── architecture/                # System design and architecture
├── development/                # Development guides
├── testing/                    # Testing documentation
└── troubleshooting/            # Problem resolution guides
```

### Archive Directory Structure
```
archive/
├── cleanup-[date]/              # Batch cleanup archives
├── reports-[year]-[month]/      # Monthly report archives
├── deprecated-[date]/           # Deprecated feature archives
└── completed-[date]/            # Completed task archives
```

---

## Date Format Standards

### ISO Format (Recommended)
**Pattern**: `YYYY-MM-DD`

**Examples**:
- `2025-10-24`
- `2025-12-31`

### Timestamp Format (For Reports)
**Pattern**: `YYYYMMDD-HHMMSS`

**Examples**:
- `20251024-143022`
- `20251231-235959`

### Month-Year Format (For Archives)
**Pattern**: `YYYY-MM`

**Examples**:
- `2025-10`
- `2025-12`

---

## Status Indicators

### Active/Current Status
- `ACTIVE` - Currently in use
- `CURRENT` - Current version
- `LATEST` - Most recent version
- `STATUS` - Current status

### Completed/Historical Status
- `COMPLETE` - Task completed
- `FINISHED` - Process finished
- `DONE` - Work completed
- `ARCHIVED` - Moved to archive

### Deprecated/Outdated Status
- `DEPRECATED` - No longer recommended
- `OUTDATED` - Superseded by newer version
- `OLD` - Previous version
- `LEGACY` - Legacy system

---

## Prevention Rules

### ❌ Avoid These Patterns
1. **Multiple completion markers**: `*_COMPLETE_FINAL_DONE.md`
2. **Ambiguous dates**: `*_TODAY.md`, `*_YESTERDAY.md`
3. **Vague status**: `*_SOMETHING.md`, `*_STUFF.md`
4. **Duplicate content**: Multiple files with same purpose
5. **Temporary names**: `*_TEMP.md`, `*_TMP.md`, `*_NEW.md`

### ✅ Use These Patterns Instead
1. **Clear status**: `*_STATUS.md`, `*_CURRENT.md`
2. **Specific dates**: `*_2025-10-24.md`
3. **Descriptive names**: `*_DEPLOYMENT.md`, `*_API.md`
4. **Single source of truth**: One file per topic
5. **Permanent names**: `*_GUIDE.md`, `*_REFERENCE.md`

---

## File Lifecycle Management

### Creation Phase
1. Use descriptive, specific names
2. Include purpose in filename
3. Follow established patterns
4. Document in appropriate index

### Active Phase
1. Keep content current
2. Update timestamps when modified
3. Maintain single source of truth
4. Link from relevant indexes

### Archive Phase
1. Move to appropriate archive directory
2. Add completion date to filename
3. Update documentation index
4. Preserve for historical reference

### Deletion Phase
1. Verify no active references
2. Confirm archival is complete
3. Remove from active directories
4. Update documentation index

---

## Enforcement Tools

### Automated Checks
- **Inventory Scanner**: Detects redundant patterns
- **Naming Validator**: Checks new files against conventions
- **Archive Manager**: Handles file lifecycle transitions

### Manual Reviews
- **Quarterly Audits**: Review file organization
- **Naming Reviews**: Check adherence to conventions
- **Cleanup Sessions**: Remove outdated content

### Git Hooks
- **Pre-commit**: Check new file names
- **Pre-push**: Validate naming conventions
- **Post-merge**: Update documentation index

---

## Examples

### ✅ Good Examples
```
README.md                          # Project overview
API_DOCUMENTATION.md              # API reference
DEPLOYMENT_GUIDE.md               # Deployment instructions
DEPLOYMENT_STATUS_2025-10-24.md  # Status report with date
test-deployment-20251024-143022.md # Test report with timestamp
archive/cleanup-2025-10-24/       # Archive with date
```

### ❌ Bad Examples
```
README_COMPLETE.md                # Redundant completion marker
DEPLOYMENT_FINAL_FINAL.md         # Multiple completion markers
TODAY_REPORT.md                   # Ambiguous date
SOMETHING_IMPORTANT.md            # Vague description
TEMP_NEW_FILE.md                  # Temporary naming
```

---

## Maintenance Schedule

### Daily
- Check new files against conventions
- Update status files as needed

### Weekly
- Review recent additions
- Clean up temporary files

### Monthly
- Archive completed reports
- Update documentation index
- Review naming compliance

### Quarterly
- Full codebase inventory
- Major cleanup and reorganization
- Convention compliance review

---

## Tools and Scripts

### Available Tools
- `scripts/codebase-inventory-analyzer.py` - Full inventory analysis
- `scripts/codebase-archival-tool.py` - Safe file archival
- `scripts/verification-helper.py` - File verification processing
- `scripts/documentation-index-generator.py` - Documentation indexing

### Usage Examples
```bash
# Generate full inventory
python scripts/codebase-inventory-analyzer.py

# Archive redundant files
python scripts/codebase-archival-tool.py --execute

# Process verification files
python scripts/verification-helper.py --mode batch

# Update documentation index
python scripts/documentation-index-generator.py
```

---

## Conclusion

Following these naming conventions will:
- **Prevent redundancy**: Clear patterns avoid duplicate files
- **Improve organization**: Logical grouping and naming
- **Enable automation**: Consistent patterns for tooling
- **Facilitate maintenance**: Easy identification and management
- **Support collaboration**: Clear standards for team members

**Remember**: When in doubt, be descriptive and specific. It's better to have a long, clear filename than a short, ambiguous one.

---

**Document Version**: 1.0  
**Last Updated**: October 24, 2025  
**Next Review**: January 24, 2026
