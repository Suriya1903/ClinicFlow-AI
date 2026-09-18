from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class PatientResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    clinic_id: UUID

    first_name: str
    last_name: str

    date_of_birth: date | None
    gender: str | None

    phone: str
    email: EmailStr | None

    address: str | None

    emergency_contact_name: str | None
    emergency_contact_phone: str | None

    blood_group: str | None
    medical_notes: str | None

    is_active: bool

    created_at: datetime
    updated_at: datetime


class PatientListResponse(BaseModel):
    patients: list[PatientResponse]
    total: int