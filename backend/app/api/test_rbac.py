from fastapi import APIRouter, Depends

from backend.app.core.rbac import require_role
from backend.app.models.user import User, UserRole


router = APIRouter(
    prefix="/rbac-test",
    tags=["RBAC Test"],
)


@router.get("/admin")
def admin_only(
    current_user: User = Depends(
        require_role(UserRole.ADMIN)
    ),
):
    return {
        "message": "Admin access granted",
        "user": current_user.name,
        "role": current_user.role.value,
    }


@router.get("/doctor")
def doctor_only(
    current_user: User = Depends(
        require_role(UserRole.DOCTOR, UserRole.ADMIN)
    ),
):
    return {
        "message": "Doctor access granted",
        "user": current_user.name,
        "role": current_user.role.value,
    }


@router.get("/receptionist")
def receptionist_access(
    current_user: User = Depends(
        require_role(
            UserRole.RECEPTIONIST,
            UserRole.DOCTOR,
            UserRole.ADMIN,
        )
    ),
):
    return {
        "message": "Clinic staff access granted",
        "user": current_user.name,
        "role": current_user.role.value,
    }