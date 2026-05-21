"""
models.py — SQLAlchemy ORM models for the Helpdesk system.

All column types and constraints are PostgreSQL-native.
The schema is designed with indexing for common query patterns and
is structured to support future AI vector-embedding columns (Phase 2).
"""

from __future__ import annotations

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func
import uuid

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


# ══════════════════════════════════════════════════════════════════════════════
# Phase 2 — Reporting & ETL Models
# These tables are ANALYTICS-ONLY. They are never written by Phase 1 CRUD ops.
# ══════════════════════════════════════════════════════════════════════════════

class ReportingTicket(Base):
    """
    Analytics-optimised copy of historical ticket data loaded via the ETL pipeline.

    Intentionally denormalised for fast aggregation queries.
    Phase 3 hook: add `embedding Vector(1536)` column via Alembic for RAG search.
    """

    __tablename__ = "reporting_tickets"

    ticket_id = Column(Integer, primary_key=True, autoincrement=True)

    # ─── Core ticket fields (mirrors Ticket) ──────────────────────────────────
    employee_name  = Column(String(150), nullable=False, index=True)
    department     = Column(String(100), nullable=False, index=True)
    issue_category = Column(String(100), nullable=False, index=True)
    description    = Column(Text,        nullable=False)
    priority       = Column(String(20),  nullable=False, index=True)
    status         = Column(String(30),  nullable=False, index=True)
    resolution_notes = Column(Text, nullable=True)

    # ─── Timestamps ───────────────────────────────────────────────────────────
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Original ticket creation time from source system",
    )
    updated_at = Column(DateTime(timezone=True), nullable=True)

    # ─── ETL provenance columns ───────────────────────────────────────────────
    source_file       = Column(String(255), nullable=False,
                               comment="Name of the CSV file this row was ingested from")
    ingestion_batch_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True,
                                comment="UUID of the ETL job that produced this row")
    is_duplicate      = Column(
        Integer,  # 0 = clean row, stored as int for portable DB support
        nullable=False,
        default=0,
        comment="1 if row was flagged as duplicate during ETL (kept for audit)",
    )

    def __repr__(self) -> str:
        return (
            f"<ReportingTicket(id={self.ticket_id}, batch='{self.ingestion_batch_id}', "
            f"category='{self.issue_category}', status='{self.status}')>"
        )


class ETLJob(Base):
    """
    Audit log for every CSV import operation.

    Provides full observability into the ETL pipeline:
    who uploaded, what file, how many rows processed, success/failure.
    """

    __tablename__ = "etl_jobs"

    job_id   = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False,
                      comment="Original filename of the uploaded CSV")
    batch_id = Column(PG_UUID(as_uuid=True), nullable=False, unique=True,
                      comment="UUID v4 identifying this ETL run")

    # ─── Row counts ───────────────────────────────────────────────────────────
    total_rows     = Column(Integer, nullable=False, default=0)
    inserted_rows  = Column(Integer, nullable=False, default=0)
    duplicate_rows = Column(Integer, nullable=False, default=0)
    error_rows     = Column(Integer, nullable=False, default=0)

    # ─── Job lifecycle ────────────────────────────────────────────────────────
    status        = Column(String(30), nullable=False, default="running",
                           comment="running | completed | failed")
    error_message = Column(Text, nullable=True)
    started_at    = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    completed_at  = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return (
            f"<ETLJob(id={self.job_id}, file='{self.filename}', "
            f"status='{self.status}', inserted={self.inserted_rows})>"
        )
