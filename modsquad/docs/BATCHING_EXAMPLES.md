# MOD SQUAD Batching Examples

**Version:** 1.0.0
**Last Updated:** 2025-10-31
**Purpose:** Practical examples of task batching for PaiiD trading application development

---

## Overview

This document provides realistic examples of how to structure task definitions for optimal batching and parallel execution in the MOD SQUAD system. Each example is based on actual PaiiD codebase patterns and demonstrates different dependency scenarios.

**Key Concepts:**
- **Parallel Tasks:** Independent tasks that can run simultaneously (share no file modifications)
- **Sequential Tasks:** Tasks with dependencies (must run in order)
- **Batching:** Grouping tasks into optimal execution sets to maximize parallelization
- **Intersections:** File conflicts that force sequential execution

---

## Example 1: Parallel Router Updates

**Scenario:** Add new health metrics to three independent backend routers that don't share any files.

### Tasks Definition

```json
{
  "tasks": [
    {
      "id": "health-metrics",
      "description": "Add uptime and memory metrics to health router",
      "squad": "ALPHA",
      "file_modifications": [
        "backend/app/routers/health.py"
      ],
      "dependencies": []
    },
    {
      "id": "order-metrics",
      "description": "Add order execution time metrics to orders router",
      "squad": "ALPHA",
      "file_modifications": [
        "backend/app/routers/orders.py"
      ],
      "dependencies": []
    },
    {
      "id": "position-metrics",
      "description": "Add position update metrics to portfolio router",
      "squad": "ALPHA",
      "file_modifications": [
        "backend/app/routers/portfolio.py"
      ],
      "dependencies": []
    }
  ]
}
```

### Execution

```bash
cd C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD\modsquad
python -m modsquad.batch_runner --tasks tasks.json --output batch_results.json
```

### Expected Output

```json
{
  "batches": [
    {
      "batch_id": 1,
      "tasks": ["health-metrics", "order-metrics", "position-metrics"],
      "parallel": true,
      "reason": "No file intersections detected"
    }
  ],
  "metrics": {
    "total_tasks": 3,
    "total_batches": 1,
    "parallelization_percent": 100.0,
    "speedup_factor": 3.0,
    "intersections": []
  }
}
```

### File Modifications

**After Execution:**
- ✅ `backend/app/routers/health.py` - Updated with uptime/memory metrics
- ✅ `backend/app/routers/orders.py` - Updated with execution time tracking
- ✅ `backend/app/routers/portfolio.py` - Updated with position update metrics

**Result:** All 3 tasks run in parallel (single batch), 3x speedup

---

## Example 2: Sequential with Dependencies (Database → Routes → Tests)

**Scenario:** Add a new `Strategy` table, create API endpoints, then add tests. Must execute in order due to code dependencies.

### Tasks Definition

```json
{
  "tasks": [
    {
      "id": "add-strategy-model",
      "description": "Create Strategy database model with SQLAlchemy",
      "squad": "ALPHA",
      "file_modifications": [
        "backend/app/models/database.py",
        "backend/alembic/versions/add_strategy_table.py"
      ],
      "dependencies": []
    },
    {
      "id": "add-strategy-router",
      "description": "Create /api/strategies endpoints (CRUD operations)",
      "squad": "ALPHA",
      "file_modifications": [
        "backend/app/routers/strategies.py",
        "backend/app/main.py"
      ],
      "dependencies": ["add-strategy-model"]
    },
    {
      "id": "add-strategy-tests",
      "description": "Add pytest tests for strategy endpoints",
      "squad": "ALPHA",
      "file_modifications": [
        "backend/tests/test_strategies.py"
      ],
      "dependencies": ["add-strategy-router"]
    }
  ]
}
```

### Execution

```bash
python -m modsquad.batch_runner --tasks tasks.json --output batch_results.json
```

### Expected Output

```json
{
  "batches": [
    {
      "batch_id": 1,
      "tasks": ["add-strategy-model"],
      "parallel": false,
      "reason": "Required by subsequent tasks"
    },
    {
      "batch_id": 2,
      "tasks": ["add-strategy-router"],
      "parallel": false,
      "reason": "Depends on: add-strategy-model"
    },
    {
      "batch_id": 3,
      "tasks": ["add-strategy-tests"],
      "parallel": false,
      "reason": "Depends on: add-strategy-router"
    }
  ],
  "metrics": {
    "total_tasks": 3,
    "total_batches": 3,
    "parallelization_percent": 0.0,
    "speedup_factor": 1.0,
    "intersections": []
  }
}
```

