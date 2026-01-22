import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

import asyncio
import logging

import streamlit as st

from app.admin.services.feedback_service import FeedbackService
from app.core.llm import get_llm
from app.domain.services.query_rewriter import QueryRewriter
from app.domain.services.rag_service import RAGService
from app.infrastructure.storage.chroma import ChromaStorage
from app.infrastructure.storage.neo4j_document_repository import Neo4jStorage
from app.infrastructure.storage.neo4j_graph_repository import Neo4jGraphRepository
from app.interfaces.api.dependencies import get_neo4j_driver, get_ingestion_service, get_repository, get_graph_repository, get_job_repository, get_chunker, get_semantic_extractor
from app.admin.agents.admin_agent import AdminAgent
from langchain_core.messages import HumanMessage, AIMessage

st.set_page_config(page_title="RAG Playground", page_icon="🎮", layout="wide")
st.title("🎮 RAG Playground")


@st.cache_resource
def get_deps():
    driver = get_neo4j_driver()

    # 1. Repositories
    neo4j_doc = Neo4jStorage(driver)
    neo4j_graph = Neo4jGraphRepository(driver)
    chroma = ChromaStorage()

    # 2. Base Services
    llm = get_llm()
    rewriter = QueryRewriter(llm)

    # 3. Domain Service
    rag_service = RAGService(
        neo4j_doc_repo=neo4j_doc,
        neo4j_graph_repo=neo4j_graph,
        chroma_repo=chroma,
        llm=llm
    )
    
    feedback_service = FeedbackService()

    # 4. Ingestion Service (For Agent)
    # Re-using API dependencies logic might be complex due to passing args.
    # Let's clean instantiate it.
    from app.use_cases.ingestion import IngestionService
    from app.infrastructure.chunker.langchain_chunker import LangChainChunker
    from app.infrastructure.chunker.langchain_chunker import LangChainChunker
    from app.domain.services.semantic_extractor import SemanticExtractor
    from app.infrastructure.brain.adapter import LangGraphAdapter
    from app.infrastructure.storage.neo4j_job_repository import Neo4jJobRepository
    
    # We need simpler instantiation for Streamlit or reuse dependency injection helpers if possible
    # But `get_ingestion_service` requires Depends().
    # Let's instantiate manually as we did in MCP server, but here we can reuse Repos.
    
    # Using specific JobRepository? Global one?
    # Admin UI usually needs persistent job repo if we want to track across reload.
    # But currently the project uses MemoryJobRepository mostly or not defined clearly.
    # Let's use MemoryJobRepository for now as per `get_job_repository` default.
    job_repo = Neo4jJobRepository(driver)
    
    # Chunker
    chunker = LangChainChunker()
    
    # Extractor
    graph_adapter = LangGraphAdapter(llm)
    extractor = SemanticExtractor(graph_adapter)
    
    # Scraper
    from app.infrastructure.scrapers.trafilatura_scraper import TrafilaturaWebScraper
    scraper = TrafilaturaWebScraper()
    
    ingestion_service = IngestionService(
        scraper=scraper,
        repository=neo4j_doc, # Atomic Storage
        graph=neo4j_graph,
        job_repository=job_repo,
        chunker=chunker,
        extractor=extractor
    )

    admin_agent = AdminAgent(rag_service, ingestion_service)

    return admin_agent, feedback_service


admin_agent, feedback_service = get_deps()

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Chat Interface ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # Display Retrieved Context (Aggregated)
        if message.get("debug_info"):
            debug = message["debug_info"]

            # Graph Facts
            if debug.get("graph_data"):
                with st.expander(f"🕸️ Graph Facts ({len(debug['graph_data'])})"):
                    for item in debug["graph_data"]:
                        st.markdown(f"- **{item.get('source')}** -[{item.get('relationship')}]-> **{item.get('target')}**")

            # Vector & Keyword Chunks
            v_chunks = debug.get("vector_chunks", [])
            k_chunks = debug.get("keyword_chunks", [])
            total_chunks = len(v_chunks) + len(k_chunks)

            if total_chunks > 0:
                with st.expander(f"📚 Retrieved Documents ({total_chunks})"):
                    st.caption("Vector Search (MMR)")
                    for c in v_chunks:
                        st.text(f"[Score/Vector] {c.metadata.get('title', 'No Title')}\n{c.content[:100]}...")
                    st.divider()
                    st.caption("Keyword Search (Neo4j)")
                    for c in k_chunks:
                        st.text(f"[Keyword] {c.metadata.get('title', 'No Title')}\n{c.content[:100]}...")

        # Debug Prompt
        if message.get("debug_prompt"):
             with st.expander("🛠️ Debug: Prompt & Rewriting"):
                 rewrite_info = message.get("debug_rewrite")
                 if rewrite_info:
                     st.caption(f"Rewritten: {rewrite_info.get('rewritten')}")
                 st.code(message["debug_prompt"], language="text")

