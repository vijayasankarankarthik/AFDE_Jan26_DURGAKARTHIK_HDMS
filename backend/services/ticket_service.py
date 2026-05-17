"""
services/ticket_service.py — Business logic layer for ticket operations.

This service acts as the single source of truth for all ticket-related
workflows. It:
  - Wraps CRUD functions
  - Enforces business rules (e.g. valid status transitions)
  - Builds paginated response envelopes
  - Raises HTTP-aware exceptions for the router layer
  - Is easily unit-testable by injecting a mock DB session
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

import crud
from schemas import (
    MessageResponse,
    TicketCreate,
    TicketListResponse,
    TicketResponse,
    TicketStatsResponse,
    TicketUpdate,
)
from utils.validators import validate_status_transition

logger = logging.getLogger(__name__)

# ─── Valid status transition map ──────────────────────────────────────────────
# Describes which statuses a ticket may transition FROM → TO.
VALID_TRANSITIONS: dict[str, list[str]] = {
    "Open": ["In Progress", "Closed"],
    "In Progress": ["Resolved", "Open", "Closed"],
    "Resolved": ["Closed", "Open"],
    "Closed": [],  # Terminal state — requires admin override (future feature)
}


class TicketService:
    """
    Encapsulates all business logic for the ticket domain.
    Instantiated per request via FastAPI dependency injection.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    # ─── Stats ─────────────────────────────────────────────────────────────────

    def get_stats(self) -> TicketStatsResponse:
        """Return aggregated ticket statistics for the dashboard."""
        stats = crud.get_ticket_stats(self.db)
        return TicketStatsResponse(**stats)

    # ─── List ──────────────────────────────────────────────────────────────────

    def list_tickets(self, page: int, page_size: int) -> TicketListResponse:
        """Return a paginated list of all tickets."""
        skip = (page - 1) * page_size
        tickets, total = crud.get_tickets(self.db, skip=skip, limit=page_size)
        return TicketListResponse(
            total=total,
            page=page,
            page_size=page_size,
            tickets=[TicketResponse.model_validate(t) for t in tickets],
        )

    # ─── Search ────────────────────────────────────────────────────────────────

    def search_tickets(
        self,
        q: Optional[str],
        status: Optional[str],
        priority: Optional[str],
        category: Optional[str],
        department: Optional[str],
        page: int,
        page_size: int,
    ) -> TicketListResponse:
        """Search and filter tickets, returning a paginated response."""
        skip = (page - 1) * page_size
        tickets, total = crud.search_tickets(
            self.db,
            q=q,
            status=status,
            priority=priority,
            category=category,
            department=department,
            skip=skip,
            limit=page_size,
        )
        return TicketListResponse(
            total=total,
            page=page,
            page_size=page_size,
            tickets=[TicketResponse.model_validate(t) for t in tickets],
        )

    # ─── Get ───────────────────────────────────────────────────────────────────

    def get_ticket(self, ticket_id: int) -> TicketResponse:
        """Retrieve a single ticket by ID or raise 404."""
        ticket = crud.get_ticket(self.db, ticket_id)
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticket #{ticket_id} was not found.",
            )
        return TicketResponse.model_validate(ticket)

    # ─── Create ────────────────────────────────────────────────────────────────

    def create_ticket(self, payload: TicketCreate) -> TicketResponse:
        """Create a new ticket. All new tickets start with status 'Open'."""
        ticket = crud.create_ticket(self.db, payload)
        logger.info(
            "Ticket #%s created — employee: %s, category: %s, priority: %s",
            ticket.ticket_id,
            ticket.employee_name,
            ticket.issue_category,
            ticket.priority,
        )
        return TicketResponse.model_validate(ticket)

    # ─── Update ────────────────────────────────────────────────────────────────

    def update_ticket(self, ticket_id: int, payload: TicketUpdate) -> TicketResponse:
        """
        Update a ticket with optional status transition validation.
        Raises 404 if the ticket does not exist.
        Raises 422 if the status transition is not permitted.
        """
        existing = crud.get_ticket(self.db, ticket_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticket #{ticket_id} was not found.",
            )

        # Validate status transition if a new status is provided
        if payload.status is not None:
            new_status = payload.status.value
            validate_status_transition(
                current_status=existing.status,
                new_status=new_status,
                valid_transitions=VALID_TRANSITIONS,
            )

        ticket = crud.update_ticket(self.db, ticket_id, payload)
        return TicketResponse.model_validate(ticket)

    # ─── Delete ────────────────────────────────────────────────────────────────

    def delete_ticket(self, ticket_id: int) -> MessageResponse:
        """Delete a ticket by ID. Raises 404 if not found."""
        deleted = crud.delete_ticket(self.db, ticket_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticket #{ticket_id} was not found.",
            )
        return MessageResponse(
            message=f"Ticket #{ticket_id} has been permanently deleted.",
            ticket_id=ticket_id,
        )