### File Modifications

**Batch 1:**
- ✅ `backend/app/models/database.py` - Add `Strategy` class
- ✅ `backend/alembic/versions/add_strategy_table.py` - Migration script

**Batch 2:**
- ✅ `backend/app/routers/strategies.py` - CRUD endpoints
- ✅ `backend/app/main.py` - Register router

**Batch 3:**
- ✅ `backend/tests/test_strategies.py` - Test coverage

**Result:** Sequential execution (dependency chain), no speedup

---

## Example 3: Frontend Component Additions (Parallel)

**Scenario:** Add three new independent workflow components to the radial menu interface.

### Tasks Definition

```json
{
  "tasks": [
    {
      "id": "add-risk-monitor",
      "description": "Create RiskMonitor.tsx component for portfolio risk analysis",
      "squad": "BRAVO",
      "file_modifications": [
        "frontend/components/RiskMonitor.tsx",
        "frontend/components/RiskMonitor.module.css"
      ],
      "dependencies": []
    },
    {
      "id": "add-tax-optimizer",
      "description": "Create TaxOptimizer.tsx for tax loss harvesting suggestions",
      "squad": "BRAVO",
      "file_modifications": [
        "frontend/components/TaxOptimizer.tsx",
        "frontend/lib/taxCalculations.ts"
      ],
      "dependencies": []
    },
    {
      "id": "add-options-screener",
      "description": "Create OptionsScreener.tsx for options chain analysis",
      "squad": "BRAVO",
      "file_modifications": [
        "frontend/components/OptionsScreener.tsx",
        "frontend/lib/optionsUtils.ts"
      ],
      "dependencies": []
    }
  ]
}
```

### Execution

```bash
python -m modsquad.batch_runner --tasks tasks.json --output batch_results.json
```

### Expected Output

```json
{
  "batches": [
    {
      "batch_id": 1,
      "tasks": ["add-risk-monitor", "add-tax-optimizer", "add-options-screener"],
      "parallel": true,
      "reason": "No file intersections detected"
    }
  ],
  "metrics": {
    "total_tasks": 3,
    "total_batches": 1,
    "parallelization_percent": 100.0,
    "speedup_factor": 3.0,
    "intersections": []
  }
}
```

### File Modifications

**After Execution:**
- ✅ `frontend/components/RiskMonitor.tsx` - New component
- ✅ `frontend/components/RiskMonitor.module.css` - Styling
- ✅ `frontend/components/TaxOptimizer.tsx` - New component
- ✅ `frontend/lib/taxCalculations.ts` - Tax calculation utilities
- ✅ `frontend/components/OptionsScreener.tsx` - New component
- ✅ `frontend/lib/optionsUtils.ts` - Options analysis utilities

**Result:** All 3 tasks run in parallel, 3x speedup

---

## Example 4: Database Migration + Code Updates (Mixed)

**Scenario:** Add position tracking columns, update models, modify routers, and update frontend. Some tasks can run in parallel within dependency levels.

### Tasks Definition

```json
{
  "tasks": [
    {
      "id": "migration-add-position-fields",
      "description": "Add last_updated, entry_time columns to positions table",
      "squad": "ALPHA",
      "file_modifications": [
        "backend/alembic/versions/add_position_timestamps.py"
      ],
      "dependencies": []
    },
    {
      "id": "update-position-model",
      "description": "Update Position model with new timestamp fields",
      "squad": "ALPHA",
      "file_modifications": [
        "backend/app/models/database.py"
      ],
      "dependencies": ["migration-add-position-fields"]
    },
    {
      "id": "update-portfolio-router",
      "description": "Modify /api/positions to return timestamp data",
      "squad": "ALPHA",
      "file_modifications": [
        "backend/app/routers/portfolio.py"
      ],
      "dependencies": ["update-position-model"]
    },
    {
      "id": "update-orders-router",
      "description": "Modify /api/orders to set entry_time on fills",
      "squad": "ALPHA",
      "file_modifications": [
        "backend/app/routers/orders.py"
      ],
      "dependencies": ["update-position-model"]
    },
    {
      "id": "update-activepositions-component",
      "description": "Display position timestamps in ActivePositions.tsx",
      "squad": "BRAVO",
      "file_modifications": [
        "frontend/components/ActivePositions.tsx"
      ],
      "dependencies": ["update-portfolio-router"]
    },
    {
      "id": "update-analytics-component",
      "description": "Add holding period analysis to Analytics.tsx",
      "squad": "BRAVO",
      "file_modifications": [
        "frontend/components/Analytics.tsx"
      ],
      "dependencies": ["update-portfolio-router"]
    }
  ]
}
```

