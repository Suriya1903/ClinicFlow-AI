from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from backend.app.core.auth_dependencies import get_current_user
from backend.app.core.tenant import get_current_clinic_id
from backend.app.db.dependencies import get_db
from backend.app.models.patient import Patient
from backend.app.models.user import User
from backend.app.schemas.patient import (
    PatientListResponse,
    PatientResponse,
)


router = APIRouter(
    prefix="/patients",
    tags=["Patients"],
)


@router.get(
    "",
    response_model=PatientListResponse,
)
def get_patients(
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
    Get patients belonging to the authenticated
    user's clinic.

    Tenant isolation is enforced using clinic_id.
    """

    query = select(Patient).where(
        Patient.clinic_id == clinic_id
    )

    if not include_inactive:
        query = query.where(
            Patient.is_active.is_(True)
        )

    if search:
        search_term = f"%{search.strip()}%"

        query = query.where(
            or_(
                Patient.first_name.ilike(
                    search_term
                ),
                Patient.last_name.ilike(
                    search_term
                ),
                Patient.phone.ilike(
                    search_term
                ),
                Patient.email.ilike(
                    search_term
                ),
            )
        )

    query = query.order_by(
        Patient.first_name.asc(),
        Patient.last_name.asc(),
    )

    patients = list(
        db.scalars(query).all()
    )

    total_query = select(
        func.count(Patient.id)
    ).where(
        Patient.clinic_id == clinic_id
    )

    if not include_inactive:
        total_query = total_query.where(
            Patient.is_active.is_(True)
        )

    if search:
        search_term = f"%{search.strip()}%"

        total_query = total_query.where(
            or_(
                Patient.first_name.ilike(
                    search_term
                ),
                Patient.last_name.ilike(
                    search_term
                ),
                Patient.phone.ilike(
                    search_term
                ),
                Patient.email.ilike(
                    search_term
                ),
            )
        )

    total = db.scalar(
        total_query
    ) or 0

    return PatientListResponse(
        patients=patients,
        total=total,
    )


@router.get(
    "/{patient_id}",
    response_model=PatientResponse,
)
def get_patient(
    patient_id: UUID,
    db: Session = Depends(get_db),
    clinic_id: UUID = Depends(
        get_current_clinic_id
    ),
    current_user: User = Depends(
        get_current_user
    ),
):
    """
    Get one patient belonging to the
    authenticated user's clinic.
    """

    patient = db.scalar(
        select(Patient).where(
            Patient.id == patient_id,
            Patient.clinic_id == clinic_id,
        )
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    return patient