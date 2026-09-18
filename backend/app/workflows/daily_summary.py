import asyncio
from uuid import UUID

from sqlalchemy.orm import Session

from backend.app.ai.agent import run_agent
from backend.app.models.workflow_execution import WorkflowTriggerType
from backend.app.services.workflow_service import WorkflowService


DAILY_SUMMARY_WORKFLOW_NAME = "daily_clinic_summary"

WORKFLOW_TIMEOUT_SECONDS = 60


async def run_daily_clinic_summary(
    db: Session,
    clinic_id: UUID,
    trigger_type: WorkflowTriggerType = WorkflowTriggerType.MANUAL,
) -> str:
    """
    Execute the Daily Clinic Summary workflow.

    The workflow creates an execution record, runs the AI agent,
    stores the result, and marks the execution as completed or failed.

    A timeout prevents a workflow from remaining in RUNNING state
    indefinitely if the AI or an external service becomes unavailable.
    """

    workflow_service = WorkflowService(db)

    execution = workflow_service.create_execution(
        clinic_id=clinic_id,
        workflow_name=DAILY_SUMMARY_WORKFLOW_NAME,
        input_data={
            "request": "Generate today's clinic summary",
        },
        trigger_type=trigger_type,
    )

    workflow_service.mark_running(execution)

    try:
        response = await asyncio.wait_for(
            run_agent(
                message=(
                    "Give me today's clinic summary. "
                    "Include today's appointments and the "
                    "current active patient count."
                ),
                clinic_id=str(clinic_id),
            ),
            timeout=WORKFLOW_TIMEOUT_SECONDS,
        )

        workflow_service.mark_completed(
            execution,
            output_data={
                "summary": response,
            },
        )

        return response

    except asyncio.TimeoutError:
        error_message = (
            "Workflow timed out after "
            f"{WORKFLOW_TIMEOUT_SECONDS} seconds."
        )

        workflow_service.mark_failed(
            execution,
            error_message=error_message,
        )

        raise RuntimeError(error_message)

    except Exception as exc:
        workflow_service.mark_failed(
            execution,
            error_message=str(exc),
        )

        raise