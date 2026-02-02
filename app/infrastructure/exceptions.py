from app.core.exceptions import BaseAppException

class InfrastructureException(BaseAppException):
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
