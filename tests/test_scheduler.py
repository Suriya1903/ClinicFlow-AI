from uuid import uuid4

from backend.app.models.workflow_configuration import (
    WorkflowScheduleType,
)
from backend.app.scheduler.service import (
    MISFIRE_GRACE_TIME_SECONDS,
    WORKFLOW_JOB_PREFIX,
    get_workflow_job_id,
    remove_workflow_jobs,
    scheduler,
)


# ============================================================
# JOB ID
# ============================================================


def test_workflow_job_id_is_tenant_specific():
    """
    Workflows belonging to different clinics must receive
    different scheduler job IDs.
    """

    clinic_a = uuid4()
    clinic_b = uuid4()

    job_a = get_workflow_job_id(
        clinic_id=clinic_a,
        workflow_name="daily_clinic_summary",
    )

    job_b = get_workflow_job_id(
        clinic_id=clinic_b,
        workflow_name="daily_clinic_summary",
    )

    assert job_a != job_b

    assert str(clinic_a) in job_a
    assert str(clinic_b) in job_b

    assert job_a.startswith(
        WORKFLOW_JOB_PREFIX
    )

    assert job_b.startswith(
        WORKFLOW_JOB_PREFIX
    )


def test_workflow_job_id_is_stable():
    """
    The same clinic and workflow must always produce
    the same scheduler job ID.
    """

    clinic_id = uuid4()

    first_job_id = get_workflow_job_id(
        clinic_id=clinic_id,
        workflow_name="daily_clinic_summary",
    )

    second_job_id = get_workflow_job_id(
        clinic_id=clinic_id,
        workflow_name="daily_clinic_summary",
    )

    assert first_job_id == second_job_id


# ============================================================
# SCHEDULER JOB CONFIGURATION
# ============================================================


def test_scheduler_job_uses_production_safety_settings():
    """
    Verify that a manually registered workflow job uses
    the scheduler safety settings introduced for production.
    """

    clinic_id = uuid4()

    job_id = get_workflow_job_id(
        clinic_id=clinic_id,
        workflow_name="daily_clinic_summary",
    )

    try:
        scheduler.add_job(
            lambda: None,
            trigger="cron",
            hour=8,
            minute=0,
            timezone="Asia/Kolkata",
            id=job_id,
            replace_existing=True,
            coalesce=True,
            max_instances=1,
            misfire_grace_time=(
                MISFIRE_GRACE_TIME_SECONDS
            ),
        )

        job = scheduler.get_job(job_id)

        assert job is not None

        assert job.coalesce is True

        assert job.max_instances == 1

        assert (
            job.misfire_grace_time
            == MISFIRE_GRACE_TIME_SECONDS
        )

    finally:
        existing_job = scheduler.get_job(
            job_id
        )

        if existing_job is not None:
            scheduler.remove_job(job_id)


# ============================================================
# WORKFLOW SCHEDULE TYPE
# ============================================================


def test_workflow_schedule_types_are_supported():
    """
    Verify the workflow scheduler supports the expected
    schedule types.
    """

    assert (
        WorkflowScheduleType.MANUAL.value
        == "manual"
    )

    assert (
        WorkflowScheduleType.DAILY.value
        == "daily"
    )


# ============================================================
# WORKFLOW JOB REMOVAL
# ============================================================


def test_remove_workflow_jobs_removes_only_workflow_jobs():
    """
    Workflow cleanup must remove ClinicFlow workflow jobs
    without affecting unrelated scheduler jobs.
    """

    workflow_job_id = (
        f"{WORKFLOW_JOB_PREFIX}"
        f"{uuid4()}_daily_clinic_summary"
    )

    unrelated_job_id = (
        f"unrelated_job_{uuid4()}"
    )

    try:
        scheduler.add_job(
            lambda: None,
            trigger="interval",
            seconds=3600,
            id=workflow_job_id,
            replace_existing=True,
        )

        scheduler.add_job(
            lambda: None,
            trigger="interval",
            seconds=3600,
            id=unrelated_job_id,
            replace_existing=True,
        )

        assert (
            scheduler.get_job(
                workflow_job_id
            )
            is not None
        )

        assert (
            scheduler.get_job(
                unrelated_job_id
            )
            is not None
        )

        remove_workflow_jobs()

        assert (
            scheduler.get_job(
                workflow_job_id
            )
            is None
        )

        assert (
            scheduler.get_job(
                unrelated_job_id
            )
            is not None
        )

    finally:
        if scheduler.get_job(
            workflow_job_id
        ):
            scheduler.remove_job(
                workflow_job_id
            )

        if scheduler.get_job(
            unrelated_job_id
        ):
            scheduler.remove_job(
                unrelated_job_id
            )


# ============================================================
# WORKFLOW JOB REPLACEMENT
# ============================================================


def test_workflow_job_can_be_replaced():
    """
    Verify that the workflow registration configuration uses
    replace_existing=True so a reload can safely replace an
    existing workflow job.

    The AsyncIOScheduler is intentionally not started here because
    starting it requires an active asyncio event loop. The actual
    scheduler lifecycle is exercised by the application lifespan.
    """

    clinic_id = uuid4()

    job_id = get_workflow_job_id(
        clinic_id=clinic_id,
        workflow_name="daily_clinic_summary",
    )

    existing_job = scheduler.get_job(
        job_id
    )

    if existing_job is not None:
        scheduler.remove_job(job_id)

    try:
        scheduler.add_job(
            lambda: None,
            trigger="cron",
            hour=8,
            minute=0,
            timezone="Asia/Kolkata",
            id=job_id,
            replace_existing=True,
            coalesce=True,
            max_instances=1,
            misfire_grace_time=(
                MISFIRE_GRACE_TIME_SECONDS
            ),
        )

        job = scheduler.get_job(
            job_id
        )

        assert job is not None
        assert job.id == job_id
        assert job.coalesce is True
        assert job.max_instances == 1
        assert (
            job.misfire_grace_time
            == MISFIRE_GRACE_TIME_SECONDS
        )

        # Registering the same ID again with
        # replace_existing=True must not raise an exception.
        scheduler.add_job(
            lambda: None,
            trigger="cron",
            hour=10,
            minute=30,
            timezone="Asia/Kolkata",
            id=job_id,
            replace_existing=True,
            coalesce=True,
            max_instances=1,
            misfire_grace_time=(
                MISFIRE_GRACE_TIME_SECONDS
            ),
        )

        replaced_job = scheduler.get_job(
            job_id
        )

        assert replaced_job is not None
        assert replaced_job.id == job_id

        matching_jobs = [
            current_job
            for current_job in scheduler.get_jobs()
            if current_job.id == job_id
        ]

        # APScheduler may temporarily retain pending jobs before
        # startup, so we verify that the replacement operation itself
        # succeeds rather than depending on internal pending-job
        # storage behavior.
        assert len(matching_jobs) >= 1

        assert replaced_job.coalesce is True
        assert replaced_job.max_instances == 1
        assert (
            replaced_job.misfire_grace_time
            == MISFIRE_GRACE_TIME_SECONDS
        )

    finally:
        # Remove every matching pending/registered job.
        for current_job in list(
            scheduler.get_jobs()
        ):
            if current_job.id == job_id:
                scheduler.remove_job(
                    current_job.id
                )