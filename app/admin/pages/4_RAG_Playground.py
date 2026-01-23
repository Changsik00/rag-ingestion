import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

import asyncio
import logging

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage

from app.admin.agents.admin_agent import AdminAgent
from app.admin.services.feedback_service import FeedbackService
from app.core.llm import get_llm
from app.domain.services.query_rewriter import QueryRewriter
from app.domain.services.rag_service import RAGService
from app.infrastructure.storage.chroma import ChromaStorage
from app.infrastructure.storage.neo4j_document_repository import Neo4jStorage
from app.infrastructure.storage.neo4j_graph_repository import Neo4jGraphRepository
from app.interfaces.api.dependencies import (
    get_neo4j_driver,
)

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
        query_rewriter=rewriter,
        llm=llm
    )

    feedback_service = FeedbackService()

    # 4. Ingestion Service (For Agent)
    # Re-using API dependencies logic might be complex due to passing args.
    # Let's clean instantiate it.
    from app.domain.services.semantic_extractor import SemanticExtractor
    from app.infrastructure.brain.adapter import LangGraphAdapter
    from app.infrastructure.chunker.langchain_chunker import LangChainChunker
    from app.infrastructure.storage.composite import CompositeStorage
    from app.infrastructure.storage.neo4j_job_repository import Neo4jJobRepository
    from app.use_cases.ingestion import IngestionService

    # We need simpler instantiation for Streamlit or reuse dependency injection helpers if possible
    # But `get_ingestion_service` requires Depends().
    # Let's instantiate manually as we did in MCP server, but here we can reuse Repos.

    # Composite Repository (Neo4j + Chroma) for Hybrid Search support
    composite_repo = CompositeStorage(neo4j_doc, chroma)

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
        repository=composite_repo, # Composite Storage (Neo4j + Chroma)
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

# --- Sidebar: Knowledge Source ---
with st.sidebar:
    st.subheader("📚 Knowledge Source")
    st.caption("Restrict search scope to specific documents")
    
    # Document Search Functionality
    search_term = st.text_input("🔍 Search Documents", placeholder="Enter title or URL...")
    
    with st.spinner("Loading Documents..."):
        try:
            doc_repo = admin_agent.rag_service.neo4j_doc_repo
            # Use the new search_term in list_documents
            docs = doc_repo.list_documents(limit=50, search_term=search_term if search_term else None)
            
            doc_options = {}
            for d in docs:
                title = d.metadata.get("title", "Untitled")
                source = d.metadata.get("source", "")
                label = f"{title} ({source})" if source else title
                doc_options[d.id] = label
            
            selected_doc_ids = st.multiselect(
                "Select Documents",
                options=list(doc_options.keys()),
                format_func=lambda x: doc_options.get(x, x),
                help="Only these documents will be used for RAG context."
            )
            
        except Exception as e:
            st.error(f"Failed to load documents: {e}")
            selected_doc_ids = []

    st.divider()
    
    with st.expander("🛠️ Advanced Settings", expanded=False):
        st.caption("Debug & Internal Settings")
        # Any other settings can go here

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

            # Prepare filters if selected
            filters = {"doc_id": selected_doc_ids} if selected_doc_ids else None

            inputs = {"messages": history_interactive, "filters": filters}
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

