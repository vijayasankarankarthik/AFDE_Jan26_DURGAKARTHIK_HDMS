"""
analytics/services.py — Business logic layer between the router and raw queries.

AnalyticsService wraps every query function, adds caching headers logic,
handles empty-result gracefully, and owns the decision of which data source
(live tickets vs reporting_tickets) to use.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from analytics import queries
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
from models import ETLJob


class AnalyticsService:
    """
    Thin service layer that translates between raw query results and
    validated Pydantic response models.
    """

    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def get_summary(self, use_reporting: bool = False) -> TicketSummary:
        data = queries.query_ticket_summary(self.db, use_reporting=use_reporting)
        return TicketSummary(**data)

    # ------------------------------------------------------------------
    # Breakdowns
    # ------------------------------------------------------------------

    def get_category_breakdown(
        self, use_reporting: bool = False
    ) -> CategoryBreakdown:
        data = queries.query_category_breakdown(self.db, use_reporting=use_reporting)
        return CategoryBreakdown(**data)

    def get_priority_breakdown(
        self, use_reporting: bool = False
    ) -> PriorityBreakdown:
        data = queries.query_priority_breakdown(self.db, use_reporting=use_reporting)
        return PriorityBreakdown(**data)

    def get_status_breakdown(
        self, use_reporting: bool = False
    ) -> StatusBreakdown:
        data = queries.query_status_breakdown(self.db, use_reporting=use_reporting)
        return StatusBreakdown(**data)

    def get_department_breakdown(
        self, use_reporting: bool = False
    ) -> DepartmentBreakdown:
        data = queries.query_department_breakdown(self.db, use_reporting=use_reporting)
        return DepartmentBreakdown(**data)

    # ------------------------------------------------------------------
    # Trends
    # ------------------------------------------------------------------

    def get_volume_trend(
        self,
        granularity: str = "monthly",
        use_reporting: bool = False,
    ) -> VolumeTrend:
        if granularity not in ("daily", "weekly", "monthly"):
            granularity = "monthly"
        data = queries.query_volume_trend(
            self.db, granularity=granularity, use_reporting=use_reporting
        )
        return VolumeTrend(**data)

    # ------------------------------------------------------------------
    # Resolution time
    # ------------------------------------------------------------------

    def get_resolution_time(
        self, use_reporting: bool = False
    ) -> ResolutionTimeBreakdown:
        data = queries.query_resolution_time(self.db, use_reporting=use_reporting)
        return ResolutionTimeBreakdown(**data)

    # ------------------------------------------------------------------
    # Top departments
    # ------------------------------------------------------------------

    def get_top_departments(
        self, limit: int = 10, use_reporting: bool = False
    ) -> TopDepartments:
        limit = max(1, min(limit, 50))  # Clamp to [1, 50]
        data = queries.query_top_departments(
            self.db, limit=limit, use_reporting=use_reporting
        )
        return TopDepartments(**data)

    # ------------------------------------------------------------------
    # ETL job history
    # ------------------------------------------------------------------

    def get_etl_jobs(self, limit: int = 20) -> List[ETLJobResponse]:
        limit = max(1, min(limit, 100))
        jobs = (
            self.db.query(ETLJob)
            .order_by(ETLJob.started_at.desc())
            .limit(limit)
            .all()
        )
        return [ETLJobResponse.model_validate(j) for j in jobs]
