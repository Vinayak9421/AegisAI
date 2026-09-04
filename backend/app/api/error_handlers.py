"""Central error handlers translating domain and HTTP exceptions into standard error envelopes."""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.errors import (
    AegisDomainError,
    AuthenticationError,
    ConflictError,
    ForbiddenError,
    JudgeUnavailableError,
    NotFoundError,
    PolicyBlockedError,
    QuotaExhaustedError,
    TargetUnavailableError,
    ValidationError,
)
from app.core.logging import logger
from app.schemas.common import ApiErrorResponse, ErrorBody


def get_req_id(request: Request) -> str:
    return getattr(request.state, "request_id", "unknown")


def register_error_handlers(app: FastAPI) -> None:
    """Register all custom error handlers with the FastAPI application."""

    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
        req_id = get_req_id(request)
        logger.warning(f"Resource not found: {exc.message} [req:{req_id}]")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ApiErrorResponse(
                error=ErrorBody(
                    code=exc.code,
                    message=exc.message,
                    details=exc.details,
                    request_id=req_id,
                )
            ).model_dump(),
        )

    @app.exception_handler(AuthenticationError)
    async def auth_error_handler(request: Request, exc: AuthenticationError) -> JSONResponse:
        req_id = get_req_id(request)
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=ApiErrorResponse(
                error=ErrorBody(
                    code=exc.code,
                    message=exc.message,
                    details=exc.details,
                    request_id=req_id,
                )
            ).model_dump(),
        )

    @app.exception_handler(ForbiddenError)
    @app.exception_handler(PolicyBlockedError)
    async def forbidden_handler(request: Request, exc: AegisDomainError) -> JSONResponse:
        req_id = get_req_id(request)
        logger.warning(f"Access forbidden / policy blocked: {exc.message} [req:{req_id}]")
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=ApiErrorResponse(
                error=ErrorBody(
                    code=exc.code,
                    message=exc.message,
                    details=exc.details,
                    request_id=req_id,
                )
            ).model_dump(),
        )

    @app.exception_handler(ConflictError)
    async def conflict_handler(request: Request, exc: ConflictError) -> JSONResponse:
        req_id = get_req_id(request)
        logger.info(f"State conflict: {exc.message} [req:{req_id}]")
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=ApiErrorResponse(
                error=ErrorBody(
                    code=exc.code,
                    message=exc.message,
                    details=exc.details,
                    request_id=req_id,
                )
            ).model_dump(),
        )

    @app.exception_handler(ValidationError)
    async def validation_handler(request: Request, exc: ValidationError) -> JSONResponse:
        req_id = get_req_id(request)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ApiErrorResponse(
                error=ErrorBody(
                    code=exc.code,
                    message=exc.message,
                    details=exc.details,
                    request_id=req_id,
                )
            ).model_dump(),
        )

    @app.exception_handler(QuotaExhaustedError)
    async def quota_handler(request: Request, exc: QuotaExhaustedError) -> JSONResponse:
        req_id = get_req_id(request)
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content=ApiErrorResponse(
                error=ErrorBody(
                    code=exc.code,
                    message=exc.message,
                    details=exc.details,
                    request_id=req_id,
                )
            ).model_dump(),
        )

    @app.exception_handler(TargetUnavailableError)
    @app.exception_handler(JudgeUnavailableError)
    async def upstream_handler(request: Request, exc: AegisDomainError) -> JSONResponse:
        req_id = get_req_id(request)
        logger.error(f"Upstream provider unavailable: {exc.message} [req:{req_id}]")
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content=ApiErrorResponse(
                error=ErrorBody(
                    code=exc.code,
                    message=exc.message,
                    details=exc.details,
                    request_id=req_id,
                )
            ).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        req_id = get_req_id(request)
        details = []
        for err in exc.errors():
            loc = ".".join(str(l) for l in err.get("loc", []))
            details.append({"field": loc, "issue": err.get("msg", "Invalid value")})
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ApiErrorResponse(
                error=ErrorBody(
                    code="VALIDATION_ERROR",
                    message="Request payload validation failed",
                    details=details,
                    request_id=req_id,
                )
            ).model_dump(),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        req_id = get_req_id(request)
        code_map = {
            400: "BAD_REQUEST",
            401: "UNAUTHENTICATED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            409: "CONFLICT",
            422: "UNPROCESSABLE_ENTITY",
            429: "RATE_LIMITED",
            500: "INTERNAL_ERROR",
            502: "BAD_GATEWAY",
            503: "SERVICE_UNAVAILABLE",
        }
        return JSONResponse(
            status_code=exc.status_code,
            content=ApiErrorResponse(
                error=ErrorBody(
                    code=code_map.get(exc.status_code, "HTTP_ERROR"),
                    message=str(exc.detail),
                    details=[],
                    request_id=req_id,
                )
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        req_id = get_req_id(request)
        logger.exception(f"Unhandled internal server error: {exc} [req:{req_id}]")
        # Ensure we never leak internal traces or SQL to client
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ApiErrorResponse(
                error=ErrorBody(
                    code="INTERNAL_SERVER_ERROR",
                    message="An unexpected internal error occurred. Please reference the request ID.",
                    details=[],
                    request_id=req_id,
                )
            ).model_dump(),
        )
