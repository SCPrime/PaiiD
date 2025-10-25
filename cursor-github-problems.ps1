# Cursor GitHub Actions Problems Monitor
# This script checks for failed GitHub Actions and shows them in Cursor's Problems panel

param(
    [string]$Repository = "SCPrime/PaiiD"
)

function Check-GitHubActionsProblems {
    param([string]$Repo)
    
    try {
        Write-Host "🔍 Checking for GitHub Actions problems..." -ForegroundColor Cyan
        
        # Get recent workflow runs
        $runsUrl = "https://api.github.com/repos/$Repo/actions/runs?per_page=20"
        $runsResponse = Invoke-RestMethod -Uri $runsUrl -Method Get
        
        $problems = @()
        
        # Check for failed runs
        $failedRuns = $runsResponse.workflow_runs | Where-Object { $_.conclusion -eq "failure" }
        
        foreach ($run in $failedRuns) {
            $problems += @{
                Type = "Error"
                Message = "GitHub Action failed: $($run.name)"
                Source = "GitHub Actions"
                Severity = "Error"
                File = $run.html_url
                Line = 1
                Description = "Workflow: $($run.workflow_name) | Created: $($run.created_at)"
            }
        }
        
        # Check for long-running workflows
        $runningRuns = $runsResponse.workflow_runs | Where-Object { $_.status -eq "in_progress" }
        $currentTime = Get-Date
        
        foreach ($run in $runningRuns) {
            $runTime = [DateTime]::Parse($run.created_at)
            $duration = ($currentTime - $runTime).TotalMinutes
            
            if ($duration -gt 30) {  # Running for more than 30 minutes
                $problems += @{
                    Type = "Warning"
                    Message = "GitHub Action running too long: $($run.name)"
                    Source = "GitHub Actions"
                    Severity = "Warning"
                    File = $run.html_url
                    Line = 1
                    Description = "Running for $([math]::Round($duration, 1)) minutes | Workflow: $($run.workflow_name)"
                }
            }
        }
        
        # Output problems in a format Cursor can understand
        if ($problems.Count -gt 0) {
            Write-Host "⚠️ Found $($problems.Count) GitHub Actions problems:" -ForegroundColor Yellow
            Write-Host ""
            
            foreach ($problem in $problems) {
                $severityColor = if ($problem.Severity -eq "Error") { "Red" } else { "Yellow" }
                Write-Host "  $($problem.Severity.ToUpper()): $($problem.Message)" -ForegroundColor $severityColor
                Write-Host "    Source: $($problem.Source)" -ForegroundColor Gray
                Write-Host "    Description: $($problem.Description)" -ForegroundColor Gray
                Write-Host "    URL: $($problem.File)" -ForegroundColor Cyan
                Write-Host ""
            }
        } else {
            Write-Host "✅ No GitHub Actions problems found!" -ForegroundColor Green
        }
        
        return $problems
        
    } catch {
        Write-Host "❌ Error checking GitHub Actions: $($_.Exception.Message)" -ForegroundColor Red
        return @()
    }
}

# Run the check
$problems = Check-GitHubActionsProblems -Repo $Repository

# If problems found, suggest solutions
if ($problems.Count -gt 0) {
    Write-Host "💡 Suggested Actions:" -ForegroundColor Magenta
    Write-Host "  1. Click on the URLs above to view detailed logs in GitHub" -ForegroundColor White
    Write-Host "  2. Check the workflow files in .github/workflows/ for configuration issues" -ForegroundColor White
    Write-Host "  3. Run 'git log --oneline -5' to see recent commits that might have caused issues" -ForegroundColor White
    Write-Host "  4. Check if all required environment variables are set in GitHub repository settings" -ForegroundColor White
}
