from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import (
    Depends,
    FastAPI,
    Request,
)
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from prometheus_fastapi_instrumentator import Instrumentator

from backend.app.api.ai import router as ai_router
from backend.app.api.agent import router as agent_router
from backend.app.api.appointments import (
    router as appointments_router,
)
from backend.app.api.audit_logs import (
    router as audit_logs_router,
)
from backend.app.api.auth import router as auth_router
from backend.app.api.clinics import router as clinics_router
from backend.app.api.dashboard import (
    router as dashboard_router,
)
from backend.app.api.doctors import router as doctors_router
from backend.app.api.patients import router as patients_router
from backend.app.api.test_rbac import router as rbac_router
from backend.app.api.test_tenant import (
    router as tenant_router,
)
from backend.app.api.workflows import (
    router as workflows_router,
)
from backend.app.core.audit_middleware import audit_request
from backend.app.core.auth_dependencies import (
    get_current_user,
)
from backend.app.models.user import User
from backend.app.scheduler.service import (
    start_scheduler,
    stop_scheduler,
)
from mcp_server.server import mcp


# ==========================================================
# API HARDENING CONFIGURATION
# ==========================================================


MAX_REQUEST_BODY_SIZE = 1024 * 1024


# ==========================================================
# APPLICATION LIFESPAN
# ==========================================================


@asynccontextmanager
async def lifespan(
    app: FastAPI,
) -> AsyncIterator[None]:
    """
    Application startup and shutdown lifecycle.
    """

    async with mcp.session_manager.run():
        start_scheduler()

        try:
            yield

        finally:
            stop_scheduler()


# ==========================================================
# APPLICATION
# ==========================================================


app = FastAPI(
    title="ClinicFlow AI",
    description=(
        "AI-Powered Multi-Tenant Clinic Operations, "
        "Workflow Automation & Product Intelligence Platform"
    ),
    version="0.1.0",
    lifespan=lifespan,
)


# ==========================================================
# PROMETHEUS MONITORING
# ==========================================================


Instrumentator().instrument(app).expose(
    app,
    endpoint="/metrics",
    include_in_schema=False,
)


# ==========================================================
# VALIDATION ERROR HANDLER
# ==========================================================


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    """
    Return a controlled validation-error response.

    FastAPI normally returns its complete validation structure.
    ClinicFlow uses a stable top-level message while preserving
    the detailed validation errors under the `errors` field.
    """

    return JSONResponse(
        status_code=422,
        content={
            "detail": "Request validation failed",
            "errors": exc.errors(),
        },
    )


# ==========================================================
# CORS
# ==========================================================


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_origin_regex=(
        r"^https?://(localhost|127\.0\.0\.1):5173$"
    ),
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "PATCH",
        "OPTIONS",
    ],
    allow_headers=[
        "Accept",
        "Authorization",
        "Content-Type",
        "Origin",
        "X-Requested-With",
    ],
)


# ==========================================================
# REQUEST SIZE + CONTENT-LENGTH HARDENING
# ==========================================================


@app.middleware("http")
async def request_hardening_middleware(
    request: Request,
    call_next,
):
    """
    Apply basic HTTP request hardening.

    Checks:

    1. Content-Length must contain a valid non-negative integer.
    2. Requests larger than 1 MB are rejected before reaching
       the endpoint.
    """

    content_length = request.headers.get(
        "Content-Length"
    )

    if content_length is not None:
        try:
            content_length_value = int(
                content_length
            )

        except (TypeError, ValueError):
            return JSONResponse(
                status_code=400,
                content={
                    "detail": (
                        "Invalid Content-Length header"
                    )
                },
            )

        if content_length_value < 0:
            return JSONResponse(
                status_code=400,
                content={
                    "detail": (
                        "Invalid Content-Length header"
                    )
                },
            )

        if (
            content_length_value
            > MAX_REQUEST_BODY_SIZE
        ):
            return JSONResponse(
                status_code=413,
                content={
                    "detail": (
                        "Request body is too large. "
                        "Maximum allowed size is 1 MB."
                    )
                },
            )

    return await call_next(request)


# ==========================================================
# SECURITY HEADERS
# ==========================================================


@app.middleware("http")
async def add_security_headers(
    request: Request,
    call_next,
):
    """
    Add standard HTTP security headers to API responses.

    These headers reduce common browser-side risks such as:

    - MIME type sniffing
    - Clickjacking
    - Unnecessary referrer leakage
    - Unwanted browser capabilities
    """

    response: Response = await call_next(
        request
    )

    response.headers[
        "X-Content-Type-Options"
    ] = "nosniff"

    response.headers[
        "X-Frame-Options"
    ] = "DENY"

    response.headers[
        "Referrer-Policy"
    ] = "strict-origin-when-cross-origin"

    response.headers[
        "Permissions-Policy"
    ] = (
        "camera=(), "
        "microphone=(), "
        "geolocation=(), "
        "payment=(), "
        "usb=()"
    )

    if request.url.path.startswith(
        (
            "/auth",
            "/protected",
            "/patients",
            "/doctors",
            "/appointments",
            "/workflows",
            "/ai",
            "/dashboard",
            "/audit-logs",
        )
    ):
        response.headers[
            "Cache-Control"
        ] = "no-store, max-age=0"

    if (
        request.url.scheme == "https"
        and request.headers.get("host")
    ):
        response.headers[
            "Strict-Transport-Security"
        ] = (
            "max-age=31536000; includeSubDomains"
        )

    return response


# ==========================================================
# AUDIT LOGGING
# ==========================================================


app.middleware("http")(audit_request)


# ==========================================================
# ROUTERS
# ==========================================================


app.include_router(
    auth_router
)

app.include_router(
    clinics_router
)

app.include_router(
    doctors_router
)

app.include_router(
    patients_router
)

app.include_router(
    appointments_router
)

app.include_router(
    dashboard_router
)

app.include_router(
    ai_router
)

app.include_router(
    agent_router
)

app.include_router(
    workflows_router
)

app.include_router(
    rbac_router
)

app.include_router(
    tenant_router
)

app.include_router(
    audit_logs_router
)


# ==========================================================
# MCP
# ==========================================================


app.mount(
    "/mcp",
    mcp.streamable_http_app(
        streamable_http_path="/",
    ),
)


# ==========================================================
# ROOT
# ==========================================================


@app.get("/")
async def root():
    return {
        "application": "ClinicFlow AI",
        "status": "running",
        "version": "0.1.0",
    }


# ==========================================================
# HEALTH
# ==========================================================


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "clinicflow-api",
    }


# ==========================================================
# PROTECTED TEST ENDPOINT
# ==========================================================


@app.get("/protected")
async def protected_endpoint(
    current_user: User = Depends(
        get_current_user
    ),
):
    return {
        "message": "You are authenticated",
        "user_id": str(
            current_user.id
        ),
        "clinic_id": str(
            current_user.clinic_id
        ),
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role.value,
    }