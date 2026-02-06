import time
import uuid

import streamlit as st

from admin.utils.api_client import get_api_client

st.set_page_config(page_title="RAG Playground", page_icon="🎮", layout="wide")
st.title("🎮 RAG Playground")

api_client = get_api_client()


# --- [Spec 032] 디버그 UI 렌더링 함수 ---
def render_debug_ui(message):
    """메시지에 포함된 디버그 정보를 통합 UI로 출력"""
    debug = message.get("debug_info", {})
    intent_info = message.get("debug_intent")
    rewrite_info = message.get("debug_rewrite")
    prompt_info = message.get("debug_prompt")

    # 1. Graph Facts
    graph_data = debug.get("graph_data", [])
    if graph_data:
        # graph_data can be a list of dicts or objects. Handle both.
        with st.expander(f"🕸️ Graph Facts ({len(graph_data)})"):
            for item in graph_data:
                if isinstance(item, dict):
                    st.markdown(f"- **{item.get('source')}** -[{item.get('relationship')}]-> **{item.get('target')}**")
                else:
                    st.markdown(f"- {str(item)}")

    # 2. Retrieved Documents
    v_chunks = debug.get("vector_chunks", [])
    k_chunks = debug.get("keyword_chunks", [])
    total_chunks = len(v_chunks) + len(k_chunks)
    if total_chunks > 0:
        with st.expander(f"📚 Retrieved Documents ({total_chunks})", expanded=False):
            if v_chunks:
                st.subheader("Vector Search (MMR)")
                for i, c in enumerate(v_chunks):
                    meta = c.get("metadata", {})
                    title = meta.get("title", "No Title")
                    score = meta.get("rerank_score", "N/A")
                    content = c.get("content", "No Content Available")

                    st.markdown(f"**[{i + 1}] {title}** (Score: {score})")
                    st.caption(content[:500] + ("..." if len(content) > 500 else ""))
                    st.divider() if i < len(v_chunks) - 1 else None

            if k_chunks:
                if v_chunks:
                    st.markdown("---")
                st.subheader("Keyword Search (Neo4j)")
                for i, c in enumerate(k_chunks):
                    meta = c.get("metadata", {})
                    title = meta.get("title", "No Title")
                    score = meta.get("rerank_score", "N/A")
                    content = c.get("content", "No Content Available")

                    st.markdown(f"**[{i + 1}] {title}** (Score: {score})")
                    st.caption(content[:500] + ("..." if len(content) > 500 else ""))
                    st.divider() if i < len(k_chunks) - 1 else None
    else:
        # User said it's empty even when count > 0, so let's check a possible edge case
        if "vector_chunks" in debug or "keyword_chunks" in debug:
            st.caption("No chunks found in debug data (Recall filtered by Threshold).")

    # 3. Intent & Prompt
    with st.expander("🛠️ Debug: Intent & Prompt"):
        if intent_info:
            st.markdown("**🧠 Intent Classification**")
            intent_type = intent_info.get("intent", "N/A")
            targets = intent_info.get("targets", [])
            reasoning = intent_info.get("reasoning", "")

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

        if rewrite_info and rewrite_info.get("rewritten"):
            st.divider()
            st.markdown("**✏️ Query Rewriting**")
            st.caption(f"Original: {rewrite_info.get('original')}")
            st.caption(f"Rewritten: {rewrite_info.get('rewritten')}")

        if prompt_info:
            st.divider()
            st.markdown("**📝 LLM Prompt**")
            st.code(prompt_info, language="text")


# --- [Spec 042] Session Persistence ---
def get_thread_id():
    """URL Query Param에서 thread_id를 가져오거나 새로 생성"""
    query_params = st.query_params
    t_id = query_params.get("thread_id")
    if not t_id:
        # 새로 생성
        if "thread_id_seed" not in st.session_state:
            st.session_state.thread_id_seed = str(uuid.uuid4())[:8]
        t_id_seed = st.session_state.thread_id_seed
        t_id = f"playground-{t_id_seed}"
        # URL 업데이트
        st.query_params["thread_id"] = t_id
    else:
        # URL에 있으면 session state 동기화
        if "thread_id_seed" not in st.session_state:
            st.session_state.thread_id_seed = t_id.replace("playground-", "")
    return t_id


def load_history(thread_id):
    """백엔드에서 대화 이력을 불러와 세션 상태 복원"""
    if "messages" not in st.session_state or not st.session_state.messages:
        try:
            res = api_client.get(f"/rag/sessions/{thread_id}/trace")
            if res and res.get("messages"):
                restored_msgs = []
                for m in res["messages"]:
                    role = "user" if m["role"] == "human" else "assistant"
                    # Backwards compatibility map 'ai' to 'assistant'
                    if m["role"] == "ai":
                        role = "assistant"

                    restored_msgs.append(
                        {
                            "role": role,
                            "content": m["content"],
                            "status": "completed",  # assume history is completed
                            # Restore debug info if available in values (complex, skipping for MVP)
                        }
                    )
                st.session_state.messages = restored_msgs
                if restored_msgs:
                    st.toast(f"Restored {len(restored_msgs)} messages from history.")
        except Exception as e:
            st.warning(f"Failed to load history: {e}")


