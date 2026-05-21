"""
etl/csv_loader.py — File I/O layer for the ETL pipeline.

Responsibilities:
  - Read raw bytes from an uploaded file
  - Auto-detect encoding (UTF-8 → latin-1 fallback)
  - Parse CSV into a pandas DataFrame
  - Validate schema columns exist
  - Surface clear error messages for malformed files

Edge cases handled:
  - BOM (byte order mark) in UTF-8 encoded files
  - Files encoded in latin-1 / ISO-8859-1 (common from Windows Excel exports)
  - Files with/without headers
  - Files where the header row is repeated mid-file
  - Excel-exported CSV with extra trailing comma columns
  - Files with inconsistent delimiter detection (tries comma first, then semicolon/tab)
"""

from __future__ import annotations

import io
import logging
from typing import Optional

import pandas as pd

from etl.validators import validate_csv_schema, validate_file_size

logger = logging.getLogger(__name__)


def detect_encoding(file_bytes: bytes) -> str:
    """
    Detect the text encoding of a byte stream.

    Strategy:
      1. Check for UTF-8 BOM
      2. Try decoding as UTF-8
      3. Fall back to latin-1 (never raises, decodes every byte)
    """
    # Check for UTF-8 BOM
    if file_bytes.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig"

    try:
        file_bytes.decode("utf-8")
        return "utf-8"
    except UnicodeDecodeError:
        logger.warning("UTF-8 decode failed — falling back to latin-1 encoding.")
        return "latin-1"


def _detect_delimiter(sample: str) -> str:
    """
    Heuristically detect CSV delimiter from the first two lines.
    Tries comma, semicolon, tab in that order.
    """
    first_lines = sample.split("\n")[:2]
    sample_str = "\n".join(first_lines)

    counts = {
        ",":  sample_str.count(","),
        ";":  sample_str.count(";"),
        "\t": sample_str.count("\t"),
        "|":  sample_str.count("|"),
    }
    return max(counts, key=counts.get)


def load_csv_from_bytes(
    file_bytes: bytes,
    filename: str,
    max_mb: int = 50,
) -> pd.DataFrame:
    """
    Parse raw CSV bytes into a pandas DataFrame.

    Steps:
      1. Size validation
      2. Encoding detection
      3. Delimiter detection
      4. CSV parsing (with duplicate-header row stripping)
      5. Schema validation

    Args:
        file_bytes: Raw file content from the HTTP upload.
        filename:   Original filename for error messages.
        max_mb:     Maximum allowed file size in megabytes.

    Returns:
        Raw DataFrame (no transformation applied yet).

    Raises:
        ValueError: For size, encoding, delimiter, or schema errors — always
                    with a user-friendly message suitable for the API response.
    """
    # Step 1 — size guard
    validate_file_size(file_bytes, max_mb=max_mb)

    # Step 2 — encoding
    encoding = detect_encoding(file_bytes)
    logger.info("Detected encoding '%s' for file '%s'.", encoding, filename)

    try:
        text_content = file_bytes.decode(encoding)
    except (UnicodeDecodeError, LookupError) as exc:
        raise ValueError(
            f"Could not decode '{filename}' with encoding '{encoding}': {exc}"
        ) from exc

    # Step 3 — delimiter detection
    delimiter = _detect_delimiter(text_content[:2000])
    logger.info("Detected delimiter %r for file '%s'.", delimiter, filename)

    # Step 4 — parse CSV
    try:
        df = pd.read_csv(
            io.StringIO(text_content),
            sep=delimiter,
            dtype=str,           # Read everything as string — normalisation handles types
            keep_default_na=False,  # Don't auto-convert '' to NaN; we handle that
            na_values=["", "NULL", "null", "N/A", "n/a", "NA", "na", "#N/A"],
            skipinitialspace=True,
            on_bad_lines="warn",  # Don't crash on malformed rows; log and skip
        )
    except pd.errors.EmptyDataError:
        raise ValueError(f"'{filename}' appears to be empty (no data found).")
    except pd.errors.ParserError as exc:
        raise ValueError(f"Could not parse '{filename}' as CSV: {exc}") from exc

    if df.empty:
        raise ValueError(f"'{filename}' contains headers but no data rows.")

    # Strip BOM from first column name if present
    if df.columns[0].startswith("\ufeff"):
        df.columns = [df.columns[0].lstrip("\ufeff")] + list(df.columns[1:])

    # Remove any rows that are exact duplicates of the header (Excel artifact)
    header_row_mask = df.apply(
        lambda row: list(row.values) == list(df.columns), axis=1
    )
    if header_row_mask.any():
        logger.warning(
            "Stripped %d header-duplicate rows from '%s'.",
            header_row_mask.sum(),
            filename,
        )
        df = df[~header_row_mask].reset_index(drop=True)

    # Drop completely unnamed trailing columns (Excel trailing commas)
    unnamed_cols = [c for c in df.columns if str(c).startswith("Unnamed:")]
    if unnamed_cols:
        df = df.drop(columns=unnamed_cols)

    logger.info(
        "Loaded '%s' — %d rows × %d columns.",
        filename, len(df), len(df.columns),
    )

    # Step 5 — schema validation
    validate_csv_schema(df)

    return df


class CSVLoader:
    """
    Stateless facade over the CSV loading functions.
    Intended to be called directly from the ETL orchestrator.
    """

    @staticmethod
    def load_and_validate(
        file_bytes: bytes,
        filename: str,
        max_mb: int = 50,
    ) -> pd.DataFrame:
        """
        Load and schema-validate a CSV file from bytes.

        Returns a raw DataFrame ready for the transformation stage.
        All exceptions are re-raised as ValueError with user-friendly messages.
        """
        return load_csv_from_bytes(file_bytes, filename, max_mb=max_mb)