# Input
if prompt := st.chat_input("Ask a question regarding the ingested content..."):
    # Add User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Bot Response
    with st.chat_message("assistant"):
        status_container = st.status("Thinking (Agentic Workflow)...", expanded=True)
        try:
            # Prepare History (LangChain Format)
            history_interactive = [
                HumanMessage(content=m["content"]) if m["role"] == "user" else AIMessage(content=m["content"])
                for m in st.session_state.messages
            ]
            
            # Run Agent
            # Using asyncio.run for sync Streamlit wrapper
            status_container.write("🤖 Detecting intent...")
            
            inputs = {"messages": history_interactive}
            final_state = asyncio.run(admin_agent.workflow.ainvoke(inputs))
            
            # Analyze Result
            intent = final_state.get("intent", "search")
            tool_output = final_state.get("tool_output", "")
            context_data = final_state.get("context_data", {})
            
            last_msg = final_state["messages"][-1]
            answer = last_msg.content if last_msg else "No response generated."
            
            status_container.write(f"🎯 Intent: **{intent.upper()}**")
            
            if intent == "ingest":
                status_container.write(f"🛠️ Tool Output: {tool_output}")
                status_container.update(label="Ingestion Completed", state="complete", expanded=False)
            else:
                status_container.write("📚 Searching Knowledge Base...")
                status_container.update(label="RAG Search Completed", state="complete", expanded=False)

            # Display Answer
            st.markdown(answer)

            # Display Context (if any)
            if context_data:
                rewritten_query = context_data.get("rewritten_query")
                graph_data = context_data.get("graph_data", [])
                vector_chunks = context_data.get("vector_chunks", [])
                keyword_chunks = context_data.get("keyword_chunks", [])
                
                if graph_data:
                    with st.expander(f"🕸️ Graph Facts ({len(graph_data)})"):
                         for item in graph_data:
                            st.markdown(f"- **{item.get('source')}** -[{item.get('relationship')}]-> **{item.get('target')}**")
                
                total_docs = len(vector_chunks) + len(keyword_chunks)
                if total_docs > 0:
                     with st.expander(f"📚 Retrieved Documents ({total_docs})"):
                        st.caption("Vector Search (MMR)")
                        for c in vector_chunks:
                            st.text(f"---\n{c.content[:200]}...")
                        st.caption("Keyword Search")
                        for c in keyword_chunks:
                            st.text(f"---\n{c.content[:200]}...")

            # Save to History
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "debug_info": context_data if context_data else {},
                "debug_rewrite": {"original": prompt, "rewritten": context_data.get("rewritten_query")} if context_data else {},
                "debug_prompt": context_data.get("full_context") if context_data else ""
            })

        except Exception as e:
            st.error(f"Error: {e}")
            logging.exception("Agent Execution Failed")

# --- Feedback Section ---
if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
    st.divider()
    st.subheader("Rate this response")

    last_user_msg = st.session_state.messages[-2]["content"] if len(st.session_state.messages) >= 2 else "Unknown"
    last_bot_msg = st.session_state.messages[-1]["content"]

    col1, col2, col3 = st.columns([1, 1, 5])
    with col1:
        if st.button("👍 Good"):
            feedback_service.save_feedback({"query": last_user_msg, "response": last_bot_msg, "feedback": "positive"})
            st.toast("Thanks for your feedback!")
    with col2:
        if st.button("👎 Bad"):
            feedback_service.save_feedback({"query": last_user_msg, "response": last_bot_msg, "feedback": "negative"})
            st.toast("Feedback recorded.")

