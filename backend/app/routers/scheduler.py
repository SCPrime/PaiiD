"""
Scheduler API Router (Simplified - File-based)
REST endpoints for managing scheduled trading tasks
"""

import json
import logging
import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ..core.unified_auth import get_current_user_unified
from ..models.database import User
from ..scheduler import APPROVALS_DIR, EXECUTIONS_DIR, SCHEDULES_DIR, get_scheduler


router = APIRouter(prefix="/scheduler", tags=["scheduler"])
logger = logging.getLogger(__name__)


# ========================
# Request/Response Models
# ========================


class ScheduleCreate(BaseModel):
    name: str
    type: str  # morning_routine, news_review, ai_recs, custom
    cron_expression: str
    timezone: str = "America/New_York"
    requires_approval: bool = True
    enabled: bool = True


class ScheduleUpdate(BaseModel):
    name: str | None = None
    cron_expression: str | None = None
    timezone: str | None = None
    requires_approval: bool | None = None
    enabled: bool | None = None


class ScheduleResponse(BaseModel):
    id: str
    name: str
    type: str
    enabled: bool
    cron_expression: str
    timezone: str
    requires_approval: bool
    last_run: str | None
    next_run: str | None
    status: str
    created_at: str

    class Config:
        from_attributes = True


class ExecutionResponse(BaseModel):
    id: str
    schedule_id: str
    schedule_name: str
    started_at: str
    completed_at: str | None
    status: str
    result: str | None
    error: str | None

    class Config:
        from_attributes = True


class ApprovalResponse(BaseModel):
    id: str
    execution_id: str
    schedule_name: str
    trade_type: str
    symbol: str
    quantity: int
    estimated_price: float
    estimated_value: float
    reason: str
    risk_score: int
    ai_confidence: float
    supporting_data: dict | None
    created_at: str
    expires_at: str

    class Config:
        from_attributes = True


class ApprovalDecision(BaseModel):
    reason: str | None = None


# ========================
# Helper Functions
# ========================


def _load_schedule(schedule_id: str) -> dict | None:
    """Load schedule from file"""
    schedule_file = SCHEDULES_DIR / f"{schedule_id}.json"
    if schedule_file.exists():
        with open(schedule_file) as f:
            return json.load(f)
    return None


def _save_schedule(schedule: dict):
    """Save schedule to file"""
    schedule_file = SCHEDULES_DIR / f"{schedule['id']}.json"
    with open(schedule_file, "w") as f:
        json.dump(schedule, f, indent=2)


def _delete_schedule_file(schedule_id: str):
    """Delete schedule file"""
    schedule_file = SCHEDULES_DIR / f"{schedule_id}.json"
    if schedule_file.exists():
        schedule_file.unlink()


def _load_all_schedules() -> list[dict]:
    """Load all schedules from files"""
    schedules = []
    for schedule_file in SCHEDULES_DIR.glob("*.json"):
        with open(schedule_file) as f:
            schedules.append(json.load(f))
    return sorted(schedules, key=lambda x: x.get("created_at", ""), reverse=True)


def _load_executions(limit: int = 20, schedule_id: str | None = None) -> list[dict]:
    """Load execution history from files"""
    executions = []
    for exec_file in EXECUTIONS_DIR.glob("*.json"):
        with open(exec_file) as f:
            execution = json.load(f)
            if schedule_id is None or execution["schedule_id"] == schedule_id:
                executions.append(execution)

    # Sort by started_at descending
    executions = sorted(executions, key=lambda x: x.get("started_at", ""), reverse=True)
    return executions[:limit]


def _load_pending_approvals() -> list[dict]:
    """Load pending approvals from files"""
    approvals = []
    now = datetime.now(UTC)

    for approval_file in APPROVALS_DIR.glob("*.json"):
        with open(approval_file) as f:
            approval = json.load(f)
            # Only include pending and not expired
            if approval["status"] == "pending":
                expires_at = datetime.fromisoformat(approval["expires_at"])
                if expires_at > now:
                    approvals.append(approval)

    return sorted(approvals, key=lambda x: x.get("created_at", ""), reverse=True)