# Apply Persistence
current_thread_id = get_thread_id()

if "messages" not in st.session_state:
    st.session_state.messages = []
    # Load history only on first init
    load_history(current_thread_id)

if "hitl_enabled" not in st.session_state:
    st.session_state.hitl_enabled = False

# --- Chat Interface (History Loop) ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # Decide whether to show default chat bubble
        is_draft = message.get("status") == "paused"
        is_clarification = message.get("is_clarification", False)

        # Only render standard bubble if it's NOT a draft (HITL) and NOT a clarification request
        if not is_draft and not is_clarification:
            st.markdown(message["content"])
        if message["role"] == "assistant":
            # [Spec 066] Ensure we only render debug UI for valid data
            render_debug_ui(message)

            # HITL Resume UI (Only for the latest paused message)
            if message.get("status") == "paused" and message == st.session_state.messages[-1]:
                # Spec 045: Canvas / Draft Editor
                st.info("📝 **Draft Mode**: You can edit the agent's response directly before finalizing.")

                # Use draft_content if available, else current message content
                draft_text = message.get("draft_content") or message.get("content", "")

                with st.form(key=f"draft_form_{len(st.session_state.messages)}"):
                    edited_content = st.text_area("Edit Draft", value=draft_text, height=300)

                    col_confirm, col_cancel = st.columns([1, 1])
                    with col_confirm:
                        if st.form_submit_button("✅ Confirm & Finalize"):
                            try:
                                if edited_content != draft_text:
                                    payload_input = f"User edited the draft to:\n\n{edited_content}"
                                else:
                                    payload_input = "Approved"

                                res = api_client.post(
                                    f"/rag/sessions/{current_thread_id}/resume", json={"input": payload_input}
                                )
                                if res:
                                    message["status"] = "completed"

                                    result_data = res.get("result", {})
                                    answer_text = "Resumed with feedback."

                                    msgs = result_data.get("messages", [])
                                    if msgs:
                                        last_msg = msgs[-1]
                                        answer_text = (
                                            last_msg.get("content") if isinstance(last_msg, dict) else last_msg.content
                                        )

                                    context_data = result_data.get("context_data") or {}
                                    debug_intent = None
                                    if context_data and context_data.get("user_intent"):
                                        ui = context_data["user_intent"]
                                        debug_intent = {
                                            "intent": ui.get("intent")
                                            if isinstance(ui, dict)
                                            else getattr(ui, "intent", "N/A"),
                                            "targets": ui.get("targets")
                                            if isinstance(ui, dict)
                                            else getattr(ui, "targets", []),
                                            "reasoning": ui.get("reasoning")
                                            if isinstance(ui, dict)
                                            else getattr(ui, "reasoning", ""),
                                        }

                                    st.session_state.messages.append(
                                        {
                                            "role": "assistant",
                                            "content": answer_text,
                                            "status": res.get("status", "completed"),
                                            "debug_info": context_data,
                                            "debug_intent": debug_intent,
                                            "debug_rewrite": {
                                                "original": payload_input,
                                                "rewritten": context_data.get("rewritten_query"),
                                            },
                                            "debug_prompt": context_data.get("full_context", ""),
                                            "is_clarification": res.get("is_clarification", False),
                                            "draft_content": res.get("draft_content"),
                                        }
                                    )
                                    st.rerun()
                            except Exception as e:
                                st.error(f"Failed to resume: {e}")

                    with col_cancel:
                        if st.form_submit_button("🔁 Request Re-generation"):
                            # Find the last user message to re-submit (Retry logic)
                            last_user_query = "Regenerate"
                            for msg in reversed(st.session_state.messages):
                                if msg["role"] == "user":
                                    last_user_query = msg["content"]
                                    break

                            try:
                                res = api_client.post(
                                    f"/rag/sessions/{current_thread_id}/resume",
                                    json={"input": last_user_query},
                                )
                                if res:
                                    message["status"] = "completed"

                                    result_data = res.get("result", {})
                                    answer_text = "Regenerated Response:"

                                    msgs = result_data.get("messages", [])
                                    if msgs:
                                        last_msg = msgs[-1]
                                        answer_text = (
                                            last_msg.get("content") if isinstance(last_msg, dict) else last_msg.content
                                        )

                                    context_data = result_data.get("context_data") or {}
                                    debug_intent = None
                                    if context_data and context_data.get("user_intent"):
                                        ui = context_data["user_intent"]
                                        debug_intent = {
                                            "intent": ui.get("intent")
                                            if isinstance(ui, dict)
                                            else getattr(ui, "intent", "N/A"),
                                            "targets": ui.get("targets")
                                            if isinstance(ui, dict)
                                            else getattr(ui, "targets", []),
                                            "reasoning": ui.get("reasoning")
                                            if isinstance(ui, dict)
                                            else getattr(ui, "reasoning", ""),
                                        }

                                    st.session_state.messages.append(
                                        {
                                            "role": "assistant",
                                            "content": answer_text,
                                            "status": res.get("status", "completed"),
                                            "debug_info": context_data,
                                            "debug_intent": debug_intent,
                                            "debug_rewrite": {
                                                "original": f"Retry: {last_user_query}",
                                                "rewritten": context_data.get("rewritten_query"),
                                            },
                                            "debug_prompt": context_data.get("full_context", ""),
                                            "is_clarification": res.get("is_clarification", False),
                                            "draft_content": res.get("draft_content"),
                                        }
                                    )
                                    st.rerun()
                            except Exception as e:
                                st.error(f"Failed to regenerate: {e}")

                st.divider()

            # Spec 045: Clarification UI
            if message.get("is_clarification"):
                st.warning(f"⚠️ **Clarification Needed**: {message['content']}")

