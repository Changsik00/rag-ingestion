import asyncio
import logging
import uuid

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver

from app.application.services.admin_agent import ConversationalRAGAgent

# App Modules (Real)
from app.core.config import get_settings
from app.infrastructure.storage.chroma import ChromaVectorRepository
from app.infrastructure.storage.neo4j_document_repository import Neo4jDocumentRepository
from app.infrastructure.storage.neo4j_graph_repository import Neo4jGraphRepository

# from app.infrastructure.brain.intent_classifier import IntentClassifier
# from app.infrastructure.brain.query_rewriter import QueryRewriter

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("VerifyHITL")


def get_real_services():
    """
    Initialize REAL services for the Admin Agent.
    Note: Using real DB connections (Neo4j, Chroma) but Read-Only mostly.
    """
    settings = get_settings()

    # 1. Repositories
    # Neo4j Driver needs to be created or passed. Neo4jStorage takes a driver.
    # But usually DI handles this. Here we need to create it manually.
    from neo4j import GraphDatabase

    driver = GraphDatabase.driver(settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD))

    _neo4j_doc_repo = Neo4jDocumentRepository(driver=driver)
    _neo4j_graph_repo = Neo4jGraphRepository(driver=driver)
    _chroma_repo = ChromaVectorRepository()  # Assuming it connects to persistent dir

    # 2. LLM Components
    _llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL_NAME, temperature=0, google_api_key=settings.GEMINI_API_KEY
    )
    # adapter = LangChainLLMAdapter(llm) # Not strictly needed if mocking RAG

    # intent_classifier = IntentClassifier(llm=adapter if hasattr(adapter, 'ainvoke') else llm)
    # query_rewriter = QueryRewriter(llm=adapter if hasattr(adapter, 'ainvoke') else llm)

    # 3. Services
    # Note: Using Mock RAG graph builder?? No, let's try to use RAG as is if possible.
    # But RAG now requires RAGGraphBuilder (Spec 033).
    # Since we are testing *AdminAgent* HITL, we can mock RAG to avoid complexity
    # OR use real one if easy.
    # Let's start with a Mock RAG Service for simplicity in testing AdminAgent's HITL logic first,
    # as defined in the plan "Minimal Dependencies".

    class MockRAG:
        async def retrieve_and_generate(self, query, history, filters=None, thread_id=None):
            logger.info(f"[MockRAG] Processing query: {query}")
            await asyncio.sleep(1)  # Simulate delay
            from app.application.services.rag import RAGResult

            return RAGResult(
                answer="This is a real LLM response from Admin Agent context, but the RAG retrieval was mocked.",
                rewritten_query=query,
                vector_chunks=[],
                keyword_chunks=[],
                graph_data=[],
                full_context="Mock Context",
                user_intent=None,
            )

    class MockIngestionUseCase:
        def create_job(self, url):
            logger.info(f"[MockIngestion] Create job for {url}")

            # Return dummy job object
            class DummyJob:
                job_id = "job-123"

            return DummyJob()

        def process_job(self, job_id):
            logger.info(f"[MockIngestion] Processing {job_id}")

        class MockJobRepo:
            def get_job(self, job_id):
                from app.domain.entities.job import Job, JobStatus

                return Job(id=job_id, url="http://dummy.com", status=JobStatus.COMPLETED, docs_ids=["doc-1"])

        job_repository = MockJobRepo()

    rag_service = MockRAG()
    ingestion_service = MockIngestionUseCase()

    return rag_service, ingestion_service


async def main():
    load_dotenv()

    print("--- 🚀 Spec 040: Real-World HITL Verification Script ---")

    # 1. Setup
    checkpointer = MemorySaver()
    rag_service, ingestion_service = get_real_services()

    agent = ConversationalRAGAgent(rag_service, ingestion_service)
    workflow = agent.build_workflow(checkpointer=checkpointer)

    # 2. Config
    thread_id = f"test-hitl-{uuid.uuid4().hex[:6]}"
    config = {"configurable": {"thread_id": thread_id}}
    print(f"🧵 Thread ID: {thread_id}")

    # 3. Interactive Loop
    while True:
        try:
            user_input = input("\n👤 User (q/exit to quit): ").strip()
            if user_input.lower() in ["q", "exit"]:
                print("👋 Exiting...")
                break

            hitl_input = input("   Enable HITL? (y/n, default n): ").strip().lower()
            hitl_enabled = hitl_input == "y"

            print(f"   (Settings: HITL={'ON' if hitl_enabled else 'OFF'})")

            # Prepare Input
            inputs = {
                "messages": [HumanMessage(content=user_input)],
                "hitl_enabled": hitl_enabled,
                "intent": "",  # Let router decide
                "tool_output": "",
                "context_data": {},
                "filters": None,
            }

            print("🤖 Agent Running...")
            async for event in workflow.astream(inputs, config=config):
                # Basic logging
                for key, value in event.items():
                    print(f"   -> Node: {key}")

            # Check for Interrupt
            snapshot = workflow.get_state(config)
            if snapshot.next:
                print(f"⏸️  Agent Paused! Next Node: {snapshot.next}")
                print("   (Waiting for human review/feedback...)")

                feedback = input("\n👤 Feedback (Enter to approve, or type text): ").strip()
                if not feedback:
                    feedback = "Approved"

                print(f"   Sending Feedback: '{feedback}'")

                # Resume
                # Update state with feedback as a user message (or tool output depending on logic)
                # AdminAgent.human_review_node is a pass-through, so we might just need to proceed.
                # Usually we update messages.
                workflow.update_state(config, {"messages": [HumanMessage(content=feedback)]})

                print("▶️  Resuming Agent...")
                # Invoke with None to resume
                async for event in workflow.astream(None, config=config):
                    for key, value in event.items():
                        print(f"   -> Node: {key}")

            # Final Result
            final_snapshot = workflow.get_state(config)
            if final_snapshot.values.get("messages"):
                last_msg = final_snapshot.values["messages"][-1]
                print(f"\n🏁 Final Answer: {last_msg.content}")

        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            break


if __name__ == "__main__":
    asyncio.run(main())
