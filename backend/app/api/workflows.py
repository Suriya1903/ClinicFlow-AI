from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.core.auth_dependencies import get_current_user
from backend.app.core.rbac import require_role
from backend.app.core.tenant import get_current_clinic_id
from backend.app.db.dependencies import get_db
from backend.app.models.user import User, UserRole
from backend.app.models.workflow_execution import (
    WorkflowExecutionStatus,
    WorkflowTriggerType,
)
from backend.app.schemas.agent import AgentResponse
from backend.app.schemas.workflow import (
    WorkflowExecutionListResponse,
    WorkflowExecutionResponse,
)
from backend.app.schemas.workflow_configuration import (
    WorkflowConfigurationCreate,
    WorkflowConfigurationResponse,
    WorkflowConfigurationUpdate,
)
from backend.app.scheduler.service import reload_workflow_jobs
from backend.app.services.workflow_service import WorkflowService
from backend.app.workflows.daily_summary import run_daily_clinic_summary


router = APIRouter(
    prefix="/workflows",
    tags=["Workflows"],
)


# ============================================================
# WORKFLOW EXECUTION
# ============================================================


@router.post(
    "/daily-summary",
    response_model=AgentResponse,
)
async def execute_daily_summary_workflow(
    db: Session = Depends(get_db),
    clinic_id=Depends(get_current_clinic_id),
    current_user: User = Depends(get_current_user),
):
    """
    Execute the Daily Clinic Summary workflow
    for the authenticated user's clinic.
    """

    try:
        summary = await run_daily_clinic_summary(
            db=db,
            clinic_id=clinic_id,
        )

        return AgentResponse(
            response=summary,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Workflow execution failed: {exc}",
        ) from exc


@router.get(
    "/history",
    response_model=WorkflowExecutionListResponse,
)
async def get_workflow_history(
    page: int = Query(
        default=1,
        ge=1,
        description="Page number",
    ),
    page_size: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Number of executions per page",
    ),
    status: WorkflowExecutionStatus | None = Query(
        default=None,
        description="Filter by workflow execution status",
    ),
    workflow_name: str | None = Query(
        default=None,
        min_length=1,
        max_length=150,
        description="Filter by workflow name",
    ),
    trigger_type: WorkflowTriggerType | None = Query(
        default=None,
        description="Filter by workflow trigger type",
    ),
    db: Session = Depends(get_db),
    clinic_id=Depends(get_current_clinic_id),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve workflow execution history
    for the authenticated user's clinic.

    Supports filtering by:
    - status
    - workflow name
    - trigger type
    """

    try:
        workflow_service = WorkflowService(db)

        (
            executions,
            total,
            total_pages,
        ) = workflow_service.get_execution_history(
            clinic_id=clinic_id,
            page=page,
            page_size=page_size,
            status=status,
            workflow_name=workflow_name,
            trigger_type=trigger_type,
        )

        return WorkflowExecutionListResponse(
            items=[
                WorkflowExecutionResponse.model_validate(
                    execution
                )
                for execution in executions
            ],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to retrieve workflow history: "
                f"{exc}"
            ),
        ) from exc


# ============================================================
# WORKFLOW CONFIGURATION
# ============================================================


@router.post(
    "/configurations",
    response_model=WorkflowConfigurationResponse,
    status_code=201,
)
def create_workflow_configuration(
    request: WorkflowConfigurationCreate,
    db: Session = Depends(get_db),
    clinic_id=Depends(get_current_clinic_id),
    current_user: User = Depends(
        require_role(UserRole.ADMIN)
    ),
):
    """
    Create a workflow configuration
    for the authenticated user's clinic.

    Only clinic administrators can create
    workflow configurations.
    """

    workflow_service = WorkflowService(db)

    try:
        configuration = (
            workflow_service.create_workflow_configuration(
                clinic_id=clinic_id,
                data=request,
            )
        )

        # Reload scheduler jobs so the newly created
        # configuration becomes active immediately.
        reload_workflow_jobs()

        return WorkflowConfigurationResponse.model_validate(
            configuration
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.get(
    "/configurations",
    response_model=list[WorkflowConfigurationResponse],
)
def get_workflow_configurations(
    db: Session = Depends(get_db),
    clinic_id=Depends(get_current_clinic_id),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve all workflow configurations
    belonging to the authenticated user's clinic.
    """

    workflow_service = WorkflowService(db)

    configurations = (
        workflow_service.get_workflow_configurations(
            clinic_id=clinic_id,
        )
    )

    return [
        WorkflowConfigurationResponse.model_validate(
            configuration
        )
        for configuration in configurations
    ]


@router.get(
    "/configurations/{configuration_id}",
    response_model=WorkflowConfigurationResponse,
)
def get_workflow_configuration(
    configuration_id: UUID,
    db: Session = Depends(get_db),
    clinic_id=Depends(get_current_clinic_id),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve one workflow configuration
    belonging to the authenticated user's clinic.
    """

    workflow_service = WorkflowService(db)

    configuration = (
        workflow_service.get_workflow_configuration(
            clinic_id=clinic_id,
            configuration_id=configuration_id,
        )
    )

    if configuration is None:
        raise HTTPException(
            status_code=404,
            detail="Workflow configuration not found",
        )

    return WorkflowConfigurationResponse.model_validate(
        configuration
    )


@router.put(
    "/configurations/{configuration_id}",
    response_model=WorkflowConfigurationResponse,
)
def update_workflow_configuration(
    configuration_id: UUID,
    request: WorkflowConfigurationUpdate,
    db: Session = Depends(get_db),
    clinic_id=Depends(get_current_clinic_id),
    current_user: User = Depends(
        require_role(UserRole.ADMIN)
    ),
):
    """
    Update a workflow configuration.

    Only clinic administrators can update
    workflow configurations.
    """

    workflow_service = WorkflowService(db)

    try:
        configuration = (
            workflow_service.update_workflow_configuration(
                clinic_id=clinic_id,
                configuration_id=configuration_id,
                data=request,
            )
        )

        if configuration is None:
            raise HTTPException(
                status_code=404,
                detail="Workflow configuration not found",
            )

        # Reload scheduler jobs so changes to
        # enable/disable status or schedule time
        # take effect immediately.
        reload_workflow_jobs()

        return WorkflowConfigurationResponse.model_validate(
            configuration
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc