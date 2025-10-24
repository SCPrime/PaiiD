# PaiiD GitHub Repository Monitor - Implementation Plan

**Created:** October 24, 2025
**Status:** Design Phase
**Priority:** High - Project Management & DevOps

---

## 🎯 EXECUTIVE SUMMARY

This plan details a comprehensive GitHub repository monitoring system that:
- **Polls repository every 5 minutes** for routine checks
- **Responds immediately to webhook events** (pushes, pulls, merges, errors)
- **Tracks running counters** for issues, events, and completion metrics
- **Monitors project health** including crashes, conflicts, and test failures
- **Provides real-time dashboard** with completion timeline
- **Sends alerts** for critical events

---

## 📊 MONITORING SCOPE

### Events to Track

#### Git Operations (High Priority)
- ✅ **Pushes** - Track commits, author, files changed
- ✅ **Pulls** - Monitor pull requests, reviews, approvals
- ✅ **Merges** - Track merge commits, conflicts, success/failure
- ✅ **Branches** - New branches, deletions, stale branches
- ✅ **Tags** - Release tags, version tags

#### Code Quality (High Priority)
- ✅ **Build Status** - Success/failure of CI/CD runs
- ✅ **Test Results** - Pass/fail counts, new failures
- ✅ **Linter Errors** - ESLint warnings (151), TypeScript errors
- ✅ **Deprecation Warnings** - Python warnings (328)
- ✅ **Code Coverage** - Current: ~8%, Target: 70%

#### Issues & Tasks (Critical)
- ✅ **Issue Count** - Current: 65 (12 P0, 27 P1, 26 P2)
- ✅ **Issue Creation** - New issues opened
- ✅ **Issue Resolution** - Closed issues, time to close
- ✅ **TODO Items** - Track TODO.md progress
- ✅ **Sprint Progress** - Current sprint completion

#### System Health (Critical)
- ✅ **Application Crashes** - Backend/Frontend crashes
- ✅ **API Errors** - 500 errors, timeouts, rate limits
- ✅ **Deployment Status** - Vercel & Render deployment state
- ✅ **Health Check Failures** - /api/health endpoint
- ✅ **Dependency Vulnerabilities** - npm audit, pip safety

#### Conflicts & Blockers (Medium Priority)
- ✅ **Merge Conflicts** - Automatic conflict detection
- ✅ **PR Blockers** - Failed checks, pending reviews
- ✅ **Deployment Blockers** - Build failures, env issues
- ✅ **Breaking Changes** - API contract violations

---

## 🏗️ ARCHITECTURE

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                   GitHub Repository                      │
│                                                          │
│  Events: Push, PR, Merge, Issues, Releases, Checks     │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ Webhooks (instant)
                 │ + API Polling (5 min)
                 │
┌────────────────▼────────────────────────────────────────┐
│              PaiiD Monitor Service                       │
│                                                          │
│  Components:                                            │
│  ├─ Event Listener (Webhooks)                          │
│  ├─ Poller (5-min interval)                            │
│  ├─ Analytics Engine                                   │
│  ├─ Counter Manager                                    │
│  └─ Alert Manager                                      │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ Store & Process
                 │
┌────────────────▼────────────────────────────────────────┐
│              Data Storage Layer                          │
│                                                          │
│  ├─ PostgreSQL (event history, counters)               │
│  ├─ Redis (real-time counters, cache)                  │
│  └─ Time-Series DB (metrics, trends) [optional]        │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ Query & Display
                 │
