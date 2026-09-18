from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from backend.app.core.auth_dependencies import get_current_user
from backend.app.core.tenant import get_current_clinic_id
from backend.app.db.dependencies import get_db
from backend.app.models.doctor import Doctor
from backend.app.models.user import User
from backend.app.schemas.doctor import (
    DoctorListResponse,
    DoctorResponse,
)


router = APIRouter(
    prefix="/doctors",
    tags=["Doctors"],
)


@router.get(
    "",
    response_model=DoctorListResponse,
)
def get_doctors(
    search: str | None = Query(
        default=None,
        max_length=150,
    ),
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    clinic_id: UUID = Depends(
        get_current_clinic_id
    ),
    current_user: User = Depends(
        get_current_user
    ),
):
    """
    Get doctors belonging to the authenticated
    user's clinic.
    """

    query = select(Doctor).where(
        Doctor.clinic_id == clinic_id
    )

    if not include_inactive:
        query = query.where(
            Doctor.is_active.is_(True)
        )

    if search:
        search_term = f"%{search.strip()}%"

        query = query.where(
            or_(
                Doctor.name.ilike(search_term),
                Doctor.specialization.ilike(
                    search_term
                ),
                Doctor.license_number.ilike(
                    search_term
                ),
                Doctor.phone.ilike(
                    search_term
                ),
            )
        )

    query = query.order_by(
        Doctor.name.asc()
    )

    doctors = list(
        db.scalars(query).all()
    )

    total_query = select(
        func.count(Doctor.id)
    ).where(
        Doctor.clinic_id == clinic_id
    )

    if not include_inactive:
        total_query = total_query.where(
            Doctor.is_active.is_(True)
        )

    if search:
        search_term = f"%{search.strip()}%"

        total_query = total_query.where(
            or_(
                Doctor.name.ilike(search_term),
                Doctor.specialization.ilike(
                    search_term
                ),
                Doctor.license_number.ilike(
                    search_term
                ),
                Doctor.phone.ilike(
                    search_term
                ),
            )
        )

    total = db.scalar(
        total_query
    ) or 0

    return DoctorListResponse(
        doctors=doctors,
        total=total,
    )


@router.get(
    "/{doctor_id}",
    response_model=DoctorResponse,
)
def get_doctor(
    doctor_id: UUID,
    db: Session = Depends(get_db),
    clinic_id: UUID = Depends(
        get_current_clinic_id
    ),
    current_user: User = Depends(
        get_current_user
    ),
):
    """
    Get one doctor belonging to the
    authenticated user's clinic.
    """

    doctor = db.scalar(
        select(Doctor).where(
            Doctor.id == doctor_id,
            Doctor.clinic_id == clinic_id,
        )
    )

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )

    return doctor