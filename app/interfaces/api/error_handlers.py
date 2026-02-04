import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from app.domain.exceptions import DomainError, DuplicateEntityError, EntityNotFoundError
from app.interfaces.api.v1.dto.common import ErrorResponse

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        Overrides the default FastAPI 422 error response to match our standard ErrorResponse format.
        """
        # Collect validation errors
        details = {}
        for error in exc.errors():
            # location is usually ('body', 'field_name')
            loc = ".".join(str(x) for x in error.get("loc", []))
            msg = error.get("msg", "Invalid value")
            details[loc] = msg

        response = ErrorResponse(
            status="error",
            error_code="VALIDATION_ERROR",
            message="Input validation failed",
            details=details,
        )
        return JSONResponse(status_code=HTTP_422_UNPROCESSABLE_ENTITY, content=response.model_dump())

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """
        Handles standard HTTP exceptions (e.g., 405 Method Not Allowed, 401 Unauthorized)
        """
        response = ErrorResponse(
            status="error",
            error_code=f"HTTP_{exc.status_code}",
            message=str(exc.detail),
        )
        return JSONResponse(status_code=exc.status_code, content=response.model_dump())

    @app.exception_handler(EntityNotFoundError)
    async def entity_not_found_handler(request: Request, exc: EntityNotFoundError):
        response = ErrorResponse(error_code="ENTITY_NOT_FOUND", message=str(exc))
        return JSONResponse(status_code=HTTP_404_NOT_FOUND, content=response.model_dump())

    @app.exception_handler(DuplicateEntityError)
    async def duplicate_entity_handler(request: Request, exc: DuplicateEntityError):
        response = ErrorResponse(error_code="DUPLICATE_ENTITY", message=str(exc))
        return JSONResponse(status_code=HTTP_409_CONFLICT, content=response.model_dump())

    @app.exception_handler(DomainError)
    async def domain_exception_handler(request: Request, exc: DomainError):
        response = ErrorResponse(error_code="DOMAIN_ERROR", message=str(exc))
        return JSONResponse(status_code=HTTP_400_BAD_REQUEST, content=response.model_dump())

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        response = ErrorResponse(error_code="INTERNAL_SERVER_ERROR", message="An unexpected error occurred.")
        return JSONResponse(status_code=HTTP_500_INTERNAL_SERVER_ERROR, content=response.model_dump())
