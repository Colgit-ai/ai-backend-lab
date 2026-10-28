
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import hash_password, verify_password


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register_user(self, email: str, password: str) -> User:
        normalized_email = email.strip().lower()

        existing_user = (
            self.db.query(User)
            .filter(User.email == normalized_email)
            .first()
        )

        if existing_user:
            raise ValueError("Email is already registered")

        user = User(
            email=normalized_email,
            hashed_password=hash_password(password),
        )

        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception:
            self.db.rollback()
            raise

    def authenticate_user(self, email: str, password: str) -> User | None:
        normalized_email = email.strip().lower()

        user = (
            self.db.query(User)
            .filter(User.email == normalized_email)
            .first()
        )

        if user is None or not verify_password(
            password, user.hashed_password
        ):
            return None

        if not user.is_active:
            return None

        return user
