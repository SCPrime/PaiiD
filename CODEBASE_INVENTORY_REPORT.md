# Codebase Inventory Report
Generated: Fri 10/24/2025 04:21 PM

## Executive Summary

### Overall Statistics
- **Total Files Analyzed**: 538
- **Total Size**: 6.69 MB
- **Code Files**: 309
- **Documentation Files**: 184
- **Other Files**: 45

### Status Breakdown
- **Current** (actively referenced): 226 (42.0%)
- **Redundant** (archival candidates): 80 (14.9%)
- **Needs Verification**: 232 (43.1%)

### Potential Space Savings
- **Redundant File Size**: 0.80 MB
- **Archival Candidates**: 80 files

---

## Redundant Files (Archival Candidates)

These files match redundancy patterns and have no active references:

### Documentation (78)
- `API_CONFIGURATION_COMPLETE.md` (6.5 KB)
- `AUDIT_FIXES_SUMMARY.md` (15.9 KB)
- `AUDIT_REPORT.md` (28.1 KB)
- `AUDIT_SUMMARY.md` (8.9 KB)
- `AUDIT_SUMMARY_2025-10-13.md` (4.8 KB)
- `AUTHENTICATION_COMPLETE.md` (7.8 KB)
- `AUTO_STARTUP_COMPLETE.md` (10.4 KB)
- `BATCH_5D_DEPLOYMENT_COMPLETE.md` (4.6 KB)
- `BATCH_6_DEPLOYMENT_AUTOMATION_COMPLETE.md` (9.9 KB)
- `BATCH_7_PRODUCTION_MONITORING_COMPLETE.md` (5.4 KB)
- `BUG_REPORT_OPTIONS_500.md` (8.5 KB)
- `CHROME_AUTO_LAUNCH_COMPLETE.md` (5.6 KB)
- `CLAUDE_AGENT_IMPLEMENTATION_SUMMARY.md` (9.5 KB)
- `CLEANUP_AUDIT_REPORT.md` (26.0 KB)
- `COMPLETE_DUAL_AI_SETUP_SUMMARY.md` (13.1 KB)
- `COMPLETE_SETUP_SUMMARY.md` (10.8 KB)
- `COMPREHENSIVE_AUDIT_REPORT.md` (25.8 KB)
- `COMPREHENSIVE_AUDIT_REPORT_2025-10-13.md` (21.6 KB)
- `COMPREHENSIVE_AUDIT_REPORT_2025-10-23.md` (15.5 KB)
- `COMPREHENSIVE_FIX_REPORT.md` (13.3 KB)
- `CUsersSSaint-CyrDocumentssourceai-TraderDEPLOYMENT_CHECKLIST.md` (0.0 KB)
- `DEPLOYMENT_CHECKLIST.md` (3.8 KB)
- `DEPLOYMENT_EXECUTION_GUIDE.md` (9.8 KB)
- `DEPLOYMENT_FIXES.md` (4.8 KB)
- `DEPLOYMENT_GUIDE.md` (6.7 KB)
- `DEPLOYMENT_PARITY_VERIFICATION.md` (13.0 KB)
- `DEPLOYMENT_SCRIPTS_README.md` (10.3 KB)
- `DEPLOYMENT_SCRIPT_PARITY.md` (8.6 KB)
- `DEPLOYMENT_STATUS_CHECK.md` (5.5 KB)
- `DEPLOYMENT_STATUS_FINAL.md` (6.2 KB)
- `DEPLOYMENT_SUCCESS_REPORT.md` (15.6 KB)
- `DEPLOYMENT_SUMMARY.md` (8.9 KB)
- `DEPLOYMENT_VERIFICATION.md` (3.8 KB)
- `DEPLOYMENT_VERIFICATION_CHECKLIST.md` (10.7 KB)
- `DEPLOYMENT_VERIFICATION_RESULTS.md` (6.7 KB)
- `DEPLOYMENT_WAITING_ROOM.md` (8.2 KB)
- `EXECUTIVE_REPORT_LOGO_AND_ROADMAP.md` (5.7 KB)
- `FINAL_DEPLOYMENT_REPORT.md` (11.7 KB)
- `FINAL_DEPLOYMENT_SUMMARY.md` (6.1 KB)
- `FIXES_APPLIED_SUMMARY.md` (7.4 KB)
- `FIXES_COMPLETED_REPORT.md` (13.7 KB)
- `FIX_IMPLEMENTATION_PLAN_2025-10-13.md` (21.3 KB)
- `FULL_DEPLOYMENT_VERIFICATION_REPORT.md` (24.9 KB)
- `IMPLEMENTATION_STATUS.md` (5.1 KB)
- `IMPLEMENTATION_STATUS_OPTIONS_FIX.md` (10.0 KB)
- `INCIDENT_REPORT_2e048fe.md` (11.2 KB)
- `INFRASTRUCTURE_SURGERY_COMPLETE.md` (18.3 KB)
- `LAUNCH_STATUS_FINAL.md` (8.0 KB)
- `MARKET_DATA_OPTIMIZATION_COMPLETE.md` (11.3 KB)
- `MCP_SETUP_COMPLETE.md` (12.6 KB)

... and 28 more (see CSV for complete list)