def _update_approval(approval_id: str, updates: dict):
    """Update approval file"""
    approval_file = APPROVALS_DIR / f"{approval_id}.json"
    if approval_file.exists():
        with open(approval_file) as f:
            approval = json.load(f)
        approval.update(updates)
        with open(approval_file, "w") as f:
            json.dump(approval, f, indent=2)


# ========================
# Schedule Management
# ========================


@router.get("/schedules", response_model=list[ScheduleResponse])
async def list_schedules(current_user: User = Depends(get_current_user_unified)):
    """Get all schedules for the current user"""
    try:
        schedules = _load_all_schedules()

        # Enrich with scheduler info
        scheduler = get_scheduler()
        enriched = []
        for schedule in schedules:
            sched_dict = {
                "id": schedule["id"],
                "name": schedule["name"],
                "type": schedule["type"],
                "enabled": schedule["enabled"],
                "cron_expression": schedule["cron_expression"],
                "timezone": schedule["timezone"],
                "requires_approval": schedule["requires_approval"],
                "last_run": schedule.get("last_run"),
                "status": schedule["status"],
                "created_at": schedule["created_at"],
                "next_run": None,
            }

            if schedule["enabled"]:
                info = scheduler.get_schedule_info(schedule["id"])
                if info:
                    sched_dict["next_run"] = info.get("next_run")

            enriched.append(sched_dict)

        return enriched
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list schedules: {e!s}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list schedules")


@router.post(
    "/schedules", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED
)
async def create_schedule(
    schedule_data: ScheduleCreate, current_user: User = Depends(get_current_user_unified)
):
    """Create a new schedule"""
    try:
        schedule_id = str(uuid.uuid4())
        schedule = {
            "id": schedule_id,
            "name": schedule_data.name,
            "type": schedule_data.type,
            "cron_expression": schedule_data.cron_expression,
            "timezone": schedule_data.timezone,
            "requires_approval": schedule_data.requires_approval,
            "enabled": schedule_data.enabled,
            "status": "active" if schedule_data.enabled else "paused",
            "created_at": datetime.now(UTC).isoformat(),
            "last_run": None,
        }

        _save_schedule(schedule)

        if schedule_data.enabled:
            scheduler = get_scheduler()
            try:
                await scheduler.add_schedule(
                    schedule_id=schedule_id,
                    schedule_type=schedule_data.type,
                    cron_expression=schedule_data.cron_expression,
                    timezone=schedule_data.timezone,
                    requires_approval=schedule_data.requires_approval,
                )
            except Exception as e:
                _delete_schedule_file(schedule_id)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to create schedule: {e!s}",
                )

        return schedule
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create schedule: {e!s}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create schedule")


@router.patch("/schedules/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: str,
    schedule_data: ScheduleUpdate,
    current_user: User = Depends(get_current_user_unified),
):
    """Update an existing schedule"""
    try:
        schedule = _load_schedule(schedule_id)
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")

        update_data = schedule_data.model_dump(exclude_unset=True)
        scheduler = get_scheduler()

        if "enabled" in update_data:
            if update_data["enabled"] and not schedule["enabled"]:
                await scheduler.resume_schedule(schedule_id)
                schedule["status"] = "active"
            elif not update_data["enabled"] and schedule["enabled"]:
                await scheduler.pause_schedule(schedule_id)
                schedule["status"] = "paused"

        if "cron_expression" in update_data or "timezone" in update_data:
            await scheduler.remove_schedule(schedule_id)
            if schedule.get("enabled", False):
                await scheduler.add_schedule(
                    schedule_id=schedule_id,
                    schedule_type=schedule["type"],
                    cron_expression=update_data.get(
                        "cron_expression", schedule["cron_expression"]
                    ),
                    timezone=update_data.get("timezone", schedule["timezone"]),
                    requires_approval=schedule["requires_approval"],
                )

        schedule.update(update_data)
        _save_schedule(schedule)
        return schedule
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update schedule {schedule_id}: {e!s}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update schedule")


