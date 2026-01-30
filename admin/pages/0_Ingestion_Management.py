import streamlit as st
import time
from admin.utils.api_client import get_api_client

st.set_page_config(page_title="Ingestion Management", page_icon="📥", layout="wide")
st.title("📥 Ingestion Management")

api_client = get_api_client()

tabs = st.tabs(["🌐 Web URL Ingestion", "📁 Local File Ingestion"])

with tabs[0]:
    st.subheader("Web URL 수집")
    url = st.text_input("Enter URL to ingest", placeholder="https://example.com")
    if st.button("🚀 Ingest URL", type="primary"):
        if url:
            with st.spinner("Starting ingestion job..."):
                # URL is handled via standard POST /ingest/web (outside admin prefix)
                # But our client base URL is /api/v1/admin. 
                # Let's check main.py again. 
                # main.py @app.post("/ingest/web") is at root. 
                # Admin router is at /api/v1/admin.
                # We might need to use a different base URL or adjust endpoints.
                # For now, let's assume we can call relative to root if we adjust client or use absolute path.
                # Actually, main.py routes:
                # app.include_router(admin_router, prefix="/api/v1/admin")
                # So /ingest/web is at /ingest/web.
                
                # We need to call ../../../ingest/web or similar if base_url is /api/v1/admin/
                res = api_client.post("/../../../ingest/web", json={"url": url})
                if res:
                    st.success(f"Job created: {res.get('job_id')}")
                    st.info("Check 'Job Queue' for status.")
        else:
            st.warning("Please enter a URL.")

with tabs[1]:
    st.subheader("로컬 파일 수집")
    st.info("지원 포맷: PDF, TXT, MD (최대 10MB)")
    
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt", "md"])
    
    if st.button("🚀 Upload & Ingest", type="primary", disabled=not uploaded_file):
        if uploaded_file:
            with st.spinner("Uploading and processing..."):
                files = {
                    "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
                }
                # /ingest/file is also at root in main.py
                res = api_client.upload_file("/../../../ingest/file", files=files)
                if res:
                    st.success(f"File uploaded and job created: {res.get('job_id')}")
                    st.info("Check 'Job Queue' for status.")
        else:
            st.warning("Please select a file.")

st.divider()
st.caption("Tip: 수집이 완료된 문서는 RAG Playground에서 바로 활용할 수 있습니다.")
