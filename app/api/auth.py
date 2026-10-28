
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
)
from app.services.auth_service import AuthService
from app.api.dependencies import get_current_user
from app.models.user import User


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: UserCreate,
    db: Session = Depends(get_db),
) -> UserResponse:
    auth_service = AuthService(db)

    try:
        user = auth_service.register_user(
            email=str(request.email),
            password=request.password,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        ) from exc

    return user


@router.post("/login", response_model=TokenResponse)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    auth_service = AuthService(db)

    user = auth_service.authenticate_user(
        email=str(request.email),
        password=request.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user_id=user.id)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    return current_user
