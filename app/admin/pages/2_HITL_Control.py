import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

import pandas as pd
import streamlit as st

from app.admin.services.hitl_service import HitlService

st.set_page_config(page_title="HITL Control", page_icon="🚦", layout="wide")
st.title("🚦 HITL Control Center")


@st.cache_resource
def get_service():
    return HitlService()


service = get_service()

# --- Active Threads List ---
st.subheader("Active Threads")

threads = service.list_threads(limit=50)

if not threads:
    st.info("No active threads found.")
else:
    # Transform to DataFrame
    data = []
    for t in threads:
        t_id = t["thread_id"]
        status = service.get_thread_status(t_id)
        data.append(
            {
                "Thread ID": t_id,
                "Status": status,
                "Checkpoint ID": t["checkpoint_id"],
                # "Updated At": t['metadata'].get('ts') # Timestamp might be in metadata
            }
        )

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)

    # Separation for Actions
    st.divider()

    st.subheader("Thread Management")

    col1, col2 = st.columns([1, 1])

    with col1:
        selected_thread = st.selectbox("Select Thread", [t["Thread ID"] for t in data])

        if selected_thread:
            current_status = next((d["Status"] for d in data if d["Thread ID"] == selected_thread), "Unknown")
            st.metric("Current Status", current_status)

            trace_data = service.get_thread_trace(selected_thread)
            with st.expander("View Trace Snapshot"):
                st.json(trace_data)

    with col2:
        if selected_thread and current_status == "Interrupted":  # Only allow resume if interrupted/human-review
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
                        success = service.resume_thread(selected_thread, input_payload)
                        if success:
                            st.success("Thread Resumed!")
                            st.rerun()
                        else:
                            st.error("Failed to resume thread.")
