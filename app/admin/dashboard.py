import streamlit as st
import requests
import pandas as pd
from datetime import datetime

import os

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000") 
# Using "backend" hostname for docker network. 
# But if I run streamlit locally for dev, it might need localhost.
# Docker compose service name is 'backend' (from Spec 001/002).

st.set_page_config(page_title="Ingestion Admin", layout="wide")

st.title("Ingestion Admin Dashboard")

st.sidebar.header("Actions")
if st.sidebar.button("Refresh"):
    st.experimental_rerun()

# Placeholders
st.info("Dashboard initialized. Connecting to API...")

try:
    response = requests.get(f"{API_URL}/health", timeout=2)
    if response.status_code == 200:
        st.success("Connected to Backend API")
    else:
        st.error(f"Backend returned {response.status_code}")
except Exception as e:
    st.error(f"Failed to connect to Backend: {e}")
    st.caption("If running locally, ensure backend is running at http://localhost:8000 and update API_URL.")

