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


# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id_seed" not in st.session_state:
    import uuid

    st.session_state.thread_id_seed = str(uuid.uuid4())[:8]

if "hitl_enabled" not in st.session_state:
    st.session_state.hitl_enabled = False

# --- Chat Interface (History Loop) ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            render_debug_ui(message)
            
            # HITL Resume UI (Only for the latest paused message)
            if message.get("status") == "paused" and message == st.session_state.messages[-1]:
                st.warning("⚠️ This is a DRAFT. Confirm to finalize or provide feedback to revise.")
                col1, col2 = st.columns([1, 3])
                thread_id = f"playground-{st.session_state.thread_id_seed}"
                
                with col1:
                    if st.button("✅ Confirm & Finalize", key=f"resume_{len(st.session_state.messages)}", help="Approve this draft as the final answer."):
                        try:
                            res = api_client.post(f"/rag/sessions/{thread_id}/resume", json={"input": "Approved"})
                            if res:
                                # Update status of current message to prevent duplicate buttons
                                message["status"] = "completed"
                                st.rerun()
                        except Exception as e:
                            st.error(f"Failed to resume: {e}")

                with col2:
                    feedback = st.text_input("Feedback", placeholder="Request changes or provide corrections...", key=f"feed_{len(st.session_state.messages)}")
                    if st.button("🛠️ Revise & Continue", key=f"feed_btn_{len(st.session_state.messages)}", help="Send feedback to the agent for revision."):
                         if feedback:
                            try:
                                res = api_client.post(f"/rag/sessions/{thread_id}/resume", json={"input": feedback})
                                # Mark previous draft as replaced/completed
                                message["status"] = "completed"
                                
                                result_data = res.get("result", {})
                                answer_text = "Resumed with feedback."
                                
                                # Extract content and debug info
                                msgs = result_data.get("messages", [])
                                if msgs:
                                    last_msg = msgs[-1]
                                    answer_text = last_msg.get("content") if isinstance(last_msg, dict) else last_msg.content

                                context_data = result_data.get("context_data", {})
                                debug_intent = None
                                if context_data and context_data.get("user_intent"):
                                    ui = context_data["user_intent"]
                                    debug_intent = {
                                        "intent": ui.get("intent") if isinstance(ui, dict) else getattr(ui, "intent", "N/A"),
                                        "targets": ui.get("targets") if isinstance(ui, dict) else getattr(ui, "targets", []),
                                        "reasoning": ui.get("reasoning") if isinstance(ui, dict) else getattr(ui, "reasoning", ""),
                                    }

                                st.session_state.messages.append({
                                    "role": "assistant", 
                                    "content": answer_text, 
                                    "status": res.get("status", "completed"),
                                    "debug_info": context_data,
                                    "debug_intent": debug_intent,
                                    "debug_rewrite": {"original": feedback, "rewritten": context_data.get("rewritten_query")},
                                    "debug_prompt": context_data.get("full_context", ""),
                                })
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to resume: {e}")

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

    with st.expander("🛠️ Advanced Settings", expanded=False):
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
        thread_id = f"playground-{st.session_state.thread_id_seed}"
        st.info(f"**Thread ID**: `{thread_id}`")

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
            thread_id = f"playground-{st.session_state.thread_id_seed}"
            filters = {"doc_id": selected_doc_ids} if selected_doc_ids else None

            # API Call
            payload = {
                "message": prompt,
                "filters": filters,
                "hitl_enabled": st.session_state.hitl_enabled,
            }

            res = api_client.post(f"/rag/sessions/{thread_id}/ask", json=payload)

            if res:
                # Check for HITL pause (This depends on how the backend returns
                # HITL state. For now assuming typical response or handling logic)
                # If we want to support HITL in thin client, the API shouldn't block
                # but return a "waiting" status.

                answer = "No response generated."
                if res.get("messages"):
                    # Last AI message
                    answer = next((m["content"] for m in reversed(res["messages"]) if m["role"] == "ai"), answer)

                context_data = res.get("context_data", {})
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