### Execution

```bash
python -m modsquad.batch_runner --tasks tasks.json --output batch_results.json
```

### Expected Output

```json
{
  "batches": [
    {
      "batch_id": 1,
      "tasks": ["migration-add-position-fields"],
      "parallel": false,
      "reason": "Required by subsequent tasks"
    },
    {
      "batch_id": 2,
      "tasks": ["update-position-model"],
      "parallel": false,
      "reason": "Depends on: migration-add-position-fields"
    },
    {
      "batch_id": 3,
      "tasks": ["update-portfolio-router", "update-orders-router"],
      "parallel": true,
      "reason": "Both depend on batch 2, no file intersections"
    },
    {
      "batch_id": 4,
      "tasks": ["update-activepositions-component", "update-analytics-component"],
      "parallel": true,
      "reason": "Both depend on batch 3, no file intersections"
    }
  ],
  "metrics": {
    "total_tasks": 6,
    "total_batches": 4,
    "parallelization_percent": 66.7,
    "speedup_factor": 1.5,
    "intersections": []
  }
}
```

### File Modifications

**Batch 1:**
- ✅ `backend/alembic/versions/add_position_timestamps.py` - Migration

**Batch 2:**
- ✅ `backend/app/models/database.py` - Model updates

**Batch 3 (Parallel):**
- ✅ `backend/app/routers/portfolio.py` - Return timestamps
- ✅ `backend/app/routers/orders.py` - Set entry_time

**Batch 4 (Parallel):**
- ✅ `frontend/components/ActivePositions.tsx` - Display timestamps
- ✅ `frontend/components/Analytics.tsx` - Holding period charts

**Result:** 4 batches (2 parallel), 66.7% parallelization, 1.5x speedup

---

## Example 5: Multi-Squad Extension Additions

**Scenario:** Add Tradier streaming quotes (BRAVO) and Alpaca webhooks (CHARLIE) simultaneously, plus a frontend dashboard (DELTA) that depends on both.

### Tasks Definition

```json
{
  "tasks": [
    {
      "id": "tradier-streaming-service",
      "description": "Implement Tradier WebSocket streaming quotes service",
      "squad": "BRAVO",
      "file_modifications": [
        "backend/app/services/tradier_streaming.py",
        "backend/requirements.txt"
      ],
      "dependencies": []
    },
    {
      "id": "tradier-streaming-router",
      "description": "Create /api/market/stream endpoint for quote subscriptions",
      "squad": "BRAVO",
      "file_modifications": [
        "backend/app/routers/market.py",
        "backend/app/main.py"
      ],
      "dependencies": ["tradier-streaming-service"]
    },
    {
      "id": "alpaca-webhooks-service",
      "description": "Implement Alpaca trade event webhooks handler",
      "squad": "CHARLIE",
      "file_modifications": [
        "backend/app/services/alpaca_webhooks.py",
        "backend/requirements.txt"
      ],
      "dependencies": []
    },
    {
      "id": "alpaca-webhooks-router",
      "description": "Create /api/webhooks/alpaca endpoint for trade events",
      "squad": "CHARLIE",
      "file_modifications": [
        "backend/app/routers/webhooks.py",
        "backend/app/main.py"
      ],
      "dependencies": ["alpaca-webhooks-service"]
    },
    {
      "id": "live-dashboard-component",
      "description": "Create LiveDashboard.tsx with real-time quotes and trade events",
      "squad": "DELTA",
      "file_modifications": [
        "frontend/components/LiveDashboard.tsx",
        "frontend/lib/websocketClient.ts"
      ],
      "dependencies": ["tradier-streaming-router", "alpaca-webhooks-router"]
    }
  ]
}
```

