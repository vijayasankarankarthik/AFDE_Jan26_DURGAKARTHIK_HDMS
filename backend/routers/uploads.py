"""
routers/uploads.py — File upload endpoint for the CSV ETL pipeline.

POST /api/upload/tickets-csv
  Accepts a multipart CSV file, runs the full ETL pipeline, and returns
  a summary of the ingestion job.

Security:
  - MIME type checked in validators.validate_mime_type
  - File size limited to 50 MB in csv_loader.load_csv_from_bytes
  - File stored only in-memory (bytes) — never written to disk
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from database import get_db
from etl.loaders import run_etl_pipeline
from etl.validators import validate_mime_type
from analytics.schemas import ETLJobResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/upload",
    tags=["uploads"],
)


@router.post(
    "/tickets-csv",
    response_model=ETLJobResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a CSV file to import historical tickets",
    description=(
        "Accepts a CSV file and runs the full ETL pipeline:\n\n"
        "1. Validate file size (≤ 50 MB) and MIME type\n"
        "2. Detect encoding (UTF-8 / latin-1)\n"
        "3. Validate required columns\n"
        "4. Normalise text, priority, status, category values\n"
        "5. Parse and validate timestamps\n"
        "6. Deduplicate rows\n"
        "7. Bulk-insert into `reporting_tickets`\n\n"
        "Returns the ETL job record with row counts and status."
    ),
)
async def upload_tickets_csv(
    file: UploadFile = File(..., description="CSV file with ticket data"),
    db: Session = Depends(get_db),
):
    # Content-type guard (non-blocking — browsers send inconsistent MIME types
    # for plain CSV, so we warn but don't reject here; the parser will fail fast
    # if the content is genuinely not CSV-shaped)
    content_type = file.content_type or "application/octet-stream"
    try:
        validate_mime_type(content_type)
    except ValueError as exc:
        logger.warning(
            "Unexpected content-type '%s' for file '%s': %s",
            content_type, file.filename, exc,
        )
        # Allow through — validate_mime_type is advisory for uploads from
        # some OS/browser combinations that mis-label CSV files.

    # Read entire file into memory
    try:
        file_bytes: bytes = await file.read()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not read uploaded file: {exc}",
        ) from exc

    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    filename = file.filename or "upload.csv"

    logger.info(
        "Received CSV upload: '%s' (%d bytes, content-type=%s).",
        filename, len(file_bytes), content_type,
    )

    # Run the ETL pipeline — it handles its own exception capture and marks
    # the job as 'failed' internally; it will not raise.
    job = run_etl_pipeline(db, file_bytes, filename)

    if job.status == "failed":
        # Return 422 so the frontend can display the error_message field
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "ETL pipeline failed — see 'error_message' for details.",
                "error_message": job.error_message,
                "job_id": job.job_id,
            },
        )

    return ETLJobResponse.model_validate(job)
