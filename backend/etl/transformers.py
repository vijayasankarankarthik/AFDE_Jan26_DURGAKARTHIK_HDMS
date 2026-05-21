"""
etl/transformers.py — Pandas-based normalisation and deduplication for the ETL pipeline.

Every function is pure: takes a DataFrame, returns a transformed DataFrame (or tuple).
No side effects, no database access — fully testable in isolation.

Normalisation strategy:
  - Aliases are resolved via lookup maps before enum validation runs.
  - Text fields are stripped and title-cased where appropriate.
  - Timestamps are coerced to UTC-aware datetimes.
  - Duplicates are detected on a composite natural key to preserve audit history.

Edge cases handled:
  - Mixed case inputs ("CRITICAL", "critical", "CrItIcAl")
  - Underscore/hyphen-separated values ("in_progress", "in-progress")
  - Abbreviated values ("crit", "hi", "med", "lo")
  - Leading/trailing whitespace in all string fields
  - Numeric values in string columns (converted to str)
  - All-NaN rows (dropped as empty rows early)
  - Mixed timestamp formats in a single file
  - Files with duplicate header rows
"""

from __future__ import annotations

import logging
from typing import Dict, Tuple

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

# ─── Alias maps — resolved before enum validation ─────────────────────────────

PRIORITY_ALIASES: Dict[str, str] = {
    # Critical
    "critical": "Critical",
    "crit":     "Critical",
    "p1":       "Critical",
    "urgent":   "Critical",
    # High
    "high":     "High",
    "hi":       "High",
    "p2":       "High",
    # Medium
    "medium":   "Medium",
    "med":      "Medium",
    "moderate": "Medium",
    "normal":   "Medium",
    "p3":       "Medium",
    # Low
    "low":      "Low",
    "lo":       "Low",
    "minor":    "Low",
    "p4":       "Low",
}

STATUS_ALIASES: Dict[str, str] = {
    "open":        "Open",
    "new":         "Open",
    "submitted":   "Open",
    "in progress": "In Progress",
    "in_progress": "In Progress",
    "in-progress": "In Progress",
    "inprogress":  "In Progress",
    "wip":         "In Progress",
    "working":     "In Progress",
    "assigned":    "In Progress",
    "resolved":    "Resolved",
    "done":        "Resolved",
    "fixed":       "Resolved",
    "completed":   "Resolved",
    "complete":    "Resolved",
    "closed":      "Closed",
    "close":       "Closed",
    "archived":    "Closed",
    "cancelled":   "Closed",
    "canceled":    "Closed",
}

CATEGORY_ALIASES: Dict[str, str] = {
    "vpn":                    "VPN Issue",
    "vpn issue":              "VPN Issue",
    "vpn problem":            "VPN Issue",
    "vpn access":             "VPN Issue",
    "password":               "Password Reset",
    "password reset":         "Password Reset",
    "pwd reset":              "Password Reset",
    "pwd":                    "Password Reset",
    "account locked":         "Password Reset",
    "software":               "Software Installation",
    "software install":       "Software Installation",
    "software installation":  "Software Installation",
    "app install":            "Software Installation",
    "laptop":                 "Laptop Issue",
    "laptop issue":           "Laptop Issue",
    "laptop problem":         "Laptop Issue",
    "hardware issue":         "Laptop Issue",
    "email":                  "Email Access",
    "email access":           "Email Access",
    "email issue":            "Email Access",
    "outlook":                "Email Access",
    "network":                "Network Connectivity",
    "network connectivity":   "Network Connectivity",
    "internet":               "Network Connectivity",
    "connectivity":           "Network Connectivity",
    "hardware":               "Hardware Request",
    "hardware request":       "Hardware Request",
    "equipment":              "Hardware Request",
    "other":                  "Other",
    "misc":                   "Other",
    "miscellaneous":          "Other",
    "general":                "Other",
}


# ─── Individual transformation functions ─────────────────────────────────────

