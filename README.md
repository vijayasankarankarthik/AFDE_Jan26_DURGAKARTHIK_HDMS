# 🖥️ Helpdesk Ticket Management System

> **A production-grade, full-stack internal IT support portal built with FastAPI, React, and PostgreSQL.**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.2-61DAFB?style=flat-square&logo=react)](https://reactjs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791?style=flat-square&logo=postgresql)](https://postgresql.org)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-CC0000?style=flat-square)](https://sqlalchemy.org)

---

## 📌 Project Overview

Modern organizations handle hundreds of IT support requests daily — from VPN failures and password resets to hardware requests and software installations. Without a centralised system, these requests get lost in emails and chat threads, leading to:

- Delayed issue resolution
- No ticket tracking or visibility
- Duplicate work by support agents
- Zero historical data for trend analysis

The **Helpdesk Ticket Management System** solves this with a centralized web portal where employees can submit support tickets and IT support admins can manage, track, and resolve them efficiently.

This is a **Phase 1 implementation** focused on core ticket management. The architecture is designed to support **Phase 2 AI/RAG enhancements** including semantic search, automatic ticket classification, and predictive analytics.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎫 **Create Tickets** | Employees submit detailed support requests with category, priority, and description |
| 📋 **View & List Tickets** | Paginated table view of all tickets with sortable columns |
| 🔍 **Search & Filter** | Keyword search + filter by status, priority, and category |
| ✏️ **Update Tickets** | Support admins update status, priority, and resolution notes inline |
| 🗑️ **Delete Tickets** | Permanent deletion with confirmation guard |
| 📊 **Dashboard** | Real-time stats: totals by status, priority distribution, recent tickets |
| 🔄 **Status Transitions** | Enforced workflow rules (Open → In Progress → Resolved → Closed) |
| 📖 **API Documentation** | Auto-generated Swagger UI and ReDoc at `/docs` and `/redoc` |

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** — High-performance async Python web framework
- **SQLAlchemy 2.x** — ORM with connection pooling (pool_size=10)
- **Pydantic v2** — Request validation, response serialization, settings management
- **PostgreSQL** — Production-grade relational database
- **psycopg2-binary** — PostgreSQL adapter
- **Alembic** — Database migrations
- **Uvicorn** — ASGI server

### Frontend
- **React 18** — Functional components with Hooks
- **React Router v6** — Client-side routing
- **Axios** — HTTP client with interceptors
- **CSS Custom Properties** — Design system tokens (no external UI framework)

### Database
- **PostgreSQL** — Enforced CHECK constraints, B-tree indexes, auto-update triggers
- **pgAdmin** — Visual database management

---

## 📁 Project Structure

```
helpdesk-ticketing-system/
│
├── backend/
│   ├── main.py                  ← FastAPI app, middleware, lifespan
│   ├── config.py                ← pydantic-settings (env-based config)
│   ├── database.py              ← Engine, session factory, Base
│   ├── models.py                ← SQLAlchemy ORM models
│   ├── schemas.py               ← Pydantic request/response models
│   ├── crud.py                  ← Database CRUD operations
│   ├── requirements.txt
│   ├── .env.example
│   ├── routers/
│   │   └── tickets.py           ← REST API route handlers
│   ├── services/
│   │   └── ticket_service.py    ← Business logic layer
│   ├── utils/
│   │   └── validators.py        ← Input validators, helpers
│   └── middleware/
│       └── __init__.py          ← Request logging middleware
│
├── frontend/
│   ├── package.json
│   ├── public/
│   │   └── index.html
│   └── src/
│       ├── App.js               ← Routes and layout
│       ├── index.js             ← React DOM entry point
│       ├── api.js               ← Axios instance
│       ├── components/
│       │   ├── Sidebar.js
│       │   ├── Navbar.js
│       │   ├── StatusBadge.js
│       │   ├── PriorityBadge.js
│       │   ├── StatCard.js
│       │   ├── TicketTable.js
│       │   ├── SearchBar.js
│       │   ├── FilterPanel.js
│       │   └── LoadingSpinner.js
│       ├── pages/
│       │   ├── Dashboard.js
│       │   ├── TicketList.js
│       │   ├── CreateTicket.js
│       │   └── TicketDetail.js
│       ├── services/
│       │   └── ticketService.js ← All API methods
│       ├── hooks/
│       │   ├── useTickets.js    ← Paginated ticket fetching hook
│       │   └── useDebounce.js   ← Search debounce hook
│       └── styles/
│           ├── globals.css      ← Design tokens, reset, utilities
│           ├── components.css   ← Shared component styles
│           ├── Dashboard.css
│           ├── TicketList.css
│           ├── TicketDetail.css
│           └── CreateTicket.css
│
├── database/
│   ├── init.sql                 ← Schema DDL (tables, indexes, triggers)
│   └── seed.sql                 ← 18 realistic sample tickets
│
├── docs/
│   ├── api_documentation.md     ← Full REST API reference
│   └── architecture.md          ← Architecture decisions and diagrams
│
├── screenshots/                 ← UI screenshots (add yours here)
│
├── README.md
├── requirements.txt
└── .gitignore
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- pgAdmin 4 (recommended) or `psql`
- Git

---

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/yourusername/helpdesk-ticketing-system.git
cd helpdesk-ticketing-system
```

---

## 2️⃣ PostgreSQL Setup with pgAdmin

### Option A: Using pgAdmin (Recommended)

1. Open **pgAdmin 4** and connect to your PostgreSQL server.
2. Right-click **Databases** → **Create** → **Database**.
3. Set database name to `helpdesk_db`, owner to `postgres`, click **Save**.
4. Click on `helpdesk_db` → **Query Tool**.
5. Open `database/init.sql`, copy the contents (excluding the `CREATE DATABASE` line since the DB already exists), paste into Query Tool, and click **▶ Execute**.
6. Open `database/seed.sql`, paste into a new Query Tool tab, and execute to load sample data.

### Option B: Using psql CLI

```bash
# Create the database
psql -U postgres -c "CREATE DATABASE helpdesk_db;"

# Run schema creation (connect to helpdesk_db first)
psql -U postgres -d helpdesk_db -f database/init.sql

# Load sample data
psql -U postgres -d helpdesk_db -f database/seed.sql
```

---

## 3️⃣ Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate          # Linux/macOS
venv\Scripts\activate             # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
```

Edit `backend/.env` with your PostgreSQL credentials:
```env
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/helpdesk_db
DEBUG=true
ALLOWED_ORIGINS=http://localhost:3000
```

```bash
# Start the backend server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Base:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health check:** http://localhost:8000/health

> **Note:** The backend automatically creates database tables on startup using SQLAlchemy's `create_all()`. If you ran `init.sql` manually, the tables already exist and this is a no-op.

---

## 4️⃣ Frontend Setup

```bash
# From project root
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

The React app will open at **http://localhost:3000**.

The `proxy` field in `frontend/package.json` is set to `http://localhost:8000`, so all `/api/*` requests are forwarded to FastAPI automatically during development.

---

## 5️⃣ Verify Setup

1. Open http://localhost:3000 — you should see the **Dashboard** with ticket statistics.
2. Open http://localhost:8000/docs — you should see the **Swagger UI** with all endpoints.
3. Open pgAdmin and query `SELECT COUNT(*) FROM tickets;` — should return 18 (seed data).

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/tickets/stats` | Dashboard statistics |
| `GET` | `/api/tickets/search` | Search & filter tickets |
| `GET` | `/api/tickets` | List all tickets (paginated) |
| `GET` | `/api/tickets/{id}` | Get ticket by ID |
| `POST` | `/api/tickets` | Create a new ticket |
| `PUT` | `/api/tickets/{id}` | Update a ticket |
| `DELETE` | `/api/tickets/{id}` | Delete a ticket |
| `GET` | `/health` | Server health check |

### Example: Create a Ticket
```bash
curl -X POST http://localhost:8000/api/tickets \
  -H "Content-Type: application/json" \
  -d '{
    "employee_name": "John Smith",
    "department": "Sales",
    "issue_category": "VPN Issue",
    "description": "Cannot connect to VPN since last Windows update. Error code 800.",
    "priority": "High"
  }'
