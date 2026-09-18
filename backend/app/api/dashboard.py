from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.auth_dependencies import get_current_user
from backend.app.core.tenant import get_current_clinic_id
from backend.app.db.dependencies import get_db
from backend.app.models.user import User
from backend.app.schemas.dashboard import DashboardResponse
from backend.app.services.dashboard_service import DashboardService


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "",
    response_model=DashboardResponse,
)
def get_dashboard(
    clinic_id: UUID = Depends(get_current_clinic_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return DashboardService.get_dashboard(
            db=db,
            clinic_id=clinic_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc