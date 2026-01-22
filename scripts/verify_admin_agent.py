import asyncio
import sys
import os
from langchain_core.messages import HumanMessage

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.admin.agents.admin_agent import AdminAgent
from app.use_cases.ingestion import IngestionService
from app.domain.services.rag_service import RAGService
from app.interfaces.api.dependencies import get_neo4j_driver
from app.infrastructure.storage.neo4j_document_repository import Neo4jStorage
from app.infrastructure.storage.neo4j_graph_repository import Neo4jGraphRepository
from app.infrastructure.storage.chroma import ChromaStorage
from app.core.llm import get_llm
from app.domain.services.query_rewriter import QueryRewriter
from app.infrastructure.chunker.langchain_chunker import LangChainChunker
from app.domain.services.semantic_extractor import SemanticExtractor
from app.infrastructure.brain.adapter import LangGraphAdapter
from app.infrastructure.storage.neo4j_job_repository import Neo4jJobRepository
from app.infrastructure.scrapers.trafilatura_scraper import TrafilaturaWebScraper

async def main():
    print("🚀 Initializing Dependencies...")
    driver = get_neo4j_driver()
    neo4j_doc = Neo4jStorage(driver)
    neo4j_graph = Neo4jGraphRepository(driver)
    chroma = ChromaStorage()
    llm = get_llm()
    rewriter = QueryRewriter(llm)
    
    rag_service = RAGService(
        neo4j_doc_repo=neo4j_doc,
        neo4j_graph_repo=neo4j_graph,
        chroma_repo=chroma,
        query_rewriter=rewriter,
        llm=llm
    )
    
    job_repo = Neo4jJobRepository(driver)
    chunker = LangChainChunker()
    graph_adapter = LangGraphAdapter(llm)
    extractor = SemanticExtractor(graph_adapter)
    scraper = TrafilaturaWebScraper()
    
    ingestion_service = IngestionService(
        scraper=scraper,
        repository=neo4j_doc,
        graph=neo4j_graph,
        job_repository=job_repo,
        chunker=chunker,
        extractor=extractor
    )
    
    agent = AdminAgent(rag_service, ingestion_service)
    print("✅ AdminAgent Initialized.")

    # 1. Test Ingestion Intent
    print("\n[Test 1] Ingestion Intent")
    url = "https://example.com"
    inputs = {"messages": [HumanMessage(content=f"이 링크 수집해줘: {url}")]}
    result = await agent.workflow.ainvoke(inputs)
    
    intent = result.get("intent")
    output = result.get("tool_output")
    print(f"Intent: {intent}")
    print(f"Output: {output}")
    assert intent == "ingest"
    assert "수집" in output or "example.com" in output

    # 2. Test Search Intent
    print("\n[Test 2] Search Intent")
    inputs = {"messages": [HumanMessage(content="RAG가 뭐야?")]}
    result = await agent.workflow.ainvoke(inputs)
    
    intent = result.get("intent")
    answer = result["messages"][-1].content
    context = result.get("context_data")
    
    print(f"Intent: {intent}")
    print(f"Answer: {answer[:50]}...")
    print(f"Context Keys: {context.keys() if context else 'None'}")
    
    assert intent == "search"
    assert context is not None
    assert "vector_chunks" in context

    print("\n🎉 Verification Success!")

if __name__ == "__main__":
    asyncio.run(main())
