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


def get_core_deps():
    """핵심 의존성 객체(드라이버, 저장소)만 캐싱하여 반환"""
    driver = get_neo4j_driver()
    neo4j_doc = Neo4jStorage(driver)
    neo4j_graph = Neo4jGraphRepository(driver)
    chroma = ChromaStorage()
    llm = get_llm()

    from app.domain.services.intent_classifier import IntentClassifier
    rewriter = QueryRewriter(llm)
    intent_classifier = IntentClassifier(llm)

    return {
        "driver": driver,
        "neo4j_doc": neo4j_doc,
        "neo4j_graph": neo4j_graph,
        "chroma": chroma,
        "llm": llm,
        "rewriter": rewriter,
        "intent_classifier": intent_classifier
    }

@st.cache_resource
def get_feedback_service():
    return FeedbackService()

async def get_active_agent(interrupt_nodes=None):
    """현재 이벤트 루프에 맞는 AdminAgent를 생성 (Checkpointer 동기화 포함)"""
    core = get_core_deps()
    from app.infrastructure.rag.graph import RAGGraphBuilder
    from app.infrastructure.rag.nodes import RAGNodes
    from app.interfaces.api.dependencies import get_checkpointer

    rag_nodes = RAGNodes(
        neo4j_doc_repo=core["neo4j_doc"],
        neo4j_graph_repo=core["neo4j_graph"],
        chroma_repo=core["chroma"],
        query_rewriter=core["rewriter"],
        intent_classifier=core["intent_classifier"],
        llm=core["llm"],
    )

    checkpointer = await get_checkpointer()
    rag_graph_builder = RAGGraphBuilder(rag_nodes)
    rag_graph = rag_graph_builder.build(checkpointer=checkpointer)
    rag_service = RAGService(graph=rag_graph)

    # Ingestion Service
    from app.domain.services.semantic_extractor import SemanticExtractor
    from app.infrastructure.brain.adapter import LangGraphAdapter
    from app.infrastructure.chunker.langchain_chunker import LangChainChunker
    from app.infrastructure.scrapers.trafilatura_scraper import TrafilaturaWebScraper
    from app.infrastructure.storage.composite import CompositeStorage
    from app.infrastructure.storage.neo4j_job_repository import Neo4jJobRepository
    from app.use_cases.ingestion import IngestionService

    composite_repo = CompositeStorage(core["neo4j_doc"], core["chroma"])
    job_repo = Neo4jJobRepository(core["driver"])
    chunker = LangChainChunker()
    graph_adapter = LangGraphAdapter(core["llm"], checkpointer=checkpointer)
    extractor = SemanticExtractor(graph_adapter)
    scraper = TrafilaturaWebScraper()

    ingestion_service = IngestionService(
        scraper=scraper,
        repository=composite_repo,
        graph=core["neo4j_graph"],
        job_repository=job_repo,
        chunker=chunker,
        extractor=extractor,
    )

    admin_agent = AdminAgent(rag_service, ingestion_service)
    # 현재 루프의 체크포인터로 워크플로우 컴파일
    admin_agent.workflow = admin_agent._build_graph(checkpointer=checkpointer, interrupt_before=interrupt_nodes)

    return admin_agent


