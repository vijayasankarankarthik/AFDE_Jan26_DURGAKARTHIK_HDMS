"""
analytics/schemas.py — Pydantic response models for all analytics endpoints.

All models use Config.from_attributes = True so they can be constructed
directly from SQLAlchemy row objects where needed.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
# Shared base
# ---------------------------------------------------------------------------

class _Base(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Summary / overview
# ---------------------------------------------------------------------------

class TicketSummary(_Base):
    """High-level counts shown on the Analytics dashboard header."""
    total_tickets: int
    open_tickets: int
    in_progress_tickets: int
    resolved_tickets: int
    closed_tickets: int
    resolution_rate: float          # 0–1 fraction
    avg_resolution_days: Optional[float]


# ---------------------------------------------------------------------------
# Category breakdown
# ---------------------------------------------------------------------------

class CategoryStat(_Base):
    category: str
    count: int
    percentage: float


class CategoryBreakdown(_Base):
    categories: List[CategoryStat]
    total: int


# ---------------------------------------------------------------------------
# Priority breakdown
# ---------------------------------------------------------------------------

class PriorityStat(_Base):
    priority: str
    count: int
    percentage: float


class PriorityBreakdown(_Base):
    priorities: List[PriorityStat]
    total: int


# ---------------------------------------------------------------------------
# Status breakdown
# ---------------------------------------------------------------------------

class StatusStat(_Base):
    status: str
    count: int
    percentage: float


class StatusBreakdown(_Base):
    statuses: List[StatusStat]
    total: int


# ---------------------------------------------------------------------------
# Department breakdown
# ---------------------------------------------------------------------------

class DepartmentStat(_Base):
    department: str
    total: int
    open_count: int
    resolved_count: int
    resolution_rate: float


class DepartmentBreakdown(_Base):
    departments: List[DepartmentStat]


# ---------------------------------------------------------------------------
# Volume trend (time series)
# ---------------------------------------------------------------------------

class TrendPoint(_Base):
    """Single data point in a time-series chart."""
    period: str        # ISO date string: "2024-01" (monthly) or "2024-01-15" (daily)
    count: int
    resolved: int
    open: int


class VolumeTrend(_Base):
    granularity: str           # "daily" | "weekly" | "monthly"
    data: List[TrendPoint]


# ---------------------------------------------------------------------------
# Resolution time
# ---------------------------------------------------------------------------

class ResolutionTimeStat(_Base):
    category: str
    avg_days: float
    min_days: float
    max_days: float
    sample_count: int


class ResolutionTimeBreakdown(_Base):
    by_category: List[ResolutionTimeStat]
    overall_avg_days: Optional[float]


# ---------------------------------------------------------------------------
# Top departments / agents
# ---------------------------------------------------------------------------

class TopDepartment(_Base):
    department: str
    ticket_count: int
    open_count: int
    high_priority_count: int


class TopDepartments(_Base):
    departments: List[TopDepartment]


# ---------------------------------------------------------------------------
# ETL job status (for recent uploads list)
# ---------------------------------------------------------------------------

class ETLJobResponse(_Base):
    job_id: int
    filename: str
    batch_id: UUID
    total_rows: Optional[int]
    inserted_rows: Optional[int]
    duplicate_rows: Optional[int]
    error_rows: Optional[int]
    status: str
    error_message: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]
