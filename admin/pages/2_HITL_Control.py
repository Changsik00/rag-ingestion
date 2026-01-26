import json

import pandas as pd
import streamlit as st

from admin.utils.api_client import get_api_client

st.set_page_config(page_title="HITL Control", page_icon="🚦", layout="wide")
st.title("🚦 HITL Control Center")

api_client = get_api_client()

# --- Active Threads List ---
st.subheader("Active Threads")

# Using the jobs endpoint for active threads
threads = api_client.get("/jobs/active/threads") or []

if not threads:
    st.info("No active threads found.")
else:
    data = []
    for t in threads:
        t_id = t["thread_id"]
        # Basic info from list
        data.append({"Thread ID": t_id, "Checkpoint ID": t["checkpoint_id"], "Metadata": str(t.get("metadata", {}))})

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)

    st.divider()

    st.subheader("Thread Management")

    col1, col2 = st.columns([1, 1])

    with col1:
        selected_thread = st.selectbox("Select Thread", [t["Thread ID"] for t in data])

        if selected_thread:
            status_res = api_client.get(f"/jobs/{selected_thread}/status")
            current_status = status_res.get("status", "Unknown") if status_res else "Unknown"
            st.metric("Current Status", current_status)

            trace_data = api_client.get(f"/jobs/{selected_thread}/trace")
            with st.expander("View Trace Snapshot"):
                st.json(trace_data)

    with col2:
        if selected_thread and current_status == "interrupted":
            st.warning(f"Thread {selected_thread} is waiting for input.")

            with st.form("resume_form"):
                decision = st.selectbox("Decision", ["Approved", "Rejected", "Retry", "Custom"])
                custom_input = st.text_area("Custom Input (JSON)", value='{"feedback": "Approved"}')

                submitted = st.form_submit_button("Resume Thread")
                if submitted:
                    input_payload = {"decision": decision}
                    if decision == "Custom":
                        try:
                            input_payload = json.loads(custom_input)
                        except Exception:
                            st.error("Invalid JSON")
                            input_payload = None

                    if input_payload:
                        # API expectation for resume: {"input": {...}}
                        res = api_client.post(f"/jobs/{selected_thread}/resume", json={"input": input_payload})
                        if res and res.get("status") == "Resumed":
                            st.success("Thread Resumed!")
                            st.rerun()
                        else:
                            st.error("Failed to resume thread.")
