"""
schemas.py — Pydantic v2 models for request validation and response serialization.

Enums enforce valid values at the API boundary.
Validators ensure data integrity before it reaches the database.
Response models use from_attributes=True for SQLAlchemy ORM compatibility.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


# ─── Enumerations ──────────────────────────────────────────────────────────────

class PriorityEnum(str, Enum):
    low = "Low"
    medium = "Medium"
    high = "High"
    critical = "Critical"


class StatusEnum(str, Enum):
    open = "Open"
    in_progress = "In Progress"
    resolved = "Resolved"
    closed = "Closed"


class CategoryEnum(str, Enum):
    vpn_issue = "VPN Issue"
    password_reset = "Password Reset"
    software_installation = "Software Installation"
    laptop_issue = "Laptop Issue"
    email_access = "Email Access"
    network_connectivity = "Network Connectivity"
    hardware_request = "Hardware Request"
    other = "Other"


# ─── Request Schemas ───────────────────────────────────────────────────────────

class TicketCreate(BaseModel):
    """Payload for creating a new support ticket."""

    employee_name: str = Field(
        ...,
        min_length=2,
        max_length=150,
        description="Full name of the employee submitting the ticket",
        examples=["Jane Doe"],
    )
    department: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Department where the employee works",
        examples=["Engineering"],
    )
    issue_category: CategoryEnum = Field(
        ...,
        description="Category that best describes the issue",
        examples=["VPN Issue"],
    )
    description: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Detailed description of the problem",
    )
    priority: PriorityEnum = Field(
        default=PriorityEnum.medium,
        description="Urgency level of the ticket",
    )

    @field_validator("employee_name", "department")
    @classmethod
    def strip_and_validate(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank.")
        return value

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 10:
            raise ValueError("Description must be at least 10 characters long.")
        return value


class TicketUpdate(BaseModel):
    """Payload for partially updating an existing ticket (all fields optional)."""

    employee_name: Optional[str] = Field(None, min_length=2, max_length=150)
    department: Optional[str] = Field(None, min_length=2, max_length=100)
    issue_category: Optional[CategoryEnum] = None
    description: Optional[str] = Field(None, min_length=10, max_length=5000)
    priority: Optional[PriorityEnum] = None
    status: Optional[StatusEnum] = None
    resolution_notes: Optional[str] = Field(None, max_length=5000)

    @field_validator("employee_name", "department", mode="before")
    @classmethod
    def strip_optional_strings(cls, value):
        if isinstance(value, str):
            stripped = value.strip()
            return stripped if stripped else None
        return value

    @field_validator("description", mode="before")
    @classmethod
    def strip_description(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value


# ─── Response Schemas ──────────────────────────────────────────────────────────

class TicketResponse(BaseModel):
    """Full ticket object returned by the API."""

    ticket_id: int
    employee_name: str
    department: str
    issue_category: str
    description: str
    priority: str
    status: str
    resolution_notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TicketListResponse(BaseModel):
    """Paginated list of tickets with metadata."""

    total: int
    page: int
    page_size: int
    tickets: List[TicketResponse]


class TicketStatsResponse(BaseModel):
    """Aggregated statistics for the dashboard."""

    total_tickets: int
    open_tickets: int
    in_progress_tickets: int
    resolved_tickets: int
    closed_tickets: int
    critical_tickets: int
    high_priority_tickets: int


class MessageResponse(BaseModel):
    """Generic message response for operations like delete."""

    message: str
    ticket_id: Optional[int] = None
