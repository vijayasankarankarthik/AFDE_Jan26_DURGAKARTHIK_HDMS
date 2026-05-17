<!-- ============================================================
  docs/api_documentation.md
  Helpdesk Ticket Management System — REST API Reference
  ============================================================ -->

# REST API Documentation

**Base URL:** `http://localhost:8000`  
**API Prefix:** `/api`  
**Interactive Docs:** `http://localhost:8000/docs` (Swagger UI)  
**Alternative Docs:** `http://localhost:8000/redoc`

---

## Authentication

Phase 1 does not include authentication. All endpoints are publicly accessible on the local network. Role-based access control (RBAC) is planned for Phase 2.

---

## Common Response Codes

| Code | Meaning |
|------|---------|
| `200 OK` | Request succeeded |
| `201 Created` | Resource successfully created |
| `404 Not Found` | Resource does not exist |
| `422 Unprocessable Entity` | Validation error (invalid input) |
| `500 Internal Server Error` | Unexpected server error |

---

## Enumerations

### Priority
| Value | Description |
|-------|-------------|
| `Low` | Non-urgent issue |
| `Medium` | Standard priority (default) |
| `High` | Important, needs prompt attention |
| `Critical` | Business-impacting, needs immediate action |

### Status
| Value | Description |
|-------|-------------|
| `Open` | Newly submitted, awaiting action |
| `In Progress` | Being actively worked on |
| `Resolved` | Issue fixed, pending closure |
| `Closed` | Fully closed |

### Issue Category
`VPN Issue`, `Password Reset`, `Software Installation`, `Laptop Issue`, `Email Access`, `Network Connectivity`, `Hardware Request`, `Other`

---

## Endpoints

---

### GET /api/tickets/stats

Returns aggregated ticket statistics for the dashboard.

**Response `200 OK`**
```json
{
  "total_tickets": 18,
  "open_tickets": 5,
  "in_progress_tickets": 4,
  "resolved_tickets": 6,
  "closed_tickets": 3,
  "critical_tickets": 2,
  "high_priority_tickets": 5
}
```

---

### GET /api/tickets/search

Search and filter tickets with keyword and filter criteria.

**Query Parameters**

| Parameter    | Type    | Required | Description |
|-------------|---------|----------|-------------|
| `q`          | string  | No  | Keyword search across employee name, description, department, category |
| `status`     | string  | No  | Filter by exact status value |
| `priority`   | string  | No  | Filter by exact priority value |
| `category`   | string  | No  | Filter by exact category value |
| `department` | string  | No  | Partial match on department |
| `page`       | integer | No  | Page number, 1-based (default: 1) |
| `page_size`  | integer | No  | Results per page, max 100 (default: 20) |

**Example Request**
```
GET /api/tickets/search?q=vpn&status=Open&priority=High&page=1&page_size=10
```

**Response `200 OK`**
```json
{
  "total": 3,
  "page": 1,
  "page_size": 10,
  "tickets": [
    {
      "ticket_id": 1,
      "employee_name": "Alice Johnson",
      "department": "Engineering",
      "issue_category": "VPN Issue",
      "description": "Unable to connect to company VPN from home…",
      "priority": "High",
      "status": "Open",
      "resolution_notes": null,
      "created_at": "2026-05-17T10:30:00Z",
      "updated_at": "2026-05-17T10:30:00Z"
    }
  ]
}
```

---

### GET /api/tickets

Retrieve all tickets with pagination (newest first).

**Query Parameters**

| Parameter   | Type    | Required | Description |
|-------------|---------|----------|-------------|
| `page`      | integer | No  | Page number (default: 1) |
| `page_size` | integer | No  | Results per page, max 100 (default: 20) |

**Response `200 OK`**
```json
{
  "total": 18,
  "page": 1,
  "page_size": 20,
  "tickets": [ ... ]
}
```

---

### GET /api/tickets/{ticket_id}

Retrieve a single ticket by its ID.

**Path Parameters**

| Parameter   | Type    | Required | Description |
|-------------|---------|----------|-------------|
| `ticket_id` | integer | Yes | Unique ticket identifier |

