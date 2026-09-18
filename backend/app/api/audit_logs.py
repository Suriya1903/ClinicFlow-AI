from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.auth_dependencies import get_current_user
from backend.app.core.rbac import require_role
from backend.app.core.tenant import get_current_clinic_id
from backend.app.db.dependencies import get_db
from backend.app.models.audit_log import AuditLog
from backend.app.models.user import User, UserRole


router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"],
)


@router.get("")
def get_audit_logs(
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
    action: str | None = Query(
        default=None,
        max_length=100,
    ),
    clinic_id: UUID = Depends(
        get_current_clinic_id
    ),
    current_user: User = Depends(
        require_role(UserRole.ADMIN)
    ),
    db: Session = Depends(get_db),
):
    """
    Retrieve audit logs for the authenticated
    administrator's clinic.

    Only clinic administrators can access audit logs.
    """

    query = (
        select(AuditLog)
        .where(
            AuditLog.clinic_id == clinic_id
        )
        .order_by(
            AuditLog.created_at.desc()
        )
        .limit(limit)
    )

    if action:
        query = query.where(
            AuditLog.action == action
        )

    logs = list(
        db.scalars(query).all()
    )

    return {
        "total": len(logs),
        "logs": [
            {
                "id": str(log.id),
                "clinic_id": (
                    str(log.clinic_id)
                    if log.clinic_id
                    else None
                ),
                "user_id": (
                    str(log.user_id)
                    if log.user_id
                    else None
                ),
                "action": log.action,
                "resource": log.resource,
                "resource_id": log.resource_id,
                "method": log.method,
                "path": log.path,
                "status_code": log.status_code,
                "success": log.success,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "metadata": log.metadata_json,
                "created_at": log.created_at,
            }
            for log in logs
        ],
    }