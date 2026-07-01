"""
FinRelief AI — FastAPI application entry point.
Configures middleware, routers, event handlers, and exception handlers.
"""
import logging
from datetime import datetime, timezone

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.db.database import Base, engine

# Import all models so that SQLAlchemy registers them before create_all()
import app.models.user  # noqa: F401
import app.models.profile  # noqa: F401
import app.models.loan  # noqa: F401
import app.models.settlement  # noqa: F401
import app.models.negotiation  # noqa: F401
import app.models.ai_response  # noqa: F401
import app.models.activity_log  # noqa: F401

from app.api import auth, users, loans, analysis, settlement, letters, history

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Application factory
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "FinRelief AI is an AI-powered personal debt management platform for India. "
        "It helps users calculate optimal debt settlement amounts, generate professional "
        "negotiation letters, and build personalised financial recovery plans — "
        "powered by Google Gemini AI with a deterministic fallback engine."
    ),
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ─────────────────────────────────────────────────────────────────────────────
# CORS middleware
# ─────────────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────────────────────
# Startup event
# ─────────────────────────────────────────────────────────────────────────────


@app.on_event("startup")
def on_startup() -> None:
    """Create all database tables on first startup (SQLite / dev mode)."""
    logger.info("Starting up %s v%s …", settings.APP_NAME, settings.APP_VERSION)
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialised.")


# ─────────────────────────────────────────────────────────────────────────────
# Router registration  (all under /api prefix)
# ─────────────────────────────────────────────────────────────────────────────

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(loans.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(settlement.router, prefix="/api")
app.include_router(letters.router, prefix="/api")
app.include_router(history.router, prefix="/api")

# ─────────────────────────────────────────────────────────────────────────────
# Health check endpoints
# ─────────────────────────────────────────────────────────────────────────────


@app.get("/", tags=["Health"], summary="Root health check")
def root() -> dict:
    """Return basic service identification."""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/api/health", tags=["Health"], summary="API health check")
def health_check() -> dict:
    """Return detailed health status with a UTC timestamp."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "gemini_enabled": bool(settings.GEMINI_API_KEY),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Custom exception handlers
# ─────────────────────────────────────────────────────────────────────────────


@app.exception_handler(404)
async def not_found_handler(request: Request, exc) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": "Not Found",
            "message": f"The requested resource '{request.url.path}' does not exist.",
            "status_code": 404,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = []
    for error in exc.errors():
        errors.append(
            {
                "field": " -> ".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
        )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "One or more request fields failed validation.",
            "details": errors,
            "status_code": 422,
        },
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc) -> JSONResponse:
    logger.exception("Unhandled server error on %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later.",
            "status_code": 500,
        },
    )
