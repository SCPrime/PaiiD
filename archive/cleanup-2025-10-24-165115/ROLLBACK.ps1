# Rollback Script - Restore Archived Files
# Generated: 2025-10-24-165115
# Run this script from the repository root to restore archived files

$ErrorActionPreference = 'Stop'

Write-Host "=" * 70
Write-Host "Rollback: Restoring Archived Files"
Write-Host "=" * 70

$restoredCount = 0
$errorCount = 0

# Restore: backup-database.sh
if (Test-Path "archive/cleanup-2025-10-24-165115/backup-database.sh") {
    try {
        $targetDir = Split-Path "backup-database.sh" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/backup-database.sh" -Destination "backup-database.sh" -Force
        Write-Host "✓ Restored: backup-database.sh"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring backup-database.sh: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/backup-database.sh" -ForegroundColor Yellow
}

# Restore: powershell-health-report-20251023-155635.json
if (Test-Path "archive/cleanup-2025-10-24-165115/powershell-health-report-20251023-155635.json") {
    try {
        $targetDir = Split-Path "powershell-health-report-20251023-155635.json" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/powershell-health-report-20251023-155635.json" -Destination "powershell-health-report-20251023-155635.json" -Force
        Write-Host "✓ Restored: powershell-health-report-20251023-155635.json"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring powershell-health-report-20251023-155635.json: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/powershell-health-report-20251023-155635.json" -ForegroundColor Yellow
}

# Restore: API_CONFIGURATION_COMPLETE.md
if (Test-Path "archive/cleanup-2025-10-24-165115/API_CONFIGURATION_COMPLETE.md") {
    try {
        $targetDir = Split-Path "API_CONFIGURATION_COMPLETE.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/API_CONFIGURATION_COMPLETE.md" -Destination "API_CONFIGURATION_COMPLETE.md" -Force
        Write-Host "✓ Restored: API_CONFIGURATION_COMPLETE.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring API_CONFIGURATION_COMPLETE.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/API_CONFIGURATION_COMPLETE.md" -ForegroundColor Yellow
}

# Restore: AUDIT_FIXES_SUMMARY.md
if (Test-Path "archive/cleanup-2025-10-24-165115/AUDIT_FIXES_SUMMARY.md") {
    try {
        $targetDir = Split-Path "AUDIT_FIXES_SUMMARY.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/AUDIT_FIXES_SUMMARY.md" -Destination "AUDIT_FIXES_SUMMARY.md" -Force
        Write-Host "✓ Restored: AUDIT_FIXES_SUMMARY.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring AUDIT_FIXES_SUMMARY.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/AUDIT_FIXES_SUMMARY.md" -ForegroundColor Yellow
}

# Restore: AUDIT_REPORT.md
if (Test-Path "archive/cleanup-2025-10-24-165115/AUDIT_REPORT.md") {
    try {
        $targetDir = Split-Path "AUDIT_REPORT.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/AUDIT_REPORT.md" -Destination "AUDIT_REPORT.md" -Force
        Write-Host "✓ Restored: AUDIT_REPORT.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring AUDIT_REPORT.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/AUDIT_REPORT.md" -ForegroundColor Yellow
}

# Restore: AUDIT_SUMMARY.md
if (Test-Path "archive/cleanup-2025-10-24-165115/AUDIT_SUMMARY.md") {
    try {
        $targetDir = Split-Path "AUDIT_SUMMARY.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/AUDIT_SUMMARY.md" -Destination "AUDIT_SUMMARY.md" -Force
        Write-Host "✓ Restored: AUDIT_SUMMARY.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring AUDIT_SUMMARY.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/AUDIT_SUMMARY.md" -ForegroundColor Yellow
}

# Restore: AUDIT_SUMMARY_2025-10-13.md
if (Test-Path "archive/cleanup-2025-10-24-165115/AUDIT_SUMMARY_2025-10-13.md") {
    try {
        $targetDir = Split-Path "AUDIT_SUMMARY_2025-10-13.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/AUDIT_SUMMARY_2025-10-13.md" -Destination "AUDIT_SUMMARY_2025-10-13.md" -Force
        Write-Host "✓ Restored: AUDIT_SUMMARY_2025-10-13.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring AUDIT_SUMMARY_2025-10-13.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/AUDIT_SUMMARY_2025-10-13.md" -ForegroundColor Yellow
}

# Restore: AUTHENTICATION_COMPLETE.md
if (Test-Path "archive/cleanup-2025-10-24-165115/AUTHENTICATION_COMPLETE.md") {
    try {
        $targetDir = Split-Path "AUTHENTICATION_COMPLETE.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/AUTHENTICATION_COMPLETE.md" -Destination "AUTHENTICATION_COMPLETE.md" -Force
        Write-Host "✓ Restored: AUTHENTICATION_COMPLETE.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring AUTHENTICATION_COMPLETE.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/AUTHENTICATION_COMPLETE.md" -ForegroundColor Yellow
}

# Restore: AUTO_STARTUP_COMPLETE.md
if (Test-Path "archive/cleanup-2025-10-24-165115/AUTO_STARTUP_COMPLETE.md") {
    try {
        $targetDir = Split-Path "AUTO_STARTUP_COMPLETE.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/AUTO_STARTUP_COMPLETE.md" -Destination "AUTO_STARTUP_COMPLETE.md" -Force
        Write-Host "✓ Restored: AUTO_STARTUP_COMPLETE.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring AUTO_STARTUP_COMPLETE.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/AUTO_STARTUP_COMPLETE.md" -ForegroundColor Yellow
}

# Restore: BATCH_5D_DEPLOYMENT_COMPLETE.md
if (Test-Path "archive/cleanup-2025-10-24-165115/BATCH_5D_DEPLOYMENT_COMPLETE.md") {
    try {
        $targetDir = Split-Path "BATCH_5D_DEPLOYMENT_COMPLETE.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/BATCH_5D_DEPLOYMENT_COMPLETE.md" -Destination "BATCH_5D_DEPLOYMENT_COMPLETE.md" -Force
        Write-Host "✓ Restored: BATCH_5D_DEPLOYMENT_COMPLETE.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring BATCH_5D_DEPLOYMENT_COMPLETE.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/BATCH_5D_DEPLOYMENT_COMPLETE.md" -ForegroundColor Yellow
}

# Restore: BATCH_6_DEPLOYMENT_AUTOMATION_COMPLETE.md
if (Test-Path "archive/cleanup-2025-10-24-165115/BATCH_6_DEPLOYMENT_AUTOMATION_COMPLETE.md") {
    try {
        $targetDir = Split-Path "BATCH_6_DEPLOYMENT_AUTOMATION_COMPLETE.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/BATCH_6_DEPLOYMENT_AUTOMATION_COMPLETE.md" -Destination "BATCH_6_DEPLOYMENT_AUTOMATION_COMPLETE.md" -Force
        Write-Host "✓ Restored: BATCH_6_DEPLOYMENT_AUTOMATION_COMPLETE.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring BATCH_6_DEPLOYMENT_AUTOMATION_COMPLETE.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/BATCH_6_DEPLOYMENT_AUTOMATION_COMPLETE.md" -ForegroundColor Yellow
}

# Restore: BATCH_7_PRODUCTION_MONITORING_COMPLETE.md
if (Test-Path "archive/cleanup-2025-10-24-165115/BATCH_7_PRODUCTION_MONITORING_COMPLETE.md") {
    try {
        $targetDir = Split-Path "BATCH_7_PRODUCTION_MONITORING_COMPLETE.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/BATCH_7_PRODUCTION_MONITORING_COMPLETE.md" -Destination "BATCH_7_PRODUCTION_MONITORING_COMPLETE.md" -Force
        Write-Host "✓ Restored: BATCH_7_PRODUCTION_MONITORING_COMPLETE.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring BATCH_7_PRODUCTION_MONITORING_COMPLETE.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/BATCH_7_PRODUCTION_MONITORING_COMPLETE.md" -ForegroundColor Yellow
}

# Restore: BUG_REPORT_OPTIONS_500.md
if (Test-Path "archive/cleanup-2025-10-24-165115/BUG_REPORT_OPTIONS_500.md") {
    try {
        $targetDir = Split-Path "BUG_REPORT_OPTIONS_500.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/BUG_REPORT_OPTIONS_500.md" -Destination "BUG_REPORT_OPTIONS_500.md" -Force
        Write-Host "✓ Restored: BUG_REPORT_OPTIONS_500.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring BUG_REPORT_OPTIONS_500.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/BUG_REPORT_OPTIONS_500.md" -ForegroundColor Yellow
}

# Restore: CHROME_AUTO_LAUNCH_COMPLETE.md
if (Test-Path "archive/cleanup-2025-10-24-165115/CHROME_AUTO_LAUNCH_COMPLETE.md") {
    try {
        $targetDir = Split-Path "CHROME_AUTO_LAUNCH_COMPLETE.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/CHROME_AUTO_LAUNCH_COMPLETE.md" -Destination "CHROME_AUTO_LAUNCH_COMPLETE.md" -Force
        Write-Host "✓ Restored: CHROME_AUTO_LAUNCH_COMPLETE.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring CHROME_AUTO_LAUNCH_COMPLETE.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/CHROME_AUTO_LAUNCH_COMPLETE.md" -ForegroundColor Yellow
}

# Restore: CLAUDE_AGENT_IMPLEMENTATION_SUMMARY.md
if (Test-Path "archive/cleanup-2025-10-24-165115/CLAUDE_AGENT_IMPLEMENTATION_SUMMARY.md") {
    try {
        $targetDir = Split-Path "CLAUDE_AGENT_IMPLEMENTATION_SUMMARY.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/CLAUDE_AGENT_IMPLEMENTATION_SUMMARY.md" -Destination "CLAUDE_AGENT_IMPLEMENTATION_SUMMARY.md" -Force
        Write-Host "✓ Restored: CLAUDE_AGENT_IMPLEMENTATION_SUMMARY.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring CLAUDE_AGENT_IMPLEMENTATION_SUMMARY.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/CLAUDE_AGENT_IMPLEMENTATION_SUMMARY.md" -ForegroundColor Yellow
}

# Restore: CLEANUP_AUDIT_REPORT.md
if (Test-Path "archive/cleanup-2025-10-24-165115/CLEANUP_AUDIT_REPORT.md") {
    try {
        $targetDir = Split-Path "CLEANUP_AUDIT_REPORT.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/CLEANUP_AUDIT_REPORT.md" -Destination "CLEANUP_AUDIT_REPORT.md" -Force
        Write-Host "✓ Restored: CLEANUP_AUDIT_REPORT.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring CLEANUP_AUDIT_REPORT.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/CLEANUP_AUDIT_REPORT.md" -ForegroundColor Yellow
}

# Restore: COMPLETE_DUAL_AI_SETUP_SUMMARY.md
if (Test-Path "archive/cleanup-2025-10-24-165115/COMPLETE_DUAL_AI_SETUP_SUMMARY.md") {
    try {
        $targetDir = Split-Path "COMPLETE_DUAL_AI_SETUP_SUMMARY.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/COMPLETE_DUAL_AI_SETUP_SUMMARY.md" -Destination "COMPLETE_DUAL_AI_SETUP_SUMMARY.md" -Force
        Write-Host "✓ Restored: COMPLETE_DUAL_AI_SETUP_SUMMARY.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring COMPLETE_DUAL_AI_SETUP_SUMMARY.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/COMPLETE_DUAL_AI_SETUP_SUMMARY.md" -ForegroundColor Yellow
}

# Restore: COMPLETE_SETUP_SUMMARY.md
if (Test-Path "archive/cleanup-2025-10-24-165115/COMPLETE_SETUP_SUMMARY.md") {
    try {
        $targetDir = Split-Path "COMPLETE_SETUP_SUMMARY.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/COMPLETE_SETUP_SUMMARY.md" -Destination "COMPLETE_SETUP_SUMMARY.md" -Force
        Write-Host "✓ Restored: COMPLETE_SETUP_SUMMARY.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring COMPLETE_SETUP_SUMMARY.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/COMPLETE_SETUP_SUMMARY.md" -ForegroundColor Yellow
}

# Restore: COMPREHENSIVE_AUDIT_REPORT.md
if (Test-Path "archive/cleanup-2025-10-24-165115/COMPREHENSIVE_AUDIT_REPORT.md") {
    try {
        $targetDir = Split-Path "COMPREHENSIVE_AUDIT_REPORT.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/COMPREHENSIVE_AUDIT_REPORT.md" -Destination "COMPREHENSIVE_AUDIT_REPORT.md" -Force
        Write-Host "✓ Restored: COMPREHENSIVE_AUDIT_REPORT.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring COMPREHENSIVE_AUDIT_REPORT.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/COMPREHENSIVE_AUDIT_REPORT.md" -ForegroundColor Yellow
}

# Restore: COMPREHENSIVE_AUDIT_REPORT_2025-10-13.md
if (Test-Path "archive/cleanup-2025-10-24-165115/COMPREHENSIVE_AUDIT_REPORT_2025-10-13.md") {
    try {
        $targetDir = Split-Path "COMPREHENSIVE_AUDIT_REPORT_2025-10-13.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/COMPREHENSIVE_AUDIT_REPORT_2025-10-13.md" -Destination "COMPREHENSIVE_AUDIT_REPORT_2025-10-13.md" -Force
        Write-Host "✓ Restored: COMPREHENSIVE_AUDIT_REPORT_2025-10-13.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring COMPREHENSIVE_AUDIT_REPORT_2025-10-13.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/COMPREHENSIVE_AUDIT_REPORT_2025-10-13.md" -ForegroundColor Yellow
}

# Restore: COMPREHENSIVE_AUDIT_REPORT_2025-10-23.md
if (Test-Path "archive/cleanup-2025-10-24-165115/COMPREHENSIVE_AUDIT_REPORT_2025-10-23.md") {
    try {
        $targetDir = Split-Path "COMPREHENSIVE_AUDIT_REPORT_2025-10-23.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/COMPREHENSIVE_AUDIT_REPORT_2025-10-23.md" -Destination "COMPREHENSIVE_AUDIT_REPORT_2025-10-23.md" -Force
        Write-Host "✓ Restored: COMPREHENSIVE_AUDIT_REPORT_2025-10-23.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring COMPREHENSIVE_AUDIT_REPORT_2025-10-23.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/COMPREHENSIVE_AUDIT_REPORT_2025-10-23.md" -ForegroundColor Yellow
}

# Restore: COMPREHENSIVE_FIX_REPORT.md
if (Test-Path "archive/cleanup-2025-10-24-165115/COMPREHENSIVE_FIX_REPORT.md") {
    try {
        $targetDir = Split-Path "COMPREHENSIVE_FIX_REPORT.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/COMPREHENSIVE_FIX_REPORT.md" -Destination "COMPREHENSIVE_FIX_REPORT.md" -Force
        Write-Host "✓ Restored: COMPREHENSIVE_FIX_REPORT.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring COMPREHENSIVE_FIX_REPORT.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/COMPREHENSIVE_FIX_REPORT.md" -ForegroundColor Yellow
}

# Restore: CUsersSSaint-CyrDocumentssourceai-TraderDEPLOYMENT_CHECKLIST.md
if (Test-Path "archive/cleanup-2025-10-24-165115/CUsersSSaint-CyrDocumentssourceai-TraderDEPLOYMENT_CHECKLIST.md") {
    try {
        $targetDir = Split-Path "CUsersSSaint-CyrDocumentssourceai-TraderDEPLOYMENT_CHECKLIST.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/CUsersSSaint-CyrDocumentssourceai-TraderDEPLOYMENT_CHECKLIST.md" -Destination "CUsersSSaint-CyrDocumentssourceai-TraderDEPLOYMENT_CHECKLIST.md" -Force
        Write-Host "✓ Restored: CUsersSSaint-CyrDocumentssourceai-TraderDEPLOYMENT_CHECKLIST.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring CUsersSSaint-CyrDocumentssourceai-TraderDEPLOYMENT_CHECKLIST.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/CUsersSSaint-CyrDocumentssourceai-TraderDEPLOYMENT_CHECKLIST.md" -ForegroundColor Yellow
}

# Restore: DEPLOYMENT_CHECKLIST.md
if (Test-Path "archive/cleanup-2025-10-24-165115/DEPLOYMENT_CHECKLIST.md") {
    try {
        $targetDir = Split-Path "DEPLOYMENT_CHECKLIST.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/DEPLOYMENT_CHECKLIST.md" -Destination "DEPLOYMENT_CHECKLIST.md" -Force
        Write-Host "✓ Restored: DEPLOYMENT_CHECKLIST.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring DEPLOYMENT_CHECKLIST.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/DEPLOYMENT_CHECKLIST.md" -ForegroundColor Yellow
}

# Restore: DEPLOYMENT_EXECUTION_GUIDE.md
if (Test-Path "archive/cleanup-2025-10-24-165115/DEPLOYMENT_EXECUTION_GUIDE.md") {
    try {
        $targetDir = Split-Path "DEPLOYMENT_EXECUTION_GUIDE.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/DEPLOYMENT_EXECUTION_GUIDE.md" -Destination "DEPLOYMENT_EXECUTION_GUIDE.md" -Force
        Write-Host "✓ Restored: DEPLOYMENT_EXECUTION_GUIDE.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring DEPLOYMENT_EXECUTION_GUIDE.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/DEPLOYMENT_EXECUTION_GUIDE.md" -ForegroundColor Yellow
}

# Restore: DEPLOYMENT_FIXES.md
if (Test-Path "archive/cleanup-2025-10-24-165115/DEPLOYMENT_FIXES.md") {
    try {
        $targetDir = Split-Path "DEPLOYMENT_FIXES.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/DEPLOYMENT_FIXES.md" -Destination "DEPLOYMENT_FIXES.md" -Force
        Write-Host "✓ Restored: DEPLOYMENT_FIXES.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring DEPLOYMENT_FIXES.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/DEPLOYMENT_FIXES.md" -ForegroundColor Yellow
}

# Restore: DEPLOYMENT_GUIDE.md
if (Test-Path "archive/cleanup-2025-10-24-165115/DEPLOYMENT_GUIDE.md") {
    try {
        $targetDir = Split-Path "DEPLOYMENT_GUIDE.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/DEPLOYMENT_GUIDE.md" -Destination "DEPLOYMENT_GUIDE.md" -Force
        Write-Host "✓ Restored: DEPLOYMENT_GUIDE.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring DEPLOYMENT_GUIDE.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/DEPLOYMENT_GUIDE.md" -ForegroundColor Yellow
}

# Restore: DEPLOYMENT_PARITY_VERIFICATION.md
if (Test-Path "archive/cleanup-2025-10-24-165115/DEPLOYMENT_PARITY_VERIFICATION.md") {
    try {
        $targetDir = Split-Path "DEPLOYMENT_PARITY_VERIFICATION.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/DEPLOYMENT_PARITY_VERIFICATION.md" -Destination "DEPLOYMENT_PARITY_VERIFICATION.md" -Force
        Write-Host "✓ Restored: DEPLOYMENT_PARITY_VERIFICATION.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring DEPLOYMENT_PARITY_VERIFICATION.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/DEPLOYMENT_PARITY_VERIFICATION.md" -ForegroundColor Yellow
}

# Restore: DEPLOYMENT_SCRIPTS_README.md
if (Test-Path "archive/cleanup-2025-10-24-165115/DEPLOYMENT_SCRIPTS_README.md") {
    try {
        $targetDir = Split-Path "DEPLOYMENT_SCRIPTS_README.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/DEPLOYMENT_SCRIPTS_README.md" -Destination "DEPLOYMENT_SCRIPTS_README.md" -Force
        Write-Host "✓ Restored: DEPLOYMENT_SCRIPTS_README.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring DEPLOYMENT_SCRIPTS_README.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/DEPLOYMENT_SCRIPTS_README.md" -ForegroundColor Yellow
}

# Restore: DEPLOYMENT_SCRIPT_PARITY.md
if (Test-Path "archive/cleanup-2025-10-24-165115/DEPLOYMENT_SCRIPT_PARITY.md") {
    try {
        $targetDir = Split-Path "DEPLOYMENT_SCRIPT_PARITY.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/DEPLOYMENT_SCRIPT_PARITY.md" -Destination "DEPLOYMENT_SCRIPT_PARITY.md" -Force
        Write-Host "✓ Restored: DEPLOYMENT_SCRIPT_PARITY.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring DEPLOYMENT_SCRIPT_PARITY.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/DEPLOYMENT_SCRIPT_PARITY.md" -ForegroundColor Yellow
}

# Restore: DEPLOYMENT_STATUS_CHECK.md
if (Test-Path "archive/cleanup-2025-10-24-165115/DEPLOYMENT_STATUS_CHECK.md") {
    try {
        $targetDir = Split-Path "DEPLOYMENT_STATUS_CHECK.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/DEPLOYMENT_STATUS_CHECK.md" -Destination "DEPLOYMENT_STATUS_CHECK.md" -Force
        Write-Host "✓ Restored: DEPLOYMENT_STATUS_CHECK.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring DEPLOYMENT_STATUS_CHECK.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/DEPLOYMENT_STATUS_CHECK.md" -ForegroundColor Yellow
}

# Restore: DEPLOYMENT_STATUS_FINAL.md
if (Test-Path "archive/cleanup-2025-10-24-165115/DEPLOYMENT_STATUS_FINAL.md") {
    try {
        $targetDir = Split-Path "DEPLOYMENT_STATUS_FINAL.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/DEPLOYMENT_STATUS_FINAL.md" -Destination "DEPLOYMENT_STATUS_FINAL.md" -Force
        Write-Host "✓ Restored: DEPLOYMENT_STATUS_FINAL.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring DEPLOYMENT_STATUS_FINAL.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/DEPLOYMENT_STATUS_FINAL.md" -ForegroundColor Yellow
}

# Restore: DEPLOYMENT_SUCCESS_REPORT.md
if (Test-Path "archive/cleanup-2025-10-24-165115/DEPLOYMENT_SUCCESS_REPORT.md") {
    try {
        $targetDir = Split-Path "DEPLOYMENT_SUCCESS_REPORT.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/DEPLOYMENT_SUCCESS_REPORT.md" -Destination "DEPLOYMENT_SUCCESS_REPORT.md" -Force
        Write-Host "✓ Restored: DEPLOYMENT_SUCCESS_REPORT.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring DEPLOYMENT_SUCCESS_REPORT.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/DEPLOYMENT_SUCCESS_REPORT.md" -ForegroundColor Yellow
}

# Restore: DEPLOYMENT_SUMMARY.md
if (Test-Path "archive/cleanup-2025-10-24-165115/DEPLOYMENT_SUMMARY.md") {
    try {
        $targetDir = Split-Path "DEPLOYMENT_SUMMARY.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/DEPLOYMENT_SUMMARY.md" -Destination "DEPLOYMENT_SUMMARY.md" -Force
        Write-Host "✓ Restored: DEPLOYMENT_SUMMARY.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring DEPLOYMENT_SUMMARY.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/DEPLOYMENT_SUMMARY.md" -ForegroundColor Yellow
}

# Restore: DEPLOYMENT_VERIFICATION.md
if (Test-Path "archive/cleanup-2025-10-24-165115/DEPLOYMENT_VERIFICATION.md") {
    try {
        $targetDir = Split-Path "DEPLOYMENT_VERIFICATION.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/DEPLOYMENT_VERIFICATION.md" -Destination "DEPLOYMENT_VERIFICATION.md" -Force
        Write-Host "✓ Restored: DEPLOYMENT_VERIFICATION.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring DEPLOYMENT_VERIFICATION.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/DEPLOYMENT_VERIFICATION.md" -ForegroundColor Yellow
}

# Restore: DEPLOYMENT_VERIFICATION_CHECKLIST.md
if (Test-Path "archive/cleanup-2025-10-24-165115/DEPLOYMENT_VERIFICATION_CHECKLIST.md") {
    try {
        $targetDir = Split-Path "DEPLOYMENT_VERIFICATION_CHECKLIST.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/DEPLOYMENT_VERIFICATION_CHECKLIST.md" -Destination "DEPLOYMENT_VERIFICATION_CHECKLIST.md" -Force
        Write-Host "✓ Restored: DEPLOYMENT_VERIFICATION_CHECKLIST.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring DEPLOYMENT_VERIFICATION_CHECKLIST.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/DEPLOYMENT_VERIFICATION_CHECKLIST.md" -ForegroundColor Yellow
}

# Restore: DEPLOYMENT_VERIFICATION_RESULTS.md
if (Test-Path "archive/cleanup-2025-10-24-165115/DEPLOYMENT_VERIFICATION_RESULTS.md") {
    try {
        $targetDir = Split-Path "DEPLOYMENT_VERIFICATION_RESULTS.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/DEPLOYMENT_VERIFICATION_RESULTS.md" -Destination "DEPLOYMENT_VERIFICATION_RESULTS.md" -Force
        Write-Host "✓ Restored: DEPLOYMENT_VERIFICATION_RESULTS.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring DEPLOYMENT_VERIFICATION_RESULTS.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/DEPLOYMENT_VERIFICATION_RESULTS.md" -ForegroundColor Yellow
}

# Restore: DEPLOYMENT_WAITING_ROOM.md
if (Test-Path "archive/cleanup-2025-10-24-165115/DEPLOYMENT_WAITING_ROOM.md") {
    try {
        $targetDir = Split-Path "DEPLOYMENT_WAITING_ROOM.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/DEPLOYMENT_WAITING_ROOM.md" -Destination "DEPLOYMENT_WAITING_ROOM.md" -Force
        Write-Host "✓ Restored: DEPLOYMENT_WAITING_ROOM.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring DEPLOYMENT_WAITING_ROOM.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/DEPLOYMENT_WAITING_ROOM.md" -ForegroundColor Yellow
}

# Restore: EXECUTIVE_REPORT_LOGO_AND_ROADMAP.md
if (Test-Path "archive/cleanup-2025-10-24-165115/EXECUTIVE_REPORT_LOGO_AND_ROADMAP.md") {
    try {
        $targetDir = Split-Path "EXECUTIVE_REPORT_LOGO_AND_ROADMAP.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/EXECUTIVE_REPORT_LOGO_AND_ROADMAP.md" -Destination "EXECUTIVE_REPORT_LOGO_AND_ROADMAP.md" -Force
        Write-Host "✓ Restored: EXECUTIVE_REPORT_LOGO_AND_ROADMAP.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring EXECUTIVE_REPORT_LOGO_AND_ROADMAP.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/EXECUTIVE_REPORT_LOGO_AND_ROADMAP.md" -ForegroundColor Yellow
}

# Restore: FINAL_DEPLOYMENT_REPORT.md
if (Test-Path "archive/cleanup-2025-10-24-165115/FINAL_DEPLOYMENT_REPORT.md") {
    try {
        $targetDir = Split-Path "FINAL_DEPLOYMENT_REPORT.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/FINAL_DEPLOYMENT_REPORT.md" -Destination "FINAL_DEPLOYMENT_REPORT.md" -Force
        Write-Host "✓ Restored: FINAL_DEPLOYMENT_REPORT.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring FINAL_DEPLOYMENT_REPORT.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/FINAL_DEPLOYMENT_REPORT.md" -ForegroundColor Yellow
}

# Restore: FINAL_DEPLOYMENT_SUMMARY.md
if (Test-Path "archive/cleanup-2025-10-24-165115/FINAL_DEPLOYMENT_SUMMARY.md") {
    try {
        $targetDir = Split-Path "FINAL_DEPLOYMENT_SUMMARY.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/FINAL_DEPLOYMENT_SUMMARY.md" -Destination "FINAL_DEPLOYMENT_SUMMARY.md" -Force
        Write-Host "✓ Restored: FINAL_DEPLOYMENT_SUMMARY.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring FINAL_DEPLOYMENT_SUMMARY.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/FINAL_DEPLOYMENT_SUMMARY.md" -ForegroundColor Yellow
}

# Restore: FIXES_APPLIED_SUMMARY.md
if (Test-Path "archive/cleanup-2025-10-24-165115/FIXES_APPLIED_SUMMARY.md") {
    try {
        $targetDir = Split-Path "FIXES_APPLIED_SUMMARY.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/FIXES_APPLIED_SUMMARY.md" -Destination "FIXES_APPLIED_SUMMARY.md" -Force
        Write-Host "✓ Restored: FIXES_APPLIED_SUMMARY.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring FIXES_APPLIED_SUMMARY.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/FIXES_APPLIED_SUMMARY.md" -ForegroundColor Yellow
}

# Restore: FIXES_COMPLETED_REPORT.md
if (Test-Path "archive/cleanup-2025-10-24-165115/FIXES_COMPLETED_REPORT.md") {
    try {
        $targetDir = Split-Path "FIXES_COMPLETED_REPORT.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/FIXES_COMPLETED_REPORT.md" -Destination "FIXES_COMPLETED_REPORT.md" -Force
        Write-Host "✓ Restored: FIXES_COMPLETED_REPORT.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring FIXES_COMPLETED_REPORT.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/FIXES_COMPLETED_REPORT.md" -ForegroundColor Yellow
}

# Restore: FIX_IMPLEMENTATION_PLAN_2025-10-13.md
if (Test-Path "archive/cleanup-2025-10-24-165115/FIX_IMPLEMENTATION_PLAN_2025-10-13.md") {
    try {
        $targetDir = Split-Path "FIX_IMPLEMENTATION_PLAN_2025-10-13.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/FIX_IMPLEMENTATION_PLAN_2025-10-13.md" -Destination "FIX_IMPLEMENTATION_PLAN_2025-10-13.md" -Force
        Write-Host "✓ Restored: FIX_IMPLEMENTATION_PLAN_2025-10-13.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring FIX_IMPLEMENTATION_PLAN_2025-10-13.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/FIX_IMPLEMENTATION_PLAN_2025-10-13.md" -ForegroundColor Yellow
}

# Restore: FULL_DEPLOYMENT_VERIFICATION_REPORT.md
if (Test-Path "archive/cleanup-2025-10-24-165115/FULL_DEPLOYMENT_VERIFICATION_REPORT.md") {
    try {
        $targetDir = Split-Path "FULL_DEPLOYMENT_VERIFICATION_REPORT.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/FULL_DEPLOYMENT_VERIFICATION_REPORT.md" -Destination "FULL_DEPLOYMENT_VERIFICATION_REPORT.md" -Force
        Write-Host "✓ Restored: FULL_DEPLOYMENT_VERIFICATION_REPORT.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring FULL_DEPLOYMENT_VERIFICATION_REPORT.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/FULL_DEPLOYMENT_VERIFICATION_REPORT.md" -ForegroundColor Yellow
}

# Restore: IMPLEMENTATION_STATUS.md
if (Test-Path "archive/cleanup-2025-10-24-165115/IMPLEMENTATION_STATUS.md") {
    try {
        $targetDir = Split-Path "IMPLEMENTATION_STATUS.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/IMPLEMENTATION_STATUS.md" -Destination "IMPLEMENTATION_STATUS.md" -Force
        Write-Host "✓ Restored: IMPLEMENTATION_STATUS.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring IMPLEMENTATION_STATUS.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/IMPLEMENTATION_STATUS.md" -ForegroundColor Yellow
}

# Restore: IMPLEMENTATION_STATUS_OPTIONS_FIX.md
if (Test-Path "archive/cleanup-2025-10-24-165115/IMPLEMENTATION_STATUS_OPTIONS_FIX.md") {
    try {
        $targetDir = Split-Path "IMPLEMENTATION_STATUS_OPTIONS_FIX.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/IMPLEMENTATION_STATUS_OPTIONS_FIX.md" -Destination "IMPLEMENTATION_STATUS_OPTIONS_FIX.md" -Force
        Write-Host "✓ Restored: IMPLEMENTATION_STATUS_OPTIONS_FIX.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring IMPLEMENTATION_STATUS_OPTIONS_FIX.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/IMPLEMENTATION_STATUS_OPTIONS_FIX.md" -ForegroundColor Yellow
}

# Restore: INCIDENT_REPORT_2e048fe.md
if (Test-Path "archive/cleanup-2025-10-24-165115/INCIDENT_REPORT_2e048fe.md") {
    try {
        $targetDir = Split-Path "INCIDENT_REPORT_2e048fe.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/INCIDENT_REPORT_2e048fe.md" -Destination "INCIDENT_REPORT_2e048fe.md" -Force
        Write-Host "✓ Restored: INCIDENT_REPORT_2e048fe.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring INCIDENT_REPORT_2e048fe.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/INCIDENT_REPORT_2e048fe.md" -ForegroundColor Yellow
}

# Restore: INFRASTRUCTURE_SURGERY_COMPLETE.md
if (Test-Path "archive/cleanup-2025-10-24-165115/INFRASTRUCTURE_SURGERY_COMPLETE.md") {
    try {
        $targetDir = Split-Path "INFRASTRUCTURE_SURGERY_COMPLETE.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/INFRASTRUCTURE_SURGERY_COMPLETE.md" -Destination "INFRASTRUCTURE_SURGERY_COMPLETE.md" -Force
        Write-Host "✓ Restored: INFRASTRUCTURE_SURGERY_COMPLETE.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring INFRASTRUCTURE_SURGERY_COMPLETE.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/INFRASTRUCTURE_SURGERY_COMPLETE.md" -ForegroundColor Yellow
}

# Restore: LAUNCH_STATUS_FINAL.md
if (Test-Path "archive/cleanup-2025-10-24-165115/LAUNCH_STATUS_FINAL.md") {
    try {
        $targetDir = Split-Path "LAUNCH_STATUS_FINAL.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/LAUNCH_STATUS_FINAL.md" -Destination "LAUNCH_STATUS_FINAL.md" -Force
        Write-Host "✓ Restored: LAUNCH_STATUS_FINAL.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring LAUNCH_STATUS_FINAL.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/LAUNCH_STATUS_FINAL.md" -ForegroundColor Yellow
}

# Restore: MARKET_DATA_OPTIMIZATION_COMPLETE.md
if (Test-Path "archive/cleanup-2025-10-24-165115/MARKET_DATA_OPTIMIZATION_COMPLETE.md") {
    try {
        $targetDir = Split-Path "MARKET_DATA_OPTIMIZATION_COMPLETE.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/MARKET_DATA_OPTIMIZATION_COMPLETE.md" -Destination "MARKET_DATA_OPTIMIZATION_COMPLETE.md" -Force
        Write-Host "✓ Restored: MARKET_DATA_OPTIMIZATION_COMPLETE.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring MARKET_DATA_OPTIMIZATION_COMPLETE.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/MARKET_DATA_OPTIMIZATION_COMPLETE.md" -ForegroundColor Yellow
}

# Restore: MCP_SETUP_COMPLETE.md
if (Test-Path "archive/cleanup-2025-10-24-165115/MCP_SETUP_COMPLETE.md") {
    try {
        $targetDir = Split-Path "MCP_SETUP_COMPLETE.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/MCP_SETUP_COMPLETE.md" -Destination "MCP_SETUP_COMPLETE.md" -Force
        Write-Host "✓ Restored: MCP_SETUP_COMPLETE.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring MCP_SETUP_COMPLETE.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/MCP_SETUP_COMPLETE.md" -ForegroundColor Yellow
}

# Restore: MCP_VERIFICATION_REPORT.md
if (Test-Path "archive/cleanup-2025-10-24-165115/MCP_VERIFICATION_REPORT.md") {
    try {
        $targetDir = Split-Path "MCP_VERIFICATION_REPORT.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/MCP_VERIFICATION_REPORT.md" -Destination "MCP_VERIFICATION_REPORT.md" -Force
        Write-Host "✓ Restored: MCP_VERIFICATION_REPORT.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring MCP_VERIFICATION_REPORT.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/MCP_VERIFICATION_REPORT.md" -ForegroundColor Yellow
}

# Restore: MOBILE_AUDIT_REPORT.md
if (Test-Path "archive/cleanup-2025-10-24-165115/MOBILE_AUDIT_REPORT.md") {
    try {
        $targetDir = Split-Path "MOBILE_AUDIT_REPORT.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/MOBILE_AUDIT_REPORT.md" -Destination "MOBILE_AUDIT_REPORT.md" -Force
        Write-Host "✓ Restored: MOBILE_AUDIT_REPORT.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring MOBILE_AUDIT_REPORT.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/MOBILE_AUDIT_REPORT.md" -ForegroundColor Yellow
}

# Restore: OLD_JAVASCRIPT_EXCISION_REPORT.md
if (Test-Path "archive/cleanup-2025-10-24-165115/OLD_JAVASCRIPT_EXCISION_REPORT.md") {
    try {
        $targetDir = Split-Path "OLD_JAVASCRIPT_EXCISION_REPORT.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/OLD_JAVASCRIPT_EXCISION_REPORT.md" -Destination "OLD_JAVASCRIPT_EXCISION_REPORT.md" -Force
        Write-Host "✓ Restored: OLD_JAVASCRIPT_EXCISION_REPORT.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring OLD_JAVASCRIPT_EXCISION_REPORT.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/OLD_JAVASCRIPT_EXCISION_REPORT.md" -ForegroundColor Yellow
}

# Restore: OPTIONS_ENDPOINT_DEBUG_REPORT.md
if (Test-Path "archive/cleanup-2025-10-24-165115/OPTIONS_ENDPOINT_DEBUG_REPORT.md") {
    try {
        $targetDir = Split-Path "OPTIONS_ENDPOINT_DEBUG_REPORT.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/OPTIONS_ENDPOINT_DEBUG_REPORT.md" -Destination "OPTIONS_ENDPOINT_DEBUG_REPORT.md" -Force
        Write-Host "✓ Restored: OPTIONS_ENDPOINT_DEBUG_REPORT.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring OPTIONS_ENDPOINT_DEBUG_REPORT.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/OPTIONS_ENDPOINT_DEBUG_REPORT.md" -ForegroundColor Yellow
}

# Restore: OPTIONS_ENDPOINT_FIX_SUMMARY.md
if (Test-Path "archive/cleanup-2025-10-24-165115/OPTIONS_ENDPOINT_FIX_SUMMARY.md") {
    try {
        $targetDir = Split-Path "OPTIONS_ENDPOINT_FIX_SUMMARY.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/OPTIONS_ENDPOINT_FIX_SUMMARY.md" -Destination "OPTIONS_ENDPOINT_FIX_SUMMARY.md" -Force
        Write-Host "✓ Restored: OPTIONS_ENDPOINT_FIX_SUMMARY.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring OPTIONS_ENDPOINT_FIX_SUMMARY.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/OPTIONS_ENDPOINT_FIX_SUMMARY.md" -ForegroundColor Yellow
}

# Restore: OPTIONS_TRADING_COMPLETE.md
if (Test-Path "archive/cleanup-2025-10-24-165115/OPTIONS_TRADING_COMPLETE.md") {
    try {
        $targetDir = Split-Path "OPTIONS_TRADING_COMPLETE.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/OPTIONS_TRADING_COMPLETE.md" -Destination "OPTIONS_TRADING_COMPLETE.md" -Force
        Write-Host "✓ Restored: OPTIONS_TRADING_COMPLETE.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring OPTIONS_TRADING_COMPLETE.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/OPTIONS_TRADING_COMPLETE.md" -ForegroundColor Yellow
}

# Restore: PARASITE_DEPENDENCY_SCAN_REPORT.md
if (Test-Path "archive/cleanup-2025-10-24-165115/PARASITE_DEPENDENCY_SCAN_REPORT.md") {
    try {
        $targetDir = Split-Path "PARASITE_DEPENDENCY_SCAN_REPORT.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/PARASITE_DEPENDENCY_SCAN_REPORT.md" -Destination "PARASITE_DEPENDENCY_SCAN_REPORT.md" -Force
        Write-Host "✓ Restored: PARASITE_DEPENDENCY_SCAN_REPORT.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring PARASITE_DEPENDENCY_SCAN_REPORT.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/PARASITE_DEPENDENCY_SCAN_REPORT.md" -ForegroundColor Yellow
}

# Restore: PHASE1_VERIFICATION_REPORT.md
if (Test-Path "archive/cleanup-2025-10-24-165115/PHASE1_VERIFICATION_REPORT.md") {
    try {
        $targetDir = Split-Path "PHASE1_VERIFICATION_REPORT.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/PHASE1_VERIFICATION_REPORT.md" -Destination "PHASE1_VERIFICATION_REPORT.md" -Force
        Write-Host "✓ Restored: PHASE1_VERIFICATION_REPORT.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring PHASE1_VERIFICATION_REPORT.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/PHASE1_VERIFICATION_REPORT.md" -ForegroundColor Yellow
}

# Restore: PHASE_0_AUDIT_REPORT.md
if (Test-Path "archive/cleanup-2025-10-24-165115/PHASE_0_AUDIT_REPORT.md") {
    try {
        $targetDir = Split-Path "PHASE_0_AUDIT_REPORT.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/PHASE_0_AUDIT_REPORT.md" -Destination "PHASE_0_AUDIT_REPORT.md" -Force
        Write-Host "✓ Restored: PHASE_0_AUDIT_REPORT.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring PHASE_0_AUDIT_REPORT.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/PHASE_0_AUDIT_REPORT.md" -ForegroundColor Yellow
}

# Restore: PHASE_STATUS_2025-10-13.md
if (Test-Path "archive/cleanup-2025-10-24-165115/PHASE_STATUS_2025-10-13.md") {
    try {
        $targetDir = Split-Path "PHASE_STATUS_2025-10-13.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/PHASE_STATUS_2025-10-13.md" -Destination "PHASE_STATUS_2025-10-13.md" -Force
        Write-Host "✓ Restored: PHASE_STATUS_2025-10-13.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring PHASE_STATUS_2025-10-13.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/PHASE_STATUS_2025-10-13.md" -ForegroundColor Yellow
}

# Restore: POWERSHELL_DEPLOYMENT_REPAIR_PLAN.md
if (Test-Path "archive/cleanup-2025-10-24-165115/POWERSHELL_DEPLOYMENT_REPAIR_PLAN.md") {
    try {
        $targetDir = Split-Path "POWERSHELL_DEPLOYMENT_REPAIR_PLAN.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/POWERSHELL_DEPLOYMENT_REPAIR_PLAN.md" -Destination "POWERSHELL_DEPLOYMENT_REPAIR_PLAN.md" -Force
        Write-Host "✓ Restored: POWERSHELL_DEPLOYMENT_REPAIR_PLAN.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring POWERSHELL_DEPLOYMENT_REPAIR_PLAN.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/POWERSHELL_DEPLOYMENT_REPAIR_PLAN.md" -ForegroundColor Yellow
}

# Restore: POWERSHELL_REPAIR_RESOLUTION_REPORT.md
if (Test-Path "archive/cleanup-2025-10-24-165115/POWERSHELL_REPAIR_RESOLUTION_REPORT.md") {
    try {
        $targetDir = Split-Path "POWERSHELL_REPAIR_RESOLUTION_REPORT.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/POWERSHELL_REPAIR_RESOLUTION_REPORT.md" -Destination "POWERSHELL_REPAIR_RESOLUTION_REPORT.md" -Force
        Write-Host "✓ Restored: POWERSHELL_REPAIR_RESOLUTION_REPORT.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring POWERSHELL_REPAIR_RESOLUTION_REPORT.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/POWERSHELL_REPAIR_RESOLUTION_REPORT.md" -ForegroundColor Yellow
}

# Restore: PRODUCTION_DEPLOYMENT_GUIDE.md
if (Test-Path "archive/cleanup-2025-10-24-165115/PRODUCTION_DEPLOYMENT_GUIDE.md") {
    try {
        $targetDir = Split-Path "PRODUCTION_DEPLOYMENT_GUIDE.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/PRODUCTION_DEPLOYMENT_GUIDE.md" -Destination "PRODUCTION_DEPLOYMENT_GUIDE.md" -Force
        Write-Host "✓ Restored: PRODUCTION_DEPLOYMENT_GUIDE.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring PRODUCTION_DEPLOYMENT_GUIDE.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/PRODUCTION_DEPLOYMENT_GUIDE.md" -ForegroundColor Yellow
}

# Restore: PR_FAILURE_ANALYSIS_REPORT_72H.md
if (Test-Path "archive/cleanup-2025-10-24-165115/PR_FAILURE_ANALYSIS_REPORT_72H.md") {
    try {
        $targetDir = Split-Path "PR_FAILURE_ANALYSIS_REPORT_72H.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/PR_FAILURE_ANALYSIS_REPORT_72H.md" -Destination "PR_FAILURE_ANALYSIS_REPORT_72H.md" -Force
        Write-Host "✓ Restored: PR_FAILURE_ANALYSIS_REPORT_72H.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring PR_FAILURE_ANALYSIS_REPORT_72H.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/PR_FAILURE_ANALYSIS_REPORT_72H.md" -ForegroundColor Yellow
}

# Restore: RENDER_DEPLOYMENT_CHECKLIST.md
if (Test-Path "archive/cleanup-2025-10-24-165115/RENDER_DEPLOYMENT_CHECKLIST.md") {
    try {
        $targetDir = Split-Path "RENDER_DEPLOYMENT_CHECKLIST.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/RENDER_DEPLOYMENT_CHECKLIST.md" -Destination "RENDER_DEPLOYMENT_CHECKLIST.md" -Force
        Write-Host "✓ Restored: RENDER_DEPLOYMENT_CHECKLIST.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring RENDER_DEPLOYMENT_CHECKLIST.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/RENDER_DEPLOYMENT_CHECKLIST.md" -ForegroundColor Yellow
}

# Restore: RENDER_DEPLOYMENT_DIAGNOSIS.md
if (Test-Path "archive/cleanup-2025-10-24-165115/RENDER_DEPLOYMENT_DIAGNOSIS.md") {
    try {
        $targetDir = Split-Path "RENDER_DEPLOYMENT_DIAGNOSIS.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/RENDER_DEPLOYMENT_DIAGNOSIS.md" -Destination "RENDER_DEPLOYMENT_DIAGNOSIS.md" -Force
        Write-Host "✓ Restored: RENDER_DEPLOYMENT_DIAGNOSIS.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring RENDER_DEPLOYMENT_DIAGNOSIS.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/RENDER_DEPLOYMENT_DIAGNOSIS.md" -ForegroundColor Yellow
}

# Restore: RENDER_DEPLOYMENT_GUIDE.md
if (Test-Path "archive/cleanup-2025-10-24-165115/RENDER_DEPLOYMENT_GUIDE.md") {
    try {
        $targetDir = Split-Path "RENDER_DEPLOYMENT_GUIDE.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/RENDER_DEPLOYMENT_GUIDE.md" -Destination "RENDER_DEPLOYMENT_GUIDE.md" -Force
        Write-Host "✓ Restored: RENDER_DEPLOYMENT_GUIDE.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring RENDER_DEPLOYMENT_GUIDE.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/RENDER_DEPLOYMENT_GUIDE.md" -ForegroundColor Yellow
}

# Restore: SCHEDULER_DEPLOYMENT_GUIDE.md
if (Test-Path "archive/cleanup-2025-10-24-165115/SCHEDULER_DEPLOYMENT_GUIDE.md") {
    try {
        $targetDir = Split-Path "SCHEDULER_DEPLOYMENT_GUIDE.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/SCHEDULER_DEPLOYMENT_GUIDE.md" -Destination "SCHEDULER_DEPLOYMENT_GUIDE.md" -Force
        Write-Host "✓ Restored: SCHEDULER_DEPLOYMENT_GUIDE.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring SCHEDULER_DEPLOYMENT_GUIDE.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/SCHEDULER_DEPLOYMENT_GUIDE.md" -ForegroundColor Yellow
}

# Restore: SESSION_SUMMARY_2025-10-24.md
if (Test-Path "archive/cleanup-2025-10-24-165115/SESSION_SUMMARY_2025-10-24.md") {
    try {
        $targetDir = Split-Path "SESSION_SUMMARY_2025-10-24.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/SESSION_SUMMARY_2025-10-24.md" -Destination "SESSION_SUMMARY_2025-10-24.md" -Force
        Write-Host "✓ Restored: SESSION_SUMMARY_2025-10-24.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring SESSION_SUMMARY_2025-10-24.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/SESSION_SUMMARY_2025-10-24.md" -ForegroundColor Yellow
}

# Restore: STATE_OF_AFFAIRS_REPORT.md
if (Test-Path "archive/cleanup-2025-10-24-165115/STATE_OF_AFFAIRS_REPORT.md") {
    try {
        $targetDir = Split-Path "STATE_OF_AFFAIRS_REPORT.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/STATE_OF_AFFAIRS_REPORT.md" -Destination "STATE_OF_AFFAIRS_REPORT.md" -Force
        Write-Host "✓ Restored: STATE_OF_AFFAIRS_REPORT.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring STATE_OF_AFFAIRS_REPORT.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/STATE_OF_AFFAIRS_REPORT.md" -ForegroundColor Yellow
}

# Restore: TRADIER_DEPLOYMENT_STATUS.md
if (Test-Path "archive/cleanup-2025-10-24-165115/TRADIER_DEPLOYMENT_STATUS.md") {
    try {
        $targetDir = Split-Path "TRADIER_DEPLOYMENT_STATUS.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/TRADIER_DEPLOYMENT_STATUS.md" -Destination "TRADIER_DEPLOYMENT_STATUS.md" -Force
        Write-Host "✓ Restored: TRADIER_DEPLOYMENT_STATUS.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring TRADIER_DEPLOYMENT_STATUS.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/TRADIER_DEPLOYMENT_STATUS.md" -ForegroundColor Yellow
}

# Restore: VERIFICATION_CHECKLIST.md
if (Test-Path "archive/cleanup-2025-10-24-165115/VERIFICATION_CHECKLIST.md") {
    try {
        $targetDir = Split-Path "VERIFICATION_CHECKLIST.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/VERIFICATION_CHECKLIST.md" -Destination "VERIFICATION_CHECKLIST.md" -Force
        Write-Host "✓ Restored: VERIFICATION_CHECKLIST.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring VERIFICATION_CHECKLIST.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/VERIFICATION_CHECKLIST.md" -ForegroundColor Yellow
}

# Restore: deployment-report-20251023-154113.md
if (Test-Path "archive/cleanup-2025-10-24-165115/deployment-report-20251023-154113.md") {
    try {
        $targetDir = Split-Path "deployment-report-20251023-154113.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/deployment-report-20251023-154113.md" -Destination "deployment-report-20251023-154113.md" -Force
        Write-Host "✓ Restored: deployment-report-20251023-154113.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring deployment-report-20251023-154113.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/deployment-report-20251023-154113.md" -ForegroundColor Yellow
}

# Restore: frontend/components/DEPRECATED_COMPONENTS.md
if (Test-Path "archive/cleanup-2025-10-24-165115/frontend/components/DEPRECATED_COMPONENTS.md") {
    try {
        $targetDir = Split-Path "frontend/components/DEPRECATED_COMPONENTS.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/frontend/components/DEPRECATED_COMPONENTS.md" -Destination "frontend/components/DEPRECATED_COMPONENTS.md" -Force
        Write-Host "✓ Restored: frontend/components/DEPRECATED_COMPONENTS.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring frontend/components/DEPRECATED_COMPONENTS.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/frontend/components/DEPRECATED_COMPONENTS.md" -ForegroundColor Yellow
}

# Restore: health-report-20251023-154129.md
if (Test-Path "archive/cleanup-2025-10-24-165115/health-report-20251023-154129.md") {
    try {
        $targetDir = Split-Path "health-report-20251023-154129.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/health-report-20251023-154129.md" -Destination "health-report-20251023-154129.md" -Force
        Write-Host "✓ Restored: health-report-20251023-154129.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring health-report-20251023-154129.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/health-report-20251023-154129.md" -ForegroundColor Yellow
}

# Restore: test-report-20251023-134322.md
if (Test-Path "archive/cleanup-2025-10-24-165115/test-report-20251023-134322.md") {
    try {
        $targetDir = Split-Path "test-report-20251023-134322.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/test-report-20251023-134322.md" -Destination "test-report-20251023-134322.md" -Force
        Write-Host "✓ Restored: test-report-20251023-134322.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring test-report-20251023-134322.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/test-report-20251023-134322.md" -ForegroundColor Yellow
}

# Restore: test-report-20251023-140252.md
if (Test-Path "archive/cleanup-2025-10-24-165115/test-report-20251023-140252.md") {
    try {
        $targetDir = Split-Path "test-report-20251023-140252.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/test-report-20251023-140252.md" -Destination "test-report-20251023-140252.md" -Force
        Write-Host "✓ Restored: test-report-20251023-140252.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring test-report-20251023-140252.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/test-report-20251023-140252.md" -ForegroundColor Yellow
}

# Restore: test-report-20251023-154119.md
if (Test-Path "archive/cleanup-2025-10-24-165115/test-report-20251023-154119.md") {
    try {
        $targetDir = Split-Path "test-report-20251023-154119.md" -Parent
        if ($targetDir -and !(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Move-Item -Path "archive/cleanup-2025-10-24-165115/test-report-20251023-154119.md" -Destination "test-report-20251023-154119.md" -Force
        Write-Host "✓ Restored: test-report-20251023-154119.md"
        $restoredCount++
    } catch {
        Write-Host "❌ Error restoring test-report-20251023-154119.md: $_" -ForegroundColor Red
        $errorCount++
    }
} else {
    Write-Host "⚠️  Not found in archive: archive/cleanup-2025-10-24-165115/test-report-20251023-154119.md" -ForegroundColor Yellow
}

Write-Host "=" * 70
Write-Host "Rollback Complete"
Write-Host "Files Restored: $restoredCount"
Write-Host "Errors: $errorCount"
Write-Host "=" * 70