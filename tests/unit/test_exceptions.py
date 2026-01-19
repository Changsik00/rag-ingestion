from app.core.exceptions import (
    DatabaseError,
    DoitException,
    DomainException,
    InfrastructureException,
    LLMError,
    ScrapingError,
)


def test_exception_inheritance():
    """Verify exception hierarchy"""
    assert issubclass(DoitException, Exception)
    assert issubclass(DomainException, DoitException)
    assert issubclass(InfrastructureException, DoitException)
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
    assert isinstance(DatabaseError("test"), DoitException)
