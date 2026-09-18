from getpass import getpass

from sqlalchemy import select

from backend.app.core.security import hash_password
from backend.app.db.session import SessionLocal
from backend.app.models.user import User


def main() -> None:
    email = "admin@greencare.com"

    new_password = getpass(
        "Enter the new admin password: "
    )

    if len(new_password) < 8:
        raise ValueError(
            "Password must contain at least 8 characters."
        )

    db = SessionLocal()

    try:
        user = db.scalar(
            select(User).where(
                User.email == email
            )
        )

        if user is None:
            print(
                f"No user found with email: {email}"
            )
            return

        user.password_hash = hash_password(
            new_password
        )

        db.commit()

        print(
            f"Password successfully reset for {email}"
        )

    finally:
        db.close()


if __name__ == "__main__":
    main()