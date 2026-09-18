from fastapi import APIRouter, Depends
from uuid import UUID

from backend.app.core.tenant import get_current_clinic_id


router = APIRouter(
    prefix="/tenant-test",
    tags=["Tenant Test"],
)


@router.get("/clinic")
def get_my_clinic(
    clinic_id: UUID = Depends(get_current_clinic_id),
):
    return {
        "message": "Tenant identified successfully",
        "clinic_id": str(clinic_id),
    }