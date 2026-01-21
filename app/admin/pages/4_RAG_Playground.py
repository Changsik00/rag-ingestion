import time

import streamlit as st

from app.admin.services.feedback_service import FeedbackService
from app.interfaces.api.dependencies import get_neo4j_driver, get_repository

st.set_page_config(page_title="RAG Playground", page_icon="🎮", layout="wide")
st.title("🎮 RAG Playground")


@st.cache_resource
def get_deps():
    driver = get_neo4j_driver()
    repo = get_repository(driver)
    feedback_service = FeedbackService()
    return repo, feedback_service


repo, feedback_service = get_deps()

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Chat Interface ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("retrieved"):
            with st.expander(f"📚 Retrieved Context ({len(message['retrieved'])} chunks)"):
                for idx, chunk in enumerate(message["retrieved"]):
                    st.markdown(f"**Chunk {idx + 1} (ID: {chunk.id})**")
                    st.text(chunk.content[:200] + "...")
                    st.caption(f"Metadata: {chunk.metadata}")
                    st.divider()
        
        if message.get("debug_prompt"):
            with st.expander("🛠️ Debug: Prompt & Logic"):
                st.code(message["debug_prompt"], language="text")

# Input
if prompt := st.chat_input("Ask a question regarding the ingested content..."):
    # Add User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Bot Response
    with st.chat_message("assistant"):
        with st.spinner("Retrieving & Thinking..."):
            # 1. Retrieval
            chunks = repo.search(prompt, limit=5)

            # Real RAG Generation
        with st.spinner("Generating answer..."):
            try:
                # Prepare Prompt
                context_text = "\n\n".join([c.content for c in chunks])
                llm_prompt = f"""
                You are a helpful assistant. Use the following context to answer the user's question.
                If the answer is not in the context, say you don't know.
                
                Context:
                {context_text}
                
                Question:
                {prompt}
                
                Answer:
                """
                
                from app.core.llm import get_llm
                llm = get_llm()
                answer = llm.generate(llm_prompt)
                
            except Exception as e:
                answer = f"Error generating answer: {e}"

            st.markdown(answer)

            # Show Context
            if chunks:
                with st.expander(f"📚 Retrieved Context ({len(chunks)} chunks)"):
                    for idx, chunk in enumerate(chunks):
                        st.markdown(f"**Chunk {idx + 1} (ID: {chunk.id})**")
                        st.text(chunk.content[:200] + "...")
                        st.caption(f"Metadata: {chunk.metadata}")
                        st.divider()
            else:
                st.warning("No relevant context found.")

            # Show Debug Prompt
            with st.expander("🛠️ Debug: Prompt & Logic"):
                st.code(llm_prompt, language="text")

        # Add Assistant Message
        st.session_state.messages.append({
            "role": "assistant", 
            "content": answer, 
            "retrieved": chunks,
            "debug_prompt": llm_prompt
        })

    st.rerun()

# --- Feedback Section (Always visible for last interaction) ---
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
