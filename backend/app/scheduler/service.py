from uuid import UUID

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from backend.app.db.session import SessionLocal
from backend.app.models.workflow_configuration import (
    WorkflowConfiguration,
    WorkflowScheduleType,
)
from backend.app.models.workflow_execution import WorkflowTriggerType
from backend.app.workflows.daily_summary import (
    run_daily_clinic_summary,
)


scheduler = AsyncIOScheduler()

SCHEDULER_TIMEZONE = "Asia/Kolkata"

WORKFLOW_JOB_PREFIX = "workflow_"

# If a scheduled execution is missed because the application
# was temporarily unavailable, APScheduler can execute it
# within this grace period after startup.
MISFIRE_GRACE_TIME_SECONDS = 300


def get_workflow_job_id(
    clinic_id: UUID,
    workflow_name: str,
) -> str:
    """
    Build a stable scheduler job ID.

    The combination of clinic ID and workflow name guarantees
    that workflows belonging to different clinics receive
    different scheduler jobs.
    """

    return (
        f"{WORKFLOW_JOB_PREFIX}"
        f"{clinic_id}_"
        f"{workflow_name}"
    )


async def run_configured_workflow(
    clinic_id: UUID,
    workflow_name: str,
) -> None:
    """
    Execute a configured workflow for a specific clinic.

    The workflow configuration is checked again immediately
    before execution.

    This protects against a workflow being disabled or changed
    after its scheduler job was registered.
    """

    db = SessionLocal()

    try:
        configuration = db.scalar(
            select(WorkflowConfiguration).where(
                WorkflowConfiguration.clinic_id == clinic_id,
                WorkflowConfiguration.workflow_name
                == workflow_name,
            )
        )

        if configuration is None:
            print(
                "[Scheduler] Configuration not found: "
                f"{workflow_name}"
            )
            return

        if not configuration.is_enabled:
            print(
                "[Scheduler] Workflow disabled. Skipping: "
                f"{workflow_name} "
                f"for clinic {clinic_id}"
            )
            return

        if (
            configuration.schedule_type
            != WorkflowScheduleType.DAILY
        ):
            print(
                "[Scheduler] Workflow is not configured "
                "for daily execution. Skipping: "
                f"{workflow_name}"
            )
            return

        if (
            configuration.schedule_hour is None
            or configuration.schedule_minute is None
        ):
            print(
                "[Scheduler] Workflow has an invalid schedule. "
                "Skipping: "
                f"{workflow_name}"
            )
            return

        print(
            "[Scheduler] Executing configured workflow: "
            f"{workflow_name} "
            f"for clinic {clinic_id}"
        )

        if workflow_name == "daily_clinic_summary":
            await run_daily_clinic_summary(
                db=db,
                clinic_id=clinic_id,
                trigger_type=WorkflowTriggerType.SCHEDULED,
            )

        else:
            print(
                "[Scheduler] No executor registered for "
                f"workflow: {workflow_name}"
            )

    except Exception as exc:
        print(
            "[Scheduler] Workflow execution failed: "
            f"{workflow_name} "
            f"for clinic {clinic_id}: {exc}"
        )

    finally:
        db.close()


def remove_workflow_jobs() -> None:
    """
    Remove all currently registered ClinicFlow workflow jobs.

    Only jobs using the ClinicFlow workflow prefix are removed.
    Other APScheduler jobs are left untouched.
    """

    existing_jobs = scheduler.get_jobs()

    removed_count = 0

    for job in existing_jobs:
        if job.id.startswith(
            WORKFLOW_JOB_PREFIX
        ):
            scheduler.remove_job(job.id)
            removed_count += 1

    if removed_count:
        print(
            "[Scheduler] Removed "
            f"{removed_count} existing workflow job(s)."
        )


def load_workflow_jobs() -> None:
    """
    Load enabled daily workflow configurations from the database
    and register them with APScheduler.
    """

    db = SessionLocal()

    try:
        configurations = list(
            db.scalars(
                select(WorkflowConfiguration)
                .where(
                    WorkflowConfiguration.is_enabled.is_(True),
                    WorkflowConfiguration.schedule_type
                    == WorkflowScheduleType.DAILY,
                )
                .order_by(
                    WorkflowConfiguration.clinic_id,
                    WorkflowConfiguration.workflow_name,
                )
            ).all()
        )

        print(
            "[Scheduler] Loading workflow configurations..."
        )

        registered_count = 0

        for configuration in configurations:
            if (
                configuration.schedule_hour is None
                or configuration.schedule_minute is None
            ):
                print(
                    "[Scheduler] Invalid schedule configuration. "
                    "Skipping: "
                    f"{configuration.workflow_name}"
                )
                continue

            job_id = get_workflow_job_id(
                clinic_id=configuration.clinic_id,
                workflow_name=configuration.workflow_name,
            )

            scheduler.add_job(
                run_configured_workflow,
                trigger="cron",
                hour=configuration.schedule_hour,
                minute=configuration.schedule_minute,
                timezone=SCHEDULER_TIMEZONE,
                id=job_id,
                replace_existing=True,
                coalesce=True,
                max_instances=1,
                misfire_grace_time=(
                    MISFIRE_GRACE_TIME_SECONDS
                ),
                kwargs={
                    "clinic_id": configuration.clinic_id,
                    "workflow_name": configuration.workflow_name,
                },
            )

            registered_count += 1

            print(
                "[Scheduler] Registered: "
                f"{configuration.display_name} "
                f"for "
                f"{configuration.schedule_hour:02d}:"
                f"{configuration.schedule_minute:02d} IST"
            )

        print(
            "[Scheduler] Loaded "
            f"{registered_count} workflow job(s)."
        )

    finally:
        db.close()


def start_scheduler() -> None:
    """
    Start APScheduler and load workflow configurations.

    Existing workflow jobs are removed first so repeated startup
    calls cannot create stale duplicate jobs.
    """

    if scheduler.running:
        return

    remove_workflow_jobs()

    load_workflow_jobs()

    scheduler.start()

    print(
        "[Scheduler] Started using database-driven "
        "workflow configuration."
    )


def reload_workflow_jobs() -> None:
    """
    Reload workflow jobs from the database.

    This is used after an administrator creates, updates,
    enables, or disables a workflow.

    If the scheduler is not running, no reload is necessary.
    Startup will load the current database configuration.
    """

    if not scheduler.running:
        return

    remove_workflow_jobs()

    load_workflow_jobs()

    print(
        "[Scheduler] Workflow jobs reloaded."
    )


def stop_scheduler() -> None:
    """
    Stop the application scheduler.
    """

    if not scheduler.running:
        return

    scheduler.shutdown(
        wait=False
    )

    print(
        "[Scheduler] Stopped."
    )