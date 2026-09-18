from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordRequestForm,
)
from sqlalchemy.orm import Session

from backend.app.core.auth_dependencies import (
    get_current_user,
)
from backend.app.core.rate_limit import (
    login_rate_limiter,
)
from backend.app.core.security import (
    decode_access_token,
)
from backend.app.core.token_revocation import (
    token_revocation_store,
)
from backend.app.db.dependencies import get_db
from backend.app.models.user import User
from backend.app.schemas.auth import (
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from backend.app.services.auth_service import (
    AuthService,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


security = HTTPBearer()


# ==========================================================
# LOGIN RATE LIMITING
# ==========================================================


def get_client_identifier(
    request: Request,
) -> str:
    """
    Get the identifier used for login rate limiting.

    The direct client address is used by default.

    X-Test-Client-IP is supported only for automated tests
    so tests can explicitly control the client identity.
    """

    test_client_ip = request.headers.get(
        "X-Test-Client-IP"
    )

    if test_client_ip:
        return test_client_ip.strip()

    if request.client is None:
        return "unknown-client"

    host = request.client.host

    if not host:
        return "unknown-client"

    return host


def check_login_rate_limit(
    request: Request,
) -> str:
    """
    Check whether the client is currently blocked.

    Returns the client identifier so the login endpoint can
    record success or failure against the same identifier.
    """

    identifier = get_client_identifier(
        request
    )

    if login_rate_limiter.is_blocked(
        identifier
    ):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                "Too many failed login attempts. "
                "Please try again later."
            ),
            headers={
                "Retry-After": "60",
            },
        )

    return identifier


# ==========================================================
# REGISTER
# ==========================================================


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user_data: UserRegister,
    db: Session = Depends(get_db),
):
    try:
        user = AuthService.register_user(
            db=db,
            name=user_data.name,
            email=user_data.email,
            password=user_data.password,
            clinic_id=user_data.clinic_id,
        )

        return user

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ==========================================================
# JSON LOGIN
# ==========================================================


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    request: Request,
    user_data: UserLogin,
    db: Session = Depends(get_db),
):
    identifier = check_login_rate_limit(
        request
    )

    try:
        user = AuthService.authenticate_user(
            db=db,
            email=user_data.email,
            password=user_data.password,
        )

        token = AuthService.create_user_token(
            user
        )

        login_rate_limiter.reset(
            identifier
        )

        return TokenResponse(
            access_token=token,
            token_type="bearer",
        )

    except ValueError as exc:
        login_rate_limiter.record_failure(
            identifier
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={
                "WWW-Authenticate": "Bearer"
            },
        ) from exc


# ==========================================================
# OAUTH2 FORM LOGIN
# ==========================================================


@router.post(
    "/login/form",
    response_model=TokenResponse,
)
def login_form(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    OAuth2-compatible login endpoint.

    FastAPI Swagger's Authorize button uses this format.
    """

    identifier = check_login_rate_limit(
        request
    )

    try:
        user = AuthService.authenticate_user(
            db=db,
            email=form_data.username,
            password=form_data.password,
        )

        token = AuthService.create_user_token(
            user
        )

        login_rate_limiter.reset(
            identifier
        )

        return TokenResponse(
            access_token=token,
            token_type="bearer",
        )

    except ValueError as exc:
        login_rate_limiter.record_failure(
            identifier
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={
                "WWW-Authenticate": "Bearer"
            },
        ) from exc


# ==========================================================
# LOGOUT
# ==========================================================


@router.post(
    "/logout",
)
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    ),
    current_user: User = Depends(
        get_current_user
    ),
):
    """
    Revoke the currently authenticated JWT.

    The JWT's unique jti is placed into the revocation
    store until the original token expiration time.

    After logout, the same JWT cannot be used again.
    """

    token = credentials.credentials

    try:
        payload = decode_access_token(
            token
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        ) from exc

    token_id = payload.get("jti")

    if not token_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    expiration = payload.get("exp")

    if not isinstance(
        expiration,
        (int, float),
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token expiration",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    now_timestamp = (
        datetime.now(
            timezone.utc
        ).timestamp()
    )

    remaining_seconds = max(
        0,
        int(
            expiration
            - now_timestamp
        ),
    )

    token_revocation_store.revoke(
        token_id=token_id,
        expires_in_seconds=remaining_seconds,
    )

    return {
        "message": "Successfully logged out",
        "user_id": str(
            current_user.id
        ),
    }