```

### Example: Search Tickets
```bash
curl "http://localhost:8000/api/tickets/search?q=vpn&status=Open&priority=High"
```

Full API documentation: [docs/api_documentation.md](docs/api_documentation.md)

---

## 🎯 Ticket Categories

| Category | Description |
|----------|-------------|
| VPN Issue | Remote access and VPN connectivity problems |
| Password Reset | Account lockouts and password changes |
| Software Installation | Application install and license requests |
| Laptop Issue | Hardware and device problems |
| Email Access | Email client and mailbox issues |
| Network Connectivity | Network, internet, and LAN problems |
| Hardware Request | New equipment procurement requests |
| Other | Miscellaneous IT support requests |

---

## 🔄 Status Workflow

```
Open  →  In Progress  →  Resolved  →  Closed
  ↑             ↓              ↓
  └─────────────┴──────────────┘  (re-open)
```

---

## 📸 Screenshots

> Add screenshots of your running application here.

Place screenshot files in the `screenshots/` directory and update the links below:

| Page | Screenshot |
|------|-----------|
| Dashboard | `screenshots/dashboard.png` |
| Ticket List | `screenshots/ticket-list.png` |
| Create Ticket | `screenshots/create-ticket.png` |
| Ticket Detail | `screenshots/ticket-detail.png` |

---

## 🔮 Future Enhancements (Phase 2)

- [ ] **JWT Authentication** — Employee and admin role separation with secure login
- [ ] **AI Ticket Classification** — Automatic category and priority suggestion using OpenAI
- [ ] **Semantic Search (RAG)** — pgvector + embeddings for intelligent ticket search
- [ ] **Email Notifications** — Automated emails on ticket create, update, and close
- [ ] **Real-time Updates** — WebSocket-based live ticket status updates
- [ ] **Analytics Dashboard** — Trend charts, resolution time metrics, agent performance
- [ ] **CSV/Excel Export** — Export filtered ticket data for reporting
- [ ] **Audit Log** — Track all changes to tickets with timestamps and actor

---

## 🐛 Troubleshooting

### Backend: `psycopg2.OperationalError: could not connect to server`
- Ensure PostgreSQL is running: `sudo service postgresql start`
- Verify `DATABASE_URL` in `backend/.env` is correct
- Confirm the `helpdesk_db` database exists in pgAdmin

### Backend: `ModuleNotFoundError`
- Ensure your virtual environment is activated: `source venv/bin/activate`
- Re-run: `pip install -r requirements.txt`

### Frontend: `Network Error` on API calls
- Ensure the backend is running on port 8000
- Check that `frontend/package.json` proxy is set to `http://localhost:8000`
- Verify CORS `allowed_origins` in `backend/.env` includes `http://localhost:3000`

### pgAdmin: Permission denied on `init.sql`
- Run the `CREATE DATABASE` statement separately as a superuser
- Skip that line when running the rest of the file against `helpdesk_db`

### Port already in use
```bash
# Kill process on port 8000 (backend)
lsof -ti:8000 | xargs kill -9

# Kill process on port 3000 (frontend)
lsof -ti:3000 | xargs kill -9
```

---

## 🧑‍💻 Development Commands

```bash
# Backend — run with hot reload
cd backend && uvicorn main:app --reload

# Backend — run tests
cd backend && pytest

# Frontend — development server
cd frontend && npm start

# Frontend — production build
cd frontend && npm run build

# Database — connect via psql
psql -U postgres -d helpdesk_db
```

---

## 📄 License

This project is for portfolio and educational demonstration purposes.

---

## 🤝 Author

Built as a Phase 1 capstone project demonstrating:
- Enterprise full-stack architecture
- REST API design best practices
- PostgreSQL + ORM integration
- Modern React patterns
- Production-ready code quality

> Architecture is intentionally designed for AI/RAG expansion in Phase 2.
