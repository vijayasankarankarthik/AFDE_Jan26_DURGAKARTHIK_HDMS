"""
main.py — FastAPI application entry point.

Configures:
  - CORS middleware (production-ready, origins from .env)
  - Global exception handlers
  - API routers with versioned /api prefix
  - Startup / shutdown lifecycle events (auto table creation)
  - Swagger / ReDoc documentation
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import get_settings
from database import create_tables
from routers import tickets

# ─── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()


# ─── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup; clean up resources on shutdown."""
    logger.info("🚀  Helpdesk API starting — initialising database tables…")
    create_tables()
    logger.info("✅  Database tables ready.")
    yield
    logger.info("🛑  Helpdesk API shutting down.")


# ─── Application factory ───────────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "**Production-grade REST API** for the Helpdesk Ticket Management System.\n\n"
        "Manages employee support tickets with full CRUD, advanced search, "
        "filtering, pagination, and dashboard analytics.\n\n"
        "Built with FastAPI + SQLAlchemy + PostgreSQL. "
        "Architecture is AI/RAG-ready for Phase 2 enhancements."
    ),
    contact={
        "name": "Helpdesk Support",
        "email": "helpdesk@example.com",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# ─── CORS Middleware ───────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# ─── Global Exception Handlers ─────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled exception on %s %s: %s",
        request.method,
        request.url.path,
        exc,
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred. Please try again later.",
            "path": str(request.url.path),
        },
    )


# ─── Routers ───────────────────────────────────────────────────────────────────
app.include_router(tickets.router, prefix="/api", tags=["Tickets"])


# ─── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["System"], summary="Health check endpoint")
async def health_check():
    """Returns API health status. Used by load balancers and monitoring tools."""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "app": settings.app_name,
    }


# ─── Root ──────────────────────────────────────────────────────────────────────
@app.get("/", tags=["System"], summary="API root")
async def root():
    """API root with navigation links."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "documentation": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "api": "/api/tickets",
    }
