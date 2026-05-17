"""
utils/validators.py — Reusable input validation and business rule helpers.

These functions are pure (no DB dependency) and easily unit-testable.
They are shared across the service layer and can be imported anywhere.
"""

from __future__ import annotations

import re
from typing import Dict, List

from fastapi import HTTPException, status


# ─── Status transition validator ───────────────────────────────────────────────

def validate_status_transition(
    current_status: str,
    new_status: str,
    valid_transitions: Dict[str, List[str]],
) -> None:
    """
    Enforce valid ticket status transitions.

    Raises HTTP 422 if the transition from current_status → new_status
    is not permitted according to the valid_transitions map.

    Args:
        current_status: The ticket's current status string.
        new_status:     The desired target status string.
        valid_transitions: A dict mapping each status to its allowed next states.
    """
    if current_status == new_status:
        return  # No-op, not an error

    allowed = valid_transitions.get(current_status, [])
    if new_status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Invalid status transition: '{current_status}' → '{new_status}'. "
                f"Allowed transitions from '{current_status}': {allowed or ['none (terminal state)']}"
            ),
        )


# ─── String sanitization ───────────────────────────────────────────────────────

def sanitize_text(value: str, max_length: int = 5000) -> str:
    """
    Sanitize a text string for safe storage.
    - Strips leading/trailing whitespace
    - Collapses multiple consecutive blank lines into one
    - Truncates to max_length characters

    Does NOT strip HTML tags here — that is the responsibility of the
    frontend or a dedicated HTML sanitizer if HTML content is ever accepted.
    """
    if not value:
        return value

    value = value.strip()
    # Collapse 3+ consecutive newlines into 2
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value[:max_length]


# ─── Pagination helpers ────────────────────────────────────────────────────────

def calculate_skip(page: int, page_size: int) -> int:
    """Convert 1-based page number to 0-based SQL offset."""
    return (page - 1) * page_size


def calculate_total_pages(total: int, page_size: int) -> int:
    """Calculate the total number of pages given total records and page size."""
    if page_size <= 0:
        return 0
    return (total + page_size - 1) // page_size


# ─── Value validators ─────────────────────────────────────────────────────────

VALID_PRIORITIES = {"Low", "Medium", "High", "Critical"}
VALID_STATUSES = {"Open", "In Progress", "Resolved", "Closed"}
VALID_CATEGORIES = {
    "VPN Issue",
    "Password Reset",
    "Software Installation",
    "Laptop Issue",
    "Email Access",
    "Network Connectivity",
    "Hardware Request",
    "Other",
}


def is_valid_priority(value: str) -> bool:
    """Return True if the priority string is one of the accepted values."""
    return value in VALID_PRIORITIES


def is_valid_status(value: str) -> bool:
    """Return True if the status string is one of the accepted values."""
    return value in VALID_STATUSES


def is_valid_category(value: str) -> bool:
    """Return True if the category string is one of the accepted values."""
    return value in VALID_CATEGORIES