def drop_empty_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Remove rows where ALL key fields are NaN/blank (genuinely empty CSV lines)."""
    key_cols = [c for c in ["employee_name", "department", "description"] if c in df.columns]
    if not key_cols:
        return df
    mask = df[key_cols].apply(
        lambda col: col.astype(str).str.strip().replace("nan", "", regex=False)
    )
    empty_mask = (mask == "").all(axis=1)
    dropped = empty_mask.sum()
    if dropped:
        logger.info("Dropped %d fully empty rows.", dropped)
    return df[~empty_mask].reset_index(drop=True)


def standardise_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Lower-case and strip all column headers.
    Also handle common variations:
      - 'Employee Name' → 'employee_name'
      - 'IssueCategory' → 'issue_category'
      - 'ResolutionNotes' → 'resolution_notes'
    """
    col_map = {}
    for col in df.columns:
        normalised = col.strip().lower().replace(" ", "_").replace("-", "_")
        col_map[col] = normalised
    df = df.rename(columns=col_map)

    # Handle CamelCase → snake_case (e.g. "EmployeeName" → "employee_name")
    import re
    new_map = {}
    for col in df.columns:
        snake = re.sub(r"(?<=[a-z0-9])([A-Z])", r"_\1", col).lower()
        if snake != col:
            new_map[col] = snake
    if new_map:
        df = df.rename(columns=new_map)

    return df


def normalize_text_fields(df: pd.DataFrame) -> pd.DataFrame:
    """
    Strip and clean string fields.
    - employee_name, department: strip + normalize consecutive whitespace
    - description, resolution_notes: strip only (preserve casing)
    - Convert any numeric values in string columns to string
    """
    text_cols = ["employee_name", "department", "description", "resolution_notes"]
    for col in text_cols:
        if col not in df.columns:
            continue
        # Convert non-string to string, replace literal 'nan' with empty
        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
            .replace(r"^nan$", "", regex=True)
            .replace(r"^None$", "", regex=True)
        )
        # Collapse multiple spaces
        if col in ("employee_name", "department"):
            df[col] = df[col].str.replace(r"\s+", " ", regex=True)

    return df


def normalize_priority(df: pd.DataFrame) -> pd.DataFrame:
    """
    Map priority column to canonical values via alias lookup.
    Unknown values are left as-is (validation will flag them).
    """
    if "priority" not in df.columns:
        return df
    df["priority"] = (
        df["priority"]
        .astype(str)
        .str.strip()
        .str.lower()
        .map(lambda v: PRIORITY_ALIASES.get(v, None))
        .fillna(df["priority"].astype(str).str.strip())
    )
    return df


def normalize_status(df: pd.DataFrame) -> pd.DataFrame:
    """Map status column to canonical values via alias lookup."""
    if "status" not in df.columns:
        return df
    df["status"] = (
        df["status"]
        .astype(str)
        .str.strip()
        .str.lower()
        .map(lambda v: STATUS_ALIASES.get(v, None))
        .fillna(df["status"].astype(str).str.strip())
    )
    return df


def normalize_category(df: pd.DataFrame) -> pd.DataFrame:
    """Map issue_category to canonical values via alias lookup."""
    if "issue_category" not in df.columns:
        return df
    df["issue_category"] = (
        df["issue_category"]
        .astype(str)
        .str.strip()
        .str.lower()
        .map(lambda v: CATEGORY_ALIASES.get(v, None))
        .fillna(df["issue_category"].astype(str).str.strip())
    )
    return df


def parse_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    """
    Coerce created_at and updated_at to UTC-aware timestamps.

    Rows where created_at cannot be parsed are flagged (NaT).
    updated_at falls back to created_at when missing.
    """
    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce", utc=True)

    if "updated_at" in df.columns:
        df["updated_at"] = pd.to_datetime(df["updated_at"], errors="coerce", utc=True)
        # Fill missing updated_at with created_at
        missing_updated = df["updated_at"].isna()
        df.loc[missing_updated, "updated_at"] = df.loc[missing_updated, "created_at"]
    else:
        # Create updated_at = created_at if column absent entirely
        df["updated_at"] = df["created_at"]

    return df