┌────────────────▼────────────────────────────────────────┐
│              Output Channels                             │
│                                                          │
│  ├─ Dashboard UI (web interface)                       │
│  ├─ Slack/Discord Alerts                               │
│  ├─ Email Reports (daily summary)                      │
│  ├─ CLI Tool (quick status check)                      │
│  └─ Status Badge (README.md)                           │
└─────────────────────────────────────────────────────────┘
```

---

## 📈 COUNTERS & METRICS

### Running Counters

#### 1. Event Counters (Reset Weekly)
```json
{
  "weekly_counters": {
    "commits": 0,
    "pushes": 0,
    "pulls_opened": 0,
    "pulls_merged": 0,
    "pulls_closed": 0,
    "issues_opened": 0,
    "issues_closed": 0,
    "deployments": 0,
    "build_failures": 0,
    "test_failures": 0,
    "conflicts": 0,
    "hotfixes": 0
  }
}
```

#### 2. Issue Health Counters (Live)
```json
{
  "issue_health": {
    "total_issues": 65,
    "critical_p0": 12,
    "high_p1": 27,
    "medium_p2": 26,
    "assigned": 45,
    "unassigned": 20,
    "blocked": 3,
    "avg_resolution_time_hours": 18.5
  }
}
```

#### 3. Project Completion Tracker (Live)
```json
{
  "completion_tracking": {
    "overall_progress": 0.42,
    "phases": {
      "phase_0_prep": {
        "progress": 0.98,
        "tasks_completed": 7,
        "tasks_total": 9,
        "blocked_tasks": 2,
        "blocker_reason": "Requires physical mobile devices"
      },
      "phase_1_options": {
        "progress": 0.00,
        "tasks_completed": 0,
        "tasks_total": 5,
        "estimated_hours_remaining": 8
      },
      "phase_2_ml": {
        "progress": 0.00,
        "tasks_completed": 0,
        "tasks_total": 4,
        "estimated_hours_remaining": 6
      },
      "phase_3_ui": {
        "progress": 0.00,
        "tasks_completed": 0,
        "tasks_total": 4,
        "estimated_hours_remaining": 8
      },
      "phase_4_cleanup": {
        "progress": 0.00,
        "tasks_completed": 0,
        "tasks_total": 3,
        "estimated_hours_remaining": 10
      }
    },
    "timeline": {
      "total_hours_budgeted": 80,
      "hours_completed": 33.6,
      "hours_remaining": 46.4,
      "estimated_completion_date": "2025-11-03",
      "days_behind_schedule": 0
    }
  }
}
```

#### 4. Code Quality Metrics (Daily)
```json
{
  "code_quality": {
    "typescript_errors": 0,
    "eslint_warnings": 151,
    "python_warnings": 328,
    "test_coverage_percent": 8,
    "lines_of_code": 45230,
    "tech_debt_hours": 83,
    "security_vulnerabilities": 2
  }
}
```

#### 5. System Health Indicators (Real-time)
```json
{
  "system_health": {
    "frontend_status": "healthy",
    "backend_status": "healthy",
    "database_status": "healthy",
    "redis_status": "healthy",
    "last_crash": null,
    "uptime_percent_7d": 99.8,
    "api_error_rate_5m": 0.002,
    "avg_response_time_ms": 245
  }
}
```

---

## 🔧 IMPLEMENTATION DETAILS

### Phase 1: Core Infrastructure (Week 1)

#### 1.1 GitHub Webhook Handler
**File:** `backend/app/services/github_monitor.py`

```python
from fastapi import APIRouter, Request, HTTPException
from typing import Dict, Any
import hmac
import hashlib
from datetime import datetime

router = APIRouter(prefix="/github", tags=["github"])

