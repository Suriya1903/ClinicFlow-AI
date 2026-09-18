from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.auth_dependencies import get_current_user
from backend.app.core.rbac import require_role
from backend.app.core.tenant import get_current_clinic_id
from backend.app.db.dependencies import get_db
from backend.app.models.user import User, UserRole
from backend.app.schemas.clinic import (
    ClinicCreate,
    ClinicResponse,
    ClinicUpdate,
)
from backend.app.services.clinic_service import ClinicService


router = APIRouter(
    prefix="/clinics",
    tags=["Clinics"],
)


@router.post(
    "",
    response_model=ClinicResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_clinic(
    clinic_data: ClinicCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new clinic and its initial administrator.

    This endpoint represents the initial SaaS onboarding flow.
    """

    try:
        clinic, admin = ClinicService.create_clinic(
            db=db,
            clinic_name=clinic_data.clinic_name,
            slug=clinic_data.slug,
            admin_name=clinic_data.admin_name,
            admin_email=clinic_data.admin_email,
            admin_password=clinic_data.admin_password,
        )

        return clinic

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/me",
    response_model=ClinicResponse,
)
def get_my_clinic(
    clinic_id: UUID = Depends(get_current_clinic_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return the clinic belonging to the authenticated user.
    """

    clinic = ClinicService.get_clinic(
        db=db,
        clinic_id=clinic_id,
    )

    if clinic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinic not found",
        )

    return clinic


@router.put(
    "/me",
    response_model=ClinicResponse,
)
def update_my_clinic(
    clinic_data: ClinicUpdate,
    clinic_id: UUID = Depends(get_current_clinic_id),
    current_user: User = Depends(
        require_role(UserRole.ADMIN)
    ),
    db: Session = Depends(get_db),
):
    """
    Update the authenticated administrator's clinic.
    """

    clinic = ClinicService.get_clinic(
        db=db,
        clinic_id=clinic_id,
    )

    if clinic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinic not found",
        )

    try:
        return ClinicService.update_clinic(
            db=db,
            clinic=clinic,
            name=clinic_data.name,
            slug=clinic_data.slug,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc