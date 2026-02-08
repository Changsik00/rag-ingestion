import pandas as pd
import streamlit as st

from admin.utils.api_client import get_api_client

st.set_page_config(page_title="Job Queue", page_icon="📋", layout="wide")
st.title("📋 Processed Job Queue")

api_client = get_api_client()

# [Spec 072] Status Filter
st.sidebar.header("Filters")
status_filter = st.sidebar.selectbox(
    "Filter by Status",
    options=["All", "PENDING", "RUNNING", "COMPLETED", "FAILED", "SKIPPED"],
    index=0,
)

try:
    # [Spec 072] Call Admin API with status filter
    if status_filter == "All":
        jobs = api_client.get("/jobs")
    else:
        # Use new Admin API endpoint
        jobs = api_client.get(f"/admin/jobs?status={status_filter}&limit=100")

    if not jobs:
        st.info("No jobs found.")
    else:
        # Summary Metrics
        total = len(jobs)
        # API returns job objects with 'status' field
        completed = sum(1 for j in jobs if j.get("status") in ["completed", "COMPLETED"])
        failed = sum(1 for j in jobs if j.get("status") in ["failed", "FAILED"])
        pending = sum(1 for j in jobs if j.get("status") in ["pending", "PENDING", "running", "RUNNING"])
        skipped = sum(1 for j in jobs if j.get("status") in ["skipped", "SKIPPED"])

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Jobs", total)
        col2.metric("Completed", completed)
        col3.metric("Failed", failed, delta_color="inverse")
        col4.metric("Pending/Running", pending)
        col5.metric("Skipped (Dedup)", skipped)

        st.divider()

        # Job List Table
        data = []
        for j in jobs:
            data.append(
                {
                    "Job ID": j.get("job_id"),
                    "Status": j.get("status"),
                    "URL": j.get("source_url"),
                    "Skip Reason": j.get("skip_reason") or "",  # [Spec 072]
                    "Created At": j.get("created_at"),
                    "Updated At": j.get("updated_at"),
                    "Error": j.get("error_message") or "",
                }
            )

        df = pd.DataFrame(data)
        if not df.empty:
            df["Created At"] = pd.to_datetime(df["Created At"])
            df = df.sort_values(by="Created At", ascending=False)

            st.dataframe(
                df,
                use_container_width=True,
                column_config={
                    "URL": st.column_config.TextColumn("Source (URL/File)", width="medium"),
                    "Status": st.column_config.TextColumn("Status", help="Current job status"),
                    "Skip Reason": st.column_config.TextColumn("Skip Reason", help="Deduplication skip reason"),
                },
                hide_index=True,
            )

            # [Spec 072] Force Refresh functionality
            st.divider()
            st.subheader("🔄 Force Re-ingest")

            job_id_to_refresh = st.text_input("Enter Job ID to force re-ingest:", placeholder="job-xxx-xxx")

            if st.button("Force Refresh", type="primary"):
                if not job_id_to_refresh:
                    st.warning("⚠️ Please enter a Job ID")
                else:
                    with st.spinner(f"Re-ingesting job {job_id_to_refresh}..."):
                        try:
                            response = api_client.post(f"/admin/jobs/{job_id_to_refresh}/force-refresh")
                            st.success(f"✅ Job {job_id_to_refresh} re-ingested successfully!")
                            st.json(response)
                            st.info("Refresh the page to see updated status.")
                        except Exception as e:
                            st.error(f"❌ Failed to force refresh: {str(e)}")

        if st.button("Refresh Page"):
            st.rerun()

except Exception as e:
    st.error(f"Failed to load jobs: {str(e)}")
    st.info("Ensure the backend service is running.")
