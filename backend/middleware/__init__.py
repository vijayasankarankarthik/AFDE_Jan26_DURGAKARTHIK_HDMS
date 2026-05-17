"""
middleware package — Custom FastAPI/Starlette middleware.

RequestLoggingMiddleware:
  Logs every incoming request with method, path, status code, and duration.
  Useful for debugging, monitoring, and audit trails.

Usage (registered in main.py):
  from middleware import RequestLoggingMiddleware
  app.add_middleware(RequestLoggingMiddleware)
"""

from __future__ import annotations

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("helpdesk.requests")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs each HTTP request with method, URL, status code, and response time.
    Excludes health-check endpoints to reduce noise in production logs.
    """

    EXCLUDED_PATHS = {"/health", "/", "/docs", "/redoc", "/openapi.json"}

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)

        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000

        logger.info(
            "%s %s → %d  (%.1f ms)",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response