@router.delete("/schedules/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    schedule_id: str, current_user: User = Depends(get_current_user_unified)
):
    """Delete a schedule"""
    try:
        schedule = _load_schedule(schedule_id)
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")

        scheduler = get_scheduler()
        await scheduler.remove_schedule(schedule_id)
        _delete_schedule_file(schedule_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete schedule {schedule_id}: {e!s}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete schedule")


# ========================
# Emergency Controls
# ========================


@router.post("/pause-all")
async def pause_all_schedules(current_user: User = Depends(get_current_user_unified)):
    """Emergency pause all schedules"""
    try:
        scheduler = get_scheduler()
        await scheduler.pause_all()
        for schedule in _load_all_schedules():
            schedule["status"] = "paused"
            schedule["enabled"] = False
            _save_schedule(schedule)
        return {"message": "All schedules paused"}
    except Exception as e:
        logger.error(f"Failed to pause all schedules: {e!s}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to pause schedules")


@router.post("/resume-all")
async def resume_all_schedules(current_user: User = Depends(get_current_user_unified)):
    """Resume all paused schedules"""
    try:
        scheduler = get_scheduler()
        await scheduler.resume_all()
        for schedule in _load_all_schedules():
            schedule["status"] = "active"
            schedule["enabled"] = True
            _save_schedule(schedule)
        return {"message": "All schedules resumed"}
    except Exception as e:
        logger.error(f"Failed to resume all schedules: {e!s}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to resume schedules")


# ========================
# Execution History
# ========================


@router.get("/executions", response_model=list[ExecutionResponse])
async def list_executions(
    limit: int = 20,
    schedule_id: str | None = None,
    current_user: User = Depends(get_current_user_unified),
):
    """Get execution history"""
    try:
        executions = _load_executions(limit, schedule_id)
        return executions
    except Exception as e:
        logger.error(f"Failed to list executions: {e!s}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list executions")


# ========================
# Approval Workflow
# ========================


@router.get("/pending-approvals", response_model=list[ApprovalResponse])
async def list_pending_approvals(current_user: User = Depends(get_current_user_unified)):
    """Get all pending trade approvals"""
    try:
        approvals = _load_pending_approvals()
        return approvals
    except Exception as e:
        logger.error(f"Failed to list pending approvals: {e!s}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list approvals")


@router.post("/approvals/{approval_id}/approve")
async def approve_trade(
    approval_id: str, current_user: User = Depends(get_current_user_unified)
):
    """Approve a pending trade"""
    try:
        approval_file = APPROVALS_DIR / f"{approval_id}.json"
        if not approval_file.exists():
            raise HTTPException(status_code=404, detail="Approval not found")

        with open(approval_file) as f:
            approval = json.load(f)

        if approval["status"] != "pending":
            raise HTTPException(status_code=400, detail="Approval already processed")

        expires_at = datetime.fromisoformat(approval["expires_at"])
        if expires_at < datetime.now(UTC):
            raise HTTPException(status_code=400, detail="Approval has expired")

        _update_approval(
            approval_id,
            {"status": "approved", "approved_at": datetime.now(UTC).isoformat()},
        )

        return {"message": "Trade approved and executed"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to approve trade {approval_id}: {e!s}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to approve trade")


@router.post("/approvals/{approval_id}/reject")
async def reject_trade(
    approval_id: str,
    decision: ApprovalDecision,
    current_user: User = Depends(get_current_user_unified),
):
    """Reject a pending trade"""
    try:
        approval_file = APPROVALS_DIR / f"{approval_id}.json"
        if not approval_file.exists():
            raise HTTPException(status_code=404, detail="Approval not found")

        with open(approval_file) as f:
            approval = json.load(f)

        if approval["status"] != "pending":
            raise HTTPException(status_code=400, detail="Approval already processed")

        _update_approval(
            approval_id,
            {
                "status": "rejected",
                "approved_at": datetime.now(UTC).isoformat(),
                "rejection_reason": decision.reason,
            },
        )

        return {"message": "Trade rejected"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reject trade {approval_id}: {e!s}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to reject trade")


# ========================
# Health & Status
# ========================


@router.get("/status")
async def scheduler_status(current_user: User = Depends(get_current_user_unified)):
    """Get scheduler health status"""
    try:
        scheduler = get_scheduler()
        return {
            "running": scheduler.running,
            "jobs_count": len(scheduler.scheduler.get_jobs()),
            "status": "healthy" if scheduler.running else "stopped",
        }
    except Exception as e:
        logger.error(f"Failed to get scheduler status: {e!s}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get scheduler status")
