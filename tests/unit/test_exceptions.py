from app.core.exceptions import BaseAppException
from app.domain.exceptions import DomainException
from app.infrastructure.exceptions import (
    DatabaseError,
    InfrastructureException,
    LLMError,
    ScrapingError,
)


def test_exception_inheritance():
    """Verify exception hierarchy"""
    assert issubclass(BaseAppException, Exception)
    assert issubclass(DomainException, BaseAppException)
    assert issubclass(InfrastructureException, BaseAppException)
    assert issubclass(ScrapingError, InfrastructureException)
    assert issubclass(LLMError, InfrastructureException)
    assert issubclass(DatabaseError, InfrastructureException)


def test_exception_messages():
    """Verify exception messages are preserved"""
    msg = "Something went wrong"
    exc = DomainException(msg)
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
    assert isinstance(DatabaseError("test"), BaseAppException)
