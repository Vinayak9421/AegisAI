"""Authentication & User Identity API Router."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, get_request_id
from app.modules.auth.models import User
from app.modules.auth.schemas import LoginRequest, RegisterRequest, TokenResponse, UserSummary
from app.schemas.common import ApiResponse, ResponseMeta
from app.modules.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=ApiResponse[TokenResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register New User Account",
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[TokenResponse]:
    """Register a new user account with role 'MEMBER'."""
    service = AuthService(db)
    user, token, expires_in = service.register_user(request)
    summary = service.to_user_summary(user)

    return ApiResponse(
        data=TokenResponse(
            access_token=token,
            token_type="bearer",
            expires_in=expires_in,
            user=summary,
        ),
        meta=ResponseMeta(request_id=request_id),
    )


@router.post(
    "/login",
    response_model=ApiResponse[TokenResponse],
    summary="Authenticate User / Admin",
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[TokenResponse]:
    """Authenticate user or admin via email and password."""
    service = AuthService(db)
    user, token, expires_in = service.authenticate_user(request.email, request.password)
    summary = service.to_user_summary(user)

    return ApiResponse(
        data=TokenResponse(
            access_token=token,
            token_type="bearer",
            expires_in=expires_in,
            user=summary,
        ),
        meta=ResponseMeta(request_id=request_id),
    )


@router.get(
    "/me",
    response_model=ApiResponse[UserSummary],
    summary="Get Current Authenticated User",
)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[UserSummary]:
    """Return profile, role, and tenant details of the currently authenticated token bearer."""
    service = AuthService(db)
    summary = service.to_user_summary(current_user)
    return ApiResponse(
        data=summary,
        meta=ResponseMeta(request_id=request_id),
    )
