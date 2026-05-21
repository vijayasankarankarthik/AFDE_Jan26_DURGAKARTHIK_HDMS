"""
routers/analytics.py — REST endpoints for the Analytics dashboard.

All endpoints are read-only GET routes.  They are available under the
prefix /api/analytics (registered in main.py).

Query parameter `source`:
  - "live"      → queries the main `tickets` table (default)
  - "reporting" → queries the `reporting_tickets` table (ETL-imported data)
"""

from __future__ import annotations

from typing import Literal, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from analytics.services import AnalyticsService
from analytics.schemas import (
    CategoryBreakdown,
    DepartmentBreakdown,
    ETLJobResponse,
    PriorityBreakdown,
    ResolutionTimeBreakdown,
    StatusBreakdown,
    TicketSummary,
    TopDepartments,
    VolumeTrend,
)
from typing import List

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
)


def _use_reporting(source: str) -> bool:
    return source.lower() == "reporting"


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

@router.get("/summary", response_model=TicketSummary, summary="Overall ticket statistics")
def get_summary(
    source: str = Query("live", description="'live' or 'reporting'"),
    db: Session = Depends(get_db),
):
    """Return high-level ticket counts and KPIs."""
    return AnalyticsService(db).get_summary(use_reporting=_use_reporting(source))


# ---------------------------------------------------------------------------
# Breakdowns
# ---------------------------------------------------------------------------

@router.get(
    "/by-category",
    response_model=CategoryBreakdown,
    summary="Ticket counts grouped by issue category",
)
def get_category_breakdown(
    source: str = Query("live"),
    db: Session = Depends(get_db),
):
    return AnalyticsService(db).get_category_breakdown(use_reporting=_use_reporting(source))


@router.get(
    "/by-priority",
    response_model=PriorityBreakdown,
    summary="Ticket counts grouped by priority",
)
def get_priority_breakdown(
    source: str = Query("live"),
    db: Session = Depends(get_db),
):
    return AnalyticsService(db).get_priority_breakdown(use_reporting=_use_reporting(source))


@router.get(
    "/by-status",
    response_model=StatusBreakdown,
    summary="Ticket counts grouped by status",
)
def get_status_breakdown(
    source: str = Query("live"),
    db: Session = Depends(get_db),
):
    return AnalyticsService(db).get_status_breakdown(use_reporting=_use_reporting(source))


@router.get(
    "/by-department",
    response_model=DepartmentBreakdown,
    summary="Ticket breakdown per department with resolution rates",
)
def get_department_breakdown(
    source: str = Query("live"),
    db: Session = Depends(get_db),
):
    return AnalyticsService(db).get_department_breakdown(use_reporting=_use_reporting(source))


# ---------------------------------------------------------------------------
# Trends
# ---------------------------------------------------------------------------

@router.get(
    "/trend",
    response_model=VolumeTrend,
    summary="Ticket volume over time",
)
def get_volume_trend(
    granularity: str = Query("monthly", description="'daily', 'weekly', or 'monthly'"),
    source: str = Query("live"),
    db: Session = Depends(get_db),
):
    return AnalyticsService(db).get_volume_trend(
        granularity=granularity, use_reporting=_use_reporting(source)
    )


# ---------------------------------------------------------------------------
# Resolution time
# ---------------------------------------------------------------------------

@router.get(
    "/resolution-time",
    response_model=ResolutionTimeBreakdown,
    summary="Average resolution time by category",
)
def get_resolution_time(
    source: str = Query("live"),
    db: Session = Depends(get_db),
):
    return AnalyticsService(db).get_resolution_time(use_reporting=_use_reporting(source))


# ---------------------------------------------------------------------------
# Top departments
# ---------------------------------------------------------------------------

@router.get(
    "/top-departments",
    response_model=TopDepartments,
    summary="Ranked list of departments by ticket volume",
)
def get_top_departments(
    limit: int = Query(10, ge=1, le=50),
    source: str = Query("live"),
    db: Session = Depends(get_db),
):
    return AnalyticsService(db).get_top_departments(
        limit=limit, use_reporting=_use_reporting(source)
    )


# ---------------------------------------------------------------------------
# ETL job history
# ---------------------------------------------------------------------------

@router.get(
    "/etl-jobs",
    response_model=List[ETLJobResponse],
    summary="Recent CSV upload / ETL pipeline jobs",
)
def get_etl_jobs(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return AnalyticsService(db).get_etl_jobs(limit=limit)