# --- Sidebar: Knowledge Source ---
with st.sidebar:
    st.subheader("📚 Knowledge Source")
    st.caption("Restrict search scope to specific documents")

    # [Spec 061] Session Controls in Sidebar
    col_new, col_del = st.columns([1, 1])
    with col_new:
        if st.button("🔄 New Chat", use_container_width=True):
            st.session_state.thread_id_seed = str(uuid.uuid4())[:8]
            st.query_params["thread_id"] = f"playground-{st.session_state.thread_id_seed}"
            st.session_state.messages = []
            st.rerun()

    with col_del:
        if st.button("🗑️ Reset", use_container_width=True, help="Delete history for current thread"):
            try:
                api_client.post(f"/rag/sessions/{current_thread_id}/reset")
                st.session_state.messages = []
                st.toast("Conversation history deleted.")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Failed to reset: {e}")

    st.divider()

    search_term = st.text_input("🔍 Search Documents", placeholder="Enter title or URL...")

    with st.spinner("Loading Documents..."):
        try:
            if search_term:
                docs = api_client.get(f"/rag/documents/autocomplete?q={search_term}") or []
            else:
                # Default list if no search term (or empty list)
                docs = []

            doc_options = {d["id"]: d["title"] for d in docs}
            selected_doc_ids = st.multiselect(
                "Select Documents",
                options=list(doc_options.keys()),
                format_func=lambda x: doc_options.get(x, x),
                help="Only these documents will be used for RAG context.",
            )
        except Exception as e:
            st.error(f"Failed to load documents: {e}")
            selected_doc_ids = []

    with st.expander("🛠️ Advanced Settings", expanded=False):
        # Spec 055: Advanced Tuning Controls
        st.caption("🔍 Retrieval & Generation Tuning")

        # Top-K
        st.session_state.settings_top_k = st.slider(
            "Top-K Documents",
            min_value=1,
            max_value=20,
            value=st.session_state.get("settings_top_k", 5),
            help="검색할 문서의 최대 개수입니다.",
        )

        # Temperature
        st.session_state.settings_temp = st.slider(
            "LLM Temperature",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.get("settings_temp", 0.0),
            step=0.1,
            help="생성 다양성을 결정합니다. 0.5 이상이면 'Relaxed Mode'가 활성화되어 부족한 컨텍스트를 외부 지식으로 보완합니다.",
        )
        if st.session_state.settings_temp >= 0.5:
            st.info("💡 **Relaxed Mode Enabled**: Agent will use internal knowledge if DB context is insufficient.")
        else:
            st.caption("🔒 **Strict RAG Mode**: Agent will only answer using uploaded documents.")

        # Search Strategy
        st.session_state.settings_strategy = st.radio(
            "Search Strategy",
            options=["hybrid", "vector", "keyword"],
            index=0
            if "settings_strategy" not in st.session_state
            else ["hybrid", "vector", "keyword"].index(st.session_state.get("settings_strategy", "hybrid")),
            horizontal=True,
            help="검색 방식을 선택합니다.",
        )

        st.divider()

        st.divider()

        st.divider()
        st.subheader("🚦 HITL Control")
        st.info(f"**Thread ID**: `{current_thread_id}`")

        hitl_enabled = st.toggle(
            "Enable HITL Review",
            value=st.session_state.hitl_enabled,
            help="If enabled, the pipeline will stop before generating the final answer for your review.",
        )
        st.session_state.hitl_enabled = hitl_enabled


