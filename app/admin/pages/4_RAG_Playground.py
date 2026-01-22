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
from app.interfaces.api.dependencies import get_neo4j_driver

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
    return rag_service, feedback_service


rag_service, feedback_service = get_deps()

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
        with st.spinner("Thinking (Hybrid RAG)..."):
            try:
                # Prepare History (excluding current)
                history_context = st.session_state.messages[:-1]

                # Execute RAG Service
                # Using asyncio.run to execute async method in sync Streamlit script
                # Note: If Streamlit runs in an event loop, this might need handling.
                # Standard Streamlit script execution allows asyncio.run().
                result = asyncio.run(rag_service.retrieve_and_generate(prompt, history_context))

                answer = result.answer

                # Display Answer
                st.markdown(answer)

                # Display New Context Immediately
                if result.graph_data:
                    with st.expander(f"🕸️ Graph Facts ({len(result.graph_data)})"):
                         for item in result.graph_data:
                            st.markdown(f"- **{item.get('source')}** -[{item.get('relationship')}]-> **{item.get('target')}**")

                total_docs = len(result.vector_chunks) + len(result.keyword_chunks)
                if total_docs > 0:
                    with st.expander(f"📚 Retrieved Documents ({total_docs})"):
                        st.caption("Vector Search (MMR)")
                        for c in result.vector_chunks:
                            st.text(f"---\n{c.content[:200]}...")
                        st.caption("Keyword Search")
                        for c in result.keyword_chunks:
                            st.text(f"---\n{c.content[:200]}...")

                # Save to History
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "debug_info": {
                        "rewritten_query": result.rewritten_query,
                        "vector_chunks": result.vector_chunks,
                        "keyword_chunks": result.keyword_chunks,
                        "graph_data": result.graph_data
                    },
                    "debug_rewrite": {"original": prompt, "rewritten": result.rewritten_query},
                    "debug_prompt": result.full_context # This is context string, serves as prompt debug
                })

            except Exception as e:
                st.error(f"Error: {e}")
                logging.exception("RAG Execution Failed")

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