### Execution

```bash
python -m modsquad.batch_runner --tasks tasks.json --output batch_results.json
```

### Expected Output

```json
{
  "batches": [
    {
      "batch_id": 1,
      "tasks": ["tradier-streaming-service", "alpaca-webhooks-service"],
      "parallel": true,
      "reason": "Independent services, requirements.txt merge handled"
    },
    {
      "batch_id": 2,
      "tasks": ["tradier-streaming-router", "alpaca-webhooks-router"],
      "parallel": false,
      "reason": "File intersection: backend/app/main.py"
    },
    {
      "batch_id": 3,
      "tasks": ["live-dashboard-component"],
      "parallel": false,
      "reason": "Depends on: tradier-streaming-router, alpaca-webhooks-router"
    }
  ],
  "metrics": {
    "total_tasks": 5,
    "total_batches": 3,
    "parallelization_percent": 40.0,
    "speedup_factor": 1.67,
    "intersections": [
      {
        "file": "backend/app/main.py",
        "tasks": ["tradier-streaming-router", "alpaca-webhooks-router"],
        "resolution": "Sequential execution required"
      }
    ]
  }
}
```

### File Modifications

**Batch 1 (Parallel):**
- ✅ `backend/app/services/tradier_streaming.py` - Streaming service (BRAVO)
- ✅ `backend/app/services/alpaca_webhooks.py` - Webhooks handler (CHARLIE)
- ✅ `backend/requirements.txt` - Dependencies merged

**Batch 2 (Sequential - main.py conflict):**
- ✅ `backend/app/routers/market.py` - Streaming endpoint
- ✅ `backend/app/main.py` - Register market router (BRAVO)
- ✅ `backend/app/routers/webhooks.py` - Webhooks endpoint
- ✅ `backend/app/main.py` - Register webhooks router (CHARLIE)

**Batch 3:**
- ✅ `frontend/components/LiveDashboard.tsx` - Real-time dashboard (DELTA)
- ✅ `frontend/lib/websocketClient.ts` - WebSocket client utilities

**Result:** 3 batches (1 parallel), 40% parallelization, 1.67x speedup

**Note:** File intersection on `backend/app/main.py` forces sequential execution for batch 2. Alternative: Create a single task that registers both routers.

---

## Example 6: File Intersection Detection

**Scenario:** Demonstrating how file conflicts force sequential execution even without explicit dependencies.

### Tasks Definition

```json
{
  "tasks": [
    {
      "id": "add-market-cache",
      "description": "Add Redis caching to market data endpoints",
      "squad": "ALPHA",
      "file_modifications": [
        "backend/app/routers/market.py",
        "backend/app/core/cache.py"
      ],
      "dependencies": []
    },
    {
      "id": "add-market-logging",
      "description": "Add structured logging to market data endpoints",
      "squad": "ALPHA",
      "file_modifications": [
        "backend/app/routers/market.py",
        "backend/app/core/logging.py"
      ],
      "dependencies": []
    },
    {
      "id": "add-market-metrics",
      "description": "Add Prometheus metrics to market data endpoints",
      "squad": "ALPHA",
      "file_modifications": [
        "backend/app/routers/market.py",
        "backend/app/core/metrics.py"
      ],
      "dependencies": []
    }
  ]
}
```

### Expected Output

```json
{
  "batches": [
    {
      "batch_id": 1,
      "tasks": ["add-market-cache"],
      "parallel": false,
      "reason": "File intersection with subsequent tasks"
    },
    {
      "batch_id": 2,
      "tasks": ["add-market-logging"],
      "parallel": false,
      "reason": "File intersection with subsequent tasks"
    },
    {
      "batch_id": 3,
      "tasks": ["add-market-metrics"],
      "parallel": false,
      "reason": "File intersection with previous tasks"
    }
  ],
  "metrics": {
    "total_tasks": 3,
    "total_batches": 3,
    "parallelization_percent": 0.0,
    "speedup_factor": 1.0,
    "intersections": [
      {
        "file": "backend/app/routers/market.py",
        "tasks": ["add-market-cache", "add-market-logging", "add-market-metrics"],
        "resolution": "Sequential execution required"
      }
    ]
  }
}
```

