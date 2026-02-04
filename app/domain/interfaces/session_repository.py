from abc import ABC, abstractmethod


class SessionRepository(ABC):
    @abstractmethod
    async def delete_session(self, thread_id: str) -> None:
        """
        Delete all data associated with a session (thread_id).
        This includes checkpoints, writes, and blobs.
        """
        pass