**Response `200 OK`**
```json
{
  "ticket_id": 1,
  "employee_name": "Alice Johnson",
  "department": "Engineering",
  "issue_category": "VPN Issue",
  "description": "Unable to connect to company VPN from home office. Error: Authentication Failed.",
  "priority": "High",
  "status": "Open",
  "resolution_notes": null,
  "created_at": "2026-05-17T10:30:00Z",
  "updated_at": "2026-05-17T10:30:00Z"
}
```

**Response `404 Not Found`**
```json
{ "detail": "Ticket #999 was not found." }
```

---

### POST /api/tickets

Create a new support ticket. Status defaults to `Open`.

**Request Body**
```json
{
  "employee_name":  "Jane Doe",
  "department":     "Finance",
  "issue_category": "Password Reset",
  "description":    "My AD account is locked. Need urgent reset before budget meeting at 2pm.",
  "priority":       "Critical"
}
```

| Field            | Type   | Required | Constraints |
|-----------------|--------|----------|-------------|
| `employee_name`  | string | Yes | 2–150 characters |
| `department`     | string | Yes | 2–100 characters |
| `issue_category` | enum   | Yes | One of the valid category values |
| `description`    | string | Yes | 10–5000 characters |
| `priority`       | enum   | No  | Default: `Medium` |

**Response `201 Created`**
```json
{
  "ticket_id": 19,
  "employee_name": "Jane Doe",
  "department": "Finance",
  "issue_category": "Password Reset",
  "description": "My AD account is locked. Need urgent reset before budget meeting at 2pm.",
  "priority": "Critical",
  "status": "Open",
  "resolution_notes": null,
  "created_at": "2026-05-17T14:00:00Z",
  "updated_at": "2026-05-17T14:00:00Z"
}
```

---

### PUT /api/tickets/{ticket_id}

Partially update a ticket (PATCH semantics — only provided fields are changed).

**Path Parameters**

| Parameter   | Type    | Required | Description |
|-------------|---------|----------|-------------|
| `ticket_id` | integer | Yes | Unique ticket identifier |

**Request Body** *(all fields optional)*
```json
{
  "status":           "In Progress",
  "priority":         "High",
  "resolution_notes": "Investigating VPN authentication issue with network team."
}
```

| Field              | Type   | Constraints |
|-------------------|--------|-------------|
| `employee_name`    | string | 2–150 characters |
| `department`       | string | 2–100 characters |
| `issue_category`   | enum   | Valid category |
| `description`      | string | 10–5000 characters |
| `priority`         | enum   | Valid priority |
| `status`           | enum   | Valid status — must follow transition rules |
| `resolution_notes` | string | Max 5000 characters |

**Status Transition Rules**

| From | Allowed To |
|------|-----------|
| `Open` | `In Progress`, `Closed` |
| `In Progress` | `Resolved`, `Open`, `Closed` |
| `Resolved` | `Closed`, `Open` |
| `Closed` | *(terminal — no transitions)* |

**Response `200 OK`** — Updated ticket object

**Response `404 Not Found`**
```json
{ "detail": "Ticket #999 was not found." }
```

**Response `422 Unprocessable Entity`**
```json
{
  "detail": "Invalid status transition: 'Closed' → 'In Progress'. Allowed transitions from 'Closed': none (terminal state)"
}
```

---

### DELETE /api/tickets/{ticket_id}

Permanently delete a ticket by ID.

**Path Parameters**

| Parameter   | Type    | Required | Description |
|-------------|---------|----------|-------------|
| `ticket_id` | integer | Yes | Unique ticket identifier |

**Response `200 OK`**
```json
{
  "message": "Ticket #1 has been permanently deleted.",
  "ticket_id": 1
}
```

**Response `404 Not Found`**
```json
{ "detail": "Ticket #999 was not found." }
```

---

## Health Check

### GET /health

Returns server health status.

**Response `200 OK`**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "app": "Helpdesk Ticket Management System"
}
```

---

## Error Response Format

All error responses follow this structure:
```json
{
  "detail": "Human-readable error message."
}
```

Validation errors (422) return Pydantic error details:
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "description"],
      "msg": "String should have at least 10 characters",
      "input": "broken"
    }
  ]
}
```
