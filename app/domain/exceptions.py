from app.core.exceptions import BaseAppException

class DomainException(BaseAppException):
    """Business logic and domain rule violations."""
    pass

class EntityNotFoundException(DomainException):
    """Raised when an entity cannot be found in the repository."""
    def __init__(self, entity_name: str, entity_id: str):
        self.entity_name = entity_name
        self.entity_id = entity_id
        super().__init__(f"{entity_name} with id {entity_id} not found.")

class DuplicateEntityException(DomainException):
    """Raised when attempting to create an entity that already exists."""
    def __init__(self, entity_name: str, entity_id: str):
        self.entity_name = entity_name
        self.entity_id = entity_id
        super().__init__(f"{entity_name} with id {entity_id} already exists.")
