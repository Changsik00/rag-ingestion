import streamlit as st

from admin.utils.api_client import get_api_client

st.set_page_config(page_title="Trace Viewer", page_icon="🔍", layout="wide")
st.title("🔍 Reasoning Trace Viewer")

api_client = get_api_client()

# Search
thread_id = st.text_input("Enter Thread ID / Job ID", value="", placeholder="e.g. job-1234")

if thread_id:
    if st.button("Analyze Trace"):
        with st.spinner("Fetching Trace..."):
            trace = api_client.get(f"/jobs/{thread_id}/trace")
            if not trace:
                st.error("Trace not found or empty.")
            else:
                st.success(f"Loaded trace for {thread_id}")

                # Layout
                tab1, tab2 = st.tabs(["State Snapshot", "Raw Data"])

                with tab1:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("Values")
                        st.json(trace.get("values", {}))
                    with col2:
                        st.subheader("Next Steps")
                        st.write(trace.get("next", []))
                        st.subheader("Tasks")
                        st.code(trace.get("tasks", ""))

                with tab2:
                    st.json(trace)
