-- =============================================================================
-- reporting_schema.sql
-- Creates the reporting_tickets and etl_jobs tables used by the Phase 2
-- ETL pipeline and analytics layer.
--
-- Run this script AFTER the main schema (which creates the `tickets` table).
-- Usage: psql -U <user> -d helpdesk_db -f database/reporting_schema.sql
-- =============================================================================

-- ---------------------------------------------------------------------------
-- ENUMs (reuse same domain as tickets table)
-- ---------------------------------------------------------------------------

DO $$ BEGIN
    CREATE TYPE priority_enum AS ENUM ('Low', 'Medium', 'High', 'Critical');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE status_enum AS ENUM ('Open', 'In Progress', 'Resolved', 'Closed');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE category_enum AS ENUM (
        'Hardware', 'Software', 'Network', 'Access & Permissions',
        'Email & Communication', 'VPN & Remote Access', 'Printer',
        'Security', 'Other'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- ---------------------------------------------------------------------------
-- reporting_tickets — stores ETL-imported historical ticket data
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS reporting_tickets (
    ticket_id           SERIAL PRIMARY KEY,

    -- Core ticket fields (mirrors tickets table)
    employee_name       VARCHAR(255)    NOT NULL,
    department          VARCHAR(255)    NOT NULL,
    issue_category      VARCHAR(100)    NOT NULL,
    description         TEXT            NOT NULL,
    priority            VARCHAR(50)     NOT NULL DEFAULT 'Medium',
    status              VARCHAR(50)     NOT NULL DEFAULT 'Open',
    resolution_notes    TEXT,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ,

    -- ETL provenance columns
    source_file         VARCHAR(512)    NOT NULL,   -- Original filename
    ingestion_batch_id  UUID            NOT NULL,   -- Links all rows from one upload
    is_duplicate        BOOLEAN         NOT NULL DEFAULT FALSE,

    -- Constraints
    CONSTRAINT rpt_priority_check CHECK (priority IN ('Low', 'Medium', 'High', 'Critical')),
    CONSTRAINT rpt_status_check   CHECK (status   IN ('Open', 'In Progress', 'Resolved', 'Closed'))
);

-- ---------------------------------------------------------------------------
-- Indexes for analytics query patterns
-- ---------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_rpt_department
    ON reporting_tickets (department);

CREATE INDEX IF NOT EXISTS idx_rpt_issue_category
    ON reporting_tickets (issue_category);

CREATE INDEX IF NOT EXISTS idx_rpt_priority
    ON reporting_tickets (priority);

CREATE INDEX IF NOT EXISTS idx_rpt_status
    ON reporting_tickets (status);

CREATE INDEX IF NOT EXISTS idx_rpt_created_at
    ON reporting_tickets (created_at);

CREATE INDEX IF NOT EXISTS idx_rpt_batch_id
    ON reporting_tickets (ingestion_batch_id);

-- Composite index for time-series queries grouped by status
CREATE INDEX IF NOT EXISTS idx_rpt_created_status
    ON reporting_tickets (created_at, status);

-- ---------------------------------------------------------------------------
-- etl_jobs — audit log of every file upload / ETL pipeline run
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS etl_jobs (
    job_id          SERIAL PRIMARY KEY,
    filename        VARCHAR(512)    NOT NULL,
    batch_id        UUID            NOT NULL UNIQUE,

    -- Row statistics (populated on completion)
    total_rows      INTEGER,
    inserted_rows   INTEGER,
    duplicate_rows  INTEGER,
    error_rows      INTEGER,

    -- Job lifecycle
    status          VARCHAR(50)     NOT NULL DEFAULT 'running',
    error_message   TEXT,
    started_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ,

    CONSTRAINT etl_status_check CHECK (status IN ('running', 'completed', 'failed'))
);

CREATE INDEX IF NOT EXISTS idx_etl_jobs_started_at
    ON etl_jobs (started_at DESC);

-- ---------------------------------------------------------------------------
-- Helpful analytics views
-- ---------------------------------------------------------------------------

-- Ticket volume per month (per source table)
CREATE OR REPLACE VIEW v_monthly_ticket_volume AS
SELECT
    DATE_TRUNC('month', created_at)::DATE  AS month,
    COUNT(*)                               AS total_tickets,
    SUM(CASE WHEN status IN ('Resolved', 'Closed') THEN 1 ELSE 0 END) AS resolved_tickets,
    SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END)                  AS open_tickets
FROM reporting_tickets
GROUP BY 1
ORDER BY 1;

-- Average resolution time per category
CREATE OR REPLACE VIEW v_avg_resolution_by_category AS
SELECT
    issue_category,
    COUNT(*)                                                        AS sample_count,
    ROUND(
        AVG(EXTRACT(EPOCH FROM (updated_at - created_at)) / 86400.0)::NUMERIC,
        2
    )                                                               AS avg_days,
    ROUND(
        MIN(EXTRACT(EPOCH FROM (updated_at - created_at)) / 86400.0)::NUMERIC,
        2
    )                                                               AS min_days,
    ROUND(
        MAX(EXTRACT(EPOCH FROM (updated_at - created_at)) / 86400.0)::NUMERIC,
        2
    )                                                               AS max_days
FROM reporting_tickets
WHERE status IN ('Resolved', 'Closed')
  AND updated_at IS NOT NULL
GROUP BY 1
ORDER BY avg_days DESC;

-- Department summary
CREATE OR REPLACE VIEW v_department_summary AS
SELECT
    department,
    COUNT(*)                                                           AS total,
    SUM(CASE WHEN status = 'Open'        THEN 1 ELSE 0 END)           AS open_count,
    SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END)           AS in_progress_count,
    SUM(CASE WHEN status IN ('Resolved', 'Closed') THEN 1 ELSE 0 END) AS resolved_count,
    ROUND(
        SUM(CASE WHEN status IN ('Resolved', 'Closed') THEN 1 ELSE 0 END)::NUMERIC
        / NULLIF(COUNT(*), 0) * 100,
        2
    )                                                                  AS resolution_rate_pct
FROM reporting_tickets
GROUP BY 1
ORDER BY total DESC;

-- =============================================================================
-- End of reporting_schema.sql
-- =============================================================================
