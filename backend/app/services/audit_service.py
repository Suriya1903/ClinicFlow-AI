from uuid import UUID

from sqlalchemy.orm import Session

from backend.app.models.audit_log import AuditLog


class AuditService:
    """
    Service responsible for creating audit records.
    """

    @staticmethod
    def create_log(
        db: Session,
        *,
        clinic_id: UUID | None,
        user_id: UUID | None,
        action: str,
        resource: str,
        resource_id: str | None,
        method: str,
        path: str,
        status_code: int,
        success: bool,
        ip_address: str | None = None,
        user_agent: str | None = None,
        metadata_json: dict | None = None,
    ) -> AuditLog:
        audit_log = AuditLog(
            clinic_id=clinic_id,
            user_id=user_id,
            action=action,
            resource=resource,
            resource_id=resource_id,
            method=method,
            path=path,
            status_code=status_code,
            success=success,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata_json=metadata_json,
        )

        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)

        return audit_log