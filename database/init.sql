-- ============================================================
-- database/init.sql
-- Helpdesk Ticket Management System — Database Initialisation
--
-- Run this script in pgAdmin Query Tool or via psql:
--   psql -U postgres -f database/init.sql
--
-- Creates the database, schema, tables, and indexes.
-- ============================================================

-- ─── Create Database ──────────────────────────────────────
-- Run as the postgres superuser. Comment out if database already exists.
CREATE DATABASE helpdesk_db
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- Connect to the new database before running the rest:
-- \c helpdesk_db     (psql command)
-- (In pgAdmin, right-click helpdesk_db > Query Tool)

-- ─── Tickets Table ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS tickets (
    ticket_id        SERIAL          PRIMARY KEY,
    employee_name    VARCHAR(150)    NOT NULL,
    department       VARCHAR(100)    NOT NULL,
    issue_category   VARCHAR(100)    NOT NULL,
    description      TEXT            NOT NULL,
    priority         VARCHAR(20)     NOT NULL    DEFAULT 'Medium',
    status           VARCHAR(30)     NOT NULL    DEFAULT 'Open',
    resolution_notes TEXT,
    created_at       TIMESTAMPTZ     NOT NULL    DEFAULT NOW(),
    updated_at       TIMESTAMPTZ     NOT NULL    DEFAULT NOW(),

    -- Enforce valid enum values at the database level
    CONSTRAINT chk_priority CHECK (
        priority IN ('Low', 'Medium', 'High', 'Critical')
    ),
    CONSTRAINT chk_status CHECK (
        status IN ('Open', 'In Progress', 'Resolved', 'Closed')
    ),
    CONSTRAINT chk_category CHECK (
        issue_category IN (
            'VPN Issue',
            'Password Reset',
            'Software Installation',
            'Laptop Issue',
            'Email Access',
            'Network Connectivity',
            'Hardware Request',
            'Other'
        )
    )
);

-- ─── Indexes (optimise common query patterns) ─────────────
CREATE INDEX IF NOT EXISTS idx_tickets_status        ON tickets (status);
CREATE INDEX IF NOT EXISTS idx_tickets_priority      ON tickets (priority);
CREATE INDEX IF NOT EXISTS idx_tickets_category      ON tickets (issue_category);
CREATE INDEX IF NOT EXISTS idx_tickets_department    ON tickets (department);
CREATE INDEX IF NOT EXISTS idx_tickets_employee_name ON tickets (employee_name);
CREATE INDEX IF NOT EXISTS idx_tickets_created_at    ON tickets (created_at DESC);

-- ─── Auto-update updated_at trigger ──────────────────────
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_tickets_updated_at
    BEFORE UPDATE ON tickets
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ─── Comments ─────────────────────────────────────────────
COMMENT ON TABLE  tickets                  IS 'Helpdesk support tickets submitted by employees';
COMMENT ON COLUMN tickets.ticket_id        IS 'Auto-incrementing unique ticket identifier';
COMMENT ON COLUMN tickets.employee_name    IS 'Full name of the employee who submitted the ticket';
COMMENT ON COLUMN tickets.department       IS 'Organizational department of the employee';
COMMENT ON COLUMN tickets.issue_category   IS 'IT support category of the reported issue';
COMMENT ON COLUMN tickets.description      IS 'Detailed description of the problem';
COMMENT ON COLUMN tickets.priority         IS 'Urgency level: Low | Medium | High | Critical';
COMMENT ON COLUMN tickets.status           IS 'Lifecycle state: Open | In Progress | Resolved | Closed';
COMMENT ON COLUMN tickets.resolution_notes IS 'Notes added by support agent when resolving the ticket';
COMMENT ON COLUMN tickets.created_at       IS 'UTC timestamp when the ticket was first created';
COMMENT ON COLUMN tickets.updated_at       IS 'UTC timestamp of the most recent update (auto-managed)';
