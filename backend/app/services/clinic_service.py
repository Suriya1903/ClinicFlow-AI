from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.security import hash_password
from backend.app.models.clinic import Clinic
from backend.app.models.user import User, UserRole


class ClinicService:

    @staticmethod
    def create_clinic(
        db: Session,
        clinic_name: str,
        slug: str,
        admin_name: str,
        admin_email: str,
        admin_password: str,
    ) -> tuple[Clinic, User]:

        # ---------------------------------------------------------
        # Check whether the clinic slug already exists.
        # ---------------------------------------------------------

        existing_clinic = db.scalar(
            select(Clinic).where(
                Clinic.slug == slug
            )
        )

        if existing_clinic is not None:
            raise ValueError(
                "A clinic with this slug already exists"
            )

        # ---------------------------------------------------------
        # Check whether the admin email already exists.
        # ---------------------------------------------------------

        existing_user = db.scalar(
            select(User).where(
                User.email == admin_email
            )
        )

        if existing_user is not None:
            raise ValueError(
                "A user with this email already exists"
            )

        # ---------------------------------------------------------
        # Create clinic.
        # ---------------------------------------------------------

        clinic = Clinic(
            name=clinic_name,
            slug=slug,
        )

        db.add(clinic)

        # Flush sends the INSERT to PostgreSQL and generates
        # the Python-side UUID without committing yet.
        db.flush()

        # ---------------------------------------------------------
        # Create initial administrator.
        # ---------------------------------------------------------

        admin = User(
            clinic_id=clinic.id,
            name=admin_name,
            email=admin_email,
            password_hash=hash_password(
                admin_password
            ),
            role=UserRole.ADMIN,
            is_active=True,
        )

        db.add(admin)

        # ---------------------------------------------------------
        # Commit both records together.
        # ---------------------------------------------------------

        db.commit()

        db.refresh(clinic)
        db.refresh(admin)

        return clinic, admin

    @staticmethod
    def get_clinic(
        db: Session,
        clinic_id: UUID,
    ) -> Clinic | None:

        return db.scalar(
            select(Clinic).where(
                Clinic.id == clinic_id
            )
        )

    @staticmethod
    def update_clinic(
        db: Session,
        clinic: Clinic,
        name: str | None = None,
        slug: str | None = None,
    ) -> Clinic:

        # ---------------------------------------------------------
        # Check slug uniqueness if slug is being changed.
        # ---------------------------------------------------------

        if (
            slug is not None
            and slug != clinic.slug
        ):
            existing_clinic = db.scalar(
                select(Clinic).where(
                    Clinic.slug == slug,
                    Clinic.id != clinic.id,
                )
            )

            if existing_clinic is not None:
                raise ValueError(
                    "A clinic with this slug already exists"
                )

            clinic.slug = slug

        # ---------------------------------------------------------
        # Update clinic name.
        # ---------------------------------------------------------

        if name is not None:
            clinic.name = name

        db.commit()
        db.refresh(clinic)

        return clinic