import streamlit as st

from admin.utils.api_client import get_api_client

st.set_page_config(page_title="Ingestion Management", page_icon="📥", layout="wide")
st.title("📥 Ingestion Management")

api_client = get_api_client()

st.divider()

# --- [Spec 056] Chunking Settings ---
with st.expander("⚙️ Chunking Settings", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        strategy = st.radio(
            "Chunking Strategy",
            options=["recursive", "semantic"],
            index=0,
            help="Recursive: 고정 크기 분할, Semantic: 의미 기반 분할",
            horizontal=True,
        )

    chunk_config = {"strategy": strategy}

    if strategy == "recursive":
        with col2:
            c_size = st.number_input("Chunk Size", value=1000, step=100)
            c_overlap = st.number_input("Chunk Overlap", value=200, step=50)
            chunk_config.update({"chunk_size": c_size, "chunk_overlap": c_overlap})
    else:
        with col2:
            threshold_type = st.selectbox(
                "Breakpoint Threshold Type",
                options=["percentile", "standard_deviation", "interquartile", "gradient"],
                index=0,
            )
            threshold_amount = st.slider("Threshold Amount", min_value=0.0, max_value=100.0, value=90.0, step=0.1)
            chunk_config.update(
                {"breakpoint_threshold_type": threshold_type, "breakpoint_threshold_amount": threshold_amount}
            )

st.divider()

tabs = st.tabs(["🌐 Web URL Ingestion", "📁 Local File Ingestion"])

with tabs[0]:
    st.subheader("Web URL 수집")
    url = st.text_input("Enter URL to ingest", placeholder="https://example.com")
    if st.button("🚀 Ingest URL", type="primary"):
        if url:
            with st.spinner("Starting ingestion job..."):
                # URL is handled via standard POST /v1/ingest/web
                res = api_client.post("ingest/web", json={"url": url, "chunking_config": chunk_config})
                if res:
                    st.success(f"Job created: {res.get('job_id')}")
                    st.info("Check 'Job Queue' for status.")
        else:
            st.warning("Please enter a URL.")

with tabs[1]:
    st.subheader("로컬 파일 수집")
    st.info("지원 포맷: PDF, TXT, MD (최대 10MB)")

    uploaded_files = st.file_uploader("Choose files", type=["pdf", "txt", "md"], accept_multiple_files=True)

    if st.button("🚀 Upload & Ingest", type="primary", disabled=not uploaded_files):
        if uploaded_files:
            with st.spinner(f"Uploading {len(uploaded_files)} files..."):
                file_list = [("files", (f.name, f.getvalue(), f.type)) for f in uploaded_files]
                # /v1/ingest/files is now standard
                res = api_client.upload_file("ingest/files", files=file_list)
                if res and "jobs" in res:
                    st.success(f"{len(res['jobs'])} files uploaded and jobs created.")
                    for job in res["jobs"]:
                        st.write(f"- Job ID: `{job['job_id']}`")
                    st.info("Check 'Job Queue' for status.")
        else:
            st.warning("Please select at least one file.")

st.divider()
st.caption("Tip: 수집이 완료된 문서는 RAG Playground에서 바로 활용할 수 있습니다.")
