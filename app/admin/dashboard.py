import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import os

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Ingestion Admin", layout="wide")

st.title("Ingestion Admin Dashboard")

# --- API Client ---
def fetch_jobs(limit=50):
    try:
        response = requests.get(f"{API_URL}/jobs", params={"limit": limit}, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to fetch jobs: {e}")
        return []

def retry_job(job_id):
    try:
        response = requests.post(f"{API_URL}/jobs/{job_id}/retry", timeout=10)
        response.raise_for_status()
        st.success(f"Retry triggered for Job {job_id}")
        return response.json()
    except Exception as e:
        st.error(f"Failed to retry job {job_id}: {e}")
        return None

# --- Sidebar ---
st.sidebar.header("Controls")
refresh = st.sidebar.button("Refresh")
auto_refresh = st.sidebar.checkbox("Auto Refresh", value=False)
limit = st.sidebar.number_input("Limit", min_value=10, max_value=200, value=50)

if auto_refresh:
    st.empty() # Placeholder for potential auto-rerun logic via query params or usage of st.rerun (if available)
    # Streamlit doesn't natively support timer-based rerun without loops or components
    # Just leave checkbox for now implies manual intent or future enhancement

# --- Main Content ---

jobs_data = fetch_jobs(limit)

if jobs_data:
    df = pd.DataFrame(jobs_data)
    
    # Format dates
    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"])
    if "updated_at" in df.columns:
        df["updated_at"] = pd.to_datetime(df["updated_at"])
    
    # KPIs
    col1, col2, col3 = st.columns(3)
    total_jobs = len(df)
    failed_jobs = len(df[df["status"] == "FAILED"]) if "status" in df.columns else 0
    running_jobs = len(df[df["status"] == "RUNNING"]) if "status" in df.columns else 0
    
    col1.metric("Total Jobs", total_jobs)
    col2.metric("Failed", failed_jobs)
    col3.metric("Running", running_jobs)

    # Job List
    st.subheader("Job List")
    
    # Style status
    def color_status(val):
        color = 'grey'
        if val == 'COMPLETED': color = 'green'
        elif val == 'FAILED': color = 'red'
        elif val == 'RUNNING': color = 'orange'
        return f'color: {color}'
    
    if "status" in df.columns:
        st.dataframe(df.style.applymap(color_status, subset=['status']), use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)

    # Detail & Actions
    st.subheader("Actions")
    selected_job_id = st.selectbox("Select Job to View/Retry", options=df["job_id"].tolist() if "job_id" in df.columns else [])
    
    if selected_job_id:
        job_details = next((item for item in jobs_data if item["job_id"] == selected_job_id), None)
        if job_details:
            with st.expander("Job Details", expanded=True):
                st.write(job_details)
                if job_details.get("status") == "FAILED":
                    if st.button(f"Retry Job {selected_job_id}"):
                        retry_job(selected_job_id)
                        st.rerun()
else:
    st.info("No jobs found.")
