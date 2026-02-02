from app.core.exceptions import BaseAppError


class InfrastructureError(BaseAppError):
    """External system failures (DB, API, Network)."""

    pass


class ScrapingError(InfrastructureError):
    """Failed to fetch or parse content from URL."""

    pass


class LLMError(InfrastructureError):
    """LLM API failures or quota exceeded."""

    pass


class DatabaseError(InfrastructureError):
    """Database connection or query failures."""

    pass
