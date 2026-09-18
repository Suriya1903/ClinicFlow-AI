from collections.abc import Callable

from fastapi import Depends, HTTPException, status

from backend.app.core.auth_dependencies import get_current_user
from backend.app.models.user import User, UserRole


def require_role(*allowed_roles: UserRole) -> Callable:
    """
    Create a FastAPI dependency that allows only
    users with one of the specified roles.
    """

    def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )

        return current_user

    return role_checker