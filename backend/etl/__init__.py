"""etl package — Production ETL pipeline for historical ticket data ingestion.

Architecture:
  csv_loader.py   → raw file I/O + schema validation
  validators.py   → row-level field validation (pure functions)
  transformers.py → pandas-based normalisation & deduplication
  loaders.py      → SQLAlchemy batch insertion + ETLJob audit management
"""