class GitHubWebhookHandler:
    """Handles GitHub webhook events"""
    
    def __init__(self, webhook_secret: str):
        self.secret = webhook_secret.encode()
        
    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify GitHub webhook signature"""
        expected = hmac.new(self.secret, payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(f"sha256={expected}", signature)
    
    async def handle_push(self, event: Dict[str, Any]):
        """Handle push events"""
        commits = event.get("commits", [])
        branch = event.get("ref", "").split("/")[-1]
        
        await self.increment_counter("pushes")
        await self.increment_counter("commits", len(commits))
        
        # Check for sensitive files
        for commit in commits:
            if any(".env" in f or ".key" in f for f in commit.get("added", [])):
                await self.send_alert("CRITICAL", "Sensitive file committed!")
        
        # Log event
        await self.log_event({
            "type": "push",
            "branch": branch,
            "commit_count": len(commits),
            "author": event.get("pusher", {}).get("name"),
            "timestamp": datetime.utcnow()
        })
    
    async def handle_pull_request(self, event: Dict[str, Any]):
        """Handle PR events"""
        action = event.get("action")
        pr = event.get("pull_request", {})
        
        await self.increment_counter(f"pulls_{action}")
        
        # Check for conflicts
        if pr.get("mergeable") is False:
            await self.send_alert("HIGH", f"PR #{pr['number']} has merge conflicts")
        
        await self.log_event({
            "type": "pull_request",
            "action": action,
            "pr_number": pr.get("number"),
            "title": pr.get("title"),
            "timestamp": datetime.utcnow()
        })
    
    async def handle_check_suite(self, event: Dict[str, Any]):
        """Handle CI/CD check results"""
        check = event.get("check_suite", {})
        conclusion = check.get("conclusion")
        
        if conclusion == "failure":
            await self.increment_counter("build_failures")
            await self.send_alert("MEDIUM", f"Build failed: {check.get('head_branch')}")
        
        await self.log_event({
            "type": "check_suite",
            "conclusion": conclusion,
            "branch": check.get("head_branch"),
            "timestamp": datetime.utcnow()
        })
    
    async def handle_issues(self, event: Dict[str, Any]):
        """Handle issue events"""
        action = event.get("action")
        issue = event.get("issue", {})
        
        await self.increment_counter(f"issues_{action}")
        
        # Update issue tracker
        await self.update_issue_health()
        
        # Alert on critical issues
        labels = [l.get("name") for l in issue.get("labels", [])]
        if "P0" in labels or "critical" in labels:
            await self.send_alert("CRITICAL", f"P0 Issue opened: {issue['title']}")

@router.post("/webhook")
async def github_webhook(request: Request):
    """Receive GitHub webhook events"""
    signature = request.headers.get("X-Hub-Signature-256")
    event_type = request.headers.get("X-GitHub-Event")
    
    payload = await request.body()
    
    handler = GitHubWebhookHandler(settings.GITHUB_WEBHOOK_SECRET)
    
    if not handler.verify_signature(payload, signature):
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    event_data = await request.json()
    
    # Route to appropriate handler
    if event_type == "push":
        await handler.handle_push(event_data)
    elif event_type == "pull_request":
        await handler.handle_pull_request(event_data)
    elif event_type == "check_suite":
        await handler.handle_check_suite(event_data)
    elif event_type == "issues":
        await handler.handle_issues(event_data)
    
    return {"status": "processed"}
```

#### 1.2 Polling Service (5-minute interval)
**File:** `backend/app/services/github_poller.py`

```python
import asyncio
from datetime import datetime, timedelta
import httpx
from typing import Dict, List

class GitHubPoller:
    """Polls GitHub API every 5 minutes for repository state"""
    
    def __init__(self, token: str, repo: str):
        self.token = token
        self.repo = repo  # Format: "owner/repo"
        self.base_url = f"https://api.github.com/repos/{repo}"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    async def poll_forever(self):
        """Run polling loop every 5 minutes"""
        while True:
            try:
                await self.run_checks()
            except Exception as e:
                logger.error(f"Polling error: {e}")
            
            await asyncio.sleep(300)  # 5 minutes
    
    async def run_checks(self):
        """Execute all polling checks"""
        async with httpx.AsyncClient() as client:
            # Run checks in parallel
            await asyncio.gather(
                self.check_open_prs(client),
                self.check_recent_commits(client),
                self.check_ci_status(client),
                self.check_issues(client),
                self.check_deployments(client),
                self.update_completion_metrics(client)
            )
    
    async def check_open_prs(self, client: httpx.AsyncClient):
        """Check for stale or problematic PRs"""
        url = f"{self.base_url}/pulls?state=open"
        response = await client.get(url, headers=self.headers)
        prs = response.json()
        
        for pr in prs:
            created_at = datetime.fromisoformat(pr["created_at"].rstrip("Z"))
            age_days = (datetime.utcnow() - created_at).days
            
            # Alert on stale PRs
            if age_days > 7:
                await self.send_alert("LOW", f"PR #{pr['number']} is {age_days} days old")
            
            # Check for conflicts
            if not pr.get("mergeable", True):
                await self.send_alert("MEDIUM", f"PR #{pr['number']} has conflicts")
    
    async def check_ci_status(self, client: httpx.AsyncClient):
        """Check latest CI/CD run status"""
        url = f"{self.base_url}/actions/runs?per_page=1"
        response = await client.get(url, headers=self.headers)
        runs = response.json().get("workflow_runs", [])
        
        if runs and runs[0]["conclusion"] == "failure":
            await self.send_alert("HIGH", f"Latest CI run failed: {runs[0]['name']}")
    
    async def check_deployments(self, client: httpx.AsyncClient):
        """Check deployment status"""
        # Check Vercel
        vercel_health = await self.check_url("https://paiid-snowy.vercel.app/api/proxy/api/health")
        if not vercel_health:
            await self.send_alert("CRITICAL", "Frontend deployment is down!")
        
        # Check Render
        render_health = await self.check_url("https://paiid-86a1.onrender.com/api/health")
        if not render_health:
            await self.send_alert("CRITICAL", "Backend deployment is down!")
    
    async def update_completion_metrics(self, client: httpx.AsyncClient):
        """Update project completion tracking"""
        # Parse TODO.md from repo
        url = f"{self.base_url}/contents/TODO.md"
        response = await client.get(url, headers=self.headers)
        
        if response.status_code == 200:
            content = base64.b64decode(response.json()["content"]).decode()
            
            # Parse markdown checkboxes
            total_tasks = content.count("- [ ]") + content.count("- [x]")
            completed_tasks = content.count("- [x]")
            progress = completed_tasks / total_tasks if total_tasks > 0 else 0
            
            await self.update_counter("project_completion", progress)
```

#### 1.3 Counter Manager
**File:** `backend/app/services/counter_manager.py`

```python
from typing import Optional
from datetime import datetime, timedelta
import json

class CounterManager:
    """Manages all monitoring counters with Redis backend"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.prefix = "monitor:counter:"
    
    async def increment(self, counter_name: str, amount: int = 1):
        """Increment a counter"""
        key = f"{self.prefix}{counter_name}"
        await self.redis.incrby(key, amount)
        
        # Also track in time-series for trending
        timestamp = datetime.utcnow().isoformat()
        await self.redis.zadd(
            f"{self.prefix}timeseries:{counter_name}",
            {timestamp: amount}
        )
    
    async def get(self, counter_name: str) -> int:
        """Get current counter value"""
        key = f"{self.prefix}{counter_name}"
        value = await self.redis.get(key)
        return int(value) if value else 0
    
    async def get_all(self) -> Dict[str, int]:
        """Get all counters"""
        keys = await self.redis.keys(f"{self.prefix}*")
        counters = {}
        
        for key in keys:
            if "timeseries" not in key:
                name = key.replace(self.prefix, "")
                counters[name] = await self.get(name)
        
        return counters
    
    async def reset_weekly_counters(self):
        """Reset weekly counters (called by cron)"""
        weekly_counters = [
            "commits", "pushes", "pulls_opened", "pulls_merged",
            "issues_opened", "issues_closed", "deployments",
            "build_failures", "conflicts"
        ]
        
        for counter in weekly_counters:
            await self.redis.delete(f"{self.prefix}{counter}")
    
    async def get_trend(self, counter_name: str, hours: int = 24) -> List[Dict]:
        """Get counter trend over time"""
        key = f"{self.prefix}timeseries:{counter_name}"
        since = (datetime.utcnow() - timedelta(hours=hours)).timestamp()
        
        data = await self.redis.zrangebyscore(
            key, since, "+inf", withscores=True
        )
        
        return [
            {"timestamp": score, "value": int(value)}
            for value, score in data
        ]
