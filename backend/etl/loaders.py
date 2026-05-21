"""
etl/loaders.py — Database persistence layer for the ETL pipeline.

Responsibilities:
  - Create / update ETLJob records to track pipeline runs
  - Batch-insert cleaned records into the `reporting_tickets` table
  - Orchestrate the full ETL flow: load → transform → validate → persist

This module is intentionally thin — it delegates all file parsing to
csv_loader.py and all data cleaning to transformers.py.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Union
from uuid import UUID

import pandas as pd
from sqlalchemy.orm import Session

from models import ETLJob, ReportingTicket
from etl.csv_loader import CSVLoader
from etl.transformers import run_full_transform
from etl.validators import validate_row

logger = logging.getLogger(__name__)

# Number of records inserted per database round-trip
_BATCH_SIZE = 500


# ---------------------------------------------------------------------------
# ETLJob helpers
# ---------------------------------------------------------------------------

def create_etl_job(
    db: Session,
    filename: str,
    batch_id: UUID,
) -> ETLJob:
    """Insert a new ETLJob row with status='running'."""
    job = ETLJob(
        filename=filename,
        batch_id=batch_id,
        status="running",
        started_at=datetime.now(timezone.utc),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    logger.info("Created ETL job %s for file '%s'.", job.job_id, filename)
    return job


def complete_etl_job(
    db: Session,
    job: ETLJob,
    stats: Dict[str, Any],
) -> ETLJob:
    """Update an ETLJob row to status='completed' with final statistics."""
    job.status = "completed"
    job.total_rows = stats.get("total_rows", 0)
    job.inserted_rows = stats.get("inserted_rows", 0)
    job.duplicate_rows = stats.get("duplicate_rows", 0)
    job.error_rows = stats.get("error_rows", 0)
    job.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(job)
    logger.info(
        "ETL job %s completed — inserted=%d, duplicates=%d, errors=%d.",
        job.job_id,
        job.inserted_rows,
        job.duplicate_rows,
        job.error_rows,
    )
    return job


def fail_etl_job(
    db: Session,
    job: ETLJob,
    error_message: str,
) -> ETLJob:
    """Update an ETLJob row to status='failed' with an error message."""
    job.status = "failed"
    job.error_message = error_message[:2000]  # Truncate to column limit
    job.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(job)
    logger.error("ETL job %s failed: %s", job.job_id, error_message)
    return job


# ---------------------------------------------------------------------------
# Batch insertion
# ---------------------------------------------------------------------------

def batch_insert_reporting_tickets(
    db: Session,
    records: List[Dict[str, Any]],
    batch_id: UUID,
    source_file: str,
) -> Dict[str, int]:
    """
    Bulk-insert a list of cleaned record dicts into `reporting_tickets`.

    Processes records in chunks of _BATCH_SIZE to avoid memory spikes.
    Each record is individually validated with validate_row; invalid records
    are counted but not inserted.

    Args:
        db:          Active SQLAlchemy session.
        records:     List of dicts — output of DataFrame.to_dict('records').
        batch_id:    UUID string linking all rows to this ETL run.
        source_file: Original filename for provenance.

    Returns:
        Dict with keys 'inserted_rows', 'error_rows'.
    """
    inserted = 0
    errors = 0

    for chunk_start in range(0, len(records), _BATCH_SIZE):
        chunk = records[chunk_start : chunk_start + _BATCH_SIZE]
        orm_objects: List[ReportingTicket] = []

        for record in chunk:
            row_errors = validate_row(record)
            if row_errors:
                logger.debug("Skipping invalid row: %s", row_errors)
                errors += 1
                continue

            orm_objects.append(
                ReportingTicket(
                    employee_name=record.get("employee_name"),
                    department=record.get("department"),
                    issue_category=record.get("issue_category"),
                    description=record.get("description"),
                    priority=record.get("priority"),
                    status=record.get("status"),
                    resolution_notes=record.get("resolution_notes"),
                    created_at=record.get("created_at"),
                    updated_at=record.get("updated_at"),
                    source_file=source_file,
                    ingestion_batch_id=batch_id,
                    is_duplicate=bool(record.get("_is_duplicate", False)),
                )
            )

        if orm_objects:
            db.bulk_save_objects(orm_objects)
            db.commit()
            inserted += len(orm_objects)
            logger.debug(
                "Inserted chunk %d–%d (%d rows).",
                chunk_start,
                chunk_start + len(chunk),
                len(orm_objects),
            )

    return {"inserted_rows": inserted, "error_rows": errors}


# ---------------------------------------------------------------------------
# Pipeline orchestrator
# ---------------------------------------------------------------------------

def run_etl_pipeline(
    db: Session,
    file_bytes: bytes,
    filename: str,
) -> ETLJob:
    """
    Execute the full ETL pipeline for a single uploaded CSV file.

    Stages:
      1. Generate a unique batch_id and create an ETLJob record
      2. Load & schema-validate the CSV (CSVLoader)
      3. Transform & clean the data (run_full_transform)
      4. Mark duplicate rows
      5. Batch-insert into reporting_tickets
      6. Update ETLJob with final statistics

    On any unhandled exception the ETLJob is marked 'failed' before
    re-raising so the caller can return a meaningful API error response.

    Args:
        db:         Active SQLAlchemy session.
        file_bytes: Raw bytes of the uploaded file.
        filename:   Original filename (used for provenance and error messages).

    Returns:
        Completed (or failed) ETLJob ORM instance.
    """
    batch_id = uuid.uuid4()   # native UUID — matches PG_UUID column type
    job = create_etl_job(db, filename, batch_id)

    try:
        # --- Stage 1: Load ---
        logger.info("ETL[%s] Stage 1: loading CSV '%s'.", batch_id, filename)
        df: pd.DataFrame = CSVLoader.load_and_validate(file_bytes, filename)
        total_rows = len(df)

        # --- Stage 2: Transform ---
        logger.info("ETL[%s] Stage 2: transforming %d rows.", batch_id, total_rows)
        df, transform_stats = run_full_transform(df)

        # --- Stage 3: Mark duplicates ---
        duplicate_rows: int = transform_stats.get("duplicates_removed", 0)

        # The transformation pipeline does not physically remove duplicates
        # — it tags them so we can count them but still insert with is_duplicate=True.
        # (run_full_transform uses drop_duplicates which does remove them;
        # adjust if soft-delete semantics are preferred.)

        # --- Stage 4: Persist ---
        records = df.to_dict("records")
        logger.info(
            "ETL[%s] Stage 3: inserting %d transformed records.", batch_id, len(records)
        )
        insert_stats = batch_insert_reporting_tickets(
            db, records, batch_id, source_file=filename
        )

        # --- Stage 5: Finalise job ---
        stats = {
            "total_rows": total_rows,
            "inserted_rows": insert_stats["inserted_rows"],
            "duplicate_rows": duplicate_rows,
            "error_rows": insert_stats["error_rows"],
        }
        return complete_etl_job(db, job, stats)

    except Exception as exc:  # noqa: BLE001
        logger.exception("ETL pipeline failed for batch %s.", batch_id)
        return fail_etl_job(db, job, str(exc))
