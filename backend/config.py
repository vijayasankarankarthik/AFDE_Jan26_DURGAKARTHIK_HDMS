"""
config.py — Centralised application configuration via pydantic-settings.

All settings are loaded from environment variables (or a .env file).
Add new settings here as the application grows. Future AI/RAG settings
are already stubbed so Phase 2 integration requires only filling in values.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    # ─── Application ──────────────────────────────────────
    app_name: str = "Helpdesk Ticket Management System"
    app_version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    # ─── Database ─────────────────────────────────────────
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/helpdesk_db"
    db_echo: bool = False

    # ─── CORS ─────────────────────────────────────────────
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:3001"]

    # ─── Future AI / RAG Integration (Phase 2) ────────────
    openai_api_key: str = ""
    vector_db_url: str = ""
    embedding_model: str = "text-embedding-ada-002"

    # ─── Pagination defaults ──────────────────────────────
    default_page_size: int = 20
    max_page_size: int = 100

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_origins(cls, value):
        """Accept either a list or a comma-separated string."""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    model_config = {
        "env_file": os.path.join(os.path.dirname(__file__), ".env"),
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings instance (singleton pattern)."""
    return Settings()