```

---

### Phase 2: Dashboard UI (Week 2)

#### 2.1 Monitor Dashboard Component
**File:** `frontend/components/MonitorDashboard.tsx`

```typescript
import React, { useEffect, useState } from 'react';
import { Card } from './Card';

interface MonitorData {
  eventCounters: {
    commits: number;
    pushes: number;
    issues_opened: number;
    issues_closed: number;
    deployments: number;
  };
  issueHealth: {
    total_issues: number;
    critical_p0: number;
    high_p1: number;
    medium_p2: number;
  };
  completionTracking: {
    overall_progress: number;
    phases: {
      [key: string]: {
        progress: number;
        tasks_completed: number;
        tasks_total: number;
      };
    };
    timeline: {
      hours_completed: number;
      hours_remaining: number;
      estimated_completion_date: string;
    };
  };
  systemHealth: {
    frontend_status: string;
    backend_status: string;
    last_crash: string | null;
    uptime_percent_7d: number;
  };
}

export const MonitorDashboard: React.FC = () => {
  const [data, setData] = useState<MonitorData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('/api/proxy/api/monitor/dashboard');
        const json = await response.json();
        setData(json);
      } catch (error) {
        console.error('Failed to fetch monitor data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30s

    return () => clearInterval(interval);
  }, []);

  if (loading) return <div>Loading monitor data...</div>;
  if (!data) return <div>Failed to load monitor data</div>;

  return (
    <div className="monitor-dashboard">
      <h1>🔍 PaiiD Repository Monitor</h1>

      {/* Event Counters */}
      <Card title="📊 This Week's Activity">
        <div className="metrics-grid">
          <Metric label="Commits" value={data.eventCounters.commits} />
          <Metric label="Pushes" value={data.eventCounters.pushes} />
          <Metric label="Deployments" value={data.eventCounters.deployments} />
          <Metric label="Issues Opened" value={data.eventCounters.issues_opened} />
          <Metric label="Issues Closed" value={data.eventCounters.issues_closed} />
        </div>
      </Card>

      {/* Issue Health */}
      <Card title="🐛 Issue Health">
        <div className="issue-health">
          <div className="total">Total: {data.issueHealth.total_issues}</div>
          <div className="critical">P0 Critical: {data.issueHealth.critical_p0}</div>
          <div className="high">P1 High: {data.issueHealth.high_p1}</div>
          <div className="medium">P2 Medium: {data.issueHealth.medium_p2}</div>
        </div>
      </Card>

      {/* Completion Timeline */}
      <Card title="🎯 Project Completion">
        <div className="completion-tracker">
          <ProgressBar 
            progress={data.completionTracking.overall_progress * 100}
            label={`Overall: ${Math.round(data.completionTracking.overall_progress * 100)}%`}
          />
          
          {Object.entries(data.completionTracking.phases).map(([phase, info]) => (
            <ProgressBar
              key={phase}
              progress={info.progress * 100}
              label={`${phase}: ${info.tasks_completed}/${info.tasks_total}`}
            />
          ))}

          <div className="timeline">
            <p>Hours Completed: {data.completionTracking.timeline.hours_completed}</p>
            <p>Hours Remaining: {data.completionTracking.timeline.hours_remaining}</p>
            <p>Est. Completion: {data.completionTracking.timeline.estimated_completion_date}</p>
          </div>
        </div>
      </Card>

      {/* System Health */}
      <Card title="💚 System Health">
        <div className="health-indicators">
          <StatusIndicator 
            label="Frontend" 
            status={data.systemHealth.frontend_status} 
          />
          <StatusIndicator 
            label="Backend" 
            status={data.systemHealth.backend_status} 
          />
          <div>Uptime (7d): {data.systemHealth.uptime_percent_7d}%</div>
          {data.systemHealth.last_crash && (
            <div className="alert">Last Crash: {data.systemHealth.last_crash}</div>
          )}
        </div>
      </Card>
    </div>
  );
};

