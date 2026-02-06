import os

import streamlit as st

from admin.utils.api_client import get_api_client

st.set_page_config(page_title="Observability & Trace", page_icon="📊", layout="wide")
st.title("📊 Observability & Trace")

api_client = get_api_client()

# --- Section 1: External Observability (LangFuse) ---
st.header("🚀 LangFuse Dashboard")
st.caption("Deep-dive into traces, scores, and LLM costs.")

langfuse_host = os.getenv("LANGFUSE_HOST")
if langfuse_host:
    st.link_button("Open LangFuse Dashboard", langfuse_host, type="primary")
else:
    st.warning("⚠️ LangFuse is not configured. (Check LANGFUSE_HOST in .env)")

st.divider()

# --- Section 2: Internal State Inspection ---
st.header("🔍 Internal State Inspector")
st.caption("Inspect raw state of LangGraph Checkpointers (RAG Sessions or Ingestion Jobs).")

search_type = st.radio("Target System", ["RAG Session", "Ingestion Job"], horizontal=True)
thread_id = st.text_input("Enter ID", placeholder="e.g. playground-xxxx or job-yyyy")

if thread_id:
    if st.button("Fetch State"):
        with st.spinner("Fetching State..."):
            try:
                data = None
                if search_type == "RAG Session":
                    # RAG Session uses different endpoint structure, but we can try /trace
                    # Note: rag/sessions/{id}/trace returns formatted TraceResponse
                    data = api_client.get(f"/rag/sessions/{thread_id}/trace")
                else:
                    # Ingestion Job
                    data = api_client.get(f"/jobs/{thread_id}/trace")

                if not data:
                    st.error(f"Trace not found for ID: {thread_id}")
                else:
                    st.success(f"Loaded state for {thread_id}")

                    # Layout
                    tab1, tab2, tab3 = st.tabs(["State Snapshot", "Rerank Analysis", "Raw Data"])

                    with tab1:
                        st.json(data.get("values", {}))

                    with tab2:
                        state_values = data.get("values", {})
                        rerank_log = state_values.get("rerank_log", [])

                        if not rerank_log:
                            st.info("No Rerank Log found in this state.")
                        else:
                            import pandas as pd
                            df = pd.DataFrame(rerank_log)

                            # Reorder and rename columns for display
                            cols = ["status", "score", "source", "reasoning", "content"]
                            df = df[[c for c in cols if c in df.columns]]

                            st.dataframe(
                                df,
                                column_config={
                                    "status": st.column_config.TextColumn("Status", width="small"),
                                    "score": st.column_config.NumberColumn("Score", format="%d"),
                                    "source": st.column_config.TextColumn("Source"),
                                    "content": st.column_config.TextColumn("Content (Snippet)", width="large"),
                                    "reasoning": st.column_config.TextColumn("Reasoning", width="medium"),
                                },
                                hide_index=True,
                                use_container_width=True
                            )

                            # Summary metrics
                            passed = sum(1 for item in rerank_log if item.get("status") == "passed")
                            dropped = sum(1 for item in rerank_log if item.get("status") == "dropped")
                            st.write(f"**Summary**: {passed} chunks passed, {dropped} chunks dropped.")

                    with tab3:
                        st.json(data)

            except Exception as e:
                st.error(f"Failed to fetch trace: {e}")
