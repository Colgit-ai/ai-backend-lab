
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
import jwt
from jwt.exceptions import InvalidTokenError

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise unauthorized

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )

        subject = payload.get("sub")

        if not isinstance(subject, str):
            raise unauthorized

        user_id = int(subject)
        if user_id <= 0:
            raise unauthorized

    except (InvalidTokenError, ValueError):
        raise unauthorized

    user = db.query(User).filter(User.id == user_id).first()

    if user is None or not user.is_active:
        raise unauthorized

    return user