const Metric: React.FC<{ label: string; value: number }> = ({ label, value }) => (
  <div className="metric">
    <div className="label">{label}</div>
    <div className="value">{value}</div>
  </div>
);

const ProgressBar: React.FC<{ progress: number; label: string }> = ({ progress, label }) => (
  <div className="progress-bar">
    <div className="label">{label}</div>
    <div className="bar">
      <div className="fill" style={{ width: `${progress}%` }}></div>
    </div>
  </div>
);

const StatusIndicator: React.FC<{ label: string; status: string }> = ({ label, status }) => (
  <div className={`status-indicator ${status}`}>
    <span className="dot"></span>
    {label}: {status}
  </div>
);

// Progress Line Graph Component
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface ProgressPoint {
  date: string;
  completion: number;
  target: number;
}

const ProgressLineGraph: React.FC<{ data: ProgressPoint[] }> = ({ data }) => {
  return (
    <Card title="📈 Completion Progress Over Time">
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis domain={[0, 100]} label={{ value: 'Completion %', angle: -90, position: 'insideLeft' }} />
          <Tooltip />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="completion" 
            stroke="#8884d8" 
            strokeWidth={2}
            name="Actual Progress"
            dot={{ r: 4 }}
          />
          <Line 
            type="monotone" 
            dataKey="target" 
            stroke="#82ca9d" 
            strokeWidth={2}
            strokeDasharray="5 5"
            name="Target Progress"
            dot={{ r: 4 }}
          />
        </LineChart>
      </ResponsiveContainer>
      
      <div className="progress-stats">
        <div className="stat">
          <strong>Current:</strong> {data[data.length - 1]?.completion || 0}%
        </div>
        <div className="stat">
          <strong>Target:</strong> {data[data.length - 1]?.target || 0}%
        </div>
        <div className="stat">
          <strong>Trend:</strong> {
            data.length > 1 
              ? (data[data.length - 1].completion - data[data.length - 2].completion > 0 ? '📈 Up' : '📉 Down')
              : 'N/A'
          }
        </div>
      </div>
    </Card>
  );
};
```

---

### Phase 3: Alert System (Week 2)

#### 3.1 Alert Manager
**File:** `backend/app/services/alert_manager.py`

```python
from enum import Enum
from typing import Optional
import asyncio

class AlertSeverity(Enum):
    CRITICAL = "critical"  # Immediate action required
    HIGH = "high"          # Attention needed soon
    MEDIUM = "medium"      # Notable event
    LOW = "low"            # Informational

