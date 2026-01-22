import pandas as pd
import streamlit as st

from app.domain.entities.job import JobStatus
from app.interfaces.api.dependencies import get_job_repository, get_neo4j_driver

st.set_page_config(page_title="Job Queue", page_icon="📋", layout="wide")
st.title("📋 Processed Job Queue")

@st.cache_resource
def get_repo():
    driver = get_neo4j_driver()
    return get_job_repository(driver)

try:
    repo = get_repo()
    jobs = repo.list_jobs(limit=50)

    if not jobs:
        st.info("No jobs found.")
    else:
        # Summary Metrics
        total = len(jobs)
        completed = sum(1 for j in jobs if j.status == JobStatus.COMPLETED)
        failed = sum(1 for j in jobs if j.status == JobStatus.FAILED)
        pending = sum(1 for j in jobs if j.status == JobStatus.PENDING)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Jobs", total)
        col2.metric("Completed", completed)
        col3.metric("Failed", failed, delta_color="inverse")
        col4.metric("Pending", pending)

        st.divider()

        # Job List Table
        data = []
        for j in jobs:
            data.append({
                "Job ID": j.job_id,
                "Status": j.status.value,
                "URL": j.source_url,
                "Created At": j.created_at,
                "Updated At": j.updated_at,
                "Error": j.error_message if j.error_message else ""
            })

        df = pd.DataFrame(data)
        # Sort by Created At desc
        df["Created At"] = pd.to_datetime(df["Created At"])
        df = df.sort_values(by="Created At", ascending=False)

        st.dataframe(
            df,
            use_container_width=True,
            column_config={
                "URL": st.column_config.LinkColumn("Source URL"),
                "Status": st.column_config.TextColumn("Status", help="Current job status"),
            }
        )

        if st.button("Refresh"):
            st.rerun()

except Exception as e:
    st.error(f"Failed to load jobs: {str(e)}")
    st.info("Ensure the backend service is running.")
