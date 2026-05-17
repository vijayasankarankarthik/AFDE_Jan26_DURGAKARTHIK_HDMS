"""
routers/tickets.py — REST API route handlers for ticket resources.

HTTP concerns only: request parsing, delegation to service layer, response codes.
Business logic lives exclusively in services/ticket_service.py.

Endpoints:
  GET    /api/tickets/stats        — Dashboard aggregate statistics
  GET    /api/tickets/search       — Search & filter tickets
  GET    /api/tickets              — List all tickets (paginated)
  GET    /api/tickets/{id}         — Get single ticket by ID
  POST   /api/tickets              — Create a new ticket
  PUT    /api/tickets/{id}         — Update an existing ticket
  DELETE /api/tickets/{id}         — Delete a ticket
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from database import get_db
from schemas import (
    MessageResponse,
    TicketCreate,
    TicketListResponse,
    TicketResponse,
    TicketStatsResponse,
    TicketUpdate,
)
from services.ticket_service import TicketService

router = APIRouter()


# ─── Helper: service factory ───────────────────────────────────────────────────

def get_service(db: Session = Depends(get_db)) -> TicketService:
    """Dependency that injects a TicketService instance per request."""
    return TicketService(db)


# ─── Statistics ────────────────────────────────────────────────────────────────

@router.get(
    "/tickets/stats",
    response_model=TicketStatsResponse,
    summary="Get dashboard statistics",
    description="Returns aggregated ticket counts by status and priority for the dashboard.",
)
def get_stats(service: TicketService = Depends(get_service)):
    return service.get_stats()


# ─── Search ────────────────────────────────────────────────────────────────────

@router.get(
    "/tickets/search",
    response_model=TicketListResponse,
    summary="Search and filter tickets",
    description=(
        "Search tickets by keyword across employee name, description, department, "
        "and category. Combine with status, priority, and category filters."
    ),
)
def search_tickets(
    q: Optional[str] = Query(None, description="Keyword to search across ticket fields"),
    status: Optional[str] = Query(None, description="Filter by status (Open, In Progress, Resolved, Closed)"),
    priority: Optional[str] = Query(None, description="Filter by priority (Low, Medium, High, Critical)"),
    category: Optional[str] = Query(None, description="Filter by issue category"),
    department: Optional[str] = Query(None, description="Filter by department (partial match)"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page"),
    service: TicketService = Depends(get_service),
):
    return service.search_tickets(
        q=q,
        status=status,
        priority=priority,
        category=category,
        department=department,
        page=page,
        page_size=page_size,
    )


# ─── List ──────────────────────────────────────────────────────────────────────

@router.get(
    "/tickets",
    response_model=TicketListResponse,
    summary="List all tickets",
    description="Retrieve all tickets with pagination. Results are ordered newest first.",
)
def list_tickets(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(20, ge=1, le=100, description="Number of tickets per page"),
    service: TicketService = Depends(get_service),
):
    return service.list_tickets(page=page, page_size=page_size)


# ─── Get by ID ─────────────────────────────────────────────────────────────────

@router.get(
    "/tickets/{ticket_id}",
    response_model=TicketResponse,
    summary="Get a ticket by ID",
    description="Retrieve a single ticket's complete details by its unique ID.",
)
def get_ticket(
    ticket_id: int,
    service: TicketService = Depends(get_service),
):
    return service.get_ticket(ticket_id)


# ─── Create ────────────────────────────────────────────────────────────────────

@router.post(
    "/tickets",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new ticket",
    description="Submit a new support ticket. The ticket status defaults to 'Open'.",
)
def create_ticket(
    payload: TicketCreate,
    service: TicketService = Depends(get_service),
):
    return service.create_ticket(payload)


# ─── Update ────────────────────────────────────────────────────────────────────

@router.put(
    "/tickets/{ticket_id}",
    response_model=TicketResponse,
    summary="Update a ticket",
    description=(
        "Partially update an existing ticket. Only provided fields are changed. "
        "Support admins can update status, priority, resolution notes, and more."
    ),
)
def update_ticket(
    ticket_id: int,
    payload: TicketUpdate,
    service: TicketService = Depends(get_service),
):
    return service.update_ticket(ticket_id, payload)


# ─── Delete ────────────────────────────────────────────────────────────────────

@router.delete(
    "/tickets/{ticket_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete a ticket",
    description="Permanently delete a ticket by ID. This action is irreversible.",
)
def delete_ticket(
    ticket_id: int,
    service: TicketService = Depends(get_service),
):
    return service.delete_ticket(ticket_id)