### Code Files (2)
- `backup-database.sh` (1.0 KB) - Matches redundancy pattern; No references found - may be entry point
- `powershell-health-report-20251023-155635.json` (39.4 KB) - Matches redundancy pattern; No references found - may be entry point


---

## Files Needing Verification

These files have no clear references but don't match redundancy patterns. 
They may be entry points, standalone scripts, or truly orphaned files.

### High Priority (Code Files - 90)
- `CLEAN_BUILD.ps1` (refs: 0)
- `CLEAN_BUILD.sh` (refs: 0)
- `EXECUTE-BATCH-7.ps1` (refs: 0)
- `EXECUTE-BATCH-7.sh` (refs: 0)
- `backend/alembic/versions/037b216f2ed1_add_auth_schema_user_sessions_activity_.py` (refs: 0)
- `backend/alembic/versions/0952a611cdfb_initial_schema_users_strategies_trades_.py` (refs: 0)
- `backend/alembic/versions/ad76030fa92e_add_order_templates_table.py` (refs: 0)
- `backend/alembic/versions/c8e4f9b52d31_add_ai_recommendations_table.py` (refs: 0)
- `backend/app/ml/signal_generator.py` (refs: 0)
- `backend/approutersai.py` (refs: 0)
- `backend/data/news_cache/market_1f7d9aceaaafc81c5b04637f6f1ddb5d.json` (refs: 0)
- `backend/data/news_cache/market_276377cf6851a53a6bbe48b2082036ac.json` (refs: 0)
- `backend/data/news_cache/market_27abd2929d3e9675ebc0e8716d536012.json` (refs: 0)
- `backend/data/news_cache/market_e02059e950e4ae6ded2258d7528cc487.json` (refs: 0)
- `backend/railway.json` (refs: 0)
- `backend/scripts/migrate_strategies.py` (refs: 0)
- `backend/test_alpaca_data.py` (refs: 0)
- `backend/test_portfolio_endpoint.py` (refs: 0)
- `backend/test_positions_endpoint.py` (refs: 0)
- `backend/tests/test_analytics.py` (refs: 0)
- `backend/tests/test_api_endpoints.py` (refs: 0)
- `backend/tests/test_auth.py` (refs: 0)
- `backend/tests/test_backtest.py` (refs: 0)
- `backend/tests/test_database.py` (refs: 0)
- `backend/tests/test_imports.py` (refs: 0)
- `backend/tests/test_news.py` (refs: 0)
- `backend/tests/test_orders.py` (refs: 0)
- `backend/tests/test_strategies.py` (refs: 0)
- `backend/verify_config.py` (refs: 0)
- `check-chrome-extensions.ps1` (refs: 0)

... and 60 more (see CSV for complete list)

### Medium Priority (Documentation - 97)
- `API_DOCUMENTATION.md`
- `API_KEY_GUIDE.md`
- `ARCHITECTURE_CLEAN.md`
- `AUDIT_CHECKLIST_DETAILED.md`
- `AUDIT_PRIORITY_MATRIX.md`
- `AUTOMATED_WORKFLOW_GUIDE.md`
- `CHATGPT_FIX_PROMPT.md`
- `CHATGPT_LOCATION_AND_TEST.md`
- `CHATGPT_TEST_PROMPT.md`
- `CHROME_EXTENSIONS_GUIDE.md`
- `CHROME_TEST_SCRIPTS.md`
- `CLAUDE_PROTOCOL.md`
- `COMPONENT_ARCHITECTURE.md`
- `COMPREHENSIVE_AUDIT_PLAN.md`
- `CONNECTION_VERIFIED.md`
- `CONNECTIVITY_TEST_RESULTS.md`
- `CONTRIBUTING.md`
- `CRITICAL_NEXT_STEP.md`
- `CURSOR_MIGRATION_GUIDE.md`
- `DATA_SOURCES.md`

... and 77 more (see CSV for complete list)


---

## Current Files

226 files are actively referenced and in use.

### By Category
- **Code**: 217 files
- **Documentation**: 9 files
- **Other**: 0 files

See CSV file for complete listing.

---

## Recommendations

### Immediate Actions
1. **Archive Redundant Files**: Move 80 redundant files to `archive/` directory
   - Estimated space savings: 0.80 MB
   - Focus on dated reports, COMPLETE.md files, and OLD_* files

2. **Review High Priority Files**: Verify 90 code files with no references
   - These may be entry points or truly orphaned code
   - Determine if they can be deleted or need to be archived

3. **Clean Documentation**: Review 97 documentation files
   - Update README files to reference current documentation
   - Archive or delete outdated guides

### Long-term Actions
1. **Establish Naming Conventions**: Prevent future redundancy by:
   - Using consistent naming for active vs archived files
   - Implementing automatic archival of dated reports
   - Creating a single source of truth for each topic

2. **Regular Audits**: Schedule quarterly codebase inventories to prevent accumulation

3. **Documentation Standards**: Maintain a documentation index that tracks:
   - Active documentation
   - Deprecated/archived documentation
   - Ownership and last update dates

---

## Next Steps

1. Review this report with project leads
2. Get approval for archival candidates listed above
3. Execute archival plan using the CSV file as reference
4. Update project documentation index

For detailed information on each file, refer to: `codebase-inventory.csv`
