"""
analytics/queries.py — Raw SQLAlchemy aggregation queries against
both the live `tickets` table and the `reporting_tickets` table.

All functions accept an optional `use_reporting` flag so the router can
direct traffic to whichever table the caller needs.

Query patterns:
  - Use func.count, func.avg, func.min, func.max for aggregations
  - All GROUP BY columns are projected in SELECT + group_by()
  - Date truncation is done with PostgreSQL's date_trunc() via func.date_trunc
  - Labels are assigned with .label() for consistent dict-key mapping
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import func, case, cast, Float, Integer, text
from sqlalchemy.orm import Session

from models import Ticket, ReportingTicket


def _model(use_reporting: bool):
    """Return the correct ORM model based on the data source flag."""
    return ReportingTicket if use_reporting else Ticket


# ---------------------------------------------------------------------------
# Summary counts
# ---------------------------------------------------------------------------

def query_ticket_summary(
    db: Session,
    use_reporting: bool = False,
) -> Dict[str, Any]:
    Model = _model(use_reporting)

    total = db.query(func.count(Model.ticket_id)).scalar() or 0
    open_ct = db.query(func.count(Model.ticket_id)).filter(Model.status == "Open").scalar() or 0
    in_progress = db.query(func.count(Model.ticket_id)).filter(Model.status == "In Progress").scalar() or 0
    resolved = db.query(func.count(Model.ticket_id)).filter(Model.status == "Resolved").scalar() or 0
    closed = db.query(func.count(Model.ticket_id)).filter(Model.status == "Closed").scalar() or 0

    resolution_rate = ((resolved + closed) / total) if total > 0 else 0.0

    # Average resolution time for resolved/closed tickets
    avg_days_row = (
        db.query(
            func.avg(
                func.extract("epoch", Model.updated_at - Model.created_at) / 86400.0
            ).label("avg_days")
        )
        .filter(Model.status.in_(["Resolved", "Closed"]))
        .one()
    )
    avg_resolution_days = float(avg_days_row.avg_days) if avg_days_row.avg_days else None

    return {
        "total_tickets": total,
        "open_tickets": open_ct,
        "in_progress_tickets": in_progress,
        "resolved_tickets": resolved,
        "closed_tickets": closed,
        "resolution_rate": round(resolution_rate, 4),
        "avg_resolution_days": round(avg_resolution_days, 2) if avg_resolution_days else None,
    }


# ---------------------------------------------------------------------------
# Category breakdown
# ---------------------------------------------------------------------------

def query_category_breakdown(
    db: Session,
    use_reporting: bool = False,
) -> Dict[str, Any]:
    Model = _model(use_reporting)

    rows = (
        db.query(
            Model.issue_category.label("category"),
            func.count(Model.ticket_id).label("count"),
        )
        .group_by(Model.issue_category)
        .order_by(func.count(Model.ticket_id).desc())
        .all()
    )

    total = sum(r.count for r in rows)
    categories = [
        {
            "category": r.category or "Unknown",
            "count": r.count,
            "percentage": round((r.count / total * 100), 2) if total else 0.0,
        }
        for r in rows
    ]
    return {"categories": categories, "total": total}


# ---------------------------------------------------------------------------
# Priority breakdown
# ---------------------------------------------------------------------------

def query_priority_breakdown(
    db: Session,
    use_reporting: bool = False,
) -> Dict[str, Any]:
    Model = _model(use_reporting)

    rows = (
        db.query(
            Model.priority.label("priority"),
            func.count(Model.ticket_id).label("count"),
        )
        .group_by(Model.priority)
        .order_by(func.count(Model.ticket_id).desc())
        .all()
    )

    priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    rows_sorted = sorted(rows, key=lambda r: priority_order.get(r.priority, 99))

    total = sum(r.count for r in rows_sorted)
    priorities = [
        {
            "priority": r.priority or "Unknown",
            "count": r.count,
            "percentage": round((r.count / total * 100), 2) if total else 0.0,
        }
        for r in rows_sorted
    ]
    return {"priorities": priorities, "total": total}


# ---------------------------------------------------------------------------
# Status breakdown
# ---------------------------------------------------------------------------

def query_status_breakdown(
    db: Session,
    use_reporting: bool = False,
) -> Dict[str, Any]:
    Model = _model(use_reporting)

    rows = (
        db.query(
            Model.status.label("status"),
            func.count(Model.ticket_id).label("count"),
        )
        .group_by(Model.status)
        .order_by(func.count(Model.ticket_id).desc())
        .all()
    )

    total = sum(r.count for r in rows)
    statuses = [
        {
            "status": r.status or "Unknown",
            "count": r.count,
            "percentage": round((r.count / total * 100), 2) if total else 0.0,
        }
        for r in rows
    ]
    return {"statuses": statuses, "total": total}


# ---------------------------------------------------------------------------
# Department breakdown
# ---------------------------------------------------------------------------

def query_department_breakdown(
    db: Session,
    use_reporting: bool = False,
) -> Dict[str, Any]:
    Model = _model(use_reporting)

    rows = (
        db.query(
            Model.department.label("department"),
            func.count(Model.ticket_id).label("total"),
            func.sum(
                case((Model.status == "Open", 1), else_=0)
            ).label("open_count"),
            func.sum(
                case((Model.status.in_(["Resolved", "Closed"]), 1), else_=0)
            ).label("resolved_count"),
        )
        .group_by(Model.department)
        .order_by(func.count(Model.ticket_id).desc())
        .all()
    )

    departments = [
        {
            "department": r.department or "Unknown",
            "total": r.total,
            "open_count": int(r.open_count or 0),
            "resolved_count": int(r.resolved_count or 0),
            "resolution_rate": round(
                int(r.resolved_count or 0) / r.total, 4
            ) if r.total else 0.0,
        }
        for r in rows
    ]
    return {"departments": departments}


# ---------------------------------------------------------------------------
# Volume trend
# ---------------------------------------------------------------------------

def query_volume_trend(
    db: Session,
    granularity: str = "monthly",
    use_reporting: bool = False,
) -> Dict[str, Any]:
    """
    Return ticket volume grouped by time period.
    granularity: 'daily' | 'weekly' | 'monthly'
    """
    Model = _model(use_reporting)

    # Map granularity to PostgreSQL date_trunc argument
    trunc_map = {"daily": "day", "weekly": "week", "monthly": "month"}
    trunc_arg = trunc_map.get(granularity, "month")

    period_col = func.date_trunc(trunc_arg, Model.created_at).label("period")

    rows = (
        db.query(
            period_col,
            func.count(Model.ticket_id).label("count"),
            func.sum(
                case((Model.status.in_(["Resolved", "Closed"]), 1), else_=0)
            ).label("resolved"),
            func.sum(
                case((Model.status == "Open", 1), else_=0)
            ).label("open"),
        )
        .group_by(period_col)
        .order_by(period_col)
        .all()
    )

    date_format = {
        "daily": "%Y-%m-%d",
        "weekly": "%Y-%m-%d",
        "monthly": "%Y-%m",
    }.get(granularity, "%Y-%m")

    data = [
        {
            "period": r.period.strftime(date_format) if r.period else "Unknown",
            "count": r.count,
            "resolved": int(r.resolved or 0),
            "open": int(r.open or 0),
        }
        for r in rows
    ]
    return {"granularity": granularity, "data": data}


# ---------------------------------------------------------------------------
# Resolution time by category
# ---------------------------------------------------------------------------

def query_resolution_time(
    db: Session,
    use_reporting: bool = False,
) -> Dict[str, Any]:
    Model = _model(use_reporting)

    rows = (
        db.query(
            Model.issue_category.label("category"),
            func.avg(
                func.extract("epoch", Model.updated_at - Model.created_at) / 86400.0
            ).label("avg_days"),
            func.min(
                func.extract("epoch", Model.updated_at - Model.created_at) / 86400.0
            ).label("min_days"),
            func.max(
                func.extract("epoch", Model.updated_at - Model.created_at) / 86400.0
            ).label("max_days"),
            func.count(Model.ticket_id).label("sample_count"),
        )
        .filter(Model.status.in_(["Resolved", "Closed"]))
        .filter(Model.updated_at.isnot(None))
        .group_by(Model.issue_category)
        .order_by(func.avg(
            func.extract("epoch", Model.updated_at - Model.created_at) / 86400.0
        ).desc())
        .all()
    )

    by_category = [
        {
            "category": r.category or "Unknown",
            "avg_days": round(float(r.avg_days or 0), 2),
            "min_days": round(float(r.min_days or 0), 2),
            "max_days": round(float(r.max_days or 0), 2),
            "sample_count": r.sample_count,
        }
        for r in rows
    ]

    overall_avg = (
        sum(r["avg_days"] * r["sample_count"] for r in by_category)
        / sum(r["sample_count"] for r in by_category)
        if by_category
        else None
    )

    return {
        "by_category": by_category,
        "overall_avg_days": round(overall_avg, 2) if overall_avg else None,
    }


# ---------------------------------------------------------------------------
# Top departments
# ---------------------------------------------------------------------------

def query_top_departments(
    db: Session,
    limit: int = 10,
    use_reporting: bool = False,
) -> Dict[str, Any]:
    Model = _model(use_reporting)

    rows = (
        db.query(
            Model.department.label("department"),
            func.count(Model.ticket_id).label("ticket_count"),
            func.sum(
                case((Model.status == "Open", 1), else_=0)
            ).label("open_count"),
            func.sum(
                case((Model.priority.in_(["High", "Critical"]), 1), else_=0)
            ).label("high_priority_count"),
        )
        .group_by(Model.department)
        .order_by(func.count(Model.ticket_id).desc())
        .limit(limit)
        .all()
    )

    departments = [
        {
            "department": r.department or "Unknown",
            "ticket_count": r.ticket_count,
            "open_count": int(r.open_count or 0),
            "high_priority_count": int(r.high_priority_count or 0),
        }
        for r in rows
    ]
    return {"departments": departments}
