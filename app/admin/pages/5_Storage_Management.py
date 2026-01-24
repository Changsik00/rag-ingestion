import os
import sys
import pandas as pd
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from app.admin.services.integrity_service import IntegrityAdminService

st.set_page_config(page_title="Storage Management", page_icon="📊", layout="wide")
st.title("📊 Storage Integrity Management")

@st.cache_resource
def get_service():
    return IntegrityAdminService()

service = get_service()

# --- Dashboard Overview ---
st.subheader("System Health Overview")

try:
    stats = service.get_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Neo4j Chunks (Source)", stats["total_primary"])
    col2.metric("Chroma Chunks (Index)", stats["total_target"])
    col3.metric("Missing (Drift)", stats["missing_count"], delta=-stats["missing_count"], delta_color="inverse")
    
    drift_pct = stats["drift_ratio"] * 100
    col4.metric("Integrity Score", f"{100 - drift_pct:.1f}%")

    if stats["missing_count"] > 0:
        st.warning(f"⚠️ {stats['missing_count']} chunks are missing from ChromaDB. Synchronization is recommended.")
    else:
        st.success("✅ Storage is perfectly synchronized.")

except Exception as e:
    st.error(f"Failed to load stats: {e}")

st.divider()

# --- Actions ---
st.subheader("Recovery Actions")
if st.button("🚀 Run Global Sync (Fix All Chunks)", type="primary"):
    progress_bar = st.progress(0.0)
    status_text = st.empty()
    
    def ui_callback(progress, message):
        progress_bar.progress(progress)
        status_text.text(f"Status: {message}")
        
    with st.status("Performing Full Synchronization...", expanded=True) as status:
        service.sync_all(callback=ui_callback)
        status.update(label="Sync Completed!", state="complete", expanded=False)
    
    st.success("Synchronization finished successfully.")
    st.rerun()

st.divider()

# --- Document Drift Report ---
st.subheader("Document-Level Drift Report")

@st.fragment
def render_doc_table():
    try:
        reports = service.get_document_reports()
        if not reports:
            st.info("No documents found in storage.")
            return

        df = pd.DataFrame(reports)
        
        # UI Formatting
        df = df[["status", "title", "total_chunks", "target_chunks", "drift_ratio", "id"]]
        
        # Search filter
        search = st.text_input("🔍 Search Document Title", key="doc_search")
        if search:
            df = df[df["title"].str.contains(search, case=False)]

        st.dataframe(
            df, 
            hide_index=True,
            column_config={
                "status": st.column_config.TextColumn("Status"),
                "title": st.column_config.TextColumn("Document Title", width="large"),
                "total_chunks": "Source Chunks",
                "target_chunks": "Indexed Chunks",
                "drift_ratio": st.column_config.ProgressColumn("Drift", format="%.2f", min_value=0, max_value=1),
                "id": None # Hide ID
            },
            use_container_width=True
        )

        # Selection for Individual Sync
        st.subheader("Manual Document Fix")
        selected_title = st.selectbox("Select document to fix", options=df["title"].tolist())
        if selected_title:
            doc_id = df[df["title"] == selected_title]["id"].values[0]
            if st.button(f"Fix '{selected_title}' Only"):
                with st.spinner(f"Repairing document {doc_id}..."):
                    res = service.sync_document(doc_id)
                    if res["success"]:
                        st.success(f"Repaired {res['count']} chunks.")
                        st.rerun()
                    else:
                        st.error(f"Repair failed: {res['error']}")

    except Exception as e:
        st.error(f"Failed to load document report: {e}")

render_doc_table()
