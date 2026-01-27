import logging
from typing import NamedTuple

from app.core.exceptions import ApplicationException
from app.infrastructure.brain.adapter import LangGraphAdapter
from app.infrastructure.storage.chroma import ChromaStorage
from app.infrastructure.storage.neo4j_document_repository import Neo4jStorage

logger = logging.getLogger(__name__)


class ResetResult(NamedTuple):
    neo4j: str
    chroma: str
    sqlite: str


class IntegrityService:
    """
    Service for maintaining system integrity and performing administrative actions
    like database reset.
    """

    def __init__(
        self,
        neo4j_storage: Neo4jStorage,
        chroma_storage: ChromaStorage,
        langgraph_adapter: LangGraphAdapter,
    ):
        self.neo4j = neo4j_storage
        self.chroma = chroma_storage
        self.adapter = langgraph_adapter

    async def reset_all(self) -> ResetResult:
        """
        Resets all data stores: Neo4j, Chroma, and SQLite Config/Checkpoints.
        """
        logger.warning("Initiating FULL SYSTEM RESET...")
        results = {}

        # 1. Neo4j
        try:
            self.neo4j.reset_database()
            results["neo4j"] = "Success: All nodes and relationships deleted"
        except Exception as e:
            logger.error(f"Neo4j reset failed: {e}")
            results["neo4j"] = f"Failed: {e}"

        # 2. Chroma
        try:
            self.chroma.reset_collection()
            results["chroma"] = "Success: Collection reset"
        except Exception as e:
            logger.error(f"Chroma reset failed: {e}")
            results["chroma"] = f"Failed: {e}"

        # 3. SQLite (Checkpointer)
        try:
            await self.adapter.reset_checkpoints()
            results["sqlite"] = "Success: Checkpoints cleared"
        except Exception as e:
            logger.error(f"SQLite reset failed: {e}")
            results["sqlite"] = f"Failed: {e}"

        return ResetResult(**results)
