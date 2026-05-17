"""
models.py — SQLAlchemy ORM models for the Helpdesk system.

All column types and constraints are PostgreSQL-native.
The schema is designed with indexing for common query patterns and
is structured to support future AI vector-embedding columns (Phase 2).
"""

from __future__ import annotations

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from database import Base


class Ticket(Base):
    """
    Represents a single helpdesk support ticket submitted by an employee.

    PostgreSQL-compatible schema with:
      - Indexed columns for efficient filtering (status, priority, category, department)
      - Timezone-aware timestamps managed by the DB server
      - Nullable resolution_notes to support open/in-progress tickets
      - Prepared for Phase 2: vector_embedding column can be added via Alembic migration
    """

    __tablename__ = "tickets"

    # ─── Primary Key ──────────────────────────────────────────────
    ticket_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="Unique auto-incrementing ticket identifier",
    )

    # ─── Employee information ─────────────────────────────────────
    employee_name = Column(
        String(150),
        nullable=False,
        index=True,
        comment="Full name of the employee who submitted the ticket",
    )
    department = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Department to which the employee belongs",
    )

    # ─── Issue details ────────────────────────────────────────────
    issue_category = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Category of the reported issue (IT, HR, Finance, etc.)",
    )
    description = Column(
        Text,
        nullable=False,
        comment="Full description of the problem reported by the employee",
    )

    # ─── Priority & Status ────────────────────────────────────────
    priority = Column(
        String(20),
        nullable=False,
        default="Medium",
        index=True,
        comment="Ticket priority: Low | Medium | High | Critical",
    )
    status = Column(
        String(30),
        nullable=False,
        default="Open",
        index=True,
        comment="Ticket lifecycle status: Open | In Progress | Resolved | Closed",
    )

    # ─── Resolution ───────────────────────────────────────────────
    resolution_notes = Column(
        Text,
        nullable=True,
        comment="Support agent notes on how the issue was resolved",
    )

    # ─── Timestamps ───────────────────────────────────────────────
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="UTC timestamp when the ticket was first created",
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="UTC timestamp of the most recent update",
    )

    # ─── Phase 2 placeholder ──────────────────────────────────────
    # When AI/RAG integration is added, uncomment and run Alembic migration:
    # from pgvector.sqlalchemy import Vector
    # embedding = Column(Vector(1536), nullable=True,
    #                    comment="OpenAI text-embedding-ada-002 vector for RAG")

    def __repr__(self) -> str:
        return (
            f"<Ticket(id={self.ticket_id}, employee='{self.employee_name}', "
            f"status='{self.status}', priority='{self.priority}')>"
        )
