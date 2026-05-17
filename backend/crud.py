"""
crud.py — Database CRUD operations (Create, Read, Update, Delete).

All functions receive a SQLAlchemy Session and return ORM model instances.
Search logic uses ILIKE for case-insensitive PostgreSQL full-text matching.
Pagination is handled via skip/limit pattern compatible with offset-based paging.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Tuple

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from models import Ticket
from schemas import TicketCreate, TicketUpdate

logger = logging.getLogger(__name__)


# ─── Create ────────────────────────────────────────────────────────────────────

def create_ticket(db: Session, payload: TicketCreate) -> Ticket:
    """Insert a new ticket row and return the persisted ORM object."""
    ticket = Ticket(
        employee_name=payload.employee_name,
        department=payload.department,
        issue_category=payload.issue_category.value,
        description=payload.description,
        priority=payload.priority.value,
        status="Open",
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    logger.info("Created ticket #%s for employee: %s", ticket.ticket_id, ticket.employee_name)
    return ticket


# ─── Read ──────────────────────────────────────────────────────────────────────

def get_ticket(db: Session, ticket_id: int) -> Optional[Ticket]:
    """Fetch a single ticket by primary key. Returns None if not found."""
    return db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()


def get_tickets(
    db: Session,
    skip: int = 0,
    limit: int = 20,
) -> Tuple[List[Ticket], int]:
    """Return a paginated list of all tickets (newest first) and the total count."""
    query = db.query(Ticket).order_by(Ticket.created_at.desc())
    total = query.count()
    tickets = query.offset(skip).limit(limit).all()
    return tickets, total


def search_tickets(
    db: Session,
    q: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    department: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
) -> Tuple[List[Ticket], int]:
    """
    Search tickets with optional keyword (q) and exact-match filters.

    Keyword search (q) performs ILIKE matching across:
      - employee_name, description, department, issue_category

    Filters (status, priority, category, department) apply as AND conditions.
    Results are ordered newest first.
    """
    query = db.query(Ticket)

    if q:
        pattern = f"%{q}%"
        query = query.filter(
            or_(
                Ticket.employee_name.ilike(pattern),
                Ticket.description.ilike(pattern),
                Ticket.department.ilike(pattern),
                Ticket.issue_category.ilike(pattern),
            )
        )

    if status:
        query = query.filter(Ticket.status == status)

    if priority:
        query = query.filter(Ticket.priority == priority)

    if category:
        query = query.filter(Ticket.issue_category == category)

    if department:
        query = query.filter(Ticket.department.ilike(f"%{department}%"))

    query = query.order_by(Ticket.created_at.desc())
    total = query.count()
    tickets = query.offset(skip).limit(limit).all()
    return tickets, total


def get_ticket_stats(db: Session) -> Dict[str, int]:
    """
    Aggregate ticket counts for dashboard statistics.
    Uses individual COUNT queries for clarity and maintainability.
    """
    def count_filter(**kwargs) -> int:
        q = db.query(func.count(Ticket.ticket_id))
        for column, value in kwargs.items():
            q = q.filter(getattr(Ticket, column) == value)
        return q.scalar() or 0

    return {
        "total_tickets": db.query(func.count(Ticket.ticket_id)).scalar() or 0,
        "open_tickets": count_filter(status="Open"),
        "in_progress_tickets": count_filter(status="In Progress"),
        "resolved_tickets": count_filter(status="Resolved"),
        "closed_tickets": count_filter(status="Closed"),
        "critical_tickets": count_filter(priority="Critical"),
        "high_priority_tickets": count_filter(priority="High"),
    }


# ─── Update ────────────────────────────────────────────────────────────────────

def update_ticket(db: Session, ticket_id: int, payload: TicketUpdate) -> Optional[Ticket]:
    """
    Apply partial updates to a ticket.
    Only fields explicitly set in the payload are updated (PATCH semantics).
    Returns the updated ORM object, or None if the ticket was not found.
    """
    ticket = get_ticket(db, ticket_id)
    if not ticket:
        return None

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            # Unwrap enum values to their string representation
            setattr(ticket, field, value.value if hasattr(value, "value") else value)

    db.commit()
    db.refresh(ticket)
    logger.info("Updated ticket #%s — modified fields: %s", ticket_id, list(update_data.keys()))
    return ticket


# ─── Delete ────────────────────────────────────────────────────────────────────

def delete_ticket(db: Session, ticket_id: int) -> bool:
    """
    Delete a ticket by ID.
    Returns True if the ticket was found and deleted, False otherwise.
    """
    ticket = get_ticket(db, ticket_id)
    if not ticket:
        return False

    db.delete(ticket)
    db.commit()
    logger.info("Deleted ticket #%s", ticket_id)
    return True
