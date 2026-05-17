# System Architecture — Helpdesk Ticket Management System

## Overview

This document describes the architecture decisions, patterns, and trade-offs for the Phase 1 implementation of the Helpdesk Ticket Management System.

---

## Architecture Style

The system follows a **three-tier architecture**:

```
┌─────────────────────────────────────────────────────┐
│  Presentation Tier  (React SPA)                     │
│  - React 18 + React Router v6                       │
│  - Axios HTTP client                                 │
│  - CSS custom properties design system              │
└────────────────────┬────────────────────────────────┘
                     │ HTTP/REST (JSON)
┌────────────────────▼────────────────────────────────┐
│  Application Tier  (FastAPI)                        │
│  - REST API (routers layer)                         │
│  - Business logic (service layer)                   │
│  - Data access (CRUD layer)                         │
│  - Pydantic validation                              │
└────────────────────┬────────────────────────────────┘
                     │ SQLAlchemy ORM
┌────────────────────▼────────────────────────────────┐
│  Data Tier  (PostgreSQL)                            │
│  - tickets table                                    │
│  - Indexes on status, priority, category, dept      │
│  - Auto-updated timestamps via trigger              │
└─────────────────────────────────────────────────────┘
```

---

## Backend Architecture

### Layer Separation

```
main.py          ← Entry point, middleware, router registration
  │
routers/         ← HTTP concerns (request parsing, response codes)
  └ tickets.py
      │
services/        ← Business logic, status transition rules
  └ ticket_service.py
      │
crud.py          ← Database operations (SQLAlchemy queries)
      │
models.py        ← ORM models (SQLAlchemy)
database.py      ← Engine, session factory, Base
config.py        ← pydantic-settings (env-based configuration)
schemas.py       ← Pydantic models (validation + serialization)
utils/           ← Pure helper functions (validators, pagination)
middleware/      ← Request logging middleware
```

### Design Principles

- **Single Responsibility**: Each layer has one job. Routers don't touch the DB; CRUD doesn't contain business rules.
- **Dependency Injection**: `TicketService` is injected per-request via `Depends()`, making it easily testable with mock sessions.
- **Fail Fast**: Pydantic validates all inputs before they reach business logic. Invalid requests never touch the database.
- **Configuration as Code**: All settings come from environment variables via `pydantic-settings`. No hardcoded values.
- **Connection Pooling**: SQLAlchemy engine uses `pool_size=10`, `max_overflow=20`, `pool_recycle=1800` for production-grade connection management.

---

## Frontend Architecture

### Component Hierarchy

```
App.js (BrowserRouter + Routes)
  │
Sidebar.js (fixed navigation)
  │
  ├── pages/Dashboard.js
  │     ├── StatCard.js (×6)
  │     ├── TicketTable.js (recent tickets)
  │     └── Status distribution bar chart
  │
  ├── pages/TicketList.js
  │     ├── SearchBar.js (debounced)
  │     ├── FilterPanel.js (status/priority/category dropdowns)
  │     └── TicketTable.js (paginated)
  │
  ├── pages/CreateTicket.js
  │     └── Form (validation, priority radio group)
  │
  └── pages/TicketDetail.js
        ├── StatusBadge, PriorityBadge
        ├── Inline edit form
        ├── Quick status update panel
        └── Danger zone (delete)
```

### State Management

Phase 1 uses **local component state** (useState + useEffect) since the data model is simple and there are no shared-state requirements across sibling components. The custom hooks (`useTickets`, `useDebounce`) encapsulate reusable async patterns.

**Future**: Redux Toolkit or Zustand can be added in Phase 2 when user sessions, notifications, and real-time updates are introduced.

### API Integration

- `src/api.js` — Axios instance with base URL and interceptors
- `src/services/ticketService.js` — All API methods in one place
- Components never import Axios directly — they only use the service layer

---

## Database Design

### Table: `tickets`

| Column            | Type          | Notes |
|------------------|---------------|-------|
| `ticket_id`       | SERIAL PK     | Auto-increment |
| `employee_name`   | VARCHAR(150)  | Indexed |
| `department`      | VARCHAR(100)  | Indexed |
| `issue_category`  | VARCHAR(100)  | Indexed + CHECK constraint |
| `description`     | TEXT          | Full text |
| `priority`        | VARCHAR(20)   | Indexed + CHECK constraint |
| `status`          | VARCHAR(30)   | Indexed + CHECK constraint |
| `resolution_notes`| TEXT          | Nullable |
| `created_at`      | TIMESTAMPTZ   | Server default NOW() |
| `updated_at`      | TIMESTAMPTZ   | Auto-updated via trigger |

### Indexes

All columns used in WHERE clauses or ORDER BY have explicit B-tree indexes to avoid full table scans:
- `idx_tickets_status`
- `idx_tickets_priority`
- `idx_tickets_category`
- `idx_tickets_department`
- `idx_tickets_employee_name`
- `idx_tickets_created_at` (DESC, for pagination)

---

## Security Considerations

- **Input validation**: Pydantic enforces type, length, and enum constraints on all inputs before database access.
- **SQL injection**: SQLAlchemy ORM uses parameterised queries; no raw SQL is constructed from user input.
- **CORS**: Restricted to configured origins via `allowed_origins` setting; wildcard `*` is never used in production.
- **Environment variables**: No credentials in source code. `.env` is `.gitignore`d.
- **Error messages**: Generic 500 responses are returned for unexpected errors; internal details are logged server-side only.

---

## Phase 2 Roadmap

The architecture is deliberately designed to accommodate these future enhancements:

| Feature | Integration Point |
|---------|------------------|
| **Authentication / RBAC** | FastAPI dependency (JWT middleware) + frontend AuthContext |
| **AI ticket classification** | `services/ai_service.py` calling OpenAI API on ticket creation |
| **Semantic search (RAG)** | pgvector extension + `embedding` column in `tickets` table |
| **Real-time notifications** | WebSocket endpoint in FastAPI + React context |
| **Analytics dashboard** | Dedicated `/api/analytics` router + Chart.js or Recharts |
| **Email notifications** | Background task (FastAPI `BackgroundTasks`) on ticket create/update |
| **Audit log** | Separate `ticket_audit` table populated via SQLAlchemy events |
| **Data export** | CSV/Excel export endpoint using `pandas` or `openpyxl` |
