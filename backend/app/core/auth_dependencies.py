from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.security import decode_access_token
from backend.app.core.token_revocation import (
    token_revocation_store,
)
from backend.app.db.dependencies import get_db
from backend.app.models.user import User


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    ),
    db: Session = Depends(get_db),
) -> User:
    """
    Authenticate the current user from a JWT bearer token.

    Validation includes:

    - JWT signature
    - JWT expiration
    - Required JWT claims
    - Token type
    - Token revocation
    - User existence
    - User account status
    """

    token = credentials.credentials

    try:
        payload = decode_access_token(token)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        ) from exc

    # ======================================================
    # TOKEN REVOCATION
    # ======================================================

    token_id = payload.get("jti")

    if not token_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    if token_revocation_store.is_revoked(
        token_id
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token has been revoked",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    # ======================================================
    # USER IDENTIFICATION
    # ======================================================

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    try:
        user_uuid = UUID(user_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user identifier in token",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        ) from exc

    # ======================================================
    # USER LOOKUP
    # ======================================================

    user = db.scalar(
        select(User).where(
            User.id == user_uuid
        )
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    # ======================================================
    # ACCOUNT STATUS
    # ======================================================

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return user