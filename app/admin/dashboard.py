import streamlit as st

st.set_page_config(
    page_title="RAG Ingestion Admin",
    page_icon="🧠",
    layout="wide",
)

st.title("🧠 RAG Ingestion Admin Dashboard")

st.markdown("""
Welcome to the **Advanced Admin Dashboard**.
Select a tool from the sidebar to get started:

*   **📋 Job Queue**: Monitor ingestion status (`Pending`, `Completed`, `Failed`).
*   **🕸️ Graph Explorer**: Visualize and query the Knowledge Graph.
*   **🚦 HITL Control**: Manage Human-in-the-loop interventions.
*   **🔍 Trace Viewer**: Analyze reasoning traces and failures.
*   **🎮 RAG Playground**: Test retrieval and generation.
""")

st.divider()

st.info("💡 Tip: Use the sidebar to navigate between modules.")
