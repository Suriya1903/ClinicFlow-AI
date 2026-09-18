from uuid import UUID

from fastapi import Depends

from backend.app.core.auth_dependencies import get_current_user
from backend.app.models.user import User


def get_current_clinic_id(
    current_user: User = Depends(get_current_user),
) -> UUID:
    """
    Return the clinic ID belonging to the authenticated user.

    This ensures that application code uses the tenant
    associated with the authenticated user instead of
    trusting a clinic ID supplied by the client.
    """
    return current_user.clinic_id