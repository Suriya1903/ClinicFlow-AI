from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from backend.app.models.appointment import AppointmentStatus


class AppointmentCreate(BaseModel):
    doctor_id: UUID
    patient_id: UUID

    scheduled_at: datetime

    reason: str | None = Field(
        default=None,
        max_length=255,
    )

    notes: str | None = None


class AppointmentUpdate(BaseModel):
    scheduled_at: datetime | None = None

    status: AppointmentStatus | None = None

    reason: str | None = Field(
        default=None,
        max_length=255,
    )

    notes: str | None = None


class AppointmentResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    clinic_id: UUID

    doctor_id: UUID
    patient_id: UUID

    scheduled_at: datetime

    status: AppointmentStatus

    reason: str | None
    notes: str | None

    created_at: datetime
    updated_at: datetime