# --- Input Handling ---
if prompt := st.chat_input("Ask a question regarding the ingested content..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# --- Response Processing ---
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    prompt = st.session_state.messages[-1]["content"]

    with st.chat_message("assistant"):
        status_container = st.status("Thinking (Agentic API)...", expanded=True)
        try:
            filters = {"doc_id": selected_doc_ids} if selected_doc_ids else {}

            # API Call
            payload = {
                "message": prompt,
                "filters": filters,
                "hitl_enabled": st.session_state.hitl_enabled,
                "advanced_settings": {
                    "top_k": st.session_state.get("settings_top_k", 5),
                    "temperature": st.session_state.get("settings_temp", 0.0),
                    "search_strategy": st.session_state.get("settings_strategy", "hybrid"),
                },
            }

            res = api_client.post(f"/rag/sessions/{current_thread_id}/ask", json=payload)

            if res:
                # Check for HITL pause (This depends on how the backend returns
                # HITL state. For now assuming typical response or handling logic)
                # If we want to support HITL in thin client, the API shouldn't block
                # but return a "waiting" status.

                answer = "No response generated."
                if res.get("messages"):
                    # Check both 'ai' and 'assistant' roles
                    for m in reversed(res["messages"]):
                        if m.get("role") in ["ai", "assistant"]:
                            answer = m["content"]
                            break

                # Spec 055 Debug: Show Raw Response
                with st.expander("📝 Raw API Response (JSON)"):
                    st.json(res)

                context_data = res.get("context_data") or {}
                intent = res.get("intent", "search")
                # Fix: Use 'current_status' from ChatResponse to detect paused state correctly
                status = res.get("current_status", "completed")

                status_container.write(f"🎯 Intent: **{intent.upper()}**")

                if status == "paused":
                    status_container.update(label="👀 Review Draft Response (HITL)", state="running", expanded=True)
                    st.info("The agent has generated a **Draft Response**. Please review and confirm to finalize.")
                else:
                    status_container.update(label="RAG Search Completed", state="complete", expanded=False)
                    # Display summary from current context
                    passed = sum(1 for item in (res.get("rerank_log") or []) if item.get("status") == "passed")
                    status_container.write(f"📊 **Rerank Summary**: {passed} chunks passed.")

                st.markdown(answer)

                # [Spec 066] Observability Links
                trace_url = context_data.get("trace_url")

                col_tr1, col_tr2 = st.columns([1, 1])
                with col_tr1:
                    if trace_url:
                        st.link_button("🚀 View LangFuse Trace", trace_url, use_container_width=True)
                with col_tr2:
                    st.link_button(
                        "🔍 View Rerank Analysis",
                        f"/Observability_&_Trace?thread_id={current_thread_id}",
                        use_container_width=True,
                    )

                # References
                citations = context_data.get("citations", []) if context_data else []
                if citations:
                    st.divider()
                    st.markdown("#### 📚 References")
                    for cite in citations:
                        st.markdown(
                            f"{cite.get('index')}. [{cite.get('title')}]({cite.get('url')}) - *{cite.get('source')}*"
                        )

                # Prepare Debug Data
                debug_intent = None
                if context_data and context_data.get("user_intent"):
                    ui = context_data["user_intent"]
                    # user_intent might be a dict or object depending on serialization
                    debug_intent = {
                        "intent": ui.get("intent") if isinstance(ui, dict) else getattr(ui, "intent", "N/A"),
                        "targets": ui.get("targets") if isinstance(ui, dict) else getattr(ui, "targets", []),
                        "reasoning": ui.get("reasoning") if isinstance(ui, dict) else getattr(ui, "reasoning", ""),
                    }

                # Update Session State
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "status": status,
                        "debug_info": context_data,
                        "debug_intent": debug_intent,
                        "debug_rewrite": {"original": prompt, "rewritten": context_data.get("rewritten_query")},
                        "debug_prompt": context_data.get("full_context", ""),
                        "is_clarification": res.get("is_clarification", False),
                        "draft_content": res.get("draft_content"),
                    }
                )
                st.rerun()
            else:
                st.error("API failed to provide a response.")

        except Exception as e:
            st.error(f"Error: {e}")
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
            if api_client.post(
                "/rag/feedback", json={"query": last_user_msg, "response": last_bot_msg, "feedback": "positive"}
            ):
                st.toast("Thanks for your feedback!")
    with col2:
        if st.button("👎 Bad"):
            if api_client.post(
                "/rag/feedback", json={"query": last_user_msg, "response": last_bot_msg, "feedback": "negative"}
            ):
                st.toast("Feedback recorded.")