class AlertManager:
    """Manages alerts across multiple channels"""
    
    def __init__(self, config: dict):
        self.slack_webhook = config.get("slack_webhook")
        self.discord_webhook = config.get("discord_webhook")
        self.email_config = config.get("email")
        self.alert_threshold = config.get("threshold", AlertSeverity.MEDIUM)
    
    async def send_alert(
        self, 
        severity: AlertSeverity, 
        title: str, 
        message: str,
        context: Optional[dict] = None
    ):
        """Send alert to configured channels"""
        
        # Filter by threshold
        if severity.value < self.alert_threshold.value:
            return
        
        alert = {
            "severity": severity.value,
            "title": title,
            "message": message,
            "context": context or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Store alert in database
        await self.store_alert(alert)
        
        # Send to channels based on severity
        tasks = []
        
        if severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]:
            if self.slack_webhook:
                tasks.append(self.send_slack(alert))
            if self.email_config:
                tasks.append(self.send_email(alert))
        
        if severity == AlertSeverity.CRITICAL and self.discord_webhook:
            tasks.append(self.send_discord(alert))
        
        if tasks:
            await asyncio.gather(*tasks)
    
    async def send_slack(self, alert: dict):
        """Send alert to Slack"""
        emoji = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢"
        }
        
        payload = {
            "text": f"{emoji[alert['severity']]} {alert['title']}",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{alert['title']}*\n{alert['message']}"
                    }
                }
            ]
        }
        
        async with httpx.AsyncClient() as client:
            await client.post(self.slack_webhook, json=payload)
    
    async def send_email(self, alert: dict):
        """Send alert via email"""
        # Implement email sending logic
        pass
    
    async def send_discord(self, alert: dict):
        """Send alert to Discord"""
        # Implement Discord webhook logic
        pass
```

---

### Phase 4: CLI Tool (Week 3)

#### 4.1 Quick Status CLI
**File:** `scripts/monitor-status.py`

```python
#!/usr/bin/env python3
"""
Quick CLI tool to check repository status

Usage:
    python scripts/monitor-status.py           # Full status
    python scripts/monitor-status.py --health  # Health only
    python scripts/monitor-status.py --issues  # Issues only
"""

import asyncio
import httpx
import json
from rich.console import Console
from rich.table import Table
from rich.progress import Progress

console = Console()

