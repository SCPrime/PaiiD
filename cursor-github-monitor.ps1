# Cursor GitHub Actions Monitor
# Run this in Cursor's integrated terminal to see real-time GitHub Actions status

param(
    [string]$Repository = "SCPrime/PaiiD",
    [int]$RefreshSeconds = 30
)

function Get-GitHubActionsStatus {
    param([string]$Repo)
    
    try {
        Write-Host "🔄 Fetching GitHub Actions status for $Repo..." -ForegroundColor Cyan
        
        # Get workflow runs
        $runsUrl = "https://api.github.com/repos/$Repo/actions/runs?per_page=10"
        $runsResponse = Invoke-RestMethod -Uri $runsUrl -Method Get
        
        # Get workflows
        $workflowsUrl = "https://api.github.com/repos/$Repo/actions/workflows"
        $workflowsResponse = Invoke-RestMethod -Uri $workflowsUrl -Method Get
        
        Clear-Host
        Write-Host "🚀 GitHub Actions Monitor - $Repo" -ForegroundColor Green
        Write-Host "=" * 50 -ForegroundColor Gray
        Write-Host ""
        
        # Status Summary
        $successCount = ($runsResponse.workflow_runs | Where-Object { $_.conclusion -eq "success" }).Count
        $failureCount = ($runsResponse.workflow_runs | Where-Object { $_.conclusion -eq "failure" }).Count
        $runningCount = ($runsResponse.workflow_runs | Where-Object { $_.status -eq "in_progress" }).Count
        $queuedCount = ($runsResponse.workflow_runs | Where-Object { $_.status -eq "queued" }).Count
        
        Write-Host "📊 Status Summary:" -ForegroundColor Yellow
        Write-Host "  ✅ Success: $successCount" -ForegroundColor Green
        Write-Host "  ❌ Failed: $failureCount" -ForegroundColor Red
        Write-Host "  🔄 Running: $runningCount" -ForegroundColor Blue
        Write-Host "  ⏳ Queued: $queuedCount" -ForegroundColor Yellow
        Write-Host ""
        
        # Recent Runs
        Write-Host "🔄 Recent Workflow Runs:" -ForegroundColor Yellow
        Write-Host "-" * 40 -ForegroundColor Gray
        
        foreach ($run in $runsResponse.workflow_runs | Select-Object -First 5) {
            $status = if ($run.status -eq "in_progress") { "🔄 Running" } 
                     elseif ($run.status -eq "queued") { "⏳ Queued" }
                     elseif ($run.conclusion -eq "success") { "✅ Success" }
                     elseif ($run.conclusion -eq "failure") { "❌ Failed" }
                     elseif ($run.conclusion -eq "cancelled") { "⏹️ Cancelled" }
                     else { "❓ Unknown" }
            
            $color = if ($run.status -eq "in_progress") { "Blue" }
                    elseif ($run.status -eq "queued") { "Yellow" }
                    elseif ($run.conclusion -eq "success") { "Green" }
                    elseif ($run.conclusion -eq "failure") { "Red" }
                    else { "Gray" }
            
            $date = [DateTime]::Parse($run.created_at).ToString("MM/dd HH:mm")
            Write-Host "  $status $($run.name) - $date" -ForegroundColor $color
            Write-Host "    Workflow: $($run.workflow_name)" -ForegroundColor Gray
            Write-Host "    URL: $($run.html_url)" -ForegroundColor Cyan
            Write-Host ""
        }
        
        # Available Workflows
        Write-Host "⚙️ Available Workflows:" -ForegroundColor Yellow
        Write-Host "-" * 40 -ForegroundColor Gray
        
        foreach ($workflow in $workflowsResponse.workflows) {
            $stateColor = if ($workflow.state -eq "active") { "Green" } else { "Red" }
            Write-Host "  📋 $($workflow.name)" -ForegroundColor White
            Write-Host "    State: $($workflow.state)" -ForegroundColor $stateColor
            Write-Host "    URL: $($workflow.html_url)" -ForegroundColor Cyan
            Write-Host ""
        }
        
        Write-Host "🔄 Auto-refresh in $RefreshSeconds seconds... (Press Ctrl+C to stop)" -ForegroundColor Magenta
        Write-Host "=" * 50 -ForegroundColor Gray
        
    } catch {
        Write-Host "❌ Error fetching GitHub Actions data: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "💡 Make sure you have internet connection and the repository is public" -ForegroundColor Yellow
    }
}

# Main monitoring loop
Write-Host "🚀 Starting GitHub Actions Monitor for $Repository" -ForegroundColor Green
Write-Host "🔄 Refresh interval: $RefreshSeconds seconds" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop monitoring" -ForegroundColor Yellow
Write-Host ""

while ($true) {
    Get-GitHubActionsStatus -Repo $Repository
    Start-Sleep -Seconds $RefreshSeconds
}