# --- [Spec 032] 디버그 UI 렌더링 함수 (중복 제거 및 일관성 유지) ---
def render_debug_ui(message):
    """메시지에 포함된 디버그 정보를 통합 UI로 출력"""
    debug = message.get("debug_info", {})
    intent_info = message.get("debug_intent")
    rewrite_info = message.get("debug_rewrite")
    prompt_info = message.get("debug_prompt")

    # 1. Graph Facts
    graph_data = debug.get("graph_data", [])
    if graph_data:
        with st.expander(f"🕸️ Graph Facts ({len(graph_data)})"):
            for item in graph_data:
                st.markdown(f"- **{item.get('source')}** -[{item.get('relationship')}]-> **{item.get('target')}**")

    # 2. Retrieved Documents
    v_chunks = debug.get("vector_chunks", [])
    k_chunks = debug.get("keyword_chunks", [])
    total_chunks = len(v_chunks) + len(k_chunks)
    if total_chunks > 0:
        with st.expander(f"📚 Retrieved Documents ({total_chunks})"):
            if v_chunks:
                st.caption("Vector Search (MMR)")
                for c in v_chunks:
                    st.text(f"[Score/Vector] {c.metadata.get('title', 'No Title')}\n{c.content[:100]}...")
            if k_chunks:
                st.divider()
                st.caption("Keyword Search (Neo4j)")
                for c in k_chunks:
                    st.text(f"[Keyword] {c.metadata.get('title', 'No Title')}\n{c.content[:100]}...")

    # 3. Intent & Prompt (통합 디버그 섹션)
    with st.expander("🛠️ Debug: Intent & Prompt"):
        if intent_info:
            st.markdown("**🧠 Intent Classification**")
            intent_type = intent_info.get("intent", "N/A")
            targets = intent_info.get("targets", [])
            reasoning = intent_info.get("reasoning", "")

            # Intent color coding
            intent_color = {
                "general_query": "🟢",
                "compare": "🔵",
                "summarize": "🟡",
                "filter_by_topic": "🟣",
            }.get(intent_type, "⚪")

            st.markdown(f"**Intent:** {intent_color} `{intent_type.upper()}`")
            if targets:
                st.markdown(f"**Targets:** {', '.join([f'`{t}`' for t in targets])}")
            st.caption(f"**Reasoning:** {reasoning}")
        else:
            st.caption("_Intent classification not available_")

        if rewrite_info and rewrite_info.get("rewritten"):
            st.divider()
            st.markdown("**✏️ Query Rewriting**")
            st.caption(f"Original: {rewrite_info.get('original')}")
            st.caption(f"Rewritten: {rewrite_info.get('rewritten')}")

        if prompt_info:
            st.divider()
            st.markdown("**📝 LLM Prompt**")
            st.code(prompt_info, language="text")

        # [Spec 034] Reasoning Trace
        reasoning_log = debug.get("reasoning_log", [])
        if reasoning_log:
            st.divider()
            st.markdown("**🔍 Reasoning Trace**")
            for entry in reasoning_log:
                st.caption(entry)

        # [Spec 034] Fallback & Recovery Info

        # [Spec 034] Fallback & Recovery Info
        fallback_triggered = debug.get("fallback_triggered", False)
        if fallback_triggered:
            st.divider()
            st.warning("🔄 **Fallback Triggered**: Strict filters returned no results. Global search was performed.")

        # [Spec 035] Citation Metadata Debug
        citations = debug.get("citations", [])
        if citations:
            st.divider()
            st.markdown("**📌 Citation Metadata**")
            st.json(citations)


feedback_service = get_feedback_service()

# Initialize Chat History and Session ID
if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id_seed" not in st.session_state:
    import uuid
    st.session_state.thread_id_seed = str(uuid.uuid4())[:8]

if "hitl_enabled" not in st.session_state:
    st.session_state.hitl_enabled = False

# --- Chat Interface (히스토리 루프) ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            render_debug_ui(message)  # 함수 호출로 통합

# --- Sidebar: Knowledge Source ---
with st.sidebar:
    st.subheader("📚 Knowledge Source")
    st.caption("Restrict search scope to specific documents")

    # Document Search Functionality
    search_term = st.text_input("🔍 Search Documents", placeholder="Enter title or URL...")

    with st.spinner("Loading Documents..."):
        try:
            # Spec 033: RAGService는 더 이상 repository를 직접 노출하지 않음
            # 대신 get_deps()에서 반환된 neo4j_doc 사용
            driver = get_neo4j_driver()
            doc_repo = Neo4jStorage(driver)
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
                help="Only these documents will be used for RAG context.",
            )

        except Exception as e:
            st.error(f"Failed to load documents: {e}")
            selected_doc_ids = []

    st.divider()

    with st.expander("🛠️ Advanced Settings", expanded=False):
        st.caption("Debug & Internal Settings")

        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        if st.button("🔄 New Conversation (Reset Thread)", use_container_width=True):
            import uuid
            st.session_state.thread_id_seed = str(uuid.uuid4())[:8]
            st.session_state.messages = []
            st.rerun()

        st.divider()
        st.subheader("🚦 HITL Control")
        # Display Thread ID for Trace Viewer
        st.info(f"**Thread ID**: `{f'playground-{st.session_state.thread_id_seed}'}`")

        if "hitl_enabled" not in st.session_state:
            st.session_state.hitl_enabled = False

        hitl_enabled = st.toggle(
            "Enable HITL Review",
            value=st.session_state.hitl_enabled,
            help="If enabled, the pipeline will stop before generating the final answer for your review.",
        )
        st.session_state.hitl_enabled = hitl_enabled

# --- Input 처리 ---
if prompt := st.chat_input("Ask a question regarding the ingested content..."):
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()  # Spec 032: 사용자 메시지 즉시 반영

