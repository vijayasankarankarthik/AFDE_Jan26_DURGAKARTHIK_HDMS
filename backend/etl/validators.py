"""
etl/validators.py — Pure, stateless validation functions for the ETL pipeline.

No database dependency. All functions are easily unit-testable.
Row-level validation catches bad data before it reaches the DB.

Edge cases handled:
  - Completely empty rows
  - Whitespace-only strings
  - Out-of-range enum values (with alias normalisation done upstream)
  - Unparseable timestamps in any of 8 common formats
  - Numeric values accidentally placed in string fields
  - NaN / None values in required fields
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd

# ─── Controlled vocabulary constants ──────────────────────────────────────────
# These mirror the enums in schemas.py to keep a single source of truth.

VALID_PRIORITIES: set[str] = {"Low", "Medium", "High", "Critical"}

VALID_STATUSES: set[str] = {"Open", "In Progress", "Resolved", "Closed"}

VALID_CATEGORIES: set[str] = {
    "VPN Issue",
    "Password Reset",
    "Software Installation",
    "Laptop Issue",
    "Email Access",
    "Network Connectivity",
    "Hardware Request",
    "Other",
}

# Minimum columns that MUST be present in the uploaded CSV
REQUIRED_COLUMNS: set[str] = {
    "employee_name",
    "department",
    "issue_category",
    "description",
    "priority",
    "status",
    "created_at",
}

# Timestamp formats accepted during parsing (tried in order)
ACCEPTED_DATETIME_FORMATS: list[str] = [
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%dT%H:%M:%S%z",
    "%Y-%m-%d",
    "%d/%m/%Y %H:%M:%S",
    "%d/%m/%Y",
    "%m/%d/%Y",
]


# ─── Schema-level validation ──────────────────────────────────────────────────

def validate_csv_schema(df: pd.DataFrame) -> None:
    """
    Validate that the DataFrame contains all required column headers.

    Raises:
        ValueError: with a descriptive message listing every missing column.
    """
    actual_cols = {c.strip().lower() for c in df.columns}
    required_lower = {c.lower() for c in REQUIRED_COLUMNS}
    missing = required_lower - actual_cols
    if missing:
        raise ValueError(
            f"CSV is missing required columns: {sorted(missing)}. "
            f"Found columns: {sorted(df.columns.tolist())}"
        )


# ─── Row-level validation ─────────────────────────────────────────────────────

def _is_blank(value: Any) -> bool:
    """Return True if value is None, NaN, or a whitespace-only string."""
    if value is None:
        return True
    if isinstance(value, float) and pd.isna(value):
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False


def _is_parseable_datetime(value: Any) -> bool:
    """Return True if value can be parsed as a datetime."""
    if _is_blank(value):
        return False
    if isinstance(value, (datetime, pd.Timestamp)):
        return True
    for fmt in ACCEPTED_DATETIME_FORMATS:
        try:
            datetime.strptime(str(value).strip(), fmt)
            return True
        except ValueError:
            continue
    # Final fallback: pandas generic parser
    try:
        pd.to_datetime(str(value), utc=False)
        return True
    except Exception:
        return False


def validate_row(row: Dict[str, Any]) -> List[str]:
    """
    Validate a single CSV row (as a dict of {column: value}).

    Returns:
        List of human-readable error strings. Empty list = row is valid.

    Edge cases:
        - NaN floats from pandas (empty CSV cells) treated as blank
        - Numeric employee_name/department accepted if non-blank (data entry error
          but not a pipeline-blocker — transformers will stringify)
        - Timestamps validated after normalisation so aliases are pre-resolved
    """
    errors: List[str] = []

    # Required string fields
    for field in ("employee_name", "department", "description"):
        if _is_blank(row.get(field)):
            errors.append(f"'{field}' is required and cannot be blank.")
        elif isinstance(row.get(field), str) and len(row[field].strip()) < 2:
            errors.append(f"'{field}' is too short (minimum 2 characters).")

    # issue_category — must be in controlled vocabulary AFTER normalisation
    category = row.get("issue_category")
    if _is_blank(category):
        errors.append("'issue_category' is required.")
    elif str(category).strip() not in VALID_CATEGORIES:
        errors.append(
            f"'issue_category' value '{category}' is not valid. "
            f"Accepted: {sorted(VALID_CATEGORIES)}"
        )

    # priority
    priority = row.get("priority")
    if _is_blank(priority):
        errors.append("'priority' is required.")
    elif str(priority).strip() not in VALID_PRIORITIES:
        errors.append(
            f"'priority' value '{priority}' is not valid. "
            f"Accepted: {sorted(VALID_PRIORITIES)}"
        )

    # status
    status = row.get("status")
    if _is_blank(status):
        errors.append("'status' is required.")
    elif str(status).strip() not in VALID_STATUSES:
        errors.append(
            f"'status' value '{status}' is not valid. "
            f"Accepted: {sorted(VALID_STATUSES)}"
        )

    # created_at
    created_at = row.get("created_at")
    if _is_blank(created_at):
        errors.append("'created_at' is required.")
    elif not _is_parseable_datetime(created_at):
        errors.append(
            f"'created_at' value '{created_at}' is not a recognisable datetime. "
            f"Expected formats: YYYY-MM-DD or YYYY-MM-DD HH:MM:SS"
        )

    return errors


def validate_file_size(file_bytes: bytes, max_mb: int = 50) -> None:
    """
    Reject files larger than max_mb megabytes.

    Raises:
        ValueError if size exceeded.
    """
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > max_mb:
        raise ValueError(
            f"File size {size_mb:.1f} MB exceeds the {max_mb} MB limit."
        )


def validate_mime_type(content_type: str) -> None:
    """
    Accept only CSV-compatible MIME types.

    Raises:
        ValueError for non-CSV MIME types.
    """
    allowed = {
        "text/csv",
        "application/csv",
        "text/plain",
        "application/octet-stream",  # Some browsers send this for .csv
    }
    # Strip parameters like charset (e.g. "text/csv; charset=utf-8")
    base_type = content_type.split(";")[0].strip().lower()
    if base_type not in allowed:
        raise ValueError(
            f"Unsupported file type '{content_type}'. "
            "Please upload a CSV file (.csv)."
        )
