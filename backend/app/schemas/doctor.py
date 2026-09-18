from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DoctorResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    clinic_id: UUID

    name: str
    specialization: str
    license_number: str

    phone: str | None
    bio: str | None

    is_active: bool

    created_at: datetime
    updated_at: datetime


class DoctorListResponse(BaseModel):
    doctors: list[DoctorResponse]
    total: int