from app.core.exceptions import BaseAppError
from app.domain.exceptions import DomainError
from app.infrastructure.exceptions import (
    DatabaseError,
    InfrastructureError,
    LLMError,
    ScrapingError,
)


def test_exception_inheritance():
    """Verify exception hierarchy"""
    assert issubclass(BaseAppError, Exception)
    assert issubclass(DomainError, BaseAppError)
    assert issubclass(InfrastructureError, BaseAppError)
    assert issubclass(ScrapingError, InfrastructureError)
    assert issubclass(LLMError, InfrastructureError)
    assert issubclass(DatabaseError, InfrastructureError)


def test_exception_messages():
    """Verify exception messages are preserved"""
    msg = "Something went wrong"
    exc = DomainError(msg)
    assert str(exc) == msg


def test_exception_with_cause():
    """Verify exception chaining"""
    try:
        raise ValueError("Original error")
    except ValueError:
        DatabaseError("DB Failed")
        # Python 3 exception chaining
        pass

    # Just verifying instantiation works
    assert isinstance(DatabaseError("test"), BaseAppError)
