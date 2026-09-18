from uuid import UUID

from fastapi import Request, Response

from backend.app.core.security import decode_access_token
from backend.app.db.session import SessionLocal
from backend.app.services.audit_service import AuditService


EXCLUDED_PATHS = {
    "/health",
    "/docs",
    "/openapi.json",
    "/redoc",
}


def get_resource_from_path(path: str) -> str:
    """
    Convert an API path into a logical resource name.
    """

    parts = [
        part
        for part in path.strip("/").split("/")
        if part
    ]

    if not parts:
        return "root"

    if parts[0] == "auth":
        return "authentication"

    return parts[0]


def get_resource_id_from_path(
    path: str,
) -> str | None:
    """
    Extract a likely resource identifier from an API path.

    UUID-like values are returned as resource IDs.
    """

    parts = [
        part
        for part in path.strip("/").split("/")
        if part
    ]

    for part in reversed(parts):
        try:
            UUID(part)
            return part
        except ValueError:
            continue

    return None


def get_action(
    method: str,
    path: str,
    status_code: int,
) -> str:
    """
    Generate a simple human-readable audit action.
    """

    if path == "/auth/login":
        return "login"

    if path == "/auth/login/form":
        return "login"

    if path == "/auth/logout":
        return "logout"

    if status_code >= 400:
        return "request_failed"

    action_map = {
        "GET": "view",
        "POST": "create",
        "PUT": "update",
        "PATCH": "update",
        "DELETE": "delete",
    }

    return action_map.get(
        method.upper(),
        "request",
    )


def extract_authenticated_identity(
    request: Request,
) -> tuple[UUID | None, UUID | None]:
    """
    Extract user_id and clinic_id from a valid JWT.

    Invalid or missing authentication is intentionally ignored
    here because unauthenticated requests should still be
    allowed to reach their normal API authentication handling.
    """

    authorization = request.headers.get(
        "Authorization"
    )

    if not authorization:
        return None, None

    scheme, _, token = authorization.partition(" ")

    if scheme.lower() != "bearer" or not token:
        return None, None

    try:
        payload = decode_access_token(token)

    except ValueError:
        return None, None

    user_id_value = payload.get("sub")
    clinic_id_value = payload.get("clinic_id")

    try:
        user_id = (
            UUID(user_id_value)
            if user_id_value
            else None
        )
    except ValueError:
        user_id = None

    try:
        clinic_id = (
            UUID(clinic_id_value)
            if clinic_id_value
            else None
        )
    except ValueError:
        clinic_id = None

    return user_id, clinic_id


async def audit_request(
    request: Request,
    call_next,
) -> Response:
    """
    Record API activity after the request completes.

    Audit logging must never break the actual API request.
    """

    if request.url.path in EXCLUDED_PATHS:
        return await call_next(request)

    response: Response

    try:
        response = await call_next(request)

    except Exception:
        # Record unexpected server failures when possible.
        try:
            user_id, clinic_id = (
                extract_authenticated_identity(
                    request
                )
            )

            db = SessionLocal()

            try:
                AuditService.create_log(
                    db,
                    clinic_id=clinic_id,
                    user_id=user_id,
                    action="request_failed",
                    resource=get_resource_from_path(
                        request.url.path
                    ),
                    resource_id=get_resource_id_from_path(
                        request.url.path
                    ),
                    method=request.method,
                    path=request.url.path,
                    status_code=500,
                    success=False,
                    ip_address=(
                        request.client.host
                        if request.client
                        else None
                    ),
                    user_agent=request.headers.get(
                        "User-Agent"
                    ),
                    metadata_json={
                        "exception": "unhandled_exception"
                    },
                )

            finally:
                db.close()

        except Exception:
            # Audit failures must never mask the original
            # application exception.
            pass

        raise

    # ------------------------------------------------------
    # Determine identity
    # ------------------------------------------------------

    user_id, clinic_id = (
        extract_authenticated_identity(
            request
        )
    )

    # ------------------------------------------------------
    # Determine audit information
    # ------------------------------------------------------

    status_code = response.status_code

    success = status_code < 400

    action = get_action(
        request.method,
        request.url.path,
        status_code,
    )

    resource = get_resource_from_path(
        request.url.path
    )

    resource_id = get_resource_id_from_path(
        request.url.path
    )

    # ------------------------------------------------------
    # Persist audit event
    # ------------------------------------------------------

    try:
        db = SessionLocal()

        try:
            AuditService.create_log(
                db,
                clinic_id=clinic_id,
                user_id=user_id,
                action=action,
                resource=resource,
                resource_id=resource_id,
                method=request.method,
                path=request.url.path,
                status_code=status_code,
                success=success,
                ip_address=(
                    request.client.host
                    if request.client
                    else None
                ),
                user_agent=request.headers.get(
                    "User-Agent"
                ),
                metadata_json={
                    "query_params": dict(
                        request.query_params
                    )
                },
            )

        finally:
            db.close()

    except Exception:
        # Never allow an audit database failure to break
        # the actual API response.
        pass

    return response