**Analysis:** All three tasks modify `market.py`, forcing sequential execution despite no explicit dependencies.

**Optimization Strategy:**
1. **Combine tasks:** Merge into single task "add-market-observability" that adds caching, logging, and metrics together
2. **Split file:** Refactor market.py into smaller modules (market_quotes.py, market_bars.py) to reduce conflicts
3. **Accept sequential:** If tasks are small, sequential execution may be acceptable

---

## Best Practices for Task Definition

### 1. **Minimize File Intersections**

**Bad:**
```json
{
  "tasks": [
    {"id": "add-endpoint-1", "file_modifications": ["app/main.py"]},
    {"id": "add-endpoint-2", "file_modifications": ["app/main.py"]},
    {"id": "add-endpoint-3", "file_modifications": ["app/main.py"]}
  ]
}
```

**Good:**
```json
{
  "tasks": [
    {"id": "add-endpoints", "file_modifications": ["app/main.py"], "description": "Add 3 new endpoints in single task"}
  ]
}
```

### 2. **Declare Explicit Dependencies**

**Bad:**
```json
{
  "tasks": [
    {"id": "add-model", "file_modifications": ["models.py"]},
    {"id": "add-router", "file_modifications": ["routers.py"]}
  ]
}
```
*Relies on implicit understanding that router needs model*

**Good:**
```json
{
  "tasks": [
    {"id": "add-model", "file_modifications": ["models.py"], "dependencies": []},
    {"id": "add-router", "file_modifications": ["routers.py"], "dependencies": ["add-model"]}
  ]
}
```

### 3. **Group by File Scope**

**Bad:**
```json
{
  "tasks": [
    {"id": "update-frontend", "file_modifications": ["component.tsx", "router.py", "model.py"]}
  ]
}
```
*Mixing frontend and backend in single task*

**Good:**
```json
{
  "tasks": [
    {"id": "update-backend", "file_modifications": ["router.py", "model.py"]},
    {"id": "update-frontend", "file_modifications": ["component.tsx"], "dependencies": ["update-backend"]}
  ]
}
```

### 4. **Use Appropriate Granularity**

**Too Fine:**
```json
{
  "tasks": [
    {"id": "add-import", "file_modifications": ["router.py"]},
    {"id": "add-function", "file_modifications": ["router.py"]},
    {"id": "add-route", "file_modifications": ["router.py"]}
  ]
}
```

**Too Coarse:**
```json
{
  "tasks": [
    {"id": "implement-feature", "file_modifications": ["20-different-files.py"]}
  ]
}
```

**Just Right:**
```json
{
  "tasks": [
    {"id": "add-portfolio-router", "file_modifications": ["app/routers/portfolio.py", "app/main.py"]},
    {"id": "add-portfolio-tests", "file_modifications": ["tests/test_portfolio.py"]}
  ]
}
```

---

## Common PaiiD Patterns

### Backend Router Addition

```json
{
  "id": "add-xyz-router",
  "description": "Create /api/xyz endpoints",
  "squad": "ALPHA",
  "file_modifications": [
    "backend/app/routers/xyz.py",
    "backend/app/main.py"
  ],
  "dependencies": []
}
```

### Frontend Component Addition

```json
{
  "id": "add-xyz-component",
  "description": "Create XYZ.tsx workflow component",
  "squad": "BRAVO",
  "file_modifications": [
    "frontend/components/XYZ.tsx",
    "frontend/lib/xyzUtils.ts"
  ],
  "dependencies": []
}
```

### Database Migration

```json
{
  "id": "add-xyz-table",
  "description": "Add XYZ table with Alembic",
  "squad": "ALPHA",
  "file_modifications": [
    "backend/app/models/database.py",
    "backend/alembic/versions/add_xyz_table.py"
  ],
  "dependencies": []
}
```

### API Integration

```json
{
  "id": "add-tradier-xyz",
  "description": "Integrate Tradier XYZ endpoint",
  "squad": "CHARLIE",
  "file_modifications": [
    "backend/app/services/tradier_client.py",
    "backend/app/routers/market.py"
  ],
  "dependencies": []
}
```

