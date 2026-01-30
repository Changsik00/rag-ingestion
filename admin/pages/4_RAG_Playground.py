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
        with st.expander(f"📚 Retrieved Documents ({total_chunks})"):
            if v_chunks:
                st.caption("Vector Search (MMR)")
                for c in v_chunks:
                    # In API response, chunks might be serialized as dicts
                    content = c.get("content", "") if isinstance(c, dict) else getattr(c, "content", "")
                    title = (
                        c.get("metadata", {}).get("title", "No Title")
                        if isinstance(c, dict)
                        else c.metadata.get("title", "No Title")
                    )
                    st.text(f"[Score/Vector] {title}\n{content[:100]}...")
            if k_chunks:
                st.divider()
                st.caption("Keyword Search (Neo4j)")
                for c in k_chunks:
                    content = c.get("content", "") if isinstance(c, dict) else getattr(c, "content", "")
                    title = (
                        c.get("metadata", {}).get("title", "No Title")
                        if isinstance(c, dict)
                        else c.metadata.get("title", "No Title")
                    )
                    st.text(f"[Keyword] {title}\n{content[:100]}...")

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
    st.divider()

    st.subheader("📁 Quick File Upload")
    quick_file = st.file_uploader("Upload PDF/TXT/MD to Chat", type=["pdf", "txt", "md"], key="quick_upload")
    if st.button("🚀 Upload & Chat", use_container_width=True, disabled=not quick_file):
        with st.spinner("Ingesting file..."):
            files = {"file": (quick_file.name, quick_file.getvalue(), quick_file.type)}
            res = api_client.upload_file("/../../../ingest/file", files=files)
            if res:
                st.success(f"Ingested: {quick_file.name}")
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"✅ 파일 수집 완료: **{quick_file.name}**\n\n이제 이 파일의 내용에 대해 질문하실 수 있습니다.",
                    "status": "completed"
                })
                st.rerun()

    st.divider()

    with st.expander("🛠️ Advanced Settings", expanded=False):
        if st.button("🗑️ Delete Thread History", use_container_width=True):
            try:
                api_client.post(f"/rag/sessions/{current_thread_id}/reset")
                st.session_state.messages = []
                st.toast("Conversation history deleted from server.")
                time.sleep(1)  # Give toast time to show
                st.rerun()
            except Exception as e:
                st.error(f"Failed to clear history: {e}")

        if st.button("🔄 New Conversation (Reset Thread)", use_container_width=True):
            st.session_state.thread_id_seed = str(uuid.uuid4())[:8]
            st.query_params["thread_id"] = f"playground-{st.session_state.thread_id_seed}"
            st.session_state.messages = []
            st.rerun()

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
            filters = {"doc_id": selected_doc_ids} if selected_doc_ids else None

            # API Call
            payload = {
                "message": prompt,
                "filters": filters,
                "hitl_enabled": st.session_state.hitl_enabled,
            }

            res = api_client.post(f"/rag/sessions/{current_thread_id}/ask", json=payload)

            if res:
                # Check for HITL pause (This depends on how the backend returns
                # HITL state. For now assuming typical response or handling logic)
                # If we want to support HITL in thin client, the API shouldn't block
                # but return a "waiting" status.

                answer = "No response generated."
                if res.get("messages"):
                    # Last AI message
                    answer = next((m["content"] for m in reversed(res["messages"]) if m["role"] == "ai"), answer)

                context_data = res.get("context_data") or {}
                intent = res.get("intent", "search")
                status = res.get("status", "completed")

                status_container.write(f"🎯 Intent: **{intent.upper()}**")

                if status == "paused":
                    status_container.update(label="👀 Review Draft Response (HITL)", state="running", expanded=True)
                    st.info("The agent has generated a **Draft Response**. Please review and confirm to finalize.")
                else:
                    status_container.update(label="RAG Search Completed", state="complete", expanded=False)

                st.markdown(answer)

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
            api_client.post(
                "/rag/feedback", json={"query": last_user_msg, "response": last_bot_msg, "feedback": "positive"}
            )
            st.toast("Thanks for your feedback!")
    with col2:
        if st.button("👎 Bad"):
            api_client.post(
                "/rag/feedback", json={"query": last_user_msg, "response": last_bot_msg, "feedback": "negative"}
            )
            st.toast("Feedback recorded.")
