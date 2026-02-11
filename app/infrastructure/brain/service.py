import logging

from app.domain.services.intent_classifier import IntentClassifier
from app.domain.services.query_rewriter import QueryRewriter
from app.domain.value_objects.intent import IntentType, UserIntent

logger = logging.getLogger(__name__)


class BrainService:
    """
    Brain Layer Service: Handles intent classification and query rewriting.
    This service coordinates the 'thinking' process of the RAG pipeline.
    """

    def __init__(self, intent_classifier: IntentClassifier, query_rewriter: QueryRewriter):
        self.intent_classifier = intent_classifier
        self.query_rewriter = query_rewriter

    async def classify_and_rewrite(self, query: str, history: list[dict]) -> tuple[UserIntent, str]:
        """
        Classifies the user's intent and rewrites the query for better search results.

        Args:
            query: The user's input query.
            history: Chat history.

        Returns:
            tuple[UserIntent, str]: (Classified Intent, Rewritten Query)
        """
        # 1. Intent Classification (with Fallback)
        try:
            # Service is async
            user_intent = await self.intent_classifier.classify(query, history)
        except Exception as e:
            logger.warning(f"Intent classification failed: {e}. Falling back to GENERAL_QUERY.")
            user_intent = UserIntent(
                intent=IntentType.GENERAL_QUERY, targets=[], reasoning=f"Fallback due to classification error: {e}"
            )

        # 2. Query Rewriting
        # Service is async
        try:
            rewritten_query = await self.query_rewriter.rewrite(query, history)
        except Exception as e:
            logger.warning(f"Query rewriting failed: {e}. Returning original query.")
            rewritten_query = query

        return user_intent, rewritten_query
