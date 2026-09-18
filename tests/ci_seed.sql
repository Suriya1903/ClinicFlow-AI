-- ClinicFlow AI CI database seed
--
-- This file contains only deterministic, non-production test fixtures.
-- It intentionally excludes audit history, temporary test users,
-- workflow execution history, and development password hashes.
--
-- The bcrypt hash below is for the password already used by the
-- existing authentication test suite. It is CI-only test data.

BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ============================================================
-- GREENCARE CLINIC
-- ============================================================

INSERT INTO public.clinics
    (id, name, slug)
VALUES
    (
        'f51477c4-fb11-4480-af11-edb70650475c',
        'GreenCare Clinic',
        'greencare-clinic'
    );

-- ============================================================
-- ADMIN USER
-- ============================================================

INSERT INTO public.users
    (
        id,
        clinic_id,
        name,
        email,
        password_hash,
        role,
        is_active
    )
VALUES
    (
        '22576a3d-b845-4cfe-a071-96b7acc65e9b',
        'f51477c4-fb11-4480-af11-edb70650475c',
        'Clinic Admin',
        'admin@greencare.com',
        crypt('12345678', gen_salt('bf', 12)),
        'ADMIN',
        true
    );

-- ============================================================
-- DOCTOR
-- ============================================================

INSERT INTO public.doctors
    (
        id,
        clinic_id,
        name,
        specialization,
        license_number,
        phone,
        bio,
        is_active
    )
VALUES
    (
        'cb8e8eea-e5a4-4dd2-9423-b91902112793',
        'f51477c4-fb11-4480-af11-edb70650475c',
        'Dr. Meera',
        'General Medicine',
        'TN-MED-10001',
        '+91-9000000000',
        'General physician specializing in primary care.',
        true
    );

-- ============================================================
-- PATIENT
-- ============================================================

INSERT INTO public.patients
    (
        id,
        clinic_id,
        first_name,
        last_name,
        date_of_birth,
        gender,
        phone,
        email,
        address,
        emergency_contact_name,
        emergency_contact_phone,
        blood_group,
        medical_notes,
        is_active
    )
VALUES
    (
        '3314a2bb-c40c-4114-a56e-d42c121813ae',
        'f51477c4-fb11-4480-af11-edb70650475c',
        'Rahul',
        'Kumar',
        '1998-05-12',
        'Male',
        '+91-9876543210',
        'rahul.kumar@example.com',
        'Chennai',
        NULL,
        NULL,
        NULL,
        'Test patient for ClinicFlow MCP integration',
        true
    );

-- ============================================================
-- TODAY'S APPOINTMENT
-- ============================================================
-- Keep the appointment at 10:30 AM Asia/Kolkata on the day
-- the CI seed is loaded. This prevents the MCP "today"
-- integration test from becoming date-dependent.

INSERT INTO public.appointments
    (
        id,
        clinic_id,
        doctor_id,
        patient_id,
        scheduled_at,
        status,
        reason,
        notes
    )
VALUES
    (
        '839b47ce-2414-45ec-9e66-994dc6024a80',
        'f51477c4-fb11-4480-af11-edb70650475c',
        'cb8e8eea-e5a4-4dd2-9423-b91902112793',
        '3314a2bb-c40c-4114-a56e-d42c121813ae',
        (CURRENT_DATE + TIME '10:30:00') AT TIME ZONE 'Asia/Kolkata',
        'SCHEDULED',
        NULL,
        NULL
    );

-- ============================================================
-- WORKFLOW CONFIGURATION
-- ============================================================

INSERT INTO public.workflow_configurations
    (
        id,
        clinic_id,
        workflow_name,
        display_name,
        description,
        is_enabled,
        schedule_type,
        schedule_hour,
        schedule_minute
    )
VALUES
    (
        '8b8e9730-d538-478e-a9d6-c5c866577602',
        'f51477c4-fb11-4480-af11-edb70650475c',
        'daily_clinic_summary',
        'Daily Clinic Summary',
        'Generate the clinic''s daily operational summary.',
        true,
        'DAILY',
        8,
        0
    );

COMMIT;
