class DoitException(Exception):  # noqa: N818
    """Base exception for all application errors."""
    pass

class DomainException(DoitException):
    """Business logic and domain rule violations."""
    pass

class InfrastructureException(DoitException):
    """External system failures (DB, API, Network)."""
    pass

class ScrapingError(InfrastructureException):
    """Failed to fetch or parse content from URL."""
    pass

class LLMError(InfrastructureException):
    """LLM API failures or quota exceeded."""
    pass

class DatabaseError(InfrastructureException):
    """Database connection or query failures."""
    pass
