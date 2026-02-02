import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from app.domain.exceptions import DomainError, DuplicateEntityError, EntityNotFoundError
from app.interfaces.api.v1.dto.common import ErrorResponse

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
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