# --- 실제 응답 처리 (마지막 메시지가 user일 때만) ---
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    prompt = st.session_state.messages[-1]["content"]

    with st.chat_message("assistant"):
        status_container = st.status("Thinking (Agentic Workflow)...", expanded=True)
        try:
            # Prepare History (LangChain Format)
            history_interactive = [
                HumanMessage(content=m["content"]) if m["role"] == "user" else AIMessage(content=m["content"])
                for m in st.session_state.messages
            ]

            status_container.write("🤖 Detecting intent...")

            # Prepare filters if selected
            filters = {"doc_id": selected_doc_ids} if selected_doc_ids else None


            # [Spec 034] HITL Thread ID & Interrupt Logic
            thread_id = f"playground-{st.session_state.thread_id_seed}"
            interrupt_nodes = ["search"] if st.session_state.hitl_enabled else None

            async def run_agent_workflow():
                thread_id = f"playground-{st.session_state.thread_id_seed}"
                config = {"configurable": {"thread_id": thread_id}}
                agent = await get_active_agent(interrupt_nodes=interrupt_nodes)

                # 1. 현 상태 먼저 확인 (이미 멈춰있는지)
                snapshot = await agent.workflow.aget_state(config)

                # 2. 멈춰있지 않은 경우에만 실행 시작
                if not snapshot.next:
                    inputs = {"messages": history_interactive, "filters": filters, "thread_id": thread_id}
                    final_state = await agent.workflow.ainvoke(inputs, config=config)
                    # 실행 후 다시 스냅샷 (인터럽트 발생했을 수 있음)
                    snapshot = await agent.workflow.aget_state(config)
                else:
                    final_state = snapshot.values

                return final_state, snapshot

            final_state, snapshot = asyncio.run(run_agent_workflow())
            config = {"configurable": {"thread_id": f"playground-{st.session_state.thread_id_seed}"}}

            if snapshot.next:
                status_container.update(label="🚦 Paused for Human Review", state="running", expanded=True)
                st.warning(f"Pipeline paused at: **{snapshot.next[0]}**. Review the reasoning trace below.")

                if st.button("✅ Confirm & Generate Answer", type="primary", use_container_width=True):
                    # Resume
                    async def resume_agent():
                        agent = await get_active_agent(interrupt_nodes=interrupt_nodes)
                        # Resume by passing None to continue from interrupt
                        return await agent.workflow.ainvoke(None, config=config)
                    final_state = asyncio.run(resume_agent())
                    answer = final_state["messages"][-1].content
                else:
                    st.info("💡 Trace Viewer 혹은 HITL Control 메뉴에서 상태를 확인하거나, 위 버튼을 눌러 계속하세요.")
                    st.stop()
            else:
                last_msg = final_state["messages"][-1]
                answer = last_msg.content if last_msg else "No response generated."

            # Analyze Result
            intent = final_state.get("intent", "search")
            tool_output = final_state.get("tool_output", "")
            context_data = final_state.get("context_data", {})

            status_container.write(f"🎯 Intent: **{intent.upper()}**")

            if intent == "ingest":
                status_container.write(f"🛠️ Tool Output: {tool_output}")
                status_container.update(label="Ingestion Completed", state="complete", expanded=False)
            else:
                status_container.write("📚 Searching Knowledge Base...")
                status_container.update(label="RAG Search Completed", state="complete", expanded=False)

            # Display Answer
            st.markdown(answer)

            # [Spec 035] References Section
            citations = context_data.get("citations", [])
            if citations:
                st.divider()
                st.markdown("#### 📚 References")
                for cite in citations:
                    index = cite.get("index")
                    title = cite.get("title", "Untitled")
                    url = cite.get("url")
                    source = cite.get("source", "Unknown")

                    if url:
                        st.markdown(f"{index}. [{title}]({url}) - *{source}*")
                    else:
                        st.markdown(f"{index}. {title} - *{source}*")

                st.caption("💡 *Numeric citations [n] refer to specific documents in our knowledge base. Sentences without citations are derived from AI's general knowledge.*")

            # 데이터 정리 (Spec 032)
            debug_intent = None
            if context_data and context_data.get("user_intent"):
                user_intent_obj = context_data["user_intent"]
                debug_intent = {
                    "intent": user_intent_obj.intent.value if hasattr(user_intent_obj, "intent") else "N/A",
                    "targets": user_intent_obj.targets if hasattr(user_intent_obj, "targets") else [],
                    "reasoning": user_intent_obj.reasoning if hasattr(user_intent_obj, "reasoning") else "",
                }

            # 세션 상태에 저장
            new_message = {
                "role": "assistant",
                "content": answer,
                "debug_info": context_data if context_data else {},
                "debug_intent": debug_intent,
                "debug_rewrite": {"original": prompt, "rewritten": context_data.get("rewritten_query")}
                if context_data
                else {},
                "debug_prompt": context_data.get("full_context", ""),
            }
            st.session_state.messages.append(new_message)

            # 화면 갱신 (루프에서 다시 그리도록 함) - Spec 032
            st.rerun()

        except Exception as e:
            st.error(f"Error: {e}")
            logging.exception("Agent Execution Failed")
            # 에러 메시지도 저장
            st.session_state.messages.append({"role": "assistant", "content": f"Error: {e}"})
            st.rerun()

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