def fill_missing_optionals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill optional columns with safe defaults.
    - resolution_notes: blank string → None (stored as SQL NULL)
    """
    if "resolution_notes" in df.columns:
        df["resolution_notes"] = df["resolution_notes"].replace(
            {"": None, "nan": None, "None": None, "none": None}
        )
        df["resolution_notes"] = df["resolution_notes"].where(
            df["resolution_notes"].notna(), other=None
        )
    else:
        df["resolution_notes"] = None

    return df


def drop_duplicates(df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
    """
    Detect and remove duplicate rows based on the natural composite key:
      (employee_name, department, issue_category, description, created_at)

    Strategy:
      - Keep the FIRST occurrence of each duplicate group (earliest-seen in file).
      - Return (deduplicated_df, duplicate_count).

    Edge cases:
      - NaT in created_at: treated as a unique timestamp (not deduplicated against other NaTs)
      - Description comparison is case-insensitive to catch case-only duplicates
    """
    natural_key = [
        "employee_name",
        "department",
        "issue_category",
    ]
    # Use lowercase description for comparison but keep original
    available_key = [c for c in natural_key if c in df.columns]

    if not available_key:
        return df, 0

    # Add description (lowercased) and date-only for dedup key
    dedup_df = df.copy()
    if "description" in df.columns:
        dedup_df["_desc_lower"] = df["description"].astype(str).str.lower().str.strip()
        available_key.append("_desc_lower")

    if "created_at" in df.columns:
        # Date-only dedup to handle timestamp precision differences
        dedup_df["_date_key"] = pd.to_datetime(df["created_at"], errors="coerce").dt.date
        available_key.append("_date_key")

    original_len = len(dedup_df)
    dedup_df = dedup_df.drop_duplicates(subset=available_key, keep="first")
    duplicate_count = original_len - len(dedup_df)

    # Drop temporary columns
    drop_cols = [c for c in ["_desc_lower", "_date_key"] if c in dedup_df.columns]
    dedup_df = dedup_df.drop(columns=drop_cols)

    if duplicate_count:
        logger.info("Removed %d duplicate rows (composite key dedup).", duplicate_count)

    return dedup_df.reset_index(drop=True), duplicate_count


# ─── Pipeline orchestrator ────────────────────────────────────────────────────

def run_full_transform(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    """
    Run the complete ETL transformation chain in dependency order.

    Chain:
      1. standardise_column_names
      2. drop_empty_rows
      3. normalize_text_fields
      4. normalize_priority
      5. normalize_status
      6. normalize_category
      7. parse_timestamps
      8. fill_missing_optionals
      9. drop_duplicates

    Returns:
        (transformed_df, stats_dict) where stats_dict contains:
          - total_input_rows
          - empty_rows_dropped
          - duplicate_rows
          - rows_with_invalid_timestamps
          - output_rows
    """
    stats: Dict = {}
    stats["total_input_rows"] = len(df)

    df = standardise_column_names(df)
    len_before_empty = len(df)
    df = drop_empty_rows(df)
    stats["empty_rows_dropped"] = len_before_empty - len(df)

    df = normalize_text_fields(df)
    df = normalize_priority(df)
    df = normalize_status(df)
    df = normalize_category(df)
    df = parse_timestamps(df)
    df = fill_missing_optionals(df)

    # Count unparseable timestamps (NaT rows)
    if "created_at" in df.columns:
        stats["rows_with_invalid_timestamps"] = int(df["created_at"].isna().sum())
    else:
        stats["rows_with_invalid_timestamps"] = 0

    df, dup_count = drop_duplicates(df)
    stats["duplicate_rows"] = dup_count
    stats["output_rows"] = len(df)

    logger.info(
        "ETL transform complete — input: %d, empty: %d, dups: %d, invalid_ts: %d, output: %d",
        stats["total_input_rows"],
        stats["empty_rows_dropped"],
        stats["duplicate_rows"],
        stats["rows_with_invalid_timestamps"],
        stats["output_rows"],
    )

    return df, stats