async def fetch_monitor_data():
    """Fetch monitor data from API"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://paiid-86a1.onrender.com/api/monitor/dashboard"
        )
        return response.json()

def display_event_counters(data: dict):
    """Display event counters table"""
    table = Table(title="📊 This Week's Activity")
    table.add_column("Event", style="cyan")
    table.add_column("Count", style="magenta", justify="right")
    
    for event, count in data["eventCounters"].items():
        table.add_row(event.replace("_", " ").title(), str(count))
    
    console.print(table)

def display_issue_health(data: dict):
    """Display issue health"""
    issues = data["issueHealth"]
    
    table = Table(title="🐛 Issue Health")
    table.add_column("Priority", style="cyan")
    table.add_column("Count", style="magenta", justify="right")
    
    table.add_row("Total", str(issues["total_issues"]))
    table.add_row("P0 (Critical)", f"[red]{issues['critical_p0']}[/red]")
    table.add_row("P1 (High)", f"[yellow]{issues['high_p1']}[/yellow]")
    table.add_row("P2 (Medium)", f"[green]{issues['medium_p2']}[/green]")
    
    console.print(table)

def display_completion(data: dict):
    """Display completion progress"""
    completion = data["completionTracking"]
    
    console.print("\n🎯 Project Completion\n", style="bold")
    
    # Overall progress
    with Progress() as progress:
        task = progress.add_task(
            "Overall Progress", 
            total=100
        )
        progress.update(task, completed=completion["overall_progress"] * 100)
    
    # Phase breakdown
    table = Table(title="Phase Breakdown")
    table.add_column("Phase", style="cyan")
    table.add_column("Progress", style="magenta", justify="right")
    table.add_column("Tasks", style="green", justify="right")
    
    for phase, info in completion["phases"].items():
        progress_pct = f"{info['progress'] * 100:.1f}%"
        tasks_ratio = f"{info['tasks_completed']}/{info['tasks_total']}"
        table.add_row(phase, progress_pct, tasks_ratio)
    
    console.print(table)
    
    # Timeline
    timeline = completion["timeline"]
    console.print(f"\n⏱️  Timeline:")
    console.print(f"  Hours Completed: {timeline['hours_completed']}")
    console.print(f"  Hours Remaining: {timeline['hours_remaining']}")
    console.print(f"  Est. Completion: {timeline['estimated_completion_date']}")

def display_system_health(data: dict):
    """Display system health"""
    health = data["systemHealth"]
    
    console.print("\n💚 System Health\n", style="bold")
    
    statuses = {
        "healthy": "✅",
        "degraded": "⚠️",
        "down": "❌"
    }
    
    console.print(f"Frontend: {statuses.get(health['frontend_status'], '❓')} {health['frontend_status']}")
    console.print(f"Backend: {statuses.get(health['backend_status'], '❓')} {health['backend_status']}")
    console.print(f"Uptime (7d): {health['uptime_percent_7d']}%")
    
    if health["last_crash"]:
        console.print(f"[red]Last Crash: {health['last_crash']}[/red]")

async def main():
    """Main CLI entry point"""
    try:
        with console.status("[bold green]Fetching monitor data..."):
            data = await fetch_monitor_data()
        
        display_event_counters(data)
        console.print()
        display_issue_health(data)
        console.print()
        display_completion(data)
        console.print()
        display_system_health(data)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 📅 IMPLEMENTATION TIMELINE

### Week 1: Core Infrastructure (32 hours)
- ✅ Day 1-2: GitHub webhook handler
- ✅ Day 2-3: Polling service
- ✅ Day 3-4: Counter manager & storage
- ✅ Day 4-5: Alert system

### Week 2: User Interfaces (24 hours)
- ✅ Day 1-2: Dashboard UI component
- ✅ Day 2-3: API endpoints
- ✅ Day 3: CLI tool
- ✅ Day 4: Status badges

### Week 3: Integration & Testing (16 hours)
- ✅ Day 1: GitHub webhook setup
- ✅ Day 2: Alert channel configuration
- ✅ Day 3: End-to-end testing
- ✅ Day 4: Documentation

**Total:** 72 hours (~2 weeks with 2 developers)

---

## 🚀 DEPLOYMENT CHECKLIST

### Prerequisites
- [ ] GitHub Personal Access Token (repo scope)
- [ ] GitHub Webhook Secret generated
- [ ] Slack/Discord webhook URLs (optional)
- [ ] Email SMTP credentials (optional)
- [ ] Redis instance available

### Backend Setup
- [ ] Add to `backend/app/routers/`:
  - `monitor.py` - Dashboard API endpoints
  - `github_webhooks.py` - Webhook handler
- [ ] Add to `backend/app/services/`:
  - `github_monitor.py`
  - `github_poller.py`
  - `counter_manager.py`
  - `alert_manager.py`
- [ ] Add environment variables to Render:
  ```
  GITHUB_TOKEN=<token>
  GITHUB_WEBHOOK_SECRET=<secret>
  GITHUB_REPO=SCPrime/PaiiD
  SLACK_WEBHOOK_URL=<url>
  MONITOR_ALERT_THRESHOLD=medium
  ```
- [ ] Run database migrations for monitor tables

### Frontend Setup
- [ ] Add `MonitorDashboard.tsx` component
- [ ] Add to RadialMenu navigation
- [ ] Test dashboard rendering

### GitHub Setup
- [ ] Go to Repository → Settings → Webhooks
- [ ] Add webhook:
  - URL: `https://paiid-86a1.onrender.com/api/github/webhook`
  - Secret: Use GITHUB_WEBHOOK_SECRET
  - Events: Select all relevant events
  - Active: ✅

### Testing
- [ ] Trigger test push (webhook should fire)
- [ ] Check `/api/monitor/dashboard` endpoint
- [ ] Verify counters incrementing
- [ ] Test alert delivery
- [ ] Run CLI tool: `python scripts/monitor-status.py`

---

## 📊 DASHBOARD WIREFRAME

```
┌─────────────────────────────────────────────────────────────┐
│  🔍 PaiiD Repository Monitor               Last Update: 2min│
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  📊 THIS WEEK'S ACTIVITY                                    │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐  │
│  │ Commits  │ Pushes   │ Deploys  │ Issues   │ Issues   │  │
│  │    47    │    23    │    12    │  Opened  │  Closed  │  │
│  │          │          │          │    8     │    15    │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘  │
│                                                              │
│  🐛 ISSUE HEALTH                      🎯 COMPLETION: 42%   │
│  ┌──────────────────────┐  ┌──────────────────────────────┐│
│  │ Total: 65            │  │ ████████░░░░░░░░░░░░░░  42%  ││
│  │ ├─ P0: 12 🔴        │  │                              ││
│  │ ├─ P1: 27 🟠        │  │ Phase 0: ████████████░  98% ││
│  │ └─ P2: 26 🟡        │  │ Phase 1: ░░░░░░░░░░░░   0% ││
│  │                      │  │ Phase 2: ░░░░░░░░░░░░   0% ││
│  │ Avg Resolution: 18.5h│  │ Phase 3: ░░░░░░░░░░░░   0% ││
│  └──────────────────────┘  │ Phase 4: ░░░░░░░░░░░░   0% ││
│                             └──────────────────────────────┘│
│  ⏱️  TIMELINE                                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Hours Completed: 33.6 / 80                          │  │
│  │ Estimated Completion: Nov 3, 2025                   │  │
│  │ Status: On Track ✅                                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  💚 SYSTEM HEALTH                                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Frontend: ✅ Healthy    Backend: ✅ Healthy         │  │
│  │ Database: ✅ Connected  Redis: ✅ Connected         │  │
│  │ Uptime (7d): 99.8%      Last Crash: None            │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  🔔 RECENT ALERTS                                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 🟠 10/24 14:23 - PR #42 has merge conflicts         │  │
│  │ 🟢 10/24 14:15 - Deployment succeeded (v1.2.3)      │  │
│  │ 🟡 10/24 14:00 - Build time increased by 15%        │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  [View Full History] [Configure Alerts] [Export Report]    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 CONFIGURATION FILE

**File:** `config/monitor.yml`

```yaml
github:
  repo: "SCPrime/PaiiD"
  token_env: "GITHUB_TOKEN"
  webhook_secret_env: "GITHUB_WEBHOOK_SECRET"
  
  polling:
    interval_seconds: 300  # 5 minutes
    enabled: true
  
  webhooks:
    enabled: true
    events:
      - push
      - pull_request
      - issues
      - check_suite
      - deployment_status
      - release

alerts:
  threshold: "medium"  # minimum severity to send
  
  channels:
    slack:
      enabled: true
      webhook_url_env: "SLACK_WEBHOOK_URL"
      severities: ["critical", "high", "medium"]
    
    discord:
      enabled: false
      webhook_url_env: "DISCORD_WEBHOOK_URL"
      severities: ["critical"]
    
    email:
      enabled: false
      smtp_host: "smtp.gmail.com"
      smtp_port: 587
      from_address_env: "ALERT_EMAIL_FROM"
      to_addresses_env: "ALERT_EMAIL_TO"
      severities: ["critical", "high"]

counters:
  weekly_reset: true
  reset_day: "monday"
  reset_time: "00:00"
  
  tracked_events:
    - commits
    - pushes
    - pulls_opened
    - pulls_merged
    - pulls_closed
    - issues_opened
    - issues_closed
    - deployments
    - build_failures
    - test_failures
    - conflicts
    - hotfixes

completion_tracking:
  source: "TODO.md"
  phases:
    - name: "Phase 0: Prep"
      pattern: "### Phase 0 Preparation"
    - name: "Phase 1: Options"
      pattern: "### Phase 1: Options Trading"
    - name: "Phase 2: ML"
      pattern: "### Phase 2: ML Strategy Engine"
    - name: "Phase 3: UI"
      pattern: "### Phase 3: UI/UX Polish"
    - name: "Phase 4: Cleanup"
      pattern: "### Phase 4: Code Quality Cleanup"

health_checks:
  interval_seconds: 60
  
  endpoints:
    - name: "Frontend"
      url: "https://paiid-snowy.vercel.app"
      expected_status: 200
    
    - name: "Backend"
      url: "https://paiid-86a1.onrender.com/api/health"
      expected_status: 200
      expected_json: { "status": "ok" }
```

---

## 📈 SUCCESS METRICS

After implementation, monitor these KPIs:

### Operational Metrics
- ✅ **Detection Time** - Time from event to alert < 30 seconds
- ✅ **False Positive Rate** - < 5% of alerts are false positives
- ✅ **Dashboard Load Time** - < 2 seconds
- ✅ **Data Freshness** - Counters updated within 5 minutes

### Business Metrics
- ✅ **Issue Resolution Time** - Reduced by 30%
- ✅ **Deployment Frequency** - Increased visibility
- ✅ **Incident Detection** - 100% of crashes detected
- ✅ **Team Awareness** - All members check dashboard daily

---

## 🎯 NEXT STEPS

1. **Review & Approve Plan** - Dr. SC Prime approval required
2. **Provision Resources** - Set up Redis, GitHub tokens
3. **Start Implementation** - Begin Week 1 tasks
4. **Test in Staging** - Verify all components work
5. **Deploy to Production** - Go live with monitoring
6. **Train Team** - Show dashboard to all team members
7. **Iterate & Improve** - Add features based on feedback

---

## 📞 SUPPORT & MAINTENANCE

**Monitoring the Monitor:**
- Dashboard uptime SLA: 99.5%
- Alert delivery SLA: 99.9%
- Data retention: 90 days
- Backup frequency: Daily

**Maintenance Schedule:**
- Weekly: Review alert accuracy
- Monthly: Analyze trends, optimize thresholds
- Quarterly: Update completion tracking logic
- Yearly: Full system audit

---

**Last Updated:** October 24, 2025
**Maintained By:** Dr. Cursor Claude
**Status:** ✅ READY FOR IMPLEMENTATION
**Approval Needed:** Dr. SC Prime - EXECUTE NOW?

