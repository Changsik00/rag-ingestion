import asyncio
import logging
import uuid

from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver

from app.application.services.admin_agent import AdminAgent


# Mocking RAGService to isolate Agent logic
class MockRAGService:
    async def retrieve_and_generate(self, query, history, filters=None, thread_id=None):
        from app.application.services.rag_service import RAGResult

        return RAGResult(
            answer="Knowledge Channel is a great TV program.",
            rewritten_query=query,
            vector_chunks=[],
            keyword_chunks=[],
            graph_data=[],
            full_context="Context about Knowledge Channel",
            user_intent=None,
        )


# Mocking IngestionService
class MockIngestionService:
    pass


async def main():
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("VerifyAdmin")

    # Setup
    rag_service = MockRAGService()
    ingestion_service = MockIngestionService()
    agent = AdminAgent(rag_service, ingestion_service)

    checkpointer = MemorySaver()

    # Init Graph
    workflow = agent.build_workflow(checkpointer=checkpointer)

    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    # Test Case 1: HITL Enabled
    logger.info("--- Test Case 1: HITL Enabled ---")
    input_state = {
        "messages": [{"role": "user", "content": "Tell me about Knowledge Channel"}],
        "hitl_enabled": True,
        "thread_id": thread_id,
    }

    # Run
    # If interrupt works, ainvoke might raise GraphInterrupt or return partial state?
    # Key: Does it return the state with tool_output?
    try:
        result = await workflow.ainvoke(input_state, config=config)
        logger.info(f"Result (HITL=True): {result.keys()}")
        if "messages" in result:
            logger.info(f"Answer: {result['messages'][-1].content}")
        else:
            logger.info("No messages in result")

        # Check next
        snapshot = workflow.get_state(config)
        logger.info(f"Next Node: {snapshot.next}")

    except Exception as e:
        logger.error(f"Exception: {e}")

    # Test Case 2: Resume
    if "human_review" in snapshot.next:
        logger.info("--- Test Case 2: Resuming ---")
        # Resume logic
        # agent.human_review_node just passes through.
        # So we just invoke with None?
        update = {"hitl_enabled": False}  # Disable to finish
        workflow.update_state(config, update)

        result_resume = await workflow.ainvoke(None, config=config)
        logger.info(f"Result (Resume): {result_resume.keys()}")


if __name__ == "__main__":
    asyncio.run(main())
