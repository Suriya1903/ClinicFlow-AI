from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.auth_dependencies import get_current_user
from backend.app.core.rbac import require_role
from backend.app.core.tenant import get_current_clinic_id
from backend.app.db.dependencies import get_db
from backend.app.models.appointment import Appointment
from backend.app.models.user import User, UserRole
from backend.app.schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentUpdate,
)
from backend.app.services.appointment_service import (
    AppointmentService,
)


router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"],
)


@router.post(
    "",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_appointment(
    appointment_data: AppointmentCreate,
    clinic_id: UUID = Depends(get_current_clinic_id),
    current_user: User = Depends(
        require_role(
            UserRole.ADMIN,
            UserRole.DOCTOR,
            UserRole.RECEPTIONIST,
        )
    ),
    db: Session = Depends(get_db),
):
    try:
        return AppointmentService.create_appointment(
            db=db,
            clinic_id=clinic_id,
            doctor_id=appointment_data.doctor_id,
            patient_id=appointment_data.patient_id,
            scheduled_at=appointment_data.scheduled_at,
            reason=appointment_data.reason,
            notes=appointment_data.notes,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=list[AppointmentResponse],
)
def list_appointments(
    clinic_id: UUID = Depends(get_current_clinic_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AppointmentService.get_appointments(
        db=db,
        clinic_id=clinic_id,
    )


@router.get(
    "/{appointment_id}",
    response_model=AppointmentResponse,
)
def get_appointment(
    appointment_id: UUID,
    clinic_id: UUID = Depends(get_current_clinic_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    appointment = AppointmentService.get_appointment(
        db=db,
        clinic_id=clinic_id,
        appointment_id=appointment_id,
    )

    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )

    return appointment


@router.put(
    "/{appointment_id}",
    response_model=AppointmentResponse,
)
def update_appointment(
    appointment_id: UUID,
    appointment_data: AppointmentUpdate,
    clinic_id: UUID = Depends(get_current_clinic_id),
    current_user: User = Depends(
        require_role(
            UserRole.ADMIN,
            UserRole.DOCTOR,
            UserRole.RECEPTIONIST,
        )
    ),
    db: Session = Depends(get_db),
):
    appointment = AppointmentService.get_appointment(
        db=db,
        clinic_id=clinic_id,
        appointment_id=appointment_id,
    )

    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )

    try:
        return AppointmentService.update_appointment(
            db=db,
            appointment=appointment,
            scheduled_at=appointment_data.scheduled_at,
            status=appointment_data.status,
            reason=appointment_data.reason,
            notes=appointment_data.notes,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{appointment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_appointment(
    appointment_id: UUID,
    clinic_id: UUID = Depends(get_current_clinic_id),
    current_user: User = Depends(
        require_role(UserRole.ADMIN)
    ),
    db: Session = Depends(get_db),
):
    appointment = AppointmentService.get_appointment(
        db=db,
        clinic_id=clinic_id,
        appointment_id=appointment_id,
    )

    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )

    AppointmentService.delete_appointment(
        db=db,
        appointment=appointment,
    )