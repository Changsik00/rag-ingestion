import pandas as pd
import streamlit as st

from admin.utils.api_client import get_api_client

st.set_page_config(page_title="Job Queue", page_icon="📋", layout="wide")
st.title("📋 Processed Job Queue")

api_client = get_api_client()

try:
    jobs = api_client.get("/jobs")

    if not jobs:
        st.info("No jobs found.")
    else:
        # Summary Metrics
        total = len(jobs)
        # API returns job objects. Mapping status to string if needed.
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
                },
            )

        if st.button("Refresh"):
            st.rerun()

except Exception as e:
    st.error(f"Failed to load jobs: {str(e)}")
    st.info("Ensure the backend service is running.")
