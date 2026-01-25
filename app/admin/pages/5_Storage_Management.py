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

# --- 1. Dashboard Overview (Summary) ---
st.subheader("System Health Overview")

try:
    stats = service.get_stats()
    missing_count = stats["missing_count"]
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Neo4j Chunks (Source)", stats["total_primary"])
    col2.metric("Chroma Chunks (Index)", stats["total_target"])
    col3.metric("Missing (Drift)", missing_count, delta=-missing_count if missing_count > 0 else 0, delta_color="inverse")
    
    drift_pct = stats["drift_ratio"] * 100
    col4.metric("Integrity Score", f"{100 - drift_pct:.1f}%")

    if missing_count > 0:
        st.warning(f"⚠️ {missing_count} chunks are missing from ChromaDB. Please review the details below.")
    else:
        st.success("✅ Storage is perfectly synchronized.")

except Exception as e:
    st.error(f"Failed to load system stats: {e}")

st.divider()

# --- 2. Document-Level Drift Report (Detailed Analysis) ---
st.subheader("🔍 Document-Level Drift Analysis")
st.info("어떤 문서가 유실되었는지, 어떤 내용이 누락되었는지 확인하세요.")

@st.fragment
def render_doc_table():
    try:
        with st.spinner("Analyzing document drift..."):
            reports = service.get_document_reports()
        
        if not reports:
            st.info("No documents found in storage.")
            return

        df = pd.DataFrame(reports)
        
        # Search & Filter
        search = st.text_input("🔍 Search Document Title", key="doc_search_v2")
        show_mismatches_only = st.checkbox("Show Mismatches Only", value=True)
        
        if search:
            df = df[df["title"].str.contains(search, case=False)]
        if show_mismatches_only:
            df = df[df["status"] != "In Sync"]

        # Display Table
        st.dataframe(
            df[["status", "title", "total_chunks", "target_chunks", "drift_ratio", "id"]], 
            hide_index=True,
            column_config={
                "status": st.column_config.TextColumn("Status"),
                "title": st.column_config.TextColumn("Document Title", width="large"),
                "total_chunks": "Source",
                "target_chunks": "Indexed",
                "drift_ratio": st.column_config.ProgressColumn("Drift", format="%.2f", min_value=0, max_value=1),
                "id": None
            },
            use_container_width=True
        )

        # Detailed View (Missing Samples)
        if not df.empty:
            st.write("---")
            st.markdown("### 📄 Missing Content Preview")
            
            # ID와 제목을 조합하여 유니크한 옵션 생성
            df["display_name"] = df["title"] + " (" + df["id"].str[:8] + "...)"
            display_to_id = dict(zip(df["display_name"], df["id"]))
            
            selected_display = st.selectbox(
                "Select document to preview missing parts", 
                options=df["display_name"].tolist()
            )
            
            if selected_display:
                doc_id = display_to_id[selected_display]
                row = df[df["id"] == doc_id].iloc[0]
                
                # 상세 정보 표시 (Missing Title인 경우 URL 중심, 아니면 본문 중심)
                tab1, tab2, tab3 = st.tabs(["💡 Diagnostic", "🔍 RAG Context Preview", "🧬 Graph Enrichment"])
                
                with tab1:
                    if row["status"] == "Missing Title":
                        st.warning(f"**Document has no title.**")
                        st.info(f"**Source URL:** {row['url']}")
                        st.caption("Fix 버튼을 누르면 위 URL을 기반으로 제목을 추출하고 하위 청크에 전파합니다.")
                    elif row["status"] != "In Sync":
                        st.error(f"**Missing Snippet Sample from '{row['title']}':**")
                        with st.spinner("Loading snippet..."):
                            snippet = service.get_missing_chunk_sample(doc_id)
                        st.code(snippet or "Snippet not available.")
                    else:
                        st.success(f"'{row['title']}' is fully synchronized.")

                with tab2:
                    st.info("LLM이 실제로 보게 될 정제된 컨텍스트입니다. Infobox 등이 잘 보존되었는지 확인하세요.")
                    if st.button("Generate Preview", key=f"preview_btn_{doc_id}"):
                        with st.spinner("Cleaning context..."):
                            import asyncio
                            cleaned_ctx = asyncio.run(service.get_cleaned_context(doc_id))
                            st.text_area("Cleaned Content", value=cleaned_ctx, height=400)

                with tab3:
                    st.info("지식 그래프 데이터(Entity/Relationship)가 부족한 경우 재추출을 실행합니다.")
                    if st.button("🚀 Re-extract Knowledge Graph", key=f"enrich_btn_{doc_id}"):
                        with st.spinner("LLM is extracting semantics..."):
                            import asyncio
                            res = asyncio.run(service.enrich_knowledge_graph(doc_id))
                            if res["success"]:
                                st.success(f"Successfully enriched: {res['entities']} entities, {res['rels']} relationships.")
                            else:
                                st.error(f"Enrichment failed: {res.get('error')}")
                
                st.divider()
                if row["status"] != "In Sync":
                    if st.button(f"🛠 Fix Selected Document Metadata & Sync", key=f"fix_btn_{doc_id}"):
                        with st.spinner("Repairing..."):
                            res = service.sync_document(doc_id)
                            if res["success"]:
                                st.success(f"Successfully repaired {res['count']} chunks.")
                                st.rerun()

    except Exception as e:
        st.error(f"Failed to load document report: {e}")

render_doc_table()

st.divider()

# --- 3. Global Recovery Actions (Execution) ---
st.subheader("🚀 Global Recovery Actions")

try:
    reports = service.get_document_reports()
    mismatch_docs = [r for r in reports if r["status"] != "In Sync"]
    needs_sync = len(mismatch_docs) > 0
    
    # 덮어씌울 수 있는 미스매치 수 (Chunk 누락 + Title 누락 포함)
    button_type = "primary" if needs_sync else "secondary"
    button_label = f"🚀 Run Global Sync (Fix {len(mismatch_docs)} Issues)" if needs_sync else "✅ Storage is Healthy"

    if st.button(button_label, type=button_type, disabled=not needs_sync):
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
except Exception as e:
    st.error(f"Failed to prepare recovery actions: {e}")

st.caption("Tip: Global Sync는 데이터 양에 따라 시간이 소요될 수 있습니다.")
