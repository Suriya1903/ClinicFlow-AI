from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from backend.app.models.clinic import Clinic
from backend.app.models.user import User, UserRole


class AuthService:
    @staticmethod
    def register_user(
        db: Session,
        name: str,
        email: str,
        password: str,
        clinic_id: UUID,
        role: UserRole = UserRole.RECEPTIONIST,
    ) -> User:
        """
        Register a new user for an existing clinic.

        Passwords are stored only as bcrypt hashes.
        """

        clinic = db.scalar(
            select(Clinic).where(Clinic.id == clinic_id)
        )

        if clinic is None:
            raise ValueError("Clinic not found")

        existing_user = db.scalar(
            select(User).where(User.email == email)
        )

        if existing_user is not None:
            raise ValueError("Email is already registered")

        password_hash = hash_password(password)

        user = User(
            clinic_id=clinic_id,
            name=name,
            email=email,
            password_hash=password_hash,
            role=role,
            is_active=True,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def authenticate_user(
        db: Session,
        email: str,
        password: str,
    ) -> User:
        """
        Authenticate a user using email and password.

        Authentication fails when:
        - The email does not exist.
        - The account is inactive.
        - The password does not match.
        """

        user = db.scalar(
            select(User).where(User.email == email)
        )

        if user is None:
            raise ValueError(
                "Invalid email or password"
            )

        if not user.is_active:
            raise ValueError(
                "User account is inactive"
            )

        if not verify_password(
            password,
            user.password_hash,
        ):
            raise ValueError(
                "Invalid email or password"
            )

        return user

    @staticmethod
    def create_user_token(
        user: User,
    ) -> str:
        """
        Create an access token for an authenticated user.

        User identity, tenant identity, and role are included
        as claims.

        Security-sensitive JWT claims such as:
        - iat
        - exp
        - jti
        - typ

        are generated internally by create_access_token().
        """

        return create_access_token(
            {
                "sub": str(user.id),
                "clinic_id": str(user.clinic_id),
                "role": user.role.value,
            }
        )

    @staticmethod
    def create_initial_admin(
        db: Session,
        name: str,
        email: str,
        password: str,
        clinic_id: UUID,
    ) -> User:
        """
        Create the initial administrator for a clinic.

        This method is intended for controlled initial
        clinic setup, not normal public registration.
        """

        clinic = db.scalar(
            select(Clinic).where(Clinic.id == clinic_id)
        )

        if clinic is None:
            raise ValueError("Clinic not found")

        existing_user = db.scalar(
            select(User).where(User.email == email)
        )

        if existing_user is not None:
            raise ValueError(
                "Email is already registered"
            )

        admin = User(
            clinic_id=clinic_id,
            name=name,
            email=email,
            password_hash=hash_password(password),
            role=UserRole.ADMIN,
            is_active=True,
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        return admin