---

## Performance Metrics Guide

### Parallelization Percentage

```
Parallelization % = (Tasks in Parallel Batches / Total Tasks) × 100
```

**Example:**
- 10 tasks total
- Batch 1: 4 tasks (parallel)
- Batch 2: 3 tasks (parallel)
- Batch 3: 2 tasks (sequential)
- Batch 4: 1 task (sequential)

```
Parallelization % = (4 + 3) / 10 × 100 = 70%
```

### Speedup Factor

```
Speedup Factor = Total Tasks / Total Batches
```

**Example:**
- 10 tasks, 4 batches
- Speedup = 10 / 4 = 2.5x

**Theoretical maximum:** Total tasks (all parallel)
**Theoretical minimum:** 1.0x (all sequential)

### Optimization Targets

| Parallelization % | Speedup Factor | Rating | Action |
|-------------------|----------------|--------|--------|
| 80-100% | 2.5x+ | Excellent | Maintain |
| 60-79% | 1.8-2.5x | Good | Minor optimization |
| 40-59% | 1.4-1.8x | Fair | Review file intersections |
| 20-39% | 1.2-1.4x | Poor | Refactor task definitions |
| 0-19% | 1.0-1.2x | Critical | Major restructuring needed |

---

## Troubleshooting

### Issue: All Tasks Sequential Despite No Dependencies

**Cause:** File intersections forcing sequential execution

**Solution:**
```bash
# Check for file conflicts
python -m modsquad.batch_runner --tasks tasks.json --dry-run --verbose

# Look for "intersections" in output
# Refactor to split files or combine tasks
```

### Issue: Incorrect Dependency Order

**Cause:** Missing or circular dependencies

**Solution:**
```bash
# Validate dependency graph
python -m modsquad.validator --check-deps tasks.json

# Fix circular dependencies or add missing deps
```

### Issue: Low Parallelization Percentage

**Cause:** Too many shared files (especially main.py, database.py)

**Solution:**
1. Combine tasks that modify the same file
2. Split large files into smaller modules
3. Use dependency injection instead of direct imports

---

## Advanced Example: Optimizing main.py Conflicts

### Before Optimization (Sequential)

```json
{
  "tasks": [
    {"id": "add-router-1", "file_modifications": ["routers/r1.py", "main.py"]},
    {"id": "add-router-2", "file_modifications": ["routers/r2.py", "main.py"]},
    {"id": "add-router-3", "file_modifications": ["routers/r3.py", "main.py"]}
  ]
}
```

**Result:** 3 batches (sequential), 0% parallelization

### After Optimization (Parallel)

```json
{
  "tasks": [
    {"id": "add-routers", "file_modifications": ["routers/r1.py", "routers/r2.py", "routers/r3.py"]},
    {"id": "register-routers", "file_modifications": ["main.py"], "dependencies": ["add-routers"]}
  ]
}
```

**Result:** 2 batches, 50% parallelization (all router creation in batch 1)

---

## File Path Conventions

All file paths in `file_modifications` should be:
- ✅ Relative to repository root
- ✅ Use forward slashes (even on Windows)
- ✅ Include file extension

**Examples:**
```json
"backend/app/routers/market.py"
"frontend/components/Analytics.tsx"
"backend/alembic/versions/abc123_migration.py"
```

**Not:**
```json
"C:\\Users\\...\\backend\\app\\routers\\market.py"  // Absolute paths
"backend\\app\\routers\\market.py"  // Backslashes
"backend/app/routers/market"  // Missing extension
```

---

## Next Steps

1. **Try Examples:** Run each example to understand batching behavior
2. **Create Custom Tasks:** Define tasks for your feature development
3. **Optimize:** Use metrics to improve parallelization
4. **Integrate:** Incorporate batching into CI/CD workflows

**Related Documentation:**
- `COMPLETE_DEPLOYMENT_PLAN.md` - Full MOD SQUAD deployment guide
- `SQUAD_ASSIGNMENTS.md` - Squad responsibilities and file ownership
- `TASK_TEMPLATE.md` - Task definition schema and validation

---

**Last Updated:** 2025-10-31
**Maintained By:** MOD SQUAD Core Team
